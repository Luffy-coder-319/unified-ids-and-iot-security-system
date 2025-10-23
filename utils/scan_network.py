#!/usr/bin/env python3
"""
Network Scanner - Discover devices on your local network
Identifies IoT devices by MAC address fingerprinting
"""

import subprocess
import re
import sys
from scapy.all import ARP, Ether, srp, conf

# Suppress Scapy warnings
conf.verb = 0

def get_local_network():
    """Get the local network CIDR (e.g., 192.168.1.0/24)"""
    try:
        # Get all network interfaces
        result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)

        # Look for non-loopback interfaces with valid networks
        interfaces = []
        current_iface = None

        for line in result.stdout.split('\n'):
            # Match interface name
            iface_match = re.match(r'\d+:\s+(\S+):', line)
            if iface_match:
                current_iface = iface_match.group(1)
                continue

            # Match IP address with CIDR
            ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/(\d+)', line)
            if ip_match and current_iface:
                ip = ip_match.group(1)
                prefix = int(ip_match.group(2))

                # Skip loopback
                if ip.startswith('127.'):
                    continue

                # Calculate network address based on prefix
                ip_parts = [int(p) for p in ip.split('.')]

                if prefix >= 24:
                    # /24 or larger (e.g., /32)
                    network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
                elif prefix >= 16:
                    # /16 to /23
                    network = f"{ip_parts[0]}.{ip_parts[1]}.0.0/16"
                elif prefix >= 8:
                    # /8 to /15
                    network = f"{ip_parts[0]}.0.0.0/8"
                else:
                    continue

                interfaces.append((network, current_iface, ip, prefix))

        if interfaces:
            # Prefer interfaces with /24 networks (most common for local networks)
            interfaces.sort(key=lambda x: abs(x[3] - 24))
            network, iface, ip, prefix = interfaces[0]
            print(f"[+] Your IP: {ip}/{prefix}")
            print(f"[+] Scanning network range: {network}")
            return network, iface

    except Exception as e:
        print(f"Error detecting network: {e}")

    # Fallback - ask user
    print("\n[!] Could not auto-detect network range.")
    print("[*] Common network ranges:")
    print("    1. 192.168.1.0/24 (most home routers)")
    print("    2. 192.168.0.0/24 (some routers)")
    print("    3. 10.0.0.0/24 (corporate networks)")
    print("    4. 172.16.0.0/24 (some private networks)")

    user_input = input("\n[?] Enter network to scan (or press Enter for 192.168.1.0/24): ").strip()
    if user_input:
        return user_input, None
    return "192.168.1.0/24", None

def scan_network(network):
    """Scan network for active devices using ARP"""
    print(f"\n[*] Scanning network: {network}")
    print("[*] This may take 10-30 seconds...\n")

    # Create ARP request
    arp = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send packet and receive responses
    result = srp(packet, timeout=3, verbose=0)[0]

    devices = []
    for sent, received in result:
        devices.append({
            'ip': received.psrc,
            'mac': received.hwsrc
        })

    return devices

def identify_iot_device(mac):
    """Identify if device is IoT based on MAC OUI"""
    # IoT device manufacturers by MAC OUI (first 3 bytes)
    IOT_OUIS = {
        'B8:27:EB': 'Raspberry Pi Foundation',
        'DC:A6:32': 'Raspberry Pi Foundation',
        'E4:5F:01': 'Raspberry Pi Foundation',
        '28:CD:C1': 'Raspberry Pi Foundation',
        '44:65:0D': 'Amazon Echo',
        '50:DC:E7': 'Amazon Echo',
        '74:75:48': 'Amazon Echo/Fire TV',
        'FC:65:DE': 'Amazon Fire TV',
        '00:FC:8B': 'Amazon Echo',
        '54:60:09': 'Google Chromecast',
        'E0:B9:4D': 'Google Nest',
        '6C:AD:F8': 'Google Nest',
        'F4:F5:D8': 'Google Home',
        '48:D6:D5': 'Google Nest Hub',
        '00:62:6E': 'Wyze Cam',
        'D0:73:D5': 'Ring Camera',
        '00:12:FB': 'Nest Cam',
        '18:B4:30': 'Nest Cam/Thermostat',
        'B4:5D:50': 'Arlo Camera',
        '00:17:88': 'Philips Hue',
        'EC:B5:FA': 'Philips Hue',
        '64:16:66': 'Nest Thermostat',
        '50:C7:BF': 'TP-Link Smart Plug',
        '1C:3B:F3': 'TP-Link Smart Plug',
        'B4:E6:2D': 'Wemo Switch',
        '98:D3:31': 'ESP8266 (IoT Dev Board)',
        '98:F4:AB': 'ESP32 (IoT Dev Board)',
        '24:0A:C4': 'ESP32 (IoT Dev Board)',
        'A4:CF:12': 'ESP8266 (IoT Dev Board)',
        '5C:CF:7F': 'ESP32 (IoT Dev Board)',
        '00:1E:C0': 'Arduino',
        '90:A2:DA': 'Arduino',
        '00:17:D5': 'Samsung SmartThings',
        '28:6D:97': 'Sonos Speaker',
        'B8:E9:37': 'Sonos Speaker',
    }

    # Normalize MAC and extract OUI
    mac_upper = mac.upper()
    oui = ':'.join(mac_upper.split(':')[:3])

    if oui in IOT_OUIS:
        return True, IOT_OUIS[oui]

    return False, None

def main():
    print("=" * 60)
    print("IoT Device Scanner - Network Discovery")
    print("=" * 60)

    # Get network to scan
    network, iface = get_local_network()

    if iface:
        print(f"[+] Detected interface: {iface}")

    # Scan network
    devices = scan_network(network)

    if not devices:
        print("[!] No devices found. You may need to:")
        print("    1. Run with sudo: sudo python3 scan_network.py")
        print("    2. Check your network connection")
        print("    3. Try a different network range")
        return

    print(f"[+] Found {len(devices)} active devices\n")
    print("=" * 60)

    iot_count = 0

    for i, device in enumerate(devices, 1):
        is_iot, device_type = identify_iot_device(device['mac'])

        print(f"\n[Device {i}]")
        print(f"  IP:  {device['ip']}")
        print(f"  MAC: {device['mac']}")

        if is_iot:
            print(f"  Type: {device_type}")
            print(f"  IoT:  YES")
            iot_count += 1
        else:
            print(f"  Type: Unknown (not in IoT database)")
            print(f"  IoT:  NO")

    print("\n" + "=" * 60)
    print(f"\n[Summary]")
    print(f"  Total devices: {len(devices)}")
    print(f"  IoT devices:   {iot_count}")
    print(f"  Other devices: {len(devices) - iot_count}")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        main()
    except PermissionError:
        print("\n[ERROR] This script requires root privileges.")
        print("Please run with: sudo python3 scan_network.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[!] Scan interrupted by user")
        sys.exit(0)
