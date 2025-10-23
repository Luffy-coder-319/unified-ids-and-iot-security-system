#!/usr/bin/env python3
"""
Clear all existing alerts from the system.
Use this to remove false positives after fixing the detection logic.
"""

import os
import json
from pathlib import Path

def clear_alerts():
    """Clear all alerts from the system"""

    # Files that store alerts
    alert_files = [
        "logs/alerts.jsonl",
        "logs/alerts.json",
        "data/alerts.json"
    ]

    cleared = []

    for file_path in alert_files:
        if os.path.exists(file_path):
            try:
                # Backup the file first
                backup_path = f"{file_path}.backup"
                os.rename(file_path, backup_path)
                print(f"[✓] Backed up {file_path} to {backup_path}")

                # Create empty file
                with open(file_path, 'w') as f:
                    if file_path.endswith('.json'):
                        json.dump([], f)
                    else:
                        pass  # Empty JSONL file

                cleared.append(file_path)
                print(f"[✓] Cleared {file_path}")
            except Exception as e:
                print(f"[!] Error clearing {file_path}: {e}")

    if cleared:
        print(f"\n[✓] Successfully cleared {len(cleared)} alert file(s)")
        print("\nNote: The alert manager's in-memory alerts will persist until server restart.")
        print("To fully clear alerts:")
        print("  1. Stop the server (Ctrl+C)")
        print("  2. Run this script")
        print("  3. Start the server again")
    else:
        print("[i] No alert files found to clear")

if __name__ == "__main__":
    print("=" * 60)
    print("Clear False Positive Alerts")
    print("=" * 60)
    print()

    response = input("This will clear all existing alerts. Continue? (y/N): ")

    if response.lower() in ['y', 'yes']:
        clear_alerts()
        print("\n[✓] Done! Restart the server to apply changes.")
    else:
        print("[i] Cancelled")
