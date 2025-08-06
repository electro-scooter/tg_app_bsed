from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import SUPPORTED_CITIES, WEATHER_MESSAGE_FORMAT
from utils.weather import get_weather, get_forecast, get_weather_emoji
from utils.action_logger import ActionLogger
from handlers.user_handler import get_user_data

action_logger = ActionLogger()

# Добавляем эмодзи для городов
CITY_EMOJIS = {
    'Сочи': '🌴',
    'Адлер': '✈️',
    'Лазаревское': '🏖',
    'Вардане': '🌊',
    'Лоо': '⛱',
    'Дагомыс': '🏊‍♂️',
    'Мацеста': '💆‍♂️',
    'Хоста': '🌺',
    'Кудепста': '🌅',
    'Красная Поляна': '🏔'
}

async def show_weather_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню выбора города для погоды"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🌴 Сочи", callback_data="city_Сочи")],
        [InlineKeyboardButton("💆‍♂️ Мацеста", callback_data="city_Мацеста")],
        [InlineKeyboardButton("🌺 Хоста", callback_data="city_Хоста")],
        [InlineKeyboardButton("🌅 Кудепста", callback_data="city_Кудепста")],
        [InlineKeyboardButton("✈️ Адлер", callback_data="city_Адлер")],
        [InlineKeyboardButton("🏔 Красная Поляна", callback_data="city_Красная Поляна")],
        [InlineKeyboardButton("🏊‍♂️ Дагомыс", callback_data="city_Дагомыс")],
        [InlineKeyboardButton("⛱ Лоо", callback_data="city_Лоо")],
        [InlineKeyboardButton("🌊 Вардане", callback_data="city_Вардане")],
        [InlineKeyboardButton("🏖 Лазаревское", callback_data="city_Лазаревское")],
        
        
        
        [InlineKeyboardButton("« Назад в меню", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "🌡 Выберите город для просмотра погоды:"
    
    if update.callback_query:
        await query.message.edit_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)

async def show_city_weather(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """Показывает погоду для выбранного города"""
    user_data = get_user_data(update.effective_user)
    weather_data = await get_weather(city)
    
    if "error" in weather_data:
        message = f"❌ {weather_data['error']}"
        status = "error"
    else:
        # Добавляем эмодзи погоды в данные
        weather_data['weather_emoji'] = get_weather_emoji(weather_data['description'])
        
        message = f"{CITY_EMOJIS[city]} Погода в городе {city}:\n" + WEATHER_MESSAGE_FORMAT.format(**weather_data)
        status = "success"
    
    action_logger.log_action(
        user_data=user_data,
        action="weather_request",
        action_type="api_request",
        action_data=f"city: {city}",
        status=status
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📅 Прогноз на неделю", callback_data=f"weekly_{city}")
        ],
        [InlineKeyboardButton("« Назад к городам", callback_data="weather")],
        [InlineKeyboardButton("« Назад в меню", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.edit_text(message, reply_markup=reply_markup)

async def show_forecast(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """Показывает прогноз погоды для выбранного города"""
    user_data = get_user_data(update.effective_user)
    forecast_data = await get_forecast(city)
    
    if "error" in forecast_data[0]:
        message = f"❌ {forecast_data[0]['error']}"
        status = "error"
    else:
        message = f"{CITY_EMOJIS[city]} Прогноз погоды в городе {city} на неделю:\n\n"
        
        for day in forecast_data:
            message += f"📅 {day['weekday']}, {day['date']}:\n"
            message += f"🌡 {day['temp_min']}°C ... {day['temp_max']}°C\n"
            message += f"{day['weather_emojis']} {', '.join(day['descriptions'])}\n\n"
        
        status = "success"
    
    action_logger.log_action(
        user_data=user_data,
        action="forecast_request",
        action_type="api_request",
        action_data=f"city: {city}",
        status=status
    )
    
    keyboard = [
        [InlineKeyboardButton("« К текущей погоде", callback_data=f"city_{city}")],
        [InlineKeyboardButton("« Назад к городам", callback_data="weather")],
        [InlineKeyboardButton("« Назад в меню", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.edit_text(message, reply_markup=reply_markup) 