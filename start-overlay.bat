@echo off
REM Game Overlay AI - Start Electron Overlay
REM Starts the Electron overlay application

echo.
echo ========================================
echo   Starting Game Overlay AI Overlay
echo ========================================
echo.

REM Check if static directory exists
if not exist static (
    echo ERROR: static directory not found
    echo Please run setup-windows.bat first
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist static\node_modules (
    echo ERROR: Node.js dependencies not installed
    echo Please run setup-windows.bat first
    pause
    exit /b 1
)

echo 🖥️  Starting Electron overlay...
echo 🎮 Overlay window should open shortly
echo.
echo Make sure the backend is running (start-backend.bat)
echo.

cd static
call npm run dev

pause
