# -*- coding: utf-8 -*-
"""Genera projects/<iso>/morphology.json desde los análisis del propio equipo.

    python tools/gen_morphology.py ame

Paratext guarda en WordAnalyses.xml la segmentación que el equipo ha hecho a
mano de las palabras del texto (Prefix / Stem / Suffix). Es su análisis, no una
segmentación estadística nuestra, así que sirve para las dos cosas que el
toolkit necesita saber sobre la morfología de una lengua:

  · el apéndice de consulta (morphology.json), afijo · función · ejemplo
  · los sufijos que el interlineal prueba a quitar (interlinear.source_suffixes
    en project.json), que este script imprime para que los pegues allí

La columna 'función' sale de la glosa que el propio equipo escribió para ese
afijo en Lexicon.xml. Cuidado al leerla: el léxico agrupa homófonos bajo una
sola forma, así que un afijo puede aparecer con varias funciones que en realidad
son morfemas distintos que suenan igual (el sufijo -o sale como 'de; NEG; en;
GEN; LOC'). El apéndice es material de consulta pendiente de revisión del
equipo, no morfología verificada.
"""
import os, sys, json, collections
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kamus import config
from kamus.build import load_lexicon

MIN_N = 2          # afijos vistos en una sola palabra: probable error de segmentación
SIN_GLOSA = "—"


def analyses(proj):
    path = os.path.join(proj.tr["dir"], "WordAnalyses.xml")
    if not os.path.exists(path):
        raise SystemExit(f"No hay WordAnalyses.xml en {proj.tr['dir']}")
    root = ET.parse(path).getroot()

    pre, suf = collections.Counter(), collections.Counter()
    example = {}
    for e in root.findall("Entry"):
        word = e.get("Word")
        for a in e.findall("Analysis"):
            parts = []
            for lx in a.findall("Lexeme"):
                t = lx.text or ""
                if ":" in t:
                    parts.append(tuple(t.split(":", 1)))
            # la segmentación completa tal como la anotó el equipo; no siempre
            # concatena a la forma de superficie, porque la raíz que registran es
            # la subyacente (póchtsohuen se analiza sobre la raíz chets)
            seg = "-".join(f for _, f in parts)
            for kind, form in parts:
                if kind not in ("Prefix", "Suffix"):
                    continue
                (pre if kind == "Prefix" else suf)[form] += 1
                key = (kind, form)
                if key not in example and len(parts) > 1:
                    example[key] = f"{word} = {seg}"
    return pre, suf, example, len(root.findall("Entry"))


def rows(pre, suf, example, lex):
    out = []
    for kind, counter in (("Prefix", pre), ("Suffix", suf)):
        for form, n in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
            if n < MIN_N:
                continue
            label = f"{form}-" if kind == "Prefix" else f"-{form}"
            gloss = lex.get(form)
            out.append([label, "; ".join(gloss) if gloss else SIN_GLOSA,
                        example.get((kind, form), "")])
    return out


def affix_list(counter):
    """Para interlinear.source_suffixes / source_prefixes: los más largos
    primero, porque el interlineal se queda con el primero que casa y '-o' se
    comería a '-eño'."""
    forms = [f for f, n in counter.items() if n >= MIN_N]
    return sorted(forms, key=lambda f: (-len(f), -counter[f], f))


if __name__ == "__main__":
    iso = sys.argv[1] if len(sys.argv) > 1 else "ame"
    proj = config.load(iso)
    pre, suf, example, n_words = analyses(proj)
    lex = load_lexicon(proj.source("lexicon"))

    table = rows(pre, suf, example, lex)
    path = os.path.join(proj.root, "morphology.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(table, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    sin_glosa = sum(1 for r in table if r[1] == SIN_GLOSA)
    print(f"escrito {path}")
    print(f"  {n_words} palabras analizadas por el equipo")
    print(f"  {len(pre)} prefijos y {len(suf)} sufijos distintos; "
          f"{len(table)} en el apéndice (vistos en {MIN_N}+ palabras)")
    print(f"  sin glosa en el léxico: {sin_glosa}")
    print()
    print("Pega esto en project.json, dentro de interlinear:")
    print('  "source_prefixes": ' + json.dumps(affix_list(pre), ensure_ascii=False) + ",")
    print('  "source_suffixes": ' + json.dumps(affix_list(suf), ensure_ascii=False))
