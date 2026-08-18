# -*- coding: utf-8 -*-
"""Capa PWA del sitio publicado: manifest, service worker e iconos.

Vive en la publicación y no en el render a propósito: los HTML de `out/` se
abren también desde disco (file://), donde el service worker no existe y el
manifest sobra. Solo la copia que va al repo de GitHub Pages se instrumenta.

Sin dependencias externas: los PNG se rasterizan y comprimen aquí mismo, para
que publicar nunca dependa de que Pillow esté instalado.
"""
import hashlib, json, os, re, struct, zlib

ACCENT = "#1f4e79"        # mismo azul que el resto del sitio
BG_LIGHT = "#f6f7f9"
BG_DARK = "#0f141a"
WHITE = (255, 255, 255)

ICONS = ("icon-192.png", "icon-512.png", "icon-maskable-512.png", "apple-touch-icon.png")

MARK_OPEN, MARK_CLOSE = "<!-- pwa -->", "<!-- /pwa -->"

HEAD = """<!-- pwa -->
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="{accent}" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="{dark}" media="(prefers-color-scheme:dark)">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="icon" type="image/png" sizes="512x512" href="icons/icon-512.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="{short}">
<script>
if ('serviceWorker' in navigator) {{
  addEventListener('load', function () {{
    var had = !!navigator.serviceWorker.controller;
    navigator.serviceWorker.register('sw.js').catch(function () {{}});
    // Tras publicar una versión nueva el SW entrante toma el control; se recarga
    // una sola vez para no dejar media página con los datos viejos. En la primera
    // visita no hay controlador previo, así que no se recarga.
    navigator.serviceWorker.addEventListener('controllerchange', function () {{
      if (had && !window.__kamusReloading) {{ window.__kamusReloading = 1; location.reload(); }}
    }});
  }});
}}
</script>
<!-- /pwa -->
"""

SW = """// Service worker del kamus. Generado por kamus-toolkit: no editar a mano.
// El nombre del cache lleva el scope y el hash del contenido publicado. El scope
// es imprescindible: todos los idiomas cuelgan del mismo origen
// (usuario.github.io/kamus-xxx/) y CacheStorage es por origen, no por scope, así
// que un prefijo común haría que cada idioma le borrase el cache offline a los
// demás al activarse. El hash hace que solo cambie cuando cambian las páginas.
const PREFIX = 'kamus' + new URL(self.registration.scope).pathname;
const CACHE = PREFIX + '{version}';
const ASSETS = {assets};
// Caches del esquema viejo (kamus-<hash>, sin scope): huérfanos que ya no
// reclama nadie. Se limpian una vez y este bloque se puede quitar más adelante.
const LEGACY = /^kamus-[0-9a-f]{{10}}$/;

self.addEventListener('install', e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
}});

self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => (k.startsWith(PREFIX) || LEGACY.test(k)) && k !== CACHE)
                              .map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
}});

// Cache-first: el diccionario es estático y pesado, y el caso de uso es trabajar
// sin cobertura. Lo que no esté precacheado se busca en red y se guarda.
self.addEventListener('fetch', e => {{
  const req = e.request;
  if (req.method !== 'GET') return;
  if (new URL(req.url).origin !== location.origin) return;
  e.respondWith(caches.match(req, {{ignoreSearch: true}}).then(hit => hit || fetch(req)
    .then(res => {{
      if (res && res.ok && res.type === 'basic') {{
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy));
      }}
      return res;
    }})
    .catch(() => req.mode === 'navigate' ? caches.match('index.html') : Response.error())));
}});
"""


# ---------------------------------------------------------------- iconos

def _rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _rrect(x0, y0, x1, y1, r):
    """Rectángulo redondeado en coordenadas 0..1: (bbox, predicado)."""
    def inside(x, y):
        cx = x0 + r if x < x0 + r else (x1 - r if x > x1 - r else x)
        cy = y0 + r if y < y0 + r else (y1 - r if y > y1 - r else y)
        dx, dy = x - cx, y - cy
        return dx * dx + dy * dy <= r * r
    return ((x0, y0, x1, y1), inside)


def _book(cx, cy, s, ink):
    """Libro abierto: bloque de páginas, lomo y renglones."""
    u = lambda t: cx + (t - .5) * s
    layers = [(_rrect(u(.06), u(.20), u(.94), u(.80), .055 * s), WHITE),
              (_rrect(u(.484), u(.20), u(.516), u(.80), .010 * s), ink)]
    for i, w in enumerate((.30, .30, .22)):
        y0, y1 = u(.34 + i * .15), u(.41 + i * .15)
        layers.append((_rrect(u(.14), y0, u(.14 + w), y1, .015 * s), ink))
        layers.append((_rrect(u(.56), y0, u(.56 + w), y1, .015 * s), ink))
    return layers


