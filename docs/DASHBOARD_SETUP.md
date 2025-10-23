# Dashboard Setup Guide

## Quick Fix: Network Flows Not Showing

The dashboard network flows component has been updated with better error handling and fallback mechanisms.

### Issue
The dashboard was not showing network flows due to:
1. WebSocket connection issues
2. Frontend not built/deployed
3. No fallback to REST API

### Solution Applied

The Flows component now:
- ✅ **Tries WebSocket first** for real-time updates
- ✅ **Falls back to REST API** if WebSocket fails
- ✅ **Shows connection status** (🟢 Live or 🔄 Polling)
- ✅ **Displays helpful error messages**
- ✅ **Shows "No flows yet" message** when no traffic detected

---

## Setup Instructions

### Step 1: Install Node.js (If Not Installed)

**Download:** https://nodejs.org/

**Verify installation:**
```powershell
node --version
npm --version
```

### Step 2: Build the Frontend

**Option A: Use build script (Easy)**
```batch
build_frontend.bat
```

**Option B: Manual build**
```powershell
cd src\frontend
npm install
npm run build
cd ..\..
```

### Step 3: Start the Server

```batch
start_server.bat
```

Or with live monitoring (Administrator required):
```powershell
.\START_LIVE_MONITORING.ps1
```

### Step 4: Access Dashboard

Open browser: **http://localhost:8000**

---

## Dashboard Features

### Main Dashboard Tab

Shows 4 key metrics:
- **Total Packets** - All captured packets
- **Detected Threats** - Number of alerts
- **Active Devices** - Unique IP addresses
- **IoT Devices** - Identified IoT devices

### Traffic Overview

**Network Flows Chart:**
- Real-time line chart showing packet counts
- Updates every 1-2 seconds
- Shows connection status (Live/Polling)

**What shows as a "flow":**
- Each unique connection (src_ip → dst_ip : port : protocol)
- Packet count for that flow
- Only shows flows with activity

### Recent Alerts

Shows latest security alerts with:
- Timestamp
- Source/Destination IPs
- Threat type
- Severity level
- Confidence score

### IoT Devices Tab

Lists detected IoT devices:
- Device type identification
- MAC address
- IP address
- Ports used
- First/Last seen times

### Alerts Tab

Full alert view with:
- All historical alerts
- Filtering options
- Acknowledgment status
- Detailed threat information

---

## Troubleshooting

### Problem 1: "No flows yet" Message

**Cause:** No network traffic being captured or filtered out

**Solutions:**

1. **Check if monitoring is running:**
   ```
   http://localhost:8000/api/network/status
   ```

2. **Generate network activity:**
   - Browse websites
   - Run: `ping google.com`
   - Download a file
   - Watch a video

3. **Check if flows are being filtered:**
   - Lower detection thresholds temporarily
   - Check DEBUG output in terminal
   - View flows via API: `http://localhost:8000/api/flows`

4. **Verify capture is working:**
   - Must run as Administrator for live capture
   - Check terminal shows `[+] Analyzer running on WiFi`
   - Look for `[DEBUG] Flow X.X.X.X->Y.Y.Y.Y` messages

### Problem 2: "Cannot connect to API"

**Cause:** Server not running or wrong port

**Solutions:**

1. **Start the server:**
   ```batch
   start_server.bat
   ```

2. **Check server is running:**
   ```powershell
   netstat -ano | findstr :8000
   ```

3. **Verify API responds:**
   ```
   http://localhost:8000/api/flows
   ```

### Problem 3: "WebSocket failed, using REST API"

**Cause:** WebSocket connection couldn't establish

**Impact:** Dashboard still works, but uses polling instead of real-time updates

**This is NORMAL and OKAY!** The dashboard automatically falls back to REST API polling.

**To fix (optional):**
1. Check browser console for errors (F12)
2. Verify CORS settings in [main.py](../src/api/main.py:64-70)
3. Ensure no firewall blocking WebSocket connections

### Problem 4: Flows showing but chart not rendering

**Cause:** Frontend build issue or React error

**Solutions:**

1. **Rebuild frontend:**
   ```batch
   build_frontend.bat
   ```

2. **Check browser console:**
   - Press F12
   - Look for JavaScript errors
   - Check Network tab for failed requests

3. **Clear browser cache:**
   - Ctrl + Shift + Delete
   - Clear cached images and files
   - Hard reload: Ctrl + F5

