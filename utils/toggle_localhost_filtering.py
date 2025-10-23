#!/usr/bin/env python3
"""
Toggle localhost filtering on/off for testing purposes.
This allows you to test anomaly detection against localhost without false positive filtering.
"""

import sys

TRAFFIC_ANALYZER = "src/network/traffic_analyzer.py"
FILTER_LINE_ENABLED = """                    should_alert = (
                        threat != 'BENIGN' and
                        (
                            not is_localhost_to_localhost or
                            (not is_low_rate and prediction.get('confidence', 0) >= 0.95)
                        ) and
                        not is_localhost  # Skip all localhost traffic for now
                    )"""

FILTER_LINE_DISABLED = """                    should_alert = (
                        threat != 'BENIGN' and
                        (
                            not is_localhost_to_localhost or
                            (not is_low_rate and prediction.get('confidence', 0) >= 0.95)
                        )
                        # LOCALHOST FILTERING DISABLED FOR TESTING
                        # Original line was: and not is_localhost
                    )"""

def read_file():
    with open(TRAFFIC_ANALYZER, 'r') as f:
        return f.read()

def write_file(content):
    with open(TRAFFIC_ANALYZER, 'w') as f:
        f.write(content)

def disable_filtering():
    content = read_file()
    if FILTER_LINE_ENABLED in content:
        new_content = content.replace(FILTER_LINE_ENABLED, FILTER_LINE_DISABLED)
        write_file(new_content)
        print("[✓] Localhost filtering DISABLED")
        print("    Alerts will now be generated for localhost traffic")
        print("    Run tests with: sudo venv/bin/python -m tests.generate_anomalies --target 127.0.0.1 --syn-flood --count 200")
        print("")
        print("    Remember to re-enable filtering after testing:")
        print("    python3 toggle_localhost_filtering.py enable")
        return True
    elif FILTER_LINE_DISABLED in content:
        print("[!] Localhost filtering is already DISABLED")
        return False
    else:
        print("[!] Could not find filtering line in traffic_analyzer.py")
        return False

def enable_filtering():
    content = read_file()
    if FILTER_LINE_DISABLED in content:
        new_content = content.replace(FILTER_LINE_DISABLED, FILTER_LINE_ENABLED)
        write_file(new_content)
        print("[✓] Localhost filtering ENABLED")
        print("    Localhost traffic will be filtered to reduce false positives")
        return True
    elif FILTER_LINE_ENABLED in content:
        print("[!] Localhost filtering is already ENABLED")
        return False
    else:
        print("[!] Could not find filtering line in traffic_analyzer.py")
        return False

def check_status():
    content = read_file()
    if FILTER_LINE_ENABLED in content:
        print("[Status] Localhost filtering: ENABLED")
        print("         Localhost alerts are suppressed (production mode)")
    elif FILTER_LINE_DISABLED in content:
        print("[Status] Localhost filtering: DISABLED")
        print("         Localhost alerts are active (testing mode)")
    else:
        print("[Status] Unknown - could not determine filtering status")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ./toggle_localhost_filtering.py disable   # Disable filtering for testing")
        print("  ./toggle_localhost_filtering.py enable    # Re-enable filtering")
        print("  ./toggle_localhost_filtering.py status    # Check current status")
        print("")
        check_status()
        return 1

    command = sys.argv[1].lower()

    if command == "disable":
        return 0 if disable_filtering() else 1
    elif command == "enable":
        return 0 if enable_filtering() else 1
    elif command == "status":
        check_status()
        return 0
    else:
        print(f"Unknown command: {command}")
        print("Use: disable, enable, or status")
        return 1

if __name__ == "__main__":
    sys.exit(main())
