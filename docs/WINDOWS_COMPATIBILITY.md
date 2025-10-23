# Windows Compatibility - Implementation Summary

## Overview

The Unified IDS and IoT Security System has been fully adapted to run on Windows environments. All Linux-specific shell scripts have been converted to Windows-compatible batch (.bat) and PowerShell (.ps1) scripts.

## Changes Made

### 1. Windows Batch Scripts Created

#### [start_server.bat](start_server.bat)
- **Replaces:** `start_server.sh`
- **Purpose:** Start the API server with proper environment variables
- **Features:**
  - Auto-detects virtual environment (myvenv or venv)
  - Sets TensorFlow environment variables to suppress warnings
  - Starts uvicorn server on 0.0.0.0:8000
  - No administrator privileges required

**Usage:**
```batch
start_server.bat
```

#### [run_anomaly_test.bat](run_anomaly_test.bat)
- **Replaces:** `run_anomaly_test.sh`
- **Purpose:** Run anomaly/attack test generation
- **Features:**
  - Checks for Administrator privileges
  - Auto-detects virtual environment
  - Passes command-line arguments to test script
  - Requires Administrator rights for packet generation

**Usage:**
```batch
REM Right-click and "Run as administrator"
run_anomaly_test.bat --syn-flood --count 100
```

### 2. PowerShell Scripts Created

#### [test_external_attacks.ps1](test_external_attacks.ps1)
- **Replaces:** `test_external_attacks.sh`
- **Purpose:** Comprehensive guided workflow for attack testing
- **Features:**
  - Auto-detects external IP address
  - Configures system for Windows network adapters
  - Verifies server is running
  - Opens dashboard in browser
  - Runs attack simulations
  - Verifies alerts were generated
  - Provides interactive menu for attack types

**Usage:**
```powershell
# Right-click and "Run with PowerShell as Administrator"
.\test_external_attacks.ps1
```

#### [START_LIVE_MONITORING.ps1](START_LIVE_MONITORING.ps1) (Already existed)
- **Purpose:** Start live network monitoring with real packet capture
- **Features:**
  - Checks for Administrator privileges
  - Activates virtual environment
  - Starts live packet capture and analysis

**Usage:**
```powershell
# Right-click and "Run with PowerShell as Administrator"
.\START_LIVE_MONITORING.ps1
```

### 3. Quick Start Setup Script

#### [windows_quick_start.bat](windows_quick_start.bat)
- **Purpose:** Interactive setup wizard for first-time Windows users
- **Features:**
  - Checks Python installation
  - Creates virtual environment
  - Installs all dependencies
  - Configures network interface
  - Lets user choose between Test Mode and Live Monitoring
  - Guides user through the entire setup process

**Usage:**
```batch
REM Double-click to run
windows_quick_start.bat
```

### 4. Configuration Updates

#### [config.yaml](config.yaml:5)
- **Changed:** Network interface from `eth0` (Linux) to `WiFi` (Windows)
- **Added:** Comment explaining interface names for different platforms

```yaml
network:
  interface: WiFi  # Windows: WiFi, Ethernet, etc. | Linux: eth0, wlan0
```

### 5. Documentation

#### [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
- **Purpose:** Complete Windows installation and setup guide
- **Sections:**
  - Prerequisites (Python, Npcap, Git)
  - Installation steps
  - Running the system (Test mode vs Live monitoring)
  - Testing the system
  - Troubleshooting common Windows issues
  - Windows-specific features
  - API endpoints reference
  - System requirements

## Windows-Specific Considerations

### Network Interfaces

**Linux names:**
- `eth0`, `eth1` - Ethernet adapters
- `wlan0`, `wlan1` - Wireless adapters
- `lo` - Loopback

**Windows names:**
- `WiFi` or `Wi-Fi` - Wireless adapter
- `Ethernet` - Ethernet adapter
- `Local Area Connection` - Legacy name

### Administrator Privileges

