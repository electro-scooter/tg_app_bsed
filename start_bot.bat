@echo off
:: Проверка наличия Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python не найден в системе!
    echo Пожалуйста, установите Python 3.x с официального сайта:
    echo https://www.python.org/downloads/
    echo.
    echo После установки убедитесь, что отметили галочку "Add Python to PATH"
    pause
    exit
)

:: Переход в директорию скрипта
cd /d "%~dp0"

:: Запуск основного скрипта
python run_bot.py
pause