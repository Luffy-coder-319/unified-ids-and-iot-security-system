#!/usr/bin/env python3
"""
Display IoT devices detected by the system.
Alternative to using curl + jq.
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api"

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def get_iot_summary():
    """Get and display IoT device summary."""
    try:
        response = requests.get(f"{API_BASE}/iot/summary")
        response.raise_for_status()
        data = response.json()

        print_section("IoT Device Summary")
        print(f"Total Devices Detected:    {data.get('total_devices', 0)}")
        print(f"IoT Devices:              {data.get('iot_devices', 0)}")
        print(f"Non-IoT Devices:          {data.get('non_iot_devices', 0)}")
        print(f"High Confidence:          {data.get('high_confidence', 0)}")
        print(f"Medium Confidence:        {data.get('medium_confidence', 0)}")

        if data.get('device_types'):
            print(f"\nDevice Types Found:")
            for dtype in data['device_types']:
                print(f"  - {dtype}")

        return data

    except requests.exceptions.ConnectionError:
        print("[!] Error: Cannot connect to server. Is it running?")
        print("    Start server with: ./start_server.sh")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"[!] HTTP Error: {e}")
        print("    The server may not have loaded the IoT detection module yet.")
        print("    Try restarting the server.")
        return None
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

def get_iot_devices():
    """Get and display all IoT devices."""
    try:
        response = requests.get(f"{API_BASE}/iot/devices")
        response.raise_for_status()
        data = response.json()

        devices = data.get('devices', [])

        if not devices:
            print_section("No IoT Devices Detected Yet")
            print("\nPossible reasons:")
            print("  1. No IoT devices are on the network")
            print("  2. IoT devices haven't sent traffic yet")
            print("  3. Server just started (wait a few minutes)")
            print("\nWhat to do:")
            print("  - Ping your IoT devices to generate traffic")
            print("  - Wait for normal IoT device activity")
            print("  - Check if server is capturing packets:")
            print("    curl http://localhost:8000/api/flows")
            return

        print_section(f"Detected IoT Devices ({len(devices)})")

        for i, device in enumerate(devices, 1):
            print(f"\n[{i}] {device.get('device_type', 'Unknown Device')}")
            print(f"    IP Address:       {device.get('ip_address', 'N/A')}")
            print(f"    MAC Address:      {device.get('mac_address', 'N/A')}")
            print(f"    Confidence:       {device.get('confidence', 'unknown').upper()}")
            print(f"    Detection Method: {device.get('detection_method', 'N/A')}")
            print(f"    Packets Seen:     {device.get('packet_count', 0)}")

            if device.get('first_seen'):
                print(f"    First Seen:       {device['first_seen']}")
            if device.get('last_seen'):
                print(f"    Last Seen:        {device['last_seen']}")

            if device.get('ports_used'):
                ports = ', '.join(str(p) for p in sorted(device['ports_used'])[:10])
                print(f"    Ports Used:       {ports}")

            if device.get('protocols_seen'):
                protocols = ', '.join(device['protocols_seen'])
                print(f"    Protocols:        {protocols}")

    except requests.exceptions.ConnectionError:
        print("[!] Error: Cannot connect to server.")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            print("[!] Server Error: IoT detection module may not be loaded.")
            print("    Restart the server to load the new code:")
            print("    Ctrl+C in server terminal, then: ./start_server.sh")
        else:
            print(f"[!] HTTP Error: {e}")
        return None
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

def get_device_by_ip(ip_address):
    """Get details for a specific device."""
    try:
        response = requests.get(f"{API_BASE}/iot/devices/{ip_address}")
        response.raise_for_status()
        device = response.json()

        print_section(f"Device Details: {ip_address}")
        print(json.dumps(device, indent=2))

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"[!] Device {ip_address} not found.")
        else:
            print(f"[!] Error: {e}")
    except Exception as e:
        print(f"[!] Error: {e}")

def main():
    import sys

    print("=" * 70)
    print(" IoT Device Detection Viewer")
    print("=" * 70)

    if len(sys.argv) > 1:
        # Get specific device
        ip = sys.argv[1]
        get_device_by_ip(ip)
    else:
        # Show summary and all devices
        summary = get_iot_summary()

        if summary is not None:
            get_iot_devices()

        print("\n" + "=" * 70)
        print(" Usage:")
        print("   python3 show_iot_devices.py              # Show all devices")
        print("   python3 show_iot_devices.py 192.168.1.100  # Show specific device")
        print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
