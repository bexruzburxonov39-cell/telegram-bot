import os
import json
import logging
import requests
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

WEATHER_CODES = {
    0: "Ochiq osmon ☀️", 1: "Deyarli ochiq 🌤️", 2: "Qisman bulutli ⛅", 3: "Bulutli ☁️",
    45: "Tumanli 🌫️", 48: "Tumanli 🌫️",
    51: "Mayda yomg'ir 🌦️", 53: "Yomg'ir 🌦️", 55: "Kuchli yomg'ir 🌧️",
    61: "Yengil yomg'ir 🌧️", 63: "Yomg'ir 🌧️", 65: "Kuchli yomg'ir 🌧️",
    71: "Yengil qor ❄️", 73: "Qor ❄️", 75: "Kuchli qor ❄️",
    80: "Jala 🌦️", 81: "Jala 🌧️", 82: "Kuchli jala ⛈️",
    95: "Momaqaldiroq ⛈️",
}


def find_keyword_reply(text: str):
    text_lower = text.lower()
    for keyword, reply in KEYWORD_REPLIES.items():
        if keyword.lower() in text_lower:
            return reply
    return None


def get_weather(city: str) -> str:
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_res = requests.get(geo_url, params={"name": city, "count": 1, "language": "ru"}, timeout=10).json()

        if not geo_res.get("results"):
            return f"'{city}' nomli shaharni topa olmadim. Nomini to'g'ri yozib qayta urinib ko'ring."

        place = geo_res["results"][0]
        lat, lon = place["latitude"], place["longitude"]
        place_name = place.get("name", city)

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_res = requests.get(weather_url, params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code,wind_speed_10m",
            "timezone": "auto"
        }, timeout=10).json()

        current = weather_res["current"]
        temp = current["temperature_2m"]
        code = current["weather_code"]
        wind = current["wind_speed_10m"]
        condition = WEATHER_CODES.get(code, "Noma'lum")

        return (
            f"📍 {place_name} uchun hozirgi ob-havo:\n\n"
            f"🌡️ Harorat: {temp}°C\n"
            f"{condition}\n"
            f"💨 Shamol: {wind} km/soat"
        )
    except Exception as e:
        logger.error(f"Ob-havo xatosi: {e}")
        return "Kechirasiz, ob-havo ma'lumotini olishda xatolik yuz berdi."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men 24/7 ishlaydigan avto-javob botman.\n\n"
        "Ob-havoni bilish uchun: 'ob-havo Toshkent' deb yozing 🌤️"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logger.info(f"Kelgan xabar: {user_text}")

    text_lower = user_text.lower().strip()

    if text_lower.startswith("ob-havo") or text_lower.startswith("ob havo"):
        city = user_text.split(maxsplit=1)
        if len(city) < 2:
            await update.message.reply_text("Qaysi shahar uchun? Masalan: 'ob-havo Samarqand'")
            return
        city_name = city[1]
        await update.message.reply_text("Qidiryapman... ⏳")
        weather_text = get_weather(city_name)
        await update.message.reply_text(weather_text)
        return

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
