import os
from datetime import datetime
from database import connect, init_db
from scanner import run_scan, get_last_scan_errors
from alerts import send_message

CATEGORY_LABELS = {
    "news": "📰 NEWS",
    "contributi": "💶 CONTRIBUTI",
    "incentivi": "🎯 INCENTIVI",
    "bandi": "📋 BANDI",
    "finanziamenti": "🏦 FINANZIAMENTI",
    "gasolio": "⛽ GASOLIO",
    "mezzi": "🚚 MEZZI",
    "immobili": "🏗️ IMMOBILI",
    "energia": "⚡ ENERGIA",
    "normative": "⚖️ NORMATIVE",
    "sardegna": "🏝️ SARDEGNA",
    "scadenze": "⏰ SCADENZE",
    "altro": "📌 ALTRO",
}

def build_daily_digest(found, errors):
    conn = connect()
    rows = conn.execute("""
        SELECT title, source, score, deadline, status, benefit, url, main_category
        FROM opportunities
        ORDER BY score DESC, id DESC
        LIMIT 12
    """).fetchall()
    conn.close()

    if not rows:
        return (
            "🚛 AUTOTRASPORTI MELONI — ANALISI GIORNALIERA\n\n"
            f"🔎 Nuovi elementi rilevati: {found}\n"
            f"⚠️ Fonti con errore: {len(errors)}\n\n"
            "Nessuna opportunità rilevante trovata nelle pagine consultate."
        )

    groups = {}
    for row in rows:
        title, source, score, deadline, status, benefit, url, category = row
        groups.setdefault(category or "altro", []).append(row)

    lines = [
        "🚛 AUTOTRASPORTI MELONI — ANALISI GIORNALIERA",
        f"📅 {datetime.now().strftime('%d/%m/%Y')}",
        "",
        f"🔎 Nuovi elementi rilevati: {found}",
        f"🌐 Fonti con errore: {len(errors)}",
        "",
    ]

    for category, items in groups.items():
        lines.append(CATEGORY_LABELS.get(category, category.upper()))
        for title, source, score, deadline, status, benefit, url, _ in items[:4]:
            lines.append(f"• {title}")
            lines.append(f"  Fonte: {source} | Score: {score} | Stato: {status or 'DA VERIFICARE'}")
            if benefit:
                lines.append(f"  💶 {benefit}")
            if deadline:
                lines.append(f"  ⏰ {deadline}")
            lines.append(f"  🔗 {url}")
        lines.append("")

    if errors:
        lines.append("⚠️ Alcune fonti non sono state raggiunte; il risultato non va considerato esaustivo.")

    return "\n".join(lines)

def main():
    init_db()
    try:
        found = run_scan()
        errors = get_last_scan_errors()
        message = build_daily_digest(found, errors)
    except Exception as exc:
        message = (
            "🚛 AUTOTRASPORTI MELONI — ANALISI GIORNALIERA\n\n"
            f"❌ Analisi non completata: {type(exc).__name__}: {exc}"
        )

    if not send_message(message):
        raise SystemExit("Invio Telegram fallito.")
    print("Analisi giornaliera inviata a Telegram.")

if __name__ == "__main__":
    main()
