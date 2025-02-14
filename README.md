# weather
Telegram Weather Bot

This is a Telegram bot built using Aiogram that provides weather updates based on the selected city. Users can set their preferred city, language, and temperature unit, and receive daily weather updates at 8:00 AM.

1. Features:

- Get weather updates for any selected city
- Supports multiple languages (English, Russian, Kazakh)
- Choose temperature unit (Celsius, Fahrenheit, Kelvin)
- Daily weather reminders at 10:00 AM
- Interactive menu for easy setup

2. Setup Instructions

1️⃣ Prerequisites
Make sure you have the following installed:
Python 3.8+
A Telegram bot token (get it from BotFather)
An API key from OpenWeather

2️⃣ Clone the Repository
git clone https://github.com/yourusername/telegram-weather-bot.git
cd telegram-weather-bot

3️⃣ Install Dependencies
pip install aiogram python-dotenv requests

4️⃣ Create a .env File
Create a .env file in the project root and add:

BOT_TOKEN=your_telegram_bot_token
API_KEY=your_openweather_api_key

5️⃣ Run the Bot
python bot.py

3. Bot Commands

/start: Start the bot and open the main menu
"Choose city": View and select a city, if there is not your city write it by clicking "Search City"
"Data language": Choose 1 language: English, Russian, Korean
"Temperate Unit": Choose 1 unit: Celsius, Fahrenheit, Kelvin
"Back": to get back

4. Reminder

The bot sends a weather update every day at 8:00 AM based on the user’s selected city, language, and temperature unit.

5. Built With

Python 3, Aiogram (Telegram bot framework), Asyncio (For scheduling daily updates), OpenWeather API (For fetching weather data)

6. License

This project is licensed under the MIT License.



Happy coding!
