# Project Structure Guide

## 📁 Clean Folder Structure

After running the cleanup script, your project will have this structure:

```
unified-ids-and-iot-security-system/
│
├── 📄 README.md                      # Main documentation & overview
├── ⚙️ config.yaml                    # System configuration
├── 📋 requirements.txt                # Python dependencies
│
├── 🚀 START_SYSTEM.bat               # Main system launcher
├── 🚀 START_SYSTEM.ps1               # PowerShell main script
├── ⚡ FULL_START.bat                 # Quick full system start
├── ⚡ QUICK_START.bat                # Quick API-only start
├── 🔧 SETUP_VENV.bat                 # Virtual environment setup
├── 📡 START_LIVE_MONITORING.ps1      # Live network monitoring
├── 🐍 start_live_monitoring.py       # Monitoring Python script
│
├── 📚 docs/                           # Essential documentation
│   ├── WINDOWS_SETUP.md              # Windows installation guide
│   ├── SYSTEM_STARTUP_GUIDE.md       # How to start the system
│   ├── DASHBOARD_SETUP.md            # Dashboard setup & usage
│   ├── COMPLETE_TESTING_GUIDE.md     # Testing procedures
│   ├── FALSE_POSITIVES_GUIDE.md      # Tuning false positives
│   ├── MODEL_TRAINING_GUIDE.md       # Training ML models
│   └── WINDOWS_COMPATIBILITY.md      # Technical Windows details
│
├── 🔧 scripts/                        # Utility scripts
│   ├── build_frontend.bat            # Build React dashboard
│   ├── run_anomaly_test.bat          # Run attack simulations
│   └── test_external_attacks.ps1     # External attack testing
│
├── 🛠️ utils/                          # Helper utilities
│   ├── clear_alerts.py               # Clear alert database
│   ├── fix_false_positives.py        # FP adjustment tool
│   ├── scan_network.py               # Network scanner
│   ├── show_iot_devices.py           # Show detected IoT devices
│   └── toggle_localhost_filtering.py # Toggle localhost filter
│
├── 💻 src/                            # Source code
│   ├── api/                          # FastAPI backend
│   │   ├── main.py                   # API server
│   │   └── endpoints.py              # API endpoints
│   │
│   ├── models/                       # ML model inference
│   │   ├── predict.py                # Prediction engine
│   │   ├── hybrid_detector.py        # Hybrid ML/DL model
│   │   └── model_ensemble.py         # Ensemble methods
│   │
│   ├── network/                      # Network monitoring
│   │   ├── packet_sniffer.py         # Packet capture
│   │   └── traffic_analyzer.py       # Traffic analysis
│   │
│   ├── iot_security/                 # IoT device detection
│   │   └── device_detector.py        # IoT device profiling
│   │
│   ├── utils/                        # Utilities
│   │   ├── alert_manager.py          # Alert management
│   │   ├── config_loader.py          # Configuration loader
│   │   └── response_actions.py       # Automated responses
│   │
│   └── frontend/                     # React dashboard
│       ├── src/                      # React source
│       ├── public/                   # Static assets
│       ├── dist/                     # Built dashboard
│       └── package.json              # Node.js config
│
├── 🧪 tests/                          # Test files
│   ├── generate_anomalies.py         # Attack generator
│   └── test_*.py                     # Various tests
│
├── 📊 notebooks/                      # Jupyter notebooks
│   ├── 01_*.ipynb                    # Data exploration
│   ├── 02_*.ipynb                    # Feature engineering
│   ├── 03_*.ipynb                    # Model training
│   └── ...
│
├── 🤖 trained_models/                 # Trained ML/DL models
│   ├── best_baseline.pkl             # ML model
│   ├── scaler_standard.pkl           # Feature scaler
│   ├── encoder.pkl                   # Label encoder
│   └── dl_models/                    # Deep learning models
│       ├── final_ffnn_residual.keras
│       ├── anomaly_autoencoder.keras
│       └── ...
│
├── 📝 logs/                           # Log files
│   ├── alerts.jsonl                  # Alert logs
│   ├── app.log                       # Application logs
│   └── alert_tracking.json           # Alert metadata
│
├── ⚙️ config/                         # Additional config files
│
└── 🐍 myvenv/                         # Python virtual environment
    ├── Scripts/                      # Python executable & tools
    └── Lib/                          # Installed packages
```

## 🎯 Key Directories Explained

### Root Directory
Contains **only essential startup scripts** and main documentation.

