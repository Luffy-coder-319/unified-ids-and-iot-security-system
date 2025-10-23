# Test script for LOCAL attack simulation (bypasses private network filtering)
# This script enables TEST MODE in the detection system

# Check for administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LOCAL Attack Testing (Test Mode)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please right-click this file and select 'Run with PowerShell as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# Step 1: Enable test mode via API
Write-Host "[Step 1/5] Enabling test mode..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/network/status" -UseBasicParsing -ErrorAction Stop
    $serverRunning = $true
} catch {
    Write-Host "[!] Server is not running" -ForegroundColor Red
    $serverRunning = $false
}

if (-not $serverRunning) {
    Write-Host ""
    Write-Host "Please start the server first:" -ForegroundColor Blue
    Write-Host "  .\START_LIVE_MONITORING.ps1" -ForegroundColor Green
    Write-Host ""
    pause
    exit 1
}

# Enable test mode by setting detection mode to 'pure_ml'
try {
    $body = @{
        mode = "pure_ml"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/detection/mode" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    Write-Host "[OK] Test mode enabled (pure ML detection)" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Could not enable test mode via API" -ForegroundColor Yellow
    Write-Host "Continuing with current detection mode..." -ForegroundColor Yellow
}
Write-Host ""

# Step 2: Get local IP
Write-Host "[Step 2/5] Detecting local IP address..." -ForegroundColor Yellow

$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.IPAddress -ne "127.0.0.1" -and $_.PrefixOrigin -ne "WellKnown"
} | Select-Object -First 1).IPAddress

if (-not $localIP) {
    $localIP = "127.0.0.1"
}

Write-Host "[OK] Target IP: $localIP" -ForegroundColor Green
Write-Host ""

# Step 3: Open dashboard
Write-Host "[Step 3/5] Opening dashboard..." -ForegroundColor Yellow
Start-Process "http://localhost:8000"
Write-Host "[OK] Dashboard URL: http://localhost:8000" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter once you have the Alerts tab open"
Write-Host ""

# Step 4: Clear existing alerts
Write-Host "[Step 4/5] Clearing previous alerts..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://localhost:8000/api/alerts/clear" -Method POST -UseBasicParsing -ErrorAction SilentlyContinue
    Write-Host "[OK] Alerts cleared" -ForegroundColor Green
} catch {
    Write-Host "[OK] Continuing..." -ForegroundColor Green
}
Write-Host ""

# Step 5: Run attack simulation
Write-Host "[Step 5/5] Running LOCAL attack simulation..." -ForegroundColor Yellow
Write-Host "Target: $localIP (local network)" -ForegroundColor Blue
Write-Host ""

Write-Host "Select attack type:" -ForegroundColor Yellow
Write-Host "  1) SYN Flood (300 packets)" -ForegroundColor White
Write-Host "  2) UDP Flood (300 packets)" -ForegroundColor White
Write-Host "  3) Port Scan (ports 75-100)" -ForegroundColor White
Write-Host "  4) All attacks (comprehensive)" -ForegroundColor White
Write-Host ""
$attackChoice = Read-Host "Select (1-4) [default: 1]"
if ([string]::IsNullOrWhiteSpace($attackChoice)) {
    $attackChoice = "1"
}

# Determine Python path
if (Test-Path "..\myvenv\Scripts\python.exe") {
    $pythonPath = "..\myvenv\Scripts\python.exe"
} elseif (Test-Path "..\venv\Scripts\python.exe") {
    $pythonPath = "..\venv\Scripts\python.exe"
} else {
    $pythonPath = "python"
}

# Set PYTHONPATH
$projectRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = $projectRoot

Write-Host ""
Write-Host "Launching attack simulation..." -ForegroundColor Cyan
Write-Host "Watch the dashboard for alerts!" -ForegroundColor Yellow
Write-Host ""

switch ($attackChoice) {
    "1" {
        Write-Host "Running SYN Flood attack..." -ForegroundColor Magenta
        & $pythonPath run_attack.py --target $localIP --syn-flood --count 300 --rate 200
    }
    "2" {
        Write-Host "Running UDP Flood attack..." -ForegroundColor Magenta
        & $pythonPath run_attack.py --target $localIP --udp-flood --count 300 --rate 200
    }
    "3" {
        Write-Host "Running Port Scan..." -ForegroundColor Magenta
        & $pythonPath run_attack.py --target $localIP --port-scan --ports 75-100
    }
    "4" {
        Write-Host "Running ALL attacks..." -ForegroundColor Magenta
        & $pythonPath run_attack.py --target $localIP --syn-flood --udp-flood --count 250 --rate 200
    }
    default {
        Write-Host "Invalid choice, running SYN Flood..." -ForegroundColor Yellow
        & $pythonPath run_attack.py --target $localIP --syn-flood --count 300 --rate 200
    }
}

Write-Host ""
Write-Host "[OK] Attack simulation completed" -ForegroundColor Green
Write-Host ""

# Step 6: Check alerts
Write-Host "Checking for alerts..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $alertResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/alerts" -UseBasicParsing
    $alertData = $alertResponse.Content | ConvertFrom-Json
    $alertCount = $alertData.total

    if ($alertCount -gt 0) {
        Write-Host ""
        Write-Host "SUCCESS! $alertCount alert(s) generated" -ForegroundColor Green
        Write-Host ""
        Write-Host "Sample alerts:" -ForegroundColor Cyan
        foreach ($alert in $alertData.alerts | Select-Object -First 5) {
            $confidence = [math]::Round($alert.confidence * 100, 1)
            Write-Host "  - $($alert.threat) | $($alert.src) -> $($alert.dst) | Confidence: $confidence%" -ForegroundColor White
        }
    } else {
        Write-Host ""
        Write-Host "No alerts generated yet." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "This could mean:" -ForegroundColor White
        Write-Host "  1. ML model classified traffic as benign" -ForegroundColor White
        Write-Host "  2. Not enough packets captured yet (try running attack again)" -ForegroundColor White
        Write-Host "  3. Network adapter not capturing properly" -ForegroundColor White
        Write-Host ""
        Write-Host "Check server terminal for detection messages" -ForegroundColor Cyan
    }
} catch {
    Write-Host "[!] Could not fetch alerts: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View dashboard: http://localhost:8000" -ForegroundColor Blue
Write-Host "View statistics: http://localhost:8000/api/statistics/realtime" -ForegroundColor Blue
Write-Host ""

# Disable test mode
Write-Host "Restoring normal detection mode..." -ForegroundColor Yellow
try {
    $body = @{
        mode = "threshold"
    } | ConvertTo-Json

    Invoke-WebRequest -Uri "http://localhost:8000/api/detection/mode" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing -ErrorAction SilentlyContinue
    Write-Host "[OK] Normal detection mode restored" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Could not restore detection mode" -ForegroundColor Yellow
}

Write-Host ""
pause
