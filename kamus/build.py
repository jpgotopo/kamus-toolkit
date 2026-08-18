# -*- coding: utf-8 -*-
"""Construye el diccionario (md, tsv, xlsx, html) desde las fuentes del proyecto.

Portado de build_all.py. Misma lógica de niveles A/B/C; lo que cambia es que
las rutas, los nombres de lengua, la morfología y las curaciones vienen de la
configuración del proyecto en vez de estar escritos en el código.

Todas las fuentes son opcionales: si un proyecto no tiene Lexicon.xml, se
construye igual con lo que haya (y sources.py ya avisó de qué faltaba).
"""
import re, json, os, unicodedata, importlib.util
import xml.etree.ElementTree as ET

from . import config
from .locales import Strings


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def norm_lemma(l):
    # Los Id de TermRenderings y las claves del mapa de glosas pueden diferir en
    # composición Unicode o traer espacio duro en los lemas compuestos: idénticos
    # en pantalla, distintos como cadena.
    l = unicodedata.normalize("NFC", l).replace("\xa0", " ").strip()
    l = re.sub(r"\.\((?:I|II|III)\)$", "", l)
    l = re.sub(r"-\d+$", "", l)
    return l.strip()


def is_hebrew(s):
    return any("HEBREW" in unicodedata.name(c, "") for c in s)


def sortkey(s):
    t = s.lower().replace("'", "").replace("’", "").replace("-", " ")
    t = "".join(c for c in unicodedata.normalize("NFD", t)
                if unicodedata.category(c) != "Mn")
    return t.strip()


def kindtag(kinds):
    for k in ("palabra", "frase", "raiz"):
        if k in kinds:
            return k
    return "palabra"


def tier(e):
    if "leks" in e["src"]:
        return "A"
    if "alk" in e["src"]:
        return "B"
    return "C"


def gloss_for_lemma_static(lem, GK, HB):
    """¿Hay glosa para este lema griego/hebreo? (usado también por 'kamus todo')."""
    for p in re.split(r"\s*\+\s*", lem):
        k = norm_lemma(p)
        g = (HB.get(k) or HB.get(p)) if is_hebrew(p) else (GK.get(k) or GK.get(p))
        if g:
            return True
    return False


def _load_py(path, name):
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------
# fuentes
# --------------------------------------------------------------------------
def load_lexicon(path):
    """Nivel [A]: glosas del propio equipo."""
    if not path:
        return {}
    root = ET.parse(path).getroot()
    entries = root.find("Entries")
    if entries is None:
        return {}
    lexicon = {}
    for item in entries.findall("item"):
        lx = item.find("Lexeme")
        if lx is None:
            continue
        form = lx.get("Form")
        entry = item.find("Entry")
        gl = []
        if entry is not None:
            for sense in entry.findall("Sense"):
                g = sense.find("Gloss")
                if g is not None and g.text and g.text.strip() and g.text.strip() != "-":
                    gl.append(g.text.strip())
        if form and gl:
            d = lexicon.setdefault(form, [])
            for g in gl:
                if g not in d:
                    d.append(g)
    return lexicon


def load_glossary(path):
    """Nivel [A]: glosario del proyecto con definiciones."""
    if not path:
        return []
    raw = open(path, encoding="utf-8", errors="replace").read()
    glossary = []
    for ch in re.split(r"\\li\s+", raw)[1:]:
        m = re.match(r"\\k\s*(.*?)\\k\*", ch, re.S)
        if not m:
            continue
        head = m.group(1).strip()
        rest = ch[m.end():]
        mi = re.search(r"B\.\s*Ind:\s*\\it\s*(.*?)\s*\\it\*", rest, re.S)
        ind = mi.group(1).strip() if mi else ""
        defn = rest
        if mi:
            idx = rest.find(")", mi.end())
            if idx != -1:
                defn = rest[idx + 1:]
        defn = re.sub(r"\\fig.*?\\fig\*", "", defn, flags=re.S)
        defn = re.sub(r"\\bk.*?\\bk\*", "", defn, flags=re.S)
        defn = re.sub(r"\\[a-z]+\d?\*?", "", defn)
        defn = re.sub(r"\s+", " ", defn.replace("\n", " ")).strip(" :\t")
        glossary.append({"head": head, "ind": ind, "defn": defn})
    return glossary


def classify(alt):
    a = alt.strip()
    if not a:
        return None
    if "*" in a:
        form, kind = a.replace("*", "").strip(), "raiz"
    elif " " in a:
        form, kind = a, "frase"
    else:
        form, kind = a, "palabra"
    form = form.strip(" .,:;")
    if not form or not any(c.isalpha() for c in form):
        return None
    return form, kind


