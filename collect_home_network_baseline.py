"""
Home Network Baseline Collection Script

This script collects legitimate traffic from your home network to create a baseline.
This baseline will be used to retrain the model to understand what's "normal" on YOUR network.

How it works:
1. Monitors your network traffic for a specified duration (e.g., 24 hours)
2. Saves all flows as "BenignTraffic"
3. Creates a dataset that can be merged with attack data for retraining
4. The retrained model will understand your home network patterns

Usage:
    python collect_home_network_baseline.py --duration 24 --output data/home_network_baseline.csv
"""

import argparse
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import os
import yaml
from pathlib import Path

from scapy.all import sniff, IP, TCP, UDP
from src.data_processing.feature_engineer import engineer_features_from_flow


class HomeNetworkCollector:
    """Collect legitimate home network traffic for model retraining."""

    def __init__(self, duration_hours=24, output_file='data/home_network_baseline.csv'):
        self.duration_hours = duration_hours
        self.output_file = output_file
        self.flows = defaultdict(lambda: {'packets': [], 'start_time': None, 'bytes': 0})
        self.collected_flows = []
        self.start_time = None
        self.end_time = None

        # Load config
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        self.interface = config['network']['interface']

        print(f"[+] Home Network Baseline Collector")
        print(f"    Interface: {self.interface}")
        print(f"    Duration: {duration_hours} hours")
        print(f"    Output: {output_file}")
        print()

    def process_packet(self, packet):
        """Process a single packet into flows."""
        try:
            if IP in packet:
                sport = (
                    packet[TCP].sport if TCP in packet
                    else packet[UDP].sport if UDP in packet
                    else 0
                )
                dport = (
                    packet[TCP].dport if TCP in packet
                    else packet[UDP].dport if UDP in packet
                    else 0
                )
                key = (packet[IP].src, packet[IP].dst, sport, packet[IP].proto)

                flow = self.flows[key]

                if flow['start_time'] is None:
                    flow['start_time'] = time.time()

                flow['packets'].append(packet)
                flow['bytes'] += len(packet)

                # Extract features every 10 packets
                if len(flow['packets']) % 10 == 0 and len(flow['packets']) >= 10:
                    self.extract_and_save_flow(key, flow)

        except Exception as e:
            pass  # Silently ignore errors during collection

    def extract_and_save_flow(self, key, flow):
        """Extract features from flow and save."""
        try:
            if not flow['packets']:
                return

            # Engineer features
            features_df = engineer_features_from_flow(flow['packets'])

            if features_df is not None and not features_df.empty:
                # Add metadata
                features_df['src_ip'] = key[0]
                features_df['dst_ip'] = key[1]
                features_df['src_port'] = key[2]
                features_df['protocol'] = key[3]
                features_df['packet_count'] = len(flow['packets'])
                features_df['timestamp'] = datetime.now().isoformat()

                # Label as benign (this is the key!)
                features_df['label'] = 'BenignTraffic'
                features_df['Label_ID'] = 0  # Assuming 0 is benign

                self.collected_flows.append(features_df)

        except Exception as e:
            pass  # Silently ignore errors

    def save_checkpoint(self):
        """Save checkpoint of collected data."""
        if not self.collected_flows:
            return

        print(f"\n[+] Saving checkpoint... ({len(self.collected_flows)} flows collected)")

        try:
            df = pd.concat(self.collected_flows, ignore_index=True)

            # Create output directory
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save to CSV
            df.to_csv(self.output_file, index=False)

            print(f"[+] Saved {len(df)} flows to {self.output_file}")
            print(f"    File size: {os.path.getsize(self.output_file) / 1024**2:.2f} MB")

        except Exception as e:
            print(f"[!] Error saving checkpoint: {e}")

    def start_collection(self):
        """Start collecting network traffic."""
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=self.duration_hours)

        print(f"[+] Starting collection at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[+] Will stop at {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("[INFO] IMPORTANT: During this collection period:")
        print("       - Use your network NORMALLY")
        print("       - Browse websites, watch videos, download files")
        print("       - Use all your normal apps and services")
        print("       - DO NOT run any attack tools or suspicious activity")
        print()
        print("[INFO] The longer you collect, the better the model will understand your network")
        print("[INFO] Recommended: 24-48 hours of normal usage")
        print()
        print("Press Ctrl+C to stop collection early")
        print("="*70)
        print()

        try:
            # Start packet capture
            checkpoint_interval = 300  # Save checkpoint every 5 minutes
            last_checkpoint = time.time()
            packet_count = 0

            def packet_handler(packet):
                nonlocal packet_count, last_checkpoint

                self.process_packet(packet)
                packet_count += 1

                # Print progress every 1000 packets
                if packet_count % 1000 == 0:
                    elapsed = datetime.now() - self.start_time
                    remaining = self.end_time - datetime.now()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Packets: {packet_count:,} | "
                          f"Flows: {len(self.collected_flows)} | "
                          f"Elapsed: {str(elapsed).split('.')[0]} | "
                          f"Remaining: {str(remaining).split('.')[0]}")

                # Save checkpoint every 5 minutes
                current_time = time.time()
                if current_time - last_checkpoint > checkpoint_interval:
                    self.save_checkpoint()
                    last_checkpoint = current_time

                # Check if duration reached
                if datetime.now() >= self.end_time:
                    print("\n[+] Collection duration reached!")
                    return True  # Stop sniffing

            # Start sniffing
            sniff(
                iface=self.interface,
                prn=packet_handler,
                store=False,
                stop_filter=lambda x: datetime.now() >= self.end_time
            )

        except KeyboardInterrupt:
            print("\n\n[!] Collection stopped by user")

        finally:
            # Save final checkpoint
            print("\n[+] Saving final data...")
            self.save_checkpoint()

            # Print summary
            print("\n" + "="*70)
            print("COLLECTION SUMMARY")
            print("="*70)
            print(f"Started:  {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Ended:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Duration: {datetime.now() - self.start_time}")
            print(f"Flows collected: {len(self.collected_flows)}")
            print(f"Output file: {self.output_file}")

            if os.path.exists(self.output_file):
                size_mb = os.path.getsize(self.output_file) / 1024**2
                print(f"File size: {size_mb:.2f} MB")

            print("\n[+] Next steps:")
            print("    1. Review the collected data to ensure it's all legitimate traffic")
            print("    2. Use this file to retrain your model with:")
            print(f"       python retrain_with_home_network.py --baseline {self.output_file}")
            print("    3. Or upload to Google Colab for retraining")
            print()


def main():
    parser = argparse.ArgumentParser(
        description='Collect home network baseline for model retraining'
    )
    parser.add_argument(
        '--duration',
        type=float,
        default=24,
        help='Duration in hours (default: 24)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/home_network_baseline.csv',
        help='Output CSV file (default: data/home_network_baseline.csv)'
    )

    args = parser.parse_args()

    # Check for admin privileges
    import platform
    import ctypes

    is_admin = False
    if platform.system() == 'Windows':
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            is_admin = False
    else:
        is_admin = os.geteuid() == 0 if hasattr(os, 'geteuid') else False

    if not is_admin:
        print("[!] ERROR: This script requires Administrator/root privileges")
        print()
        if platform.system() == 'Windows':
            print("Please run this script as Administrator:")
            print("  1. Right-click Command Prompt")
            print("  2. Select 'Run as Administrator'")
            print(f"  3. Run: python {__file__} --duration {args.duration}")
        else:
            print(f"Please run: sudo python {__file__} --duration {args.duration}")
        return 1

    # Start collection
    collector = HomeNetworkCollector(
        duration_hours=args.duration,
        output_file=args.output
    )

    collector.start_collection()

    return 0


if __name__ == '__main__':
    exit(main())
