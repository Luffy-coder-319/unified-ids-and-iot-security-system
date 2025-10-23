@echo off
REM Full system startup with live monitoring - REQUIRES ADMINISTRATOR
REM This is a shortcut to START_SYSTEM.bat with monitoring enabled

echo ===============================================================================
echo   FULL SYSTEM START - LIVE MONITORING REQUIRED
echo ===============================================================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Administrator privileges required for live monitoring
    echo [INFO] Requesting elevation...
    echo.
    powershell.exe -NoProfile -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [OK] Running with Administrator privileges
echo.

REM Change to script directory
cd /d "%~dp0"

REM Run the main startup script (will default to full mode)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0START_SYSTEM.ps1"

pause
