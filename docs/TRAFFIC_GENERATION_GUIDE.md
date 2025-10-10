# Traffic Generation Guide

Complete guide for testing the IDS with different traffic patterns.

---

## Quick Start

### Option 1: Application-Level Traffic (No sudo required)
```bash
# Terminal 1: Start IDS
source venv/bin/activate
sudo venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Generate traffic
python generate_test_traffic.py
```

### Option 2: Packet-Level Traffic (Requires sudo)
```bash
# Terminal 1: Start IDS
source venv/bin/activate
sudo venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Generate packets
sudo venv/bin/python generate_packet_traffic.py
```

---

## Traffic Generators

### 1. Application-Level Traffic (`generate_test_traffic.py`)

**Pros**:
- No sudo required
- Easy to use
- Tests real HTTP/TCP behavior
- Works on any system

**Cons**:
- Limited to application protocols
- Can't craft raw packets
- May not trigger all detection rules

**Usage**:

```bash
# Run all scenarios
python generate_test_traffic.py

# Run specific scenario
python generate_test_traffic.py --scenario flood
python generate_test_traffic.py --scenario scan
python generate_test_traffic.py --scenario normal

# Custom target
python generate_test_traffic.py --target http://192.168.1.100:8000
```

**Scenarios Available**:
- `normal` - Normal HTTP traffic (should NOT alert)
- `slow` - Slow legitimate requests (should NOT alert)
- `flood` - HTTP flood attack (SHOULD alert)
- `spam` - Connection spam (SHOULD alert)
- `scan` - Port scan (SHOULD alert)
- `all` - Run all scenarios (default)

---

### 2. Packet-Level Traffic (`generate_packet_traffic.py`)

**Pros**:
- Full control over packets
- Tests low-level detection
- Triggers all rules
- More realistic attacks

**Cons**:
- Requires sudo/root
- Needs scapy installed
- Only works on Linux/Mac

**Usage**:

```bash
# Run all scenarios
sudo venv/bin/python generate_packet_traffic.py

# Run specific scenario
sudo venv/bin/python generate_packet_traffic.py --scenario syn-flood
sudo venv/bin/python generate_packet_traffic.py --scenario udp-flood
sudo venv/bin/python generate_packet_traffic.py --scenario port-scan

# Custom parameters
sudo venv/bin/python generate_packet_traffic.py \
    --scenario syn-flood \
    --target 127.0.0.1 \
    --port 8000 \
    --count 200 \
    --rate 500
```

**Scenarios Available**:
- `normal` - Normal TCP traffic (should NOT alert)
- `syn-flood` - SYN flood attack (SHOULD alert as DoS Hulk)
- `udp-flood` - UDP flood attack (SHOULD alert as DDoS)
- `icmp-flood` - ICMP flood/ping flood (SHOULD alert)
- `port-scan` - Port scan (SHOULD alert as PortScan)
- `all` - Run all scenarios (default)

---

### 3. Original Anomaly Generator (`generate_anomalies.py`)

**Most powerful option** - generates various attack types.

**Usage**:

```bash
# SYN flood
sudo python3 generate_anomalies.py --target 127.0.0.1 --syn-flood --count 200 --rate 500

# UDP flood
sudo python3 generate_anomalies.py --target 127.0.0.1 --udp-flood --count 200 --rate 500

# ICMP flood
sudo python3 generate_anomalies.py --target 127.0.0.1 --icmp-flood --count 200 --rate 500

# Port scan
sudo python3 generate_anomalies.py --target 127.0.0.1 --port-scan --ports 1-1024

# Large payloads
sudo python3 generate_anomalies.py --target 127.0.0.1 --large-payload --count 10

# Malformed packets
sudo python3 generate_anomalies.py --target 127.0.0.1 --malformed --count 50

# Multiple attacks
sudo python3 generate_anomalies.py --target 127.0.0.1 --syn-flood --udp-flood --port-scan --count 100
```

---

## Expected Results

### What SHOULD Trigger Alerts

| Attack Type | Detection Method | Confidence | Alert Type |
|-------------|-----------------|------------|------------|
| SYN Flood (>100 pkt/s) | Rule: SYN_FLOOD | 85% | DoS Hulk |
| UDP Flood (>200 pkt/s) | Rule: UDP_FLOOD | 80% | DDoS |
| Port Scan | Rule: PORT_SCAN | 75% | PortScan |
| High Rate (>500 pkt/s) | Rule: HIGH_RATE | 70% | DoS Hulk |
| HTTP Flood | Rule: HIGH_RATE | 70% | DoS Hulk |
| Connection Spam | Anomaly + Rule | 65-75% | Anomaly/DDoS |

### What Should NOT Trigger Alerts

| Traffic Type | Rate | Reason |
|--------------|------|--------|
| Normal HTTP | 5-10 req/s | Below threshold, localhost filter |
| Slow Requests | <1 req/s | Very low rate |
| Single Connection | Any | Not enough packets (need ≥10) |
| Localhost API | <50 pkt/s | Filtered by localhost exception |

---

## Checking Results

