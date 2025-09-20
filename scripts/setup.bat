@echo off
REM Legal Document Analysis AI System - Windows Setup Script
REM This script sets up the entire development environment on Windows

echo 🚀 Setting up Legal Document Analysis AI System...
echo.

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.8+ is required but not installed
    echo Please install Python from https://python.org
    pause
    exit /b 1
)
echo [SUCCESS] Python found
echo.

REM Check if Node.js is installed
echo [INFO] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js 18+ is required but not installed
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)
echo [SUCCESS] Node.js found
echo.

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist uploads mkdir uploads
if not exist results mkdir results
if not exist logs mkdir logs
echo [SUCCESS] Directories created
echo.

REM Setup backend
echo [INFO] Setting up backend...
cd src\backend

REM Create virtual environment
echo [INFO] Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment and install dependencies
echo [INFO] Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo [INFO] Creating .env file...
    echo OPENAI_API_KEY=your_openai_api_key_here > .env
    echo [WARNING] Please update .env file with your OpenAI API key
)

echo [SUCCESS] Backend setup complete
cd ..\..

REM Setup frontend
echo [INFO] Setting up frontend...
cd src\frontend

REM Install dependencies
echo [INFO] Installing Node.js dependencies...
npm install

echo [SUCCESS] Frontend setup complete
cd ..\..

REM Final instructions
echo.
echo ==========================================
echo [SUCCESS] Setup complete! 🎉
echo ==========================================
echo.
echo Next steps:
echo 1. Update your OpenAI API key in src\backend\.env
echo 2. Start the backend: cd src\backend ^&^& python main.py
echo 3. Start the frontend: cd src\frontend ^&^& npm run dev
echo 4. Open http://localhost:3000 in your browser
echo.
echo For more information, see README.md
echo.
pause
