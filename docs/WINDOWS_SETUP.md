# Windows Setup Guide - IoT Security System

Complete guide to install and run the Unified IDS and IoT Security System on Windows.

## Prerequisites

### Required Software

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

2. **Npcap** (for packet capture)
   - Download from: https://npcap.com/#download
   - ✅ Install with "WinPcap API-compatible mode" enabled
   - Required for network packet sniffing

3. **Git** (optional, for cloning)
   - Download from: https://git-scm.com/download/win

### Verify Installation

Open PowerShell or Command Prompt and verify:

```powershell
python --version
# Should show: Python 3.8.x or higher
```

---

## Installation Steps

### Step 1: Clone or Download the Project

**Option A: Using Git**
```powershell
git clone <repository-url>
cd unified-ids-and-iot-security-system
```

**Option B: Download ZIP**
- Download and extract the project ZIP file
- Open PowerShell in the project folder

### Step 2: Create Virtual Environment

```powershell
python -m venv myvenv
```

### Step 3: Activate Virtual Environment

```powershell
.\myvenv\Scripts\Activate.ps1
```

**Note:** If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Install Dependencies

```powershell
pip install -r requirements.txt
```

This will install all required packages including:
- TensorFlow (deep learning)
- Scapy (packet capture)
- FastAPI (web server)
- And more...

### Step 5: Configure Network Interface

Check your network adapter name:
```powershell
ipconfig
# Look for your active adapter (e.g., "Wi-Fi", "Ethernet")
```

Edit [config.yaml](config.yaml:5) and set your interface:
```yaml
network:
  interface: WiFi  # Change to your adapter name
```

Common Windows adapter names:
- `WiFi` or `Wi-Fi`
- `Ethernet`
- `Local Area Connection`

---

## Running the System

### Option 1: Quick Start (No Admin Required)

**Test Mode - Works without Administrator privileges:**

1. **Start the API server** (Terminal 1):
```powershell
.\myvenv\Scripts\Activate.ps1
python -m uvicorn src.api.main:app --reload
```

Or simply double-click: [start_server.bat](start_server.bat)

2. **View the dashboard**:
   - Open browser: http://localhost:8000
   - View alerts: http://localhost:8000/api/alerts

This mode works with pre-generated alerts or simulation data.

---

### Option 2: Live Network Monitoring (Administrator Required)

**Real Packet Capture - Requires Administrator privileges:**

#### Method A: Using PowerShell Script

1. **Right-click** [START_LIVE_MONITORING.ps1](START_LIVE_MONITORING.ps1)
2. Select **"Run with PowerShell as Administrator"**
3. Follow the prompts

#### Method B: Manual Start

1. Open PowerShell **as Administrator**
2. Navigate to project folder
3. Run:
```powershell
.\myvenv\Scripts\Activate.ps1
python start_live_monitoring.py
```

**Expected Output:**
```
===============================================================================
  LIVE NETWORK MONITORING - IoT Security System
===============================================================================

[OK] Running with Administrator privileges
[INFO] Configuration loaded:
  Network Interface: WiFi
  Capture Filter: All traffic
[INFO] Starting packet capture on: WiFi
[OK] Live monitoring ACTIVE!
```

---

## Testing the System

### Test 1: View Existing Alerts

```powershell
# Open browser
http://localhost:8000/api/alerts
```

### Test 2: Generate Test Alerts

Run in a separate terminal (Administrator required):
```powershell
.\myvenv\Scripts\Activate.ps1
python -m tests.generate_anomalies --syn-flood --count 100
```

Or double-click: [run_anomaly_test.bat](run_anomaly_test.bat) (as Administrator)

### Test 3: Complete Attack Simulation

**Right-click and run as Administrator:**
```powershell
.\test_external_attacks.ps1
```

This guided workflow will:
1. Detect your IP address
2. Configure the system
3. Verify server is running
4. Open the dashboard
5. Run attack simulations
6. Verify alerts are generated

---

## Troubleshooting

### Issue 1: "python: command not found"

**Solution:** Reinstall Python and check "Add Python to PATH"

Verify:
```powershell
python --version
```

### Issue 2: "Execution Policy Error"

**Error:**
```
cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: "Address already in use"

**Error:**
```
[ERROR] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Solution:** Kill the process using port 8000:
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue 4: "Permission denied" for packet capture

**Error:**
```
PermissionError: [WinError 5] Access is denied
```

**Solution:**
- Install Npcap from https://npcap.com/#download
- Run script as Administrator
- Verify "WinPcap API-compatible mode" is enabled in Npcap

### Issue 5: No packets captured

**Possible causes:**
1. Wrong network interface name
2. Npcap not installed
3. Not running as Administrator

