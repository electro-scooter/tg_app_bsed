import sys
import os
import logging
from datetime import datetime
import subprocess
import urllib.request

# Настройка логирования
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"bot_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def install_pip():
    logger.info("Установка pip...")
    try:
        # Скачиваем get-pip.py
        url = "https://bootstrap.pypa.io/get-pip.py"
        get_pip_path = "get-pip.py"
        urllib.request.urlretrieve(url, get_pip_path)
        
        # Устанавливаем pip
        subprocess.check_call([sys.executable, get_pip_path])
        
        # Удаляем временный файл
        os.remove(get_pip_path)
        logger.info("pip успешно установлен")
    except Exception as e:
        logger.error(f"Ошибка при установке pip: {e}")
        raise

def install_requirements():
    logger.info("Проверка и установка зависимостей...")
    try:
        # Проверяем наличие pip
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "--version"])
        except subprocess.CalledProcessError:
            logger.info("pip не найден, устанавливаем...")
            install_pip()
        
        # Устанавливаем зависимости
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("Зависимости успешно установлены")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при установке зависимостей: {e}")
        raise

try:
    # Устанавливаем зависимости перед запуском
    install_requirements()
    
    logger.info("Запуск бота...")
    from main import main
    
    if __name__ == '__main__':
        main()
        
except Exception as e:
    logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
    # Держим окно открытым в случае ошибки
    input("Нажмите Enter для выхода...") 