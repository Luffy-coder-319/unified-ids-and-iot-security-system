"""
IoT Device Detection and Fingerprinting

This module identifies IoT devices on the network by analyzing:
- MAC address OUI (Organizationally Unique Identifier)
- Traffic patterns
- Port usage
- Behavior fingerprinting
"""

import re
import socket
from collections import defaultdict
from datetime import datetime, timedelta

# Known IoT device manufacturers by MAC OUI (first 3 bytes)
IOT_DEVICE_OUIS = {
    # Smart Home Devices
    'B8:27:EB': 'Raspberry Pi Foundation',
    'DC:A6:32': 'Raspberry Pi Foundation',
    'E4:5F:01': 'Raspberry Pi Foundation',
    '28:CD:C1': 'Raspberry Pi Foundation',

    # Amazon Devices
    '44:65:0D': 'Amazon Echo',
    '50:DC:E7': 'Amazon Echo',
    '74:75:48': 'Amazon Echo/Fire TV',
    'FC:65:DE': 'Amazon Fire TV',
    '00:FC:8B': 'Amazon Echo',

    # Google Devices
    '54:60:09': 'Google Chromecast',
    'E0:B9:4D': 'Google Nest',
    '6C:AD:F8': 'Google Nest',
    'F4:F5:D8': 'Google Home',
    '48:D6:D5': 'Google Nest Hub',

    # Smart Cameras
    '00:62:6E': 'Wyze Cam',
    'D0:73:D5': 'Ring Camera',
    '00:12:FB': 'Nest Cam',
    '18:B4:30': 'Nest Cam',
    'B4:5D:50': 'Arlo Camera',

    # Smart Lights/Hue
    '00:17:88': 'Philips Hue',
    'EC:B5:FA': 'Philips Hue',

    # Smart Thermostats
    '18:B4:30': 'Nest Thermostat',
    '64:16:66': 'Nest Thermostat',

    # Smart Plugs
    '50:C7:BF': 'TP-Link Smart Plug',
    '1C:3B:F3': 'TP-Link Smart Plug',
    'B4:E6:2D': 'Wemo Switch',

    # IoT Development Boards
    '98:D3:31': 'Espressif (ESP8266)',
    '98:F4:AB': 'Espressif (ESP32)',
    '24:0A:C4': 'Espressif (ESP32)',
    'A4:CF:12': 'Espressif (ESP8266)',
    '5C:CF:7F': 'Espressif (ESP32)',

    # Arduino
    '00:1E:C0': 'Arduino',
    '90:A2:DA': 'Arduino',

    # Other IoT
    '00:17:D5': 'Samsung SmartThings',
    '28:6D:97': 'Sonos Speaker',
    'B8:E9:37': 'Sonos Speaker',
}

# Common IoT device behaviors
IOT_PORT_PATTERNS = {
    'mqtt': [1883, 8883],  # MQTT (IoT messaging)
    'coap': [5683, 5684],  # CoAP (IoT protocol)
    'upnp': [1900],        # UPnP (device discovery)
    'mdns': [5353],        # mDNS (service discovery)
    'homekit': [51827],    # Apple HomeKit
    'zigbee': [17754, 17755],  # Zigbee
    'zwave': [41120],      # Z-Wave
}

# Cloud services used by IoT devices
IOT_CLOUD_DOMAINS = {
    'amazon': ['amazonaws.com', 'amazon-adsystem.com'],
    'google': ['googleapis.com', 'google.com'],
    'apple': ['icloud.com', 'apple.com'],
    'samsung': ['samsungiotcloud.com'],
    'tuya': ['tuyaus.com', 'tuyacn.com'],  # Generic IoT platform
    'alibaba': ['alibabacloud.com'],
}


