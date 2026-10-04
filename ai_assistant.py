import os
from openai import OpenAI
from database import get_latest

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

SYSTEM = """Sei l'assistente AI di AUTOTRASPORTI MELONI, specializzato in autotrasporto e imprese artigiane in Sardegna e Italia.
Rispondi in italiano, in modo pratico e chiaro.
Puoi aiutare su incentivi, contributi, rimborsi, gasolio/accise, mezzi, rinnovo flotta,
rimorchi, officina, capannoni/rimesse, energia, formazione, lavoro, pedaggi, porti,
logistica, adempimenti e normativa.
Non inventare requisiti, importi o scadenze. Se un'informazione è incerta o dipende
dalla data, dichiaralo chiaramente e usa la ricerca web quando disponibile.
Distingui sempre tra informazione ufficialmente verificata e semplice segnalazione.
Per questioni fiscali o legali importanti invita a verificare la fonte ufficiale o il professionista.
"""

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

def answer(question):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return "⚠️ Assistente AI non configurato: manca OPENAI_API_KEY."

    client = OpenAI(api_key=api_key)
    prompt = (
        SYSTEM
        + "\n\n"
        + _archive_context()
        + "\n\nDomanda dell'utente:\n"
        + question
    )

    response = client.responses.create(
        model=MODEL,
        tools=[{"type": "web_search"}],
        input=prompt,
    )
    return response.output_text.strip()
