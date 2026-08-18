# -*- coding: utf-8 -*-
"""Publicación: repo git por idioma + GitHub Pages."""
import os, glob, shutil, subprocess, json, datetime

from . import config, pwa


def resolve_git():
    """Un git que funcione. El del PATH puede ser demasiado viejo para GitHub."""
    pat = os.path.join(os.environ.get("LOCALAPPDATA", ""),
                       "GitHubDesktop", "app-*", "resources", "app", "git", "cmd", "git.exe")
    cands = sorted(glob.glob(pat))
    if cands:
        return cands[-1]
    return shutil.which("git")


def _run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if check and r.returncode != 0:
        raise SystemExit(f"Falló: {' '.join(cmd)}\n{r.stderr or r.stdout}")
    return r


LANDING = """<!doctype html>
<html lang="{gloss_iso}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root{{--bg:#f6f7f9;--card:#fff;--ink:#1c2530;--muted:#63707e;--line:#e3e8ee;--accent:#1f4e79;
    --A:#2f7d3b;--Abg:#e6f4ea;--B:#b3651b;--Bbg:#fbead9;--C:#2563a8;--Cbg:#e1ecf7;--shadow:0 1px 3px rgba(0,0,0,.06);}}
  @media (prefers-color-scheme:dark){{:root{{--bg:#0f141a;--card:#171e26;--ink:#e6ebf1;--muted:#93a1b0;--line:#25303b;
    --accent:#6aa9e0;--A:#6cc47a;--Abg:#16281a;--B:#e0a262;--Bbg:#2a1d10;--C:#6aa9e0;--Cbg:#132234;--shadow:0 1px 3px rgba(0,0,0,.4);}}}}
  *{{box-sizing:border-box}}
  body{{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.5}}
  .wrap{{max-width:820px;margin:0 auto;padding:40px 16px 60px}}
  h1{{font-size:24px;margin:0 0 4px}}
  .sub{{color:var(--muted);font-size:14px;margin:0 0 28px}}
  .cards{{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}}
  a.card{{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;
    box-shadow:var(--shadow);text-decoration:none;color:inherit;transition:border-color .15s,transform .15s}}
  a.card:hover{{border-color:var(--accent);transform:translateY(-2px)}}
  .card h2{{font-size:17px;margin:0 0 6px;color:var(--accent)}}
  .card p{{margin:0;font-size:13.5px;color:var(--muted)}}
  .go{{display:inline-block;margin-top:12px;font-size:13px;font-weight:600;color:var(--accent)}}
  .note{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;font-size:13px;color:var(--muted);margin-top:28px}}
  .badge{{font-size:10.5px;font-weight:700;padding:2px 7px;border-radius:6px;letter-spacing:.4px}}
  .badge.A{{background:var(--Abg);color:var(--A)}} .badge.B{{background:var(--Bbg);color:var(--B)}}
  .badge.C{{background:var(--Cbg);color:var(--C)}}
  .foot{{color:var(--muted);font-size:12px;margin-top:24px}}
</style>
</head>
<body>
<div class="wrap">
  <h1>{title}</h1>
  <p class="sub">{subtitle}</p>
  <div class="cards">
    <a class="card" href="{kamus}">
      <h2>📖 {card_kamus_title}</h2>
      <p>{card_kamus_desc}</p>
      <span class="go">{go_kamus}</span>
    </a>
    <a class="card" href="{inter}">
      <h2>⇄ Interlinear</h2>
      <p>{card_inter_desc}</p>
      <span class="go">{go_inter}</span>
    </a>
  </div>
  <div class="note">
    <span class="badge A">A</span> {tier_a}<br>
    <span class="badge B">B</span> {tier_b}<br>
    <span class="badge C">C</span> {tier_c}
  </div>
  <p class="foot">{foot}</p>
</div>
</body>
</html>
"""