### Problem 5: Dashboard shows 0 for all metrics

**Cause:** No traffic captured yet or API not returning data

**Solutions:**

1. **Check API directly:**
   ```
   http://localhost:8000/api/flows
   http://localhost:8000/api/alerts
   ```

2. **Generate test traffic:**
   ```powershell
   # Right-click and run as Administrator
   .\run_anomaly_test.bat --syn-flood --count 100
   ```

3. **Verify monitoring is active:**
   - Check terminal shows packet capture messages
   - Look for `[DEBUG] Flow` lines
   - Ensure running as Administrator

---

## Development Mode

For development with hot-reload:

```powershell
cd src\frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:5173

API will still be at: http://localhost:8000

---

## API Endpoints for Dashboard

The dashboard uses these endpoints:

### Flow Data
- **WebSocket:** `ws://localhost:8000/ws/flows`
- **REST:** `GET /api/flows`

### Alert Data
- **WebSocket:** `ws://localhost:8000/ws/alerts`
- **REST:** `GET /api/alerts`

### Statistics
- `GET /api/statistics/summary`
- `GET /api/statistics/realtime`
- `GET /api/statistics/by-severity`

### IoT Devices
- `GET /api/iot/devices`
- `GET /api/iot/summary`

### Network Status
- `GET /api/network/status`
- `GET /api/network/interfaces`

---

## Understanding Network Flows

### What is a "Flow"?

A flow represents a unique network conversation:
```
Source IP → Destination IP : Source Port : Protocol
192.168.1.100 → 8.8.8.8 : 443 : TCP
```

### Why might flows not show?

1. **All traffic filtered out:**
   - Cloud services whitelisted (Google, Microsoft, etc.)
   - Private network traffic excluded
   - Below packet threshold (< 50 packets)

2. **No network activity:**
   - No browsing or network usage
   - Monitoring just started

3. **Monitoring not active:**
   - Not running as Administrator
   - Network interface not correctly configured

### How to see flows:

**Generate legitimate traffic:**
```powershell
# Visit websites
start chrome https://example.com

# DNS lookups
nslookup google.com

# Ping test
ping -n 100 8.8.8.8

# Download test
curl https://speed.cloudflare.com/__down?bytes=10000000
```

**View flows via API:**
```powershell
# PowerShell
(Invoke-WebRequest http://localhost:8000/api/flows).Content | ConvertFrom-Json

# Browser
http://localhost:8000/api/flows
```

---

## Performance Notes

### WebSocket vs REST API

**WebSocket (Default):**
- ✅ Real-time updates (1 second)
- ✅ Lower overhead
- ✅ Push-based
- ❌ May fail in some environments

**REST API (Fallback):**
- ✅ Always works
- ✅ Simple and reliable
- ✅ Polling every 2 seconds
- ❌ Slightly higher latency

The dashboard automatically chooses the best option!

### Chart Performance

- Shows up to all flows (no limit by default)
- Updates smoothly every 1-2 seconds
- Efficient rendering with Recharts library

---

## Summary

### ✅ Dashboard Now Shows:

1. **Real-time network flows** (if traffic is active)
2. **Connection status indicator** (Live/Polling)
3. **Helpful messages** when no data
4. **Automatic fallback** to REST API
5. **Error handling** with user-friendly messages

### 🔧 To See Flows:

1. **Build frontend:** `build_frontend.bat`
2. **Start monitoring:** `.\START_LIVE_MONITORING.ps1` (as Admin)
3. **Generate traffic:** Browse, download, or run tests
4. **Open dashboard:** http://localhost:8000
5. **Check flows appear** in the chart

### 📊 Expected Behavior:

**With Traffic:**
```
🟢 Live
[Chart shows active flows with packet counts]
```

**Without Traffic:**
```
No network flows detected yet
Start browsing or generate network activity to see flows
```

**API Fallback:**
```
🔄 Polling (WebSocket failed, using REST API)
[Chart updates every 2 seconds]
```

---

## Support

- **Server not starting:** [WINDOWS_SETUP.md](../WINDOWS_SETUP.md)
- **False positives:** [docs/NORMAL_TRAFFIC_FIX.md](NORMAL_TRAFFIC_FIX.md)
- **Testing:** [COMPLETE_TESTING_GUIDE.md](COMPLETE_TESTING_GUIDE.md)
- **Main docs:** [README.md](../README.md)

**Dashboard is ready! 📊🛡️**
