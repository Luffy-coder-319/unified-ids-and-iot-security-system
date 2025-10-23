"""
Feature Engineering Module for Network IDS
Supports CICIoT2023 dataset format (46 features).
Optimized for IoT device traffic detection and real-time analysis.
CICIoT2023 Features:
- Flow duration and rates
- Protocol flags and types
- Statistical measures (min, max, avg, std)
- Inter-arrival times
- Protocol indicators (HTTP, HTTPS, DNS, SSH, etc.)
- Advanced metrics (Magnitude, Radius, Covariance, Weight)
"""

import numpy as np
import pandas as pd
from scapy.all import TCP, UDP, IP, ICMP, ARP
from typing import List, Dict, Optional
import json
from pathlib import Path

# --- Load the exact feature list required by the models ---
# NOTE: We use CICIoT2023 features (46) for the system
try:
    FEATURE_INFO_PATH = Path('trained_models/retrained/feature_info.json')
    with open(FEATURE_INFO_PATH, 'r') as f:
        _feature_info = json.load(f)
    REQUIRED_FEATURES = _feature_info.get("feature_names", [])
    if not REQUIRED_FEATURES:
        raise ValueError("Feature list is empty in feature_info.json")
except Exception as e:
    # Fallback to CICIoT2023 feature list since that's what the system uses
    print(f"CRITICAL: Failed to load feature list from {FEATURE_INFO_PATH}: {e}")
    REQUIRED_FEATURES = [
        'flow_duration', 'Header_Length', 'Protocol Type', 'Duration', 'Rate', 'Drate',
        'fin_flag_number', 'syn_flag_number', 'psh_flag_number', 'ack_flag_number',
        'ece_flag_number', 'cwr_flag_number', 'syn_count', 'fin_count', 'urg_count',
        'rst_count', 'HTTP', 'HTTPS', 'DNS', 'Telnet', 'SMTP', 'SSH', 'IRC', 'TCP',
        'UDP', 'DHCP', 'ARP', 'ICMP', 'IPv', 'Tot sum', 'Min', 'Max', 'AVG',
        'Tot size', 'IAT', 'Covariance', 'Variance'
    ]

