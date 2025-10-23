# System Startup Guide

Complete guide for starting the Unified IDS and IoT Security System on Windows.

## 🚀 Quick Start Options

### Option 1: Full System (Recommended)

**Double-click:** [START_SYSTEM.bat](../START_SYSTEM.bat)

- ✅ Automatically requests Administrator privileges
- ✅ Checks all dependencies
- ✅ Lets you choose startup mode
- ✅ Starts API + Live Monitoring

---

### Option 2: Quick Start (No Admin)

**Double-click:** [QUICK_START.bat](../QUICK_START.bat)

- ✅ No Administrator required
- ✅ API Server only
- ✅ Shows historical alerts
- ❌ No live packet capture

---

### Option 3: Full Monitoring Only

**Double-click:** [FULL_START.bat](../FULL_START.bat)

- ✅ Automatically elevates to Administrator
- ✅ Full live monitoring
- ✅ Real-time packet capture
- ✅ API + Monitoring combined

---

## 📋 Startup Scripts Explained

### START_SYSTEM.bat / START_SYSTEM.ps1

**The master startup script** - handles everything automatically.

**Features:**
- ✅ Admin privilege checking and elevation
- ✅ Python installation verification
- ✅ Virtual environment creation/detection
- ✅ Dependency installation (if needed)
- ✅ Frontend build option
- ✅ Configuration validation
- ✅ Multiple startup modes

**Usage:**
```batch
# Simple - just double-click
START_SYSTEM.bat

# Or with PowerShell directly
.\START_SYSTEM.ps1

# Build frontend too
.\START_SYSTEM.ps1 -BuildFrontend

# Skip monitoring (API only)
.\START_SYSTEM.ps1 -SkipMonitoring
```

**Startup Modes:**

1. **Full System** (API + Live Monitoring)
   - Best for production use
   - Captures real network traffic
   - Detects threats in real-time
   - Requires Administrator

2. **API Server Only**
   - No admin required
   - Shows historical data
   - Dashboard works
   - No live capture

3. **Live Monitoring Only**
   - Monitoring without API
   - Requires API running separately
   - Advanced use case

---

### QUICK_START.bat

**Fastest way to start** - no prompts, no admin.

**Use when:**
- Testing the dashboard
- Viewing historical alerts
- Don't need live monitoring
- Quick demo

**What it does:**
```
1. Checks virtual environment
2. Starts API server immediately
3. Opens on http://localhost:8000
```

**Limitations:**
- ❌ No live packet capture
- ❌ No real-time threat detection
- ✅ Dashboard still works
- ✅ Historical alerts visible

---

### FULL_START.bat

**One-click full system** - automatically elevates.

**Use when:**
- Want full monitoring
- Don't want to choose options
- Production deployment

**What it does:**
```
1. Requests Administrator (UAC prompt)
2. Starts full system automatically
3. API + Live Monitoring together
```

---

## 🔧 Step-by-Step Startup Process

### First Time Setup

**Step 1: Run START_SYSTEM.bat**

Double-click `START_SYSTEM.bat` - it will:

1. ✅ Request Administrator privileges (click "Yes" on UAC prompt)
2. ✅ Check Python is installed
3. ✅ Create virtual environment (myvenv)
4. ✅ Install all dependencies automatically
5. ✅ Check configuration
6. ✅ Show startup options

**Step 2: Choose Startup Mode**

```
Choose startup mode:
  1) Full System (API Server + Live Monitoring)
  2) API Server Only (No live capture)
  3) Live Monitoring Only (Requires API running separately)

Enter choice (1-3) [default: 1]:
```

**Recommended:** Press Enter (defaults to Full System)

**Step 3: System Starts**

```
Dashboard: http://localhost:8000
API: http://localhost:8000/api/
API Docs: http://localhost:8000/docs

[OK] API server starting...
[+] Analyzer running on WiFi
[OK] Live monitoring ACTIVE!
```

**Step 4: Access Dashboard**

Open browser: **http://localhost:8000**

---

### Subsequent Startups

After first setup, simply:

**Double-click:** `START_SYSTEM.bat` or `FULL_START.bat`

Everything is already configured!

---

## 📊 What Gets Started

### Full System Mode:

