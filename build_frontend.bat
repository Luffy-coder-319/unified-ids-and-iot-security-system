@echo off
REM Build the React frontend for the IDS Dashboard

echo ===============================================================================
echo   Building IDS Dashboard Frontend
echo ===============================================================================
echo.

cd src\frontend

REM Check if node_modules exists
if not exist "node_modules\" (
    echo [INFO] Installing dependencies...
    call npm install
    if %errorLevel% neq 0 (
        echo [ERROR] npm install failed!
        echo.
        echo Please ensure Node.js is installed: https://nodejs.org/
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Building production bundle...
call npm run build

if %errorLevel% neq 0 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [OK] Frontend built successfully!
echo.
echo The dashboard is now ready at: http://localhost:8000
echo.
echo To start the server:
echo   start_server.bat
echo.
pause
