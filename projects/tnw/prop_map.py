# -*- coding: utf-8 -*-
# Tonsawang (tnw) — nombres propios y compuestos capitalizados.
#
# Criterio: solo se mueve a TERM_MOVE lo que tiene respaldo en los datos del
# propio proyecto — glosa [A] del Lexicon o rendering [B] del equipo. Las formas
# tonsawang cuyo significado no se puede sostener con esa evidencia se dejan sin
# tocar, para que las resuelva el equipo. Ver la lista al final del fichero.

# (1) Formas capitalizadas que son en realidad TÉRMINOS TRADUCIBLES.
#     Se mueven al diccionario principal con esta glosa indonesia. [B]
TERM_MOVE = {
    # nombres y títulos divinos
    "Ningumélé'd": "Allah",
    "Ninguméléd": "Allah",
    "Ningumélé'dnu": "Allahmu",
    "Ningumélé'd mapéreta tanu Da'ja": "Allah yang memerintah sebagai Raja",
    "Ningumélé'd mapéréta tanu da'ja": "Allah yang memerintah sebagai Raja",
    "Ningumélé'd é makawasa tanu da'ja": "Allah yang berkuasa sebagai Raja",
    "Amang": "bapa; Bapa (sebutan bagi Allah)",
    "Tuhan": "Tuhan",
    "Tuhanku": "Tuhanku",
    "Kristus": "Kristus, Mesias",
    "Mesias": "Mesias",
    "Bata' i Ningumélé'd": "Anak Allah",
    "How é mbata' i Ningumélé'd": "Engkau Anak Allah",
    "Bata' i totumu'": "Anak Manusia",
    "Ni'it matatang": "Yang Mahatinggi",
    "Roh": "roh; Roh",
    "Roh i Ningumélé'd": "Roh Allah",
    "Roh lenas": "Roh Kudus",
    "Roh lénas": "Roh Kudus",
    "Roh ta'pia": "roh jahat",
    "Paki'itan i setang": "Iblis, pemfitnah",
    "Kanalu": "roh, napas",
    "Kanaluhu": "roh, napas",
    "BéwélésNa": "kasih sayang-Nya",
    "Kawasana": "kuasa, wewenang",

    # términos religiosos y del culto
    "A'bar Mauléng": "kabar baik, Injil",
    "Na'bar mauléng": "kabar baik, Injil",
    "Mbalé Lénas": "Bait Suci, rumah Allah",
    "Bale i Ningumélé'd": "rumah Allah",
    "Buni Lénas": "Ruang Kudus",
    "Lenas": "kudus, suci",
    "Lénas": "kudus, suci",
    "Imam": "imam",
    "Imam Bako'": "imam besar",
    "Imam kapala": "imam kepala",
    "Na'bi": "nabi",
    "Na'bi towo": "nabi palsu",
    "Sanipén": "salib",
    "Tapélowi'd": "juruselamat, penyelamat",
    "Mawalowi'd": "menyelamatkan; keselamatan",
    "Mawé'disém": "bertobatlah",
    "Mawé'disémre": "bertobatlah",
    "Dayowén": "terpujilah",
    "Kamahamangén nange": "diberkatilah",
    "Konunga'an": "kemuliaan",
    "Pahohuta'an i Agama Yahudi": "majelis agama Yahudi (Sanhedrin)",

    # cargos, grupos y gentilicios
    "Kaisar": "Kaisar, Maharaja Roma",
    "Ha'kim": "hakim; pemimpin, penguasa",
    "Maha'kim": "menghakimi, mengadili",
    "Kupangasing": "pemungut cukai",
    "Tou Gerasa": "orang Gerasa",
    "Tou i Parisi": "orang Farisi",
    "Tou i Samaria": "orang Samaria",
    "Manga da'ja i bangsa-bangsa é tahi'i mahailala i Ningumélé'd":
        "raja-raja bangsa yang tidak mengenal Allah",
    "Ata": "hamba, budak",
    "Ata-Na": "hamba-Nya",
    "Tuang": "tuan",
    "Po'gku": "saudara (laki-laki)",
    "Karua": "teman, sekutu; dengan",

    # cosas, plantas, medidas
    "Latang": "pakaian, jubah",
    "Tu'd i nara": "pohon ara",
    "Bua' i nara": "buah ara",
    "Bua' i nanggor": "buah anggur",
    "Sesawi": "sesawi (biji sesawi)",
    "Bale'd i talun": "serigala",
    "Legion": "legiun (pasukan)",
    "Mina": "mina (satuan uang)",

    # palabras gramaticales y adjetivos que el detector capitalizó
    "Ahu": "aku; hamba",
    "How": "engkau",
    "Sia": "ia, dia",
    "Oho": "bersama; itu",
    "Musti": "harus",
    "Mauléng": "baik, elok, indah",
    "Matatang": "mahatinggi, tinggi",
    "Ni'itio' matatang": "sangat tinggi",
    "Totu'u": "benar, sejati; sungguh",
    "Kaulitanna": "sungguh, sebenarnya",
    "Tumuli'd": "melakukan",
    "Tépai": "tanda, bukti",
    "Iehem": "berilah",
    "Lohow": "seluruh; bumi, tanah",
}