# --------------------------------------------------------------------------
# ensamblado
# --------------------------------------------------------------------------
def assemble(proj, verbose=True):
    """Devuelve (main, propers, glossary, counts)."""
    # curaciones del proyecto
    pm = _load_py(os.path.join(proj.root, "prop_map.py"), f"{proj.id}_prop_map")
    TERM_MOVE = getattr(pm, "TERM_MOVE", {}) if pm else {}
    PROP = getattr(pm, "PROP", {}) if pm else {}
    PROP_ID = getattr(pm, "PROP_ID", {}) if pm else {}

    # mapa de glosas griego/hebreo → lengua de glosa
    gm = _load_py(os.path.join(config.GLOSSES, proj.gloss_map + ".py"), proj.gloss_map)
    GK = getattr(gm, "GK", {}) if gm else {}
    HB = getattr(gm, "HB", {}) if gm else {}

    def gloss_for_lemma(lem):
        outs = []
        for p in re.split(r"\s*\+\s*", lem):
            k = norm_lemma(p)
            g = (HB.get(k) or HB.get(p)) if is_hebrew(p) else (GK.get(k) or GK.get(p))
            if g:
                outs.append(g)
        return outs or None

    lexicon = load_lexicon(proj.source("lexicon"))
    glossary = load_glossary(proj.source("glossary") or _autoglossary(proj))

    main, propers = {}, {}

    # semilla: léxico del equipo (A)
    for form, gl in lexicon.items():
        e = main.setdefault(form, {"glosses": [], "src": set(), "kinds": set(), "lemmas": []})
        e["src"].add("leks"); e["kinds"].add("palabra")
        for g in gl:
            if g not in e["glosses"]:
                e["glosses"].append(g)

    # renderings del equipo (B)
    ren_path = proj.source("renderings")
    if ren_path and (GK or HB):
        tr = ET.parse(ren_path).getroot()
        for t in tr.findall("TermRendering"):
            ren = t.find("Renderings")
            if ren is None or not ren.text or not ren.text.strip():
                continue
            lid = t.get("Id")
            gl = gloss_for_lemma(lid)
            for alt in ren.text.strip().split("||"):
                c = classify(alt)
                if not c:
                    continue
                form, kind = c
                if form[:1].islower():
                    if not gl:
                        continue
                    e = main.setdefault(form, {"glosses": [], "src": set(), "kinds": set(), "lemmas": []})
                    e["src"].add("alk"); e["kinds"].add(kind)
                    if lid not in e["lemmas"]:
                        e["lemmas"].append(lid)
                    for g in gl:
                        for piece in g.split(", "):
                            piece = piece.strip()
                            if piece and piece not in e["glosses"]:
                                e["glosses"].append(piece)
                elif form in TERM_MOVE:
                    e = main.setdefault(form, {"glosses": [], "src": set(), "kinds": set(), "lemmas": []})
                    e["src"].add("alk"); e["kinds"].add(kind)
                    if lid not in e["lemmas"]:
                        e["lemmas"].append(lid)
                    for piece in TERM_MOVE[form].split(", "):
                        piece = piece.strip()
                        if piece and piece not in e["glosses"]:
                            e["glosses"].append(piece)
                else:
                    e = propers.setdefault(form, {"kinds": set(), "lemmas": []})
                    e["kinds"].add(kind)
                    if lid not in e["lemmas"]:
                        e["lemmas"].append(lid)

    # corpus (C)
    cpath = proj.workfile("corpus_lexicon.json")
    corpus = json.load(open(cpath, encoding="utf-8")) if os.path.exists(cpath) else {}
    for w, cinfo in corpus.items():
        if cinfo["conf"] not in ("alta", "media"):
            continue
        if w in main:
            main[w]["corpus"] = cinfo
        elif cinfo.get("name"):
            if w not in propers:
                propers[w] = {"kinds": {"palabra"}, "lemmas": [], "src": "corpus",
                              "ind": cinfo["gloss"][0]}
        else:
            e = main.setdefault(w, {"glosses": [], "src": set(), "kinds": set(), "lemmas": []})
            e["src"].add("corpus"); e["kinds"].add("frase" if " " in w else "palabra")
            e["corpus"] = cinfo
            for g in cinfo["gloss"]:
                if g not in e["glosses"]:
                    e["glosses"].append(g)

    counts = {
        "main": len(main),
        "A": sum(1 for e in main.values() if tier(e) == "A"),
        "B": sum(1 for e in main.values() if tier(e) == "B"),
        "C": sum(1 for e in main.values() if tier(e) == "C"),
        "glos": len(glossary),
        "prop": len(propers),
    }
    if verbose:
        print(f"MAIN: {counts['main']}  A: {counts['A']}  B: {counts['B']}  C: {counts['C']}"
              f"  | glossary: {counts['glos']}  propers: {counts['prop']}")
    return main, propers, glossary, counts, (PROP, PROP_ID)


def _autoglossary(proj):
    from .sources import detect_glossary
    found = detect_glossary(proj.tr["dir"], proj.tr["postpart"])
    return found[0] if found else None


def load_morphology(proj):
    """Apéndice morfológico: específico de cada lengua, opcional."""
    p = os.path.join(proj.root, "morphology.json")
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding="utf-8"))


def source_list(proj):
    names = []
    for key in ("lexicon", "glossary", "renderings"):
        p = proj.source(key)
        if p:
            names.append(os.path.basename(p))
    if proj.bt:
        names.append(f"korpus {proj.tr['name']}↔{proj.bt['name']} (IBM Model 1)")
    return ", ".join(names) or "—"
