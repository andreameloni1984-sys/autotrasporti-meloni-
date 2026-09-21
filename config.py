import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "data/autotrasporti.db"
)

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))

MIN_RELEVANCE_SCORE = int(
    os.getenv("MIN_RELEVANCE_SCORE", "35")
)

KEYWORDS = {
    "autotrasporto": [
        "autotrasporto",
        "trasporto merci",
        "trasportatore",
        "conto terzi",
        "conto proprio",
        "camion",
        "autocarro",
        "rimorchio",
        "semirimorchio",
        "flotta"
    ],

    "gasolio": [
        "gasolio",
        "carburante",
        "diesel",
        "accisa",
        "credito carburante",
        "rimborso accise",
        "carburanti",
        "hvo"
    ],

    "mezzi": [
        "rinnovo parco",
        "veicoli",
        "mezzi pesanti",
        "autocarri",
        "euro vi",
        "euro 6",
        "ecobonus",
        "rottamazione"
    ],

    "rimessa": [
        "rimessa",
        "deposito",
        "garage",
        "piazzale",
        "area di sosta",
        "capannone",
        "immobile",
        "terreno"
    ],

    "officina": [
        "officina",
        "attrezzature",
        "macchinari",
        "impianti",
        "beni strumentali",
        "nuova sabatini"
    ],

    "energia": [
        "energia",
        "fotovoltaico",
        "autoconsumo",
        "batterie",
        "accumulo",
        "efficientamento energetico",
        "colonnine",
        "ricarica"
    ],

    "formazione": [
        "formazione",
        "patente",
        "cqc",
        "sicurezza",
        "autisti",
        "lavoratori",
        "formazione professionale"
    ],

    "lavoro": [
        "assunzione",
        "occupazione",
        "incentivo assunzione",
        "contributo assunzioni",
        "apprendistato"
    ],

    "artigianato": [
        "artigianato",
        "impresa artigiana",
        "artigiano",
        "artigiane",
        "confartigianato",
        "cna"
    ],

    "sardegna": [
        "sardegna",
        "regione sardegna",
        "sardegnaimpresa",
        "sipes",
        "buras",
        "cagliari",
        "oristano",
        "sassari",
        "nuoro",
        "sud sardegna"
    ],

    "finanza": [
        "contributo",
        "incentivo",
        "agevolazione",
        "finanziamento",
        "credito d'imposta",
        "credito imposta",
        "fondo perduto",
        "garanzia",
        "bando",
        "voucher"
    ],

    "logistica": [
        "porto",
        "porti",
        "intermodale",
        "logistica",
        "autostrada del mare",
        "trasporto combinato",
        "toll",
        "pedaggio"
    ]
}

IMPORTANT_WORDS = [
    "apertura",
    "aperto",
    "domande",
    "scadenza",
    "proroga",
    "rifinanziamento",
    "nuova misura",
    "nuovo bando",
    "modifica",
    "decreto",
    "circolare",
    "contributo",
    "incentivo",
    "credito",
    "rimborso"
]