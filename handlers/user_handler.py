from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from utils.user_data import UserDataManager
from utils.action_logger import ActionLogger

user_manager = UserDataManager()
action_logger = ActionLogger()

def get_user_data(user) -> dict:
    """Получение данных пользователя в виде словаря"""
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'language_code': user.language_code
    }

async def request_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос номера телефона у пользователя"""
    user_data = get_user_data(update.effective_user)
    action_logger.log_action(
        user_data=user_data,
        action="request_phone",
        action_type="button_click"
    )
    
    keyboard = [[KeyboardButton("📱 Поделиться номером телефона", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "Для получения дополнительных возможностей, пожалуйста, поделитесь своим номером телефона:",
        reply_markup=reply_markup
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка полученного контакта"""
    contact = update.message.contact
    user_id = update.effective_user.id
    user_data = get_user_data(update.effective_user)
    
    if contact.user_id == user_id:  # Проверяем, что контакт принадлежит пользователю
        user_manager.update_phone_number(user_id, contact.phone_number)
        action_logger.log_action(
            user_data=user_data,
            action="phone_shared",
            action_type="user_data",
            action_data=f"phone: {contact.phone_number}",
            status="success"
        )
        await update.message.reply_text(
            "Спасибо! Ваш номер телефона успешно сохранен.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        action_logger.log_action(
            user_data=user_data,
            action="phone_shared",
            action_type="user_data",
            action_data="invalid_phone_owner",
            status="error"
        )
        await update.message.reply_text(
            "К сожалению, мы можем принять только ваш собственный номер телефона.",
            reply_markup=ReplyKeyboardRemove()
        )

def log_user_activity(update: Update, action: str):
    """Логирование активности пользователя"""
    user_data = get_user_data(update.effective_user)
    
    # Обновляем информацию о пользователе
    user_manager.update_user(user_data, action)
    
    # Логируем действие
    action_type = "command" if action.startswith("/") else "button_click"
    action_logger.log_action(
        user_data=user_data,
        action=action,
        action_type=action_type
    ) 