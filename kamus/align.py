# -*- coding: utf-8 -*-
"""Nivel [C]: alineamiento estadístico traducción ↔ retrotraducción.

Portado de align_extract.py + align_model1.py + align_build.py, parametrizado.
Los algoritmos y umbrales son los mismos; solo cambian las rutas y los patrones
de fichero, que ahora salen de Settings.xml.

Es la parte del pipeline que funciona con cualquier par de lenguas: no sabe nada
del vernáculo, solo cuenta co-ocurrencias en versículos paralelos.
"""
import re, os, json
from collections import defaultdict, Counter

from . import config

NULL = "<NULL>"


# --------------------------------------------------------------------------
# 1. Extracción de versículos paralelos
# --------------------------------------------------------------------------
def strip_markers(t):
    t = re.sub(r"\\[fx]\b.*?\\[fx]\*", " ", t)   # notas al pie / referencias
    t = re.sub(r"\|[^\\]*?\\w\*", " ", t)        # atributos de palabra
    t = re.sub(r"\\[a-z0-9]+\*", " ", t)         # marcadores de cierre
    t = re.sub(r"\\[a-z0-9]+\b", " ", t)         # marcadores de apertura
    return t.replace("*", " ")


SKIP_MARKERS = r"\\(c|v|id|mt|ms|mr|s\d?|r|h|toc|ip|ili|imt|ide|periph)\b"
BREAK_MARKERS = r"\\(s\d?|r|ms|mr)\b"


def parse_verses(path):
    """{(capítulo, versículo): texto} de un fichero SFM."""
    out, chap, cur_ref, buf = {}, None, None, []

    def flush():
        nonlocal buf, cur_ref
        if cur_ref and buf:
            out[cur_ref] = strip_markers(" ".join(buf))
        buf = []

    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        mc = re.match(r"\\c\s+(\d+)", line)
        if mc:
            flush(); cur_ref = None; chap = int(mc.group(1)); continue
        mv = re.match(r"\\v\s+(\d+[ab]?)\s?(.*)", line)
        if mv:
            flush()
            if chap is not None:
                cur_ref = (chap, mv.group(1))
                buf = [mv.group(2)]
            continue
        if cur_ref is not None and not re.match(SKIP_MARKERS, line):
            if line.startswith("\\"):
                m = re.match(r"\\[a-z0-9]+\s*(.*)", line)
                if m and m.group(1).strip():
                    buf.append(m.group(1))
            else:
                buf.append(line)
        elif re.match(BREAK_MARKERS, line):
            flush(); cur_ref = None
    flush()
    return out


def clean_tokens(text):
    text = text.lower()
    text = re.sub(r"[“”‘’\"()\[\]{}.,:;!?—–\-/|]", " ", text)
    toks = [w.strip("'") for w in text.split()]
    return [w for w in toks if w and any(c.isalpha() for c in w)]


