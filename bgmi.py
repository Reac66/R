import os
import random
from telegram import Update, ReactionTypeEmoji
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# Emojis list
EMOJIS = ["❤️‍🔥", "❤️", "🔥", "💘", "🕊️", "⚡", "👏", "💯", "🍾", "🍌", "👻"]

reacted = set()

# Auto reaction function
async def auto_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.message_id:
        return

    key = (msg.chat.id, msg.message_id)
    if key in reacted:
        return

    emoji = random.choice(EMOJIS)

    try:
        await context.bot.set_message_reaction(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            reaction=[ReactionTypeEmoji(emoji=emoji)]
        )
        reacted.add(key)
        print(f"Reacted {emoji} -> {msg.message_id}")
    except Exception as e:
        print("Reaction failed:", e)

def main():
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, auto_react))

    print("🤖 BGMI Auto Reaction Bot Started")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
