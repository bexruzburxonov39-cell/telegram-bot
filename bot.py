import os
import json
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from anthropic import Anthropic

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "BOTFATHER_DAN_OLGAN_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY_BU_YERGA")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

with open(os.path.join(os.path.dirname(__file__), "keywords.json"), "r", encoding="utf-8") as f:
    KEYWORD_REPLIES = json.load(f)

SYSTEM_PROMPT = (
    "Siz do'stona va foydali yordamchisiz. O'zbek tilida, qisqa va tushunarli javob bering."
)


def find_keyword_reply(text: str):
    text_lower = text.lower()
    for keyword, reply in KEYWORD_REPLIES.items():
        if keyword.lower() in text_lower:
            return reply
    return None


async def ask_claude(user_text: str) -> str:
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_text}],
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Claude API xatosi: {e}")
        return "Kechirasiz, hozir javob bera olmadim. Birozdan so'ng qayta urinib ko'ring."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men 24/7 ishlaydigan avto-javob botman. Menga xabar yozing 🙂"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logger.info(f"Kelgan xabar: {user_text}")

    reply = find_keyword_reply(user_text)

    if reply is None:
        reply = await ask_claude(user_text)

    await update.message.reply_text(reply)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot ishga tushdi (polling rejimida)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
