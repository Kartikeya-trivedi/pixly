@echo off
REM Quick fix to create .env file
echo.
echo ========================================
echo   Creating .env file
echo ========================================
echo.

if exist .env (
    echo ✅ .env file already exists
    pause
    exit /b 0
)

echo 📝 Creating .env file...
echo HOST=127.0.0.1 > .env
echo PORT=8000 >> .env
echo DEBUG=true >> .env
echo DATABASE_URL=sqlite:///./game_overlay.db >> .env
echo CHROMA_PERSIST_DIRECTORY=./chroma_db >> .env
echo VECTOR_DB_COLLECTION_NAME=game_guides >> .env
echo EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 >> .env
echo CHUNK_SIZE=1000 >> .env
echo CHUNK_OVERLAP=200 >> .env
echo GEMINI_API_KEY=your_gemini_api_key_here >> .env
echo OPENAI_API_KEY=your_openai_api_key_here >> .env
echo MAX_TIPS_PER_REQUEST=5 >> .env
echo OVERLAY_UPDATE_INTERVAL=5 >> .env

echo ✅ .env file created successfully!
echo.
echo ⚠️  IMPORTANT: Please edit .env file and add your API keys:
echo    - GEMINI_API_KEY=your_gemini_api_key_here
echo    - OPENAI_API_KEY=your_openai_api_key_here (optional)
echo.
echo You can now run: start-dev.bat
echo.
pause
