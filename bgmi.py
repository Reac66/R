import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("8592651544:AAF5HrvXcBAFi_BurXmpbYQa2vyUN_ryXAU")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set in environment variables")

ADMIN_ID = 6281757332
API_URL = "https://aetherosint.site/api/api.php?key=IntelX&type=mobile&term="

APPROVED_FILE = "approved_users.txt"
APPROVED_USERS = set()

def load_users():
    if os.path.exists(APPROVED_FILE):
        with open(APPROVED_FILE, "r") as f:
            for line in f:
                if line.strip().isdigit():
                    APPROVED_USERS.add(int(line.strip()))

def save_users():
    with open(APPROVED_FILE, "w") as f:
        for uid in APPROVED_USERS:
            f.write(str(uid) + "\n")

def is_allowed(uid):
    return uid == ADMIN_ID or uid in APPROVED_USERS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        await update.message.reply_text("Access Denied.")
        return
    await update.message.reply_text("Send valid 10-digit mobile number.")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Only owner can approve.")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /approve <user_id>")
        return

    uid = int(context.args[0])
    APPROVED_USERS.add(uid)
    save_users()
    await update.message.reply_text(f"User {uid} approved.")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        await update.message.reply_text("Access Denied.")
        return

    num = update.message.text.strip()

    if not num.isdigit() or len(num) != 10:
        await update.message.reply_text("Invalid 10-digit number.")
        return

    await update.message.reply_text("Searching...")

    try:
        resp = requests.get(API_URL + num, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        await update.message.reply_text("API error or no response.")
        return

    if not isinstance(data, dict) or "aadhaar" not in data:
        await update.message.reply_text("No data found.")
        return

    msg = f"""
Name: {data.get('name','N/A')}
Father: {data.get('father_name','N/A')}
Aadhaar: {data.get('aadhaar','N/A')}
Mobile: {data.get('mobile','N/A')}
Email: {data.get('email','N/A')}
Address: {data.get('address','N/A')}
"""
    await update.message.reply_text(msg)

def main():
    load_users()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

    print("Bot running...")
    app.run_polling()

if name == "main":
    main()
