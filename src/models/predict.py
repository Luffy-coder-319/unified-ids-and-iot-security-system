import os
import gc
import json
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import threading

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

# Clipping configuration (short-term mitigation for extreme z-scores)
CLIP_ENABLED = os.getenv('PREDICTION_CLIP_ENABLED', '1') == '1'
try:
    CLIP_Z = float(os.getenv('PREDICTION_CLIP_Z', '5.0'))
except Exception:
    CLIP_Z = 5.0

# Global model cache
_model_cache = {}
_model_cache_lock = threading.Lock()


#Utility Functions

def get_cached_model(key, loader_fn):
    """Thread-safe cache models or scalers to speed up repeated inference."""
    # Double-checked locking to avoid multiple loads
    if key not in _model_cache:
        with _model_cache_lock:
            if key not in _model_cache:
                _model_cache[key] = loader_fn()
    return _model_cache[key]


def runtime_sanity_check(verbose: bool = True) -> bool:
    """
    Perform quick runtime sanity checks:
      - required files (feature_info, scaler, models) exist
      - feature list in feature_info.json matches the feature engineer's list

    Returns True if checks pass, False otherwise.
    """
    issues = []
    paths = {
        'feature_info': FEATURE_INFO_PATH,
        'scaler': SCALER_PATH,
        'dl_model': DL_MODEL_PATH,
        'rf_model': RF_MODEL_PATH,
    }

    for name, p in paths.items():
        try:
            if not p.exists():
                issues.append(f"Missing {name}: {p}")
        except Exception as e:
            issues.append(f"Error checking {name} at {p}: {e}")

    # Compare feature list with feature_engineer
    try:
        from src.data_processing.feature_engineer import get_feature_names as _fe_get
        fe_names = _fe_get()
        # Load model feature info if available
        model_feats = []
        if FEATURE_INFO_PATH.exists():
            with open(FEATURE_INFO_PATH, 'r') as f:
                fi = json.load(f)
                model_feats = fi.get('feature_names', [])

        if model_feats and fe_names and model_feats != fe_names:
            issues.append("Feature name/order mismatch between feature_info.json and feature_engineer.get_feature_names()")
    except Exception as e:
        issues.append(f"Failed to compare feature lists: {e}")

    if issues:
        if verbose:
            logger.warning("Runtime sanity check found issues:")
            for it in issues:
                logger.warning("  - %s", it)
            logger.warning("Proceeding in degraded/simulation mode. Fix the issues to enable full live inference.")
        return False

    if verbose:
        logger.info("Runtime sanity check passed: feature info, scaler, and model files appear present and consistent.")
    return True


def _scale_and_clip(X_df):
    """Scale DataFrame with the configured scaler and apply clipping to z-scores.

    Returns a numpy array (scaled). Raises if scaler cannot be loaded.
    """
    scaler = get_cached_model('scaler', lambda: joblib.load(SCALER_PATH))
    X_scaled = scaler.transform(X_df)
    if CLIP_ENABLED:
        # Count clipped entries for logging
        clipped = np.abs(X_scaled) > CLIP_Z
        n_clipped = int(np.sum(clipped))
        if n_clipped > 0:
            logger.info(f"Applied z-score clipping: {n_clipped} values clipped to +/-{CLIP_Z}")
        X_scaled = np.clip(X_scaled, -CLIP_Z, CLIP_Z)
    return X_scaled


def eager_load_models(verbose: bool = True) -> bool:
    """
    Eagerly load scaler and models into the cache. Returns True if loads succeed.
    """
    success = True
    try:
        # Load scaler
        get_cached_model('scaler', lambda: joblib.load(SCALER_PATH))
    except Exception as e:
        success = False
        logger.error(f"Eager load failed for scaler: {e}")

    try:
        # Load RF
        get_cached_model('rf_model', lambda: joblib.load(RF_MODEL_PATH))
    except Exception as e:
        success = False
        logger.error(f"Eager load failed for RF model: {e}")

    try:
        # Load DL model
        get_cached_model('dl_model', lambda: load_model(DL_MODEL_PATH, custom_objects={'focal_loss_fixed': focal_loss_fixed, 'focal_loss': focal_loss}))
    except Exception as e:
        success = False
        logger.error(f"Eager load failed for DL model: {e}")

    if verbose:
        if success:
            logger.info("Eager model loading succeeded")
        else:
            logger.warning("Eager model loading encountered errors; see logs")
    return success


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description='Model predict utilities')
    p.add_argument('--sanity-check', action='store_true', help='Run runtime sanity checks')
    p.add_argument('--eager-load', action='store_true', help='Eagerly load models into cache')
    args = p.parse_args()

    if args.sanity_check:
        ok = runtime_sanity_check(verbose=True)
        raise SystemExit(0 if ok else 2)

    if args.eager_load:
        ok = eager_load_models(verbose=True)
        raise SystemExit(0 if ok else 3)


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
        class_mapping = get_cached_model('class_mapping', load_class_mapping)

        X_df = _validate_features(features, return_dataframe=True)
        X_scaled = _scale_and_clip(X_df)

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
        class_mapping = get_cached_model('class_mapping', load_class_mapping)

        X_df = _validate_features(features, return_dataframe=True)
        X_scaled = _scale_and_clip(X_df)

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


