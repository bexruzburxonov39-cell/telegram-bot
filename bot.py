    import os
import json
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# O'zbekiston viloyat markazlari
UZBEK_CITIES = [
    "Toshkent", "Andijon", "Buxoro", "Farg'ona",
    "Jizzax", "Namangan", "Navoiy", "Qarshi",
    "Samarqand", "Guliston", "Termiz", "Nurafshon",
    "Urganch", "Nukus",
]


def get_weather(city: str) -> str:
    """Berilgan shahar uchun ob-havo ma'lumotini OpenWeatherMap orqali oladi."""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "uz",
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code != 200:
            return f"Kechirasiz, '{city}' uchun ma'lumot topilmadi."

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        return (
            f"🌤 <b>{city}</b> ob-havosi:\n\n"
            f"🌡 Harorat: {temp}°C (his qilinishi: {feels_like}°C)\n"
            f"☁️ Holat: {description}\n"
            f"💧 Namlik: {humidity}%\n"
            f"💨 Shamol: {wind_speed} m/s"
        )
    except Exception as e:
        logger.error(f"Ob-havo olishda xato: {e}")
        return "Kechirasiz, ob-havo ma'lumotini olishda xatolik yuz berdi."


def build_city_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    row = []
    for i, city in enumerate(UZBEK_CITIES, 1):
        row.append(InlineKeyboardButton(city, callback_data=f"city_{city}"))
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men 24/7 ishlaydigan avto-javob botman.\n\n"
        "Ob-havoni bilish uchun: 'ob-havo Toshkent' deb yozing 🌤\n"
        "Yoki shunchaki 'ob-havo' deb yozsangiz, shaharlar ro'yxati chiqadi."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lower_text = text.lower()

    if lower_text == "ob-havo" or lower_text == "ob havo":
        await update.message.reply_text(
            "Qaysi shahar uchun ob-havoni bilmoqchisiz?",
            reply_markup=build_city_keyboard(),
        )
        return

    if lower_text.startswith("ob-havo ") or lower_text.startswith("ob havo "):
        city = text.split(" ", 1)[1].strip()
        await update.message.reply_text("Qidiryapman... ⏳")
        weather_text = get_weather(city)
        await update.message.reply_text(weather_text, parse_mode="HTML")
        return

    await update.message.reply_text(
        "Kechirasiz, savolingizni tushunmadim. Boshqacha so'z bilan yozib ko'ring."
    )


async def city_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = query.data.replace("city_", "")
    weather_text = get_weather(city)
    await query.edit_message_text(text=weather_text, parse_mode="HTML")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(city_button_handler, pattern="^city_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
