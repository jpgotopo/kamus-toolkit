# kamus-toolkit

Genera un **diccionario** y un **traductor interlineal** para cualquier lengua, a partir de
la carpeta Paratext de la traducción y la de su retrotraducción, y los publica en GitHub Pages.

Es la generalización del pipeline que se construyó a mano para Tontémboan. Ese pipeline
original sigue intacto en `BahasaTemboan/_kamus_build/`; este toolkit lo reproduce
**entrada por entrada** (verificado: 2.496 lemas idénticos) pero funciona con cualquier proyecto.

## Uso

```bash
python -m kamus detect                  # busca proyectos Paratext y lee sus Settings.xml
python -m kamus check   <proyecto>      # qué niveles A/B/C son alcanzables (ANTES de construir)
python -m kamus align   <proyecto>      # solo el nivel C (lento: ~2 min)
python -m kamus build   <proyecto>      # diccionario + interlineal
python -m kamus todo    <proyecto>      # qué falta por curar
python -m kamus publish <proyecto>      # copia al repo, lo hace PWA, commit, push, Pages
python -m kamus all     <proyecto>      # align + build + publish
```

## Añadir un idioma

1. `python -m kamus detect` → anota las rutas de la traducción y la retrotraducción.
2. `cp -r projects/_ejemplo projects/<iso>` y edita `project.json`.
3. `python -m kamus check <iso>` → te dice qué niveles saldrán y qué falta.
4. `python -m kamus build <iso>`.
5. `python -m kamus todo <iso>` → curación: glosas que faltan y nombres propios sin tipo.
6. `python -m kamus publish <iso>`.

## Niveles de confianza

| | Origen | Depende de |
|---|---|---|
| **[A]** verificado | glosas del propio equipo | `Lexicon.xml`, glosario del proyecto |
| **[B]** conjetura alta | rendering oficial del equipo para un lema griego/hebreo, glosado con el equivalente léxico estándar | `TermRenderings.xml` + `glosses/<mapa>.py` |
| **[C]** alineado por corpus | IBM Model 1 (EM) + Dice sobre versículos paralelos | traducción y retrotraducción que compartan libros |

Un proyecto sin `Lexicon.xml` no tendrá nivel [A] por mucho que se ejecute el pipeline.
Por eso `check` se ejecuta antes y lo dice explícitamente.

## Qué se reutiliza entre idiomas

- **`glosses/gloss_id.py`** — mapa lema griego/hebreo → indonesio (765 entradas, hecho a mano).
  Está indexado por el **lema griego/hebreo**, no por la lengua vernácula, así que **sirve tal
  cual para cualquier proyecto cuya retrotraducción sea en indonesio**. Es el activo caro;
  no hay que rehacerlo por idioma.
- **`kamus/align.py`** — el nivel C es estadística pura; no sabe nada de la lengua.
- **`templates/`**, `kamus/render.py` — parametrizados por `locales.py`.

Lo que **sí** hay que hacer por idioma:

- `projects/<iso>/project.json` — rutas y metadatos.
- `projects/<iso>/prop_map.py` — nombres propios: tipo, forma en la lengua de glosa, y
  compuestos capitalizados que en realidad son términos traducibles (`TERM_MOVE`). Opcional.
- `projects/<iso>/morphology.json` — apéndice de afijos. Opcional.
- `interlinear.source_suffixes` en `project.json` — sufijos que el interlineal prueba a
  quitar para encontrar la raíz. Opcional, pero sube bastante la cobertura.

## Otra lengua de glosa

Si un proyecto retrotraduce a algo que no sea indonesio hacen falta dos cosas, **una vez**
(no por cada idioma vernáculo):

1. `glosses/gloss_<iso>.py` con `GK = {...}` y `HB = {...}` (lema griego/hebreo → esa lengua).
2. Un bloque nuevo en `kamus/locales.py` con los textos de interfaz, copiando `ID` y traduciendo.

## Estructura

```
kamus/
  config.py       autodetección de Settings.xml + configuración de proyecto
  sources.py      inventario de fuentes y veredicto de niveles alcanzables
  align.py        nivel C: extracción de bitexto, IBM Model 1, entradas [C]
  build.py        ensamblado de las entradas A/B/C
  render.py       salidas md / tsv / xlsx / html
  interlinear.py  herramienta interlineal bidireccional
  publish.py      repo git por idioma + GitHub Pages
  pwa.py          manifest, service worker e iconos del sitio publicado
  locales.py      textos de interfaz (hoy: indonesio)
  cli.py          línea de comandos
glosses/          mapas lema griego/hebreo → lengua de glosa (compartidos)
projects/<iso>/   config + curaciones + salidas de cada idioma
templates/        plantillas HTML del kamus y del interlineal
```

## Nota sobre git en esta máquina

El `git` del PATH es 2.9.2 (2016) y su transporte HTTPS está roto contra GitHub (muere con
exit 128 sin mensaje). `publish.py` lo esquiva usando el git moderno que trae GitHub Desktop.
