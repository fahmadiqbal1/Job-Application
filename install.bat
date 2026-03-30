@echo off
setlocal EnableDelayedExpansion

echo.
echo ============================================
echo  Job Application Dashboard - Setup
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found.
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo [1/6] Creating Python virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create venv
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate venv
    pause
    exit /b 1
)

echo [3/6] Installing Python packages...
pip install --upgrade pip -q
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: Failed to install Python packages
    pause
    exit /b 1
)

echo [4/6] Installing Playwright browser...
playwright install chromium -q
if errorlevel 1 (
    echo WARNING: Playwright installation had issues, continuing anyway
)

echo [5/6] Installing frontend dependencies...
cd frontend
npm install --silent
if errorlevel 1 (
    echo WARNING: npm install had issues
)

echo [6/6] Building React dashboard...
npm run build
if errorlevel 1 (
    echo WARNING: Build had issues, may not affect functionality
)

cd ..

echo.
echo [SETUP COMPLETE]
echo.

REM Check if .env exists
if not exist ".env" (
    echo Copying .env.example to .env...
    copy .env.example .env >nul
    echo.
    echo IMPORTANT: Edit .env and fill in your API keys:
    echo   - OPENAI_API_KEY
    echo   - TELEGRAM_BOT_TOKEN
    echo   - SMTP credentials (or leave blank for no email)
    echo.
)

echo To start the system, run:
echo   venv\Scripts\activate
echo   python main.py
echo.
echo Then open: http://localhost:8000
echo.
pause