def engineer_features_from_flow(packets):
    """
    Extract the exact features required by the ML models from a list of Scapy packets.

    Args:
        packets: List of Scapy packet objects

    Returns:
        pd.DataFrame: Single-row DataFrame with the required model features.
    """
    if not packets:
        return pd.DataFrame()

    # --- Basic packet analysis ---
    first_pkt = packets[0]
    src_ip = first_pkt[IP].src if IP in first_pkt else None
    dst_ip = first_pkt[IP].dst if IP in first_pkt else None

    # Protocol detection
    protocol = first_pkt[IP].proto if IP in first_pkt else 0

    # --- Timing and basic metrics ---
    times = np.array([pkt.time for pkt in packets])
    sizes = np.array([len(pkt) for pkt in packets])

    flow_duration = times[-1] - times[0] if len(times) > 1 else 0.0
    total_packets = len(packets)
    total_bytes = sizes.sum()

    # --- Header length calculation ---
    header_lengths = []
    for pkt in packets:
        if IP in pkt:
            ip_hdr = pkt[IP].ihl * 4 if pkt[IP].ihl else 20
            if TCP in pkt:
                tcp_hdr = (pkt[TCP].dataofs or 5) * 4
                header_lengths.append(ip_hdr + tcp_hdr)
            elif UDP in pkt:
                header_lengths.append(ip_hdr + 8)
            else:
                header_lengths.append(ip_hdr)
        else:
            header_lengths.append(0)

    header_length = np.mean(header_lengths) if header_lengths else 0

    # --- Protocol type (numeric encoding) ---
    # TCP=6, UDP=17, ICMP=1, etc.
    protocol_type = protocol

    # --- Duration (same as flow_duration) ---
    duration = flow_duration

    # --- Rates ---
    rate = total_packets / duration if duration > 0 else total_packets  # Total packet rate

    # Split by direction
    fwd_packets = []
    bwd_packets = []
    fwd_bytes = 0
    bwd_bytes = 0

    for pkt in packets:
        if IP not in pkt:
            continue
        pkt_size = len(pkt)
        if pkt[IP].src == src_ip:
            fwd_packets.append(pkt)
            fwd_bytes += pkt_size
        else:
            bwd_packets.append(pkt)
            bwd_bytes += pkt_size

    srate = len(fwd_packets) / duration if duration > 0 else 0.0  # Source rate
    drate = len(bwd_packets) / duration if duration > 0 else 0.0  # Destination rate

    # --- Flag counts ---
    fin_flag_number = 0
    syn_flag_number = 0
    rst_flag_number = 0
    psh_flag_number = 0
    ack_flag_number = 0
    ece_flag_number = 0
    cwr_flag_number = 0
    urg_count = 0

    for pkt in packets:
        if TCP in pkt:
            flags = pkt[TCP].flags
            fin_flag_number += int('F' in flags)
            syn_flag_number += int('S' in flags)
            rst_flag_number += int('R' in flags)
            psh_flag_number += int('P' in flags)
            ack_flag_number += int('A' in flags)
            ece_flag_number += int('E' in flags)
            cwr_flag_number += int('C' in flags)
            urg_count += int('U' in flags)
    ack_count = ack_flag_number
    syn_count = syn_flag_number
    fin_count = fin_flag_number
    rst_count = rst_flag_number
    has_http = 0
    has_https = 0
    has_dns = 0
    has_telnet = 0
    has_smtp = 0
    has_ssh = 0
    has_irc = 0
    has_tcp = 0
    has_udp = 0
    has_dhcp = 0
    has_arp = 0
    has_icmp = 0
    has_ipv = 0
    has_llc = 0

    for pkt in packets:
        if TCP in pkt:
            has_tcp = 1
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
            if sport == 80 or dport == 80:
                has_http = 1
            if sport == 443 or dport == 443:
                has_https = 1
            if sport == 23 or dport == 23:
                has_telnet = 1
            if sport == 25 or dport == 25:
                has_smtp = 1
            if sport == 22 or dport == 22:
                has_ssh = 1
            if sport in [6667, 6668, 6669] or dport in [6667, 6668, 6669]:
                has_irc = 1
        elif UDP in pkt:
            has_udp = 1
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
            if sport == 53 or dport == 53:
                has_dns = 1
            if sport == 67 or dport == 68 or sport == 68 or dport == 67:
                has_dhcp = 1
        elif ICMP in pkt:
            has_icmp = 1
        elif ARP in pkt:
            has_arp = 1

        if IP in pkt:
            has_ipv = 1

    # --- Statistical features ---
    tot_sum = total_bytes
    min_size = np.min(sizes) if len(sizes) > 0 else 0
    max_size = np.max(sizes) if len(sizes) > 0 else 0
    avg_size = np.mean(sizes) if len(sizes) > 0 else 0
    std_size = np.std(sizes) if len(sizes) > 0 else 0
    tot_size = total_bytes
    # --- Inter-arrival time (IAT) ---
    if len(times) > 1:
        iats = np.diff(times)
        iat = np.mean(iats)
    else:
        iat = 0.0

    # --- Number of packets ---
    number = total_packets
    # --- Advanced features ---
   
    magnitude = np.sqrt(np.sum(sizes ** 2)) if len(sizes) > 0 else 0

    # Radius: Mean distance from centroid
    if len(sizes) > 1:
        centroid = np.mean(sizes)
        radius = np.mean(np.abs(sizes - centroid))
    else:
        radius = 0

    # Covariance: Between packet size and inter-arrival time
    if len(times) > 1 and len(sizes) > 1:
        iats_full = np.diff(times)
        sizes_for_cov = sizes[:-1]  # Match length with IATs
        if len(iats_full) == len(sizes_for_cov):
            covariance = np.cov(sizes_for_cov, iats_full)[0, 1]
        else:
            covariance = 0
    else:
        covariance = 0

    # Variance
    variance = np.var(sizes) if len(sizes) > 0 else 0

    # Weight: Ratio of payload to total size
    payload_sum = 0
    for pkt in packets:
        if TCP in pkt and hasattr(pkt[TCP], 'payload'):
            payload_sum += len(pkt[TCP].payload)
        elif UDP in pkt and hasattr(pkt[UDP], 'payload'):
            payload_sum += len(pkt[UDP].payload)
    weight = payload_sum / total_bytes if total_bytes > 0 else 0

    # --- Build feature dictionary in exact required order ---
    features = {
        'flow_duration': flow_duration, 'Header_Length': header_length,
        'Protocol Type': protocol_type, 'Duration': duration,
        'Rate': rate, 'Drate': drate,
        'fin_flag_number': fin_flag_number, 'syn_flag_number': syn_flag_number,
        'psh_flag_number': psh_flag_number, 'ack_flag_number': ack_flag_number,
        'ece_flag_number': ece_flag_number,'cwr_flag_number': cwr_flag_number,
        'syn_count': syn_count, 'fin_count': fin_count,
        'urg_count': urg_count, 'rst_count': rst_count,
        'HTTP': has_http, 'HTTPS': has_https,
        'DNS': has_dns, 'Telnet': has_telnet,
        'SMTP': has_smtp, 'SSH': has_ssh,
        'IRC': has_irc, 'TCP': has_tcp,
        'UDP': has_udp,
        'DHCP': has_dhcp,
        'ARP': has_arp,
        'ICMP': has_icmp,
        'IPv': has_ipv,
        'Tot sum': tot_sum,
        'Min': min_size,
        'Max': max_size,
        'AVG': avg_size,
        'Tot size': tot_size,
        'IAT': iat,
        'Covariance': covariance,
        'Variance': variance
    }

    # The system now uses CICIoT2023 features (46) since that's the dataset the models were trained on
    model_features = features

    df = pd.DataFrame([model_features])
    # Replace NaN and inf values with 0.0
    df = df.replace([np.inf, -np.inf], 0.0)
    df = df.fillna(0.0)

    # Add debug logging to check for feature mismatches
    expected_features = REQUIRED_FEATURES
    actual_features = list(df.columns)
    if len(actual_features) != len(expected_features):
        print(f"[DEBUG] Feature count mismatch: expected {len(expected_features)}, got {len(actual_features)}")
        print(f"[DEBUG] Expected: {expected_features}")
        print(f"[DEBUG] Actual: {actual_features}")
        missing = set(expected_features) - set(actual_features)
        extra = set(actual_features) - set(expected_features)
        if missing:
            print(f"[DEBUG] Missing features: {missing}")
        if extra:
            print(f"[DEBUG] Extra features: {extra}")

    return df


def get_feature_names():
    """
    Get the list of feature names required by the retrained models.
    Returns: List[str]: List of required feature names.
    """
    return REQUIRED_FEATURES

def validate_features(features_df):
    """
    Validate that the features DataFrame has the correct structure for the model.
    Args: features_df: DataFrame to validate.
    Returns: bool: True if valid, otherwise raises a ValueError.
    """
    expected_features = get_feature_names()
    n_expected = len(expected_features)
    if features_df.shape[1] != n_expected:
        raise ValueError(f"Expected {n_expected} features, but got {features_df.shape[1]}.")

    missing_features = set(expected_features) - set(features_df.columns)
    if missing_features:
        raise ValueError(f"The following required features are missing: {missing_features}")

    extra_features = set(features_df.columns) - set(expected_features)
    if extra_features:
        raise ValueError(f"The following extra features were found: {extra_features}")

    if not all(features_df.columns == expected_features):
        raise ValueError("The feature columns are not in the expected order.")
    return True
