# Model Configuration Guide

This directory contains configuration files for the Unified IDS and IoT Security System.

## model_config.json

Main configuration file for the integrated detection system.

### Key Sections:

#### 1. Ensemble Configuration
```json
"ensemble": {
  "mode": "weighted_voting",
  "confidence_threshold": 0.6
}
```

**Ensemble Modes:**
- `weighted_voting`: Models vote based on assigned weights and performance
- `confidence`: Use prediction from model with highest confidence
- `voting`: Simple majority voting (one vote per model)

#### 2. Model Configuration

Each model has:
- `enabled`: Whether to use this model
- `path`: Path to trained model file
- `weight`: Voting weight (higher = more influence)
- `scaler_path`/`encoder_path`: Preprocessing artifacts

**Available Models:**
1. **ml_classifier**: Traditional ML (XGBoost/LightGBM) - Fast, accurate
2. **dl_ffnn**: Deep Learning FFNN with Residual Connections - High accuracy
3. **dl_cnn**: Deep Learning CNN - Pattern recognition
4. **anomaly_detector**: Autoencoder for anomaly detection - Unknown threats

#### 3. Detection Thresholds

```json
"thresholds": {
  "anomaly_threshold_multiplier": 2.5,
  "rule_confidence_threshold": 0.7,
  "high_severity_confidence": 0.8,
  "medium_severity_confidence": 0.6
}
```

- `anomaly_threshold_multiplier`: MSE must exceed this × training threshold
- `rule_confidence_threshold`: Minimum confidence for rule-based detection
- Severity thresholds: Classify threat severity based on confidence

#### 4. Detection Methods

```json
"detection": {
  "use_deep_learning": true,
  "use_rule_based": true,
  "use_anomaly_detection": true
}
```

Enable/disable specific detection approaches.

#### 5. Performance Monitoring

```json
"performance": {
  "enable_monitoring": true,
  "enable_adaptive_weights": true,
  "min_samples_for_adaptation": 10
}
```

- `enable_monitoring`: Track model accuracy over time
- `enable_adaptive_weights`: Automatically adjust weights based on performance
- `min_samples_for_adaptation`: Minimum predictions before adjusting weights

## Usage Example

```python
from src.utils.config_loader import load_config
from src.models.hybrid_detector import hybrid_predict_threat

# Load configuration
config = load_config('config/model_config.json')

# Use in detection
result = hybrid_predict_threat(
    features,
    anomaly_threshold_multiplier=config['thresholds']['anomaly_threshold_multiplier'],
    rule_confidence_threshold=config['thresholds']['rule_confidence_threshold'],
    use_deep_learning=config['detection']['use_deep_learning']
)
```

## Tuning Guide

### For Higher Accuracy (More False Positives)
- Decrease `anomaly_threshold_multiplier` from 2.5 to 1.5
- Decrease `rule_confidence_threshold` from 0.7 to 0.5
- Increase DL model weights to 1.5

### For Fewer False Positives (May Miss Some Attacks)
- Increase `anomaly_threshold_multiplier` from 2.5 to 3.5
- Increase `rule_confidence_threshold` from 0.7 to 0.85
- Increase `confidence_threshold` to 0.75

### For Faster Detection (Less Accurate)
- Disable deep learning models: `"enabled": false` for dl_ffnn and dl_cnn
- Use only ml_classifier and rule_based detection
- Set `ensemble_mode` to "confidence"

### For Maximum Accuracy (Slower)
- Enable all models
- Use `weighted_voting` mode
- Enable `adaptive_weights`
- Lower confidence thresholds to catch more attacks

## Model Paths

All paths are relative to the project root directory:
```
unified-ids-and-iot-security-system/
├── trained_models/
│   ├── best_baseline.pkl          # ML classifier
│   ├── scaler_standard.pkl         # Feature scaler
│   ├── encoder.pkl                 # Label encoder
│   └── dl_models/
│       ├── final_ffnn_residual.keras
│       ├── final_cnn_stable.keras
│       ├── anomaly_autoencoder.keras
│       ├── anormaly_scaler.joblib
│       └── anomaly_threshold.npy
```

## Troubleshooting

**Models not loading:**
- Check file paths are correct
- Ensure models were trained and saved
- Check TensorFlow/Keras version compatibility

**Poor detection accuracy:**
- Review thresholds in `thresholds` section
- Enable adaptive weights
- Check model paths point to best-performing models

**High false positive rate:**
- Increase `anomaly_threshold_multiplier`
- Increase `rule_confidence_threshold`
- Adjust model weights (lower anomaly detector weight)

**Slow performance:**
- Disable deep learning models for faster inference
- Use `confidence` mode instead of `weighted_voting`
- Increase confidence threshold to reduce processing
