#!/usr/bin/env python3
"""
Generate packet-level traffic using scapy (requires sudo/root).
Run with: sudo venv/bin/python generate_packet_traffic.py
"""
import time
import argparse
from scapy.all import IP, TCP, UDP, ICMP, send, sr1, conf
import random

# Suppress scapy warnings
conf.verb = 0


def generate_syn_flood(target="127.0.0.1", dport=8000, count=100, rate=200):
    """
    Generate SYN flood attack (should trigger alert).
    """
    print(f"[SYN Flood] Target: {target}:{dport}")
    print(f"  Packets: {count}, Rate: {rate} pkt/s")
    print(f"  Expected: ALERT (DoS Hulk / SYN Flood)")
    print()

    start = time.time()
    interval = 1.0 / rate

    for i in range(count):
        sport = random.randint(1024, 65535)
        pkt = IP(dst=target) / TCP(sport=sport, dport=dport, flags="S", seq=random.randint(0, 0xFFFFFFFF))
        send(pkt, verbose=False)

        if (i + 1) % 50 == 0:
            print(f"  Sent {i + 1}/{count} SYN packets...")

        next_time = start + (i + 1) * interval
        sleep_time = next_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

    elapsed = time.time() - start
    actual_rate = count / elapsed
    print(f"  Completed: {count} packets in {elapsed:.2f}s ({actual_rate:.1f} pkt/s)")


def generate_udp_flood(target="127.0.0.1", dport=8000, count=100, rate=200, payload_size=100):
    """
    Generate UDP flood attack (should trigger alert).
    """
    print(f"[UDP Flood] Target: {target}:{dport}")
    print(f"  Packets: {count}, Rate: {rate} pkt/s, Payload: {payload_size} bytes")
    print(f"  Expected: ALERT (DDoS / UDP Flood)")
    print()

    start = time.time()
    interval = 1.0 / rate

    for i in range(count):
        sport = random.randint(1024, 65535)
        data = bytes(random.getrandbits(8) for _ in range(payload_size))
        pkt = IP(dst=target) / UDP(sport=sport, dport=dport) / data
        send(pkt, verbose=False)

        if (i + 1) % 50 == 0:
            print(f"  Sent {i + 1}/{count} UDP packets...")

        next_time = start + (i + 1) * interval
        sleep_time = next_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

    elapsed = time.time() - start
    actual_rate = count / elapsed
    print(f"  Completed: {count} packets in {elapsed:.2f}s ({actual_rate:.1f} pkt/s)")


def generate_icmp_flood(target="127.0.0.1", count=100, rate=200):
    """
    Generate ICMP flood (ping flood) - should trigger alert.
    """
    print(f"[ICMP Flood] Target: {target}")
    print(f"  Packets: {count}, Rate: {rate} pkt/s")
    print(f"  Expected: ALERT (ICMP Flood)")
    print()

    start = time.time()
    interval = 1.0 / rate

    for i in range(count):
        pkt = IP(dst=target) / ICMP()
        send(pkt, verbose=False)

        if (i + 1) % 50 == 0:
            print(f"  Sent {i + 1}/{count} ICMP packets...")

        next_time = start + (i + 1) * interval
        sleep_time = next_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

    elapsed = time.time() - start
    actual_rate = count / elapsed
    print(f"  Completed: {count} packets in {elapsed:.2f}s ({actual_rate:.1f} pkt/s)")


def generate_port_scan(target="127.0.0.1", ports="8000-8030", timeout=0.3):
    """
    Generate port scan - should trigger alert.
    """
    # Parse port range
    if "-" in ports:
        start_port, end_port = ports.split("-")
        port_list = list(range(int(start_port), int(end_port) + 1))
    else:
        port_list = [int(ports)]

    print(f"[Port Scan] Target: {target}")
    print(f"  Ports: {ports} ({len(port_list)} ports)")
    print(f"  Expected: ALERT (Port Scan)")
    print()

    open_ports = []

    for i, port in enumerate(port_list):
        sport = random.randint(1024, 65535)
        pkt = IP(dst=target) / TCP(sport=sport, dport=port, flags="S")
        resp = sr1(pkt, timeout=timeout, verbose=False)

        if resp is not None and resp.haslayer(TCP):
            flags = resp.getlayer(TCP).flags
            if flags & 0x12:  # SYN-ACK
                open_ports.append(port)
                print(f"  Port {port}: OPEN")
            elif flags & 0x14:  # RST
                pass  # Closed
        else:
            pass  # Filtered/no response

        if (i + 1) % 10 == 0:
            print(f"  Scanned {i + 1}/{len(port_list)} ports...")

    print(f"  Completed: Scanned {len(port_list)} ports, found {len(open_ports)} open")


