from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from handlers.user_handler import log_user_activity

logger = logging.getLogger(__name__)

async def show_accommodation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает информацию о жилье"""
    query = update.callback_query
    await query.answer()
    
    # Логируем действие
    log_user_activity(update, "открыл раздел жилья")
    
    message = """
🏨 Жильё на Черноморском побережье!

Найдите идеальное жильё для отдыха с помощью Суточно.ру:

🏠 Квартиры и дома
🏖 Апартаменты у моря
🌅 Виды на море
🎯 В центре города
💰 Лучшие цены
🔒 Безопасное бронирование
👥 Отзывы от гостей

Нажмите кнопку ниже, чтобы найти лучшие предложения по аренде:
"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Перейти на сайт", url="https://sutochno.tp.st/zntj72if")],
        [InlineKeyboardButton("« Назад в меню", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(message, reply_markup=reply_markup) 