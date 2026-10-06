import json
import os
import hashlib
from datetime import datetime
from database import connect, init_db
from scanner import run_scan, get_last_scan_errors
from alerts import send_message

STATE_PATH = "data/daily_seen.json"

CATEGORY_LABELS = {
    "news": "📰 NEWS", "contributi": "💶 CONTRIBUTI", "incentivi": "🎯 INCENTIVI",
    "bandi": "📋 BANDI", "finanziamenti": "🏦 FINANZIAMENTI", "gasolio": "⛽ GASOLIO",
    "mezzi": "🚚 MEZZI", "immobili": "🏗️ IMMOBILI", "energia": "⚡ ENERGIA",
    "normative": "⚖️ NORMATIVE", "sardegna": "🏝️ SARDEGNA", "scadenze": "⏰ SCADENZE",
    "altro": "📌 ALTRO",
}

def _fingerprint(row):
    title, source, score, deadline, status, benefit, url, category = row
    value = "|".join(str(x or "") for x in (title, source, score, deadline, status, benefit, category))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def _load_state():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_state(rows):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    state = {row[6]: _fingerprint(row) for row in rows if row[6]}
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)

def _current_rows():
    conn = connect()
    rows = conn.execute("""
        SELECT title, source, score, deadline, status, benefit, url, main_category
        FROM opportunities ORDER BY score DESC, id DESC
    """).fetchall()
    conn.close()
    return rows

def build_daily_digest(rows, errors):
    if not rows:
        return (
            "🚛 AUTOTRASPORTI MELONI — ANALISI GIORNALIERA\n\n"
            f"🌐 Fonti con errore: {len(errors)}\n\n"
            "Nessuna opportunità rilevante trovata oggi."
        )

    groups = {}
    for row in rows[:15]:
        groups.setdefault(row[7] or "altro", []).append(row)

    lines = [
        "🚛 AUTOTRASPORTI MELONI — ANALISI GIORNALIERA",
        f"📅 {datetime.now().strftime('%d/%m/%Y')}",
        f"🆕 Nuove/aggiornate: {len(rows)}",
        f"🌐 Fonti con errore: {len(errors)}",
        "",
    ]
    for category, items in groups.items():
        lines.append(CATEGORY_LABELS.get(category, category.upper()))
        for title, source, score, deadline, status, benefit, url, _ in items[:5]:
            lines.append(f"• {title}")
            lines.append(f"  Fonte: {source} | Score: {score} | Stato: {status or 'DA VERIFICARE'}")
            if benefit:
                lines.append(f"  💶 {benefit}")
            if deadline:
                lines.append(f"  ⏰ {deadline}")
            lines.append(f"  🔗 {url}")
        lines.append("")
    if errors:
        lines.append("⚠️ Alcune fonti non sono state raggiunte: l'analisi potrebbe non essere completa.")
    return "\n".join(lines)

def main():
    init_db()
    previous = _load_state()
    try:
        run_scan()
        errors = get_last_scan_errors()
        current = _current_rows()
        fresh = [row for row in current if previous.get(row[6]) != _fingerprint(row)]
        # Salva sempre lo stato completo per il confronto del giorno successivo.
        _save_state(current)
        message = build_daily_digest(fresh, errors)
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
