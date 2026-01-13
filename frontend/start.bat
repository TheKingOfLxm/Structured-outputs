@echo off
chcp 65001 >nul
echo ================================================
echo   Academic Reading Assistant - Frontend
echo ================================================
echo.

if not exist "node_modules" (
    echo [1/2] Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo Error: npm install failed
        pause
        exit /b 1
    )
) else (
    echo [1/2] Dependencies installed
)

echo [2/2] Starting dev server...
echo.
echo Server: http://localhost:5173
echo Press Ctrl+C to stop
echo.
call npm run dev

pause
