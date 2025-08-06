import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Токены и ключи API
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
AVIASALES_API_KEY = os.getenv('AVIASALES_API_KEY')

# Настройки временной зоны
TIMEZONE = 'Europe/Moscow'  # UTC+3

# Поддерживаемые города
SUPPORTED_CITIES = [
    'Лазаревское',
    'Вардане',
    'Лоо',
    'Дагомыс',
    'Сочи',
    'Мацеста',
    'Хоста',
    'Кудепста',
    'Адлер',
    'Красная Поляна'
]

# Ссылки
TELEGRAM_GROUP_LINK = 'https://t.me/blackseaeveryday'

# Настройки погодного API
WEATHER_UPDATE_INTERVAL = 1800  # 30 минут
FORECAST_DAYS = 7

# Форматы сообщений
WEATHER_MESSAGE_FORMAT = """
{weather_emoji} {description}

🌡 Температура: {temp}°C
🌡 Ощущается как: {feels_like}°C
💧 Влажность: {humidity}%
🌪 Ветер: {wind_speed} м/с, {wind_direction}
🌫 Давление: {pressure} мм рт.ст.
☁️ Облачность: {clouds}%
🌅 Восход: {sunrise}
🌇 Закат: {sunset}{visibility_info}
""" 