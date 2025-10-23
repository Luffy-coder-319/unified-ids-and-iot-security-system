"""
Start Live Network Monitoring with Real Traffic Capture

This script starts the IDS system to monitor REAL live network traffic
on your WiFi adapter. It will detect and alert on actual threats.

IMPORTANT: Must run as Administrator on Windows!
"""
import sys
import os
import time

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_admin_privileges():
    """Check if running with Administrator privileges"""
    import platform
    import ctypes

    if platform.system() == 'Windows':
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            return is_admin
        except:
            return False
    else:
        # Linux/Mac
        return os.geteuid() == 0 if hasattr(os, 'geteuid') else False

def main():
    print("=" * 80)
    print("  LIVE NETWORK MONITORING - IoT Security System")
    print("=" * 80)

    # Check admin privileges
    if not check_admin_privileges():
        print("\n[ERROR] Administrator privileges required!")
        print("\nPlease run this script as Administrator:")
        print("  1. Right-click PowerShell")
        print("  2. Select 'Run as Administrator'")
        print("  3. Navigate to project directory")
        print("  4. Run: python start_live_monitoring.py\n")
        return 1

    print("\n[OK] Running with Administrator privileges")

    # Import after path setup
    from src.network.traffic_analyzer import start_analyzer
    from src.utils.config_loader import load_config

    # Load configuration
    config = load_config('config.yaml')
    interface = config.get('network', {}).get('interface', 'WiFi')

    print(f"\n[INFO] Configuration loaded:")
    print(f"  Network Interface: {interface}")
    print(f"  Capture Filter: {config.get('network', {}).get('capture_filter', 'All traffic')}")
    print(f"  Confidence Threshold: {config.get('detection', {}).get('confidence_threshold', 0.7)}")
    print(f"  Anomaly Multiplier: {config.get('detection', {}).get('anomaly_multiplier', 2.5)}")

    print(f"\n[INFO] Starting packet capture on: {interface}")
    print("[INFO] This will capture and analyze REAL network traffic...")
    print("\n[STATUS] Monitoring for threats...")
    print("  - Press Ctrl+C to stop")
    print("  - View dashboard at: http://localhost:8000")
    print("  - Alerts will appear in real-time")
    print("  - API alerts: http://localhost:8000/api/alerts\n")

    # Start the analyzer
    print("[+] Initializing traffic analyzer...")
    analyzer_thread = start_analyzer(interface=interface, config=config)

    if analyzer_thread is None:
        print("\n[ERROR] Failed to start traffic analyzer!")
        print("  Possible causes:")
        print("  - Network interface name is incorrect")
        print("  - Npcap driver not installed")
        print("  - Another packet capture tool is running")
        print("\n  Try running: ipconfig")
        print("  And verify the interface name matches config.yaml\n")
        return 1

    print("[OK] Live monitoring ACTIVE!")
    print("\n[INFO] Threat detection is now running...")
    print("[INFO] Generate network activity to see alerts:")
    print("  - Browse websites")
    print("  - Run: ping google.com")
    print("  - Download files")
    print("  - Any suspicious activity will trigger alerts\n")

    try:
        # Keep the script running
        packet_count = 0
        while True:
            time.sleep(5)
            packet_count += 1
            if packet_count % 12 == 0:  # Every minute
                print(f"[{time.strftime('%H:%M:%S')}] Still monitoring... (Ctrl+C to stop)")

    except KeyboardInterrupt:
        print("\n\n[STOP] Stopping live monitoring...")
        print("[OK] Monitoring stopped successfully")
        print(f"\n[INFO] Check logs/alerts.jsonl for captured alerts")
        return 0

if __name__ == "__main__":
    sys.exit(main())
