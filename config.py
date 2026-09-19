import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import (
    TELEGRAM_BOT_TOKEN,
    MAX_RESULTS,
)

from database import (
    init_database,
    get_opportunities,
    get_by_category,
)


def format_row(row):
    return (
        f"#{row['id']} "
        f"⭐ {row['score']}/100\n"
        f"🚛 {row['title']}\n"
        f"📂 {row['category']}\n"
        f"📌 {row['status']}\n"
        f"🏛 {row['source']}\n"
        f"🔗 {row['url']}\n"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
🚛 AUTOTRASPORTI MELONI

Radar incentivi, contributi e normativa
per autotrasporto/artigianato.

Comandi:

/nuovi      → ultime opportunità
/tutti      → archivio
/scadenze   → misure da verificare
/camion     → camion e veicoli
/gasolio    → carburanti e accise
/rimessa    → immobili/rimesse
/energia    → energia e fotovoltaico
/formazione → formazione/personale

/aggiorna   → informazioni sul sistema

Il database distingue le opportunità
nuove da quelle già registrate.
"""

    await update.message.reply_text(
        message
    )


async def nuovi(update, context):

    rows = get_opportunities(
        limit=MAX_RESULTS,
        only_relevant=True,
    )

    if not rows:
        await update.message.reply_text(
            "🔎 Nessuna opportunità trovata."
        )
        return

    message = (
        "🚛 NUOVE OPPORTUNITÀ\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for row in rows:
        message += format_row(row) + "\n"

    await update.message.reply_text(
        message,
        disable_web_page_preview=True,
    )


async def tutti(update, context):

    rows = get_opportunities(
        limit=MAX_RESULTS,
        only_relevant=False,
    )

    if not rows:
        await update.message.reply_text(
            "📭 Archivio vuoto."
        )
        return

    message = (
        "📚 ARCHIVIO AUTOTRASPORTI\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for row in rows:
        message += format_row(row) + "\n"

    await update.message.reply_text(
        message,
        disable_web_page_preview=True,
    )


async def category_command(
    update,
    context,
    category,
    title,
):

    rows = get_by_category(
        category,
        limit=MAX_RESULTS,
    )

    if not rows:
        await update.message.reply_text(
            f"🔎 Nessun risultato per {title}."
        )
        return

    message = (
        f"{title}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for row in rows:
        message += format_row(row) + "\n"

    await update.message.reply_text(
        message,
        disable_web_page_preview=True,
    )


async def camion(update, context):
    await category_command(
        update,
        context,
        "CAMION/VEICOLI",
        "🚚 CAMION / VEICOLI",
    )


async def gasolio(update, context):
    await category_command(
        update,
        context,
        "GASOLIO/CARBURANTI",
        "⛽ GASOLIO / CARBURANTI",
    )


async def rimessa(update, context):
    await category_command(
        update,
        context,
        "IMMOBILI/RIMESSE",
        "🏭 RIMESSE / CAPANNONI",
    )


async def energia(update, context):
    await category_command(
        update,
        context,
        "ENERGIA",
        "⚡ ENERGIA",
    )


async def formazione(update, context):
    await category_command(
        update,
        context,
        "FORMAZIONE/PERSONALE",
        "👷 FORMAZIONE / PERSONALE",
    )


async def scadenze(update, context):

    rows = get_opportunities(
        limit=MAX_RESULTS,
        only_relevant=True,
    )

    rows = [
        row for row in rows
        if row["status"] != "CHIUSO"
    ]

    if not rows:
        await update.message.reply_text(
            "📅 Nessuna scadenza rilevata."
        )
        return

    message = (
        "📅 SCADENZE / MISURE ATTIVE\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for row in rows:
        message += format_row(row) + "\n"

    await update.message.reply_text(
        message,
        disable_web_page_preview=True,
    )


async def aggiorna(update, context):

    await update.message.reply_text(
        "🔄 Il sistema viene aggiornato "
        "automaticamente dal motore di scansione.\n\n"
        "Le fonti vengono analizzate e le "
        "opportunità vengono archiviate nel database."
    )


def main():

    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN non configurato."
        )

    init_database()

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("nuovi", nuovi)
    )

    app.add_handler(
        CommandHandler("tutti", tutti)
    )

    app.add_handler(
        CommandHandler("scadenze", scadenze)
    )

    app.add_handler(
        CommandHandler("camion", camion)
    )

    app.add_handler(
        CommandHandler("gasolio", gasolio)
    )

    app.add_handler(
        CommandHandler("rimessa", rimessa)
    )

    app.add_handler(
        CommandHandler("energia", energia)
    )

    app.add_handler(
        CommandHandler("formazione", formazione)
    )

    app.add_handler(
        CommandHandler("aggiorna", aggiorna)
    )

    print(
        "AUTOTRASPORTI MELONI TELEGRAM BOT AVVIATO"
    )

    app.run_polling()


if __name__ == "__main__":
    main()