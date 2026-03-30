#!/bin/bash

echo ""
echo "============================================"
echo " Job Application Dashboard - Setup"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found."
    echo "Please install Python 3.11+ from https://python.org"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found."
    echo "Please install Node.js from https://nodejs.org"
    exit 1
fi

echo "[1/6] Creating Python virtual environment..."
python3 -m venv venv || exit 1

echo "[2/6] Activating virtual environment..."
source venv/bin/activate || exit 1

echo "[3/6] Installing Python packages..."
pip install --upgrade pip -q
pip install -r requirements.txt -q || exit 1

echo "[4/6] Installing Playwright browser..."
playwright install chromium -q || echo "WARNING: Playwright installation had issues"

echo "[5/6] Installing frontend dependencies..."
cd frontend
npm install --silent || echo "WARNING: npm install had issues"

echo "[6/6] Building React dashboard..."
npm run build || echo "WARNING: Build had issues"

cd ..

echo ""
echo "[SETUP COMPLETE]"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env and fill in your API keys:"
    echo "  - OPENAI_API_KEY"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - SMTP credentials (or leave blank for no email)"
    echo ""
fi

echo "To start the system, run:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Then open: http://localhost:8000"
echo ""
