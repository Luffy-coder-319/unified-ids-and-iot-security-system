from scapy.all import IP, TCP, UDP, sniff
import numpy as np
import time
import threading
import subprocess
from collections import defaultdict

from src.models.predict import predict_threat
from src.data_processing.feature_engineer import engineer_features
from src.iot_security.device_profiler import DeviceProfiler

# Track flows by (src, dst, port, proto)
flows = defaultdict(lambda: {
    'packets': [],
    'start_time': None,
    'bytes': 0
})

alerts = []
profiler = DeviceProfiler()   # ✅ properly instantiated


def extract_live_features(flow):
    """Extract basic live features for ML model (expand as needed)."""
    if not flow['packets']:
        return None

    duration = time.time() - flow['start_time']
    pkt_count = len(flow['packets'])
    avg_pkt_size = flow['bytes'] / pkt_count if pkt_count else 0

    # Placeholder: you can add IAT, flags, etc.
    features = [duration, pkt_count, avg_pkt_size]
    return np.array(features).reshape(1, -1), duration, pkt_count


def analyse_packet(packet):
    """Process a single packet into flows and run threat detection."""
    if IP in packet:
        # Flow key = (src IP, dst IP, sport, protocol)
        sport = packet[TCP].sport if TCP in packet else packet[UDP].sport if UDP in packet else 0
        key = (packet[IP].src, packet[IP].dst, sport, packet[IP].proto)

        flow = flows[key]

        # Initialize flow start time
        if flow['start_time'] is None:
            flow['start_time'] = time.time()

        flow['packets'].append(packet)
        flow['bytes'] += len(packet)

        # IoT device profiling
        profiler.profile_device(key[0], len(packet))

        # Process every 10 packets in a flow
        if len(flow['packets']) % 10 == 0:
            features, duration, pkt_count = extract_live_features(flow)
            if features is not None:
                threat, severity = predict_threat(features)

                if threat != 'BENIGN':
                    alert = {
                        'time': time.time(),
                        'src': key[0],
                        'dst': key[1],
                        'threat': threat,
                        'severity': severity,
                        'context': f'Packets: {pkt_count}, Rate: {pkt_count/duration:.2f}/s'
                    }
                    alerts.append(alert)
                    print(f"[!] ALERT: {alert}")  # Debug output

                    # Defensive action if threat is high severity
                    if severity.lower() == 'high':
                        subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', key[0], '-j', 'DROP'])


def start_analyzer(interface='eth0'):
    """Start live packet analyzer in a background thread."""
    thread = threading.Thread(
        target=sniff,
        kwargs={'iface': interface, 'prn': analyse_packet, 'store': False},
        daemon=True
    )
    thread.start()
    print(f"[+] Analyzer running on {interface}")
    return thread
