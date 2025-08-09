import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler
from urllib.parse import urlparse

BOT_TOKEN = os.environ.get("7506281676:AAFV-pMaVUi6D2Yul3xKgrthG1GJAWcETeU")  # simpan token di Railway ENV
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://app-delta-jet-50.vercel.app/")

async def start(update, context):
    args = context.args
    ref_id = None
    if args:
        try:
            ref_id = int(args[0])
        except:
            pass

    user_id = update.effective_user.id

    # Daftarkan user di backend
    requests.get(f"{BACKEND_URL}/api/balance", params={"user_id": user_id})
    if ref_id and ref_id != user_id:
        requests.post(f"{BACKEND_URL}/api/reward", json={"user_id": ref_id, "amount": 10})

    kb = [[InlineKeyboardButton("💰 Buka Game", web_app=WebAppInfo(url=f"{WEBAPP_URL}"))]]
    await update.message.reply_text("Selamat datang! Mainkan game dan dapatkan koin!", reply_markup=InlineKeyboardMarkup(kb))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
