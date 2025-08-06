import csv
import os
from datetime import datetime
import pytz
from config import TIMEZONE

class UserDataManager:
    def __init__(self, csv_file='data/users.csv'):
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
                    'user_id',
                    'username',
                    'first_name',
                    'last_name',
                    'phone_number',
                    'language_code',
                    'last_activity',
                    'last_command',
                    'registration_date'
                ])

    def get_current_time(self):
        """Получение текущего времени в нужном формате"""
        return datetime.now(pytz.timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')

    def update_user(self, user_data: dict, command: str = None):
        """Обновление или добавление информации о пользователе"""
        current_time = self.get_current_time()
        users = self.read_users()
        
        user_entry = {
            'user_id': user_data.get('id'),
            'username': user_data.get('username', ''),
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'phone_number': user_data.get('phone_number', ''),
            'language_code': user_data.get('language_code', ''),
            'last_activity': current_time,
            'last_command': command or '',
            'registration_date': current_time
        }

        # Проверяем, существует ли пользователь
        user_exists = False
        for i, user in enumerate(users):
            if str(user['user_id']) == str(user_entry['user_id']):
                user_exists = True
                # Сохраняем дату регистрации и телефон, если они уже были
                user_entry['registration_date'] = user['registration_date']
                if not user_entry['phone_number'] and user['phone_number']:
                    user_entry['phone_number'] = user['phone_number']
                users[i] = user_entry
                break

        if not user_exists:
            users.append(user_entry)

        self.write_users(users)

    def read_users(self) -> list:
        """Чтение всех пользователей из CSV"""
        if not os.path.exists(self.csv_file):
            return []
        
        with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)

    def write_users(self, users: list):
        """Запись пользователей в CSV"""
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
            if not users:
                return
            
            writer = csv.DictWriter(file, fieldnames=users[0].keys())
            writer.writeheader()
            writer.writerows(users)

    def log_user_action(self, user_id: int, action: str):
        """Логирование действий пользователя"""
        users = self.read_users()
        for user in users:
            if str(user['user_id']) == str(user_id):
                user['last_activity'] = self.get_current_time()
                user['last_command'] = action
                break
        self.write_users(users)

    def update_phone_number(self, user_id: int, phone_number: str):
        """Обновление номера телефона пользователя"""
        users = self.read_users()
        for user in users:
            if str(user['user_id']) == str(user_id):
                user['phone_number'] = phone_number
                break
        self.write_users(users) 