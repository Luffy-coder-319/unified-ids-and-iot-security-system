# Detection Modes: Pure ML vs Threshold-Based

## Overview

The IDS system supports **two detection modes**:

1. **Threshold Mode** (Default) - Uses ML models + thresholds + filtering
2. **Pure ML Mode** - Trusts ML model classification completely

## How It Works

### Detection Pipeline

```
Network Traffic → Extract Features → ML Models (RandomForest + Autoencoder) → Prediction
                                                                                   ↓
                                                                    [MODE SELECTION]
                                                                                   ↓
                                                   ┌───────────────────────────────┴───────────────────────────────┐
                                                   ↓                                                                 ↓
                                          THRESHOLD MODE                                                      PURE ML MODE
                                                   ↓                                                                 ↓
                                     Apply 6-layer filtering:                                       Trust model completely
                                     1. Confidence ≥95%                                            If threat → Alert
                                     2. Packets ≥100                                               No filtering
                                     3. Not cloud provider                                          No thresholds
                                     4. Not private IPs
                                     5. Not legitimate ports
                                     6. Is threat (not BENIGN)
                                                   ↓
                                            Alert/Ignore
```

---

## Mode 1: Threshold Mode (Default - Recommended for Production)

### How It Works

**Features → ML Model → Prediction → Apply Thresholds → Apply Filters → Alert**

The system makes decisions using:
1. **ML Model prediction** (RandomForest + Autoencoder)
2. **Confidence thresholds** (must be ≥95% confident)
3. **Packet count thresholds** (must have ≥100 packets)
4. **Business logic filters** (whitelist Google, AWS, Microsoft, etc.)
5. **Private network filters** (ignore local 192.168.x.x traffic)
6. **Legitimate port filters** (HTTP/HTTPS need 200+ packets to alert)

### Pros ✅
- **Fewer false positives** - Filters out legitimate traffic
- **Production-ready** - Safe for real deployments
- **Whitelists trusted services** - Won't alert on Google, AWS, CDNs
- **Configurable** - Adjust thresholds to your needs
- **Business logic** - Can add custom rules

### Cons ⚠️
- **Might miss subtle attacks** - Requires high confidence
- **Needs tuning** - Thresholds may need adjustment
- **More complex** - Additional filtering logic
- **Slower response** - Must meet multiple criteria

### Configuration

```yaml
detection:
  mode: 'threshold'  # Use threshold mode

  confidence_threshold: 0.95     # 95% confidence required
  min_packet_threshold: 100      # 100+ packets required
  anomaly_multiplier: 5.0        # 5x above baseline

  filter_private_networks: true  # Filter local traffic
  legitimate_port_packet_threshold: 200  # HTTP/HTTPS needs 200 pkts
```

### When to Use
- ✅ Production environments
- ✅ When false positives are costly
- ✅ Enterprise networks with cloud services
- ✅ When you need whitelisting capability
- ✅ Compliance requirements

---

## Mode 2: Pure ML Mode (Research/Testing)

### How It Works

**Features → ML Model → Prediction → Alert (if threat)**

The system:
1. Extracts features from network flow
2. Sends to ML models (RandomForest + Autoencoder)
3. Gets classification (BENIGN, DDoS, PortScan, etc.)
4. **Trusts the model** - If model says "DDoS", creates alert immediately
5. **No thresholds** - No confidence requirements
6. **No filtering** - No whitelist, no business logic

### Pros ✅
- **Simpler** - Just trust the trained model
- **More sensitive** - Detects subtle patterns
- **Faster response** - No filtering delays
- **Research-friendly** - See what model really thinks
- **No tuning needed** - Model decides everything

### Cons ⚠️
- **More false positives** - Model isn't 100% accurate
- **May flag Google/AWS** - No whitelisting
- **Noisy** - Alerts on anything model thinks is suspicious
- **Not production-ready** - Too sensitive for real use

### Configuration

```yaml
detection:
  mode: 'pure_ml'  # Use pure ML mode

  # All threshold settings are ignored in pure_ml mode
  # confidence_threshold: ignored
  # min_packet_threshold: ignored
  # anomaly_multiplier: ignored
```

### When to Use
- ✅ Security research
- ✅ Model evaluation/testing
- ✅ Understanding model behavior
- ✅ Lab environments
- ✅ Dataset generation
- ❌ **NOT for production** (too many false positives)

---

## Comparison Table

| Feature | Threshold Mode | Pure ML Mode |
|---------|---------------|--------------|
| **False Positives** | Very Low (filtered) | Higher (unfiltered) |
| **False Negatives** | Possible (if below thresholds) | Lower (detects more) |
| **Sensitivity** | Low (strict) | High (sensitive) |
| **Whitelist Support** | Yes (Google, AWS, etc.) | No |
| **Configuration** | Tunable thresholds | No configuration needed |
| **Production Ready** | ✅ Yes | ❌ No |
| **Research/Testing** | ⚠️ May miss subtle attacks | ✅ Best for research |
| **Response Time** | Slower (filtering) | Faster (immediate) |
| **Alerts on Normal Traffic** | Rare | Common |

---

## How to Switch Modes

### Enable Threshold Mode (Default)

Edit [config.yaml](config.yaml):

