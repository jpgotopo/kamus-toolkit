# De Excel a FLEx: plantilla y conversor

Plantilla para pasar datos léxicos de una hoja de cálculo a FieldWorks Language
Explorer, con los datos del yanesha' (`ame`) como ejemplo.

| Archivo | Qué es |
|---|---|
| `Plantilla-FLEx-Yanesha.xlsx` | La plantilla completa. 22 columnas, 36 filas de ejemplo con palabras yanesha' reales, y hojas de instrucciones, campos, categorías y dominios. Contempla los dos alfabetos. |
| `Plantilla-FLEx-Yanesha-SIL.xlsx` | La misma plantilla, pero solo para el alfabeto SIL. 21 columnas: sin la columna `lxo` ni las instrucciones del segundo sistema de escritura. |
| `Lexico-FLEx-Yanesha.xlsx` | El diccionario **completo**: 1681 entradas en 2163 filas. Misma estructura de columnas. Ver [Exportar el diccionario completo](#exportar-el-diccionario-completo). |
| `Lexico-FLEx-Yanesha-SIL.xlsx` | El diccionario completo, solo alfabeto SIL. |
| `excel_a_flex.py` | Convierte cualquiera de los cuatro en `.sfm` y `.lift`. |
| `../../tools/gen_plantilla_flex.py` | Regenera todo. Otro proyecto: `python tools/gen_plantilla_flex.py tnt`. Variantes: `--sil` (solo alfabeto SIL), `--todo` (diccionario completo). |

### Cuál usar

Si el equipo trabaja íntegramente en el alfabeto SIL —el de los diacríticos— y
no tiene previsto migrar, usa **`-SIL`**: una columna menos que explicar y una
menos que dejar vacía.

Usa la completa si vas a registrar las dos ortografías en paralelo, para que
FLEx las guarde como dos sistemas de escritura vernáculos.

Las dos comparten todo lo demás: misma estructura de una fila por acepción,
misma normalización NFC, misma fuente Charis SIL en las columnas vernáculas.
Cambiar de una a otra más adelante no obliga a rehacer los datos.

```
python templates/flex/excel_a_flex.py "templates/flex/Plantilla-FLEx-Yanesha.xlsx"
```

Requiere `openpyxl` (`pip install openpyxl`).

---

## El problema de fondo

Una hoja de cálculo es plana y una entrada de diccionario no lo es: una palabra
tiene varias acepciones, y cada acepción su propia categoría, definición y
ejemplos. Beth Bryson lo resumió en la lista cuando alguien preguntó justo esto
para el enggano:

> It is challenging to represent multiple senses in a spreadsheet, because a
> spreadsheet is not designed to handle that kind of structure.

De ahí salen casi todos los desastres de importación que se ven en la lista.

**La convención de esta plantilla: una fila por acepción, no por entrada.**
Se repite el lexema en la columna `lx` en cada fila y se numera en `sn`. El
conversor vuelve a agrupar las filas que comparten lexema.

```
lx              ps    sn  ge
acheret̃        adj   1   asado
acheret̃        s     2   yuca asada
acheret̃        s     3   pan de la proposición
acheret̃        s     4   pan de la Presencia
acheret̃        s     5   pan sagrado
```

Eso son cinco filas y **una** entrada con cinco acepciones — y de paso muestra
que la categoría gramatical puede cambiar entre acepciones de la misma entrada.

Lo que **no** hay que hacer nunca: meter `asado; yuca asada; pan sagrado` en una
sola celda. Entra a FLEx como una glosa larga y absurda, y hay que deshacerla a
mano entrada por entrada.

---

## Por qué no SheetSwiper

[SheetSwiper](https://software.sil.org/sheetswiper/) es la respuesta habitual en
la lista y funciona, pero cobra tres peajes:

1. Exige `.xls` antiguo, no `.xlsx`.
2. Trata cada fila como una entrada: una palabra con tres acepciones entra como
   tres entradas sueltas.
3. Las columnas vacías dejan bloques `\ps \sn \ge` huecos que hay que borrar con
   expresiones regulares en Notepad++ antes de importar — que fue exactamente la
   solución que Beth le dio al proyecto enggano.

`excel_a_flex.py` escribe el SFM directamente y no tiene ninguno de los tres
problemas: agrupa las acepciones y nunca escribe un campo vacío. Si prefieres
SheetSwiper, la plantilla igual te sirve: los códigos de la fila 1 ya son los
marcadores SFM.

---

## SFM o LIFT

El conversor genera los dos. **Usa LIFT si puedes.**

| | LIFT | SFM |
|---|---|---|
| Menú | `File > Import > Lexicon (LIFT)` | `File > Import > Standard Format Marker Data` |
| Mapear marcadores a mano | no | sí, uno por uno |
| Acepciones múltiples | intactas | dependen del mapeo |
| Reimportar el mismo archivo | actualiza (GUID estables) | duplica |

Los GUID del LIFT se derivan del lexema, así que reimportar el mismo Excel
corregido actualiza las entradas en vez de duplicarlas.

---

## Los tropiezos clásicos

**`lx` va primero y nunca vacía.** FLEx usa el lexema como marcador de registro.
Es el mismo consejo que se dio en el hilo de importación de audios: *"you usually
want the lexeme form as the first entry of each record"*.

**Campos que caen en «Residue».** `\hm`, `\et` y `\va` casi siempre caen ahí la
primera vez y entonces no se importan. En la ventana de mapeo, selecciona el
marcador, pulsa **Modify** y dile a FLEx a qué campo va.

**El truco de la entrada de prueba.** Antes de importar nada, crea a mano en FLEx
una entrada con todos los campos que vas a usar y expórtala como SFM
(`File > Export > Standard Format`). Ese archivo te muestra los marcadores
exactos que tu proyecto espera. Es el mejor consejo que ha circulado por la
lista sobre esto.

**Categorías gramaticales duplicadas.** `v` y `V` crean dos categorías distintas
en FLEx, y fusionarlas después es tedioso. La columna `ps` de la plantilla tiene
lista desplegable por eso. Si ya te pasó, se arregla renombrando una, moviendo
las entradas con Bulk Edit y borrando la vacía.

**Codificación al abrir CSV en Excel.** Si abres un CSV exportado de FLEx con
doble clic, los caracteres especiales se destrozan. Hay que entrar por
`Datos > Obtener datos > Desde archivo` y poner la codificación en
**65001: Unicode (UTF-8)**. El `.xlsx` de la plantilla no tiene este problema —
solo aparece si haces el viaje de vuelta por CSV.

---

## Lo específico del yanesha'

### Dos alfabetos

En enero de 2025 se preguntó en la lista justamente por el yanesha': el
diccionario ortográfico que trae FLEx usa el alfabeto de SIL, pero el gobierno
peruano oficializó otro **con digrafos en lugar de diacríticos**.

La plantilla tiene por eso dos columnas de lexema:

- `lx` — ortografía SIL, la que usa el corpus actual (`acheret̃`, `áqueshp̃at`)
- `lxo` — alfabeto oficial MINEDU, para llenar cuando se haga la conversión

Se importan como dos sistemas de escritura vernáculos distintos. Hay que crear
el segundo antes de importar, en `Format > Set up Vernacular Writing Systems`, y
al mapear `\lxo` elegir **Lexeme Form** con ese segundo sistema.

La variante `Plantilla-FLEx-Yanesha-SIL.xlsx` omite `lxo` por completo: no hay
segundo sistema de escritura que crear ni marcador extra que mapear. Si más
adelante hace falta la otra ortografía, se agrega en FLEx sin rehacer nada, con
el procedimiento de Bulk Edit que se explicó en la lista para este mismo caso.

Si hay que convertir masivamente de un alfabeto al otro, la herramienta es
**SIL Converters** con una tabla TECkit de correspondencias — se puede armar la
tabla en el mismo Excel.

### Los diacríticos compuestos

`c̈`, `p̃`, `t̃`, `m̃` **no existen como caracteres precompuestos en Unicode**:
son siempre base + diacrítico combinante (`c` + U+0308, `p` + U+0303). En cambio
`ñ`, `á`, `é`, `ó` sí son precompuestos. El corpus del proyecto está en NFC.

Consecuencias prácticas:

- **No uses Buscar y reemplazar de Excel** sobre la columna `lx` sin revisar el
  resultado: puede separar la letra de su diacrítico.
- Dos formas que se ven idénticas pueden ser distintas para FLEx. El conversor
  normaliza todo a NFC al leer, precisamente para que `acheñ` no entre dos veces.
- Usa una fuente que dibuje bien los combinantes: **Charis SIL** o **Andika**.
  La plantilla ya aplica Charis SIL a las columnas vernáculas.
- Si el orden alfabético sale raro después de importar, no es un error: hay que
  definir reglas de ordenamiento ICU personalizadas para el alfabeto yanesha'.

### El corpus ya construido

Las filas de ejemplo salen del diccionario yanesha'–español de este repositorio
(`projects/ame/out/`), que tiene 1681 entradas con su nivel de confianza A/B y,
en las bíblicas, el lema hebreo o griego que traducen. La oración de ejemplo es
1 Samuel 1:10 del corpus alineado del propio proyecto.

Las dos últimas columnas son de ese origen y no son MDF estándar:

- `st` — confianza A/B/C del equipo
- `lem` — lema hebreo/griego que la entrada traduce

Para conservarlas hay que crear campos personalizados
(`Tools > Configure > Custom Fields`). Si no interesan, se dejan en Residue y no
pasa nada.

### Exportar el diccionario completo

```
python tools/gen_plantilla_flex.py ame --todo          # las dos ortografías
python tools/gen_plantilla_flex.py ame --todo --sil    # solo alfabeto SIL
```

Genera `Lexico-FLEx-Yanesha.xlsx` con **las 1681 entradas en 2163 filas** —una
por acepción, porque las glosas separadas por `;` en el TSV se abren en
acepciones distintas— y con la misma estructura de columnas, así que
`excel_a_flex.py` lo procesa sin cambios.

Se rellena solo lo que el corpus permite afirmar:

| Columna | Cómo se llena |
|---|---|
| `lx`, `ge`, `sn` | del diccionario, una fila por acepción |
| `st` | el nivel de confianza A/B del equipo |
| `lem` | el lema hebreo/griego (623 filas) |
| `ps` | **solo en 259 de 2163 filas** |
| `nt` | aviso en los afijos (88 filas) |

**La categoría gramatical es el trabajo que queda.** El TSV no la tiene, y no se
puede deducir de una glosa: que `acheret̃` signifique 'asado' no dice si en
yanesha' es adjetivo o nominalización. Solo se rellena donde hay evidencia:

- `fras` (145) — la entrada tiene espacios; FLEx la marcaría como frase de todos modos
- `suf` (48) y `pref` (28) — la forma está en `morphology.json`, o sea el equipo ya la segmentó como afijo en Paratext
- `nprop` (38) — la glosa es un nombre propio de `prop_map.py`, incluso flexionado (`de Aarón`, `en Silo`)

Las otras 1904 quedan en blanco. El conversor lo avisa una sola vez, agregado, y
las importa igual: entran a FLEx sin *Grammatical Info*, que se puede completar
después con **Bulk Edit Entries** filtrando por categoría vacía.

Dos cosas que conviene mirar antes de importar:

- **Los afijos van sin guion.** En el TSV son `a`, `ach`, `pe`; FLEx necesita
  `a-`, `-ach`, `pe-` para asignar el tipo de morfema. Las 88 filas afectadas
  llevan nota. En las ambiguas —`a` aparece como prefijo *y* como sufijo— se
  deja `ps` vacío a propósito: esa decisión es del equipo.
- **Las anotaciones curadas se conservan.** La definición de `acheñ`, el dominio
  semántico y el ejemplo de 1 Samuel 1:10 aparecen también en la exportación
  completa, no solo en la plantilla de muestra.

Sugerencia de flujo: importar primero solo las de confianza `A` para ver cómo
queda, y dejar las `B` para una segunda tanda ya revisadas.

---

## Referencias

- [Technical Notes on SFM Database Import](https://software.sil.org/fieldworks/help/technical-documents/) — la lista completa de marcadores y a qué campo de FLEx va cada uno
- [Importing SFM to FLEx](https://youtube.com/playlist?list=PLE0Ud4zAQz-2ZDh3ebKxCCR6dKZQpmrUu) — videos de Beth Bryson sobre la ventana de mapeo
- [LIFT standard](https://github.com/sillsdev/lift-standard/tree/master)
- [SheetSwiper](https://software.sil.org/sheetswiper/) · [SIL Converters](https://software.sil.org/silconverters/)
