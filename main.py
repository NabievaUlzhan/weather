import asyncio
import logging
import requests
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties

from datetime import datetime

# API from .env 
load_dotenv()
API_KEY = os.getenv('API_KEY')
TOKEN = os.getenv('BOT_TOKEN')

# init bot and dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# user settings
user_preferences = {}

# lists
CITIES = sorted(["Almaty", "Astana", "New York", "London", "Moscow", "Berlin", "Tokyo", "Paris"])

LANGS = {
    "en": ["City", "Weather", "Temperature", "Feels like", "Min", "Max", "Humidity", "Wind Speed", "Sunrise", "Sunset"],
    "ru": ["Город", "Погода", "Температура", "Ощущается как", "Мин", "Макс", "Влажность", "Скорость ветра", "Рассвет", "Закат"],
    "kr": ["도시", "날씨", "온도", "체감 온도", "최저", "최고", "습도", "풍속", "일출", "일몰"]
}

# city search
class CitySearch(StatesGroup):
    waiting_for_city = State()

def format_dt(dt):
    dt_object = datetime.utcfromtimestamp(dt)
    formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time

# get weather data
def get_weather(city: str, unit: str, lang: str):

    unit_mapping = {
        "Celsius": "metric", 
        "Fahrenheit": "imperial", 
        "Kelvin": "standard"
    }

    units_param = unit_mapping.get(unit, "metric")

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&lang={lang}&units={units_param}&appid={API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        weather_desc = data['weather'][0]['description'].title()
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        temp_min = data['main']['temp_min']
        temp_max = data['main']['temp_max']
        sunrise = data['sys']['sunrise']
        sunset = data['sys']['sunset']
        city_name = data['name']

        formatted_sunrise = format_dt(sunrise)
        formatted_sunset = format_dt(sunset)

        return (f"🌍 <b>{LANGS[lang][0]}:</b> {city_name}\n"
                f"🌤 <b>{LANGS[lang][1]}:</b> {weather_desc}\n"
                f"🌡 <b>{LANGS[lang][2]}:</b> {temp}° ({unit}) ({LANGS[lang][3]} {feels_like}°)\n"
                f"🌡 <b>{LANGS[lang][4]}:</b> {temp_min}° ({unit}) | <b>{LANGS[lang][5]}:</b> {temp_max}° ({unit})\n"
                f"💧 <b>{LANGS[lang][6]}:</b> {humidity}%\n"
                f"💨 <b>{LANGS[lang][7]}:</b> {wind_speed} m/s\n"
                f"🌅 <b>{LANGS[lang][8]}:</b> {formatted_sunrise} \n"
                f"🌄 <b>{LANGS[lang][9]}:</b> {formatted_sunset}\n"
            )

    else:
        return "⚠️ City not found! Please check the name and try again."

# reminder
async def send_daily_weather():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)

        if now >= target_time: 
            target_time = target_time.replace(day=now.day + 1)

        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)

        for user_id, prefs in user_preferences.items():
            city = prefs.get("city", "Almaty")
            lang = prefs.get("language", "en")
            temp_unit = prefs.get("temp_unit", "Celsius")
            
            weather_info = get_weather(city, temp_unit, lang)
            await bot.send_message(user_id, f"☀️ Your daily weather update:\n\n{weather_info}")

# start reminder
async def start_reminder():
    asyncio.create_task(send_daily_weather())

# main menu
def main_menu():

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Choose City", callback_data="choose_city")],
        [InlineKeyboardButton(text="🌐 Data Language", callback_data="choose_language")],
        [InlineKeyboardButton(text="🌡 Temperature Unit", callback_data="choose_temp")]
    ])

# back button
def back_button():

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="back_main")]
    ])

# start
@dp.message(Command("start"))
async def start(message: Message):

    user_preferences[message.from_user.id] = {
        "language": "en", 
        "temp_unit": "Celsius"
    }
    await message.answer("🌤 Hello! Choose an option:", reply_markup=main_menu())

# main
@dp.callback_query(lambda c: c.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("🌤 Main Menu:", reply_markup=main_menu())

# cities menu
@dp.callback_query(lambda c: c.data == "choose_city")
async def choose_city(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=city, callback_data=f"city_{city}")] for city in CITIES
    ])

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔍 Search City", callback_data="search_city")])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")])

    await callback.message.edit_text("🌍 Choose a city or search:", reply_markup=keyboard)

# select city
@dp.callback_query(lambda c: c.data.startswith("city_"))
async def city_selected(callback: CallbackQuery):
    city = callback.data.split("_")[1]
    user_id = callback.from_user.id
    temp_unit = user_preferences.get(user_id, {}).get("temp_unit", "Celsius")
    lang = user_preferences.get(user_id, {}).get("language", "en")

    weather_info = get_weather(city, temp_unit, lang)

    await callback.message.answer(weather_info)

# search city
@dp.callback_query(lambda c: c.data == "search_city")
async def search_city(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CitySearch.waiting_for_city)
    await callback.message.answer("🔍 Enter the city name:", reply_markup=back_button())

# city search input
@dp.message(CitySearch.waiting_for_city)
async def receive_city_name(message: Message, state: FSMContext):
    city = message.text.strip()
    user_id = message.from_user.id
    temp_unit = user_preferences.get(user_id, {}).get("temp_unit", "Celsius")
    lang = user_preferences.get(user_id, {}).get("language", "en")

    weather_info = get_weather(city, temp_unit, lang)
    await message.answer(weather_info)
    await state.clear()

# langs menu
@dp.callback_query(lambda c: c.data == "choose_language")
async def choose_language(callback: CallbackQuery):

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English", callback_data="lang_en")],
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="한국어", callback_data="lang_kr")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])

    await callback.message.edit_text("🌐 Change language:", reply_markup=keyboard)

# select lang
@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery):

    lang = callback.data.split("_")[1]
    user_preferences[callback.from_user.id]["language"] = lang

    await callback.message.answer(f"✅ Language set to {lang}!", reply_markup=back_button())

# temp menu
@dp.callback_query(lambda c: c.data == "choose_temp")
async def choose_temperature_unit(callback: CallbackQuery):

    keyboard = InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text="🌡 Celsius (°C)", callback_data="temp_Celsius")],
        [InlineKeyboardButton(text="🌡 Fahrenheit (°F)", callback_data="temp_Fahrenheit")],
        [InlineKeyboardButton(text="🌡 Kelvin (K)", callback_data="temp_Kelvin")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
    ])

    await callback.message.edit_text("🌡 Choose a temperature unit:", reply_markup=keyboard)

# select temp
@dp.callback_query(lambda c: c.data.startswith("temp_"))
async def temperature_unit_selected(callback: CallbackQuery):
    
    temp_unit = callback.data.split("_")[1]
    user_preferences[callback.from_user.id]["temp_unit"] = temp_unit
    await callback.message.answer(f"✅ Temperature unit set to {temp_unit}!", reply_markup=back_button())

# run
async def main():
    logging.basicConfig(level=logging.INFO)
    await start_reminder() 
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
