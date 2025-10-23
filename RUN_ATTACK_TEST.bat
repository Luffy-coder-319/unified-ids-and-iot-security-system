@echo off
REM Quick Attack Testing Script for IDS
REM This script helps you test the IDS system with various attacks

echo ============================================
echo IDS Attack Testing Script
echo ============================================
echo.

:menu
echo Select a test to run:
echo.
echo 1. HTTP Flood Attack (DoS-HTTP_Flood)
echo 2. Port Scan (Recon-PortScan)
echo 3. UDP Flood (DoS-UDP_Flood)
echo 4. SYN Flood (DoS-SYN_Flood)
echo 5. SQL Injection Test (SqlInjection)
echo 6. XSS Test (XSS)
echo 7. Mixed Attack (Multiple types)
echo 8. Benign Traffic (Baseline)
echo 9. View Logs
echo 0. Exit
echo.

set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto http_flood
if "%choice%"=="2" goto port_scan
if "%choice%"=="3" goto udp_flood
if "%choice%"=="4" goto syn_flood
if "%choice%"=="5" goto sql_injection
if "%choice%"=="6" goto xss_test
if "%choice%"=="7" goto mixed_attack
if "%choice%"=="8" goto benign
if "%choice%"=="9" goto view_logs
if "%choice%"=="0" goto end

echo Invalid choice. Please try again.
echo.
goto menu

:http_flood
echo.
echo Running HTTP Flood Attack Test...
echo Target: 192.168.1.238:8000
echo Duration: 30 seconds, 20 threads
echo.
python tests\attack_simulator.py --attack http-flood --target 192.168.1.238 --port 8000 --duration 30 --threads 20
echo.
pause
goto menu

:port_scan
echo.
echo Running Port Scan Test...
echo Target: 192.168.1.238
echo Ports: 1-200
echo.
python tests\attack_simulator.py --attack port-scan --target 192.168.1.238 --start-port 1 --end-port 200
echo.
pause
goto menu

:udp_flood
echo.
echo Running UDP Flood Attack Test...
echo Target: 192.168.1.238:53
echo Packets: 1000
echo.
python tests\attack_simulator.py --attack udp-flood --target 192.168.1.238 --port 53 --count 1000
echo.
pause
goto menu

:syn_flood
echo.
echo Running SYN Flood Attack Test...
echo Target: 192.168.1.238:80
echo Packets: 1000
echo Note: Requires Scapy (optional)
echo.
python tests\attack_simulator.py --attack syn-flood --target 192.168.1.238 --port 80 --count 1000
echo.
pause
goto menu

:sql_injection
echo.
echo Running SQL Injection Test...
echo Target: 192.168.1.238:8000/api/test
echo.
python tests\attack_simulator.py --attack sql-injection --target 192.168.1.238 --port 8000
echo.
pause
goto menu

:xss_test
echo.
echo Running XSS Test...
echo Target: 192.168.1.238:8000/api/test
echo.
python tests\attack_simulator.py --attack xss --target 192.168.1.238 --port 8000
echo.
pause
goto menu

:mixed_attack
echo.
echo Running Mixed Attack Test...
echo Target: 192.168.1.238
echo Duration: 60 seconds
echo Multiple attack types will be tested in sequence
echo.
python tests\attack_simulator.py --attack mixed --target 192.168.1.238 --duration 60
echo.
pause
goto menu

:benign
echo.
echo Running Benign Traffic Test...
echo Target: 192.168.1.238:8000
echo Duration: 30 seconds
echo.
python tests\attack_simulator.py --attack benign --target 192.168.1.238 --port 8000 --duration 30
echo.
pause
goto menu

:view_logs
echo.
echo ============================================
echo Recent Alerts (Last 20 lines)
echo ============================================
echo.
type logs\alerts.jsonl 2>nul | more
echo.
echo ============================================
echo Statistics
echo ============================================
echo.
type logs\statistics.json 2>nul | more
echo.
echo ============================================
echo To monitor logs in real-time, open PowerShell and run:
echo Get-Content logs\alerts.jsonl -Wait -Tail 20
echo ============================================
echo.
pause
goto menu

:end
echo.
echo Exiting...
exit /b 0
