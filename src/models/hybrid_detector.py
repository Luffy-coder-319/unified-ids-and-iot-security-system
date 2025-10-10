"""
Hybrid Detection System combining anomaly detection, classification, and rule-based detection.
This improves detection accuracy for live traffic that differs from training data.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from src.models.predict import detect_anormaly, classify_attack


def rule_based_detection(features_df):
    """
    Rule-based detection for common attack patterns.

    Args:
        features_df: DataFrame with CICIDS2017 features

    Returns:
        dict with 'attack' and 'confidence' or None if no rules match
    """
    if features_df.empty:
        return None

    features = features_df.iloc[0]

    # Rule 1: SYN Flood Detection
    syn_count = features.get('SYN Flag Count', 0)
    total_packets = features.get('Total Fwd Packets', 0) + features.get('Total Backward Packets', 0)
    if total_packets > 0:
        syn_ratio = syn_count / total_packets
        if syn_ratio > 0.7 and syn_count > 20:
            pkt_rate = features.get('Flow Packets/s', 0)
            if pkt_rate > 100:
                return {'attack': 'DoS Hulk', 'confidence': 0.85, 'rule': 'SYN_FLOOD'}

    # Rule 2: Port Scan Detection
    # High packet count with low bytes, multiple flags
    rst_count = features.get('RST Flag Count', 0)
    pkt_count = total_packets
    if pkt_count > 10:
        avg_pkt_size = features.get('Average Packet Size', 0)
        if avg_pkt_size < 100 and (syn_count > 5 or rst_count > 5):
            return {'attack': 'PortScan', 'confidence': 0.75, 'rule': 'PORT_SCAN'}

    # Rule 3: UDP Flood
    # All UDP packets, high rate
    fwd_packets = features.get('Total Fwd Packets', 0)
    tcp_packets = syn_count + features.get('ACK Flag Count', 0) + features.get('FIN Flag Count', 0)
    if tcp_packets == 0 and fwd_packets > 20:
        pkt_rate = features.get('Flow Packets/s', 0)
        if pkt_rate > 200:
            return {'attack': 'DDoS', 'confidence': 0.80, 'rule': 'UDP_FLOOD'}

    # Rule 4: High packet rate (generic DoS)
    pkt_rate = features.get('Flow Packets/s', 0)
    if pkt_rate > 500:
        return {'attack': 'DoS Hulk', 'confidence': 0.70, 'rule': 'HIGH_RATE'}

    # Rule 5: Abnormal packet size patterns
    pkt_std = features.get('Packet Length Std', 0)
    pkt_mean = features.get('Packet Length Mean', 0)
    if pkt_mean > 0 and pkt_std / pkt_mean > 2.0 and total_packets > 10:
        return {'attack': 'DDoS', 'confidence': 0.65, 'rule': 'PKT_SIZE_ANOMALY'}

    return None


def hybrid_predict_threat(features,
                         anomaly_threshold_multiplier=0.9,
                         rule_confidence_threshold=0.7):
    """
    Hybrid threat detection combining ML models and rules.

    Args:
        features: Feature array or DataFrame
        anomaly_threshold_multiplier: Threshold for anomaly detection (0.9 = 90% of threshold)
        rule_confidence_threshold: Minimum confidence for rule-based detection

    Returns:
        dict with attack type, severity, confidence, and detection method
    """
    # Convert to DataFrame if needed
    if isinstance(features, np.ndarray):
        features_df = pd.DataFrame([features])
    elif isinstance(features, pd.DataFrame):
        features_df = features
    else:
        features_df = pd.DataFrame([features])

    # 1. Run all detection methods
    anomaly_info = detect_anormaly(features_df)
    ml_prediction, ml_severity = classify_attack(features_df)
    rule_result = rule_based_detection(features_df)

    # 2. Decision fusion logic
    attack_type = 'BENIGN'
    severity = 'low'
    confidence = 0.0
    detection_method = 'none'
    details = {}

    # Check anomaly detection
    is_anomaly = anomaly_info['mse_normalized'] > anomaly_threshold_multiplier

    # Priority 1: Rule-based detection (high confidence)
    if rule_result and rule_result['confidence'] >= rule_confidence_threshold:
        attack_type = rule_result['attack']
        severity = 'high' if rule_result['confidence'] > 0.8 else 'medium'
        confidence = rule_result['confidence']
        detection_method = f"rule:{rule_result['rule']}"
        details['rule_matched'] = rule_result['rule']

    # Priority 2: ML classifier (if not BENIGN)
    elif ml_prediction != 'BENIGN':
        attack_type = ml_prediction
        severity = ml_severity
        confidence = 0.75  # Default confidence for ML
        detection_method = 'classifier'

    # Priority 3: Anomaly detection override
    elif is_anomaly:
        attack_type = 'Anomaly Detected'
        severity = anomaly_info['severity']
        confidence = anomaly_info['confidence']
        detection_method = 'anomaly'

        # Try to classify anomaly type using rules with lower threshold
        if rule_result and rule_result['confidence'] >= 0.5:
            attack_type = f"{rule_result['attack']} (Anomaly)"
            details['likely_attack'] = rule_result['attack']
            details['rule_confidence'] = rule_result['confidence']

    # Priority 4: Everything agrees it's benign
    else:
        attack_type = 'BENIGN'
        severity = 'low'
        confidence = 0.9 if not is_anomaly else 0.5
        detection_method = 'all_agree'

    return {
        'attack': attack_type,
        'severity': severity,
        'confidence': confidence,
        'detection_method': detection_method,
        'anomaly': anomaly_info,
        'ml_prediction': ml_prediction,
        'rule_result': rule_result,
        'details': details
    }


def get_detection_explanation(result):
    """
    Generate human-readable explanation of detection result.

    Args:
        result: Output from hybrid_predict_threat()

    Returns:
        str: Explanation text
    """
    method = result['detection_method']
    attack = result['attack']

    if method.startswith('rule:'):
        rule_name = method.split(':')[1]
        return f"Detected {attack} using rule {rule_name} (confidence: {result['confidence']:.1%})"
    elif method == 'classifier':
        return f"ML classifier identified {attack} (severity: {result['severity']})"
    elif method == 'anomaly':
        mse = result['anomaly']['mse_normalized']
        return f"Anomaly detected with MSE {mse:.2f}x threshold (classified as {attack})"
    elif method == 'all_agree':
        return "No threats detected - traffic appears benign"
    else:
        return f"Detected {attack} via {method}"
