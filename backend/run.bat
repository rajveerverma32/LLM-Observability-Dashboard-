@echo off
REM LLM Observability Backend Startup Script for Windows

echo.
echo 🚀 LLM Observability Dashboard - Backend Startup
echo ==================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

echo ✓ Python version:
python --version

REM Check if requirements are installed
echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist .env (
    echo 📝 Creating .env from template...
    copy .env.example .env
    echo ⚠️  Please update .env with your configuration
)

REM Start the server
echo.
echo 🎯 Starting FastAPI server...
echo 📍 API will be available at: http://localhost:8000
echo 📖 Documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

pause