# (2) Nombres propios genuinos -> tipo.  orang=persona, tempat=lugar,
#     bangsa=pueblo/nación, lain=otro (ángel, título, moneda, fiesta, etc.)
PROP = {
 "Abia":"orang","Abilene":"tempat","Abraham":"orang","Adam":"orang","Adi":"orang",
 "Admin":"orang","Agabus":"orang","Agustus":"orang","Akaya":"tempat","Akwila":"orang",
 "Aleksander":"orang","Aleksandria":"tempat","Alpeus":"orang","Aminadab":"orang",
 "Amos":"orang","Ananias":"orang","Andreas":"orang","Antiokhia":"tempat",
 "Antiokhia a sakumén i Pisidia":"tempat","Antiokia":"tempat","Apolonia":"tempat",
 "Apolos":"orang","Areopagus":"tempat","Aristakhus":"orang","Aristarkhus":"orang",
 "Arni":"orang","Arpakhsad":"orang","Artemis":"lain","Asia":"tempat","Asos":"tempat",
 "Asyer":"orang","Atalia":"tempat","Atena":"tempat","Babel":"tempat","Barabas":"orang",
 "Barnabas":"orang","Barnabas bo si Paulus":"orang","Barsabas":"orang",
 "Bartolomeus":"orang","Baryesus":"orang","Benyamin":"orang","Berea":"tempat",
 "Betania":"tempat","Betlehem":"tempat","Betpage":"tempat","Betsaida":"tempat",
 "Bitinia":"tempat","Boas":"orang","Bélsebul":"lain","Daud":"orang","Demetrius":"orang",
 "Eber":"orang","Eli":"orang","Elia":"orang","Elieser":"orang","Elisa":"orang",
 "Elisabeth":"orang","Elmadam":"orang","Elyakim":"orang","Emaus":"tempat",
 "Eneas":"orang","Enos":"orang","Epesus":"tempat","Er":"orang","Erastus":"orang",
 "Gabriel":"lain","Galilea":"tempat","Gayus":"orang","Génésaret":"tempat",
 "Habel":"orang","Hakal-Dama":"tempat","Hana":"orang","Hanas":"orang","Harun":"orang",
 "Henokh":"orang","Herodes":"orang","Herodias":"orang","Hesli":"orang","Hezron":"orang",
 "Isai":"orang","Isak":"orang","Ishak":"orang","Iskariot":"lain","Israel":"bangsa",
 "Iturea":"tempat","Kaisarea":"tempat","Kapadokia":"tempat","Kapernaum":"tempat",
 "Kapérnaum":"tempat","Kauda":"tempat","Kayafas":"orang","Kenan":"orang",
 "Khorazim":"tempat","Khusa":"orang","Kirene":"tempat","Kirenius":"orang",
 "Kleopas":"orang","Korintuswe":"tempat","Kos":"tempat","Kosam":"orang","Kreta":"tempat",
 "Lamekh":"orang","Lasarus":"orang","Lewi":"orang","Libia":"tempat","Lisanias":"orang",
 "Lot":"orang","Maat":"orang","Mahalaleel":"orang","Makedonia":"tempat","Malkhi":"orang",
 "Maria":"orang","Maria tou i Magdala":"orang","Marta":"orang","Matat":"orang",
 "Matata":"orang","Matias":"orang","Matika":"orang","Matius":"orang","Media":"tempat",
 "Melea":"orang","Mesir":"tempat","Mesopotamia":"tempat","Metusalah":"orang",
 "Musa":"orang","Naaman":"orang","Nagai":"orang","Nahason":"orang","Nahor":"orang",
 "Nahum":"orang","Nain":"tempat","Nasaret":"tempat","Natan":"orang","Neri":"orang",
 "Nuh":"orang","Obed":"orang","Pampilia":"tempat","Panuel":"orang","Partia":"tempat",
 "Paskah":"lain","Patara":"tempat","Paulus":"orang","Peleg":"orang","Penisia":"tempat",
 "Peres":"orang","Petrus":"orang","Pilatus":"orang","Pilipus":"orang","Pirdaus":"lain",
 "Pontius":"orang","Pontus":"tempat","Prigia":"tempat","Ptolemais":"tempat",
 "Rehu":"orang","Resa":"orang","Rodos":"tempat","Roma":"tempat","Sakaria":"orang",
 "Sakeus":"orang","Sakharia":"orang","Salmon":"orang","Salomo":"orang","Samaria":"tempat",
 "Sarfat":"tempat","Sebedeus":"orang","Selot":"lain","Sem":"orang","Serubabel":"orang",
 "Serug":"orang","Set":"orang","Si'don":"tempat","Siloam":"tempat","Simei":"orang",
 "Simeon":"orang","Simon":"orang","Siprus":"tempat","Siria":"tempat","So'dom":"tempat",
 "Sodom":"tempat","Susana":"orang","Teopilus é pahisingéiku":"orang","Terah":"orang",
 "Tiberius":"orang","Timotius":"orang","Tirus":"tempat","Tirus bo Si'don":"tempat",
 "Tomas":"orang","Trakhonitis":"tempat","Yairus":"orang","Yakobus":"orang",
 "Yakub":"orang","Yanai":"orang","Yared":"orang","Yehuda":"orang","Yeriho":"tempat",
 "Yerikho":"tempat","Yerusalem":"tempat","Yerusalém":"tempat","Yesaya":"orang",
 "Yeses":"orang","Yesua":"orang","Yesus":"orang","Yoda":"orang","Yoel":"orang",
 "Yohana":"orang","Yohanan":"orang","Yohanes":"orang","Yonam":"orang","Yordan":"tempat",
 "Yorim":"orang","Yosekh":"orang","Yudas":"orang","Yudea":"tempat","Yunani":"bangsa",
 "Yunus":"orang","Yustus":"orang","Yusup":"orang",

 # formas en minúscula tal como aparecen en el corpus
 "agripa":"orang","ananias":"orang","antiokia":"tempat","artemis":"lain",
 "barnabas":"orang","damsyik":"tempat","epesus":"tempat","galilea":"tempat",
 "kilikia":"tempat","kornelius":"orang","lewi":"orang","listra":"tempat",
 "makedonia":"tempat","mesias":"lain","mesir":"tempat","musa":"orang",
 "nasaret":"tempat","paskah":"lain","paulus":"orang","peliks":"orang",
 "pestus":"orang","pilatus":"orang","pilipus":"orang","romawi":"bangsa",
 "saulus":"orang","silas":"orang","simeon":"orang","simon":"orang",
 "siprus":"tempat","stepanus":"orang","tesalonika":"tempat","timotius":"orang",
 "tirus":"tempat","yairus":"orang","yakobus":"orang","yesaya":"orang",
 "yope":"tempat","yunani":"bangsa","yusup":"orang",
}