class IoTDeviceDetector:
    """
    Detects and profiles IoT devices on the network.
    """

    def __init__(self):
        self.devices = {}  # {mac_address: device_info}
        self.ip_to_mac = {}  # {ip_address: mac_address}
        self.hostname_cache = {}  # {ip_address: hostname}

    def get_hostname(self, ip_address):
        """
        Resolve hostname for an IP address using reverse DNS.

        Args:
            ip_address: IP address to resolve

        Returns:
            str: Hostname or None if resolution fails
        """
        # Check cache first
        if ip_address in self.hostname_cache:
            return self.hostname_cache[ip_address]

        try:
            # Try reverse DNS lookup (with short timeout)
            hostname = socket.gethostbyaddr(ip_address)[0]

            # Clean up the hostname (remove domain suffix for readability)
            if '.' in hostname:
                # Keep only the first part (e.g., "johns-iphone" from "johns-iphone.local")
                clean_name = hostname.split('.')[0]
            else:
                clean_name = hostname

            # Cache it
            self.hostname_cache[ip_address] = clean_name
            return clean_name

        except (socket.herror, socket.gaierror, socket.timeout, OSError):
            # DNS lookup failed - cache None to avoid repeated lookups
            self.hostname_cache[ip_address] = None
            return None

    def generate_friendly_name(self, device_profile):
        """
        Generate a friendly display name for a device.

        Args:
            device_profile: Device profile dict

        Returns:
            str: Friendly name for the device
        """
        ip_address = device_profile.get('ip_address')
        device_type = device_profile.get('device_type', 'Unknown Device')
        hostname = device_profile.get('hostname')

        # Priority 1: Use hostname if available and descriptive
        if hostname and hostname != ip_address and len(hostname) > 3:
            return hostname

        # Priority 2: Use device type if identified
        if device_type and device_type != 'unknown' and device_type != 'Unknown Device':
            return device_type

        # Priority 3: Use last octet of IP for identification
        if ip_address:
            last_octet = ip_address.split('.')[-1]
            return f"Device-{last_octet}"

        return "Unknown Device"

    def identify_device_by_mac(self, mac_address):
        """
        Identify device type by MAC address OUI.

        Args:
            mac_address: MAC address in format "AA:BB:CC:DD:EE:FF"

        Returns:
            dict with device info or None
        """
        if not mac_address or mac_address == 'N/A':
            return None

        # Normalize MAC address
        mac_upper = mac_address.upper()

        # Extract OUI (first 3 bytes)
        oui = ':'.join(mac_upper.split(':')[:3])

        if oui in IOT_DEVICE_OUIS:
            return {
                'type': 'iot',
                'manufacturer': IOT_DEVICE_OUIS[oui],
                'oui': oui,
                'confidence': 'high',
                'method': 'mac_fingerprint'
            }

        return None

    def identify_device_by_behavior(self, ip_address, ports_used, protocols_seen):
        """
        Identify device by network behavior patterns.

        Args:
            ip_address: Device IP
            ports_used: List of ports the device communicates on
            protocols_seen: List of protocols observed

        Returns:
            dict with device info or None
        """
        iot_indicators = []

        # Check for IoT-specific ports
        for protocol, ports in IOT_PORT_PATTERNS.items():
            if any(port in ports_used for port in ports):
                iot_indicators.append(f'{protocol}_protocol')

        # Check protocol patterns
        if 'MQTT' in protocols_seen:
            iot_indicators.append('mqtt_traffic')

        if iot_indicators:
            return {
                'type': 'iot',
                'indicators': iot_indicators,
                'confidence': 'medium',
                'method': 'behavior_analysis'
            }

        return None

    def register_device(self, ip_address, mac_address=None, packet_info=None):
        """
        Register or update a device in the detection system.

        Args:
            ip_address: Device IP address
            mac_address: Device MAC address (if available)
            packet_info: Additional packet information

        Returns:
            Device profile dict
        """
        # Skip localhost
        if ip_address in ('127.0.0.1', '::1'):
            return None

        # Check if device already profiled
        if mac_address and mac_address in self.devices:
            device = self.devices[mac_address]
            device['last_seen'] = datetime.now()
            device['packet_count'] = device.get('packet_count', 0) + 1
            return device

        # Try to resolve hostname
        hostname = self.get_hostname(ip_address)

        # New device detection
        device_profile = {
            'ip_address': ip_address,
            'mac_address': mac_address,
            'hostname': hostname,
            'first_seen': datetime.now(),
            'last_seen': datetime.now(),
            'packet_count': 1,
            'is_iot': False,
            'device_type': 'unknown',
            'confidence': 'unknown',
            'ports_used': set(),
            'protocols_seen': set(),
        }

        # Try MAC-based identification
        if mac_address:
            mac_info = self.identify_device_by_mac(mac_address)
            if mac_info:
                device_profile['is_iot'] = True
                device_profile['device_type'] = mac_info.get('manufacturer', 'Unknown IoT Device')
                device_profile['confidence'] = mac_info['confidence']
                device_profile['detection_method'] = mac_info['method']

        # Generate friendly name
        device_profile['friendly_name'] = self.generate_friendly_name(device_profile)

        # Store device
        if mac_address:
            self.devices[mac_address] = device_profile
            self.ip_to_mac[ip_address] = mac_address

        return device_profile

    def update_device_behavior(self, ip_address, port=None, protocol=None):
        """
        Update device behavior profile.

        Args:
            ip_address: Device IP
            port: Port number being used
            protocol: Protocol name
        """
        mac_address = self.ip_to_mac.get(ip_address)

        if mac_address and mac_address in self.devices:
            device = self.devices[mac_address]

            if port:
                device['ports_used'].add(port)
            if protocol:
                device['protocols_seen'].add(protocol)

            # Re-evaluate if not yet identified as IoT
            if not device['is_iot']:
                behavior_info = self.identify_device_by_behavior(
                    ip_address,
                    list(device['ports_used']),
                    list(device['protocols_seen'])
                )

                if behavior_info:
                    device['is_iot'] = True
                    device['device_type'] = 'IoT Device (Behavior-based)'
                    device['confidence'] = behavior_info['confidence']
                    device['detection_method'] = behavior_info['method']
                    device['iot_indicators'] = behavior_info['indicators']

    def get_device_info(self, ip_address=None, mac_address=None):
        """
        Get device information by IP or MAC.

        Args:
            ip_address: Device IP
            mac_address: Device MAC

        Returns:
            Device profile dict or None
        """
        if mac_address and mac_address in self.devices:
            return self.devices[mac_address]

        if ip_address and ip_address in self.ip_to_mac:
            mac = self.ip_to_mac[ip_address]
            return self.devices.get(mac)

        return None

    def get_all_devices(self):
        """
        Get all detected devices (IoT and non-IoT).

        Returns:
            List of all device profiles
        """
        devices_list = []
        for device in self.devices.values():
            # Create a copy to avoid modifying the original
            device_copy = device.copy()
            # Ensure sets are converted to lists for JSON serialization
            if 'ports_used' in device_copy and isinstance(device_copy['ports_used'], set):
                device_copy['ports_used'] = list(device_copy['ports_used'])
            if 'protocols_seen' in device_copy and isinstance(device_copy['protocols_seen'], set):
                device_copy['protocols_seen'] = list(device_copy['protocols_seen'])
            devices_list.append(device_copy)
        return devices_list

    def get_all_iot_devices(self):
        """
        Get all detected IoT devices.

        Returns:
            List of IoT device profiles
        """
        all_devices = self.get_all_devices()
        return [device for device in all_devices if device.get('is_iot', False)]

    def get_device_summary(self):
        """
        Get summary statistics of detected devices.

        Returns:
            dict with summary stats
        """
        iot_devices = self.get_all_iot_devices()

        return {
            'total_devices': len(self.devices),
            'iot_devices': len(iot_devices),
            'non_iot_devices': len(self.devices) - len(iot_devices),
            'high_confidence': sum(1 for d in iot_devices if d.get('confidence') == 'high'),
            'medium_confidence': sum(1 for d in iot_devices if d.get('confidence') == 'medium'),
            'device_types': list(set(d.get('device_type') for d in iot_devices)),
        }

    def is_iot_device(self, ip_address=None, mac_address=None):
        """
        Quick check if an IP/MAC is an IoT device.

        Args:
            ip_address: Device IP
            mac_address: Device MAC

        Returns:
            bool
        """
        device = self.get_device_info(ip_address, mac_address)
        return device.get('is_iot', False) if device else False


# Global instance
iot_detector = IoTDeviceDetector()
