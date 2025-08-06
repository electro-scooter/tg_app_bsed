import os
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.action_logger import ActionLogger
from handlers.user_handler import get_user_data, log_user_activity
import logging

logger = logging.getLogger(__name__)

action_logger = ActionLogger()

def load_excursions():
    """Загрузка данных об экскурсиях из Excel файла"""
    file_path = 'data/price.xls'
    
    # Проверяем существование файла
    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        return None
        
    print(f"Файл найден: {file_path}")
    
    try:
        # Загружаем файл как xls
        df = pd.read_excel(file_path, sheet_name='Sheet1', engine='xlrd')
        print("Успешно загружен файл")
    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")
        return None
    
    # Проверяем наличие необходимых колонок
    required_columns = ['Категория', 'Название', 'Идентификатор', 'Описание', 'Цена', 'Фото', 'Популярный товар', 'В наличии']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Отсутствуют колонки: {missing_columns}")
        return None
    
    # Выводим информацию о загруженных данных
    print(f"Загружено {len(df)} экскурсий")
    print(f"Категории: {df['Категория'].unique().tolist()}")
    
    return df

def get_categories():
    """Получение списка уникальных категорий экскурсий"""
    df = load_excursions()
    if df is not None:
        # Получаем уникальные категории и сортируем их
        categories = sorted(df['Категория'].unique().tolist())
        print(f"Найдены категории: {categories}")
        return categories
    print("Не удалось получить категории")
    return []

# Получение экскурсий по категории
def get_excursions_by_category(category):
    """Получение списка экскурсий определенной категории"""
    df = load_excursions()
    if df is not None:
        return df[df['Категория'] == category].to_dict('records')
    return []

def get_excursion_by_id(excursion_id: str) -> dict:
    """Получает информацию об экскурсии по её идентификатору"""
    print(f"Поиск экскурсии с ID: {excursion_id}")
    
    df = load_excursions()
    if df is None:
        print("Не удалось загрузить данные об экскурсиях")
        return None
    
    # Преобразуем excursion_id в строку для сравнения
    excursion_id = str(excursion_id)
    print(f"Преобразованный ID для поиска: {excursion_id}")
    
    # Выводим все доступные ID для проверки
    print(f"Доступные ID в базе: {df['Идентификатор'].tolist()}")
    
    # Ищем экскурсию по идентификатору
    excursion = df[df['Идентификатор'].astype(str) == excursion_id]
    
    if excursion.empty:
        print(f"Экскурсия с ID {excursion_id} не найдена")
        return None
    
    print(f"Найдена экскурсия: {excursion.iloc[0]['Название']}")
    return excursion.iloc[0].to_dict()

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список категорий экскурсий"""
    user_data = get_user_data(update.effective_user)
    categories = get_categories()
    
    if not categories:
        await update.callback_query.message.edit_text(
            "❌ В данный момент информация об экскурсиях недоступна.\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Назад в меню", callback_data="main_menu")
            ]])
        )
        return
    
    action_logger.log_action(
        user_data=user_data,
        action="excursions_menu",
        action_type="menu_view"
    )
    
    keyboard = []
    for category in categories:
        keyboard.append([InlineKeyboardButton(f"🌴 {category}", callback_data=f"category_{category}")])
    
    keyboard.append([InlineKeyboardButton("« Назад в меню", callback_data="start")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "🌴 Выберите категорию экскурсий:"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)

async def show_excursions_list(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    """Показывает список экскурсий в выбранной категории"""
    query = update.callback_query
    await query.answer()
    
    # Логируем действие пользователя
    log_user_activity(update, f"открыл список экскурсий в категории {category}")
    
    excursions = get_excursions_by_category(category)
    if not excursions:
        await query.message.edit_text(
            "❌ В данной категории пока нет доступных экскурсий.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Назад к категориям", callback_data="excursions"),
                InlineKeyboardButton("🏠 В главное меню", callback_data="start")
            ]])
        )
        return
    
    message = f"🌴 Экскурсии в категории {category}:\n\n"
    for excursion in excursions:
        message += f"• {excursion['Название']}\n"
    
    # Создаем клавиатуру с кнопками навигации
    keyboard = []
    for excursion in excursions:
        keyboard.append([InlineKeyboardButton(
            f"🏔 {excursion['Название']}", 
            callback_data=f"excursion_{excursion['Идентификатор']}"
        )])
    
    # Добавляем кнопки навигации внизу
    keyboard.append([
        InlineKeyboardButton("« Назад к категориям", callback_data="excursions"),
        InlineKeyboardButton("🏠 В главное меню", callback_data="start")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.message.edit_text(message, reply_markup=reply_markup)
    except Exception as e:
        print(f"Ошибка при редактировании сообщения: {e}")
        # Если не удалось отредактировать, отправляем новое сообщение
        await query.message.reply_text(message, reply_markup=reply_markup)

async def show_excursion_info(update: Update, context: ContextTypes.DEFAULT_TYPE, excursion_id: str):
    """Показывает детальную информацию об экскурсии"""
    query = update.callback_query
    await query.answer()
    
    # Получаем данные об экскурсии
    excursion = get_excursion_by_id(excursion_id)
    
    if not excursion:
        # Логируем ошибку
        log_user_activity(update, f"попытался открыть несуществующую экскурсию с ID {excursion_id}")
        
        await query.message.edit_text(
            "❌ К сожалению, информация об этой экскурсии недоступна.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Назад к категориям", callback_data="excursions"),
                InlineKeyboardButton("🏠 В главное меню", callback_data="start")
            ]])
        )
        return
    
    # Логируем успешное открытие экскурсии
    log_user_activity(update, f"открыл информацию об экскурсии {excursion['Название']}")
    
    # Формируем сообщение
    message = f"🏔 {excursion['Название']}\n\n"
    message += f"📝 {excursion['Описание']}\n\n"
    message += f"💰 Цена: {excursion['Цена']} ₽\n"
    
    if excursion['Популярный товар'] == 'Да':
        message += "⭐️ Популярная экскурсия!\n"
    
    if excursion['В наличии'] == 'Да':
        message += "✅ Доступна для бронирования\n"
    else:
        message += "❌ Временно недоступна\n"
    
    # Создаем клавиатуру с кнопками навигации
    keyboard = [
        [InlineKeyboardButton("« Назад к списку", callback_data=f"category_{excursion['Категория']}")],
        [
            InlineKeyboardButton("« Назад к категориям", callback_data="excursions"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="start")
        ]
    ]
    
    # Если есть фото, отправляем его с описанием
    if excursion['Фото'] and not pd.isna(excursion['Фото']):
        try:
            # Отправляем фото с описанием и кнопками
            await query.message.reply_photo(
                photo=excursion['Фото'],
                caption=message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            # Удаляем предыдущее сообщение со списком экскурсий
            await query.message.delete()
        except Exception as e:
            print(f"Ошибка при отправке фото: {e}")
            await query.message.edit_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        await query.message.edit_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )