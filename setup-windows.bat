@echo off
REM Game Overlay AI - Windows Setup Script
REM This script sets up the development environment on Windows

echo.
echo ========================================
echo   Game Overlay AI - Windows Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

echo ✅ Python and Node.js are installed
echo.

REM Install uv if not present
echo 📦 Installing uv (Python package manager)...
pip install uv
if %errorlevel% neq 0 (
    echo ERROR: Failed to install uv
    pause
    exit /b 1
)

echo ✅ uv installed successfully
echo.

REM Create virtual environment and install Python dependencies
echo 📦 Creating virtual environment...
uv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo 📦 Installing Python dependencies...
uv pip install -e ".[dev]"
if %errorlevel% neq 0 (
    echo WARNING: Editable install failed, trying system install...
    echo 🔧 Installing dependencies without editable mode...
    uv pip install --system fastapi uvicorn sqlalchemy pydantic pydantic-settings chromadb sentence-transformers google-generativeai requests beautifulsoup4 python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv httpx aiofiles
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Python dependencies
        pause
        exit /b 1
    )
    echo 📦 Installing development dependencies...
    uv pip install --system pytest pytest-asyncio pytest-cov black isort flake8 mypy pre-commit
    if %errorlevel% neq 0 (
        echo WARNING: Some development dependencies may not have installed correctly
    )
)

echo ✅ Python dependencies installed
echo.

REM Install Electron dependencies
echo 📦 Installing Electron dependencies...
cd static
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Electron dependencies
    pause
    exit /b 1
)
cd ..

echo ✅ Electron dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    if exist env.example (
        copy env.example .env
        echo ✅ .env file created
    ) else (
        echo 📝 Creating basic .env file...
        echo HOST=127.0.0.1 > .env
        echo PORT=8000 >> .env
        echo DEBUG=true >> .env
        echo DATABASE_URL=sqlite:///./game_overlay.db >> .env
        echo CHROMA_PERSIST_DIRECTORY=./chroma_db >> .env
        echo GEMINI_API_KEY=your_gemini_api_key_here >> .env
        echo ✅ .env file created
    )
    echo.
    echo ⚠️  IMPORTANT: Please edit .env file and add your API keys:
    echo    - GEMINI_API_KEY=your_gemini_api_key_here
    echo    - OPENAI_API_KEY=your_openai_api_key_here (optional)
    echo.
) else (
    echo ✅ .env file already exists
)

echo.

REM Initialize database
echo 🗄️  Initializing database...
uv run python -c "from src.db.database import create_tables; create_tables(); print('Database initialized')"
if %errorlevel% neq 0 (
    echo WARNING: uv run failed, trying direct python...
    python -c "from src.db.database import create_tables; create_tables(); print('Database initialized')"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to initialize database
        pause
        exit /b 1
    )
)

echo ✅ Database initialized
echo.

REM Run sample ETL pipeline
echo 📊 Running sample ETL pipeline...
uv run python scripts/etl_sample_data.py
if %errorlevel% neq 0 (
    echo WARNING: uv run ETL failed, trying direct python...
    python scripts/etl_sample_data.py
    if %errorlevel% neq 0 (
        echo WARNING: ETL pipeline failed, but setup can continue
        echo You can run it later with: uv run python scripts/etl_sample_data.py
    )
)

echo.
echo ========================================
echo   Setup Complete! 🎉
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your API keys
echo 2. Start the backend: start-backend.bat
echo 3. Start the overlay: start-overlay.bat
echo.
echo Or run both together: start-dev.bat
echo.
pause