```yaml
detection:
  mode: 'threshold'
  confidence_threshold: 0.95
  min_packet_threshold: 100
  anomaly_multiplier: 5.0
```

**What you'll see:**
```
[INFO] Detection mode: threshold
[INFO] Threshold mode: Confidence ≥0.95, Packets ≥100
[FILTER] 192.168.1.5->142.251.47.14:443 | Threat:DDoS Conf:87% Pkts:50 Cloud:True
(Filtered out - Google IP, low confidence, few packets)
```

---

### Enable Pure ML Mode

Edit [config.yaml](config.yaml):

```yaml
detection:
  mode: 'pure_ml'
```

**What you'll see:**
```
[INFO] Detection mode: pure_ml
[INFO] Pure ML mode: Trusting model classification without thresholds
[PURE ML] 192.168.1.5->142.251.47.14 | Threat:DDoS Conf:75% Pkts:20
[!] ALERT: DDoS detected from 192.168.1.5
(Alert generated - no filtering)
```

---

## Restart Required

After changing the mode in config.yaml, **restart the system**:

```batch
# Stop current system (Ctrl+C)
# Then restart
START_SYSTEM.bat
```

---

## Example Scenarios

### Scenario 1: Normal Browsing to YouTube

**Traffic:** 50 packets to 142.251.47.14 (Google/YouTube)
**ML Model says:** "DDoS" (87% confidence)

| Mode | Result | Reason |
|------|--------|--------|
| **Threshold** | ❌ No Alert | Filtered (Google IP, <100 packets, <95% conf) |
| **Pure ML** | ✅ Alert | Model said "DDoS", trust it |

### Scenario 2: Real SYN Flood Attack

**Traffic:** 1000 SYN packets to localhost at 500 pkt/s
**ML Model says:** "DDoS" (98% confidence)

| Mode | Result | Reason |
|------|--------|--------|
| **Threshold** | ✅ Alert | High confidence, many packets, clear threat |
| **Pure ML** | ✅ Alert | Model said "DDoS", trust it |

### Scenario 3: Subtle Port Scan

**Traffic:** Slow scan of 5 ports over 5 minutes
**ML Model says:** "PortScan" (92% confidence)

| Mode | Result | Reason |
|------|--------|--------|
| **Threshold** | ❌ No Alert | <100 packets threshold not met |
| **Pure ML** | ✅ Alert | Model detected it, trust it |

---

## Recommendations

### For Production Use
```yaml
detection:
  mode: 'threshold'
  confidence_threshold: 0.95    # Very high confidence
  min_packet_threshold: 100     # Sustained activity only
  anomaly_multiplier: 5.0       # Clear anomalies only
```

**Result:** Very few false positives, safe for production

---

### For Security Testing
```yaml
detection:
  mode: 'threshold'
  confidence_threshold: 0.85    # Medium confidence
  min_packet_threshold: 50      # More sensitive
  anomaly_multiplier: 3.0       # Moderate anomalies
```

**Result:** Balanced - detects more threats, some false positives

---

### For Research/ML Evaluation
```yaml
detection:
  mode: 'pure_ml'
```

**Result:** See everything the model thinks is a threat

---

## Technical Implementation

### Threshold Mode Code Path

```python
# In traffic_analyzer.py
if detection_mode == 'threshold':
    # Apply 6-layer filtering
    min_confidence = config.get('confidence_threshold', 0.95)
    has_high_confidence = prediction['confidence'] >= min_confidence

    min_packets = config.get('min_packet_threshold', 100)
    has_significant_traffic = pkt_count >= min_packets

    is_cloud = check_cloud_whitelist(src_ip, dst_ip)
    is_private = check_private_network(src_ip, dst_ip)
    is_legit_port = check_legitimate_ports(dst_port, pkt_count)

    should_alert = (
        is_threat and
        has_high_confidence and
        has_significant_traffic and
        not is_cloud and
        not is_private and
        not is_legit_port
    )
```

### Pure ML Mode Code Path

```python
# In traffic_analyzer.py
if detection_mode == 'pure_ml':
    # Trust the model completely
    is_threat = (prediction['attack'] != 'BENIGN')
    should_alert = is_threat

    if should_alert:
        print(f"[PURE ML] {src}->{dst} | Threat:{threat} Conf:{conf}%")
        create_alert(prediction)
```

---

## Summary

| Use Case | Recommended Mode | Configuration |
|----------|-----------------|---------------|
| Production deployment | Threshold | confidence=0.95, packets=100 |
| Security operations center | Threshold | confidence=0.90, packets=50 |
| Threat hunting | Threshold | confidence=0.85, packets=30 |
| ML model research | Pure ML | No config needed |
| Dataset generation | Pure ML | No config needed |
| Testing attack detection | Threshold | confidence=0.85, packets=50 |

**Bottom Line:**
- **Threshold Mode** = Production-ready, fewer false positives, requires tuning
- **Pure ML Mode** = Research tool, see raw model output, not for production

---

**Current Default:** Threshold Mode with strict settings (95% confidence, 100+ packets)

To answer your original question: **Yes, the system CAN work purely on ML classification by setting `mode: 'pure_ml'` in config.yaml!** 🚀
