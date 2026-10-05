import os
from database import init_db, get_latest, get_unnotified, get_by_category
from scanner import run_scan
from alerts import send_unnotified
from ai_assistant import answer
from config import CATEGORY_LABELS

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

HELP = (
    "🚛 AUTOTRASPORTI MELONI\n\n"
    "Scrivimi una domanda normale e ti rispondo.\n\n"
    "Esempi:\n"
    "• Ci sono contributi per comprare un camion?\n"
    "• Ci sono agevolazioni per una rimessa in Sardegna?\n"
    "• Come funziona il rimborso del gasolio?\n"
    "• Quali scadenze ci sono?\n\n"
    "📌 Comandi:\n"
    "/start — avvia il bot\n/menu — menu\n/nuovi — nuove opportunità\n"
    "/ultime — ultime opportunità\n/scadenze — scadenze archiviate\n"
    "/aggiorna — nuova scansione\n/help — guida"
)

def menu_markup():
    keys=[("news","📰 News"),("contributi","💶 Contributi"),("incentivi","🎯 Incentivi"),("bandi","📋 Bandi"),
          ("finanziamenti","🏦 Finanziamenti"),("gasolio","⛽ Gasolio"),("mezzi","🚚 Mezzi"),("immobili","🏗️ Immobili"),
          ("energia","⚡ Energia"),("normative","⚖️ Normative"),("sardegna","🏝️ Sardegna"),("scadenze","⏰ Scadenze")]
    rows=[]
    for i in range(0,len(keys),2):
        rows.append([InlineKeyboardButton(keys[i][1],callback_data="cat:"+keys[i][0]),
                     InlineKeyboardButton(keys[i+1][1],callback_data="cat:"+keys[i+1][0])])
    rows.append([InlineKeyboardButton("🆕 Nuove",callback_data="nuovi"),InlineKeyboardButton("📋 Ultime",callback_data="ultime")])
    rows.append([InlineKeyboardButton("🔄 Aggiorna",callback_data="aggiorna"),InlineKeyboardButton("ℹ️ Guida",callback_data="help")])
    return InlineKeyboardMarkup(rows)

def format_row(row):
    title, url, source, categories, score, deadline, status, benefit = row
    parts = [f"🚛 {title}", f"📍 Fonte: {source}", f"⭐ Score: {score}",
             f"📊 Stato: {status or 'DA VERIFICARE'}"]
    if categories:
        parts.append(f"🏷 {categories.replace(',', ' • ')}")
    if benefit:
        parts.append(f"💶 {benefit}")
    if deadline:
        parts.append(f"⏰ Scadenza: {deadline}")
    parts.append(f"🔗 {url}")
    return "\n".join(parts)

def format_unnotified(row):
    _, title, url, source, categories, score, deadline, status, benefit = row
    return format_row((title, url, source, categories, score, deadline, status, benefit))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚛 AUTOTRASPORTI MELONI\n\n"
        "Sono pronto. Scrivimi direttamente una domanda e ti rispondo.\n\n"
        "Esempio: «Ci sono incentivi per rinnovare un camion in Sardegna?»",
        reply_markup=menu_markup(),
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP, reply_markup=menu_markup())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP, reply_markup=menu_markup())

async def nuovi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_unnotified()
    if not rows:
        await update.message.reply_text("🆕 Nessuna nuova opportunità non ancora segnalata.")
        return
    await update.message.reply_text(
        "🆕 NUOVE OPPORTUNITÀ\n\n" + "\n\n".join(format_unnotified(r) for r in rows[:10]),
        disable_web_page_preview=True)

async def ultime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_latest(10)
    if not rows:
        await update.message.reply_text("📋 Archivio ancora vuoto.")
        return
    await update.message.reply_text(
        "📋 ULTIME OPPORTUNITÀ\n\n" + "\n\n".join(format_row(r) for r in rows),
        disable_web_page_preview=True)

async def scadenze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = [r for r in get_latest(50) if r[5]]
    if not rows:
        await update.message.reply_text("⏰ Nessuna scadenza presente nell'archivio.")
        return
    await update.message.reply_text(
        "⏰ SCADENZE\n\n" + "\n\n".join(format_row(r) for r in rows[:15]),
        disable_web_page_preview=True)

async def aggiorna(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Avvio scansione...")
    found = run_scan()
    sent = send_unnotified()
    await update.message.reply_text(
        f"✅ Scansione completata.\nNuovi elementi: {found}\nAvvisi Telegram inviati: {sent}",
        reply_markup=menu_markup())

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = (update.message.text or "").strip()
    if not q:
        return
    await update.message.chat.send_action("typing")
    try:
        response = answer(q)
        if not response:
            response = "Non sono riuscito a formulare una risposta."
        for i in range(0, len(response), 3900):
            await update.message.reply_text(response[i:i+3900], disable_web_page_preview=True)
    except Exception as exc:
        print(f"AI error: {type(exc).__name__}: {exc}")
        await update.message.reply_text(
            "⚠️ Non riesco a completare la richiesta in questo momento. "
            "Riprova tra poco.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("cat:"):
        category=query.data.split(":",1)[1]
        rows=get_by_category(category,10)
        label=CATEGORY_LABELS.get(category,category.upper())
        text=(f"{label}\n\n" + "\n\n".join(format_row(r) for r in rows)) if rows else f"{label}\n\nNessun elemento in questa categoria."
    elif query.data == "nuovi":
        rows = get_unnotified()
        text = "🆕 NUOVE OPPORTUNITÀ\n\n" + "\n\n".join(
            format_unnotified(r) for r in rows[:10]) if rows else "🆕 Nessuna nuova opportunità."
    elif query.data == "ultime":
        rows = get_latest(10)
        text = "📋 ULTIME OPPORTUNITÀ\n\n" + "\n\n".join(
            format_row(r) for r in rows) if rows else "📋 Archivio ancora vuoto."
    elif query.data == "scadenze":
        rows = [r for r in get_latest(50) if r[5]]
        text = "⏰ SCADENZE\n\n" + "\n\n".join(
            format_row(r) for r in rows[:15]) if rows else "⏰ Nessuna scadenza presente nell'archivio."
    elif query.data == "help":
        text = HELP
    elif query.data == "aggiorna":
        await query.edit_message_text("🔄 Avvio scansione...")
        found = run_scan()
        sent = send_unnotified()
        await query.message.reply_text(
            f"✅ Scansione completata.\nNuovi elementi: {found}\nAvvisi Telegram inviati: {sent}",
            reply_markup=menu_markup())
        return
    else:
        return
    await query.edit_message_text(text, reply_markup=menu_markup())

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, question))
    port = int(os.getenv("PORT", "10000"))
    public_url = os.getenv("RENDER_EXTERNAL_URL", "https://autotrasporti-meloni-ai.onrender.com").rstrip("/")
    webhook_url = f"{public_url}/telegram"
    print(f"Starting Telegram webhook: {webhook_url}")
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="telegram",
        webhook_url=webhook_url,
        drop_pending_updates=False,
    )

if __name__ == "__main__":
    main()
