# Complete workflow to test attacks on external IP and view on dashboard
# Windows PowerShell version

# Check for administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "External IP Attack Testing Workflow" -ForegroundColor Cyan
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

# Step 1: Get external IP
Write-Host "[Step 1/6] Detecting external IP address..." -ForegroundColor Yellow

# Get active network adapter IP (excluding loopback)
$externalIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.IPAddress -ne "127.0.0.1" -and $_.PrefixOrigin -ne "WellKnown"
} | Select-Object -First 1).IPAddress

if (-not $externalIP) {
    Write-Host "[!] Could not detect external IP automatically" -ForegroundColor Red
    Write-Host "Please check your IP with: ipconfig" -ForegroundColor Yellow
    $externalIP = Read-Host "Enter your IP address manually"
}

Write-Host "[OK] External IP detected: $externalIP" -ForegroundColor Green
Write-Host ""

# Step 2: Configure system for external monitoring
Write-Host "[Step 2/6] Configuring system for external monitoring..." -ForegroundColor Yellow

# Get network interface name
$adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.InterfaceDescription -notmatch "Loopback" } | Select-Object -First 1
$interfaceName = $adapter.Name

Write-Host "  Active network interface: $interfaceName" -ForegroundColor Cyan

# Update config.yaml
if (Test-Path "config.yaml") {
    $config = Get-Content "config.yaml" -Raw
    if ($config -match "interface:\s*eth0" -or $config -match "interface:\s*lo") {
        Write-Host "  Updating config.yaml with Windows interface..." -ForegroundColor Cyan
        $config = $config -replace "interface:\s*\w+", "interface: $interfaceName"
        Set-Content "config.yaml" -Value $config
        Write-Host "[OK] Updated config.yaml" -ForegroundColor Green
    } else {
        Write-Host "[OK] Config already configured" -ForegroundColor Green
    }
} else {
    Write-Host "[WARNING] config.yaml not found" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Check if server is running
Write-Host "[Step 3/6] Checking if server is running..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/network/status" -UseBasicParsing -ErrorAction SilentlyContinue
    $status = $response.Content | ConvertFrom-Json

    Write-Host "[OK] Server is running and monitoring: $($status.monitoring_interface)" -ForegroundColor Green
    $serverRunning = $true
} catch {
    Write-Host "[!] Server is not running" -ForegroundColor Red
    $serverRunning = $false
}