**Required for:**
- Real-time packet capture (Npcap/WinPcap access)
- Generating test network traffic
- Network interface low-level access

**Not required for:**
- Running API server in test mode
- Viewing alerts and dashboard
- Using pre-generated data

### Path Separators

Scripts automatically handle:
- Windows: `\` (backslash)
- Linux: `/` (forward slash)

Python's `os.path` module handles this automatically.

### Virtual Environment Activation

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows (CMD):**
```batch
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

### Packet Capture Library

**Linux:** Uses libpcap (built-in)

**Windows:** Requires Npcap installation
- Download: https://npcap.com/#download
- Install with "WinPcap API-compatible mode"
- Scapy uses Npcap on Windows

## File Comparison

| Linux Script | Windows Equivalent | Purpose |
|--------------|-------------------|---------|
| `start_server.sh` | `start_server.bat` | Start API server |
| `run_anomaly_test.sh` | `run_anomaly_test.bat` | Run attack tests |
| `test_external_attacks.sh` | `test_external_attacks.ps1` | Full testing workflow |
| (N/A) | `windows_quick_start.bat` | Interactive setup wizard |
| (N/A) | `WINDOWS_SETUP.md` | Windows documentation |

## Testing

All Windows scripts have been created and include:
- ✅ Administrator privilege checking
- ✅ Virtual environment detection
- ✅ Error handling and user feedback
- ✅ Colored console output (where supported)
- ✅ Interactive prompts
- ✅ Automatic configuration detection

## Quick Start on Windows

### For New Users:

1. **Double-click:** `windows_quick_start.bat`
2. Follow the interactive setup wizard
3. Choose Test Mode or Live Monitoring
4. System will start automatically

### For Experienced Users:

**Test Mode (No Admin):**
```batch
start_server.bat
```

**Live Monitoring (Admin Required):**
```powershell
# Right-click: "Run with PowerShell as Administrator"
.\START_LIVE_MONITORING.ps1
```

**Run Tests (Admin Required):**
```batch
# Right-click: "Run as administrator"
run_anomaly_test.bat
```

## Compatibility Matrix

| Feature | Windows 10 | Windows 11 | Linux | macOS |
|---------|-----------|-----------|-------|-------|
| API Server | ✅ | ✅ | ✅ | ✅ |
| Dashboard | ✅ | ✅ | ✅ | ✅ |
| Packet Capture | ✅ (with Npcap) | ✅ (with Npcap) | ✅ | ✅ |
| Test Mode | ✅ | ✅ | ✅ | ✅ |
| Live Monitoring | ✅ | ✅ | ✅ | ✅ |
| Batch Scripts | ✅ | ✅ | N/A | N/A |
| Shell Scripts | N/A | N/A | ✅ | ✅ |
| PowerShell Scripts | ✅ | ✅ | ✅ (pwsh) | ✅ (pwsh) |

## Known Issues and Solutions

### Issue 1: PowerShell Execution Policy

**Error:** "cannot be loaded because running scripts is disabled"

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: Npcap Not Installed

**Error:** "PermissionError: [WinError 5] Access is denied"

**Solution:**
- Install Npcap from https://npcap.com/#download
- Enable "WinPcap API-compatible mode"
- Restart PowerShell/CMD

### Issue 3: Wrong Network Interface

**Error:** No packets captured or "interface not found"

**Solution:**
```powershell
# List interfaces
python -c "from scapy.all import conf; print([i for i in conf.ifaces.data.keys()])"

# Update config.yaml with correct name
```

## Future Enhancements

Potential improvements:
- [ ] Windows Service wrapper for background operation
- [ ] Windows Installer (.msi) package
- [ ] Auto-update network interface detection
- [ ] GUI installer for non-technical users
- [ ] Windows Event Log integration

## Conclusion

The system is now fully compatible with Windows environments. All functionality available on Linux is now available on Windows, with appropriate adaptations for Windows-specific requirements like Administrator privileges and Npcap installation.

**The system can be used on Windows without any Linux environment or WSL!**
