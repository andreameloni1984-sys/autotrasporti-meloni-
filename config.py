import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "data/autotrasporti_meloni.db"
)

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "25"))

# Numero massimo di risultati mostrati da Telegram
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "15"))

# Sardegna
REGION_KEYWORDS = [
    "sardegna",
    "sardegnaimpresa",
    "regione sardegna",
    "buras",
    "cagliari",
    "sassari",
    "nuoro",
    "oristano",
    "olbia",
    "tempio",
    "arborea",
    "porto torres",
]

# Settore
TRANSPORT_KEYWORDS = [
    "autotrasporto",
    "autotrasporti",
    "trasporto merci",
    "trasportatore",
    "trasportatori",
    "conto terzi",
    "conto proprio",
    "logistica",
    "camion",
    "autocarro",
    "autocarri",
    "rimorchio",
    "semirimorchio",
    "flotta",
    "parco veicoli",
    "parco mezzi",
    "veicoli commerciali",
]

# Attività/artigianato
ARTISAN_KEYWORDS = [
    "artigian",
    "impresa artigiana",
    "artigiani",
    "microimpresa",
    "micro impresa",
    "piccola impresa",
    "pmi",
]

# Mezzi
VEHICLE_KEYWORDS = [
    "camion",
    "autocarro",
    "rimorchio",
    "semirimorchio",
    "veicolo commerciale",
    "veicoli commerciali",
    "n1",
    "n2",
    "n3",
    "euro vi",
    "euro v",
    "rinnovo parco",
    "rottamazione",
]

# Carburanti
FUEL_KEYWORDS = [
    "gasolio",
    "diesel",
    "carburante",
    "accisa",
    "accise",
    "credito carburante",
    "rimborso carburante",
    "hvo",
    "biocarburante",
]

# Immobili e infrastrutture
PROPERTY_KEYWORDS = [
    "capannone",
    "immobile",
    "fabbricato",
    "deposito",
    "garage",
    "rimessa",
    "piazzale",
    "area",
    "terreno",
    "officina",
]

# Energia
ENERGY_KEYWORDS = [
    "fotovoltaico",
    "fotovoltaica",
    "energia",
    "risparmio energetico",
    "efficienza energetica",
    "batterie",
    "accumulo",
    "colonnina",
    "ricarica",
    "elettrico",
]

# Formazione e personale
PEOPLE_KEYWORDS = [
    "formazione",
    "formativo",
    "corso",
    "lavoratori",
    "dipendenti",
    "assunzione",
    "assunzioni",
    "occupazione",
    "sicurezza",
]

# Finanza
FINANCE_KEYWORDS = [
    "contributo",
    "contributi",
    "incentivo",
    "incentivi",
    "agevolazione",
    "agevolazioni",
    "finanziamento",
    "finanziamenti",
    "credito d'imposta",
    "credito di imposta",
    "rimborso",
    "fondo perduto",
    "garanzia",
    "leasing",
    "voucher",
    "sovvenzione",
]

# Parole che indicano potenziale irrilevanza
EXCLUDE_KEYWORDS = [
    "agricoltura",
    "pesca",
    "turismo",
    "edilizia",
]