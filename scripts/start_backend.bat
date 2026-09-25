@echo off
cd /d C:\Projetos\controleveterinario
if not exist logs mkdir logs
call venv\Scripts\activate.bat
echo ---------------------------------------------- >> logs\backend.log
echo Iniciado em %date% %time% >> logs\backend.log
uvicorn app.main:app --host 127.0.0.1 --port 8082 >> logs\backend.log 2>&1
