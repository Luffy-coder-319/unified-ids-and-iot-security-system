# Detection Tuning Guide

## Problem: Attack Simulations Not Generating Alerts

If you're running attack simulations but not seeing any alerts, the detection system is likely configured for **production use** with very strict thresholds to minimize false positives.

---

## Root Causes

### 1. High Confidence Thresholds
**Location:** `config.yaml` - `detection.confidence_threshold`

**Problem:** Default value of 0.98 (98%) is too strict for testing
- Most ML models rarely achieve >95% confidence
- Attack simulations may trigger with 60-80% confidence
- This threshold was designed to prevent false positives in production

**Solution:** Lower to 0.30-0.50 for testing

---

### 2. High Packet Count Requirement
**Location:** `config.yaml` - `detection.min_packet_threshold`

**Problem:** Default value of 500 packets is too high for test attacks
- Your SYN flood sends only 250 packets
- UDP flood sends only 250 packets
- Real attacks may send fewer packets before being blocked

**Solution:** Lower to 30-50 packets for testing

---

### 3. Network Filtering Enabled
**Locations:**
- `config.yaml` - `detection.filter_localhost`
- `config.yaml` - `detection.filter_private_networks`
- `traffic_analyzer.py:186-252` - Cloud provider whitelist

**Problem:** Multi-layer filtering blocks legitimate test traffic
- Private network traffic (192.168.x.x, 10.x.x.x) is filtered
- Cloud provider IPs are whitelisted
- Localhost traffic requires higher confidence

**Solution:** Disable for testing by setting both to `false`

---

### 4. Model Ensemble Threshold
**Location:** `src/models/predict.py` - `OPTIMAL_THRESHOLD`

**Problem:** Default value of 0.55 filters borderline detections
- This threshold was optimized to reduce false positives
- Combined with other filters, it blocks many real attacks

**Solution:** Lower to 0.35 for testing

---

### 5. Rule-Based Detection Thresholds
**Location:** `src/models/hybrid_detector.py` - Various rules

**Problem:** Rules require very high packet rates
- SYN Flood: Requires 100 pkt/s, 20+ SYN packets, 70% SYN ratio
- UDP Flood: Requires 200 pkt/s, 20+ UDP packets
- High Rate DoS: Requires 500 pkt/s

**Solution:** Lowered thresholds in code:
- SYN Flood: 50 pkt/s, 10+ SYN packets, 60% SYN ratio
- UDP Flood: 50 pkt/s, 10+ UDP packets
- High Rate DoS: 100 pkt/s

---

## Testing vs Production Configurations

### Testing Configuration (config.testing.yaml)

Use this for attack simulations and testing:

```yaml
detection:
  mode: threshold
  confidence_threshold: 0.30          # Very sensitive
  min_packet_threshold: 30            # Low packet count
  filter_localhost: false             # No filtering
  filter_private_networks: false      # No filtering
  whitelist_ports: []                 # Detect on all ports
  adaptive_baseline:
    enabled: false                    # No learning during tests
```

**Model Threshold:** `OPTIMAL_THRESHOLD = 0.35` in predict.py

**When to Use:**
- Running attack simulations
- Testing detection capabilities
- Validating rule-based detection
- Debugging alert generation

---

### Production Configuration (config.yaml)

Use this for real network monitoring:

```yaml
detection:
  mode: threshold
  confidence_threshold: 0.98          # Very strict
  min_packet_threshold: 500           # High packet count
  filter_localhost: true              # Enable filtering
  filter_private_networks: true       # Enable filtering
  whitelist_ports: [80, 443, 53, ...]# Whitelist common services
  adaptive_baseline:
    enabled: true                     # Learn network patterns
    learning_period: 3600             # 1 hour learning
```

**Model Threshold:** `OPTIMAL_THRESHOLD = 0.55` in predict.py

**When to Use:**
- Production deployment
- Home network monitoring
- Enterprise security
- Minimizing false positives

---

## How to Switch Modes

### Method 1: Use Testing Config File
```bash
# Copy testing config to main config
copy config.testing.yaml config.yaml

# Restart the system
.\START_SYSTEM.ps1
```

### Method 2: Manual Adjustment
Edit `config.yaml` and change these values:

```yaml
detection:
  confidence_threshold: 0.30      # Lower for testing
  min_packet_threshold: 30        # Lower for testing
  filter_localhost: false         # Disable for testing
  filter_private_networks: false  # Disable for testing
```

