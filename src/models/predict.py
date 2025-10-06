from tensorflow.keras.models import load_model
import joblib
import numpy as np
from pathlib import Path
import pandas as pd

def detect_anormaly(features,
                    anomaly_path=Path('trained_models/dl_models/anomaly_autoencoder.keras'),
                    anomaly_scaler_path=Path('trained_models/dl_models/anormaly_scaler.joblib'),
                    threshold_path=Path('trained_models/dl_models/anomaly_threshold.npy')
                    ):
    
    '''Detects anomalies using autoencoder.'''

    autoencoder = load_model(anomaly_path)
    anomaly_scaler = joblib.load(anomaly_scaler_path)
    threshold = np.load(threshold_path)

    X = np.asarray(features)
    if X.ndim == 1:
        X = X.reshape(1, -1)
    
    # Convert to DataFrame with correct feature name to avoid warnings
    if hasattr(anomaly_scaler, "feature_names_in_"):
        X_df = pd.DataFrame(X, columns=anomaly_scaler.feature_names_in_)
    else:
        X_df = pd.DataFrame(X)

    X_scaled = anomaly_scaler.transform(X_df)

    reconstructions = autoencoder.predict(X_scaled)
    mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
    
    # Normalized MSE (relative to threshold)
    normalized_mse = np.clip(mse / threshold, 0, 2.0)
    confidence = np.clip(normalized_mse / 2.0, 0, 1.0)

    # Severity scaling
    if normalized_mse[0] < 0.9:
        severity = "low"
    elif 0.9 <= normalized_mse[0] < 1.5:
        severity = "medium"
    else:
        severity = "high"
    

    return{
        'mse_normalized': float(normalized_mse[0]),
        'confidence': float(confidence[0]),
        'threshold': threshold,
        'severity': severity
    }


def classify_attack(features, 
                   model_path=Path('trained_models/best_baseline.pkl'), 
                   scaler_path=Path('trained_models/scaler_standard.pkl'), 
                   encoder_path=Path('trained_models/encoder.pkl')):
    
    '''Classify attack type using trained classifier'''

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    encoder = joblib.load(encoder_path)

    X = np.asarray(features)
    if X.ndim == 1:
        X = X.reshape(1, -1)

    # Convert to DataFrame with correct feature names to avoid warnings
    if hasattr(scaler, "feature_names_in_"):
        X_df = pd.DataFrame(X, columns=scaler.feature_names_in_)
    else:
        X_df = pd.DataFrame(X)

    X_scaled = scaler.transform(X_df)
    
    # Make predictions
    model_pred = model.predict(X_scaled)
    
    
    # Determine class indices
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_scaled)
        class_index = np.argmax(proba, axis=1)
    elif isinstance(model_pred, np.ndarray) and model_pred.ndim > 1 and model_pred.shape[1] > 1:
        class_index = np.argmax(model_pred, axis=1)
    else:  
        class_index = (model_pred > 0.5).astype(int).ravel()

    # Decode class Label

    try:
        decoded_labels = encoder.inverse_transform(class_index)
    except Exception:
        decoded_labels = encoder.inverse_transform(class_index.reshape(-1, 1))

    predicted_label = decoded_labels[0] if len(decoded_labels) == 1 else decoded_labels
    severity = 'high' if predicted_label != 'BENIGN' else 'low'

    return predicted_label, severity 


def predict_threat(features):
    """returns a unified dictionary with attack predictions,
    severity and anomaly information"""

    anomaly_info = detect_anormaly(features)
    predicted_label, severity = classify_attack(features)

    return {
        'attack': predicted_label,
        'severity': severity,
        'anomaly': anomaly_info
    }

# quick usage example (single sample)
if __name__ == "__main__":
    final_input = np.array([[80.0, 1293792.0, 3.0, 7.0, 26.0, 11607.0, 20.0, 0.0, 8.666666667, 10.26320288,
        5840.0, 0.0, 1658.142857, 2137.29708, 8991.398927, 7.72921768, 143754.6667, 430865.8067,
        1292730.0, 2.0, 747.0, 373.5, 523.9661249, 744.0, 3.0, 1293746.0, 215624.3333, 527671.9348,
        1292730.0, 2.0, 0.0, 0.0, 0.0, 0.0, 72.0, 152.0, 2.318765304, 5.410452376, 0.0, 5840.0,
        1057.545455, 1853.437529, 3435230.673, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 2.0,
        1163.3, 8.666666667, 1658.142857, 72.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 26.0, 7.0,
        11607.0, 8192.0, 229.0, 2.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
    
    result = predict_threat(final_input)
    print(result)