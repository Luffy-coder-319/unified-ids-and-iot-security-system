# Unified IDS and IoT Security System - Complete Startup Script
# This script starts the entire system with proper admin privileges

param(
    [switch]$BuildFrontend = $false,
    [switch]$SkipMonitoring = $false
)

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

Clear-Host
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "  UNIFIED IDS AND IOT SECURITY SYSTEM - COMPLETE STARTUP" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check for Administrator privileges
Write-Info "[Step 1/6] Checking Administrator privileges..."
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Warning "[!] This script requires Administrator privileges for full functionality"
    Write-Warning "    (Live network monitoring requires admin access)"
    Write-Host ""
    Write-Info "Attempting to restart with Administrator privileges..."
    Write-Host ""

    # Restart script with admin privileges, preserving working directory
    $scriptPath = $PSCommandPath
    $workingDir = $PSScriptRoot
    $arguments = "-NoProfile -ExecutionPolicy Bypass -Command `"Set-Location '$workingDir'; & '$scriptPath'"
    if ($BuildFrontend) { $arguments += " -BuildFrontend" }
    if ($SkipMonitoring) { $arguments += " -SkipMonitoring" }
    $arguments += "`""

    Start-Process powershell.exe -ArgumentList $arguments -Verb RunAs
    exit
}

Write-Success "[OK] Running with Administrator privileges"
Write-Host ""

# Ensure we're in the correct directory (project root)
$projectRoot = $PSScriptRoot
if (-not $projectRoot) {
    $projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}
Set-Location $projectRoot
Write-Info "[INFO] Working directory: $projectRoot"
Write-Host ""

# Step 2: Check Python installation
Write-Info "[Step 2/6] Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "[OK] $pythonVersion detected"
} catch {
    Write-Error "[ERROR] Python is not installed or not in PATH!"
    Write-Host ""
    Write-Warning "Please install Python 3.8+ from: https://www.python.org/downloads/"
    Write-Warning "Make sure to check 'Add Python to PATH' during installation"
    pause
    exit 1
}
Write-Host ""

# Step 3: Check Virtual Environment
Write-Info "[Step 3/6] Checking virtual environment..."
$venvPath = "myvenv"

if (Test-Path "myvenv\Scripts\python.exe") {
    Write-Success "[OK] Using myvenv virtual environment"

    # Verify dependencies are installed
    Write-Info "Verifying dependencies..."
    $pipList = & "myvenv\Scripts\pip.exe" list 2>&1
    if ($pipList -match "fastapi" -and $pipList -match "uvicorn") {
        Write-Success "[OK] Dependencies verified"
    } else {
        Write-Warning "[!] Some dependencies may be missing. Installing..."
        & "myvenv\Scripts\pip.exe" install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Success "[OK] Dependencies installed"
        } else {
            Write-Warning "[WARNING] Some packages may have failed to install"
        }
    }
} else {
    Write-Error "[ERROR] Virtual environment 'myvenv' not found!"
    Write-Info "Please create it first with:"
    Write-Info "  python -m venv myvenv"
    Write-Info "  myvenv\Scripts\pip install -r requirements.txt"
    Write-Host ""
    Write-Warning "Or use the windows_quick_start.bat script to set up automatically"
    pause
    exit 1
}
Write-Host ""

