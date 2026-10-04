import re
from database import get_latest
from scanner import run_scan

SEARCH_TRIGGERS = [
    "ci sono novità", "ci sono novita", "novità", "novita",
    "cosa c'è di nuovo", "cosa ce di nuovo", "che novità ci sono",
    "che novita ci sono", "aggiornamenti", "ultime novità", "ultime novita",
    "verifica", "cosa è cambiato", "cosa e cambiato",
]

def _wants_search(question):
    q = re.sub(r"\s+", " ", question.lower()).strip()
    return any(trigger in q for trigger in SEARCH_TRIGGERS)

def _format_opportunity(row):
    title, url, source, categories, score, deadline, status, benefit = row
    status = status or "DA VERIFICARE"
    icon = "🟢" if status in ("NUOVO", "APPLICABILE", "APERTO") else ("🔴" if status in ("CHIUSO", "SCADUTO") else "🟡")
    text = f"{icon} {title}\nFonte: {source}\nStato: {status}\nScore: {score}"
    if categories:
        text += f"\nCategorie: {categories}"
    if deadline:
        text += f"\nScadenza: {deadline}"
    if benefit:
        text += f"\nBeneficio: {benefit}"
    text += f"\n🔗 {url}"
    return text

def _free_news_report():
    try:
        found = run_scan()
    except Exception as exc:
        found = 0

    rows = get_latest(20)
    if not rows:
        return (
            "🚛 AUTOTRASPORTI MELONI\n\n"
            "Non ho trovato opportunità nell'archivio. "
            "La ricerca gratuita sulle fonti istituzionali non ha prodotto risultati utilizzabili."
        )

    header = (
        "🚛 AUTOTRASPORTI MELONI — AGGIORNAMENTO\n\n"
        f"🔎 Nuovi elementi rilevati: {found}\n"
        "Le informazioni sono raccolte dalle fonti configurate e vanno verificate sulla fonte ufficiale.\n\n"
    )
    items = [_format_opportunity(row) for row in rows[:10]]
    return header + "\n\n".join(items)

def _archive_answer(question):
    rows = get_latest(10)
    q = question.lower()
    if not rows:
        return (
            "🚛 AUTOTRASPORTI MELONI\n\n"
            "Non ho ancora dati nell'archivio. Scrivi «Ci sono novità?» "
            "per avviare la ricerca gratuita sulle fonti configurate."
        )

    if any(x in q for x in ("aiuto", "help", "come funziona", "cosa puoi fare")):
        return (
            "🚛 AUTOTRASPORTI MELONI\n\n"
            "Posso cercare gratuitamente aggiornamenti su bandi, incentivi, gasolio, "
            "camion, flotta, rimesse, officina, energia, formazione, lavoro, pedaggi, "
            "porti e misure per la Sardegna.\n\n"
            "Scrivi: «Ci sono novità?»"
        )

    return (
        "🚛 AUTOTRASPORTI MELONI\n\n"
        "Per una risposta aggiornata scrivi «Ci sono novità?». "
        "In questo modo avvio la ricerca gratuita sulle fonti configurate.\n\n"
        "Ultimi elementi in archivio:\n\n"
        + "\n\n".join(_format_opportunity(row) for row in rows[:5])
    )

def answer(question):
    if _wants_search(question):
        return _free_news_report()
    return _archive_answer(question)
