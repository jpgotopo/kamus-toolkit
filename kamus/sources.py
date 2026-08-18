# -*- coding: utf-8 -*-
"""Inventario de fuentes: qué tiene el proyecto y qué niveles A/B/C son posibles.

Se ejecuta ANTES de construir. Un equipo que no mantiene Lexicon.xml no puede
tener nivel [A] por mucho que corramos el pipeline; más vale saberlo antes.
"""
import os, re, glob, importlib.util
import xml.etree.ElementTree as ET

from . import config


def _count_lexicon(path):
    try:
        root = ET.parse(path).getroot()
        entries = root.find("Entries")
        if entries is None:
            return 0
        n = 0
        for item in entries.findall("item"):
            e = item.find("Entry")
            if e is None:
                continue
            for s in e.findall("Sense"):
                g = s.find("Gloss")
                if g is not None and g.text and g.text.strip() not in ("", "-"):
                    n += 1
                    break
        return n
    except ET.ParseError:
        return 0


def _count_renderings(path):
    try:
        root = ET.parse(path).getroot()
        return sum(1 for t in root.findall("TermRendering")
                   if t.find("Renderings") is not None
                   and (t.find("Renderings").text or "").strip())
    except ET.ParseError:
        return 0


def detect_glossary(project_dir, postpart):
    """Un glosario Paratext es un SFM con marcadores \\k …\\k* (entradas de glosario)."""
    cands = []
    for f in glob.glob(os.path.join(project_dir, "*.SFM")):
        base = os.path.basename(f)
        if not re.match(r"\d", base):        # los libros bíblicos empiezan por número
            try:
                head = open(f, encoding="utf-8", errors="replace").read(20000)
            except OSError:
                continue
            if "\\k " in head or "\\k\t" in head:
                cands.append(f)
    return cands