# Step 4: Build Frontend (Optional)
Write-Info "[Step 4/6] Checking frontend..."
if ($BuildFrontend) {
    Write-Info "Building frontend dashboard..."

    # Check Node.js
    try {
        $nodeVersion = node --version 2>&1
        Write-Success "[OK] Node.js $nodeVersion detected"
    } catch {
        Write-Error "[ERROR] Node.js is not installed!"
        Write-Warning "Please install Node.js from: https://nodejs.org/"
        Write-Warning "Frontend build skipped. API will still work."
        pause
    }

    if (Test-Path "src\frontend\package.json") {
        Push-Location src\frontend

        Write-Info "Installing npm dependencies..."
        npm install

        if ($LASTEXITCODE -eq 0) {
            Write-Info "Building production bundle..."
            npm run build

            if ($LASTEXITCODE -eq 0) {
                Write-Success "[OK] Frontend built successfully"
            } else {
                Write-Warning "[WARNING] Frontend build failed, but API will still work"
            }
        } else {
            Write-Warning "[WARNING] npm install failed, but API will still work"
        }

        Pop-Location
    }
} else {
    Write-Info "Frontend build skipped (use -BuildFrontend flag to build)"
    if (Test-Path "src\frontend\dist") {
        Write-Success "[OK] Frontend already built"
    } else {
        Write-Warning "[!] Frontend not built. Dashboard may not work."
        Write-Info "    Run: .\START_SYSTEM.ps1 -BuildFrontend"
    }
}
Write-Host ""

# Step 5: Check Configuration
Write-Info "[Step 5/6] Checking configuration..."

if (Test-Path "config.yaml") {
    Write-Success "[OK] Configuration file found"

    # Get network interface
    $adapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.InterfaceDescription -notmatch "Loopback" } | Select-Object -First 1
    if ($adapter) {
        Write-Info "    Active network interface: $($adapter.Name)"
        Write-Info "    You can change this in config.yaml if needed"
    }
} else {
    Write-Warning "[WARNING] config.yaml not found - using defaults"
}
Write-Host ""

# Step 6: Start the System
Write-Info "[Step 6/6] Starting system components..."
Write-Host ""

Write-Host "===============================================================================" -ForegroundColor Green
Write-Host "  SYSTEM STARTUP" -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host ""

# Display startup options
Write-Info "Choose startup mode:"
Write-Host "  1) Full System (API Server + Live Monitoring)"
Write-Host "  2) API Server Only (No live capture)"
Write-Host "  3) Live Monitoring Only (Requires API running separately)"
Write-Host ""

if ($SkipMonitoring) {
    $choice = "2"
    Write-Info "Auto-selected: API Server Only (SkipMonitoring flag set)"
} else {
    $choice = Read-Host "Enter choice (1-3) [default: 1]"
    if ([string]::IsNullOrWhiteSpace($choice)) {
        $choice = "1"
    }
}

Write-Host ""

