import os
import re
from openai import OpenAI
from database import get_latest

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

SYSTEM = """Sei l'assistente AI di AUTOTRASPORTI MELONI, specializzato in autotrasporto e imprese artigiane in Sardegna e Italia.
Rispondi in italiano, in modo pratico e chiaro.
Puoi aiutare su incentivi, contributi, rimborsi, gasolio/accise, mezzi, rinnovo flotta,
rimorchi, officina, capannoni/rimesse, energia, formazione, lavoro, pedaggi, porti,
logistica, adempimenti e normativa.
Non inventare requisiti, importi o scadenze.
Distingui sempre tra archivio interno, informazioni ufficialmente verificate e semplice segnalazione.
Per questioni fiscali o legali importanti invita a verificare la fonte ufficiale o il professionista.
"""

SEARCH_WORDS = [
    "cerca", "ricerca", "cercami", "verifica", "controlla", "controllami",
    "aggiorna", "aggiornami", "novità", "novita", "ultime", "attuale",
    "oggi", "adesso", "recenti", "recente", "bando aperto", "scadenza",
    "quanto è", "quanto e", "è ancora aperto", "e ancora aperto",
]

def _archive_context():
    rows = get_latest(15)
    if not rows:
        return "Archivio interno: nessun dato disponibile."
    chunks = []
    for title, url, source, categories, score, deadline, status, benefit in rows:
        chunks.append(
            f"Titolo: {title}\nFonte: {source}\nCategorie: {categories}\n"
            f"Score: {score}\nScadenza: {deadline}\nStato: {status}\n"
            f"Beneficio: {benefit}\nURL: {url}"
        )
    return "Archivio interno AUTOTRASPORTI MELONI:\n\n" + "\n\n".join(chunks)

def _wants_search(question):
    q = re.sub(r"\s+", " ", question.lower()).strip()
    return any(word in q for word in SEARCH_WORDS)

def answer(question):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return "⚠️ Assistente AI non configurato: manca OPENAI_API_KEY."

    client = OpenAI(api_key=api_key)
    search_requested = _wants_search(question)

    prompt = (
        SYSTEM
        + "\n\n"
        + _archive_context()
        + "\n\n"
        + ("MODALITÀ RICERCA: l'utente ha chiesto esplicitamente una ricerca/verifica. "
           "Usa il web e privilegia fonti ufficiali e aggiornate.\n"
           if search_requested else
           "MODALITÀ RISPOSTA: NON fare ricerche web. Rispondi usando conoscenza generale "
           "e archivio interno. Se servono dati aggiornati, chiedi all'utente di dire "
           "«cerca» o «verifica».\n")
        + "\nDomanda dell'utente:\n"
        + question
    )

    kwargs = {"model": MODEL, "input": prompt}
    if search_requested:
        kwargs["tools"] = [{"type": "web_search"}]

    response = client.responses.create(**kwargs)
    return response.output_text.strip()
