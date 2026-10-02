@echo off
chcp 65001 >nul
setlocal
set "MYSQL=C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"
set "OUT=%~dp0Lab2_output.txt"
echo Lab2: root password is asked ONCE per script (4 times).
echo. > "%OUT%"
for %%F in (01_create_schema 02_insert_data 03_select_queries 04_users_privileges) do (
  echo ===== %%F ===== >> "%OUT%"
  "%MYSQL%" -u root -p --default-character-set=utf8mb4 -t -vvv < "%~dp0%%F.sql" >> "%OUT%" 2>&1
)
echo Done. Results saved to: %OUT%
pause
