import os
from database import init_db, get_latest, get_unnotified
from scanner import run_scan
from alerts import send_unnotified

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

HELP = (
    "🚛 AUTOTRASPORTI MELONI\n\n"
    "Il tuo centro Telegram per incentivi, rimborsi e novità.\n\n"
    "📌 Comandi:\n"
    "/start — avvia il bot\n"
    "/menu — apre il menu\n"
    "/nuovi — nuove opportunità non ancora segnalate\n"
    "/ultime — ultime opportunità archiviate\n"
    "/scadenze — opportunità con scadenza indicata\n"
    "/aggiorna — esegue una nuova scansione\n"
    "/help — guida"
)


def menu_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🆕 Nuove", callback_data="nuovi"),
            InlineKeyboardButton("📋 Ultime", callback_data="ultime"),
        ],
        [
            InlineKeyboardButton("⏰ Scadenze", callback_data="scadenze"),
            InlineKeyboardButton("🔄 Aggiorna", callback_data="aggiorna"),
        ],
        [
            InlineKeyboardButton("ℹ️ Guida", callback_data="help"),
        ],
    ])


def format_row(row):
    title, url, source, categories, score, deadline, status, benefit = row
    parts = [
        f"🚛 {title}",
        f"📍 Fonte: {source}",
        f"⭐ Score: {score}",
        f"📊 Stato: {status or 'DA VERIFICARE'}",
    ]
    if categories:
        parts.append(f"🏷 {categories.replace(',', ' • ')}")
    if benefit:
        parts.append(f"💶 {benefit}")
    if deadline:
        parts.append(f"⏰ Scadenza: {deadline}")
    parts.append(f"🔗 {url}")
    return "\n".join(parts)


def format_unnotified(row):
    item_id, title, url, source, categories, score, deadline, status, benefit = row
    return format_row(
        (title, url, source, categories, score, deadline, status, benefit)
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚛 AUTOTRASPORTI MELONI\n\n"
        "Benvenuto. Qui trovi incentivi, rimborsi, bandi, "
        "agevolazioni e novità utili all'autotrasporto.\n\n"
        "Usa il menu qui sotto.",
        reply_markup=menu_markup(),
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP, reply_markup=menu_markup())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP, reply_markup=menu_markup())


async def nuovi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_unnotified()
    if not rows:
        await update.message.reply_text(
            "🆕 Nessuna nuova opportunità non ancora segnalata.",
            reply_markup=menu_markup(),
        )
        return

    text = "🆕 NUOVE OPPORTUNITÀ\n\n" + "\n\n".join(
        format_unnotified(row) for row in rows[:10]
    )
    await update.message.reply_text(text, disable_web_page_preview=True)


async def ultime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_latest(10)
    if not rows:
        await update.message.reply_text(
            "📋 Archivio ancora vuoto.", reply_markup=menu_markup()
        )
        return

    text = "📋 ULTIME OPPORTUNITÀ\n\n" + "\n\n".join(
        format_row(row) for row in rows
    )
    await update.message.reply_text(text, disable_web_page_preview=True)


async def scadenze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = [r for r in get_latest(50) if r[5]]
    if not rows:
        await update.message.reply_text(
            "⏰ Nessuna scadenza presente nell'archivio.",
            reply_markup=menu_markup(),
        )
        return

    text = "⏰ SCADENZE\n\n" + "\n\n".join(
        format_row(row) for row in rows[:15]
    )
    await update.message.reply_text(text, disable_web_page_preview=True)


async def aggiorna(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Avvio scansione...")
    found = run_scan()
    sent = send_unnotified()
    await update.message.reply_text(
        f"✅ Scansione completata.\n"
        f"Nuovi elementi: {found}\n"
        f"Avvisi Telegram inviati: {sent}",
        reply_markup=menu_markup(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "nuovi":
        rows = get_unnotified()
        if not rows:
            await query.edit_message_text(
                "🆕 Nessuna nuova opportunità non ancora segnalata.",
                reply_markup=menu_markup(),
            )
            return
        text = "🆕 NUOVE OPPORTUNITÀ\n\n" + "\n\n".join(
            format_unnotified(row) for row in rows[:10]
        )
        await query.edit_message_text(text, reply_markup=menu_markup())
        return

    if query.data == "ultime":
        rows = get_latest(10)
        if not rows:
            await query.edit_message_text(
                "📋 Archivio ancora vuoto.", reply_markup=menu_markup()
            )
            return
        text = "📋 ULTIME OPPORTUNITÀ\n\n" + "\n\n".join(
            format_row(row) for row in rows
        )
        await query.edit_message_text(text, reply_markup=menu_markup())
        return

    if query.data == "scadenze":
        rows = [r for r in get_latest(50) if r[5]]
        if not rows:
            await query.edit_message_text(
                "⏰ Nessuna scadenza presente nell'archivio.",
                reply_markup=menu_markup(),
            )
            return
        text = "⏰ SCADENZE\n\n" + "\n\n".join(
            format_row(row) for row in rows[:15]
        )
        await query.edit_message_text(text, reply_markup=menu_markup())
        return

    if query.data == "help":
        await query.edit_message_text(HELP, reply_markup=menu_markup())
        return

    if query.data == "aggiorna":
        await query.edit_message_text("🔄 Avvio scansione...")
        found = run_scan()
        sent = send_unnotified()
        await query.message.reply_text(
            f"✅ Scansione completata.\n"
            f"Nuovi elementi: {found}\n"
            f"Avvisi Telegram inviati: {sent}",
            reply_markup=menu_markup(),
        )


def main():
    init_db()

    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN non configurato.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("nuovi", nuovi))
    app.add_handler(CommandHandler("ultime", ultime))
    app.add_handler(CommandHandler("scadenze", scadenze))
    app.add_handler(CommandHandler("aggiorna", aggiorna))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
