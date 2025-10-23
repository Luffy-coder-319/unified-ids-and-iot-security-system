"""
Pure ML/DL Detection System using only machine learning and deep learning models.
"""
import pandas as pd
import numpy as np
import logging
from src.models.predict import predict_threat

logger = logging.getLogger(__name__)


def hybrid_predict_threat(features,
                         anomaly_threshold_multiplier=0.9,
                         rule_confidence_threshold=0.7,  
                         use_deep_learning=True,
                         ensemble_mode='confidence'):
    """
    Pure ML/DL threat detection using ensemble of machine learning and deep learning models.

    NO RULE-BASED DETECTION - relies entirely on trained models.

    Args:
        features: Feature array or DataFrame
        anomaly_threshold_multiplier: Threshold for anomaly detection (0.9 = 90% of threshold)
        rule_confidence_threshold: DEPRECATED - kept for API compatibility only
        use_deep_learning: Whether to use deep learning model (always enabled)
        ensemble_mode: 'confidence' or 'voting' - how to combine predictions
    Returns:
        dict with attack type, severity, confidence, and detection method
    """
    # Convert to DataFrame if needed
    if isinstance(features, np.ndarray):
        features_df = pd.DataFrame([features])
    elif isinstance(features, pd.DataFrame):
        features_df = features
    else:
        features_df = pd.DataFrame([features])

    # Get unified prediction from ensemble of ML and DL models
    prediction_result = predict_threat(features_df, use_ensemble=True)

    # Extract results from model ensemble
    attack_type = prediction_result['attack']
    severity = prediction_result['severity']
    confidence = prediction_result['confidence']
    detection_method = prediction_result['method']
    anomaly_info = prediction_result['anomaly']

    details = {
        'ml_prediction': prediction_result['models']['ml'],
        'dl_prediction': prediction_result['models']['dl'],
        'ensemble_method': prediction_result['method'],
        'threshold_applied': prediction_result.get('threshold', 0.55),
        'pure_ml_dl': True,  # Flag indicating no rule-based detection used
        'models_used': ['RandomForest', 'FFNN_Residual', 'Anomaly_Autoencoder']
    }

    # Check if anomaly was detected
    is_anomaly = anomaly_info.get('is_anomaly', False)

    # Determine final classification
    if attack_type not in ['BenignTraffic']:
        # Model detected a threat
        final_attack = attack_type
        final_severity = severity
        final_confidence = confidence
        final_method = detection_method
    else:
        final_attack = 'BenignTraffic'
        final_severity = 'low'
        final_confidence = confidence
        final_method = 'ensemble:BenignTraffic'

    return {
        'attack': final_attack,
        'severity': final_severity,
        'confidence': final_confidence,
        'detection_method': final_method,
        'anomaly': anomaly_info,
        'ml_prediction': prediction_result['models']['ml']['attack'],
        'ml_confidence': prediction_result['models']['ml']['confidence'],
        'dl_predictions': {'ffnn': prediction_result['models']['dl']},
        'rule_result': None, 
        'details': details
    }


def get_detection_explanation(result):
    """
    Generate human-readable explanation of detection result.
    Args:
        result: Output from hybrid_predict_threat()
    Returns:
        str: Explanation text
    """
    method = result['detection_method']
    attack = result['attack']
    confidence = result['confidence']

    if 'ensemble' in method:
        if attack == 'BenignTraffic':
            return f"ML/DL ensemble classified traffic as benign (confidence: {confidence:.1%})"
        else:
            ml_pred = result['ml_prediction']
            dl_pred = result['dl_predictions']['ffnn']['attack']
            return f"ML/DL ensemble detected {attack} (ML: {ml_pred}, DL: {dl_pred}, confidence: {confidence:.1%})"

    elif method == 'classifier':
        return f"ML classifier identified {attack} (severity: {result['severity']}, confidence: {confidence:.1%})"

    elif method == 'anomaly':
        mse = result['anomaly']['mse_normalized']
        return f"Anomaly detected with MSE {mse:.2f}x threshold (classified as {attack}, confidence: {confidence:.1%})"

    else:
        return f"Detected {attack} via {method} (confidence: {confidence:.1%})"
