# -*- coding: utf-8 -*-
"""Autodetección de proyectos Paratext y configuración del pipeline.

Paratext ya declara en Settings.xml todo lo que el pipeline necesita saber sobre
un proyecto (nombre, ISO, cómo se llaman los ficheros SFM), así que no adivinamos
convenciones: las leemos.
"""
import os, re, glob, json
import xml.etree.ElementTree as ET

TOOLKIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS = os.path.join(TOOLKIT, "projects")
TEMPLATES = os.path.join(TOOLKIT, "templates")
GLOSSES = os.path.join(TOOLKIT, "glosses")


# --------------------------------------------------------------------------
# Lectura de Settings.xml
# --------------------------------------------------------------------------
def read_settings(project_dir):
    """Extrae los metadatos de un proyecto Paratext. None si no lo es."""
    path = os.path.join(project_dir, "Settings.xml")
    if not os.path.exists(path):
        return None
    root = ET.parse(path).getroot()

    def txt(tag, default=""):
        el = root.find(tag)
        return (el.text or "").strip() if el is not None and el.text else default

    naming = root.find("Naming")
    prepart = postpart = bookform = ""
    if naming is not None:
        prepart = naming.get("PrePart", "") or ""
        postpart = naming.get("PostPart", "") or ""
        bookform = naming.get("BookNameForm", "") or ""
    postpart = postpart or txt("FileNamePostPart")
    prepart = prepart or txt("FileNamePrePart")
    bookform = bookform or txt("FileNameBookNameForm")

    iso_raw = txt("LanguageIsoCode")          # p.ej. "tnt:Latn::" o "id:::"
    iso = iso_raw.split(":")[0] if iso_raw else ""

    return {
        "dir": os.path.abspath(project_dir),
        "name": txt("Name") or os.path.basename(project_dir),
        "full_name": txt("FullName"),
        "iso": iso,
        "prepart": prepart,
        "postpart": postpart,
        "book_form": bookform,
        "font": txt("DefaultFont"),
    }


def sfm_glob(settings):
    """Patrón glob que casa los libros SFM de este proyecto."""
    return os.path.join(settings["dir"], f"{settings['prepart']}*{settings['postpart']}")


def book_files(settings):
    """{clave_de_libro: ruta}, p.ej. {'41MAT': 'C:/.../41MATTemboan.SFM'}."""
    out = {}
    for f in glob.glob(sfm_glob(settings)):
        m = re.match(r"(\d+[A-Z0-9]{2,3})", os.path.basename(f))
        if m:
            out[m.group(1)] = f
    return out


def find_projects(search_dirs):
    """Busca carpetas Paratext (con Settings.xml) y sus subproyectos."""
    found = []
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for entry in sorted(os.listdir(d)):
            p = os.path.join(d, entry)
            if not os.path.isdir(p):
                continue
            s = read_settings(p)
            if s:
                found.append(s)
                # las retrotraducciones suelen vivir como subcarpeta
                for sub in sorted(os.listdir(p)):
                    sp = os.path.join(p, sub)
                    if os.path.isdir(sp):
                        ss = read_settings(sp)
                        if ss:
                            ss["parent"] = s["name"]
                            found.append(ss)
    return found


# --------------------------------------------------------------------------
# Configuración de un proyecto del toolkit
# --------------------------------------------------------------------------
DEFAULT_TIER_THRESHOLDS = {
    # nivel C: umbrales del alineamiento estadístico (ver align.py)
    "min_freq": 3, "min_cooc": 4,
    "alta": {"p": 0.55, "n": 10, "d": 0.45},
    "media": {"p": 0.35, "n": 6},
    "baja": {"p": 0.22, "n": 5},
}


class Project:
    """Un proyecto del toolkit: traducción + retrotraducción + curaciones."""

    def __init__(self, cfg, root):
        self.cfg = cfg
        self.root = root                       # projects/<id>/
        self.id = cfg["id"]
        self.work = os.path.join(root, "work")  # intermedios (bitext, align…)
        os.makedirs(self.work, exist_ok=True)

        self.tr = read_settings(cfg["translation_dir"])
        if not self.tr:
            raise SystemExit(f"No es un proyecto Paratext: {cfg['translation_dir']}")

        bt_dir = cfg.get("backtranslation_dir")
        self.bt = read_settings(bt_dir) if bt_dir else None
        if bt_dir and not self.bt:
            raise SystemExit(f"No es un proyecto Paratext: {bt_dir}")

        lang = cfg.get("language", {})
        self.lang_name = lang.get("name") or self.tr["full_name"] or self.tr["name"]
        self.lang_alt = lang.get("alt", "")
        self.lang_iso = lang.get("iso") or self.tr["iso"]
        self.lang_region = lang.get("region", "")

        gl = cfg.get("gloss_language", {})
        self.gloss_name = gl.get("name", "Bahasa Indonesia")
        self.gloss_iso = gl.get("iso") or (self.bt["iso"] if self.bt else "id")
        self.gloss_map = gl.get("map", "gloss_id")

        self.thresholds = dict(DEFAULT_TIER_THRESHOLDS)
        self.thresholds.update(cfg.get("thresholds", {}))

        out = cfg.get("output", {})
        self.out_dir = out.get("dir") or os.path.join(root, "out")
        self.basename = out.get("basename") or f"Kamus-{self._slug()}"
        self.inter_basename = out.get("interlinear") or f"Interlinear-{self._slug()}"
        os.makedirs(self.out_dir, exist_ok=True)

        self.publish = cfg.get("publish", {})

    def _slug(self):
        import unicodedata
        s = f"{self.lang_name}-{self.gloss_name}"
        s = "".join(c for c in unicodedata.normalize("NFD", s)
                    if unicodedata.category(c) != "Mn")
        return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")

    # --- rutas de fuentes -------------------------------------------------
    def source(self, key):
        """Ruta de una fuente declarada en sources, o None si no existe."""
        v = self.cfg.get("sources", {}).get(key)
        if not v:
            return None
        p = v if os.path.isabs(v) else os.path.join(self.tr["dir"], v)
        return p if os.path.exists(p) else None

    def out(self, ext, interlinear=False):
        base = self.inter_basename if interlinear else self.basename
        return os.path.join(self.out_dir, f"{base}.{ext}")

    def workfile(self, name):
        return os.path.join(self.work, name)


def load(project_id):
    root = os.path.join(PROJECTS, project_id)
    cfgp = os.path.join(root, "project.json")
    if not os.path.exists(cfgp):
        avail = [d for d in sorted(os.listdir(PROJECTS))
                 if os.path.exists(os.path.join(PROJECTS, d, "project.json"))] \
                if os.path.isdir(PROJECTS) else []
        raise SystemExit(f"No existe el proyecto '{project_id}'. Disponibles: {', '.join(avail) or 'ninguno'}")
    cfg = json.load(open(cfgp, encoding="utf-8"))
    cfg.setdefault("id", project_id)
    return Project(cfg, root)


def list_projects():
    if not os.path.isdir(PROJECTS):
        return []
    return [d for d in sorted(os.listdir(PROJECTS))
            if os.path.exists(os.path.join(PROJECTS, d, "project.json"))]