def prepare(proj, S, counts):
    """Copia las salidas al repo del idioma y escribe la portada."""
    repo = proj.publish.get("dir")
    if not repo:
        raise SystemExit("Falta publish.dir en project.json")
    os.makedirs(repo, exist_ok=True)

    copied = []
    for src in (proj.out("html"), proj.out("html", interlinear=True)):
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(repo, os.path.basename(src)))
            copied.append(os.path.basename(src))

    open(os.path.join(repo, ".nojekyll"), "w").close()

    # fuentes del nivel A, para nombrarlas en la portada
    lexicon_names = ", ".join(
        os.path.basename(p) for p in (proj.source("lexicon"), proj.source("glossary")) if p
    ) or "—"

    html = LANDING.format(
        gloss_iso=proj.gloss_iso or "id",
        title=S("title"),
        subtitle=S("lang_desc").replace("**", ""),
        kamus=proj.basename + ".html",
        inter=proj.inter_basename + ".html",
        card_kamus_title=S("card_kamus_title"),
        card_kamus_desc=S("card_kamus_desc"),
        card_inter_desc=S("card_inter_desc"),
        go_kamus=S("go_kamus"), go_inter=S("go_inter"),
        tier_a=S("tier_A", lexicon=lexicon_names).replace("**", "").replace("[A] ", ""),
        tier_b=S("tier_B").replace("**", "").replace("*", "").replace("[B] ", ""),
        tier_c=S("tier_C").replace("**", "").replace("[C] ", ""),
        foot=S("landing_foot"),
    )
    open(os.path.join(repo, "index.html"), "w", encoding="utf-8").write(html)
    copied.append("index.html")

    # PWA: instalable en el móvil y utilizable sin cobertura, que es la
    # situación normal del equipo en campo.
    copied += pwa.emit(
        repo,
        name=S("title"),
        short=S("pwa_short"),
        desc=S("pwa_desc"),
        lang=proj.gloss_iso or "id",
        pages=copied[:],
        shortcuts=[(S("card_kamus_title"), proj.basename + ".html"),
                   ("Interlinear", proj.inter_basename + ".html")],
        accent=proj.publish.get("theme_color", pwa.ACCENT),
    )
    return repo, copied


def push(proj, message=None, create=True):
    """Commit + push. Crea el repo en GitHub con gh si aún no existe."""
    repo = proj.publish.get("dir")
    slug = proj.publish.get("repo")           # p.ej. "usuario/kamus-xxx"
    git = resolve_git()
    if not git:
        raise SystemExit("No se encontró git.")

    if not os.path.isdir(os.path.join(repo, ".git")):
        _run([git, "init"], cwd=repo)
        _run([git, "branch", "-m", "main"], cwd=repo, check=False)

    if not _run([git, "status", "--porcelain"], cwd=repo).stdout.strip():
        print("Sin cambios: lo publicado ya está al día.")
        return None

    _run([git, "add", "-A"], cwd=repo)
    msg = message or f"Actualiza kamus e interlinear ({datetime.date.today():%Y-%m-%d})"
    _run([git, "-c", "user.email=kamus@local", "-c", "user.name=kamus-toolkit",
          "commit", "-m", msg], cwd=repo)

    has_remote = _run([git, "remote"], cwd=repo).stdout.strip()
    if not has_remote:
        if not slug:
            print("Commit hecho. Falta publish.repo en project.json para subirlo.")
            return None
        gh = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"
        if create and os.path.exists(gh):
            vis = "--public" if proj.publish.get("public", True) else "--private"
            _run([gh, "repo", "create", slug, vis, "--source", repo,
                  "--remote", "origin"], check=False)
        _run([git, "remote", "add", "origin", f"https://github.com/{slug}.git"],
             cwd=repo, check=False)

    _run([git, "push", "-u", "origin", "main"], cwd=repo)
    url = f"https://{slug.split('/')[0]}.github.io/{slug.split('/')[1]}/" if slug else "(repo local)"
    print("Publicado:", url)
    return url


def enable_pages(proj):
    slug = proj.publish.get("repo")
    gh = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"
    if not slug or not os.path.exists(gh):
        return False
    r = _run([gh, "api", "--method", "POST", f"repos/{slug}/pages",
              "-f", "source[branch]=main", "-f", "source[path]=/"], check=False)
    return r.returncode == 0 or "already" in (r.stderr or "").lower()
