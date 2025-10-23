@echo off
REM Helper script to run anomaly tests on Windows
REM Must be run as Administrator for packet capture

echo ===============================================================================
echo   Anomaly Test Generator - Administrator Required
echo ===============================================================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges!
    echo.
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Running with Administrator privileges
echo.

REM Check if myvenv virtual environment exists
if exist "myvenv\Scripts\python.exe" (
    echo [OK] Using myvenv virtual environment
    set PYTHON_PATH=myvenv\Scripts\python.exe
) else (
    echo [ERROR] Virtual environment 'myvenv' not found!
    echo.
    echo Please create it first with:
    echo   python -m venv myvenv
    echo   myvenv\Scripts\pip install -r requirements.txt
    echo.
    echo Or run START_SYSTEM.bat to set up automatically
    pause
    exit /b 1
)

echo.
echo [INFO] Running anomaly generator...
echo.

REM Run with virtual environment Python
%PYTHON_PATH% -m tests.generate_anomalies %*

echo.
echo [INFO] Test completed
pause
