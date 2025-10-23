"""
Quick script to apply home network tuning to reduce false positives.
This adjusts the detection thresholds for networks with gaming, streaming, VPN, etc.

Run this script to automatically update traffic_analyzer.py with more lenient settings.
"""

import os
import re
from pathlib import Path

def apply_tuning():
    """Apply home network tuning to traffic_analyzer.py"""

    analyzer_path = Path('src/network/traffic_analyzer.py')

    if not analyzer_path.exists():
        print(f"Error: {analyzer_path} not found!")
        return False

    print(f"Reading {analyzer_path}...")
    with open(analyzer_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes_made = []

    # Change 1: Increase confidence threshold from 95% to 98%
    old_confidence = "min_confidence = detection_config.get('confidence_threshold', 0.95)"
    new_confidence = "min_confidence = detection_config.get('confidence_threshold', 0.98)  # Tuned for home network"

    if old_confidence in content:
        content = content.replace(old_confidence, new_confidence)
        changes_made.append("✓ Confidence threshold: 95% → 98%")

    # Change 2: Increase packet threshold from 100 to 500
    old_packets = "min_packet_count = detection_config.get('min_packet_threshold', 100)"
    new_packets = "min_packet_count = detection_config.get('min_packet_threshold', 500)  # Tuned for home network"

    if old_packets in content:
        content = content.replace(old_packets, new_packets)
        changes_made.append("✓ Packet threshold: 100 → 500 packets")

    # Change 3: Add commonly misclassified attack types to ignore
    # Find the line with "is_threat = threat != 'BENIGN'"
    if "is_threat = threat != 'BENIGN'" in content:
        ignore_code = """
                    # Ignore attack types commonly misclassified on home networks
                    ignored_attack_types = {
                        'Mirai-greip_flood',  # Often triggered by gaming/P2P traffic
                        'DDoS-ICMP_Fragmentation',  # Often triggered by normal fragmentation
                    }
                    is_ignored_attack = threat in ignored_attack_types

                    # Layer 6: Threat classification
                    # Only alert on actual threats, not benign or ignored traffic
                    is_threat = threat != 'BENIGN' and threat != 'BenignTraffic' and not is_ignored_attack"""

        content = content.replace(
            "# Layer 6: Threat classification\n                    # Only alert on actual threats, not benign traffic\n                    is_threat = threat != 'BENIGN'",
            ignore_code
        )
        changes_made.append("✓ Ignoring Mirai-greip_flood and DDoS-ICMP_Fragmentation")

    # Write changes if any were made
    if content != original_content:
        # Backup original file
        backup_path = analyzer_path.with_suffix('.py.backup')
        print(f"\nCreating backup: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)

        # Write updated file
        print(f"Updating {analyzer_path}...")
        with open(analyzer_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("\n" + "="*60)
        print("HOME NETWORK TUNING APPLIED")
        print("="*60)
        for change in changes_made:
            print(change)

        print("\n" + "="*60)
        print("WHAT THIS MEANS")
        print("="*60)
        print("- Alerts only trigger at 98% confidence (instead of 95%)")
        print("- Alerts only trigger after 500 packets (instead of 100)")
        print("- Mirai and fragmentation attacks ignored (common false positives)")
        print("\nThis should significantly reduce false positives on:")
        print("  • Gaming traffic")
        print("  • Streaming services")
        print("  • VPN connections")
        print("  • P2P applications")

        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("1. Restart your monitoring system")
        print("2. Monitor for 1-2 hours")
        print("3. Check if alerts are reduced")
        print("4. If still too many alerts, increase thresholds further")
        print("\nTo revert changes, restore from:")
        print(f"  {backup_path}")

        return True
    else:
        print("No changes needed - file may already be tuned or has different format")
        return False

if __name__ == '__main__':
    print("="*60)
    print("HOME NETWORK FALSE POSITIVE REDUCTION")
    print("="*60)
    print("\nThis script will tune your detection system for home networks")
    print("with gaming, streaming, VPN, and P2P applications.\n")

    response = input("Apply tuning? (yes/no): ").strip().lower()

    if response in ['yes', 'y']:
        success = apply_tuning()
        if success:
            print("\n✓ Tuning applied successfully!")
        else:
            print("\n✗ Tuning failed or not needed")
    else:
        print("\nTuning cancelled.")
        print("\nFor manual tuning, see: docs/FALSE_POSITIVE_TUNING.md")
