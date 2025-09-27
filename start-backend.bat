@echo off
REM Game Overlay AI - Start Backend Server
REM Starts the FastAPI backend server

echo.
echo ========================================
echo   Starting Game Overlay AI Backend
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found
    echo Please run setup-windows.bat first
    pause
    exit /b 1
)

echo 🚀 Starting FastAPI backend server...
echo 📡 Backend will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uv run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

pause
