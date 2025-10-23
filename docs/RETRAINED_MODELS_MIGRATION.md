# Retrained Models Migration

## Overview
The detection system has been migrated to use the retrained models from `trained_models/retrained/` directory. These models are optimized for false positive reduction and provide better accuracy.

## Changes Made

### 1. Model Updates

#### Previous Models (Removed)
- **XGBoost**: `trained_models/final/final_xgb_optuna.pkl`
- **LightGBM**: `trained_models/final/final_lgbm_optuna.pkl`
- **FFNN Residual**: `trained_models/dl_models/final_ffnn_residual.keras`
- **CNN Stable**: `trained_models/dl_models/final_cnn_stable.keras`
- **Anomaly Autoencoder**: `trained_models/dl_models/anomaly_autoencoder.keras`

#### New Models (Active)
- **Random Forest Calibrated**: `trained_models/retrained/random_forest_calibrated.pkl`
- **Deep Learning FP-Optimized**: `trained_models/retrained/dl_model_retrained_fp_optimized.keras`
- **Standard Scaler**: `trained_models/retrained/scaler_standard_retrained.pkl`

### 2. Feature Engineering

**Feature Count**: 37 features (reduced from 46)

**Feature List**:
```
flow_duration, Header_Length, Protocol Type, Duration,
Rate, Drate, fin_flag_number, syn_flag_number,
psh_flag_number, ack_flag_number, ece_flag_number, cwr_flag_number,
syn_count, fin_count, urg_count, rst_count,
HTTP, HTTPS, DNS, Telnet, SMTP, SSH, IRC,
TCP, UDP, DHCP, ARP, ICMP, IPv,
Tot sum, Min, Max, AVG, Tot size, IAT,
Covariance, Variance
```

**Removed Features**:
- Srate (replaced by Rate)
- LLC
- Std, Number, Magnitue, Radius, Weight

### 3. Attack Classification

**Total Classes**: 34 (including BenignTraffic)

**New Attack Types**:
- Backdoor_Malware
- BrowserHijacking
- CommandInjection
- DDoS variants (ACK_Fragmentation, HTTP_Flood, ICMP_Flood, etc.)
- DoS variants (HTTP_Flood, SYN_Flood, TCP_Flood, UDP_Flood)
- DNS_Spoofing
- DictionaryBruteForce
- MITM-ArpSpoofing
- Mirai variants (greeth_flood, greip_flood, udpplain)
- Recon variants (HostDiscovery, OSScan, PingSweep, PortScan)
- SqlInjection
- Uploading_Attack
- VulnerabilityScan
- XSS

### 4. Ensemble Detection

**Weights**:
- Random Forest: 60%
- Deep Learning: 40%

**Optimal Threshold**: 0.55 (for false positive reduction)

**Detection Method**:
1. Both models make predictions
2. Weighted confidence calculated: `(RF_conf * 0.6) + (DL_conf * 0.4)`
3. If weighted confidence < 0.55 → BenignTraffic
4. If weighted confidence >= 0.55:
   - If both agree → Use consensus with boosted confidence
   - If disagree → Use model with higher weighted confidence

### 5. Performance Metrics

Based on training configuration:

**Random Forest**:
- Accuracy: 99.08%
- Precision: 99.18%
- Recall: 99.08%
- F1-Score: 99.10%

**Deep Learning**:
- Accuracy: 89.61%
- Precision: 90.44%
- Recall: 89.61%
- F1-Score: 47.63%

**Ensemble**:
- Accuracy: 98.63%
- Precision: 99.65%
- Recall: 98.63%
- F1-Score: 99.03%

**Threshold Optimization**:
- Precision: 92.54%
- Recall: 85.28%
- F1-Score: 87.61%

## File Changes

### Modified Files

1. **[src/models/predict.py](../src/models/predict.py)**
   - Updated model paths to use retrained models
   - Replaced encoder with class mapping JSON
   - Updated feature names to match 37-feature set
   - Implemented weighted ensemble with threshold
   - Added load_class_mapping() function
   - Removed separate anomaly detection (now integrated in ensemble)

2. **[src/models/hybrid_detector.py](../src/models/hybrid_detector.py)**
   - Updated attack labels to match new classification
   - Updated rule-based detection patterns
   - Modified decision fusion logic for BenignTraffic
   - Added threshold information to results

### Configuration Files Used

- `trained_models/retrained/training_config.json` - Model performance metrics
- `trained_models/retrained/feature_info.json` - Feature names and count
- `trained_models/retrained/class_mapping.json` - Label encoding
- `trained_models/retrained/optimal_threshold.json` - Detection threshold
- `trained_models/retrained/model_comparison.csv` - Model comparison metrics

## Backward Compatibility

### Breaking Changes
- Attack labels changed (e.g., `BENIGN` → `BenignTraffic`, `DoS Hulk` → `DoS-TCP_Flood`)
- Feature count reduced from 46 to 37
- Removed standalone anomaly detection

### Frontend Updates Needed
The frontend should be updated to handle new attack types:
- Update alert filtering for new attack names
- Update visualization categories
- Update severity mapping for new attack types

## Testing Recommendations

1. **Verify Model Loading**:
   ```python
   from src.models.predict import classify_ml, classify_dl
   # Test with sample data
   ```

2. **Check Feature Engineering**:
   - Ensure feature_engineer.py outputs all 37 required features
   - Verify feature order matches MODEL_FEATURE_NAMES

3. **Test Detection Pipeline**:
   - Run live monitoring with sample traffic
   - Verify alerts are generated correctly
   - Check false positive rate

4. **Performance Testing**:
   - Monitor memory usage (should be lower with fewer models)
   - Check inference speed
   - Verify model cache is working

## Rollback Instructions

If you need to rollback to old models:

1. Restore old model paths in `src/models/predict.py`:
   ```python
   ML_MODEL_PATH = Path('trained_models/final/final_xgb_optuna.pkl')
   DL_MODEL_PATH = Path('trained_models/dl_models/final_ffnn_residual.keras')
   # etc.
   ```

2. Restore old feature names (46 features)

3. Restore old attack labels in hybrid_detector.py

4. Restart the system

## Benefits

1. **Improved Accuracy**: Ensemble achieves 98.63% accuracy
2. **Reduced False Positives**: Optimized threshold (0.55) reduces false alarms
3. **Better Calibration**: Random Forest model is calibrated for better probability estimates
4. **Simplified Pipeline**: Single scaler, no separate anomaly detector
5. **Modern Attacks**: Covers wider range of contemporary attack types

## Notes

- The retrained models were trained on a larger dataset (9.3M samples)
- Models support 34 attack classes vs previous limited set
- Threshold tuning specifically optimized for production deployment
- Models include recent IoT and web attack patterns
