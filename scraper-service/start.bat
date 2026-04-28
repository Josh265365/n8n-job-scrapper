@echo off
REM FastAPI Scraper Service Startup Script

echo ========================================
echo  Job Scraper Service - Startup
echo ========================================

cd /d "%~dp0"

REM 1. Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM 2. Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM 3. Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM 4. Install/upgrade dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM 5. Check if Playwright browsers are installed
echo [INFO] Checking Playwright browsers...
python -c "from playwright.sync_api import sync_playwright; sync_playwright().stop()" 2>nul
if errorlevel 1 (
    echo [INFO] Installing Playwright Chromium browser...
    playwright install chromium
)

REM 6. Load .env and start server
echo [INFO] Starting FastAPI server on port 8000...
echo [INFO] n8n should call: http://host.docker.internal:8000/scrape
echo ========================================

python main.py
