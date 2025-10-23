#!/usr/bin/env python3
"""
Quick fix script for false positive alerts.
This script will help you configure the system to reduce false positives.
"""

import sys
import yaml
from pathlib import Path

CONFIG_FILE = "config.yaml"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

def print_current_config():
    config = load_config()
    print("\n" + "="*60)
    print("Current Configuration:")
    print("="*60)
    print(f"Network Interface: {config.get('network', {}).get('interface', 'NOT SET')}")
    print(f"Confidence Threshold: {config.get('detection', {}).get('confidence_threshold', 'NOT SET')}")
    print(f"Anomaly Multiplier: {config.get('detection', {}).get('anomaly_multiplier', 'NOT SET')}")
    print(f"Filter Localhost: {config.get('detection', {}).get('filter_localhost', 'NOT SET')}")
    print("="*60)

def apply_production_settings():
    """Apply recommended settings for production (minimal false positives)"""
    config = load_config()

    # Update settings
    if 'network' not in config:
        config['network'] = {}
    config['network']['interface'] = 'eth0'

    if 'detection' not in config:
        config['detection'] = {}
    config['detection']['confidence_threshold'] = 0.85
    config['detection']['anomaly_multiplier'] = 3.5
    config['detection']['filter_localhost'] = True

    save_config(config)

    print("\n[✓] Applied production settings:")
    print("  - Interface: eth0 (external traffic only)")
    print("  - Confidence threshold: 0.85 (stricter)")
    print("  - Anomaly multiplier: 3.5 (less sensitive)")
    print("  - Localhost filtering: Enabled")
    print("\nNext steps:")
    print("  1. Enable localhost filtering: python3 toggle_localhost_filtering.py enable")
    print("  2. Restart server: ./start_server.sh")

def apply_testing_settings():
    """Apply recommended settings for testing attacks"""
    config = load_config()

    # Update settings
    if 'network' not in config:
        config['network'] = {}
    config['network']['interface'] = 'lo'

    if 'detection' not in config:
        config['detection'] = {}
    config['detection']['confidence_threshold'] = 0.7
    config['detection']['anomaly_multiplier'] = 2.5
    config['detection']['filter_localhost'] = False

    save_config(config)

    print("\n[✓] Applied testing settings:")
    print("  - Interface: lo (loopback for localhost testing)")
    print("  - Confidence threshold: 0.7 (more sensitive)")
    print("  - Anomaly multiplier: 2.5 (more sensitive)")
    print("  - Localhost filtering: Disabled in config")
    print("\nNext steps:")
    print("  1. Disable localhost filtering: python3 toggle_localhost_filtering.py disable")
    print("  2. Restart server: ./start_server.sh")
    print("  3. Run tests: sudo venv/bin/python -m tests.generate_anomalies --target 127.0.0.1 --syn-flood --count 200")

def apply_balanced_settings():
    """Apply balanced settings (some false positives acceptable)"""
    config = load_config()

    # Update settings
    if 'network' not in config:
        config['network'] = {}
    config['network']['interface'] = 'eth0'

    if 'detection' not in config:
        config['detection'] = {}
    config['detection']['confidence_threshold'] = 0.75
    config['detection']['anomaly_multiplier'] = 3.0
    config['detection']['filter_localhost'] = True

    save_config(config)

    print("\n[✓] Applied balanced settings:")
    print("  - Interface: eth0 (external traffic)")
    print("  - Confidence threshold: 0.75 (moderate)")
    print("  - Anomaly multiplier: 3.0 (moderate)")
    print("  - Localhost filtering: Enabled")
    print("\nNext steps:")
    print("  1. Enable localhost filtering: python3 toggle_localhost_filtering.py enable")
    print("  2. Restart server: ./start_server.sh")

def main():
    if not Path(CONFIG_FILE).exists():
        print(f"[!] Error: {CONFIG_FILE} not found")
        return 1

    if len(sys.argv) < 2:
        print("False Positive Fix Script")
        print("=" * 60)
        print("\nUsage:")
        print("  python3 fix_false_positives.py status      # Show current config")
        print("  python3 fix_false_positives.py production  # Minimize false positives")
        print("  python3 fix_false_positives.py testing     # Enable attack testing")
        print("  python3 fix_false_positives.py balanced    # Balanced settings")
        print("\nRecommended for your situation:")
        print("  If seeing too many alerts: python3 fix_false_positives.py production")
        print("  If testing attacks: python3 fix_false_positives.py testing")
        print()
        print_current_config()
        return 0

    command = sys.argv[1].lower()

    if command == "status":
        print_current_config()
    elif command == "production":
        apply_production_settings()
    elif command == "testing":
        apply_testing_settings()
    elif command == "balanced":
        apply_balanced_settings()
    else:
        print(f"Unknown command: {command}")
        print("Use: status, production, testing, or balanced")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
