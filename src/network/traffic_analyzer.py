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
from src.models.hybrid_detector import hybrid_predict_threat, get_detection_explanation
from src.data_processing.feature_engineer import engineer_features_from_flow
from src.iot_security.device_profiler import DeviceProfiler
from src.utils.notification_service import NotificationService
from src.utils.statistics_tracker import StatisticsTracker
from src.utils.alert_manager import AlertManager
from src.utils.response_actions import ResponseActionManager


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
# Add some dummy flows for demonstration
flows[("192.168.1.1", "192.168.1.2", 80, 6)] = {'packets': ["dummy"] * 5, 'start_time': time.time() - 10, 'bytes': 500}
flows[("192.168.1.2", "192.168.1.3", 443, 6)] = {'packets': ["dummy"] * 3, 'start_time': time.time() - 5, 'bytes': 300}
alerts = []
profiler = DeviceProfiler()   # properly instantiated

# === Initialize enhanced services ===
notification_service = None
statistics_tracker = StatisticsTracker()
alert_manager = AlertManager()
response_manager = None


def extract_live_features(flow):
    """Extract basic live features for ML model."""
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
                    # Use hybrid detector with higher threshold to reduce false positives
                    # Threshold 2.0+ means anomaly MSE must be 2x the training threshold
                    prediction = hybrid_predict_threat(features, anomaly_threshold_multiplier=2.5)
                    threat = prediction['attack']
                    severity = prediction['severity']
                    detection_method = prediction.get('detection_method', 'unknown')

                    # Debug: Print all predictions
                    print(f"[DEBUG] Flow {key[0]}:{key[2]}->{key[1]} - Prediction: {threat}, Severity: {severity}, Method: {detection_method}, Confidence: {prediction.get('confidence', 0):.1%}")

                    # Filter out likely false positives from normal traffic
                    is_localhost = key[0] in ('127.0.0.1', '::1') or key[1] in ('127.0.0.1', '::1')
                    is_low_rate = (pkt_count / duration if duration > 0 else 0) < 50

                    # Only alert if: not benign AND (high confidence OR not localhost low-rate traffic)
                    should_alert = (
                        threat != 'BENIGN' and
                        (prediction.get('confidence', 0) >= 0.7 or not (is_localhost and is_low_rate))
                    )

                    if should_alert:
                        alert = {
                            'time': time.time(),
                            'src': key[0],
                            'dst': key[1],
                            'threat': threat,
                            'severity': severity,
                            'context': f'Packets: {pkt_count}, Rate: {pkt_count/duration:.2f}/s',
                            'anomaly': prediction.get('anomaly', {})
                        }
                        alerts.append(alert)

                        # Thread-safe JSON logging
                        with log_lock:
                            alert_logger.info(alert)

                        print(f"[!] ALERT: {alert}")

                        # Track alert in alert manager
                        alert_id = alert_manager.add_alert(alert)

                        # Record statistics
                        statistics_tracker.record_alert(alert)

                        # Send notifications for critical threats
                        if notification_service:
                            notification_service.send_alert(alert, severity_threshold='high')

                        # Enhanced automated response
                        if response_manager:
                            response_result = response_manager.handle_threat(alert)
                            if response_result['success']:
                                print(f"[+] Automated response taken: {response_result['actions_taken']}")
                        else:
                            # Fallback to basic blocking for high severity
                            if severity and severity.lower() == 'high':
                                subprocess.run(
                                    ['sudo', 'iptables', '-A', 'INPUT', '-s', key[0], '-j', 'DROP']
                                )

        return None  # Always return None so Scapy doesn't try to unpack

    except Exception as e:
        print(f"[analyse_packet] Error: {e}")
        return None


def initialize_services(config=None):
    """
    Initialize notification, response, and other services.

    Args:
        config: Configuration dictionary
    """
    global notification_service, response_manager

    if config:
        # Initialize notification service if configured
        if 'notifications' in config:
            notification_service = NotificationService(config['notifications'])
            print("[+] Notification service initialized")

        # Initialize response manager if configured
        if 'response_actions' in config:
            response_manager = ResponseActionManager(config['response_actions'])
            print("[+] Response action manager initialized")


def start_analyzer(interface='eth0', config=None):
    """
    Start live packet analyzer in a background thread.

    Args:
        interface: Network interface to monitor
        config: Configuration dictionary for services
    """
    if os.geteuid() != 0:
        print("[!] Warning: Packet sniffer requires root privileges to capture packets. Skipping analyzer start. Please run the application as root or with NET_RAW capability.")
        return None

    # Initialize enhanced services
    initialize_services(config)

    thread = threading.Thread(
        target=sniff,
        kwargs={'iface': interface, 'prn': analyse_packet, 'store': False},
        daemon=True
    )
    thread.start()
    print(f"[+] Analyzer running on {interface}")
    return thread
