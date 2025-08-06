import csv
import os
from datetime import datetime
import pytz
from config import TIMEZONE

class ActionLogger:
    def __init__(self, csv_file='data/actions_log.csv'):
        self.csv_file = csv_file
        self.ensure_data_dir()
        self.ensure_csv_exists()

    def ensure_data_dir(self):
        """Создание директории для данных, если она не существует"""
        os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)

    def ensure_csv_exists(self):
        """Создание CSV файла с заголовками, если он не существует"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'Дата и время',
                    'ID пользователя',
                    'Имя пользователя',
                    'Имя',
                    'Фамилия',
                    'Действие',
                    'Тип действия',
                    'Дополнительные данные',
                    'Статус'
                ])

    def get_current_time(self):
        """Получение текущего времени в нужном формате"""
        return datetime.now(pytz.timezone(TIMEZONE)).strftime('%d.%m.%Y %H:%M:%S')

    def get_action_description(self, action: str, action_type: str = None) -> str:
        """Получение человекочитаемого описания действия"""
        # Словарь с описаниями типов действий
        action_type_descriptions = {
            'command': 'Команда',
            'button_click': 'Нажатие кнопки',
            'api_request': 'API запрос',
            'menu_view': 'Просмотр меню',
            'user_data': 'Данные пользователя'
        }
        
        # Словарь с описаниями действий
        action_descriptions = {
            'weather_menu': 'Открытие меню погоды',
            'weather_request': 'Запрос погоды',
            'forecast_request': 'Запрос прогноза погоды',
            'phone_shared': 'Отправка номера телефона',
            'request_phone': 'Запрос номера телефона',
            'main_menu': 'Возврат в главное меню'
        }
        
        action_desc = action_descriptions.get(action, action)
        type_desc = action_type_descriptions.get(action_type, action_type) if action_type else ''
        
        return f"{type_desc}: {action_desc}" if type_desc else action_desc

    def get_status_description(self, status: str) -> str:
        """Получение человекочитаемого описания статуса"""
        status_descriptions = {
            'success': 'Успешно',
            'error': 'Ошибка',
            'pending': 'В процессе',
            'cancelled': 'Отменено'
        }
        return status_descriptions.get(status, status)

    def log_action(self, user_data: dict, action: str, action_type: str = None, action_data: str = None, status: str = "success"):
        """
        Логирование действия пользователя
        
        :param user_data: Словарь с данными пользователя
        :param action: Действие пользователя
        :param action_type: Тип действия
        :param action_data: Дополнительные данные о действии
        :param status: Статус выполнения действия
        """
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                self.get_current_time(),
                user_data.get('id', ''),
                user_data.get('username', ''),
                user_data.get('first_name', ''),
                user_data.get('last_name', ''),
                self.get_action_description(action, action_type),
                action_type or '',
                action_data or '',
                self.get_status_description(status)
            ])

    def get_user_actions(self, user_id: int) -> list:
        """Получение всех действий конкретного пользователя"""
        actions = []
        with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if str(row['ID пользователя']) == str(user_id):
                    actions.append(row)
        return actions

    def get_action_statistics(self, action_type: str = None) -> dict:
        """
        Получение статистики по действиям
        
        :param action_type: Тип действия для фильтрации (опционально)
        :return: Словарь со статистикой
        """
        stats = {
            'всего_действий': 0,
            'уникальных_пользователей': set(),
            'действия_по_типу': {},
            'процент_успешных': 0,
            'ошибок': 0
        }
        
        with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if action_type and row['Тип действия'] != action_type:
                    continue
                    
                stats['всего_действий'] += 1
                stats['уникальных_пользователей'].add(row['ID пользователя'])
                
                # Подсчет действий по типу
                action_type_key = row['Тип действия'] or 'неизвестно'
                stats['действия_по_типу'][action_type_key] = stats['действия_по_типу'].get(action_type_key, 0) + 1
                
                # Подсчет ошибок
                if row['Статус'] != 'Успешно':
                    stats['ошибок'] += 1
        
        # Расчет процента успешных действий
        if stats['всего_действий'] > 0:
            stats['процент_успешных'] = ((stats['всего_действий'] - stats['ошибок']) / stats['всего_действий']) * 100
        
        # Преобразуем set в количество уникальных пользователей
        stats['уникальных_пользователей'] = len(stats['уникальных_пользователей'])
        
        return stats 