# (3) Forma indonesia estándar donde difiere de la forma tonsawang.
PROP_ID = {
 "Akaya":"Akhaya","Alpeus":"Alfeus","Antiokia":"Antiokhia",
 "Antiokhia a sakumén i Pisidia":"Antiokhia di Pisidia",
 "Aristakhus":"Aristarkhus","Barnabas bo si Paulus":"Barnabas dan Paulus",
 "Betpage":"Betfage","Bélsebul":"Beelzebul (penghulu setan)",
 "Elieser":"Eliezer","Elisabeth":"Elisabet","Epesus":"Efesus","epesus":"Efesus",
 "Génésaret":"Genesaret","Hakal-Dama":"Hakal-Dama (Tanah Darah)",
 "Isak":"Ishak","Iskariot":"Iskariot (dari Keriot)","Kapérnaum":"Kapernaum",
 "Khusa":"Khuza","Korintuswe":"Korintus","Lasarus":"Lazarus",
 "Maria tou i Magdala":"Maria Magdalena","Nasaret":"Nazaret","nasaret":"Nazaret",
 "Panuel":"Fanuel","Penisia":"Fenisia","peliks":"Feliks","pestus":"Festus",
 "Pilipus":"Filipus","pilipus":"Filipus","Pirdaus":"Firdaus","Prigia":"Frigia",
 "Sakaria":"Zakharia","Sakharia":"Zakharia","Sakeus":"Zakheus",
 "Sebedeus":"Zebedeus","Selot":"Zelot","Serubabel":"Zerubabel",
 "Si'don":"Sidon","So'dom":"Sodom","stepanus":"Stefanus",
 "Teopilus é pahisingéiku":"Teofilus","Tirus bo Si'don":"Tirus dan Sidon",
 "Yeriho":"Yerikho","Yerusalém":"Yerusalem","Yusup":"Yusuf","yusup":"Yusuf",
}

# --- PENDIENTE PARA EL EQUIPO ---------------------------------------------
# Formas capitalizadas cuyo significado no se puede sostener con [A] ni [B].
# No se han tocado a propósito: siguen apareciendo como "nombre propio" en el
# diccionario hasta que el equipo diga qué son.
#
#   Balun · Batu pahilingan · Bekow · Bi'bit · Bonang · Da' · Dasing ·
#   Ihalésange · Kamangénange · Kiongnga · Kusi' · Lohos · Lowi'dén ·
#   Maharaw, i mawaharaw, mawaharaw · Manésélém · Manga ko'daitNa monunga mio' ·
#   Mawé'disangere · Meya panana'gan · Moho'imbahut · Mosononoioho ·
#   Na'am ahu itarukira · Ningumélé'd noras Sia mahi tanu Da'ja · Pa' ·
#   Pangeleianange kamang · Pangépe'an · Parandian · Piring · Poapar ·
#   Sa ahu kumua · Sa si latahula ahi'i ma pahataan · Sinahei · Tialo · Tiei ·
#   Ulah · Uli-ulit sia sumairi bo mawaéte' · Wa'i mbata'Ku
