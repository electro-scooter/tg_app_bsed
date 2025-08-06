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

:: Проверка прав администратора и перезапуск с повышением прав при необходимости
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin
) else (
    echo Запрашиваем права администратора...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit
)

:admin
cd /d "%~dp0"
python run_bot.py
pause 