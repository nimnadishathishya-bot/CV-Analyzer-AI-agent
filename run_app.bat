@echo off
title HR CV Analyzer AI
echo ===================================================
echo        Starting HR CV Analyzer AI App...
echo ===================================================
cd /d "%~dp0"

:: Release port 8000 if previously occupied
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo Starting Python FastAPI Server...
start "" py -m uvicorn main:app --host 127.0.0.1 --port 8000

echo Waiting for server to initialize...
timeout /t 2 /nobreak >nul

echo Opening browser at http://localhost:8000 ...
start http://localhost:8000

echo ===================================================
echo  App is active at http://localhost:8000
echo  Press Ctrl+C or close this window to stop.
echo ===================================================
pause
