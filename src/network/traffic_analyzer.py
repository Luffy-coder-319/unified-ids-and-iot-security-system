import os
import time
import threading
import subprocess
import logging
import json
from collections import defaultdict
from logging.handlers import RotatingFileHandler
from threading import Lock
from scapy.all import IP, TCP, UDP, sniff

from src.models.predict import predict_threat
from src.data_processing.feature_engineer import engineer_features_from_flow
from src.iot_security.device_profiler import DeviceProfiler


# === Ensure log directory exists ===
os.makedirs("logs", exist_ok=True)

# === JSON-based alert logger setup ===
log_lock = Lock()

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created)),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)

alert_logger = logging.getLogger("alert_logger")
alert_logger.setLevel(logging.INFO)

handler = RotatingFileHandler("logs/alerts.jsonl", maxBytes=1_000_000, backupCount=5)
handler.setFormatter(JsonFormatter())
alert_logger.addHandler(handler)


# === Flow tracking setup ===
flows = defaultdict(lambda: {'packets': [], 'start_time': None, 'bytes': 0})
alerts = []
profiler = DeviceProfiler()   # properly instantiated


def extract_live_features(flow):
    """Extract basic live features for ML model (expand as needed)."""
    if not flow['packets']:
        return None

    duration = time.time() - flow['start_time']
    pkt_count = len(flow['packets'])

    # Full CICIDS-style feature engineering
    features_df = engineer_features_from_flow(flow['packets'])

    return features_df, duration, pkt_count


def analyse_packet(packet):
    """Process a single packet into flows and run threat detection."""
    try:
        if IP in packet:
            sport = (
                packet[TCP].sport if TCP in packet
                else packet[UDP].sport if UDP in packet
                else 0
            )
            key = (packet[IP].src, packet[IP].dst, sport, packet[IP].proto)

            flow = flows[key]

            if flow['start_time'] is None:
                flow['start_time'] = time.time()

            flow['packets'].append(packet)
            flow['bytes'] += len(packet)

            profiler.profile_device(key[0], len(packet))

            # Analyze every 10 packets in this flow
            if len(flow['packets']) % 10 == 0:
                result = extract_live_features(flow)
                if result is not None:
                    features, duration, pkt_count = result
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

                        # Thread-safe JSON logging
                        with log_lock:
                            alert_logger.info(alert)

                        print(f"[!] ALERT: {alert}")

                        # Defensive action for high severity
                        if severity and severity.lower() == 'high':
                            subprocess.run(
                                ['sudo', 'iptables', '-A', 'INPUT', '-s', key[0], '-j', 'DROP']
                            )
                    else:
                        print("Normal")

        return None  # Always return None so Scapy doesn't try to unpack

    except Exception as e:
        print(f"[analyse_packet] Error: {e}")
        return None


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
