@echo off
title HR CV Analyzer AI
echo ===================================================
echo        Starting HR CV Analyzer AI App...
echo ===================================================
cd /d "%~dp0"

echo Opening browser at http://localhost:8000 ...
start http://localhost:8000

echo Starting Python FastAPI Server...
py -m uvicorn main:app --host 127.0.0.1 --port 8000

pause
