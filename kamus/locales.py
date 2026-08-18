# -*- coding: utf-8 -*-
"""Textos de interfaz, separados del código.

Los diccionarios se redactan en la LENGUA DE GLOSA (la de la retrotraducción),
porque es la que lee el equipo. Hoy solo está el indonesio, que es lo que se
usa; para añadir otra lengua-glosa basta con copiar el bloque y traducirlo.

Placeholders disponibles: {lang} {lang_alt} {iso} {region} {gloss_lang}
{bt_name} {lexicon} {glossary} {renderings} {n_main} {n_A} {n_B} {n_C}
{n_glos} {n_prop}
"""

ID = {
    "code": "id",
    "title":            "Kamus Bahasa {lang} – {gloss_lang}",
    "intro":            ("Disusun otomatis dari data proyek penerjemahan Alkitab {lang} (Paratext). "
                         "**Versi diperluas:** semua bentuk alternatif (dipisah `||`), akar berimbuhan (`*`), "
                         "dan frasa kini menjadi lema tersendiri."),
    "lang_desc":        "Bahasa {lang}{alt_paren} = {region} (ISO **{iso}**).",
    "tiers_heading":    "Tingkat keyakinan & jenis lema",
    "tier_A":           "**[A]** terverifikasi — dari leksikon & glosarium tim ({lexicon}).",
    "tier_B":           ("**[B]** konjektur berkeyakinan tinggi — bentuk {lang} = *rendering* resmi tim "
                         "untuk kata Yunani/Ibrani; arti = padanan baku kata itu."),
    "tier_C":           ("**[C]** hasil penjajaran korpus — diturunkan otomatis dengan menyejajarkan teks "
                         "{lang} dengan retrotraduksi {gloss_lang} (proyek **{bt_name}**) memakai IBM Model 1. "
                         "Keandalan statistik: **tinggi** (kata sering, p≥0.55) atau **sedang**."),
    "corpus_confirm":   "Bila sebuah entri A/B juga dikonfirmasi korpus, diberi tanda **✓korpus**.",
    "kinds_note":       ("Jenis lema: **kata** (satu kata) · **frasa** (ungkapan) · "
                         "**akar** (bentuk dasar dari pola berimbuhan `*…*`; di teks selalu memakai imbuhan)."),
    "summary":          ("**Ringkasan:** {n_main} entri utama ({n_A} A / {n_B} B / {n_C} C) · "
                         "{n_glos} glosarium · {n_prop} nama diri."),
    "sec_main":         "Bagian 1 — Kamus utama ({lang} → {gloss_lang})",
    "sec_glossary":     "Bagian 2 — Glosarium istilah (dengan definisi) [A]",
    "sec_propers":      "Bagian 3 — Nama diri (nama orang, tempat, bangsa)",
    "propers_note":     ("Setiap nama diberi **jenis** (orang / tempat / bangsa/suku / lain-lain). "
                         "Bentuk {gloss_lang} baku dicantumkan bila berbeda dari bentuk {lang}."),
    "sec_morphology":   "Lampiran — Morfologi (afiks yang sering muncul)",
    "sources_footer":   "*Sumber: {sources}.*",
    "search_ph":        "Cari kata {lang} atau arti {gloss_lang}…",
    "kind_names":       {"palabra": "kata", "frase": "frasa", "raiz": "akar (bentuk dasar)"},
    "type_names":       {"orang": "orang", "tempat": "tempat", "bangsa": "bangsa/suku",
                         "lain": "lain-lain", "korpus": "nama (korpus)"},
    # --- pestañas y columnas ---
    "tab_main":         "Kamus utama",
    "tab_glossary":     "Glosarium",
    "tab_propers":      "Nama diri",
    "tab_morphology":   "Morfologi",
    "col_source":       "{lang}",
    "col_gloss":        "{gloss_lang}",
    "col_kind":         "Jenis",
    "col_tier":         "Tingkat",
    "col_corpus":       "Konf.korpus",
    "col_lemma":        "Lema Yunani/Ibrani",
    "col_definition":   "Definisi ({lang})",
    "col_type":         "Jenis",
    "col_srcname":      "Sumber",
    "col_affix":        "Afiks / kata",
    "col_function":     "Fungsi",
    "col_example":      "Contoh",
    "chip_A":           "A · terverifikasi",
    "chip_B":           "B · konjektur",
    "chip_C":           "C · korpus",
    "readme_sheet":     "Baca dulu",
    "readme_lines": [
        "Kamus Bahasa {lang} – {gloss_lang}",
        "Versi diperluas: semua bentuk alternatif (||), akar berimbuhan (*) dan frasa jadi lema tersendiri.",
        "",
        "TINGKAT: A=terverifikasi (leksikon/glosarium tim). B=konjektur tinggi (rendering tim utk kata Yunani/Ibrani).",
        "         C=penjajaran korpus (teks {lang} <-> retrotraduksi {bt_name}, IBM Model 1); conf_corpus=tinggi/sedang.",
        "JENIS: kata=satu kata · frasa=ungkapan · akar=bentuk dasar dari pola *…* (di teks selalu berimbuhan).",
        "Baris hijau=A, jingga=B, biru=C. Kolom 'Konfirm.korpus'=si bila entri A/B dikonfirmasi korpus.",
        "",
        "Ringkasan: {n_main} entri utama ({n_A} A / {n_B} B / {n_C} C) · {n_glos} glosarium · {n_prop} nama diri.",
        "Sumber: {sources}.",
    ],
    # --- portada del sitio (index.html) ---
    "card_kamus_title": "Kamus",
    "card_kamus_desc":  "{n_main} lema · {n_glos} glosarium · {n_prop} nama diri.",
    "card_inter_desc":  "Glosa kata-demi-kata plus terjemahan perkiraan. Dua arah, bekerja offline.",
    "go_kamus":         "Buka kamus →",
    "go_inter":         "Buka interlinear →",
    "landing_foot":     "Alat bantu kerja, bukan kamus normatif. Selalu periksa dengan penutur asli.",
    # --- nombre y descripción de la app instalable (manifest.webmanifest) ---
    "pwa_short":        "Kamus {lang}",
    "pwa_desc":         ("Kamus dan interlinear {lang}–{gloss_lang}. Bisa dipasang di ponsel "
                         "dan bekerja penuh tanpa internet."),
    # --- textos que viven dentro del JavaScript de la página ---
    "js": {
        "stat_main":  "Menampilkan <b>{shown}</b> dari {total} entri &middot; total: {all} ({A} A / {B} B)",
        "stat_glos":  "Glosarium: <b>{shown}</b> / {total} istilah",
        "stat_prop":  "Nama diri: <b>{shown}</b> / {total}",
        "stat_morf":  "Morfologi: {shown} pola",
        "no_results": "Tidak ada hasil untuk “{q}”.",
        "morf_note":  ("Pola imbuhan & kata tugas yang sering muncul — untuk menafsirkan "
                       "bentuk berimbuhan yang tak tercantum sebagai lema."),
    },
    # --- interlineal ---
    "il_title":         "Interlinear {lang} ↔ {gloss_lang}",
    "il_sub":           "Terjemahan perkiraan kata-demi-kata. <b>Bukan terjemahan halus.</b> Bekerja offline.",
    "il_dir_t2i":       "{lang} → {gloss_lang}",
    "il_dir_i2t":       "{gloss_lang} → {lang}",
    "link_to_inter":    "⇄ Buka alat Interlinear",
    "link_to_kamus":    "📖 Buka Kamus lengkap",
    "js_il": {
        "btn_swap":       "Tukar",
        "btn_copy_tr":    "Salin terjemahan",
        "btn_copy_il":    "Salin interlinear",
        "btn_copy":       "Salin",
        "btn_clear":      "Bersihkan",
        "lbl_translation": "Terjemahan perkiraan",
        "placeholder_out": "Hasil akan muncul di sini…",
        "ph_gloss":       "arti…",
        "opt_own":        "✎ tulis sendiri…",
        "tip_edit":       "Tulis/ubah arti",
        "tip_join":       "Gabung dengan kata berikut",
        "tip_split":      "Pisahkan lagi",
        "stat_found":     "{found}/{total} unit ditemukan ({pct}%)",
        "no_text":        "Tidak ada teks",
        "copy_fail":      "Gagal menyalin",
        "toast_tr":       "Terjemahan disalin ✓",
        "toast_il":       "Interlinear disalin ✓",
        "legend":         ("Frasa yang dikenal otomatis digabung — kotak bergaris biru.<br>"
                           "<b>⊕</b> gabung kata ini dengan kata berikut · <b>⊝</b> pisahkan lagi · "
                           "<b>✎</b> tulis / ubah arti sendiri (disimpan otomatis).<br>"
                           "Garis titik-titik = ada beberapa arti; klik untuk memilih. "
                           "Kotak merah = tidak ditemukan."),
        "ph_src":         "Ketik teks {lang}…",
        "ph_gl":          "Ketik teks {gloss_lang}…",
    },
    # afijos de la lengua de glosa, para buscar la raíz cuando la forma flexionada no está
    "gloss_prefixes": ["di", "meng", "meny", "mem", "men", "me", "ber", "ter",
                       "peng", "pen", "pem", "per", "ke", "se"],
    "gloss_suffixes": ["nya", "lah", "kah", "kan", "ku", "mu", "i", "an"],
}