### 1. Console Output
Look for DEBUG messages:
```
[DEBUG] Flow 127.0.0.1:xxxxx->127.0.0.1 - Prediction: DoS Hulk, Severity: high, Method: rule:SYN_FLOOD, Confidence: 85.0%
[!] ALERT: {'time': ..., 'src': '127.0.0.1', 'dst': '127.0.0.1', 'threat': 'DoS Hulk', ...}
```

### 2. Log File
```bash
# View recent alerts
tail -20 logs/alerts.jsonl

# Count alerts
wc -l logs/alerts.jsonl

# View statistics
cat logs/statistics.json | python -m json.tool
```

### 3. API
```bash
# Get all alerts
curl http://localhost:8000/api/alerts

# Get statistics
curl http://localhost:8000/api/stats

# Get flows
curl http://localhost:8000/api/flows
```

### 4. Web Interface
Open in browser:
```
http://localhost:8000
```

---

## Test Scenarios

### Scenario 1: Verify Detection Works
```bash
# Terminal 1: Start IDS
sudo venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Generate attack
sudo venv/bin/python generate_packet_traffic.py --scenario syn-flood --count 150 --rate 500

# Check: Should see alert within 5 seconds
curl http://localhost:8000/api/alerts | python -m json.tool
```

**Expected**: Alert for "DoS Hulk" with 85% confidence

---

### Scenario 2: Verify No False Positives
```bash
# Terminal 1: Start IDS
sudo venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Generate normal traffic
python generate_test_traffic.py --scenario normal

# Check: Should see NO alerts
curl http://localhost:8000/api/alerts | python -m json.tool
```

**Expected**: Zero or very few alerts (benign traffic filtered)

---

### Scenario 3: Mixed Traffic
```bash
# Terminal 1: Start IDS
sudo venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Normal traffic (background)
python generate_test_traffic.py --scenario normal &

# Wait 10 seconds, then attack
sleep 10
sudo venv/bin/python generate_packet_traffic.py --scenario syn-flood --count 200

# Check: Should only see alert for SYN flood
curl http://localhost:8000/api/alerts | python -m json.tool
```

**Expected**: 1 alert for attack, none for normal traffic

---

## Troubleshooting

### No Alerts Generated

**Problem**: Traffic generated but no alerts

**Checklist**:
1. ✓ IDS running with sudo?
2. ✓ Packet count ≥10? (need 10 packets to analyze)
3. ✓ Rate high enough? (need >50 pkt/s for localhost attacks)
4. ✓ Check DEBUG output for predictions
5. ✓ Threshold too high? Lower in [traffic_analyzer.py:102](src/network/traffic_analyzer.py#L102)

### Too Many False Positives

**Problem**: Normal traffic triggering alerts

**Solution**:
1. Increase threshold: `anomaly_threshold_multiplier=3.5`
2. Check if localhost filter active
3. See [TUNING_GUIDE.md](TUNING_GUIDE.md)

### Permission Denied

**Problem**: "Permission denied" or "Operation not permitted"

**Solution**:
```bash
# Use sudo with venv python
sudo venv/bin/python script.py

# NOT just:
sudo python script.py  # Wrong! Uses system Python
```

### Module Not Found

**Problem**: "No module named 'scapy'" or similar

**Solution**:
```bash
# Activate venv first
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Then use with sudo
sudo venv/bin/python script.py
```

---

## Parameters Reference

### `generate_test_traffic.py`
```
--target URL      Target API URL (default: http://127.0.0.1:8000)
--scenario STR    Traffic scenario: normal|flood|scan|spam|slow|all
```

### `generate_packet_traffic.py`
```
--target IP       Target IP address (default: 127.0.0.1)
--port INT        Target port (default: 8000)
--scenario STR    Attack scenario: normal|syn-flood|udp-flood|icmp-flood|port-scan|all
--count INT       Number of packets (default: 100)
--rate INT        Packets per second (default: 200)
```

### `generate_anomalies.py`
```
--target IP       Target IP (required)
--syn-flood       Enable SYN flood attack
--udp-flood       Enable UDP flood attack
--icmp-flood      Enable ICMP flood attack
--port-scan       Enable port scan
--large-payload   Enable large payload attack
--malformed       Enable malformed packets
--dport INT       Destination port (default: 80)
--count INT       Number of packets per attack (default: 200)
--rate FLOAT      Packets per second (default: 500.0)
--payload INT     Payload size for UDP flood (default: 200)
--ports STR       Port range for scan (default: 1-1024)
--spoof           Spoof source IPs (may not work on all systems)
```

---

## Best Practices

1. **Start Simple**: Begin with `generate_test_traffic.py` (no sudo required)

2. **One Attack at a Time**: Test each scenario separately to verify detection

3. **Check Logs**: Always verify alerts are being generated and logged

4. **Tune Thresholds**: Adjust based on your environment (see [TUNING_GUIDE.md](TUNING_GUIDE.md))

5. **Use Realistic Traffic**: Mix normal and attack traffic for real-world testing

6. **Monitor Performance**: High rates (>1000 pkt/s) may overload the system

---

## Quick Commands

```bash
# Complete test workflow
sudo venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
sleep 5
python generate_test_traffic.py --scenario all
sudo venv/bin/python generate_packet_traffic.py --scenario all
curl http://localhost:8000/api/alerts | python -m json.tool
```
