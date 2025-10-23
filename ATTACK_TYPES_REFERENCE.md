# Attack Types Detection Reference

This document lists all 34 attack types that the Unified IDS and IoT Security System can detect, organized by category with descriptions and severity levels.

## Table of Contents
- [DDoS Attacks](#ddos-attacks)
- [DoS Attacks](#dos-attacks)
- [Reconnaissance Attacks](#reconnaissance-attacks)
- [Mirai Botnet Attacks](#mirai-botnet-attacks)
- [Web Application Attacks](#web-application-attacks)
- [Man-in-the-Middle Attacks](#man-in-the-middle-attacks)
- [Authentication Attacks](#authentication-attacks)
- [Malware Attacks](#malware-attacks)
- [Browser Attacks](#browser-attacks)
- [Scanning Attacks](#scanning-attacks)
- [Other Attacks](#other-attacks)
- [Testing Commands](#testing-commands)

---

## DDoS Attacks
**Severity: Medium** | **Category: Distributed Denial of Service**

### 1. DDoS-ACK_Fragmentation
- **Description**: Distributed attack using fragmented ACK packets to overwhelm the target
- **Target**: Network infrastructure, firewalls
- **Impact**: Resource exhaustion, service degradation

### 2. DDoS-HTTP_Flood
- **Description**: Distributed HTTP GET/POST request flooding
- **Target**: Web servers, application layer
- **Impact**: Server overload, website unavailability

### 3. DDoS-ICMP_Flood
- **Description**: Distributed ICMP echo request (ping) flooding
- **Target**: Network devices, servers
- **Impact**: Network congestion, bandwidth exhaustion

### 4. DDoS-ICMP_Fragmentation
- **Description**: Distributed attack using fragmented ICMP packets
- **Target**: Network stack, firewall rules
- **Impact**: Processing overhead, service disruption

### 5. DDoS-PSHACK_Flood
- **Description**: Distributed flooding with PSH+ACK TCP flags set
- **Target**: TCP/IP stack, application servers
- **Impact**: Connection table exhaustion

### 6. DDoS-RSTFINFlood
- **Description**: Distributed flooding with RST+FIN TCP flags
- **Target**: TCP connections, stateful firewalls
- **Impact**: Connection state confusion, resource exhaustion

### 7. DDoS-SYN_Flood
- **Description**: Distributed SYN packet flooding (classic SYN flood from multiple sources)
- **Target**: TCP services, connection tables
- **Impact**: Half-open connection exhaustion, service unavailability

### 8. DDoS-SlowLoris
- **Description**: Distributed slow HTTP connections keeping connections open
- **Target**: Web servers (Apache, nginx)
- **Impact**: Connection pool exhaustion, server unavailability

### 9. DDoS-SynonymousIP_Flood
- **Description**: Distributed flooding using multiple spoofed source IPs
- **Target**: Network services, DDoS mitigation systems
- **Impact**: Traffic filtering difficulty, bandwidth exhaustion

### 10. DDoS-TCP_Flood
- **Description**: Distributed TCP packet flooding
- **Target**: TCP services, network bandwidth
- **Impact**: Network congestion, service degradation

### 11. DDoS-UDP_Flood
- **Description**: Distributed UDP packet flooding
- **Target**: UDP services, network bandwidth
- **Impact**: Bandwidth saturation, legitimate traffic drops

### 12. DDoS-UDP_Fragmentation
- **Description**: Distributed attack using fragmented UDP packets
- **Target**: Network reassembly mechanisms
- **Impact**: Processing overhead, memory exhaustion

---

## DoS Attacks
**Severity: Medium** | **Category: Denial of Service**

### 13. DoS-HTTP_Flood
- **Description**: Single-source HTTP request flooding
- **Target**: Web applications, HTTP servers
- **Impact**: Server resource exhaustion

### 14. DoS-SYN_Flood
- **Description**: Single-source SYN packet flooding
- **Target**: TCP services
- **Impact**: SYN backlog queue exhaustion

### 15. DoS-TCP_Flood
- **Description**: Single-source TCP flooding attack
- **Target**: Network services
- **Impact**: Connection exhaustion

### 16. DoS-UDP_Flood
- **Description**: Single-source UDP flooding attack
- **Target**: UDP services, network bandwidth
- **Impact**: Service unavailability

---

## Reconnaissance Attacks
**Severity: Medium** | **Category: Information Gathering**

### 17. Recon-HostDiscovery
- **Description**: Network scanning to discover active hosts
- **Target**: Network infrastructure
- **Impact**: Network topology mapping, precursor to attacks
- **Indicators**: Multiple connection attempts to different IPs

### 18. Recon-OSScan
- **Description**: Operating system fingerprinting and identification
- **Target**: Servers, workstations, IoT devices
- **Impact**: OS version disclosure, vulnerability targeting
- **Indicators**: Unusual TCP/IP stack probing

### 19. Recon-PingSweep
- **Description**: ICMP-based network sweep to find live hosts
- **Target**: Network ranges
- **Impact**: Active host enumeration
- **Indicators**: Sequential ICMP echo requests

### 20. Recon-PortScan
- **Description**: Systematic scanning of ports to find open services
- **Target**: Network services, applications
- **Impact**: Service enumeration, attack surface mapping
- **Indicators**: Sequential connection attempts to multiple ports

---

## Mirai Botnet Attacks
**Severity: High** | **Category: IoT Botnet**

### 21. Mirai-greeth_flood
- **Description**: Mirai botnet GRE+ETH protocol flooding
- **Target**: Network infrastructure, IoT devices
- **Impact**: Network disruption, bandwidth exhaustion

### 22. Mirai-greip_flood
- **Description**: Mirai botnet GRE+IP protocol flooding
- **Target**: Network routers, gateways
- **Impact**: Routing disruption, service outages

### 23. Mirai-udpplain
- **Description**: Mirai botnet plain UDP flooding attack
- **Target**: Any UDP-based service
- **Impact**: Service unavailability, bandwidth saturation

---

## Web Application Attacks
**Severity: High** | **Category: Application Layer**

### 24. SqlInjection
- **Description**: SQL code injection into application queries
- **Target**: Database-driven web applications
- **Impact**: Data breach, unauthorized access, data manipulation
- **Indicators**: SQL keywords in HTTP parameters

### 25. XSS (Cross-Site Scripting)
- **Description**: Injection of malicious scripts into web pages
- **Target**: Web applications, end users
- **Impact**: Session hijacking, credential theft, defacement
- **Indicators**: JavaScript code in input fields

### 26. CommandInjection
- **Description**: OS command injection through application inputs
- **Target**: Web applications, APIs
- **Impact**: Remote code execution, system compromise
- **Indicators**: Shell metacharacters in parameters

---

## Man-in-the-Middle Attacks
**Severity: High** | **Category: Interception**

### 27. MITM-ArpSpoofing
- **Description**: ARP cache poisoning for traffic interception
- **Target**: Local network communications
- **Impact**: Traffic interception, session hijacking, credential theft
- **Indicators**: Duplicate ARP responses, MAC address conflicts

### 28. DNS_Spoofing
- **Description**: DNS response manipulation to redirect traffic
- **Target**: DNS queries, name resolution
- **Impact**: Traffic redirection, phishing, malware distribution
- **Indicators**: Unexpected DNS responses, TTL anomalies

---

## Authentication Attacks
**Severity: High** | **Category: Credential Access**

### 29. DictionaryBruteForce
- **Description**: Automated password guessing using common passwords
- **Target**: Login forms, SSH, FTP, RDP services
- **Impact**: Unauthorized access, account compromise
- **Indicators**: Multiple failed login attempts, sequential authentication requests

---

## Malware Attacks
**Severity: High** | **Category: Malicious Software**

### 30. Backdoor_Malware
- **Description**: Backdoor communication and malware command-and-control traffic
- **Target**: Compromised systems
- **Impact**: Persistent access, data exfiltration, lateral movement
- **Indicators**: Unusual outbound connections, suspicious protocols

---

## Browser Attacks
**Severity: High** | **Category: Client-Side**

### 31. BrowserHijacking
- **Description**: Unauthorized modification of browser settings and behavior
- **Target**: Web browsers, user sessions
- **Impact**: Privacy violation, malware installation, credential theft
- **Indicators**: Unexpected redirects, modified settings

---

## Scanning Attacks
**Severity: Medium** | **Category: Vulnerability Assessment**

### 32. VulnerabilityScan
- **Description**: Automated vulnerability scanning and assessment
- **Target**: Network services, web applications
- **Impact**: Vulnerability identification, precursor to exploitation
- **Indicators**: Multiple service probes, vulnerability scanner signatures

---

## Other Attacks
**Severity: High** | **Category: File Upload**

### 33. Uploading_Attack
- **Description**: Malicious file upload attempts (web shells, malware)
- **Target**: Web applications with file upload functionality
- **Impact**: Remote code execution, server compromise
- **Indicators**: Suspicious file types, executable uploads

---

## Benign Traffic
**Severity: Low** | **Category: Legitimate**

### 34. BenignTraffic
- **Description**: Normal, legitimate network traffic
- **Target**: N/A
- **Impact**: None
- **Examples**: Regular browsing, API calls, system updates

---

## Detection Model Information

### Ensemble Architecture
- **Random Forest**: 60% weight (high accuracy)
- **Deep Learning**: 40% weight (false positive optimized)
- **Confidence Threshold**: 0.35 (configurable in config.yaml)

### Feature Set (37 features)
- Flow characteristics: duration, rate, header length
- TCP flags: SYN, FIN, ACK, PSH, RST, URG, ECE, CWR
- Protocols: HTTP, HTTPS, DNS, Telnet, SMTP, SSH, IRC, TCP, UDP, DHCP, ARP, ICMP, IPv
- Statistical: min, max, avg, variance, covariance, IAT (Inter-Arrival Time)

### Severity Classification
- **Low**: BenignTraffic
- **Medium**: DDoS, DoS, Reconnaissance, Scanning
- **High**: Backdoor, Malware, Injection, MITM, Mirai, BruteForce, Browser Attacks

---

## Testing Commands

### Generate Test Traffic

```bash
# Run the anomaly generator
python tests/generate_anomalies.py

# Start live monitoring
python start_live_monitoring.py

# Use specific test configuration
python start_live_monitoring.py --config config.testing.yaml
```

### Test Specific Attack Categories

```bash
# Test DDoS detection
hping3 -S --flood -p 80 <target_ip>

# Test port scanning (Recon-PortScan)
nmap -sS -p 1-1000 <target_ip>

# Test SYN flood (DoS-SYN_Flood)
hping3 -S -p 80 --flood <target_ip>

# Test UDP flood (DoS-UDP_Flood)
hping3 --udp --flood -p 53 <target_ip>

# Test ICMP flood (DDoS-ICMP_Flood)
ping -f <target_ip>
```

### Web Application Attack Tests

```bash
# Test SQL Injection (use on your own systems only)
curl "http://localhost:8000/api?id=1' OR '1'='1"

# Test XSS
curl "http://localhost:8000/api?input=<script>alert('XSS')</script>"

# Test Command Injection
curl "http://localhost:8000/api?cmd=;ls -la"
```

### Monitoring Commands

```bash
# View real-time alerts
tail -f logs/alerts.log

# Check detection statistics
curl http://localhost:8000/api/stats

# View current flows
curl http://localhost:8000/api/flows

# Check system health
curl http://localhost:8000/api/health
```

---

## Safety Notes

⚠️ **WARNING**: Only test attacks on systems you own or have explicit permission to test.

- Never run attack tests against production systems
- Use isolated test environments or virtual networks
- Be aware that some tests may trigger IDS/IPS systems
- Some tests require root/administrator privileges
- Ensure proper firewall rules before testing

---

## References

- **Model Location**: `trained_models/retrained/`
- **Class Mapping**: `trained_models/retrained/class_mapping.json`
- **Prediction Module**: `src/models/predict.py`
- **Configuration**: `config.yaml`
- **Test Generator**: `tests/generate_anomalies.py`

---

## Quick Test Checklist

Use this checklist to systematically test detection capabilities:

- [ ] BenignTraffic - Normal browsing, legitimate API calls
- [ ] DDoS-SYN_Flood - SYN flooding from multiple sources
- [ ] DoS-HTTP_Flood - HTTP request flooding
- [ ] Recon-PortScan - Nmap port scanning
- [ ] SqlInjection - SQL injection attempts
- [ ] XSS - Cross-site scripting payloads
- [ ] MITM-ArpSpoofing - ARP poisoning detection
- [ ] DictionaryBruteForce - Multiple login attempts
- [ ] Mirai-udpplain - Mirai botnet activity
- [ ] VulnerabilityScan - Automated scanner detection

---

**Last Updated**: 2025-10-19
**System Version**: Unified IDS and IoT Security System
**Model Version**: Retrained False Positive Optimized