ES = {
    "code": "es",
    "title":            "Diccionario {lang} – {gloss_lang}",
    "intro":            ("Compilado automáticamente a partir de los datos del proyecto de traducción "
                         "bíblica {lang} (Paratext). **Versión ampliada:** cada forma alternativa "
                         "(separadas por `||`), cada raíz con afijos (`*`) y cada frase es un lema aparte."),
    "lang_desc":        "{lang}{alt_paren} = {region} (ISO **{iso}**).",
    "tiers_heading":    "Niveles de confianza y tipos de lema",
    "tier_A":           "**[A]** verificado — del léxico y el glosario del equipo ({lexicon}).",
    "tier_B":           ("**[B]** conjetura de alta confianza — la forma {lang} es el *rendering* "
                         "oficial del equipo para una palabra griega o hebrea; el significado es el "
                         "estándar de esa palabra."),
    "tier_C":           ("**[C]** alineamiento de corpus — deducido automáticamente alineando el texto "
                         "{lang} con la retrotraducción en {gloss_lang} (proyecto **{bt_name}**) mediante "
                         "IBM Model 1. Fiabilidad estadística: **alta** (palabras frecuentes, p≥0.55) "
                         "o **media**."),
    "corpus_confirm":   "Si una entrada A o B queda además confirmada por el corpus, se marca con **✓corpus**.",
    "kinds_note":       ("Tipo de lema: **palabra** (una sola) · **frase** (expresión) · "
                         "**raíz** (forma base de un patrón con afijos `*…*`; en el texto siempre aparece afijada)."),
    "summary":          ("**Resumen:** {n_main} entradas principales ({n_A} A / {n_B} B / {n_C} C) · "
                         "{n_glos} de glosario · {n_prop} nombres propios."),
    "sec_main":         "Parte 1 — Diccionario principal ({lang} → {gloss_lang})",
    "sec_glossary":     "Parte 2 — Glosario de términos (con definición) [A]",
    "sec_propers":      "Parte 3 — Nombres propios (personas, lugares, pueblos)",
    "propers_note":     ("Cada nombre lleva su **tipo** (persona / lugar / pueblo / otros). "
                         "La forma estándar en {gloss_lang} se indica cuando difiere de la forma {lang}."),
    "sec_morphology":   "Apéndice — Morfología (afijos frecuentes)",
    "sources_footer":   "*Fuentes: {sources}.*",
    "search_ph":        "Busca una palabra {lang} o un significado en {gloss_lang}…",
    "kind_names":       {"palabra": "palabra", "frase": "frase", "raiz": "raíz (forma base)"},
    "type_names":       {"orang": "persona", "tempat": "lugar", "bangsa": "pueblo/etnia",
                         "lain": "otros", "korpus": "nombre (corpus)"},
    # --- pestañas y columnas ---
    "tab_main":         "Diccionario",
    "tab_glossary":     "Glosario",
    "tab_propers":      "Nombres propios",
    "tab_morphology":   "Morfología",
    "col_source":       "{lang}",
    "col_gloss":        "{gloss_lang}",
    "col_kind":         "Tipo",
    "col_tier":         "Nivel",
    "col_corpus":       "Conf.corpus",
    "col_lemma":        "Lema griego/hebreo",
    "col_definition":   "Definición ({lang})",
    "col_type":         "Tipo",
    "col_srcname":      "Fuente",
    "col_affix":        "Afijo / palabra",
    "col_function":     "Función",
    "col_example":      "Ejemplo",
    "chip_A":           "A · verificado",
    "chip_B":           "B · conjetura",
    "chip_C":           "C · corpus",
    "readme_sheet":     "Léeme primero",
    "readme_lines": [
        "Diccionario {lang} – {gloss_lang}",
        "Versión ampliada: cada forma alternativa (||), cada raíz con afijos (*) y cada frase es un lema aparte.",
        "",
        "NIVEL: A=verificado (léxico/glosario del equipo). B=conjetura alta (rendering del equipo para una palabra griega/hebrea).",
        "       C=alineamiento de corpus (texto {lang} <-> retrotraducción {bt_name}, IBM Model 1); conf_corpus=alta/media.",
        "TIPO: palabra=una sola · frase=expresión · raíz=forma base de un patrón *…* (en el texto siempre lleva afijos).",
        "Fila verde=A, naranja=B, azul=C. La columna 'Conf.corpus'=sí cuando el corpus confirma una entrada A o B.",
        "",
        "Resumen: {n_main} entradas principales ({n_A} A / {n_B} B / {n_C} C) · {n_glos} de glosario · {n_prop} nombres propios.",
        "Fuentes: {sources}.",
    ],
    # --- portada del sitio (index.html) ---
    "card_kamus_title": "Diccionario",
    "card_kamus_desc":  "{n_main} lemas · {n_glos} de glosario · {n_prop} nombres propios.",
    "card_inter_desc":  "Glosa palabra por palabra más una traducción aproximada. Bidireccional, funciona sin conexión.",
    "go_kamus":         "Abrir el diccionario →",
    "go_inter":         "Abrir el interlineal →",
    "landing_foot":     "Herramienta de trabajo, no un diccionario normativo. Contrástalo siempre con hablantes nativos.",
    # --- nombre y descripción de la app instalable (manifest.webmanifest) ---
    "pwa_short":        "Dicc. {lang}",
    "pwa_desc":         ("Diccionario e interlineal {lang}–{gloss_lang}. Se instala en el "
                         "móvil y funciona entero sin conexión."),
    # --- textos que viven dentro del JavaScript de la página ---
    "js": {
        "stat_main":  "Mostrando <b>{shown}</b> de {total} entradas &middot; total: {all} ({A} A / {B} B)",
        "stat_glos":  "Glosario: <b>{shown}</b> / {total} términos",
        "stat_prop":  "Nombres propios: <b>{shown}</b> / {total}",
        "stat_morf":  "Morfología: {shown} patrones",
        "no_results": "Sin resultados para “{q}”.",
        "morf_note":  ("Patrones de afijos y partículas frecuentes — para interpretar las formas "
                       "afijadas que no aparecen como lema."),
    },
    # --- interlineal ---
    "il_title":         "Interlineal {lang} ↔ {gloss_lang}",
    "il_sub":           "Traducción aproximada palabra por palabra. <b>No es una traducción pulida.</b> Funciona sin conexión.",
    "il_dir_t2i":       "{lang} → {gloss_lang}",
    "il_dir_i2t":       "{gloss_lang} → {lang}",
    "link_to_inter":    "⇄ Abrir el interlineal",
    "link_to_kamus":    "📖 Abrir el diccionario completo",
    "js_il": {
        "btn_swap":       "Invertir",
        "btn_copy_tr":    "Copiar la traducción",
        "btn_copy_il":    "Copiar el interlineal",
        "btn_copy":       "Copiar",
        "btn_clear":      "Limpiar",
        "lbl_translation": "Traducción aproximada",
        "placeholder_out": "El resultado aparecerá aquí…",
        "ph_gloss":       "significado…",
        "opt_own":        "✎ escribir el mío…",
        "tip_edit":       "Escribir o cambiar el significado",
        "tip_join":       "Unir con la palabra siguiente",
        "tip_split":      "Volver a separar",
        "stat_found":     "{found}/{total} unidades encontradas ({pct}%)",
        "no_text":        "No hay texto",
        "copy_fail":      "No se pudo copiar",
        "toast_tr":       "Traducción copiada ✓",
        "toast_il":       "Interlineal copiado ✓",
        "legend":         ("Las frases conocidas se unen solas — recuadro de borde azul.<br>"
                           "<b>⊕</b> unir esta palabra con la siguiente · <b>⊝</b> volver a separar · "
                           "<b>✎</b> escribir o cambiar el significado (se guarda solo).<br>"
                           "Subrayado punteado = hay varios significados; pulsa para elegir. "
                           "Recuadro rojo = no encontrado."),
        "ph_src":         "Escribe un texto en {lang}…",
        "ph_gl":          "Escribe un texto en {gloss_lang}…",
    },
    # Afijos de la lengua de glosa para buscar la raíz cuando la forma flexionada no
    # está. Solo se prueban si la búsqueda exacta falla, y solo se aceptan si la forma
    # reducida existe en el mapa; aun así, en español conviene quedarse en plural y
    # género. Las desinencias verbales no llevan a la forma de cita (*amaba → am*, no
    # *amar*), así que no se listan, y ningún prefijo castellano da la raíz.
    "gloss_prefixes": [],
    "gloss_suffixes": ["s", "es", "as", "os"],
}

