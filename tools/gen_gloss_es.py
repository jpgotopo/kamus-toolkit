# -*- coding: utf-8 -*-
"""Genera glosses/gloss_es.py desde la lista oficial de Paratext.

A diferencia de gloss_id.py, que está escrito a mano, el mapa español se deriva
de BiblicalTermsEs.xml — la localización castellana de la lista Major que
mantiene Paratext. Es una fuente publicada, no una conjetura nuestra.

Recibe los proyectos cuyos Id deben quedar cubiertos, porque cada proyecto puede
vocalizar los Id de otra forma que la lista (ver tools/terms.py):

    python tools/gen_gloss_es.py ame            # regenera cubriendo projects/ame
    python tools/gen_gloss_es.py ame xyz        # varios proyectos a la vez
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kamus import config
from tools import terms
from tools.terms import Terms, script_of, unpointed, nfc

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "glosses", "gloss_es.py")

# Los lemas de Yanesha que la lista española no cubre. Solo rellenan huecos: si
# la lista oficial trae el término, manda ella (glosa בְּדָן-1 como 'Barac', no
# 'Bedán', y esa es su decisión, no nuestra). La glosa es el significado estándar
# del término hebreo, tomado de la glosa inglesa de la lista Major —que se cita
# al lado— y puesto en la forma castellana usual.
#
# Los dos que no están en ninguna lista: Estemoa es la ciudad de Judá de
# 1 S 30:28, y כְּרוּב en Samuel es siempre el querubín del arca (1 S 4:4,
# 2 S 6:2, 22:11), no el topónimo de Esdras.
MANUAL = {
    "אֲרִי":          "león",                         # lion
    "אֵפֹד-2":        "efod, delantal sacerdotal",    # ephod; priestly apron
    "אֵפֹד-3":        "efod, delantal sagrado",       # ephod; sacred apron
    "אֶשְׁתְּמֹעַ-1":     "Estemoa",                      # (solo en la lista Major)
    "חַיָּה-1":        "ser viviente, animal salvaje", # living creature, wild land animal
    "יוֹנָתָן-1":       "Jonatán",                      # Jonathan
    "יצא ובוא":      "salir y entrar; dirigir",      # to lead
    "כְּרוּב-1":        "querubín",                     # cherub, cherubim
    "מַלְאָךְ-2":       "ángel",                        # angel
    "עֲרָבָה-1":       "Arabá",                        # Arabah
    "עָרֵל-1":         "incircunciso",                 # uncircumcised person
    "צְדָקָה":         "justicia, rectitud",           # right, justice
    "קֶסֶם-1":         "oráculo, adivinación",         # oracle, divination
}


def build(isos):
    T = Terms()
    entries = dict(T.es)              # clave = Id tal cual lo publica Paratext
    manual = {nfc(k): v for k, v in MANUAL.items()}
    redundant = sorted(k for k in manual if k in entries)
    resolved, unresolved = {}, []

    for iso in isos:
        proj = config.load(iso)
        books = terms.project_books(proj)
        for pid in terms.rendering_ids_of(proj):
            key = nfc(pid)
            if key in entries or key in manual:
                continue
            # la lista española no trae este Id: resuélvelo contra Major
            g = T.spanish(pid, books)
            if g:
                resolved[key] = g
            else:
                unresolved.append(pid)

    entries.update(resolved)
    for k, v in manual.items():       # MANUAL solo rellena huecos
        entries.setdefault(k, v)

    tables = {"GK": {}, "HB": {}}
    for i, g in entries.items():
        s = script_of(i)
        if s:
            tables[s][i] = g
    return tables, resolved, unresolved, redundant


def emit(tables, isos, aliases, path):
    L = [
        "# -*- coding: utf-8 -*-",
        "# Lema griego/hebreo -> glosa en español.",
        "#",
        "# GENERADO — no editar a mano. Se regenera con:",
        "#     python tools/gen_gloss_es.py " + " ".join(isos),
        "#",
        "# Fuente: BiblicalTermsEs.xml, la localización castellana oficial de la",
        "# lista Major de Paratext. Los significados NO son conjetura nuestra; lo",
        "# conjetural del nivel [B] sigue siendo el emparejamiento entre la forma",
        "# vernácula y el lema, que sale de los renderings del equipo.",
        "#",
        f"# {len(aliases)} claves se añadieron para los proyectos indicados: la lista",
        "# española vocaliza esos Id de otro modo y build.py compara cadenas exactas.",
        "# Se resolvieron término a término contra la lista Major (ver tools/terms.py),",
        "# nunca por simple coincidencia de consonantes.",
        "#",
        "# Excepciones glosadas a mano: ver MANUAL en tools/gen_gloss_es.py.",
        "",
    ]
    for name in ("GK", "HB"):
        t = tables[name]
        L.append(f"{name} = {{")
        for k in sorted(t, key=lambda s: (unpointed(s), s)):
            g = t[k].replace('"', '\\"')
            L.append(f'    "{k}": "{g}",')
        L.append("}")
        L.append("")
    open(path, "w", encoding="utf-8").write("\n".join(L))


if __name__ == "__main__":
    isos = sys.argv[1:] or ["ame"]
    tables, resolved, unresolved, redundant = build(isos)
    emit(tables, isos, resolved, OUT)
    print(f"gloss_es.py: {len(tables['GK'])} griego + {len(tables['HB'])} hebreo")
    print(f"  resueltos contra la lista Major: {len(resolved)}")
    print(f"  glosados a mano: {len(MANUAL)}")
    if redundant:
        print(f"  · {len(redundant)} de MANUAL ya están en la lista oficial y se ignoran;")
        print("    bórralos de MANUAL: " + " ".join(redundant))
    if unresolved:
        print(f"  ! {len(unresolved)} sin glosa (quedarán fuera de [B]):")
        print("    " + " ".join(unresolved))
