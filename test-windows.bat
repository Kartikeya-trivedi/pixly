@echo off
REM Game Overlay AI - Run Tests on Windows
REM Runs the test suite with proper Windows paths

echo.
echo ========================================
echo   Running Game Overlay AI Tests
echo ========================================
echo.

REM Check if dependencies are installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: uv not found
    echo Please run setup-windows.bat first
    pause
    exit /b 1
)

echo 🧪 Running test suite...
echo.

REM Run tests with coverage
uv run pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

if %errorlevel% neq 0 (
    echo.
    echo ❌ Some tests failed
    echo Check the output above for details
) else (
    echo.
    echo ✅ All tests passed!
    echo 📊 Coverage report generated in htmlcov/
)

echo.
pause
