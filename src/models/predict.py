import os
import gc
import json
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# Suppress TensorFlow messages BEFORE importing tensorflow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0=all, 1=no INFO, 2=no WARNING, 3=no INFO/WARNING/ERROR except Python
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN custom operations messages

from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K

# Import custom losses if required for model loading
from src.models.custom_losses import focal_loss_fixed, focal_loss

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- Load Feature Configuration from JSON ---
RETRAINED_DIR = Path('trained_models/retrained')
FEATURE_INFO_PATH = RETRAINED_DIR / 'feature_info.json'

def load_feature_info():
    """Loads feature names and count from the JSON file."""
    try:
        with open(FEATURE_INFO_PATH, 'r') as f:
            feature_info = json.load(f)
        feature_names = feature_info.get("feature_names", [])
        n_features = feature_info.get("n_features", len(feature_names))
        
        if n_features != len(feature_names):
            raise ValueError("Mismatch between 'n_features' and the actual number of feature names.")
            
        logger.info(f"Successfully loaded {n_features} features from {FEATURE_INFO_PATH}")
        return feature_names, n_features
    except Exception as e:
        logger.error(f"Failed to load or parse {FEATURE_INFO_PATH}: {e}")
        # Fallback to an empty list to prevent crashing, though this will likely cause downstream errors
        return [], 0

MODEL_FEATURE_NAMES, EXPECTED_FEATURES = load_feature_info()

# Verify that features were loaded successfully
if not MODEL_FEATURE_NAMES or EXPECTED_FEATURES == 0:
    logger.error("CRITICAL: Feature list could not be loaded. Predictions will fail.")
    # You might want to exit or handle this more gracefully depending on application requirements
    # For now, we'll let the assertion fail to make the problem obvious.

assert len(MODEL_FEATURE_NAMES) == EXPECTED_FEATURES, f"Feature count mismatch after loading: expected {EXPECTED_FEATURES}, got {len(MODEL_FEATURE_NAMES)}"

# Model paths - using retrained models only
DL_MODEL_PATH = RETRAINED_DIR / 'dl_model_retrained_fp_optimized.keras'
RF_MODEL_PATH = RETRAINED_DIR / 'random_forest_calibrated.pkl'
SCALER_PATH = RETRAINED_DIR / 'scaler_standard_retrained.pkl'
CLASS_MAPPING_PATH = RETRAINED_DIR / 'class_mapping.json'
OPTIMAL_THRESHOLD_PATH = RETRAINED_DIR / 'optimal_threshold.json'

# Ensemble configuration - rebalanced for better attack detection
ENSEMBLE_WEIGHTS = {
    'deep_learning': 0.6,  # Increased from 0.4
    'random_forest': 0.4   # Decreased from 0.6
}
OPTIMAL_THRESHOLD = 0.4  # Lowered from 0.55 for better detection

# Global model cache
_model_cache = {}


#Utility Functions

def get_cached_model(key, loader_fn):
    """Cache models or scalers to speed up repeated inference."""
    if key not in _model_cache:
        _model_cache[key] = loader_fn()
    return _model_cache[key]


def load_class_mapping():
    """Load class mapping from JSON file."""
    try:
        with open(CLASS_MAPPING_PATH, 'r') as f:
            mapping = json.load(f)
        # Convert string keys to integers
        return {int(k): v for k, v in mapping.items()}
    except Exception as e:
        logger.error(f"Failed to load class mapping: {e}")
        return {}


def clear_model_cache():
    """Clear cached models and release memory."""
    global _model_cache
    _model_cache.clear()
    K.clear_session()
    gc.collect()
    logger.info("Model cache and TensorFlow session cleared.")


def _validate_features(features, return_dataframe=False):
    """
    Ensure correct shape for model input and select required features.

    Args:
        features: Either DataFrame or numpy array with features
        return_dataframe: If True, return DataFrame instead of numpy array

    Returns:
        DataFrame or numpy array with exactly EXPECTED_FEATURES in correct order
    """
    # Convert DataFrame to select only required features
    if isinstance(features, pd.DataFrame):
        # Select only the features the model expects, in the correct order
        try:
            X_df = features[MODEL_FEATURE_NAMES]
        except KeyError as e:
            logger.error(f"Missing required features: {e}")
            # Fallback: use whatever features are available
            X_df = features
    else:
        X = np.asarray(features)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        # Convert to DataFrame with feature names
        X_df = pd.DataFrame(X, columns=MODEL_FEATURE_NAMES)

    if X_df.shape[1] != EXPECTED_FEATURES:
        raise ValueError(f"Expected {EXPECTED_FEATURES} features, got {X_df.shape[1]}")

    return X_df if return_dataframe else X_df.values