**Quick Start Files:**
- `START_SYSTEM.bat` - Main launcher with setup
- `FULL_START.bat` - One-click full system
- `QUICK_START.bat` - One-click API only

### docs/
**Only 7 essential guides** - everything you need to use the system.

**For Users:**
- `WINDOWS_SETUP.md` - First-time installation
- `SYSTEM_STARTUP_GUIDE.md` - How to start
- `DASHBOARD_SETUP.md` - Dashboard usage

**For Tuning:**
- `FALSE_POSITIVES_GUIDE.md` - Reduce false positives
- `COMPLETE_TESTING_GUIDE.md` - Testing procedures

**For Developers:**
- `MODEL_TRAINING_GUIDE.md` - Retrain models
- `WINDOWS_COMPATIBILITY.md` - Technical details

### scripts/
**Build and test scripts** that aren't needed daily.

Use when:
- Building frontend: `scripts\build_frontend.bat`
- Testing attacks: `scripts\run_anomaly_test.bat`
- External testing: `scripts\test_external_attacks.ps1`

### utils/
**Helper utilities** for maintenance and troubleshooting.

Use when:
- Clear old alerts: `utils\clear_alerts.py`
- Fix FP issues: `utils\fix_false_positives.py`
- Scan network: `utils\scan_network.py`
- Check IoT devices: `utils\show_iot_devices.py`

### src/
**Source code** - organized by functionality.

- `api/` - REST API and WebSocket server
- `models/` - ML/DL prediction engine
- `network/` - Packet capture and analysis
- `iot_security/` - IoT device detection
- `utils/` - Core utilities
- `frontend/` - React dashboard

### tests/
**Test scripts** for development and validation.

### notebooks/
**Jupyter notebooks** for ML model development.

### trained_models/
**Pre-trained ML/DL models** - ready to use.

### logs/
**Runtime logs** - alerts, errors, status.

### config/
**Additional configuration** files.

### myvenv/
**Python virtual environment** with all dependencies.

## 📊 File Count Comparison

**Before Cleanup:**
- Root directory: ~25 files
- docs/ directory: ~64 files
- **Total: ~90 files** at top level

**After Cleanup:**
- Root directory: ~10 essential files
- docs/ directory: ~7 essential guides
- scripts/: 3 files
- utils/: 5 files
- **Total: ~25 files** at top level
- **Reduction: 72% cleaner!**

## 🎨 Benefits of Clean Structure

### ✅ For Users:
- **Find startup scripts instantly** - All in root
- **Clear documentation** - Only what you need
- **Professional appearance** - Industry standard

### ✅ For Developers:
- **Easy navigation** - Logical folder structure
- **Quick file location** - Know where to look
- **Maintainable** - Clean separation of concerns

### ✅ For Maintenance:
- **Less clutter** - Focus on essentials
- **Easier updates** - Know what to modify
- **Version control friendly** - Less noise in commits

## 🔧 Running the Cleanup

### Option 1: Test First (Dry Run)
```powershell
.\CLEANUP_SYSTEM.ps1 -DryRun
```
Shows what would be changed without modifying anything.

### Option 2: Run Cleanup
```batch
# Double-click
CLEANUP_SYSTEM.bat

# Or PowerShell
.\CLEANUP_SYSTEM.ps1
```

### Option 3: Cleanup Without Archive
```powershell
.\CLEANUP_SYSTEM.ps1 -ArchiveOld:$false
```
Removes files instead of archiving them.

## 📦 What Happens to Old Files?

All obsolete files are moved to:
```
archive_YYYYMMDD_HHMMSS/
├── docs/          # Old documentation
└── scripts/       # Old scripts
```

**You can safely delete the archive folder** after verifying everything works!

## ✨ Post-Cleanup

After cleanup, your workflow is simpler:

**Starting the system:**
```batch
# From root directory
START_SYSTEM.bat
```

**Finding documentation:**
```
docs/
  ├── WINDOWS_SETUP.md          # Setup
  ├── SYSTEM_STARTUP_GUIDE.md   # Start
  └── DASHBOARD_SETUP.md        # Dashboard
```

**Running utilities:**
```batch
# From root
utils\clear_alerts.py
scripts\build_frontend.bat
```

## 🎯 Summary

**Clean structure means:**
- ✅ **10 files** in root (vs 25)
- ✅ **7 docs** (vs 64)
- ✅ **Organized folders** (scripts/, utils/)
- ✅ **Professional appearance**
- ✅ **Easy to navigate**
- ✅ **Maintainable**

**Everything you need, nothing you don't!** 🚀