switch ($choice) {
    "1" {
        Write-Success "==> Starting Full System (API + Live Monitoring)"
        Write-Host ""
        Write-Info "Dashboard: http://localhost:8000"
        Write-Info "API: http://localhost:8000/api/"
        Write-Info "API Docs: http://localhost:8000/docs"
        Write-Host ""
        Write-Warning "This will open TWO windows:"
        Write-Warning "  1. API Server (separate window)"
        Write-Warning "  2. Live Monitoring (this window)"
        Write-Warning ""
        Write-Warning "Close BOTH windows to stop the system completely"
        Write-Host ""

        # Set environment variables
        $env:TF_CPP_MIN_LOG_LEVEL = "3"
        $env:TF_ENABLE_ONEDNN_OPTS = "0"

        # Start API server in a new window
        Write-Info "Starting API server in separate window..."
        $apiProcess = Start-Process powershell.exe -ArgumentList @(
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-Command",
            "Set-Location '$projectRoot'; `$env:TF_CPP_MIN_LOG_LEVEL='3'; `$env:TF_ENABLE_ONEDNN_OPTS='0'; Write-Host '===============================================================================' -ForegroundColor Green; Write-Host '  API SERVER - Unified IDS and IoT Security System' -ForegroundColor Green; Write-Host '===============================================================================' -ForegroundColor Green; Write-Host ''; Write-Host 'Dashboard: http://localhost:8000' -ForegroundColor Cyan; Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor Cyan; Write-Host ''; Write-Host 'Press Ctrl+C or close this window to stop the API server' -ForegroundColor Yellow; Write-Host ''; & 'myvenv\Scripts\python.exe' -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000; Write-Host ''; Write-Host 'API Server stopped. Press any key to close...' -ForegroundColor Red; `$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')"
        ) -PassThru

        # Wait for API to start and check if it's ready
        Write-Info "Waiting for API server to initialize (loading models, this may take 10-20 seconds)..."
        Start-Sleep -Seconds 3

        # Try to open the dashboard in the default browser
        try {
            $testUrl = "http://localhost:8000"
            $maxAttempts = 30
            $opened = $false
            Write-Host "Checking server status" -NoNewline
            for ($i = 1; $i -le $maxAttempts; $i++) {
                try {
                    $response = Invoke-WebRequest -Uri $testUrl -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
                    if (-not $opened) {
                        Write-Host ""
                        Write-Success "[OK] API server is ready!"
                        Write-Info "Opening dashboard in browser..."
                        Start-Process $testUrl
                        $opened = $true
                    }
                    break
                } catch {
                    if ($i -eq $maxAttempts) {
                        Write-Host ""
                        Write-Warning "[WARNING] Could not verify API is ready after $maxAttempts attempts"
                        Write-Info "Check the API Server window for errors, or try opening http://localhost:8000 manually"
                    } else {
                        Write-Host "." -NoNewline
                    }
                    Start-Sleep -Seconds 1
                }
            }
            if (-not ($i -eq $maxAttempts)) {
                Write-Host ""
            }
        } catch {
            Write-Host ""
            Write-Warning "[WARNING] Could not open browser automatically"
            Write-Info "Please open http://localhost:8000 manually"
        }

        # Start live monitoring
        Write-Host ""
        Write-Info "Starting live network monitoring in THIS window..."
        Write-Host ""
        & "myvenv\Scripts\python.exe" start_live_monitoring.py

        # When monitoring stops, ask if user wants to stop API server
        Write-Host ""
        Write-Warning "Live monitoring stopped."
        Write-Info "The API server is still running in the other window."
        Write-Info "To stop it, close the API Server window or press Ctrl+C in that window."
        Write-Host ""
    }

    "2" {
        Write-Success "==> Starting API Server Only"
        Write-Host ""
        Write-Info "Dashboard: http://localhost:8000"
        Write-Info "API: http://localhost:8000/api/"
        Write-Info "API Docs: http://localhost:8000/docs"
        Write-Host ""
        Write-Info "Note: Live packet capture is DISABLED"
        Write-Info "      System will show alerts from logs only"
        Write-Host ""
        Write-Warning "Press Ctrl+C to stop the server"
        Write-Host ""

        # Set environment variables
        $env:TF_CPP_MIN_LOG_LEVEL = "3"
        $env:TF_ENABLE_ONEDNN_OPTS = "0"

        # Open browser in background after a delay
        Start-Job -ScriptBlock {
            Start-Sleep -Seconds 3
            # Try to verify server is up before opening (up to 30 seconds)
            for ($i = 1; $i -le 30; $i++) {
                try {
                    $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
                    Start-Process "http://localhost:8000"
                    break
                } catch {
                    Start-Sleep -Seconds 1
                }
            }
        } | Out-Null

        Write-Info "Dashboard will open automatically once the server is ready (this may take 10-20 seconds)..."
        Write-Host ""

        # Start API server
        & "myvenv\Scripts\python.exe" -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
    }

    "3" {
        Write-Success "==> Starting Live Monitoring Only"
        Write-Host ""
        Write-Warning "Note: API server must be running separately for dashboard to work"
        Write-Info "      Run 'start_server.bat' in another terminal if needed"
        Write-Host ""
        Write-Warning "Press Ctrl+C to stop monitoring"
        Write-Host ""

        & "myvenv\Scripts\python.exe" start_live_monitoring.py
    }

    default {
        Write-Error "[ERROR] Invalid choice!"
        pause
        exit 1
    }
}

Write-Host ""
Write-Info "[INFO] System stopped"
Write-Host ""
Write-Success "Thank you for using Unified IDS and IoT Security System!"
pause
