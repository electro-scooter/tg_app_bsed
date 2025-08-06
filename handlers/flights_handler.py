from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from handlers.user_handler import log_user_activity

logger = logging.getLogger(__name__)

async def show_flights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает информацию об авиабилетах"""
    query = update.callback_query
    await query.answer()
    
    # Логируем действие
    log_user_activity(update, "открыл раздел авиабилетов")
    
    message = """
✈️ Авиабилеты на Черноморское побережье!

Найдите самые выгодные предложения на авиабилеты с помощью Aviasales:

🎯 Поиск по всем авиакомпаниям
💰 Лучшие цены на рынке
🔔 Уведомления о снижении цен
🎫 Бронирование онлайн
💳 Безопасная оплата
🌍 Поиск по всему миру

Нажмите кнопку ниже, чтобы найти самые выгодные предложения по авиабилетам:
"""
    
    keyboard = [
        [InlineKeyboardButton("✈️ Найти авиабилеты", url="https://aviasales.tp.st/WFskNTRl")],
        [InlineKeyboardButton("« Назад в меню", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(message, reply_markup=reply_markup) 