```
┌─────────────────────────────────────┐
│  API Server (Port 8000)             │
│  - REST API endpoints               │
│  - WebSocket connections            │
│  - Dashboard serving                │
│  - Status: http://localhost:8000    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Live Network Monitoring            │
│  - Packet capture (Npcap/Scapy)    │
│  - ML/DL threat detection           │
│  - Real-time analysis               │
│  - Alert generation                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Dashboard (Frontend)               │
│  - Network flows visualization      │
│  - Real-time alerts                 │
│  - IoT device detection             │
│  - Statistics & metrics             │
└─────────────────────────────────────┘
```

### API Only Mode:

```
┌─────────────────────────────────────┐
│  API Server (Port 8000)             │
│  - REST API endpoints               │
│  - Historical data access           │
│  - Dashboard serving                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Dashboard (Frontend)               │
│  - Shows historical alerts          │
│  - Displays saved flows             │
│  - No live updates                  │
└─────────────────────────────────────┘
```

---

## 🛠️ Advanced Options

### Build Frontend During Startup

```powershell
.\START_SYSTEM.ps1 -BuildFrontend
```

This will:
1. Check Node.js is installed
2. Run `npm install` in src/frontend
3. Build production bundle
4. Then start the system

**When to use:**
- First time setup
- After frontend code changes
- Dashboard not displaying correctly

---

### API Server Only Mode

```powershell
.\START_SYSTEM.ps1 -SkipMonitoring
```

Or just run:
```batch
QUICK_START.bat
```

**Use cases:**
- Development/testing
- Don't have admin access
- Only need API
- Viewing historical data

---

### Custom Configuration

Edit [config.yaml](../config.yaml) before starting:

```yaml
network:
  interface: WiFi  # Change to your adapter name

detection:
  confidence_threshold: 0.90  # Adjust sensitivity
  min_packet_threshold: 50

response_actions:
  enabled: false  # Enable auto-blocking
  auto_block_high_severity: false
```

---

## ❌ Troubleshooting

### Issue 1: "Python is not installed"

**Error:**
```
[ERROR] Python is not installed or not in PATH!
```

**Solution:**
1. Install Python 3.8+ from https://www.python.org/downloads/
2. ✅ CHECK "Add Python to PATH" during installation
3. Restart terminal
4. Run `START_SYSTEM.bat` again

---

### Issue 2: "Failed to install dependencies"

**Error:**
```
[ERROR] Failed to install dependencies!
```

**Solutions:**

1. **Check internet connection** (pip needs to download packages)

2. **Update pip:**
   ```powershell
   python -m pip install --upgrade pip
   ```

3. **Manual installation:**
   ```powershell
   .\myvenv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Try installing one by one:**
   ```powershell
   pip install fastapi uvicorn
   pip install scapy
   pip install tensorflow
   ```

---

### Issue 3: "Address already in use"

**Error:**
```
[ERROR] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Solution:**

**Kill the process using port 8000:**
```powershell
# Find process
netstat -ano | findstr :8000

# Kill it (replace PID with actual number)
taskkill /PID <PID> /F
```

**Or use a different port:**
Edit config.yaml:
```yaml
app:
  port: 8001  # Change from 8000
```

---

### Issue 4: "Frontend not built"

**Warning:**
```
[WARNING] Frontend not built. Dashboard may not work.
```

**Solution:**

**Option A: Use build flag:**
```powershell
.\START_SYSTEM.ps1 -BuildFrontend
```

**Option B: Build manually:**
```batch
build_frontend.bat
```

**Option C: Build with npm:**
```powershell
cd src\frontend
npm install
npm run build
```

---

### Issue 5: "Administrator privileges required"

**Error:**
```
[ERROR] Administrator privileges required!
```

**Solutions:**

1. **Use START_SYSTEM.bat** (auto-elevates)

2. **Right-click START_SYSTEM.ps1** → "Run with PowerShell as Administrator"

3. **Or use API-only mode** (no admin needed):
   ```batch
   QUICK_START.bat
   ```

---

### Issue 6: "No network flows showing"

**Problem:** Dashboard shows "No flows yet"

**This is NORMAL!** See [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md) for details.

**Quick solutions:**

1. **Generate network activity:**
   - Browse websites
   - Run: `ping google.com -n 100`
   - Download a file

