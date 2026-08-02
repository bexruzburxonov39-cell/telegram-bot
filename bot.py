import os
import json
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "BOTFATHER_DAN_OLGAN_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

with open(os.path.join(os.path.dirname(__file__), "keywords.json"), "r", encoding="utf-8") as f:
    KEYWORD_REPLIES = json.load(f)

DEFAULT_REPLY = "Kechirasiz, savolingizni tushunmadim. Boshqacha so'z bilan yozib ko'ring."


def find_keyword_reply(text: str):
    text_lower = text.lower()
    for keyword, reply in KEYWORD_REPLIES.items():
        if keyword.lower() in text_lower:
            return reply
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men 24/7 ishlaydigan avto-javob botman. Menga xabar yozing 🙂"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logger.info(f"Kelgan xabar: {user_text}")

    reply = find_keyword_reply(user_text) or DEFAULT_REPLY
    await update.message.reply_text(reply)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot ishga tushdi (polling rejimida)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
