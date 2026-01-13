@echo off
chcp 65001 >nul
echo ================================================
echo   Academic Reading Assistant - Backend (No Venv)
echo ================================================
echo.

REM Find Python
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :found
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py
    goto :found
)

echo Error: Python not found!
pause
exit /b 1

:found
echo Found Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

if not exist ".env" (
    echo Creating .env file...
    echo SECRET_KEY=dev-secret-key > .env
    echo JWT_SECRET_KEY=dev-jwt-secret-key >> .env
    echo ZHIPUAI_API_KEY= >> .env
    echo .env file created
    echo.
)

echo Installing dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt

echo.
echo Starting Flask server...
echo Server: http://localhost:5000
echo.
%PYTHON_CMD% run.py

pause