def diagnose_prediction(features):
    """
    Run a detailed diagnostic for a single feature vector or DataFrame row.

    Returns a dictionary with:
      - raw_features: original feature values (dict)
      - scaled_features: values after scaler.transform (list)
      - rf: {label, confidence, proba}
      - dl: {label, confidence, proba}
      - weighted_confidence: combined weighted confidence
      - threshold: OPTIMAL_THRESHOLD
      - threshold_pass: bool whether weighted_conf >= threshold
      - ensemble: result of combine_predictions (full dict)

    The function is defensive: if a model or scaler cannot be loaded it will include
    an "error" field for that model and still return any available information.
    """
    result = {
        'raw_features': None,
        'scaled_features': None,
        'rf': None,
        'dl': None,
        'weighted_confidence': None,
        'threshold': OPTIMAL_THRESHOLD,
        'threshold_pass': None,
        'ensemble': None,
        'errors': []
    }

    try:
        X_df = _validate_features(features, return_dataframe=True)
    except Exception as e:
        result['errors'].append(f"feature_validation_failed: {e}")
        return result

    # Record raw features
    try:
        result['raw_features'] = X_df.iloc[0].to_dict()
    except Exception:
        result['errors'].append('failed_to_serialize_raw_features')

    # Attempt to scale
    scaler = None
    try:
        X_scaled = _scale_and_clip(X_df)
        result['scaled_features'] = X_scaled[0].astype(float).tolist()
    except Exception as e:
        result['errors'].append(f'scaler_error: {e}')
        X_scaled = None

    # Random Forest prediction
    try:
        rf = get_cached_model('rf_model', lambda: joblib.load(RF_MODEL_PATH))
        if X_scaled is None:
            # Try to transform without scaler (not recommended)
            try:
                X_scaled = X_df.values
            except Exception:
                X_scaled = None

        if X_scaled is not None:
            rf_preds = rf.predict(X_scaled)
            rf_proba = rf.predict_proba(X_scaled)[0].astype(float).tolist()
            rf_label = get_cached_model('class_mapping', load_class_mapping).get(int(rf_preds[0]), 'Unknown')
            rf_conf = float(max(rf_proba))
            result['rf'] = {'label': rf_label, 'confidence': rf_conf, 'proba': rf_proba}
        else:
            result['rf'] = {'error': 'no_scaled_features'}
    except Exception as e:
        result['rf'] = {'error': str(e)}
        result['errors'].append(f'rf_error: {e}')

    # Deep Learning prediction
    try:
        dl = get_cached_model('dl_model', lambda: load_model(DL_MODEL_PATH, custom_objects={'focal_loss_fixed': focal_loss_fixed, 'focal_loss': focal_loss}))
        if X_scaled is None:
            try:
                X_scaled = X_df.values
            except Exception:
                X_scaled = None

        if X_scaled is not None:
            dl_preds = dl.predict(X_scaled, verbose=0)
            dl_proba = dl_preds[0].astype(float).tolist()
            dl_index = int(np.argmax(dl_preds, axis=1)[0])
            dl_label = get_cached_model('class_mapping', load_class_mapping).get(dl_index, 'Unknown')
            dl_conf = float(max(dl_proba))
            result['dl'] = {'label': dl_label, 'confidence': dl_conf, 'proba': dl_proba}
        else:
            result['dl'] = {'error': 'no_scaled_features'}
    except Exception as e:
        result['dl'] = {'error': str(e)}
        result['errors'].append(f'dl_error: {e}')

    # Compute weighted confidence if both model confidences available
    try:
        rf_conf = result['rf'].get('confidence') if isinstance(result.get('rf'), dict) else None
        dl_conf = result['dl'].get('confidence') if isinstance(result.get('dl'), dict) else None
        if rf_conf is not None and dl_conf is not None:
            weighted_conf = (rf_conf * ENSEMBLE_WEIGHTS.get('random_forest', 0.5)) + (dl_conf * ENSEMBLE_WEIGHTS.get('deep_learning', 0.5))
            result['weighted_confidence'] = float(weighted_conf)
            result['threshold_pass'] = weighted_conf >= OPTIMAL_THRESHOLD
        else:
            result['weighted_confidence'] = None
            result['threshold_pass'] = None
    except Exception as e:
        result['errors'].append(f'weighted_conf_error: {e}')

    # Full ensemble decision (may already load models but is useful for consistency)
    try:
        ensemble = combine_predictions(features)
        result['ensemble'] = ensemble
    except Exception as e:
        result['errors'].append(f'ensemble_error: {e}')

    return result
