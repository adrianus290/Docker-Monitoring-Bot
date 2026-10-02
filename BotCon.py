import os
import docker
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
ALLOWED_CHAT_ID = "YOUR CHAT ID"
client = docker.from_env()

# Command /start atau /status untuk melihat container yang mati
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return

    containers = client.containers.list(all=True, filters={"status": "exited"})
    if not containers:
        await update.message.reply_text("✅ Semua container saat ini berjalan normal!")
        return

    keyboard = []
    for c in containers:
        name = c.name
        keyboard.append([InlineKeyboardButton(f"▶️ Start {name}", callback_data=f"start_{name}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🚨 **Daftar Container Mati:**\nPilih container yang ingin dinyalakan kembali:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Handler untuk memproses klik pada tombol Inline Keyboard
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.message.chat.id != ALLOWED_CHAT_ID:
        return

    await query.answer()
    data = query.data

    if data.startswith("start_"):
        container_name = data.replace("start_", "")
        try:
            container = client.containers.get(container_name)
            container.start()
            await query.edit_message_text(
                f"✅ Container **{container_name}** berhasil dinyalakan kembali!",
                parse_mode="Markdown"
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ Gagal menyalakan **{container_name}**: {str(e)}",
                parse_mode="Markdown"
            )

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    # Daftarkan command & handler tombol
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot Controller Running...")
    app.run_polling()

