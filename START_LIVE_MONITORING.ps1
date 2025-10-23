# Start Live Network Monitoring (Administrator Required)
# This script starts the IDS system with real network traffic capture

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "  LIVE NETWORK MONITORING - IoT Security System" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please right-click this file and select 'Run with PowerShell as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or run PowerShell as Administrator and execute:" -ForegroundColor Yellow
    Write-Host "  .\START_LIVE_MONITORING.ps1" -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

Write-Host "[OK] Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Cyan
if (Test-Path ".\myvenv\Scripts\Activate.ps1") {
    & .\myvenv\Scripts\Activate.ps1
    Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create it first: python -m venv myvenv" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "[INFO] Starting live network monitoring..." -ForegroundColor Cyan
Write-Host "[INFO] Monitoring WiFi adapter: 192.168.1.238" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API alerts endpoint: http://localhost:8000/api/alerts" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
Write-Host ""

# Start the system
python start_live_monitoring.py

Write-Host ""
Write-Host "[INFO] Monitoring stopped" -ForegroundColor Cyan
pause
