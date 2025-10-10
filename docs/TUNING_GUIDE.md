# Detection Tuning Guide

## Problem: Too Many False Positives

If you're seeing alerts for normal traffic (especially localhost), adjust these settings:

---

## Quick Fix: Adjust Anomaly Threshold

**File**: [src/network/traffic_analyzer.py:102](src/network/traffic_analyzer.py#L102)

```python
# Current setting
anomaly_threshold_multiplier=2.5  # Balanced

# Too many false positives? Increase:
anomaly_threshold_multiplier=3.0  # More strict

# Missing real attacks? Decrease:
anomaly_threshold_multiplier=1.5  # More sensitive
```

**What it does**: Higher values mean the model needs stronger evidence before flagging anomalies.

---

## Threshold Recommendations

| Environment | Threshold | Description |
|-------------|-----------|-------------|
| **Production Network** | 2.5 - 3.0 | Reduce false positives, focus on real threats |
| **Lab/Testing** | 1.5 - 2.0 | More sensitive, catch more patterns |
| **High Security** | 1.0 - 1.5 | Very sensitive, expect false positives |
| **Development (localhost)** | 3.0+ | Filter out dev traffic noise |

---

## Understanding the Filters

### 1. Anomaly Threshold Multiplier
```python
anomaly_threshold_multiplier=2.5
```
- Anomaly MSE must be **2.5x** the training threshold
- Training threshold: ~1.53
- Effective threshold: 1.53 × 2.5 = **3.825**
- Only anomalies with MSE > 3.825 trigger alerts

### 2. Localhost Filter
```python
is_localhost = key[0] in ('127.0.0.1', '::1') or key[1] in ('127.0.0.1', '::1')
is_low_rate = (pkt_count / duration) < 50
```
- Suppresses alerts for localhost traffic with <50 pkts/sec
- API calls, database queries, etc. won't trigger false alerts
- **Real attacks** on localhost (>50 pkt/s or high confidence) still detected

### 3. Confidence Filter
```python
prediction.get('confidence', 0) >= 0.7
```
- Requires 70% confidence to alert
- Rule-based detections have 70-85% confidence
- Anomaly-only detections may be suppressed if low confidence

---

## Disable Localhost Filtering

If you want to detect attacks on localhost services:

**File**: [src/network/traffic_analyzer.py:115-118](src/network/traffic_analyzer.py#L115-118)

```python
# Before (filters localhost)
should_alert = (
    threat != 'BENIGN' and
    (prediction.get('confidence', 0) >= 0.7 or not (is_localhost and is_low_rate))
)

# After (alerts on all threats)
should_alert = (threat != 'BENIGN')
```

---

## Rule-Based Detection Tuning

Rules are in [src/models/hybrid_detector.py](src/models/hybrid_detector.py#L24-84)

### SYN Flood Rule
```python
# Current
if syn_ratio > 0.7 and syn_count > 20 and pkt_rate > 100:
    return {'attack': 'DoS Hulk', 'confidence': 0.85}

# More sensitive (catch smaller floods)
if syn_ratio > 0.6 and syn_count > 10 and pkt_rate > 50:
    return {'attack': 'DoS Hulk', 'confidence': 0.80}
```

### High Rate Rule
```python
# Current
if pkt_rate > 500:
    return {'attack': 'DoS Hulk', 'confidence': 0.70}

# Less sensitive (reduce false positives)
if pkt_rate > 1000:
    return {'attack': 'DoS Hulk', 'confidence': 0.70}
```

---

## Testing Your Configuration

### 1. Test with synthetic attacks
```bash
# Terminal 1: Start IDS
sudo venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Generate attack
sudo python3 generate_anomalies.py --target 127.0.0.1 --syn-flood --count 100 --rate 500
```

**Expected**: Should detect (high rate + high SYN count)

### 2. Test with normal traffic
```bash
# Generate normal web traffic
for i in {1..20}; do curl http://localhost:8000/api/health; sleep 0.5; done
```

**Expected**: Should NOT alert (low rate, normal API calls)

### 3. Check debug output
Look for:
```
[DEBUG] Flow 127.0.0.1:xxxxx->127.0.0.1 - Prediction: BENIGN, Severity: low, Method: all_agree, Confidence: 90.0%
```

---

## Common Scenarios

### Scenario 1: Localhost API alerts constantly
**Problem**: Normal API traffic triggering anomaly detection

**Solution**:
1. Increase threshold to 3.0+
2. Keep localhost filter enabled
3. Check if rate is actually <50 pkt/s

### Scenario 2: Missing real attacks
**Problem**: Known attack patterns not detected

**Solution**:
1. Decrease threshold to 1.5-2.0
2. Check rule patterns match attack characteristics
3. Verify packet rate is high enough (>10 packets analyzed)

### Scenario 3: SSH/DB connections flagged
**Problem**: Legitimate high-traffic services detected

**Solution**:
1. Add port whitelist in traffic_analyzer.py:
```python
WHITELISTED_PORTS = {22, 3306, 5432, 6379}  # SSH, MySQL, PostgreSQL, Redis

if key[2] in WHITELISTED_PORTS or (TCP in packet and packet[TCP].dport in WHITELISTED_PORTS):
    should_alert = False
```

---

## Monitoring & Metrics

Check statistics:
```bash
cat logs/statistics.json
```

Look for:
- **Total alerts**: Should be reasonable (not thousands)
- **Alerts by severity**: High severity should be rare
- **Alerts by type**: Check for patterns

Check recent alerts:
```bash
tail -10 logs/alerts.jsonl
```

---

## Recommended Settings by Use Case

### Web Server (Production)
```python
anomaly_threshold_multiplier=3.0
confidence_threshold=0.75
localhost_filter=True
```

### IoT Gateway
```python
anomaly_threshold_multiplier=2.0
confidence_threshold=0.70
localhost_filter=False  # Monitor all device traffic
```

### Development Environment
```python
anomaly_threshold_multiplier=4.0
confidence_threshold=0.85
localhost_filter=True
```

### Honeypot / High Security
```python
anomaly_threshold_multiplier=1.0
confidence_threshold=0.60
localhost_filter=False
```

---

## Advanced: Per-Network Tuning

Create different thresholds for different networks:

```python
# In traffic_analyzer.py
def get_threshold_for_ip(ip):
    if ip.startswith('192.168.'):
        return 3.0  # Internal network - less sensitive
    elif ip.startswith('10.'):
        return 2.0  # DMZ - moderate
    else:
        return 1.5  # External - very sensitive

# Use it
threshold = get_threshold_for_ip(key[0])
prediction = hybrid_predict_threat(features, anomaly_threshold_multiplier=threshold)
```

---

## Need Help?

1. Check [SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md) for how detection works
2. Run diagnostic: `python test_hybrid_detection.py`
3. Review debug output in console for pattern analysis
