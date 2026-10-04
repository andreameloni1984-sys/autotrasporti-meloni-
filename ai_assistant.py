import os
import re
from openai import OpenAI
from database import get_latest

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

SYSTEM = """Sei l'assistente AI di AUTOTRASPORTI MELONI, specializzato in autotrasporto e imprese artigiane in Sardegna e Italia.

Quando l'utente chiede "ci sono novità?", "novità", "cosa c'è di nuovo?", "aggiornamenti",
"che novità ci sono?" o una richiesta equivalente, DEVI fare una ricerca web completa e
aggiornata e fornire una vera ANALISI COMPLETA per AUTOTRASPORTI MELONI.

L'analisi deve coprire, quando pertinenti:
- incentivi, contributi, bandi e finanziamenti;
- gasolio, accise, rimborsi e carburanti;
- camion, rimorchi, rinnovo flotta ed ecobonus;
- rimesse, piazzali, capannoni, terreni;
- officina, macchinari e Nuova Sabatini;
- energia, fotovoltaico e accumulo;
- formazione, CQC, autisti, assunzioni;
- pedaggi, porti, logistica e collegamenti Sardegna-continente;
- normativa e adempimenti;
- misure Regione Sardegna, Stato e UE rilevanti per l'impresa.

Distingui chiaramente:
🟢 NUOVO/APPLICABILE
🟡 DA VERIFICARE
🔴 CHIUSO/SCADUTO
Per ogni opportunità importante indica cosa significa concretamente per l'azienda,
beneficio, requisiti essenziali, scadenza e fonte ufficiale quando disponibili.
Non inventare importi, requisiti o scadenze.

Per le domande normali NON fare ricerche web automaticamente: usa conoscenza generale
e archivio interno. Se l'utente vuole una verifica aggiornata può chiedere "ci sono novità?"
o "verifica".
"""

SEARCH_TRIGGERS = [
    "ci sono novità", "ci sono novita", "novità", "novita",
    "cosa c'è di nuovo", "cosa ce di nuovo", "che novità ci sono",
    "che novita ci sono", "aggiornamenti", "ultime novità", "ultime novita",
]

def _archive_context():
    rows = get_latest(20)
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
    return any(trigger in q for trigger in SEARCH_TRIGGERS)

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
        + ("RICERCA COMPLETA RICHIESTA: cerca sul web informazioni aggiornate e pertinenti. "
           "Privilegia fonti ufficiali (Regione Sardegna, MIT, Agenzia Entrate, ADM, INPS, "
           "MIMIT, MASE, Gazzetta Ufficiale, CCIAA e fonti istituzionali). Confronta le fonti "
           "e non limitarti ai primi risultati. Produci un'analisi completa e pratica.\n"
           if search_requested else
           "NESSUNA RICERCA WEB: rispondi solo con conoscenza generale e archivio interno.\n")
        + "\nDomanda dell'utente:\n"
        + question
    )

    kwargs = {"model": MODEL, "input": prompt}
    if search_requested:
        kwargs["tools"] = [{"type": "web_search"}]

    response = client.responses.create(**kwargs)
    return response.output_text.strip()
