@echo off
chcp 65001 >nul
echo ================================================
echo   Academic Reading Assistant - Backend
echo ================================================
echo.

REM Find Python
set PYTHON_CMD=
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :found
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python3
    goto :found
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py
    goto :found
)

echo Error: Python not found!
echo Please install Python 3.8+ from: https://www.python.org/
echo.
echo After installation, make sure to check "Add Python to PATH"
pause
exit /b 1

:found
echo Found Python: %PYTHON_CMD%
%PYTHON_CMD% --version

if not exist "venv" (
    echo.
    echo [1/3] Creating virtual environment...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo.
        echo Error: Failed to create virtual environment
        echo.
        echo Try installing venv:
        echo   %PYTHON_CMD% -m pip install virtualenv
        echo.
        pause
        exit /b 1
    )
    echo Virtual environment created!
) else (
    echo [1/3] Virtual environment exists
)

echo [2/3] Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Error: venv\Scripts\activate.bat not found
    echo Try deleting the venv folder and run this script again
    pause
    exit /b 1
)

echo [2/3] Installing dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt

if not exist ".env" (
    echo.
    echo [3/3] Creating .env file...
    if exist ".env.example" (
        copy .env.example .env
        echo .env file created from .env.example
    ) else (
        echo Creating .env file...
        echo SECRET_KEY=dev-secret-key > .env
        echo JWT_SECRET_KEY=dev-jwt-secret-key >> .env
        echo ZHIPUAI_API_KEY= >> .env
    )
    echo.
    echo ================================================
    echo   IMPORTANT! Edit backend\.env file:
    echo   - Set ZHIPUAI_API_KEY (optional)
    echo ================================================
    echo.
)

echo [3/3] Starting Flask server...
echo.
echo Server: http://localhost:5000
echo Press Ctrl+C to stop
echo.
%PYTHON_CMD% run.py

pause