# Anomaly Detection (Removed - using ensemble only)
# The retrained models use ensemble-based detection instead of separate anomaly detection

def detect_anomaly(features):
    """
    Placeholder for anomaly detection - retrained models use ensemble approach.
    Returns neutral result for compatibility.
    """
    return {
        'is_anomaly': False,
        'mse_normalized': 0.0,
        'confidence': 0.0,
        'severity': 'low',
        'note': 'Using ensemble detection from retrained models'
    }



# Machine Learning Classifier (Random Forest)

def classify_ml(features):
    """Classify attack type using calibrated Random Forest model."""
    try:
        model = get_cached_model('rf_model', lambda: joblib.load(RF_MODEL_PATH))
        scaler = get_cached_model('scaler', lambda: joblib.load(SCALER_PATH))
        class_mapping = get_cached_model('class_mapping', load_class_mapping)

        X_df = _validate_features(features, return_dataframe=True)
        X_scaled = scaler.transform(X_df)

        # Get predictions
        preds = model.predict(X_scaled)
        proba = model.predict_proba(X_scaled)

        class_index = preds[0]
        confidence = float(np.max(proba[0]))

        # Decode label using class mapping
        label = class_mapping.get(class_index, 'Unknown')

        # Determine severity based on attack type
        if label == 'BenignTraffic':
            severity = 'low'
        elif any(x in label for x in ['DDoS', 'DoS', 'Flood']):
            severity = 'medium'
        elif any(x in label for x in ['Backdoor', 'Malware', 'Injection', 'Mirai']):
            severity = 'high'
        elif any(x in label for x in ['Recon', 'Scan', 'Discovery']):
            severity = 'medium'
        else:
            severity = 'high'

        return label, severity, confidence

    except Exception as e:
        logger.error(f"Random Forest classification failed: {e}")
        return 'BenignTraffic', 'low', 0.0



# Deep Learning Classifier (False Positive Optimized)

def classify_dl(features):
    """Classify attack type using retrained deep learning model optimized for false positive reduction."""
    try:
        model = get_cached_model('dl_model', lambda: load_model(DL_MODEL_PATH, custom_objects={
            'focal_loss_fixed': focal_loss_fixed,
            'focal_loss': focal_loss
        }))
        scaler = get_cached_model('scaler', lambda: joblib.load(SCALER_PATH))
        class_mapping = get_cached_model('class_mapping', load_class_mapping)

        X_df = _validate_features(features, return_dataframe=True)
        X_scaled = scaler.transform(X_df)

        # Get predictions
        predictions = model.predict(X_scaled, verbose=0)
        class_index = np.argmax(predictions, axis=1)[0]
        confidence = float(np.max(predictions[0]))

        # Decode label using class mapping
        label = class_mapping.get(class_index, 'Unknown')

        # Determine severity based on attack type
        if label == 'BenignTraffic':
            severity = 'low'
        elif any(x in label for x in ['DDoS', 'DoS', 'Flood']):
            severity = 'medium'
        elif any(x in label for x in ['Backdoor', 'Malware', 'Injection', 'Mirai']):
            severity = 'high'
        elif any(x in label for x in ['Recon', 'Scan', 'Discovery']):
            severity = 'medium'
        else:
            severity = 'high'

        return label, severity, confidence

    except Exception as e:
        logger.error(f"Deep learning classification failed: {e}")
        return 'BenignTraffic', 'low', 0.0


