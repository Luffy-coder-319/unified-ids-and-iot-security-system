@echo off
echo ========================================
echo   Adaptive Baseline Learning Setup
echo ========================================
echo.
echo This will enable automatic learning to reduce false positives.
echo.
echo What it does:
echo   - System learns your network for 1 hour
echo   - Automatically suppresses false positives
echo   - No manual work required!
echo.
echo Current status:
echo   Adaptive baseline is ALREADY ENABLED in config.yaml
echo.
echo Next step:
echo   Just start the monitoring system!
echo.
echo ========================================
echo.
pause
echo.
echo Starting live monitoring with adaptive baseline...
echo.
python start_live_monitoring.py
