@echo off
REM Quick setup script for creating myvenv virtual environment

title IDS System - Virtual Environment Setup

echo ===============================================================================
echo   VIRTUAL ENVIRONMENT SETUP
echo ===============================================================================
echo.
echo This script will create the 'myvenv' virtual environment
echo and install all required dependencies.
echo.
pause

REM Check Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Check if myvenv already exists
if exist "myvenv\" (
    echo [WARNING] myvenv directory already exists!
    echo.
    set /p RECREATE="Do you want to recreate it? This will delete the existing one (y/n): "
    if /i "%RECREATE%"=="y" (
        echo Removing old myvenv...
        rmdir /s /q myvenv
    ) else (
        echo Keeping existing myvenv
        echo.
        echo Installing/updating dependencies only...
        goto :install_deps
    )
)

echo [INFO] Creating virtual environment 'myvenv'...
python -m venv myvenv

if %errorLevel% neq 0 (
    echo [ERROR] Failed to create virtual environment!
    pause
    exit /b 1
)

echo [OK] Virtual environment created
echo.

:install_deps
echo [INFO] Installing dependencies (this may take several minutes)...
echo.

myvenv\Scripts\python.exe -m pip install --upgrade pip
myvenv\Scripts\pip.exe install -r requirements.txt

if %errorLevel% neq 0 (
    echo [WARNING] Some packages may have failed to install
    echo.
    echo Common issues:
    echo   - No internet connection
    echo   - Package compatibility issues
    echo   - Missing system dependencies
    echo.
    echo You can try installing packages individually:
    echo   myvenv\Scripts\pip install fastapi uvicorn
    echo   myvenv\Scripts\pip install scapy
    echo   myvenv\Scripts\pip install tensorflow
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo   SETUP COMPLETE!
echo ===============================================================================
echo.
echo Virtual environment 'myvenv' is ready!
echo.
echo To activate it manually:
echo   myvenv\Scripts\activate
echo.
echo To start the system:
echo   START_SYSTEM.bat
echo   or
echo   QUICK_START.bat
echo.
pause
