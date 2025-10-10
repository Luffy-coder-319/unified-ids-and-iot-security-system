# Detection Issues and Solutions

## Problem Summary
The IDS is **NOT detecting anomalies** from generated or live network traffic, even though the system is capturing packets and processing them correctly.

## Root Causes Identified

### 1. **Classification Model Limitation** ⚠️
- **Issue**: RandomForest classifier predicts everything as `BENIGN`
- **Why**: Model was trained on CICIDS2017 dataset which has different statistical properties than live/synthetic traffic
- **Evidence**:
  - SYN flood with 50 packets, 1020 pkts/s → Classified as BENIGN
  - UDP flood with 510 pkts/s → Classified as BENIGN
  - Anomaly detector shows high MSE (2.0) but classifier ignores it

### 2. **Feature Distribution Mismatch** 📊
- **Issue**: Training data features have different value ranges than live traffic
- **Example**:
  - CICIDS2017: Pre-processed flows with full bidirectional communication
  - Live traffic: One-sided flows, incomplete handshakes, different timing
- **Impact**: Model doesn't generalize to real-world traffic patterns

### 3. **Flow Analysis Threshold** 📈
- **Issue**: Traffic analyzer only checks flows every 10 packets
- **Location**: [traffic_analyzer.py:95](src/network/traffic_analyzer.py#L95)
- **Impact**: Short attacks (<10 packets) are never analyzed

### 4. **Anomaly Detection Works but is Ignored** ✓
- **Finding**: Autoencoder correctly detects high MSE values
- **Issue**: Classification result overrides anomaly detection
- **Code**: [predict.py:104-106](src/models/predict.py#L104-106) - severity based only on classifier

## Test Results

### Benign Traffic (Normal HTTP)
```
Flow Packets/s: 10.53
SYN Flag Count: 0
→ Classification: BENIGN ✓
→ Anomaly MSE: 2.0 (high)
```

### SYN Flood Attack
```
Flow Packets/s: 1020.41
SYN Flag Count: 50
→ Classification: BENIGN ✗ (WRONG!)
→ Anomaly MSE: 2.0 (high) ✓
```

### UDP Flood Attack
```
Flow Packets/s: 510.20
→ Classification: BENIGN ✗ (WRONG!)
→ Anomaly MSE: 2.0 (high) ✓
```

## Solutions

### Quick Fix (Use Anomaly Detection as Primary)
**Change prediction logic to trust anomaly detector:**

```python
# In predict.py predict_threat()
if anomaly_info['severity'] in ['medium', 'high']:
    # Override classifier if anomaly detected
    if predicted_label == 'BENIGN':
        predicted_label = 'Anomaly Detected'
        severity = anomaly_info['severity']
```

### Medium-term Fix (Hybrid Detection)
**Combine both models with rules:**

1. If anomaly MSE > threshold AND high packet rate → DDoS/DoS
2. If anomaly MSE > threshold AND high SYN count → Port Scan
3. Otherwise use classifier prediction

### Long-term Fix (Retrain Model)
**Retrain classifier on augmented dataset:**

1. Mix CICIDS2017 with synthetic attack traffic
2. Include live benign traffic samples
3. Use semi-supervised learning to adapt to new patterns
4. Regular retraining with production data

### Architectural Fix (Multi-Model Ensemble)
**Use multiple detection methods:**

```
┌─────────────────┐
│ Live Packets    │
└────────┬────────┘
         │
    ┌────▼─────────┐
    │ Feature Eng  │
    └────┬─────────┘
         │
    ┌────┴──────────┐
    │               │
┌───▼────┐    ┌────▼────────┐
│Anomaly │    │Classifier   │
│Detect  │    │(RF/DL)      │
└───┬────┘    └────┬────────┘
    │              │
    └──────┬───────┘
           │
    ┌──────▼──────────┐
    │ Rule-based      │
    │ Decision Fusion │
    └─────────────────┘
```

## Immediate Recommendations

### Option 1: Use Only Anomaly Detection (Fastest)
- Disable classifier predictions
- Alert on anomaly MSE > threshold
- Less precise but will catch attacks

### Option 2: Add Rule-based Detection
- Create rules for common patterns:
  - SYN flood: SYN flags > 80% of packets
  - Port scan: >20 unique dest ports
  - UDP flood: UDP packet rate > 500/s
- Combine with anomaly detection

### Option 3: Lower Detection Threshold
- Reduce flow packet threshold from 10 to 5
- Analyze flows more frequently
- May increase false positives

## Files to Modify

1. **[src/models/predict.py](src/models/predict.py)** - Update `predict_threat()` logic
2. **[src/network/traffic_analyzer.py](src/network/traffic_analyzer.py)** - Adjust thresholds
3. **[src/data_processing/feature_engineer.py](src/data_processing/feature_engineer.py)** - Fixed TCP header bug ✓

## Testing Command

Run diagnostic test:
```bash
source venv/bin/activate
python test_detection.py
```

## Next Steps

Choose one solution and implement:
1. **Quick win**: Use anomaly detection + simple rules
2. **Better accuracy**: Retrain model with mixed data
3. **Production ready**: Implement ensemble + continuous learning
