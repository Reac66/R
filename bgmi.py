import random
from telegram import Update, ReactionTypeEmoji
from telegram.ext import Application, MessageHandler, ContextTypes, filters

EMOJIS = ["❤️‍🔥", "❤️", "🔥", "💘", "🕊️", "⚡", "👏", "💯", "🍾", "🍌", "👻"]
reacted = set()
# Code By : @Atinnn_00
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
        print(f"Reacted {emoji} - {msg.message_id}")
    except:
        pass
# Code By : @Atinnn_00
def main():
    BOT_TOKEN = "8592651544:AAF5HrvXcBAFi_BurXmpbYQa2vyUN_ryXAU"
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, auto_react))
    app.run_polling(drop_pending_updates=True)
# Code By : @Atinnn_00
if __name__ == "__main__":
    main()