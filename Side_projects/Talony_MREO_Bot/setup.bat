@echo off
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>nul && (py -3 -m venv .venv) || (python -m venv .venv)
if errorlevel 1 goto :err
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto :err
python -m playwright install chromium
if errorlevel 1 goto :err
if not exist config.json copy config.example.json config.json >nul
echo.
echo [OK] Setup done. Now open config.json and paste telegram_token (see README.md).
pause
exit /b 0

:err
echo [ERROR] Setup failed. Check that Python 3.10+ is installed (python.org, tick "Add to PATH").
pause
exit /b 1
