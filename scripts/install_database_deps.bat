@echo off
REM Install database dependencies

echo ===============================================================================
echo   INSTALLING DATABASE DEPENDENCIES
echo ===============================================================================
echo.

cd /d "%~dp0.."

echo Installing SQLAlchemy for database support...
echo.

myvenv\Scripts\pip.exe install sqlalchemy>=2.0.0

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] SQLAlchemy installed successfully!
    echo.
    echo Next steps:
    echo   1. Enable database in config.yaml (database.enabled = true)
    echo   2. Run START_SYSTEM.bat to start monitoring
    echo   3. Data will be saved to: data\flows\network_flows.sqlite
    echo.
) else (
    echo.
    echo [ERROR] Installation failed!
    echo.
    echo Try running:
    echo   myvenv\Scripts\pip install --upgrade pip
    echo   myvenv\Scripts\pip install sqlalchemy
    echo.
)

pause
