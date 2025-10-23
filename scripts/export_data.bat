@echo off
REM Quick data export script for Windows

echo ===============================================================================
echo   DATA EXPORT UTILITY - Network Flow Database
echo ===============================================================================
echo.

REM Change to project root
cd /d "%~dp0.."

echo Choose export type:
echo   1) Export for model training (last 30 days)
echo   2) Export attack samples only
echo   3) Export labeled data
echo   4) Export balanced samples per attack type
echo   5) Custom export (advanced)
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo [1] Exporting training data from last 30 days...
    echo.
    myvenv\Scripts\python.exe -m src.database.export_utils train --output data\exports\training_data.csv --days 30
    echo.
    echo [OK] Exported to: data\exports\training_data.csv
)

if "%choice%"=="2" (
    echo.
    echo [2] Exporting attack samples only...
    echo.
    myvenv\Scripts\python.exe -m src.database.export_utils train --output data\exports\attacks_only.csv --no-benign --days 30
    echo.
    echo [OK] Exported to: data\exports\attacks_only.csv
)

if "%choice%"=="3" (
    echo.
    echo [3] Exporting labeled data...
    echo.
    myvenv\Scripts\python.exe -m src.database.export_utils labels --output data\exports\labeled_data.csv
    echo.
    echo [OK] Exported to: data\exports\labeled_data.csv
)

if "%choice%"=="4" (
    echo.
    echo [4] Exporting balanced samples per attack type...
    echo.
    myvenv\Scripts\python.exe -m src.database.export_utils samples --output-dir data\exports\balanced
    echo.
    echo [OK] Exported to: data\exports\balanced\
)

if "%choice%"=="5" (
    echo.
    echo [5] Custom Export Options:
    echo.
    echo Examples:
    echo   Export last 7 days:
    echo     python -m src.database.export_utils train --output my_data.csv --days 7
    echo.
    echo   Export high confidence only:
    echo     python -m src.database.export_utils train --output high_conf.csv --min-confidence 0.95
    echo.
    echo   Export specific attacks:
    echo     python -m src.database.export_utils train --output ddos.csv --attacks DDoS
    echo.
    echo See docs\DATABASE_GUIDE.md for full documentation
)

echo.
pause
