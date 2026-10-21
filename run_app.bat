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

echo Opening browser at http://localhost:8000 ...
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

echo Starting Python FastAPI Server (Press Ctrl+C to stop)...
echo ===================================================
py -m uvicorn main:app --host 127.0.0.1 --port 8000

if %errorlevel% neq 0 (
    echo.
    echo "py" launcher not found or failed, trying "python"...
    python -m uvicorn main:app --host 127.0.0.1 --port 8000
)

pause
