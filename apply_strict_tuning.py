"""
Quick script to apply very strict tuning for home network monitoring.
This will significantly reduce false positives by:
1. Increasing confidence threshold to 98%
2. Increasing packet count requirement to 500
3. Adding more ignored attack types
4. Updating config.yaml with optimal settings
"""

import yaml
import os

def apply_strict_tuning():
    config_path = 'config.yaml'

    # Load current config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Apply very strict settings
    config['detection']['confidence_threshold'] = 0.98  # Very high - only super confident detections
    config['detection']['min_packet_threshold'] = 500   # High - only sustained traffic
    config['detection']['anomaly_multiplier'] = 7.0     # Higher - reduce anomaly sensitivity

    # Save updated config
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print("[+] Applied strict tuning to config.yaml:")
    print(f"    - Confidence threshold: 98%")
    print(f"    - Min packet threshold: 500 packets")
    print(f"    - Anomaly multiplier: 7.0x")
    print()
    print("[+] Restart the monitoring system for changes to take effect:")
    print("    python start_live_monitoring.py")
    print()
    print("[INFO] These settings will reduce false positives significantly")
    print("[INFO] If you still get false positives, we'll need to retrain the model")

if __name__ == '__main__':
    apply_strict_tuning()