**Solution:**
```powershell
# List available interfaces
python -c "from scapy.all import conf; print([i for i in conf.ifaces.data.keys()])"

# Update config.yaml with correct interface name
```

### Issue 6: TensorFlow warnings

**Warning messages like:**
```
tensorflow/core/platform/cpu_feature_guard.cc
```

**Solution:** These are informational and can be ignored. To suppress:
```powershell
$env:TF_CPP_MIN_LOG_LEVEL="3"
```

Or they're already suppressed in [start_server.bat](start_server.bat)

---

## Windows-Specific Features

### Batch Scripts (Double-click to run)

- [start_server.bat](start_server.bat) - Start API server
- [run_anomaly_test.bat](run_anomaly_test.bat) - Run tests (Admin required)

### PowerShell Scripts

- [START_LIVE_MONITORING.ps1](START_LIVE_MONITORING.ps1) - Live monitoring
- [test_external_attacks.ps1](test_external_attacks.ps1) - Attack simulation

### Network Interface Detection

Windows uses different interface names than Linux:
- Linux: `eth0`, `wlan0`, `lo`
- Windows: `WiFi`, `Ethernet`, `Local Area Connection`

The system automatically detects and adapts to Windows interfaces.

---

## File Structure

```
unified-ids-and-iot-security-system/
├── config.yaml                    # Configuration file
├── start_server.bat               # Windows batch script
├── START_LIVE_MONITORING.ps1      # PowerShell monitoring script
├── run_anomaly_test.bat           # Windows test script
├── test_external_attacks.ps1      # Attack simulation script
├── myvenv/                        # Virtual environment
├── src/
│   ├── api/                       # FastAPI backend
│   ├── models/                    # ML models
│   ├── network/                   # Packet capture
│   └── utils/                     # Utilities
├── logs/
│   └── alerts.jsonl               # Alert logs
└── trained_models/                # Pre-trained models
```

---

## Next Steps

### 1. Basic Usage
```powershell
# Start server
.\start_server.bat

# Open dashboard
http://localhost:8000
```

### 2. Live Monitoring
```powershell
# Right-click and "Run as Administrator"
.\START_LIVE_MONITORING.ps1
```

### 3. Run Tests
```powershell
# Right-click and "Run as Administrator"
.\run_anomaly_test.bat
```

### 4. Advanced Features

See documentation:
- [README.md](README.md) - Overview and features
- [QUICK_START.md](docs/QUICK_START.md) - Quick start guide
- [COMPLETE_TESTING_GUIDE.md](docs/COMPLETE_TESTING_GUIDE.md) - Comprehensive testing

---

## API Endpoints

All accessible at http://localhost:8000

### Core Endpoints
- `GET /api/alerts` - Get all alerts
- `GET /api/statistics/summary` - Get statistics
- `GET /api/flows` - Get network flows
- `WebSocket /ws/alerts` - Real-time alerts

### Alert Management
- `GET /api/alerts/{id}` - Get specific alert
- `POST /api/alerts/{id}/acknowledge` - Acknowledge alert
- `GET /api/alerts/stats/unacknowledged` - Unacknowledged count

### Response Actions
- `POST /api/response/block-ip` - Block IP address
- `GET /api/response/blocked-ips` - Get blocked IPs

Full API docs: http://localhost:8000/docs

---

## System Requirements

### Minimum Requirements
- Windows 10 or later
- Python 3.8+
- 4 GB RAM
- 2 GB disk space
- Network adapter (WiFi or Ethernet)

### Recommended Requirements
- Windows 11
- Python 3.10+
- 8 GB RAM
- 5 GB disk space
- Dedicated network adapter

---

## Security Notes

### Administrator Privileges

Administrator (elevated) privileges are required for:
- Real-time packet capture
- Network interface access
- Generating test traffic

**Not required for:**
- API server (simulation mode)
- Viewing pre-generated alerts
- Dashboard access

### Firewall

Windows Firewall may prompt for permissions:
- ✅ Allow Python (python.exe)
- ✅ Allow uvicorn server
- ✅ Allow network capture

---

## Support

### Common Issues
- Check [Troubleshooting](#troubleshooting) section above
- Review error messages in terminal
- Check logs in `logs/` folder

### Documentation
- [README.md](README.md) - Main documentation
- [QUICK_START.md](docs/QUICK_START.md) - Quick start
- API docs: http://localhost:8000/docs

### Testing
- Run system tests: `python -m pytest tests/`
- Check network status: http://localhost:8000/api/network/status

---

## Success!

If you can access http://localhost:8000 and see the dashboard, your system is working!

**Next:** Try generating some test alerts:
```powershell
# Right-click and run as Administrator
.\run_anomaly_test.bat
```

Then view them at: http://localhost:8000/api/alerts

**Happy monitoring! 🛡️**
