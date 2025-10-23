# Project Cleanup Plan

## Current Issues
- 64+ documentation files (many redundant/obsolete)
- 23+ scripts in root directory (duplicates, test files)
- Unclear folder structure
- Old/deprecated files mixed with current ones

## Cleanup Strategy

### Files to KEEP (Essential)

#### Root Directory - Startup Scripts:
- ✅ **START_SYSTEM.bat** - Main launcher
- ✅ **START_SYSTEM.ps1** - Main PowerShell script
- ✅ **FULL_START.bat** - Quick full system start
- ✅ **QUICK_START.bat** - API only start
- ✅ **SETUP_VENV.bat** - Virtual environment setup
- ✅ **START_LIVE_MONITORING.ps1** - Live monitoring
- ✅ **start_live_monitoring.py** - Python monitoring script
- ✅ **README.md** - Main documentation
- ✅ **config.yaml** - Configuration
- ✅ **requirements.txt** - Dependencies

#### Docs - Keep Only:
- ✅ **WINDOWS_SETUP.md** - Windows installation
- ✅ **SYSTEM_STARTUP_GUIDE.md** - How to start
- ✅ **DASHBOARD_SETUP.md** - Dashboard guide
- ✅ **COMPLETE_TESTING_GUIDE.md** - Testing guide
- ✅ **FALSE_POSITIVES_GUIDE.md** - FP tuning
- ✅ **MODEL_TRAINING_GUIDE.md** - Training models
- ✅ **WINDOWS_COMPATIBILITY.md** - Windows tech details

### Files to MOVE

#### To scripts/ folder:
- build_frontend.bat
- run_anomaly_test.bat
- test_external_attacks.ps1

#### To utils/ folder:
- clear_alerts.py
- fix_false_positives.py
- scan_network.py
- show_iot_devices.py
- toggle_localhost_filtering.py

#### To tests/ folder:
- start_system_test.py
- test_alert_generation.py
- test_network_interfaces.py

### Files to REMOVE (Obsolete)

#### Duplicate/Old Scripts:
- ❌ start_server.bat (use START_SYSTEM.bat)
- ❌ start_server.sh (use START_SYSTEM.ps1 or linux equivalent)
- ❌ run_anomaly_test.sh (Windows only now)
- ❌ test_external_attacks.sh (Windows only now)
- ❌ windows_quick_start.bat (use QUICK_START.bat)

#### Obsolete Docs (57 to remove):
- ❌ All "FIX", "STATUS", "BEFORE_AFTER" docs
- ❌ Duplicate quick start guides
- ❌ Old migration/integration docs
- ❌ Redundant testing guides
- ❌ Obsolete memory optimization reports

## Proposed Clean Structure

```
unified-ids-and-iot-security-system/
├── README.md                      # Main documentation
├── config.yaml                    # Configuration
├── requirements.txt               # Dependencies
│
├── START_SYSTEM.bat              # 🚀 Main launcher
├── START_SYSTEM.ps1              # Main script
├── FULL_START.bat                # Quick full start
├── QUICK_START.bat               # Quick API start
├── SETUP_VENV.bat                # Venv setup
├── START_LIVE_MONITORING.ps1     # Live monitoring
├── start_live_monitoring.py      # Monitoring Python
│
├── docs/                          # 📚 Essential docs only
│   ├── WINDOWS_SETUP.md          # Setup guide
│   ├── SYSTEM_STARTUP_GUIDE.md   # How to start
│   ├── DASHBOARD_SETUP.md        # Dashboard guide
│   ├── TESTING_GUIDE.md          # Testing
│   ├── FALSE_POSITIVES_GUIDE.md  # FP tuning
│   ├── MODEL_TRAINING_GUIDE.md   # Training
│   └── WINDOWS_COMPATIBILITY.md  # Technical details
│
├── scripts/                       # 🔧 Utility scripts
│   ├── build_frontend.bat
│   ├── run_anomaly_test.bat
│   └── test_external_attacks.ps1
│
├── utils/                         # 🛠️ Helper utilities
│   ├── clear_alerts.py
│   ├── fix_false_positives.py
│   ├── scan_network.py
│   ├── show_iot_devices.py
│   └── toggle_localhost_filtering.py
│
├── src/                           # Source code
│   ├── api/                      # FastAPI backend
│   ├── models/                   # ML models
│   ├── network/                  # Packet capture
│   ├── iot_security/             # IoT detection
│   ├── utils/                    # Utilities
│   └── frontend/                 # React dashboard
│
├── tests/                         # Test files
│   ├── generate_anomalies.py
│   ├── start_system_test.py
│   └── test_*.py
│
├── logs/                          # Log files
├── trained_models/                # ML models
├── notebooks/                     # Jupyter notebooks
├── config/                        # Config files
└── myvenv/                        # Virtual environment
```

## Benefits

✅ **Cleaner root directory** - Only essential files
✅ **Organized scripts** - In dedicated folders
✅ **Reduced docs** - From 64 to 7 essential guides
✅ **Easy navigation** - Clear folder purpose
✅ **Professional structure** - Industry standard
✅ **Easier maintenance** - Find files quickly

## Implementation

Run the cleanup script to automatically:
1. Create new folders (scripts/, utils/)
2. Move files to correct locations
3. Archive obsolete docs
4. Update references
5. Generate new structure guide