def gloss_map_entries(gloss_map_name):
    """Carga glosses/<name>.py y cuenta lemas griegos/hebreos disponibles."""
    path = os.path.join(config.GLOSSES, gloss_map_name + ".py")
    if not os.path.exists(path):
        return None, 0, 0
    spec = importlib.util.spec_from_file_location(gloss_map_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, len(getattr(mod, "GK", {})), len(getattr(mod, "HB", {}))


def inventory(proj):
    """Devuelve un dict con lo encontrado y los niveles alcanzables."""
    inv = {"tiers": {}, "notes": [], "warnings": []}

    # --- fuentes de nivel A ---
    lex = proj.source("lexicon")
    inv["lexicon"] = {"path": lex, "entries": _count_lexicon(lex) if lex else 0}

    glo = proj.source("glossary")
    if not glo:
        found = detect_glossary(proj.tr["dir"], proj.tr["postpart"])
        if found:
            glo = found[0]
            inv["notes"].append(
                f"Glosario detectado automáticamente: {os.path.basename(glo)}"
                + (f" (+{len(found)-1} más)" if len(found) > 1 else ""))
    inv["glossary"] = {"path": glo}

    # --- fuentes de nivel B ---
    ren = proj.source("renderings")
    inv["renderings"] = {"path": ren, "terms": _count_renderings(ren) if ren else 0}
    mod, ngk, nhb = gloss_map_entries(proj.gloss_map)
    inv["gloss_map"] = {"name": proj.gloss_map, "found": mod is not None,
                        "gk": ngk, "hb": nhb}

    # --- fuentes de nivel C ---
    tr_books = config.book_files(proj.tr)
    bt_books = config.book_files(proj.bt) if proj.bt else {}
    common = sorted(set(tr_books) & set(bt_books))
    inv["books"] = {"translation": len(tr_books), "backtranslation": len(bt_books),
                    "parallel": common}

    # --- curaciones específicas del proyecto ---
    inv["prop_map"] = os.path.exists(os.path.join(proj.root, "prop_map.py"))
    inv["morphology"] = os.path.exists(os.path.join(proj.root, "morphology.json"))

    # --- veredicto por nivel ---
    inv["tiers"]["A"] = bool(inv["lexicon"]["entries"] or glo)
    inv["tiers"]["B"] = bool(ren and mod and inv["renderings"]["terms"])
    inv["tiers"]["C"] = len(common) > 0

    if not inv["tiers"]["A"]:
        inv["warnings"].append(
            "Sin Lexicon.xml con glosas ni glosario: no habrá entradas [A] verificadas.")
    if not inv["tiers"]["B"]:
        if not ren:
            inv["warnings"].append("Sin TermRenderings.xml: no habrá entradas [B].")
        elif not mod:
            inv["warnings"].append(
                f"Falta glosses/{proj.gloss_map}.py (lema griego/hebreo → {proj.gloss_name}): no habrá [B].")
    if not inv["tiers"]["C"]:
        if not proj.bt:
            inv["warnings"].append("Sin retrotraducción configurada: no habrá entradas [C].")
        else:
            inv["warnings"].append(
                "Traducción y retrotraducción no comparten ningún libro: no habrá [C].")
    elif len(common) < 3:
        inv["warnings"].append(
            f"Solo {len(common)} libro(s) paralelo(s): el nivel [C] será pobre y poco fiable.")

    if not any(inv["tiers"].values()):
        inv["warnings"].append("NINGÚN nivel es alcanzable — no tiene sentido construir.")
    return inv


def report(proj, inv):
    """Informe legible para el usuario."""
    L = []
    A = L.append
    A(f"Proyecto: {proj.id}")
    A(f"  Traducción     : {proj.tr['name']} — {proj.tr['full_name'] or '(sin FullName)'} "
      f"[{proj.tr['iso'] or '?'}]  ·  {inv['books']['translation']} libros SFM")
    if proj.bt:
        A(f"  Retrotraducción: {proj.bt['name']} — {proj.bt['full_name'] or '(sin FullName)'} "
          f"[{proj.bt['iso'] or '?'}]  ·  {inv['books']['backtranslation']} libros SFM")
    else:
        A("  Retrotraducción: (ninguna configurada)")
    A("")
    A("Fuentes encontradas:")
    lx = inv["lexicon"]
    A(f"  [A] Lexicon.xml      : {lx['entries']} lemas glosados" if lx["path"]
      else "  [A] Lexicon.xml      : NO")
    A(f"  [A] Glosario         : {os.path.basename(inv['glossary']['path'])}" if inv["glossary"]["path"]
      else "  [A] Glosario         : NO")
    rn = inv["renderings"]
    A(f"  [B] TermRenderings   : {rn['terms']} términos con rendering" if rn["path"]
      else "  [B] TermRenderings   : NO")
    gm = inv["gloss_map"]
    A(f"  [B] Mapa de glosas   : {gm['name']} ({gm['gk']} griego + {gm['hb']} hebreo)" if gm["found"]
      else f"  [B] Mapa de glosas   : NO ({gm['name']}.py no existe)")
    bk = inv["books"]
    A(f"  [C] Libros paralelos : {len(bk['parallel'])} → {', '.join(bk['parallel']) or '—'}")
    A(f"  Curación propia      : prop_map.py {'sí' if inv['prop_map'] else 'no'} · "
      f"morphology.json {'sí' if inv['morphology'] else 'no'}")
    A("")
    ok = [t for t in "ABC" if inv["tiers"][t]]
    no = [t for t in "ABC" if not inv["tiers"][t]]
    A(f"Niveles alcanzables: {', '.join('['+t+']' for t in ok) or 'NINGUNO'}"
      + (f"   ·   no alcanzables: {', '.join('['+t+']' for t in no)}" if no else ""))
    for w in inv["warnings"]:
        A(f"  ! {w}")
    for n in inv["notes"]:
        A(f"  · {n}")
    return "\n".join(L)