2. **Check if monitoring is active:**
   ```
   http://localhost:8000/api/network/status
   ```

3. **View flows via API:**
   ```
   http://localhost:8000/api/flows
   ```

4. **Lower thresholds temporarily** (in config.yaml):
   ```yaml
   detection:
     confidence_threshold: 0.80  # Lower = more sensitive
     min_packet_threshold: 20     # Lower = see more flows
   ```

---

## 🔐 Security Considerations

### Administrator Privileges

**Required for:**
- Live packet capture (Npcap/WinPcap access)
- Network interface monitoring
- Automated IP blocking (if enabled)

**NOT required for:**
- API server
- Dashboard viewing
- Historical data access
- Configuration changes

### Firewall Permissions

Windows may prompt for firewall access:
- ✅ **Allow** Python (python.exe)
- ✅ **Allow** Uvicorn server
- ✅ **Allow** Private networks
- ❌ **Block** Public networks (recommended)

### Auto-Blocking Safety

By default, auto-blocking is **DISABLED**:

```yaml
response_actions:
  enabled: false
  auto_block_high_severity: false
```

**Before enabling:**
1. Monitor system for 24-48 hours
2. Verify no false positives
3. Test with attack simulations
4. See [docs/FALSE_POSITIVES_GUIDE.md](FALSE_POSITIVES_GUIDE.md)

---

## 📈 Monitoring & Logs

### Console Output

**Startup messages:**
```
[Step 1/6] Checking Administrator privileges...
[OK] Running with Administrator privileges

[Step 2/6] Checking Python installation...
[OK] Python 3.11.0 detected

[Step 3/6] Checking virtual environment...
[OK] Using myvenv virtual environment
```

**Runtime messages:**
```
[+] Analyzer running on WiFi
[OK] Live monitoring ACTIVE!
[DEBUG] Flow 8.8.8.8->192.168.1.100 - BENIGN
[FILTER] ... | Cloud:True (filtered)
```

### Log Files

Located in `logs/` directory:

- **alerts.jsonl** - All alerts (one per line)
- **app.log** - Application logs
- **alert_tracking.json** - Alert metadata

### API Status

Check system status:
```
http://localhost:8000/api/network/status
```

Returns:
```json
{
  "monitoring_active": true,
  "monitoring_interface": "WiFi",
  "capture_enabled": true,
  "admin_mode": true
}
```

---

## 🎯 Best Practices

### Startup

1. ✅ **Always use START_SYSTEM.bat** for first-time setup
2. ✅ **Run as Administrator** for full monitoring
3. ✅ **Check configuration** before starting
4. ✅ **Monitor console output** for errors

### Monitoring

1. ✅ **Start with API-only mode** for testing
2. ✅ **Test for false positives** before enabling auto-block
3. ✅ **Monitor for 24 hours** before production use
4. ✅ **Review logs regularly**

### Maintenance

1. ✅ **Update dependencies** periodically:
   ```powershell
   pip install --upgrade -r requirements.txt
   ```

2. ✅ **Clear old logs** to save space:
   ```powershell
   del logs\alerts.jsonl.old
   ```

3. ✅ **Backup configuration**:
   ```powershell
   copy config.yaml config.yaml.backup
   ```

---

## 📚 Related Documentation

- **Setup:** [WINDOWS_SETUP.md](../WINDOWS_SETUP.md)
- **Dashboard:** [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md)
- **False Positives:** [docs/NORMAL_TRAFFIC_FIX.md](NORMAL_TRAFFIC_FIX.md)
- **Testing:** [COMPLETE_TESTING_GUIDE.md](COMPLETE_TESTING_GUIDE.md)
- **Main Docs:** [README.md](../README.md)

---

## ✅ Summary: How to Start

### First Time:
```batch
1. Double-click: START_SYSTEM.bat
2. Click "Yes" on UAC prompt
3. Wait for setup to complete
4. Press Enter (choose Full System)
5. Open: http://localhost:8000
```

### Every Time After:
```batch
1. Double-click: FULL_START.bat
   OR
   Double-click: QUICK_START.bat (no admin)
2. Open: http://localhost:8000
```

### That's it! 🎉

---

**The system is now ready for use with one-click startup! 🚀🛡️**
