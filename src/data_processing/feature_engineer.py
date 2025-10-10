import numpy as np
import pandas as pd
from scapy.all import TCP, UDP, IP

def engineer_features_from_flow(packets):
    """
    Extract CICIDS-style flow features from a list of Scapy packets.
    Approximates CICIDS2017 features for live IDS analysis.
    """
    if not packets:
        return pd.DataFrame()

    # --- Basic direction detection ---
    first_pkt = packets[0]
    src_ip = first_pkt[IP].src if 'IP' in first_pkt else None
    dst_ip = first_pkt[IP].dst if 'IP' in first_pkt else None
    protocol = first_pkt[IP].proto if 'IP' in first_pkt else 0
    dst_port = (
        first_pkt[TCP].dport if TCP in first_pkt else
        first_pkt[UDP].dport if UDP in first_pkt else 0
    )

    # --- Timing and packet metrics ---
    times = np.array([pkt.time for pkt in packets])
    sizes = np.array([len(pkt) for pkt in packets])
    duration = times[-1] - times[0] if len(times) > 1 else 0.0
    total_packets = len(packets)
    total_bytes = sizes.sum()

    # --- Direction-based split (approximation) ---
    fwd_sizes = []
    bwd_sizes = []
    fwd_times = []
    bwd_times = []
    for pkt in packets:
        if 'IP' not in pkt:
            continue
        if pkt[IP].src == src_ip:
            fwd_sizes.append(len(pkt))
            fwd_times.append(pkt.time)
        else:
            bwd_sizes.append(len(pkt))
            bwd_times.append(pkt.time)
    fwd_sizes = np.array(fwd_sizes) if fwd_sizes else np.array([0])
    bwd_sizes = np.array(bwd_sizes) if bwd_sizes else np.array([0])
    fwd_times = np.array(fwd_times) if fwd_times else np.array([])
    bwd_times = np.array(bwd_times) if bwd_times else np.array([])

    # --- Inter-arrival times ---
    iats = np.diff(times) if len(times) > 1 else np.array([0])
    fwd_iats = np.diff(fwd_times) if len(fwd_times) > 1 else np.array([0])
    bwd_iats = np.diff(bwd_times) if len(bwd_times) > 1 else np.array([0])

    fwd_iat_total = fwd_times[-1] - fwd_times[0] if len(fwd_times) > 1 else 0.0
    bwd_iat_total = bwd_times[-1] - bwd_times[0] if len(bwd_times) > 1 else 0.0

    # --- Flag counts (split for PSH and URG, overall for others) ---
    fin = syn = rst = psh = ack = urg = cwe = ece = 0
    fwd_psh = bwd_psh = fwd_urg = bwd_urg = 0
    for pkt in packets:
        if TCP in pkt:
            flags = pkt[TCP].flags
            fin += int('F' in flags)
            syn += int('S' in flags)
            rst += int('R' in flags)
            psh += int('P' in flags)
            ack += int('A' in flags)
            urg += int('U' in flags)
            ece += int('E' in flags)
            cwe += int('C' in flags)

            if pkt[IP].src == src_ip:
                fwd_psh += int('P' in flags)
                fwd_urg += int('U' in flags)
            else:
                bwd_psh += int('P' in flags)
                bwd_urg += int('U' in flags)

    # --- Header lengths ---
    fwd_header_len = 0
    bwd_header_len = 0
    fwd_seg_sizes = []
    for pkt in packets:
        if 'IP' not in pkt:
            continue
        if TCP in pkt:
            hlen = (pkt[TCP].dataofs or 5) * 4  # Default to 5 (20 bytes) if None
        elif UDP in pkt:
            hlen = 8
        else:  # ICMP or other
            hlen = 8  # approximation
        if pkt[IP].src == src_ip:
            fwd_header_len += hlen
            fwd_seg_sizes.append(hlen)
        else:
            bwd_header_len += hlen

    min_seg_size_fwd = min(fwd_seg_sizes) if fwd_seg_sizes else 0

    # --- Init window sizes ---
    init_win_fwd = -1
    init_win_bwd = -1
    fwd_tcp_pkts = [pkt for pkt in packets if TCP in pkt and pkt[IP].src == src_ip]
    bwd_tcp_pkts = [pkt for pkt in packets if TCP in pkt and pkt[IP].src != src_ip]
    if fwd_tcp_pkts:
        fwd_tcp_pkts.sort(key=lambda p: p.time)
        init_win_fwd = fwd_tcp_pkts[0][TCP].window
    if bwd_tcp_pkts:
        bwd_tcp_pkts.sort(key=lambda p: p.time)
        init_win_bwd = bwd_tcp_pkts[0][TCP].window

    # --- Active data packets fwd ---
    act_data_pkt_fwd = sum(1 for pkt in packets if 'IP' in pkt and pkt[IP].src == src_ip and TCP in pkt and len(pkt[TCP].payload) > 0)

    # --- Active/Idle stats ---
    all_times = sorted(times)
    active_mean = active_std = active_max = active_min = 0.0
    idle_mean = idle_std = idle_max = idle_min = 0.0
    if len(all_times) >= 2:
        iats = np.diff(all_times)
        threshold = 1.0  # 1 second threshold for idle
        active_durs = []
        idle_durs = []
        start = all_times[0]
        for i in range(1, len(all_times)):
            if iats[i-1] > threshold:
                active_durs.append(all_times[i-1] - start)
                idle_durs.append(iats[i-1])
                start = all_times[i]
        active_durs.append(all_times[-1] - start)
        if active_durs:
            active_mean = np.mean(active_durs)
            active_std = np.std(active_durs)
            active_max = np.max(active_durs)
            active_min = np.min(active_durs)
        if idle_durs:
            idle_mean = np.mean(idle_durs)
            idle_std = np.std(idle_durs)
            idle_max = np.max(idle_durs)
            idle_min = np.min(idle_durs)

    # --- Derived rates ---
    flow_bytes_s = total_bytes / duration if duration > 0 else total_bytes
    flow_pkts_s = total_packets / duration if duration > 0 else total_packets
    fwd_pkts_s = len(fwd_sizes) / duration if duration > 0 else len(fwd_sizes)
    bwd_pkts_s = len(bwd_sizes) / duration if duration > 0 else len(bwd_sizes)

    # --- Basic statistics ---
    def safe_stats(arr):
        if len(arr) == 0:
            return {'max': 0, 'min': 0, 'mean': 0, 'std': 0, 'var': 0}
        return {
            'max': np.max(arr),
            'min': np.min(arr),
            'mean': np.mean(arr),
            'std': np.std(arr),
            'var': np.var(arr)
        }

    pkt_stats = safe_stats(sizes)
    fwd_stats = safe_stats(fwd_sizes)
    bwd_stats = safe_stats(bwd_sizes)
    flow_iat_stats = safe_stats(iats)
    fwd_iat_stats = safe_stats(fwd_iats)
    bwd_iat_stats = safe_stats(bwd_iats)

    # --- Down/Up Ratio ---
    down_up_ratio = len(bwd_sizes) / len(fwd_sizes) if len(fwd_sizes) > 0 else 0

    # --- Build final feature dict (full CICIDS2017) ---
    data = {
        'Destination Port': [dst_port],
        'Flow Duration': [duration],
        'Total Fwd Packets': [len(fwd_sizes)],
        'Total Backward Packets': [len(bwd_sizes)],
        'Total Length of Fwd Packets': [fwd_sizes.sum()],
        'Total Length of Bwd Packets': [bwd_sizes.sum()],
        'Fwd Packet Length Max': [fwd_stats['max']],
        'Fwd Packet Length Min': [fwd_stats['min']],
        'Fwd Packet Length Mean': [fwd_stats['mean']],
        'Fwd Packet Length Std': [fwd_stats['std']],
        'Bwd Packet Length Max': [bwd_stats['max']],
        'Bwd Packet Length Min': [bwd_stats['min']],
        'Bwd Packet Length Mean': [bwd_stats['mean']],
        'Bwd Packet Length Std': [bwd_stats['std']],
        'Flow Bytes/s': [flow_bytes_s],
        'Flow Packets/s': [flow_pkts_s],
        'Flow IAT Mean': [flow_iat_stats['mean']],
        'Flow IAT Std': [flow_iat_stats['std']],
        'Flow IAT Max': [flow_iat_stats['max']],
        'Flow IAT Min': [flow_iat_stats['min']],
        'Fwd IAT Total': [fwd_iat_total],
        'Fwd IAT Mean': [fwd_iat_stats['mean']],
        'Fwd IAT Std': [fwd_iat_stats['std']],
        'Fwd IAT Max': [fwd_iat_stats['max']],
        'Fwd IAT Min': [fwd_iat_stats['min']],
        'Bwd IAT Total': [bwd_iat_total],
        'Bwd IAT Mean': [bwd_iat_stats['mean']],
        'Bwd IAT Std': [bwd_iat_stats['std']],
        'Bwd IAT Max': [bwd_iat_stats['max']],
        'Bwd IAT Min': [bwd_iat_stats['min']],
        'Fwd PSH Flags': [fwd_psh],
        'Bwd PSH Flags': [bwd_psh],
        'Fwd URG Flags': [fwd_urg],
        'Bwd URG Flags': [bwd_urg],
        'Fwd Header Length': [fwd_header_len],
        'Bwd Header Length': [bwd_header_len],
        'Fwd Packets/s': [fwd_pkts_s],
        'Bwd Packets/s': [bwd_pkts_s],
        'Min Packet Length': [pkt_stats['min']],
        'Max Packet Length': [pkt_stats['max']],
        'Packet Length Mean': [pkt_stats['mean']],
        'Packet Length Std': [pkt_stats['std']],
        'Packet Length Variance': [pkt_stats['var']],
        'FIN Flag Count': [fin],
        'SYN Flag Count': [syn],
        'RST Flag Count': [rst],
        'PSH Flag Count': [psh],
        'ACK Flag Count': [ack],
        'URG Flag Count': [urg],
        'CWE Flag Count': [cwe],
        'ECE Flag Count': [ece],
        'Down/Up Ratio': [down_up_ratio],
        'Average Packet Size': [total_bytes / total_packets if total_packets > 0 else 0],
        'Avg Fwd Segment Size': [fwd_stats['mean']],
        'Avg Bwd Segment Size': [bwd_stats['mean']],
        'Fwd Header Length.1': [fwd_header_len],  # Duplicate in dataset
        'Fwd Avg Bytes/Bulk': [0],
        'Fwd Avg Packets/Bulk': [0],
        'Fwd Avg Bulk Rate': [0],
        'Bwd Avg Bytes/Bulk': [0],
        'Bwd Avg Packets/Bulk': [0],
        'Bwd Avg Bulk Rate': [0],
        'Subflow Fwd Packets': [len(fwd_sizes)],
        'Subflow Fwd Bytes': [fwd_sizes.sum()],
        'Subflow Bwd Packets': [len(bwd_sizes)],
        'Subflow Bwd Bytes': [bwd_sizes.sum()],
        'Init_Win_bytes_forward': [init_win_fwd],
        'Init_Win_bytes_backward': [init_win_bwd],
        'act_data_pkt_fwd': [act_data_pkt_fwd],
        'min_seg_size_forward': [min_seg_size_fwd],
        'Active Mean': [active_mean],
        'Active Std': [active_std],
        'Active Max': [active_max],
        'Active Min': [active_min],
        'Idle Mean': [idle_mean],
        'Idle Std': [idle_std],
        'Idle Max': [idle_max],
        'Idle Min': [idle_min],
    }

    # Fill any missing features with 0 so it matches model expectations
    df = pd.DataFrame(data).fillna(0.0)
    return df