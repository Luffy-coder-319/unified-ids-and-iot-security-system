@echo off
REM Quickest way to start the system - API Server only (no admin required)
REM For full monitoring with live capture, use START_SYSTEM.bat instead

title IDS System - Quick Start (API Server Only)

echo ===============================================================================
echo   QUICK START - API SERVER ONLY
echo ===============================================================================
echo.
echo This mode does NOT require Administrator privileges
echo Live packet capture is DISABLED
echo System will show historical alerts only
echo.
echo For full monitoring with live capture, use START_SYSTEM.bat
echo.
echo ===============================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if myvenv virtual environment exists
if exist "myvenv\Scripts\python.exe" (
    set PYTHON_PATH=myvenv\Scripts\python.exe
    echo [OK] Using myvenv virtual environment
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

REM Set environment variables to suppress warnings
set TF_CPP_MIN_LOG_LEVEL=3
set TF_ENABLE_ONEDNN_OPTS=0

echo [INFO] Starting API server...
echo.
echo Dashboard: http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

REM Start the server
%PYTHON_PATH% -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

pause