# Ensemble Combination Function
def combine_predictions(features):
    """
    Combine predictions from RF and DL models using weighted ensemble.
    """
    rf_label, rf_sev, rf_conf = classify_ml(features)
    dl_label, dl_sev, dl_conf = classify_dl(features)

    rf_weight = ENSEMBLE_WEIGHTS['random_forest']
    dl_weight = ENSEMBLE_WEIGHTS['deep_learning']

    weighted_conf = (rf_conf * rf_weight) + (dl_conf * dl_weight)

    if weighted_conf < OPTIMAL_THRESHOLD:
        final_label = 'BenignTraffic'
        final_sev = 'low'
        final_conf = weighted_conf
        method = 'ensemble:threshold_filtered'
    else:
        if rf_label == dl_label:
            final_label = rf_label
            final_sev = rf_sev if rf_conf > dl_conf else dl_sev
            final_conf = min(weighted_conf * 1.15, 1.0)
            method = 'ensemble:unanimous'
        else:
            if rf_conf * rf_weight > dl_conf * dl_weight:
                final_label, final_sev, final_conf = rf_label, rf_sev, rf_conf
                method = 'ensemble:random_forest'
            else:
                final_label, final_sev, final_conf = dl_label, dl_sev, dl_conf
                method = 'ensemble:deep_learning'

    return {
        'attack': final_label,
        'severity': final_sev,
        'confidence': float(final_conf),
        'method': method,
        'models': {
            'ml': {'attack': rf_label, 'severity': rf_sev, 'confidence': rf_conf},
            'dl': {'attack': dl_label, 'severity': dl_sev, 'confidence': dl_conf}
        }
    }

# Ensemble Threat Prediction
def predict_threat(features, use_ensemble=True):
    """
    Predict threat using ensemble combination function.
    """
    try:
        anomaly_info = detect_anomaly(features)

        if use_ensemble:
            ensemble_result = combine_predictions(features)
            return {
                **ensemble_result,
                'threshold': OPTIMAL_THRESHOLD,
                'anomaly': anomaly_info
            }
        else:
            rf_label, rf_sev, rf_conf = classify_ml(features)
            return {
                'attack': rf_label,
                'severity': rf_sev,
                'confidence': float(rf_conf),
                'method': 'random_forest_only',
                'threshold': OPTIMAL_THRESHOLD,
                'anomaly': anomaly_info,
                'models': {
                    'ml': {'attack': rf_label, 'severity': rf_sev, 'confidence': rf_conf},
                    'dl': {'attack': 'BenignTraffic', 'severity': 'low', 'confidence': 0.0}
                }
            }

    except Exception as e:
        logger.error(f"Threat prediction failed: {e}")
        return {
            'attack': 'BenignTraffic',
            'severity': 'unknown',
            'confidence': 0.0,
            'method': 'error',
            'error': str(e),
            'anomaly': {'is_anomaly': False, 'confidence': 0.0},
            'models': {
                'ml': {'attack': 'BenignTraffic', 'severity': 'low', 'confidence': 0.0},
                'dl': {'attack': 'BenignTraffic', 'severity': 'low', 'confidence': 0.0}
            }
        }


# Add diagnostic logging function
def add_diagnostic_logging():
    """Add detailed logging to investigate detection issues."""
    import logging
    logger = logging.getLogger(__name__)

    # Monkey patch combine_predictions to add logging
    original_combine_predictions = globals()['combine_predictions']

    def combine_predictions_with_logging(features):
        result = original_combine_predictions(features)

        # Log detailed prediction analysis
        rf_result = result['models']['ml']
        dl_result = result['models']['dl']
        final_result = result

        logger.info(f"ENSEMBLE ANALYSIS: RF={rf_result['attack']}(conf:{rf_result['confidence']:.3f}), "
                   f"DL={dl_result['attack']}(conf:{dl_result['confidence']:.3f}) -> "
                   f"FINAL={final_result['attack']}(conf:{final_result['confidence']:.3f}, method:{final_result['method']})")

        # Log threshold filtering logic
        weighted_conf = (rf_result['confidence'] * 0.6) + (dl_result['confidence'] * 0.4)
        threshold = OPTIMAL_THRESHOLD
        threshold_filter = weighted_conf < threshold

        if threshold_filter:
            logger.info(f"THRESHOLD FILTER: weighted_conf={weighted_conf:.3f} < threshold={threshold:.3f}, "
                       f"forcing BenignTraffic")
        else:
            logger.info(f"THRESHOLD PASS: weighted_conf={weighted_conf:.3f} >= threshold={threshold:.3f}")

        return result

    # Replace the function in global scope
    globals()['combine_predictions'] = combine_predictions_with_logging

    logger.info("Diagnostic logging enabled for ensemble predictions")
