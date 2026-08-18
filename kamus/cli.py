# -*- coding: utf-8 -*-
"""Interfaz de línea de comandos del toolkit.

    python -m kamus detect  [carpeta…]      busca proyectos Paratext
    python -m kamus check   <proyecto>      qué niveles A/B/C son alcanzables
    python -m kamus align   <proyecto>      solo el nivel C (lento)
    python -m kamus build   <proyecto>      diccionario + interlineal
    python -m kamus todo    <proyecto>      qué falta por curar
    python -m kamus publish <proyecto>      copia al repo, commit y push
    python -m kamus all     <proyecto>      align + build + publish
"""
import sys, os, argparse, json

from . import config, sources, align, build, render, interlinear, publish
from .locales import Strings


def cmd_detect(args):
    dirs = args.dirs or [os.path.join(os.path.expanduser("~"), "Documents")]
    found = config.find_projects(dirs)
    if not found:
        print("No se encontró ningún proyecto Paratext en:", ", ".join(dirs))
        return
    print(f"{len(found)} proyecto(s) Paratext:\n")
    for s in found:
        tag = f"  (subcarpeta de {s['parent']})" if s.get("parent") else ""
        print(f"  {s['name']:<14} {s['iso'] or '?':<6} {s['full_name'] or ''}{tag}")
        print(f"    {s['dir']}")
        print(f"    ficheros: {s['prepart']}*{s['postpart']}")
    print("\nPara crear un proyecto del toolkit copia projects/_ejemplo/project.json")


def cmd_check(args):
    proj = config.load(args.project)
    inv = sources.inventory(proj)
    print(sources.report(proj, inv))
    return inv


def cmd_align(args):
    proj = config.load(args.project)
    if not proj.bt:
        raise SystemExit("Este proyecto no tiene retrotraducción: no hay nivel [C].")
    align.run(proj, iters=args.iters)


def cmd_build(args):
    proj = config.load(args.project)
    inv = sources.inventory(proj)
    for w in inv["warnings"]:
        print("  !", w)

    cpath = proj.workfile("corpus_lexicon.json")
    if inv["tiers"]["C"] and not os.path.exists(cpath):
        print("\nNo hay alineamiento previo; ejecutando el nivel [C] (puede tardar)…")
        align.run(proj)

    main, propers, glossary, counts, propmaps = build.assemble(proj)
    S = Strings(proj, {"n_main": counts["main"], "n_A": counts["A"], "n_B": counts["B"],
                       "n_C": counts["C"], "n_glos": counts["glos"], "n_prop": counts["prop"]})

    print("\nEscribiendo salidas:")
    for fn in (render.markdown(proj, S, main, propers, glossary, counts, propmaps),
               render.tsv(proj, S, main),
               render.xlsx(proj, S, main, propers, glossary, counts, propmaps),
               render.html(proj, S, main, propers, glossary, counts, propmaps)):
        if fn:
            print("  ", os.path.basename(fn))
    render.dump(proj, main, propers, propmaps)
    interlinear.build(proj, S)
    print("\nSalidas en:", proj.out_dir)
    return proj, S, counts


def cmd_todo(args):
    """Lemas sin glosar y nombres propios sin clasificar: la cola de curación."""
    import xml.etree.ElementTree as ET
    import re
    proj = config.load(args.project)
    gm = build._load_py(os.path.join(config.GLOSSES, proj.gloss_map + ".py"), proj.gloss_map)
    GK = getattr(gm, "GK", {}) if gm else {}
    HB = getattr(gm, "HB", {}) if gm else {}

    ren = proj.source("renderings")
    if not ren:
        print("Sin TermRenderings.xml: nada que curar en el nivel [B].")
        return
    tr = ET.parse(ren).getroot()
    missing = []
    for t in tr.findall("TermRendering"):
        r = t.find("Renderings")
        if r is None or not r.text or not r.text.strip():
            continue
        lid = t.get("Id")
        if build.gloss_for_lemma_static(lid, GK, HB):
            continue
        forms = [build.classify(a) for a in r.text.strip().split("||")]
        forms = [f[0] for f in forms if f and f[0][:1].islower()]
        if forms:
            missing.append((lid, forms))

    pm = build._load_py(os.path.join(proj.root, "prop_map.py"), f"{proj.id}_pm")
    PROP = getattr(pm, "PROP", {}) if pm else {}

    print(f"Lemas griego/hebreo SIN glosa en {proj.gloss_map}.py: {len(missing)}")
    print("(cada uno bloquea entradas [B] que ya tienen rendering del equipo)\n")
    for lid, forms in missing[:args.limit]:
        print(f'  "{lid}": "",'.ljust(42) + f"# → {', '.join(forms[:4])}")
    if len(missing) > args.limit:
        print(f"  … y {len(missing)-args.limit} más (usa --limit)")

    out = proj.workfile("todo_glosas.json")
    json.dump({lid: forms for lid, forms in missing}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\nLista completa: {out}")
    print(f"Nombres propios sin tipo en prop_map.py: "
          f"{'(no hay prop_map.py)' if not pm else 'PROP tiene ' + str(len(PROP)) + ' clasificados'}")


def cmd_publish(args):
    proj = config.load(args.project)
    if not os.path.exists(proj.out("html")):
        raise SystemExit("No hay salidas todavía: ejecuta 'build' primero.")
    main, propers, glossary, counts, propmaps = build.assemble(proj, verbose=False)
    S = Strings(proj, {"n_main": counts["main"], "n_A": counts["A"], "n_B": counts["B"],
                       "n_C": counts["C"], "n_glos": counts["glos"], "n_prop": counts["prop"]})
    repo, copied = publish.prepare(proj, S, counts)
    print("Repo:", repo)
    for c in copied:
        print("  ", c)
    url = publish.push(proj, args.message)
    if url:
        publish.enable_pages(proj)


def cmd_all(args):
    cmd_align(args)
    cmd_build(args)
    cmd_publish(args)


def main(argv=None):
    p = argparse.ArgumentParser(prog="kamus", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("detect"); d.add_argument("dirs", nargs="*"); d.set_defaults(f=cmd_detect)
    c = sub.add_parser("check"); c.add_argument("project"); c.set_defaults(f=cmd_check)
    a = sub.add_parser("align"); a.add_argument("project")
    a.add_argument("--iters", type=int, default=8); a.set_defaults(f=cmd_align)
    b = sub.add_parser("build"); b.add_argument("project"); b.set_defaults(f=cmd_build)
    t = sub.add_parser("todo"); t.add_argument("project")
    t.add_argument("--limit", type=int, default=40); t.set_defaults(f=cmd_todo)
    pu = sub.add_parser("publish"); pu.add_argument("project")
    pu.add_argument("-m", "--message"); pu.set_defaults(f=cmd_publish)
    al = sub.add_parser("all"); al.add_argument("project")
    al.add_argument("--iters", type=int, default=8)
    al.add_argument("-m", "--message"); al.set_defaults(f=cmd_all)

    args = p.parse_args(argv)
    args.f(args)


if __name__ == "__main__":
    main()
