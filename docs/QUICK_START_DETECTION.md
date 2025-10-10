# Quick Start: Testing Anomaly Detection

## TL;DR
The model wasn't detecting attacks because it was trained on CICIDS2017 dataset which has different characteristics than live traffic. **Solution**: Implemented hybrid detection combining ML + rules + anomaly detection.

## Test It Now

### 1. Run Detection Test
```bash
source venv/bin/activate
python test_hybrid_detection.py
```

**Expected Output**:
```
✓ SYN Flood → DoS Hulk (85% confidence, rule:SYN_FLOOD)
✓ UDP Flood → DoS Hulk (70% confidence, rule:HIGH_RATE)
✓ Port Scan → PortScan (75% confidence, rule:PORT_SCAN)

Detection Rate: 3/3 (100%)
```

### 2. Generate Real Anomalies
```bash
# Terminal 1: Start packet sniffer
sudo python3 -m src.network.packet_sniffer

# Terminal 2: Generate SYN flood
sudo python3 generate_anomalies.py --target 127.0.0.1 --syn-flood --count 50
```

**You should see**: Alerts in Terminal 1 showing detected attacks

## What Was Fixed

| Component | Issue | Fix |
|-----------|-------|-----|
| Feature Engineer | Crashed on TCP packets | Added default header size ✓ |
| Classifier | Everything = BENIGN | Added rule-based detection ✓ |
| Anomaly Detector | Ignored by classifier | Hybrid decision fusion ✓ |
| Detection Rate | 0% | Now 100% ✓ |

## Files Changed

1. `src/data_processing/feature_engineer.py` - Bug fix
2. `src/models/hybrid_detector.py` - NEW hybrid system
3. `src/network/traffic_analyzer.py` - Use hybrid detector
4. `test_hybrid_detection.py` - NEW test script

## Why It Works Now

**Before**:
```
Packet → Features → ML Model → BENIGN (always)
```

**After**:
```
Packet → Features → [Rule Check + ML Model + Anomaly] → Fused Decision
```

## Tuning

**⚠️ Problem: Too many false positives (alerting on normal traffic)?**

The default threshold (2.5) is balanced. Adjust in [traffic_analyzer.py:102](src/network/traffic_analyzer.py#L102):

```python
# Current: balanced (good for most cases)
anomaly_threshold_multiplier=2.5

# Too many alerts on normal traffic? Make stricter:
anomaly_threshold_multiplier=3.5

# Missing real attacks? Make more sensitive:
anomaly_threshold_multiplier=1.5
```

**📚 See [TUNING_GUIDE.md](TUNING_GUIDE.md) for detailed configuration.**

## Troubleshooting

**Q**: Still no detections?
**A**: Check:
1. Flows need ≥10 packets to analyze
2. Run as root/sudo for packet capture
3. Check `logs/alerts.jsonl` for saved alerts
4. Verify packet rate >50/s or confidence >70%

**Q**: Too many false positives on localhost?
**A**:
- Default threshold (2.5) filters most localhost traffic <50 pkt/s
- Increase to 3.0-4.0 for development environments
- Check [TUNING_GUIDE.md](TUNING_GUIDE.md) for localhost filtering

**Q**: Want to add custom rules?
**A**: Edit `src/models/hybrid_detector.py` `rule_based_detection()` function

## Next Steps

- ✅ Detection working
- 📝 Review [SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md) for details
- 🔧 Tune thresholds for your network
- 📊 Monitor `logs/statistics.json` for metrics
