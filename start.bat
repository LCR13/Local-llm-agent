@echo off
title LLA start

set ENV_NAME=local_llm

echo [SYSTEM] Activating Environment: %ENV_NAME%

echo [1/2] Launching backend
start "Backend API" cmd /k "call conda activate %ENV_NAME% && cd backend && uvicorn main:app --host 127.0.0.1 --port 8000"

timeout /t 5 >nul

echo [2/2] Launching web interface
start "Frontend Server" cmd /k "cd frontend && python run.py"

echo [SUCCESS]