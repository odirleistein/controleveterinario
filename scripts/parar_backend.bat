@echo off
rem Derruba o uvicorn que esta ouvindo na porta 8082.
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /r /c:"TCP.*:8082.*LISTENING"') do taskkill /PID %%p /F