Edit `src/models/predict.py` line 55:
```python
OPTIMAL_THRESHOLD = 0.35  # Lower for testing (was 0.55)
```

---

## Troubleshooting Alert Generation

### 1. Check Server Logs
Look for debug output showing predictions:
```
[DEBUG] Flow 192.168.56.1->192.168.1.1 - DDoS-SYN_Flood, Confidence: 65%
[FILTER] 192.168.56.1->192.168.1.1:80 | Threat:DDoS-SYN_Flood Conf:65% Pkts:100 ...
```

If you see `[DEBUG]` but not `[FILTER]` - model is detecting but filters are blocking

If you see `[FILTER]` but not `[!] ALERT` - threshold requirements not met

### 2. Verify Packet Capture
Check if packets are being captured:
```
[OK] Server is running and monitoring: \Device\NPF_{...}
```

### 3. Check Attack Parameters
Your test script shows:
- SYN Flood: 250 packets at 200 pkt/s
- UDP Flood: 250 packets at 200 pkt/s

**Recommendations:**
- Increase packet count to 300+
- Increase rate to 250+ pkt/s for better detection
- Ensure target IP is correct (not filtered)

### 4. Monitor Feature Extraction
Check if features are being extracted correctly:
```
Analyzing every 10 packets in flow...
```

If you don't see this, packet capture may not be working.

---

## Detection Mode Options

### Threshold Mode (Recommended for Production)
```yaml
detection:
  mode: threshold
```

**Behavior:**
- Applies all 6-7 layers of filtering
- High confidence threshold
- High packet count requirement
- Network filtering enabled
- Very few false positives

### Pure ML Mode (Not Recommended)
```yaml
detection:
  mode: pure_ml
```

**Behavior:**
- Trusts model completely
- No thresholds or filtering
- Any non-benign prediction triggers alert
- HIGH false positive rate
- Only for testing/debugging

---

## Recommended Testing Workflow

1. **Enable Testing Mode**
   ```bash
   copy config.testing.yaml config.yaml
   ```

2. **Update Model Threshold**
   Edit `src/models/predict.py` line 55:
   ```python
   OPTIMAL_THRESHOLD = 0.35
   ```

3. **Restart System**
   ```bash
   .\START_SYSTEM.ps1
   ```

4. **Run Attack Simulation**
   ```bash
   cd scripts
   .\test_external_attacks.ps1
   ```

5. **Monitor Alerts**
   - Watch server terminal for `[DEBUG]`, `[FILTER]`, and `[!] ALERT` messages
   - Check dashboard Alerts tab
   - Review `logs/alerts.jsonl`

6. **Restore Production Mode**
   - Restore original `config.yaml` from backup
   - Change `OPTIMAL_THRESHOLD` back to 0.55
   - Restart system

---

## Alert Filtering Layers

Understanding the 7 layers of filtering (in order):

1. **Threat Classification** - Must not be 'BenignTraffic'
2. **Confidence Threshold** - Must exceed configured threshold
3. **Packet Count** - Must exceed min_packet_threshold
4. **Cloud Provider Whitelist** - Must not be known cloud service
5. **Private Network Filter** - Must not be internal-only traffic
6. **Legitimate Port Filter** - Low packet count on common ports ignored
7. **Adaptive Baseline** - Optional learning-based suppression

**In Testing Mode:** Layers 2-3 are loosened, 4-7 are disabled

**In Production Mode:** All layers are active

---

## Summary Table

| Setting | Testing | Production | Location |
|---------|---------|-----------|----------|
| Confidence Threshold | 0.30 | 0.98 | config.yaml:22 |
| Min Packets | 30 | 500 | config.yaml:24 |
| Filter Localhost | false | true | config.yaml:25 |
| Filter Private Nets | false | true | config.yaml:26 |
| Model Threshold | 0.35 | 0.55 | predict.py:55 |
| Adaptive Baseline | false | true | config.yaml:39-41 |
| Whitelist Ports | [] | [80,443,...] | config.yaml:29-36 |

---

## Need Help?

If alerts still aren't generating after following this guide:

1. Check that you're running with Administrator privileges
2. Verify network interface is correct in config
3. Ensure trained models exist in `trained_models/retrained/`
4. Check for errors in server terminal output
5. Review `logs/app.log` for errors

For persistent issues, enable debug logging:
```yaml
logging:
  level: DEBUG
```