def generate_normal_traffic(target="127.0.0.1", dport=8000, count=20):
    """
    Generate normal TCP traffic (should NOT trigger alert).
    """
    print(f"[Normal Traffic] Target: {target}:{dport}")
    print(f"  Packets: {count} (low rate)")
    print(f"  Expected: NO alerts (benign traffic)")
    print()

    sport = random.randint(10000, 60000)

    for i in range(count):
        # SYN
        syn = IP(dst=target) / TCP(sport=sport, dport=dport, flags="S", seq=1000)
        send(syn, verbose=False)

        # ACK (simulate response)
        ack = IP(dst=target) / TCP(sport=sport, dport=dport, flags="A", seq=1001, ack=1)
        send(ack, verbose=False)

        if (i + 1) % 5 == 0:
            print(f"  Sent {i + 1}/{count} connection attempts...")

        time.sleep(0.5)  # Slow rate - 2 per second

    print(f"  Completed: {count} normal connections")


def main():
    parser = argparse.ArgumentParser(
        description="Generate packet-level traffic for IDS testing (requires sudo)"
    )
    parser.add_argument("--target", default="127.0.0.1", help="Target IP address")
    parser.add_argument("--port", type=int, default=8000, help="Target port")
    parser.add_argument("--scenario", choices=[
        "normal", "syn-flood", "udp-flood", "icmp-flood", "port-scan", "all"
    ], default="all", help="Attack scenario to generate")
    parser.add_argument("--count", type=int, default=100, help="Number of packets")
    parser.add_argument("--rate", type=int, default=200, help="Packets per second")

    args = parser.parse_args()

    print("="*70)
    print("PACKET-LEVEL TRAFFIC GENERATOR (requires sudo)")
    print("="*70)
    print(f"Target: {args.target}:{args.port}")
    print(f"Scenario: {args.scenario}")
    print("="*70)
    print()
    print("⚠️  Make sure the IDS is running in another terminal:")
    print("   sudo venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000")
    print()

    if args.scenario in ["normal", "all"]:
        print("\n--- Scenario 1: Normal Traffic ---")
        generate_normal_traffic(args.target, args.port, count=20)
        print("\n✓ Should NOT trigger alerts\n")
        time.sleep(3)

    if args.scenario in ["syn-flood", "all"]:
        print("\n--- Scenario 2: SYN Flood Attack ---")
        print("⚠️  This SHOULD trigger an alert!")
        if args.scenario == "all":
            input("Press Enter to start attack...")
        generate_syn_flood(args.target, args.port, count=args.count, rate=args.rate)
        print("\n✓ Check for DoS Hulk / SYN Flood alert\n")
        time.sleep(3)

    if args.scenario in ["udp-flood", "all"]:
        print("\n--- Scenario 3: UDP Flood Attack ---")
        print("⚠️  This SHOULD trigger an alert!")
        if args.scenario == "all":
            input("Press Enter to start attack...")
        generate_udp_flood(args.target, args.port, count=args.count, rate=args.rate)
        print("\n✓ Check for DDoS / UDP Flood alert\n")
        time.sleep(3)

    if args.scenario in ["icmp-flood", "all"]:
        print("\n--- Scenario 4: ICMP Flood Attack ---")
        print("⚠️  This SHOULD trigger an alert!")
        if args.scenario == "all":
            input("Press Enter to start attack...")
        generate_icmp_flood(args.target, count=args.count, rate=args.rate)
        print("\n✓ Check for ICMP Flood alert\n")
        time.sleep(3)

    if args.scenario in ["port-scan", "all"]:
        print("\n--- Scenario 5: Port Scan ---")
        print("⚠️  This SHOULD trigger an alert!")
        if args.scenario == "all":
            input("Press Enter to start attack...")
        generate_port_scan(args.target, ports=f"{args.port}-{args.port+30}")
        print("\n✓ Check for Port Scan alert\n")

    print("\n" + "="*70)
    print("TRAFFIC GENERATION COMPLETE")
    print("="*70)
    print("\nCheck for alerts in:")
    print("  1. IDS console output (DEBUG messages)")
    print("  2. logs/alerts.jsonl")
    print("  3. API: http://127.0.0.1:8000/api/alerts")
    print("\nExpected results:")
    print("  ✓ Normal traffic: NO alerts")
    print("  ✓ Attack traffic: Alerts with 70-85% confidence")


if __name__ == "__main__":
    import sys
    import os

    if os.geteuid() != 0:
        print("ERROR: This script requires root privileges to send raw packets.")
        print("Please run with: sudo venv/bin/python generate_packet_traffic.py")
        sys.exit(1)

    main()
