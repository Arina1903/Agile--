@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "PYEXE=%~dp0.venv\Scripts\python.exe"

if not exist "%PYEXE%" (
  echo Создание виртуального окружения .venv ...
  py -3 -m venv .venv 2>nul
  if not exist "%PYEXE%" python -m venv .venv
  if not exist "%PYEXE%" (
    echo Не удалось создать venv. Установите Python с python.org и добавьте его в PATH.
    pause
    exit /b 1
  )
)

echo Установка зависимостей ^(pip install -r requirements.txt^) ...
"%PYEXE%" -m pip install -r requirements.txt -q
if errorlevel 1 (
  echo Ошибка pip install.
  pause
  exit /b 1
)

echo Запуск веб-приложения http://127.0.0.1:8000 ...
"%PYEXE%" -m webapp

echo.
pause
