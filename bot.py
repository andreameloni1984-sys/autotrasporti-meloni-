import os
from database import init_db, get_latest, get_unnotified
from scanner import run_scan
from alerts import send_unnotified

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
except ImportError:
    Update = None
    Application = None
    CommandHandler = None
    ContextTypes = None


async def start(update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
    await update.message.reply_text(
        "🚛 AUTOTRASPORTI MELONI\n"
        "Bot di monitoraggio incentivi, rimborsi e novità per autotrasporto."
    )


async def nuovi(update, context):
    rows = get_unnotified()

    if not rows:
        await update.message.reply_text("Nessuna nuova opportunità.")
        return

    text = "\n\n".join(
        f"🚛 {r[1]}\nFonte: {r[3]}\nScore: {r[5]}\n{r[2]}"
        for r in rows[:10]
    )

    await update.message.reply_text(text)


async def aggiorna(update, context):
    found = run_scan()
    sent = send_unnotified()
    await update.message.reply_text(
        f"Scansione completata. Nuovi elementi: {found}. Avvisi inviati: {sent}."
    )


def main():
    init_db()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "")

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN non configurato.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nuovi", nuovi))
    app.add_handler(CommandHandler("aggiorna", aggiorna))

    app.run_polling()


if __name__ == "__main__":
    main()
