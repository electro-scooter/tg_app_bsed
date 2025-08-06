import asyncio
import aiohttp
from datetime import datetime
import pytz
from config import WEATHER_API_KEY, SUPPORTED_CITIES, TIMEZONE

async def check_city_visibility(city: str, session: aiohttp.ClientSession) -> dict:
    """Проверка видимости для конкретного города"""
    try:
        # Получаем координаты города
        geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},RU&limit=1&appid={WEATHER_API_KEY}"
        async with session.get(geocoding_url) as response:
            location_data = await response.json()
            if not location_data:
                return {"city": city, "error": "Город не найден"}
            
            lat = location_data[0]["lat"]
            lon = location_data[0]["lon"]
        
        # Получаем данные о погоде
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        async with session.get(weather_url) as response:
            weather_data = await response.json()
            
            # Получаем текущее время
            tz = pytz.timezone(TIMEZONE)
            current_time = datetime.now(tz).strftime("%H:%M:%S")
            
            result = {
                "city": city,
                "time": current_time,
                "visibility": weather_data.get("visibility", None),
                "visibility_km": round(weather_data.get("visibility", 0) / 1000, 1) if "visibility" in weather_data else None,
                "weather": weather_data["weather"][0]["description"],
                "temp": round(weather_data["main"]["temp"]),
                "humidity": weather_data["main"]["humidity"]
            }
            
            return result
            
    except Exception as e:
        return {"city": city, "error": f"Ошибка: {str(e)}"}

async def check_all_cities():
    """Проверка видимости во всех городах"""
    async with aiohttp.ClientSession() as session:
        tasks = [check_city_visibility(city, session) for city in SUPPORTED_CITIES]
        results = await asyncio.gather(*tasks)
        
        # Выводим результаты
        print("\n=== Проверка видимости во всех городах ===")
        print(f"Время проверки: {datetime.now(pytz.timezone(TIMEZONE)).strftime('%d.%m.%Y %H:%M:%S')}\n")
        
        for result in results:
            if "error" in result:
                print(f"❌ {result['city']}: {result['error']}")
            else:
                visibility_status = "✅" if result["visibility"] is not None else "❌"
                print(f"{visibility_status} {result['city']}:")
                print(f"   Время: {result['time']}")
                print(f"   Погода: {result['weather']}")
                print(f"   Температура: {result['temp']}°C")
                print(f"   Влажность: {result['humidity']}%")
                if result["visibility"] is not None:
                    print(f"   Видимость: {result['visibility']} м ({result['visibility_km']} км)")
                else:
                    print("   Видимость: Нет данных")
                print()

if __name__ == "__main__":
    asyncio.run(check_all_cities()) 