@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\activate.bat (
  echo [ERROR] Run setup.bat first.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python monitor.py %*
pause