def _raster(size, layers, ss=3):
    """Rasteriza por supermuestreo. Las capas van de abajo arriba."""
    out = bytearray(size * size * 4)
    inv = 1.0 / size
    offs = [(i + .5) / ss for i in range(ss)]
    n = ss * ss
    top = layers[::-1]
    for py in range(size):
        ys = [(py + t) * inv for t in offs]
        rows = [L for L in top if L[0][0][1] <= ys[-1] and L[0][0][3] >= ys[0]]
        if not rows:
            continue
        base = py * size * 4
        for pxi in range(size):
            xs = [(pxi + t) * inv for t in offs]
            r = g = b = cnt = 0
            for y in ys:
                for x in xs:
                    for ((bb, f), col) in rows:
                        if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] and f(x, y):
                            r += col[0]; g += col[1]; b += col[2]; cnt += 1
                            break
            if cnt:
                i = base + pxi * 4
                out[i] = r // cnt; out[i + 1] = g // cnt; out[i + 2] = b // cnt
                out[i + 3] = (255 * cnt) // n
    return bytes(out)


def _png(path, size, rgba):
    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    stride = size * 4
    raw = b"".join(b"\x00" + rgba[y * stride:(y + 1) * stride] for y in range(size))
    blob = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))
    open(path, "wb").write(blob)


def icons(dirpath, accent=ACCENT):
    """Escribe el juego de iconos si falta alguno. Rasterizar es lento y el
    resultado no depende del contenido del diccionario: no se rehace cada vez."""
    os.makedirs(dirpath, exist_ok=True)
    if all(os.path.exists(os.path.join(dirpath, n)) for n in ICONS):
        return []
    ink = _rgb(accent)
    specs = [("icon-192.png", 192, .22, .70, 3),
             ("icon-512.png", 512, .22, .70, 2),
             # maskable: el glifo se queda dentro de la zona segura central
             ("icon-maskable-512.png", 512, 0, .50, 2),
             # iOS enmascara por su cuenta y no admite transparencia
             ("apple-touch-icon.png", 180, 0, .64, 3)]
    for name, size, radius, glyph, ss in specs:
        layers = [(_rrect(0, 0, 1, 1, radius), ink)] + _book(.5, .5, glyph, ink)
        _png(os.path.join(dirpath, name), size, _raster(size, layers, ss))
    return list(ICONS)


# ---------------------------------------------------------------- montaje

def inject(path, head):
    """Mete el bloque PWA en el <head>. Idempotente: reemplaza el anterior."""
    html = open(path, encoding="utf-8").read()
    if MARK_OPEN in html:
        html = re.sub(re.escape(MARK_OPEN) + ".*?" + re.escape(MARK_CLOSE) + "\n?",
                      "", html, flags=re.S)
    open(path, "w", encoding="utf-8").write(html.replace("</head>", head + "</head>", 1))


def _version(paths):
    h = hashlib.sha1()
    for p in sorted(paths):
        h.update(open(p, "rb").read())
    return h.hexdigest()[:10]


def emit(repo, *, name, short, desc, lang, pages, shortcuts=(), accent=ACCENT):
    """Instrumenta el repo publicado. `pages` son los HTML ya copiados.

    Devuelve la lista de ficheros escritos, para el resumen del publish.
    """
    written = icons(os.path.join(repo, "icons"), accent)

    manifest = {
        "id": "./",
        "name": name,
        "short_name": short,
        "description": desc,
        "lang": lang,
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": BG_LIGHT,
        "theme_color": accent,
        "icons": [
            {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icons/icon-maskable-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "maskable"},
        ],
    }
    if shortcuts:
        manifest["shortcuts"] = [{"name": t, "url": "./" + u} for t, u in shortcuts]
    open(os.path.join(repo, "manifest.webmanifest"), "w", encoding="utf-8").write(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    head = HEAD.format(accent=accent, dark=BG_DARK, short=short)
    for p in pages:
        inject(os.path.join(repo, p), head)

    assets = ["./"] + ["./" + p for p in pages] + ["./manifest.webmanifest"] \
        + ["./icons/" + n for n in ICONS if n != "apple-touch-icon.png"]
    open(os.path.join(repo, "sw.js"), "w", encoding="utf-8").write(
        SW.format(version=_version([os.path.join(repo, p) for p in pages]),
                  assets=json.dumps(assets, indent=2)))

    return written + ["manifest.webmanifest", "sw.js"]
