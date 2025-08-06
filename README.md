# Черноморский Туристический Бот

Telegram-бот для помощи туристам на Черноморском побережье России.

## Основные функции

- 🌡 Погода в реальном времени
- 🗺 Информация об экскурсиях
- 🏨 Поиск жилья
- 📰 Новости региона
- 🎫 Бронирование туров

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/black-sea-bot.git
cd black-sea-bot
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` и добавьте необходимые токены:
```
BOT_TOKEN=your_telegram_bot_token
WEATHER_API_KEY=your_weather_api_key
```

5. Запустите бота:
```bash
python main.py
```

## Структура проекта

```
├── main.py                 # Точка входа
├── config.py              # Конфигурация
├── handlers/              # Обработчики команд
├── services/             # Бизнес-логика
├── models/              # Модели данных
├── utils/               # Вспомогательные функции
└── requirements.txt     # Зависимости
```

## Поддерживаемые города

- Лазаревское
- Вардане
- Лоо
- Дагомыс
- Сочи
- Мацеста
- Хоста
- Кудепста
- Адлер

## Лицензия

MIT 