import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN, TELEGRAM_GROUP_LINK
from handlers.weather_handler import show_weather_menu, show_city_weather, show_forecast
from handlers.user_handler import request_phone_number, handle_contact, log_user_activity
from handlers.excursions_handler import show_categories, show_excursions_list, show_excursion_info, get_categories
from handlers.accommodation_handler import show_accommodation
from handlers.flights_handler import show_flights

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_main_menu():
    """Функция для генерации главного меню"""
    keyboard = [
        [
            InlineKeyboardButton("😎 Погода", callback_data="weather")
        ],
        [
            InlineKeyboardButton("🌴 Мои экскурсии", callback_data="excursions")
        ],
        [
            InlineKeyboardButton("🏖 Жильё", callback_data="accommodation"),
            InlineKeyboardButton("✈️ Авиабилеты", callback_data="flights")
        ],
        [
            InlineKeyboardButton("🎨 Получить фирменные стикеры", callback_data="stickers")
        ],
        [
            InlineKeyboardButton("🌊 Телеграм группа", url=TELEGRAM_GROUP_LINK)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_welcome_message():
    """Функция для генерации приветственного сообщения"""
    return """
👋 Привет! Я ваш помощник по отдыху на Черноморском побережье!

Что я могу:
🌡 Показать погоду в разных городах
🎫 Помочь с выбором экскурсий
🏨 Найти жильё
✈️ Подобрать авиабилеты

Выберите интересующий вас раздел:
"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"Пользователь {user.full_name} (id: {user.id}) запустил бота")
    
    # Логируем активность пользователя
    log_user_activity(update, "Запуск бота")
    
    welcome_message = get_welcome_message()
    
    # Проверяем тип обновления
    if update.callback_query:
        await update.callback_query.message.edit_text(welcome_message, reply_markup=get_main_menu())
    else:
        await update.message.reply_text(welcome_message, reply_markup=get_main_menu())

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /menu"""
    user = update.effective_user
    logger.info(f"Пользователь {user.full_name} (id: {user.id}) открыл главное меню")
    
    # Логируем активность пользователя
    log_user_activity(update, "Открытие главного меню")
    
    # Перенаправляем на функцию start для показа главного меню
    await start_command(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    data = query.data
    
    # Логируем нажатие кнопки
    user = query.from_user
    button_name = data.replace('_', ' ').title()
    logger.info(f"Пользователь {user.full_name} (id: {user.id}) нажал кнопку {button_name}")
    
    # Логируем действие в CSV
    log_user_activity(update, f"нажал кнопку {button_name}")
    
    try:
        if data == "start":
            # Проверяем, есть ли у сообщения фото
            if query.message.photo:
                # Если есть фото, отправляем новое сообщение с главным меню
                await query.message.reply_text(
                    get_welcome_message(),
                    reply_markup=get_main_menu()
                )
            else:
                # Если нет фото, редактируем сообщение
                await start_command(update, context)
        elif data == "stickers":
            message = "🎨 Наконец-то у нас появились фирменные стикеры!\n\n"
            message += "Нажмите кнопку ниже, чтобы добавить стикеры в свой Telegram:"
            
            keyboard = [
                [InlineKeyboardButton("🎨 Добавить стикеры", url="https://t.me/addstickers/blacksea365")],
                [InlineKeyboardButton("« Назад в меню", callback_data="start")]
            ]
            await query.message.edit_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        elif data == "excursions":
            # Проверяем, есть ли у сообщения фото
            if query.message.photo:
                # Если есть фото, отправляем новое сообщение со списком категорий
                categories = get_categories()
                keyboard = []
                for category in categories:
                    keyboard.append([InlineKeyboardButton(f"🌴 {category}", callback_data=f"category_{category}")])
                keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="start")])
                
                await query.message.reply_text(
                    "🌴 Выберите категорию экскурсий:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                # Если нет фото, редактируем сообщение
                await show_categories(update, context)
        elif data == "weather":
            await show_weather_menu(update, context)
        elif data == "accommodation":
            await show_accommodation(update, context)
        elif data == "flights":
            await show_flights(update, context)
        elif data.startswith("category_"):
            category = data.replace("category_", "")
            await show_excursions_list(update, context, category)
        elif data.startswith("excursion_"):
            excursion_id = data.replace("excursion_", "")
            await show_excursion_info(update, context, excursion_id)
        elif data.startswith("city_"):
            city = data.replace("city_", "")
            await show_city_weather(update, context, city)
        elif data.startswith("weekly_"):
            city = data.replace("weekly_", "")
            await show_forecast(update, context, city)
        elif data == "back_to_cities":
            await show_weather_menu(update, context)
        elif data == "back_to_current":
            city = context.user_data.get('current_city')
            if city:
                await show_city_weather(update, context, city)
    except Exception as e:
        logger.error(f"Ошибка при обработке кнопки {data}: {e}")
        # В случае ошибки отправляем новое сообщение
        await query.message.reply_text(
            "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Главное меню", callback_data="start")
            ]])
        )

def main():
    """Основная функция запуска бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 