if (-not $serverRunning) {
    Write-Host ""
    Write-Host "Please start the server in another terminal:" -ForegroundColor Blue
    Write-Host "  start_server.bat" -ForegroundColor Green
    Write-Host ""
    Write-Host "Or use PowerShell:" -ForegroundColor Blue
    Write-Host "  .\START_LIVE_MONITORING.ps1" -ForegroundColor Green
    Write-Host ""
    Read-Host "Press Enter once the server is running"

    # Verify server is now accessible
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:8000/api/network/status" -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Host "[!] Server is still not accessible. Please check the server terminal." -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host "[OK] Server is ready" -ForegroundColor Green
Write-Host ""

# Step 4: Open dashboard
Write-Host "[Step 4/6] Opening dashboard in browser..." -ForegroundColor Yellow
Write-Host "Dashboard URL: http://localhost:8000" -ForegroundColor Blue
Write-Host ""

Start-Process "http://localhost:8000"

Write-Host "[OK] Dashboard opened in browser" -ForegroundColor Green
Write-Host "    Navigate to the Alerts tab to see real-time detections" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter once you have the dashboard open"
Write-Host ""

# Step 5: Run attack simulation
Write-Host "[Step 5/6] Running attack simulation..." -ForegroundColor Yellow
Write-Host "Target: $externalIP" -ForegroundColor Blue
Write-Host ""

Write-Host "Which attack would you like to simulate?"
Write-Host "  1) SYN Flood (DDoS simulation)"
Write-Host "  2) UDP Flood"
Write-Host "  3) Port Scan"
Write-Host "  4) All attacks (comprehensive test)"
Write-Host ""
$attackChoice = Read-Host "Select (1-4) [default: 1]"
if ([string]::IsNullOrWhiteSpace($attackChoice)) {
    $attackChoice = "1"
}

Write-Host ""
Write-Host "Launching attack simulation..." -ForegroundColor Blue
Write-Host "Watch the dashboard for alerts!" -ForegroundColor Yellow
Write-Host ""

# Determine which Python to use
if (Test-Path "..\myvenv\Scripts\python.exe") {
    $pythonPath = "..\myvenv\Scripts\python.exe"
} elseif (Test-Path "..\venv\Scripts\python.exe") {
    $pythonPath = "..\venv\Scripts\python.exe"
} else {
    $pythonPath = "python"
}

# Set PYTHONPATH to include project root
$projectRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = $projectRoot

switch ($attackChoice) {
    "1" {
        Write-Host "Running SYN Flood attack..." -ForegroundColor Cyan
        & $pythonPath run_attack.py --target $externalIP --syn-flood --count 300 --rate 200
    }
    "2" {
        Write-Host "Running UDP Flood attack..." -ForegroundColor Cyan
        & $pythonPath run_attack.py --target $externalIP --udp-flood --count 300 --rate 200
    }
    "3" {
        Write-Host "Running Port Scan..." -ForegroundColor Cyan
        & $pythonPath run_attack.py --target $externalIP --port-scan --ports 75-100
    }
    "4" {
        Write-Host "Running all attacks..." -ForegroundColor Cyan
        & $pythonPath run_attack.py --target $externalIP --syn-flood --udp-flood --count 250 --rate 200
    }
    default {
        Write-Host "Invalid choice, running SYN Flood..." -ForegroundColor Yellow
        & $pythonPath run_attack.py --target $externalIP --syn-flood --count 300 --rate 200
    }
}

Write-Host ""
Write-Host "[OK] Attack simulation completed" -ForegroundColor Green
Write-Host ""

# Step 6: Verify alerts
Write-Host "[Step 6/6] Checking for alerts..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $alertResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/alerts" -UseBasicParsing
    $alertData = $alertResponse.Content | ConvertFrom-Json
    $alertCount = $alertData.total

    if ($alertCount -gt 0) {
        Write-Host "[OK] SUCCESS! $alertCount alert(s) generated" -ForegroundColor Green
        Write-Host ""
        Write-Host "View alerts:" -ForegroundColor Blue
        Write-Host "  - Dashboard: http://localhost:8000 (Alerts tab)"
        Write-Host "  - API: http://localhost:8000/api/alerts"
        Write-Host "  - Real-time stats: http://localhost:8000/api/statistics/realtime"
        Write-Host ""

        Write-Host "Sample alerts:" -ForegroundColor Blue
        foreach ($alert in $alertData.alerts | Select-Object -First 3) {
            $confidence = [math]::Round($alert.confidence * 100, 1)
            Write-Host "  - $($alert.threat) from $($alert.src) to $($alert.dst) (Confidence: $confidence%)"
        }
    } else {
        Write-Host "[!] No alerts generated" -ForegroundColor Red
        Write-Host ""
        Write-Host "Possible reasons:"
        Write-Host "  1. Network adapter not capturing properly"
        Write-Host "  2. Confidence threshold too high (check config.yaml)"
        Write-Host "  3. Server not capturing packets on correct interface"
        Write-Host ""
        Write-Host "Check server terminal for debug messages"
    }
} catch {
    Write-Host "[!] Could not fetch alerts: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing workflow complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  - View alerts on dashboard: http://localhost:8000"
Write-Host "  - Run more tests: .\run_anomaly_test.bat"
Write-Host "  - Check statistics: http://localhost:8000/api/statistics/realtime"
Write-Host ""

pause
