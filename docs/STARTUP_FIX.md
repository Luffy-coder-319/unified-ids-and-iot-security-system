# Startup Script Working Directory Fix

## Problem

When running `START_SYSTEM.bat` or `FULL_START.bat`, the scripts would fail with errors like:
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
C:\Users\sherp\AppData\Local\Programs\Python\Python311\python.exe: can't open file 'C:\\WINDOWS\\system32\\start_live_monitoring.py': [Errno 2] No such file or directory
```

## Root Cause

When PowerShell requests Administrator privileges using `Start-Process -Verb RunAs`, the elevated process starts with a default working directory of `C:\WINDOWS\system32` instead of the project directory. This caused all relative file paths to fail.

## Solution Applied

### 1. Fixed PowerShell Elevation (START_SYSTEM.ps1)

**Before:**
```powershell
$arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
Start-Process powershell.exe -ArgumentList $arguments -Verb RunAs
```

**After:**
```powershell
# Preserve working directory when elevating
$scriptPath = $PSCommandPath
$workingDir = $PSScriptRoot
$arguments = "-NoProfile -ExecutionPolicy Bypass -Command `"Set-Location '$workingDir'; & '$scriptPath'"
if ($BuildFrontend) { $arguments += " -BuildFrontend" }
if ($SkipMonitoring) { $arguments += " -SkipMonitoring" }
$arguments += "`""

Start-Process powershell.exe -ArgumentList $arguments -Verb RunAs
```

**Changes:**
- Captures the script's directory using `$PSScriptRoot`
- Uses `-Command` instead of `-File` to allow multiple commands
- Explicitly sets location with `Set-Location` before running the script
- Preserves command-line parameters

### 2. Added Working Directory Check (START_SYSTEM.ps1)

Added explicit working directory verification after privilege check:
```powershell
# Ensure we're in the correct directory (project root)
$projectRoot = $PSScriptRoot
if (-not $projectRoot) {
    $projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}
Set-Location $projectRoot
Write-Info "[INFO] Working directory: $projectRoot"
```

This ensures the script always runs from the correct directory, even if something goes wrong with elevation.

### 3. Fixed Background Job Directory (START_SYSTEM.ps1)

**Before:**
```powershell
$apiJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & "myvenv\Scripts\python.exe" -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
}
```

**After:**
```powershell
$apiJob = Start-Job -ScriptBlock {
    Set-Location $using:projectRoot
    & "myvenv\Scripts\python.exe" -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
}
```

Uses the explicitly set `$projectRoot` variable instead of `$PWD` for reliability.

### 4. Fixed Batch File Working Directories

Added `cd /d "%~dp0"` to all batch launchers:

**START_SYSTEM.bat:**
```batch
REM Change to script directory
cd /d "%~dp0"

REM Check for admin rights
net session >nul 2>&1
```

**FULL_START.bat:**
```batch
echo [OK] Running with Administrator privileges
echo.

REM Change to script directory
cd /d "%~dp0"

REM Run the main startup script
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0START_SYSTEM.ps1"
```

**QUICK_START.bat:**
```batch
echo ===============================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if myvenv virtual environment exists
```

**What `cd /d "%~dp0"` does:**
- `%~dp0` = Drive and path of the batch file
- `cd /d` = Change directory including drive letter
- Ensures the script always runs from its own directory

## Files Modified

1. ✅ [START_SYSTEM.ps1](START_SYSTEM.ps1) - Lines 32-38, 47-54, 211
2. ✅ [START_SYSTEM.bat](START_SYSTEM.bat) - Lines 10-11
3. ✅ [FULL_START.bat](FULL_START.bat) - Lines 23-24
4. ✅ [QUICK_START.bat](QUICK_START.bat) - Lines 20-21

## Testing

To verify the fix works:

1. **Test from any directory:**
   ```batch
   cd C:\
   "d:\project\unified-ids-and-iot-security-system\START_SYSTEM.bat"
   ```

2. **Test double-click from Explorer:**
   - Navigate to project folder in Windows Explorer
   - Double-click `START_SYSTEM.bat`
   - Should work correctly regardless of current directory

3. **Verify working directory:**
   - When script starts, it should display:
     ```
     [INFO] Working directory: d:\project\unified-ids-and-iot-security-system
     ```

4. **Check for errors:**
   - Should NOT see "No such file or directory" errors
   - Should find `requirements.txt`, `config.yaml`, `start_live_monitoring.py`

## Benefits

✅ **Works from any directory** - No matter where you run it from
✅ **Preserves location on elevation** - Admin mode uses correct directory
✅ **Consistent behavior** - All batch files work the same way
✅ **Clear feedback** - Shows working directory on startup
✅ **Reliable file access** - All relative paths work correctly

## Technical Details

### Why `$PSScriptRoot`?

- `$PSScriptRoot` = Directory containing the script
- Available in PowerShell 3.0+
- More reliable than `$PWD` or `Get-Location`
- Works even when script is called from another directory

### Why `-Command` instead of `-File`?

When using `Start-Process -Verb RunAs`:
- `-File` doesn't allow setting working directory first
- `-Command` allows multiple commands: `Set-Location; & script.ps1`
- This ensures directory is set BEFORE the script runs

### Why `cd /d` in batch files?

- `cd` alone won't change drives (C: to D:)
- `cd /d` changes both directory AND drive
- Essential for projects on non-system drives

## Previous Error Example

```
[Step 3/6] Checking virtual environment...
[OK] Using myvenv virtual environment
Verifying dependencies...
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'

...

Starting live network monitoring...
C:\Users\sherp\AppData\Local\Programs\Python\Python311\python.exe: can't open file 'C:\\WINDOWS\\system32\\start_live_monitoring.py': [Errno 2] No such file or directory
```

**Reason:** Script was looking in `C:\WINDOWS\system32\` instead of project directory.

## Current Expected Output

```
[Step 1/6] Checking Administrator privileges...
[OK] Running with Administrator privileges

[INFO] Working directory: d:\project\unified-ids-and-iot-security-system

[Step 2/6] Checking Python installation...
[OK] Python 3.11.9 detected

[Step 3/6] Checking virtual environment...
[OK] Using myvenv virtual environment
[OK] Dependencies verified

[Step 4/6] Checking frontend...
Frontend build skipped (use -BuildFrontend flag to build)

[Step 5/6] Checking configuration...
[OK] Configuration file found

[Step 6/6] Starting system components...
```

All file operations now work correctly! 🎉

## Summary

The fix ensures that all startup scripts:
1. Always run from the project root directory
2. Preserve the working directory when elevating to admin
3. Display the current working directory for verification
4. Work consistently whether run from Explorer, command line, or any directory

This resolves the "file not found" errors and ensures reliable system startup.
