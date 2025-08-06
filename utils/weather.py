import aiohttp
from datetime import datetime, timedelta
import pytz
from config import WEATHER_API_KEY, TIMEZONE

# Добавляем словарь с эмодзи для разных погодных условий
WEATHER_EMOJIS = {
    'ясно': '☀️',
    'облачно с прояснениями': '🌤',
    'переменная облачность': '⛅️',
    'небольшая облачность': '🌤',
    'облачно': '☁️',
    'пасмурно': '🌥',
    'небольшой дождь': '🌦',
    'дождь': '🌧',
    'сильный дождь': '⛈',
    'гроза': '🌩',
    'снег': '🌨',
    'туман': '🌫',
    'default': '🌡'
}

def get_weather_emoji(description: str) -> str:
    """Получение эмодзи для описания погоды"""
    for key, emoji in WEATHER_EMOJIS.items():
        if key in description.lower():
            return emoji
    return WEATHER_EMOJIS['default']

async def get_weather(city: str) -> dict:
    """Получение текущей погоды для города"""
    async with aiohttp.ClientSession() as session:
        try:
            # Специальная обработка для Красной Поляны
            if city == "Красная Поляна":
                weather_url = f"https://api.openweathermap.org/data/2.5/weather?id=542681&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            else:
                # Получаем координаты города
                geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},RU&limit=1&appid={WEATHER_API_KEY}"
                async with session.get(geocoding_url) as response:
                    location_data = await response.json()
                    if not location_data:
                        return {"error": "Город не найден"}
                    
                    lat = location_data[0]["lat"]
                    lon = location_data[0]["lon"]
                
                weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            
            async with session.get(weather_url) as response:
                weather_data = await response.json()
                
                # Конвертируем время восхода и заката
                tz = pytz.timezone(TIMEZONE)
                sunrise = datetime.fromtimestamp(weather_data["sys"]["sunrise"]).astimezone(tz).strftime("%H:%M")
                sunset = datetime.fromtimestamp(weather_data["sys"]["sunset"]).astimezone(tz).strftime("%H:%M")
                
                weather_info = {
                    "temp": round(weather_data["main"]["temp"]),
                    "feels_like": round(weather_data["main"]["feels_like"]),
                    "humidity": weather_data["main"]["humidity"],
                    "pressure": round(weather_data["main"]["pressure"] * 0.750062),  # Конвертация из гПа в мм рт.ст.
                    "wind_speed": round(weather_data["wind"]["speed"]),
                    "wind_direction": get_wind_direction(weather_data["wind"]["deg"]),
                    "clouds": weather_data["clouds"]["all"],
                    "description": weather_data["weather"][0]["description"],
                    "sunrise": sunrise,
                    "sunset": sunset
                }
                
                # Добавляем visibility только если оно есть в ответе
                if "visibility" in weather_data:
                    weather_info["visibility"] = round(weather_data["visibility"] / 1000, 1)
                    weather_info["visibility_info"] = f"\n👁 Видимость: {weather_info['visibility']} км"
                else:
                    weather_info["visibility"] = None
                    weather_info["visibility_info"] = "\n👁 Видимость: нет данных"
                
                return weather_info
                
        except Exception as e:
            return {"error": f"Ошибка при получении погоды: {str(e)}"}

def get_wind_direction(degrees: float) -> str:
    """Конвертация градусов в текстовое направление ветра"""
    directions = [
        "северный", "северо-восточный", "восточный", "юго-восточный",
        "южный", "юго-западный", "западный", "северо-западный"
    ]
    index = round(degrees / 45) % 8
    return directions[index]

async def get_forecast(city: str, days: int = 7) -> list:
    """Получение прогноза погоды на неделю"""
    async with aiohttp.ClientSession() as session:
        try:
            # Специальная обработка для Красной Поляны
            if city == "Красная Поляна":
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?id=542681&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            else:
                # Получаем координаты города
                geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},RU&limit=1&appid={WEATHER_API_KEY}"
                async with session.get(geocoding_url) as response:
                    location_data = await response.json()
                    if not location_data:
                        return [{"error": "Город не найден"}]
                    
                    lat = location_data[0]["lat"]
                    lon = location_data[0]["lon"]
                
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            
            async with session.get(forecast_url) as response:
                forecast_data = await response.json()
                
                if "error" in forecast_data:
                    return [{"error": forecast_data["error"]}]
                
                # Группируем прогноз по дням
                daily_forecast = {}
                tz = pytz.timezone(TIMEZONE)
                
                for item in forecast_data["list"]:
                    date = datetime.fromtimestamp(item["dt"]).astimezone(tz)
                    date_key = date.strftime("%Y-%m-%d")
                    
                    if date_key not in daily_forecast:
                        daily_forecast[date_key] = {
                            "date": date.strftime("%d.%m.%Y"),
                            "weekday": date.strftime("%A"),
                            "temp_min": float('inf'),
                            "temp_max": float('-inf'),
                            "descriptions": set(),
                            "emojis": set()
                        }
                    
                    temp = round(item["main"]["temp"])
                    daily_forecast[date_key]["temp_min"] = min(daily_forecast[date_key]["temp_min"], temp)
                    daily_forecast[date_key]["temp_max"] = max(daily_forecast[date_key]["temp_max"], temp)
                    daily_forecast[date_key]["descriptions"].add(item["weather"][0]["description"])
                    daily_forecast[date_key]["emojis"].add(get_weather_emoji(item["weather"][0]["description"]))
                
                # Преобразуем в список и сортируем по дате
                forecast = []
                for date_key in sorted(daily_forecast.keys())[:days]:
                    day_data = daily_forecast[date_key]
                    # Конвертируем weekday в русский язык
                    weekday_ru = {
                        'Monday': 'Понедельник',
                        'Tuesday': 'Вторник',
                        'Wednesday': 'Среда',
                        'Thursday': 'Четверг',
                        'Friday': 'Пятница',
                        'Saturday': 'Суббота',
                        'Sunday': 'Воскресенье'
                    }[day_data["weekday"]]
                    
                    forecast.append({
                        "date": day_data["date"],
                        "weekday": weekday_ru,
                        "temp_min": round(day_data["temp_min"]),
                        "temp_max": round(day_data["temp_max"]),
                        "descriptions": list(day_data["descriptions"]),
                        "weather_emojis": " ".join(day_data["emojis"])
                    })
                
                return forecast
        except Exception as e:
            return [{"error": f"Ошибка при получении прогноза: {str(e)}"}] 