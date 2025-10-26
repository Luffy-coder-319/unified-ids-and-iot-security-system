"""Run a local diagnostic to see why benign traffic may be classified as attack.

Builds a small benign HTTP-like flow using scapy, runs feature engineering and the
diagnose function in `src.models.predict`, and prints a JSON summary for inspection.
"""
import time
import json
from scapy.all import Ether, IP, TCP

from src.data_processing.feature_engineer import engineer_features_from_flow
from src.models.predict import diagnose_prediction


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


def main():
    pkts = build_benign_flow(20)
    features_df = engineer_features_from_flow(pkts)

    print("[diagnose] Generated features:\n")
    print(features_df.to_string(index=False))

    diag = diagnose_prediction(features_df)

    print('\n[diagnose] Diagnostic JSON:')
    print(json.dumps(diag, indent=2))


if __name__ == '__main__':
    main()