LOCALES = {"id": ID, "es": ES}


class Strings:
    """Acceso a los textos con las variables del proyecto ya sustituidas."""

    def __init__(self, proj, extra=None):
        # copia, nunca el dict global: los overrides de un proyecto no deben
        # filtrarse a los demás que comparten esta lengua de glosa
        self.d = dict(LOCALES.get(proj.gloss_iso, ID))
        for k, v in (proj.cfg.get("ui") or {}).items():
            if isinstance(v, dict) and isinstance(self.d.get(k), dict):
                self.d[k] = {**self.d[k], **v}
            else:
                self.d[k] = v
        alt = proj.lang_alt
        self.vars = {
            "lang": proj.lang_name,
            "lang_alt": alt,
            "alt_paren": f" ({alt})" if alt else "",
            "iso": proj.lang_iso,
            "region": proj.lang_region or "—",
            "gloss_lang": proj.gloss_name,
            "bt_name": proj.bt["name"] if proj.bt else "—",
        }
        if extra:
            self.vars.update(extra)

    def update(self, **kw):
        self.vars.update(kw)

    def __call__(self, key, **kw):
        v = self.d.get(key, key)
        if isinstance(v, str):
            return v.format(**{**self.vars, **kw})
        return v

    def list(self, key, **kw):
        return [s.format(**{**self.vars, **kw}) for s in self.d.get(key, [])]

    def map(self, key):
        return self.d.get(key, {})

    def ui(self):
        """Blob de strings que se inyecta en el JavaScript de la página."""
        u = dict(self.d.get("js", {}))
        u["kinds"] = self.map("kind_names")
        u["types"] = self.map("type_names")
        for k in ("col_source", "col_gloss", "col_type",
                  "col_affix", "col_function", "col_example"):
            u[k] = self(k)
        return u

    def ui_interlinear(self):
        """Strings del JavaScript del interlineal.

        Sustitución segura: solo se resuelven las variables del proyecto ({lang},
        {gloss_lang}…). Los placeholders que rellena el JavaScript en tiempo de
        ejecución ({found}, {pct}, {q}…) se dejan intactos.
        """
        def safe(s):
            for k, v in self.vars.items():
                s = s.replace("{" + k + "}", str(v))
            return s
        return {k: (safe(v) if isinstance(v, str) else v)
                for k, v in self.d.get("js_il", {}).items()}
