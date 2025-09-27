@echo off
REM Game Overlay AI - Clean Windows Environment
REM Cleans up temporary files and caches

echo.
echo ========================================
echo   Cleaning Game Overlay AI Environment
echo ========================================
echo.

echo 🧹 Cleaning Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f"
for /r . %%f in (*.pyo) do @if exist "%%f" del /q "%%f"

echo 🧹 Cleaning test artifacts...
if exist htmlcov rmdir /s /q htmlcov
if exist .coverage del /q .coverage
if exist .pytest_cache rmdir /s /q .pytest_cache
if exist .mypy_cache rmdir /s /q .mypy_cache

echo 🧹 Cleaning build artifacts...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.egg-info rmdir /s /q *.egg-info

echo 🧹 Cleaning database files...
if exist *.db del /q *.db
if exist *.sqlite del /q *.sqlite
if exist *.sqlite3 del /q *.sqlite3

echo 🧹 Cleaning vector database...
if exist chroma_db rmdir /s /q chroma_db
if exist chroma_db_dev rmdir /s /q chroma_db_dev

echo 🧹 Cleaning data directory...
if exist data rmdir /s /q data

echo.
echo ✅ Cleanup complete!
echo.
pause
