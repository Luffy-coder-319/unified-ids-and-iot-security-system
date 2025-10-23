@echo off
REM Simple launcher for the Unified IDS and IoT Security System
REM This will automatically request Administrator privileges if needed

echo ===============================================================================
echo   UNIFIED IDS AND IOT SECURITY SYSTEM - LAUNCHER
echo ===============================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges
    echo.
    REM Run PowerShell script directly
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0START_SYSTEM.ps1"
) else (
    echo [INFO] Requesting Administrator privileges...
    echo.
    REM Request admin and run PowerShell script
    powershell.exe -NoProfile -Command "Start-Process powershell.exe -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0START_SYSTEM.ps1\"' -Verb RunAs"
)
