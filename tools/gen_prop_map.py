# -*- coding: utf-8 -*-
"""Genera projects/<iso>/prop_map.py desde la lista Major de Paratext.

    python tools/gen_prop_map.py ame

Los renderings del equipo llegan a build.py como una lista plana de formas; las
que empiezan por mayúscula acaban en la sección de nombres propios sin tipo ni
forma castellana. Pero el lema hebreo de cada una sí trae esa información en la
lista Major: Category dice si es un nombre propio (PN) y Domain de qué clase es.

Rellena los tres diccionarios que espera build.py:

  PROP       forma -> orang / tempat / bangsa / lain   (solo Category=PN)
  PROP_ID    forma -> forma castellana estándar        (glosa de BiblicalTermsEs)
  TERM_MOVE  forma -> glosa                            (Category != PN: no son
             nombres propios sino términos que quedaron capitalizados en el
             rendering; build.py los devuelve al diccionario principal)

El fichero se sobreescribe entero, así que si luego corriges una entrada a mano
guárdala en OVERRIDE aquí abajo en vez de en la salida.
"""
import os, sys, collections

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import terms
from tools.terms import Terms

# Domain de la lista Major -> tipo del toolkit. Los Domain compuestos
# ("person; area") se resuelven por su primer componente.
DOMAIN2TYPE = {
    "person":     "orang",
    "settlement": "tempat",
    "locale":     "tempat",
    "area":       "tempat",
    "nature":     "tempat",
    "group":      "bangsa",
    "language":   "bangsa",
}

# Correcciones a mano, si alguna hiciera falta: forma -> tipo.
OVERRIDE = {}


def type_for(domain):
    first = domain.split(";")[0].strip().lower()
    return DOMAIN2TYPE.get(first, "lain")


def _gloss_map(proj):
    """GK+HB del mapa de glosas del proyecto, ya generado."""
    import importlib.util
    from kamus import config
    path = os.path.join(config.GLOSSES, proj.gloss_map + ".py")
    if not os.path.exists(path):
        raise SystemExit(f"Falta {path}: genera antes el mapa de glosas.")
    spec = importlib.util.spec_from_file_location(proj.gloss_map, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {**getattr(mod, "GK", {}), **getattr(mod, "HB", {})}


def build(iso):
    from kamus import config, build as kbuild
    proj = config.load(iso)

    # se ensambla SIN prop_map para ver el reparto crudo de formas
    pm = os.path.join(proj.root, "prop_map.py")
    tmp = pm + ".off"
    had = os.path.exists(pm)
    if had:
        os.replace(pm, tmp)
    try:
        main, propers, _glo, _counts, _pmaps = kbuild.assemble(proj, verbose=False)
    finally:
        if had:
            os.replace(tmp, pm)

    T = Terms()
    books = terms.project_books(proj)
    # las glosas se leen del mapa ya generado, que incluye las manuales
    GL = _gloss_map(proj)

    PROP, PROP_ID, TERM_MOVE = {}, {}, {}
    stats = collections.Counter()
    unknown = []

    for form, pe in sorted(propers.items()):
        lemmas = pe.get("lemmas") or []
        term = next((t for t in (T.resolve(l, books) for l in lemmas) if t), None)
        gloss = next((g for g in (GL.get(terms.nfc(l)) for l in lemmas) if g), None)

        if term is None:
            unknown.append(form)
            stats["sin lema en la lista"] += 1
            continue

        category, domain = term.cat, term.domain
        if category == "PN":
            t = OVERRIDE.get(form) or type_for(domain)
            PROP[form] = t
            stats[t] += 1
            # la forma castellana solo aporta si difiere de la vernácula
            if gloss and gloss.lower() != form.lower():
                PROP_ID[form] = gloss
        elif gloss:
            TERM_MOVE[form] = gloss
            stats["TERM_MOVE"] += 1
        else:
            unknown.append(form)
            stats["sin glosa castellana"] += 1

    return proj, PROP, PROP_ID, TERM_MOVE, stats, unknown


def emit(proj, PROP, PROP_ID, TERM_MOVE, unknown, iso):
    def block(name, d, comment):
        L = [comment, f"{name} = {{"]
        if d:
            w = max(len(k) for k in d) + 3
            for k in sorted(d):
                L.append(f'    "{k}":'.ljust(w + 9) + f' "{d[k]}",')
        L.append("}")
        return L

    L = [
        "# -*- coding: utf-8 -*-",
        f"# Nombres propios y términos capitalizados de {proj.lang_name}.",
        "#",
        "# GENERADO — no editar a mano. Se regenera con:",
        f"#     python tools/gen_prop_map.py {iso}",
        "# Las correcciones van en OVERRIDE, dentro de ese script.",
        "#",
        "# Tipos y formas castellanas derivados de Category/Domain de la lista Major",
        "# de Paratext y de la glosa de BiblicalTermsEs.xml.",
        "",
    ]
    L += block("PROP", PROP,
               "# forma -> persona (orang) / lugar (tempat) / pueblo (bangsa) / otros (lain)")
    L.append("")
    L += block("PROP_ID", PROP_ID,
               "# forma -> forma castellana estándar (solo cuando difiere de la vernácula)")
    L.append("")
    L += block("TERM_MOVE", TERM_MOVE,
               "# capitalizadas que NO son nombres propios: vuelven al diccionario principal")
    L.append("")
    if unknown:
        L.append("# Sin datos en la lista Major, se quedan como 'otros' sin forma castellana:")
        for f in unknown:
            L.append(f"#   {f}")
        L.append("")
    path = os.path.join(proj.root, "prop_map.py")
    open(path, "w", encoding="utf-8").write("\n".join(L))
    return path


if __name__ == "__main__":
    iso = sys.argv[1] if len(sys.argv) > 1 else "ame"
    proj, PROP, PROP_ID, TERM_MOVE, stats, unknown = build(iso)
    path = emit(proj, PROP, PROP_ID, TERM_MOVE, unknown, iso)
    print(f"escrito {path}")
    print(f"  PROP: {len(PROP)}  ·  PROP_ID: {len(PROP_ID)}  ·  TERM_MOVE: {len(TERM_MOVE)}")
    for k, v in stats.most_common():
        print(f"    {k:24s} {v}")
    if unknown:
        print(f"  ! {len(unknown)} sin resolver: {' '.join(unknown)}")
