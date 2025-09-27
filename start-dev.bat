@echo off
REM Game Overlay AI - Start Full Development Environment
REM Starts both backend and overlay in separate windows

echo.
echo ========================================
echo   Starting Full Development Environment
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found
    echo Please run setup-windows.bat first
    pause
    exit /b 1
)

echo 🚀 Starting Game Overlay AI development environment...
echo.

REM Start backend in new window
echo 📡 Starting backend server...
start "Game Overlay AI - Backend" cmd /k "uv run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start overlay in new window
echo 🖥️  Starting overlay application...
start "Game Overlay AI - Overlay" cmd /k "cd static && npm run dev"

echo.
echo ✅ Development environment started!
echo.
echo 📡 Backend: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 🖥️  Overlay: Electron window should open
echo.
echo Both windows will stay open. Close them to stop the services.
echo.
pause
