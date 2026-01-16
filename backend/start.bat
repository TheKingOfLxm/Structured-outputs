@echo off
chcp 65001
echo ================================================
echo   Academic Reading Assistant - Backend
echo ================================================
echo.

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python not found!
    echo Please install Python 3.8+
    pause
    exit /b 1
)

echo Found Python
python --version

if not exist "venv" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install Flask==3.0.0 Flask-CORS==4.0.0 Flask-JWT-Extended==4.6.0
python -m pip install Flask-SQLAlchemy==3.1.1 SQLAlchemy==2.0.23
python -m pip install PyPDF2==3.0.1 pdfplumber==0.10.3 Pillow==10.2.0
python -m pip install zhipuai openai
python -m pip install python-dotenv requests Werkzeug psutil

if not exist ".env" (
    echo [3/3] Creating .env file...
    echo SECRET_KEY=dev-secret-key > .env
    echo JWT_SECRET_KEY=dev-jwt-secret-key >> .env
    echo ZHIPUAI_API_KEY= >> .env
)

echo [3/3] Starting Flask server...
echo.
echo Server: http://localhost:5000
echo Press Ctrl+C to stop
echo.
python run.py

pause
