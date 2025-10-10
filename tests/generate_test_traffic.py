#!/usr/bin/env python3
"""
Generate various types of network traffic for testing the IDS.
Can be run without sudo (uses application-level traffic).
"""
import time
import socket
import threading
import requests
import argparse
from concurrent.futures import ThreadPoolExecutor


def generate_normal_http(target_url="http://127.0.0.1:8000", duration=30, rate=5):
    """
    Generate normal HTTP traffic (should NOT trigger alerts).

    Args:
        target_url: Target API endpoint
        duration: How long to run (seconds)
        rate: Requests per second
    """
    print(f"[Normal HTTP] Starting normal traffic to {target_url}")
    print(f"  Duration: {duration}s, Rate: {rate} req/s")
    print(f"  Expected: NO alerts (benign traffic)")

    endpoints = ['/api/health', '/api/stats', '/api/flows', '/api/alerts']
    start_time = time.time()
    count = 0

    while time.time() - start_time < duration:
        try:
            endpoint = endpoints[count % len(endpoints)]
            response = requests.get(f"{target_url}{endpoint}", timeout=2)
            count += 1
            if count % 10 == 0:
                print(f"  Sent {count} requests...")
            time.sleep(1.0 / rate)
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(1)

    print(f"[Normal HTTP] Completed: {count} requests in {duration}s")


def generate_http_flood(target_url="http://127.0.0.1:8000", duration=10, rate=100):
    """
    Generate HTTP flood (high rate - should trigger alerts).

    Args:
        target_url: Target API endpoint
        duration: How long to run (seconds)
        rate: Requests per second
    """
    print(f"[HTTP Flood] Starting flood attack to {target_url}")
    print(f"  Duration: {duration}s, Rate: {rate} req/s")
    print(f"  Expected: ALERT (high rate attack)")

    def send_request():
        try:
            requests.get(f"{target_url}/api/health", timeout=1)
        except:
            pass

    start_time = time.time()
    count = 0

    with ThreadPoolExecutor(max_workers=20) as executor:
        while time.time() - start_time < duration:
            executor.submit(send_request)
            count += 1
            if count % 100 == 0:
                print(f"  Sent {count} requests...")
            time.sleep(1.0 / rate)

    print(f"[HTTP Flood] Completed: {count} requests in {duration}s")


def generate_port_scan(target_host="127.0.0.1", port_range=(8000, 8050)):
    """
    Generate port scan pattern (should trigger alerts).

    Args:
        target_host: Target host
        port_range: Range of ports to scan (start, end)
    """
    print(f"[Port Scan] Scanning {target_host} ports {port_range[0]}-{port_range[1]}")
    print(f"  Expected: ALERT (port scan detected)")

    count = 0
    open_ports = []

    for port in range(port_range[0], port_range[1] + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)

        try:
            result = sock.connect_ex((target_host, port))
            if result == 0:
                open_ports.append(port)
                print(f"  Port {port}: OPEN")
            count += 1
        except Exception as e:
            pass
        finally:
            sock.close()

        time.sleep(0.05)  # Small delay between scans

    print(f"[Port Scan] Completed: Scanned {count} ports, found {len(open_ports)} open")


def generate_connection_spam(target_host="127.0.0.1", target_port=8000, count=100, rate=50):
    """
    Generate many rapid TCP connections (should trigger alerts).

    Args:
        target_host: Target host
        target_port: Target port
        count: Number of connections
        rate: Connections per second
    """
    print(f"[Connection Spam] Opening {count} connections to {target_host}:{target_port}")
    print(f"  Rate: {rate} conn/s")
    print(f"  Expected: ALERT (high connection rate)")

    def make_connection():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((target_host, target_port))
            sock.close()
        except:
            pass

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(count):
            executor.submit(make_connection)
            if (i + 1) % 20 == 0:
                print(f"  Sent {i + 1} connections...")
            time.sleep(1.0 / rate)

    elapsed = time.time() - start_time
    print(f"[Connection Spam] Completed: {count} connections in {elapsed:.2f}s")


def generate_slow_requests(target_url="http://127.0.0.1:8000", count=20):
    """
    Generate slow, legitimate-looking requests (should NOT trigger).

    Args:
        target_url: Target API endpoint
        count: Number of requests
    """
    print(f"[Slow Requests] Sending {count} slow requests to {target_url}")
    print(f"  Expected: NO alerts (normal behavior)")

    for i in range(count):
        try:
            response = requests.get(f"{target_url}/api/health", timeout=5)
            print(f"  Request {i+1}/{count}: {response.status_code}")
            time.sleep(2)  # Wait 2 seconds between requests
        except Exception as e:
            print(f"  Request {i+1}/{count} failed: {e}")

    print(f"[Slow Requests] Completed")


def main():
    parser = argparse.ArgumentParser(description="Generate test traffic for IDS testing")
    parser.add_argument("--target", default="http://127.0.0.1:8000", help="Target URL")
    parser.add_argument("--scenario", choices=[
        "normal", "flood", "scan", "spam", "slow", "all"
    ], default="all", help="Traffic scenario to generate")

    args = parser.parse_args()

    print("="*70)
    print("IDS TRAFFIC GENERATOR")
    print("="*70)
    print(f"Target: {args.target}")
    print(f"Scenario: {args.scenario}")
    print("="*70)
    print()

    if args.scenario in ["normal", "all"]:
        print("\n--- Scenario 1: Normal HTTP Traffic ---")
        generate_normal_http(args.target, duration=15, rate=5)
        time.sleep(2)

    if args.scenario in ["slow", "all"]:
        print("\n--- Scenario 2: Slow Legitimate Requests ---")
        generate_slow_requests(args.target, count=10)
        time.sleep(2)

    if args.scenario in ["flood", "all"]:
        print("\n--- Scenario 3: HTTP Flood Attack ---")
        print("⚠️  This should trigger an alert!")
        input("Press Enter to start attack...")
        generate_http_flood(args.target, duration=10, rate=100)
        time.sleep(2)

    if args.scenario in ["spam", "all"]:
        print("\n--- Scenario 4: Connection Spam ---")
        print("⚠️  This should trigger an alert!")
        input("Press Enter to start attack...")
        target_port = int(args.target.split(":")[-1].split("/")[0]) if ":" in args.target else 8000
        generate_connection_spam("127.0.0.1", target_port, count=100, rate=50)
        time.sleep(2)

    if args.scenario in ["scan", "all"]:
        print("\n--- Scenario 5: Port Scan ---")
        print("⚠️  This should trigger an alert!")
        input("Press Enter to start attack...")
        generate_port_scan("127.0.0.1", port_range=(8000, 8030))

    print("\n" + "="*70)
    print("TRAFFIC GENERATION COMPLETE")
    print("="*70)
    print("\nCheck the IDS logs for alerts:")
    print("  - Console output (DEBUG messages)")
    print("  - logs/alerts.jsonl")
    print("  - API: http://127.0.0.1:8000/api/alerts")


if __name__ == "__main__":
    main()
