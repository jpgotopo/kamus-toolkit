# -*- coding: utf-8 -*-
"""Acceso a las listas de términos bíblicos de Paratext.

Existe por dos problemas concretos.

El primero: los Id de TermRenderings.xml de un proyecto no siempre traen la misma
vocalización masorética que la lista instalada. En Yanesha, 141 de 361 términos
solo casan si se comparan las consonantes. Como build.py busca por igualdad
exacta de cadena, todo lo que derivemos de las listas hay que emparejarlo con
tolerancia y volver a emitirlo con el Id que usa el proyecto.

El segundo, y más peligroso: emparejar sin vocales confunde homógrafos. גד es
Gad y también el cilantro; כלב es Caleb y también el perro; עזה es Gaza y
también Uzá. Un emparejamiento ingenuo glosa al profeta Gad como 'cilantro'.

De ahí la forma de este módulo: la lista Major (BiblicalTerms.xml) es la espina
dorsal, porque trae Id exactos, Category, Domain y las referencias de cada
término. Un Id de proyecto se resuelve primero contra Major —descartando por
referencias los homógrafos que no aparecen en los libros que el proyecto
traduce— y solo entonces se busca su glosa castellana, exigiendo que la entrada
española pertenezca a la misma Category y Domain. Cuando la ambigüedad no se
deja resolver, se devuelve None: una glosa ausente es mejor que una equivocada.
"""
import os, re, collections, unicodedata
import xml.etree.ElementTree as ET

LISTS = r"C:\Program Files\Paratext 9\Terms\Lists"


def nfc(l):
    """Los Id de las listas y los del proyecto no siempre traen la misma
    composición Unicode: גַּד-2 puede ser NFC en uno y NFD en el otro, idénticos
    en pantalla pero distintos como cadena. Lo mismo pasa con el espacio duro de
    los lemas compuestos (קִרְיַת יְעָרִים). Sin esto, términos que están en la
    lista con su Id exacto se dan por ausentes y caen al emparejado por
    consonantes, que es justo el que confunde homógrafos."""
    return unicodedata.normalize("NFC", l).replace("\xa0", " ")


def norm_lemma(l):
    """Misma normalización que build.norm_lemma, más el NBSP que traen algunos Id."""
    l = nfc(l).strip()
    l = re.sub(r"\.\((?:I|II|III)\)$", "", l)
    l = re.sub(r"-\d+$", "", l)
    return l.strip()


def unpointed(l):
    """Consonantes desnudas: quita vocales masoréticas, cantilación y dagesh."""
    return "".join(c for c in unicodedata.normalize("NFD", norm_lemma(l))
                   if unicodedata.category(c) != "Mn")


def script_of(s):
    for c in s:
        n = unicodedata.name(c, "")
        if "HEBREW" in n:
            return "HB"
        if "GREEK" in n:
            return "GK"
    return None


def _clean(g):
    return re.sub(r"\s+", " ", (g or "").strip()).replace(" ,", ",").strip()


class Term:
    __slots__ = ("id", "cat", "domain", "books", "gloss_en")

    def __init__(self, id, cat, domain, books, gloss_en):
        self.id, self.cat, self.domain = id, cat, domain
        self.books, self.gloss_en = books, gloss_en

    @property
    def sense(self):
        """Lo que distingue a un homógrafo de otro."""
        return (self.cat, self.domain)

    def __repr__(self):
        return f"<{self.id} {self.cat}/{self.domain}>"


class Terms:
    """Las listas Major y su localización castellana, indexadas juntas."""

    def __init__(self, lists=LISTS):
        self.major = {}
        self._by_norm = collections.defaultdict(list)
        self._by_bare = collections.defaultdict(list)

        root = ET.parse(os.path.join(lists, "BiblicalTerms.xml")).getroot()
        for t in root.findall("Term"):
            tid = nfc(t.get("Id"))     # todo el índice vive en NFC
            refs = t.find("References")
            books = {int(v.text[:3]) for v in refs.findall("Verse")} if refs is not None else set()
            term = Term(tid, (t.findtext("Category") or "").strip(),
                        (t.findtext("Domain") or "").strip(), books,
                        _clean(t.findtext("Gloss")))
            self.major[tid] = term
            self._by_norm[norm_lemma(tid)].append(term)
            self._by_bare[unpointed(tid)].append(term)

        # Localizaciones. La inglesa reproduce la glosa de Major en el 100% de
        # los Id que comparten, así que sirve de puente: cuando la española
        # vocaliza un Id de otro modo y no casa por igualdad, se busca entre sus
        # homógrafas la que en inglés significa lo mismo que el término Major
        # resuelto. Es un puente por significado, no por consonantes, y por eso
        # no confunde a Gad con el cilantro.
        self.es = self._localization(lists, "BiblicalTermsEs.xml")
        self.en = self._localization(lists, "BiblicalTermsEn.xml")
        self._es_by_bare = collections.defaultdict(list)
        for eid, g in self.es.items():
            self._es_by_bare[unpointed(eid)].append((eid, g))

    @staticmethod
    def _localization(lists, fname):
        root = ET.parse(os.path.join(lists, fname)).getroot()
        out = {}
        for L in root.find("Terms").findall("Localization"):
            g = _clean(L.get("Gloss"))
            if g:
                out[nfc(L.get("Id"))] = g
        return out

    # -- resolución -------------------------------------------------------
    def candidates(self, tid):
        """Términos Major que podrían ser este Id, del más estricto al más laxo."""
        if nfc(tid) in self.major:
            return [self.major[nfc(tid)]]
        for group in (self._by_norm.get(norm_lemma(tid)), self._by_bare.get(unpointed(tid))):
            if group:
                return list(group)
        return []

    def resolve(self, tid, books=None):
        """Término Major correspondiente, o None si la ambigüedad no se resuelve.

        `books` son los números de libro que traduce el proyecto; sirven para
        descartar homógrafos que no aparecen en ellos.
        """
        cands = self.candidates(tid)
        if not cands:
            return None
        if len(cands) > 1 and books:
            attested = [c for c in cands if c.books & books]
            if attested:
                cands = attested
        if len(cands) == 1:
            return cands[0]
        senses = {c.sense for c in cands}
        return cands[0] if len(senses) == 1 else None

    def spanish(self, tid, books=None):
        """Glosa castellana para un Id de proyecto, o None si no es segura.

        Primero por Id exacto; si la lista española vocaliza ese lema de otro
        modo, por puente con la inglesa. Nunca por consonantes a secas: eso es
        lo que hacía salir el topónimo Arabá glosado como 'álamo, sauce'.
        """
        term = self.resolve(tid, books)
        if term is None:
            return None
        if term.id in self.es:
            return self.es[term.id]
        same = {g for eid, g in self._es_by_bare.get(unpointed(term.id), [])
                if self.en.get(eid) == term.gloss_en}
        return same.pop() if len(same) == 1 else None


# -- utilidades de proyecto ----------------------------------------------
def rendering_ids(iso):
    """Id de TermRenderings.xml que tienen rendering, para el proyecto dado."""
    from kamus import config
    proj = config.load(iso)
    return rendering_ids_of(proj)


def rendering_ids_of(proj):
    path = proj.source("renderings")
    if not path:
        return []
    root = ET.parse(path).getroot()
    return [t.get("Id") for t in root.findall("TermRendering")
            if t.find("Renderings") is not None
            and (t.find("Renderings").text or "").strip()]


def project_books(proj):
    """Números de libro Paratext que traduce el proyecto ('091SAY' -> 9)."""
    from kamus import config
    return {int(k[:2]) for k in config.book_files(proj.tr) if k[:2].isdigit()}
