# -*- coding: utf-8 -*-
"""Genera la herramienta interlineal bidireccional (portado de make_interlinear.py)."""
import json, os
from collections import defaultdict

from . import config

LVW = {"A": 1.0, "B": 0.9, "C": 0.75}   # peso por nivel de confianza


def build(proj, S, verbose=True):
    dumpf = proj.workfile("dict_dump.json")
    alignf = proj.workfile("align_result.json")
    if not os.path.exists(dumpf):
        raise SystemExit("Falta dict_dump.json: construye primero el diccionario.")
    dump = json.load(open(dumpf, encoding="utf-8"))
    align = (json.load(open(alignf, encoding="utf-8"))["results"]
             if os.path.exists(alignf) else {})

    # ---------- vernáculo -> glosa ----------
    src2gl = {}

    def add(form, gloss, w):
        form, gloss = form.lower().strip(), gloss.strip()
        if not form or not gloss:
            return
        lst = src2gl.setdefault(form, [])
        for i, (g, ww) in enumerate(lst):
            if g == gloss:
                if w > ww:
                    lst[i] = (g, w)
                return
        lst.append((gloss, w))

    for form, info in dump["main"].items():
        w = LVW.get(info["lv"], 0.7)
        for g in info["g"][:4]:
            for piece in g.split("; "):
                add(form, piece, w)
    for form, idn in dump["prop"].items():
        add(form, idn, 0.95)

    # el corpus cubre formas flexionadas de superficie que el diccionario no lista
    for ws, info in align.items():
        if info["freq"] < 2 or not info["cands"]:
            continue
        for wt, p, co, d in info["cands"][:2]:
            if p >= 0.20 and co >= 2:
                add(ws, wt, min(0.7, 0.3 + p * 0.4))

    for form in src2gl:
        src2gl[form].sort(key=lambda x: -x[1])
        src2gl[form] = [g for g, _ in src2gl[form][:4]]

    # ---------- glosa -> vernáculo ----------
    gl2src = defaultdict(list)
    freq_src = {ws: align[ws]["freq"] for ws in align}
    for form, info in dump["main"].items():
        w = LVW.get(info["lv"], 0.7)
        for g in info["g"][:4]:
            for piece in g.split("; "):
                piece = piece.lower().strip()
                if piece:
                    gl2src[piece].append((form, w + freq_src.get(form, 0) / 5000.0))
    for form, idn in dump["prop"].items():
        gl2src[idn.lower()].append((form, 0.95))
    for ws, info in align.items():
        if info["freq"] < 2:
            continue
        for wt, p, co, d in info["cands"][:2]:
            if p >= 0.25 and co >= 3:
                gl2src[wt.lower()].append((ws, 0.3 + p * 0.4 + info["freq"] / 5000.0))

    gl2src_final = {}
    for k, lst in gl2src.items():
        best = {}
        for s, w in lst:
            if s not in best or w > best[s]:
                best[s] = w
        gl2src_final[k] = [s for s, _ in sorted(best.items(), key=lambda x: -x[1])[:5]]

    if verbose:
        print(f"{proj.lang_iso or 'src'}->{proj.gloss_iso} entradas: {len(src2gl)}")
        print(f"{proj.gloss_iso}->{proj.lang_iso or 'src'} entradas: {len(gl2src_final)}")

    DATA = {"t2i": src2gl, "i2t": gl2src_final}
    tpl = open(os.path.join(config.TEMPLATES, "interlinear.html"), encoding="utf-8").read()
    # afijos del vernáculo: los declara el proyecto (morfología propia de la lengua)
    il_cfg = proj.cfg.get("interlinear", {})
    src_suffixes = il_cfg.get("source_suffixes", [])
    src_prefixes = il_cfg.get("source_prefixes", [])
    subs = {
        "__DATA__": json.dumps(DATA, ensure_ascii=False, separators=(",", ":")),
        "__UI__": json.dumps(S.ui_interlinear(), ensure_ascii=False),
        "__SRC_SUFFIXES__": json.dumps(src_suffixes, ensure_ascii=False),
        "__SRC_PREFIXES__": json.dumps(src_prefixes, ensure_ascii=False),
        "__GLOSS_SUFFIXES__": json.dumps(S.d.get("gloss_suffixes", []), ensure_ascii=False),
        "__GLOSS_PREFIXES__": json.dumps(S.d.get("gloss_prefixes", []), ensure_ascii=False),
        "__GLOSS_ISO__": proj.gloss_iso or "id",
        "__TITLE__": S("il_title"),
        "__SUB__": S("il_sub"),
        "__DIR_T2I__": S("il_dir_t2i"),
        "__DIR_I2T__": S("il_dir_i2t"),
        "__LINK_KAMUS__": S("link_to_kamus"),
        "__KAMUS_FILE__": proj.basename + ".html",
    }
    for k, v in subs.items():
        tpl = tpl.replace(k, v)

    path = proj.out("html", interlinear=True)
    open(path, "w", encoding="utf-8").write(tpl)
    if verbose:
        print(f"escrito {os.path.basename(path)} ({len(tpl)} chars)")
    return path
