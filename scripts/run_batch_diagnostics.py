"""Run a batch of diagnostic flows (benign and attack) and summarize predictions.

Produces a simple CSV-like summary printed to stdout and a small aggregate report of
false positives (benign predicted as attack) and detection rate (attacks predicted as attack).
"""
import time
import json
from collections import Counter
from scapy.all import Ether, IP, TCP, UDP

from src.data_processing.feature_engineer import engineer_features_from_flow
from src.models.predict import diagnose_prediction, predict_threat


def build_benign_flow(count=20):
    pkts = []
    base_time = time.time()
    for i in range(count):
        if i % 2 == 0:
            pkt = Ether()/IP(src="192.168.1.10", dst="192.168.1.100")/TCP(sport=12345, dport=80, flags='A')
        else:
            pkt = Ether()/IP(src="192.168.1.100", dst="192.168.1.10")/TCP(sport=80, dport=12345, flags='A')
        pkt.time = base_time + (i * 0.05)
        pkts.append(pkt)
    return pkts


def build_syn_flood(count=40):
    pkts = []
    base_time = time.time()
    for i in range(count):
        pkt = Ether()/IP(src=f"10.0.0.{i%50}", dst="192.168.1.100")/TCP(sport=1024+i, dport=80, flags='S')
        pkt.time = base_time + (i * 0.001)
        pkts.append(pkt)
    return pkts


def build_udp_flood(count=40):
    pkts = []
    base_time = time.time()
    for i in range(count):
        pkt = Ether()/IP(src=f"10.0.1.{i%50}", dst="192.168.1.100")/UDP(sport=5000+i, dport=53)
        pkt.time = base_time + (i * 0.001)
        pkts.append(pkt)
    return pkts


def run_batch(benign_n=10, syn_n=5, udp_n=5):
    rows = []
    summary = {'benign_total': 0, 'benign_fp': 0, 'syn_total': 0, 'syn_detected': 0, 'udp_total': 0, 'udp_detected': 0}

    print('id,type,attack,severity,confidence,method,weighted_conf')

    # Benign flows
    for i in range(benign_n):
        pkts = build_benign_flow(20)
        feats = engineer_features_from_flow(pkts)
        diag = diagnose_prediction(feats)
        pred = predict_threat(feats)
        attack = pred.get('attack')
        conf = pred.get('confidence')
        method = pred.get('method')
        weighted = diag.get('weighted_confidence')
        print(f"benign_{i},benign,{attack},{pred.get('severity')},{conf:.4f},{method},{weighted}")
        summary['benign_total'] += 1
        if attack and attack != 'BenignTraffic':
            summary['benign_fp'] += 1

    # SYN floods
    for i in range(syn_n):
        pkts = build_syn_flood(50)
        feats = engineer_features_from_flow(pkts)
        diag = diagnose_prediction(feats)
        pred = predict_threat(feats)
        attack = pred.get('attack')
        conf = pred.get('confidence')
        method = pred.get('method')
        weighted = diag.get('weighted_confidence')
        print(f"syn_{i},syn,{attack},{pred.get('severity')},{conf:.4f},{method},{weighted}")
        summary['syn_total'] += 1
        if attack and attack != 'BenignTraffic':
            summary['syn_detected'] += 1

    # UDP floods
    for i in range(udp_n):
        pkts = build_udp_flood(50)
        feats = engineer_features_from_flow(pkts)
        diag = diagnose_prediction(feats)
        pred = predict_threat(feats)
        attack = pred.get('attack')
        conf = pred.get('confidence')
        method = pred.get('method')
        weighted = diag.get('weighted_confidence')
        print(f"udp_{i},udp,{attack},{pred.get('severity')},{conf:.4f},{method},{weighted}")
        summary['udp_total'] += 1
        if attack and attack != 'BenignTraffic':
            summary['udp_detected'] += 1

    # Print summary
    print('\nSUMMARY:')
    benign_fp_rate = summary['benign_fp'] / summary['benign_total'] if summary['benign_total'] else 0.0
    syn_detect_rate = summary['syn_detected'] / summary['syn_total'] if summary['syn_total'] else 0.0
    udp_detect_rate = summary['udp_detected'] / summary['udp_total'] if summary['udp_total'] else 0.0
    print(f"Benign flows: {summary['benign_total']} total, {summary['benign_fp']} false positives, FP rate={benign_fp_rate:.2%}")
    print(f"SYN floods: {summary['syn_total']} total, {summary['syn_detected']} detected, Detection rate={syn_detect_rate:.2%}")
    print(f"UDP floods: {summary['udp_total']} total, {summary['udp_detected']} detected, Detection rate={udp_detect_rate:.2%}")


if __name__ == '__main__':
    # Default batch sizes; small to keep runtime reasonable
    run_batch(benign_n=10, syn_n=5, udp_n=5)
