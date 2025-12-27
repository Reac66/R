import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ==========================================
ADMIN_ID = 6281757332   # <-- Replace with your Telegram User ID

# NAYA API: mobile se Aadhaar details
API_URL = "https://aetherosint.site/api/api.php?key=IntelX&type=mobile&term="

APPROVED_FILE = "approved_users.txt"
APPROVED_USERS = set()
# ==========================================


def load_users():
    if os.path.exists(APPROVED_FILE):
        with open(APPROVED_FILE, "r") as f:
            for line in f:
                uid = line.strip()
                if uid.isdigit():
                    APPROVED_USERS.add(int(uid))


def save_users():
    with open(APPROVED_FILE, "w") as f:
        for uid in APPROVED_USERS:
            f.write(str(uid) + "\n")


def is_allowed(user_id):
    return user_id == ADMIN_ID or user_id in APPROVED_USERS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_allowed(user_id):
        await update.message.reply_text("Access Denied.\nWait for approval.")
        return

    await update.message.reply_text(
        "Welcome.\nSend any 10-digit mobile number to get Aadhaar details."
    )


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("Only owner can approve users.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Usage: /approve <user_id>")
        return

    uid = int(context.args[0])
    APPROVED_USERS.add(uid)
    save_users()

    await update.message.reply_text(f"User {uid} approved permanently.")


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("Only owner can remove users.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Usage: /remove <user_id>")
        return

    uid = int(context.args[0])

    if uid in APPROVED_USERS:
        APPROVED_USERS.remove(uid)
        save_users()
        await update.message.reply_text(f"User {uid} removed permanently.")
    else:
        await update.message.reply_text("User was not approved.")


async def search_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_allowed(user_id):
        await update.message.reply_text("Access Denied.")
        return

    number = update.message.text.strip().replace(" ", "")

    # Sirf digits + 10-digit check (agar aur length chahi ho to change kar sakte ho)
    if not number.isdigit() or len(number) != 10:
        await update.message.reply_text("Send only valid 10-digit mobile number.")
        return

    await update.message.reply_text("Searching...")

    try:
        # Naya API: direct object return karega
        resp = requests.get(API_URL + number, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Example data:
        # {
        #   "Developer": "Basic Coders | @Atinnn_00",
        #   "aadhaar": "696999326965",
        #   "address": "...",
        #   "email": "",
        #   "father_name": "Ramesh Kumar",
        #   "mobile": "8853995100",
        #   "name": "Anshul Kumar"
        # }

        # Agar kuch galat aaya
        if not isinstance(data, dict) or "aadhaar" not in data:
            await update.message.reply_text("No data found.")
            return

        name = (data.get("name") or "N/A").strip()
        fname = (data.get("father_name") or "N/A").strip()
        aadhaar = data.get("aadhaar") or "N/A"
        mobile = data.get("mobile") or "N/A"
        address = data.get("address") or "N/A"
        email = data.get("email") or ""
        if not email:
            email = "N/A"

        # Yaha DEVELOPER ko IGNORE kiya hai – use nahi kar rahe
        # dev = data.get("Developer")

        text = f"""
Input Number: {number}

Name: {name}
Father: {fname}
Aadhaar: {aadhaar}
Mobile: {mobile}
Email: {email}
Address: {address}

"""
        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


def main():
    load_users()

    app = ApplicationBuilder().token("6921680287:AAEL2ojcHgaUpOd5Gtq0R6XBtYEEiJW7pd0").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_number))

    print("Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