def extract(proj, verbose=True):
    """Construye el bitext de versículos paralelos."""
    tr_files = config.book_files(proj.tr)
    bt_files = config.book_files(proj.bt)
    books = sorted(set(tr_files) & set(bt_files))
    if verbose:
        print("libros en ambos:", books)

    pairs, stats = [], {}
    for bk in books:
        tv = parse_verses(tr_files[bk])
        bv = parse_verses(bt_files[bk])
        common = sorted(set(tv) & set(bv))
        n = 0
        for ref in common:
            s = clean_tokens(tv[ref])
            t = clean_tokens(bv[ref])
            if 0 < len(s) <= 80 and 0 < len(t) <= 80:
                pairs.append([s, t]); n += 1
        stats[bk] = (len(tv), len(bv), len(common), n)

    if verbose:
        print("\nlibro: (vers_trad, vers_rt, comunes, usados)")
        for bk in books:
            print(f"  {bk}: {stats[bk]}")
        print("\nTOTAL pares de versículos:", len(pairs))
        sv = Counter(w for s, _ in pairs for w in s)
        tv_ = Counter(w for _, t in pairs for w in t)
        print(f"vocab {proj.lang_name} (tipos): {len(sv)}  tokens: {sum(sv.values())}")
        print(f"vocab {proj.gloss_name} (tipos): {len(tv_)}  tokens: {sum(tv_.values())}")

    json.dump(pairs, open(proj.workfile("bitext.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    return pairs


# --------------------------------------------------------------------------
# 2. IBM Model 1 (EM) + coeficiente de Dice
# --------------------------------------------------------------------------
def model1(proj, pairs=None, iters=8, verbose=True):
    if pairs is None:
        pairs = json.load(open(proj.workfile("bitext.json"), encoding="utf-8"))

    src_f = Counter(w for s, _ in pairs for w in s)
    cooc = defaultdict(Counter)
    src_sent, tgt_sent = defaultdict(int), defaultdict(int)
    for s, t in pairs:
        for w in set(s): src_sent[w] += 1
        for w in set(t): tgt_sent[w] += 1
        for ws in set(s):
            for wt in set(t):
                cooc[ws][wt] += 1

    # init uniforme sobre candidatos observados
    t = {}
    for ws, c in cooc.items():
        n = len(c) + 1
        t[ws] = {wt: 1.0 / n for wt in c}
    t[NULL] = defaultdict(lambda: 1e-6)

    for it in range(iters):
        count = defaultdict(lambda: defaultdict(float))
        total = defaultdict(float)
        for s, t_sent in pairs:
            s2 = s + [NULL]
            for wt in t_sent:
                denom = 0.0
                for ws in s2:
                    denom += t.get(ws, {}).get(wt, 1e-6 if ws == NULL else 0.0)
                if denom == 0:
                    continue
                for ws in s2:
                    p = t.get(ws, {}).get(wt, 1e-6 if ws == NULL else 0.0)
                    if p == 0:
                        continue
                    c = p / denom
                    count[ws][wt] += c
                    total[ws] += c
        newt = {}
        for ws, cc in count.items():
            tot = total[ws]
            if tot <= 0:
                continue
            newt[ws] = {wt: v / tot for wt, v in cc.items()}
        t = newt
        if NULL not in t:
            t[NULL] = defaultdict(lambda: 1e-6)
        if verbose:
            print(f"iter {it+1}/{iters} listo")

    def dice(ws, wt):
        a = cooc[ws][wt]
        denom = src_sent[ws] + tgt_sent[wt]
        return 2 * a / denom if denom else 0

    results = {}
    for ws in src_f:
        if ws == NULL:
            continue
        ranked = []
        for wt, p in t.get(ws, {}).items():
            if wt == NULL:
                continue
            ranked.append((wt, p, cooc[ws][wt], dice(ws, wt)))
        ranked.sort(key=lambda x: (x[1] * x[3]), reverse=True)
        results[ws] = {"freq": src_f[ws], "cands": ranked[:6]}

    json.dump({"results": results},
              open(proj.workfile("align_result.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    if verbose:
        print("guardado align_result.json  (palabras fuente:", len(results), ")")
    return results


# --------------------------------------------------------------------------
# 3. Convertir el alineamiento en entradas [C]
# --------------------------------------------------------------------------
def detect_names(proj):
    """Tokens de la RT que son nombres propios (mayúscula dominante)."""
    cap, tot = Counter(), Counter()
    for fn in config.book_files(proj.bt).values():
        for line in open(fn, encoding="utf-8", errors="replace"):
            if not re.match(r"\\v\s", line):
                continue
            for m in re.finditer(r"[A-Za-zÀ-ÿ']+", strip_markers(line)):
                w = m.group(0)
                lw = w.lower(); tot[lw] += 1
                if w[:1].isupper():
                    cap[lw] += 1
    return {w for w in tot if tot[w] >= 3 and cap[w] / tot[w] >= 0.75}


def build_tier_c(proj, results=None, verbose=True):
    if results is None:
        results = json.load(open(proj.workfile("align_result.json"),
                                 encoding="utf-8"))["results"]
    names = detect_names(proj)
    if verbose:
        print(f"tokens 'nombre propio' detectados en {proj.bt['name']}:", len(names))

    th = proj.thresholds
    corpus = {}
    for ws, info in results.items():
        freq, cands = info["freq"], info["cands"]
        if freq < th["min_freq"] or not cands:
            continue
        wt, p, co, d = cands[0]
        if co < th["min_cooc"]:
            continue
        if p >= th["alta"]["p"] and co >= th["alta"]["n"] and d >= th["alta"]["d"]:
            conf = "alta"
        elif p >= th["media"]["p"] and co >= th["media"]["n"]:
            conf = "media"
        elif p >= th["baja"]["p"] and co >= th["baja"]["n"]:
            conf = "baja"
        else:
            continue
        glosses = [wt]
        for wt2, p2, co2, d2 in cands[1:3]:
            if p2 >= 0.20 and co2 >= 5 and wt2 not in glosses:
                glosses.append(wt2)
        corpus[ws] = {"gloss": glosses, "conf": conf, "p": round(p, 2),
                      "n": co, "freq": freq, "name": glosses[0].lower() in names}

    if verbose:
        print("entradas [C] candidatas:", len(corpus))
        print("por confianza:", Counter(v["conf"] for v in corpus.values()))
    json.dump(corpus, open(proj.workfile("corpus_lexicon.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    return corpus


def run(proj, iters=8, verbose=True):
    """Pipeline completo del nivel C."""
    pairs = extract(proj, verbose)
    if not pairs:
        print("Sin versículos paralelos: no hay nivel [C].")
        return {}
    results = model1(proj, pairs, iters, verbose)
    return build_tier_c(proj, results, verbose)
