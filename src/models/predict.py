from tensorflow.keras.models import load_model
import joblib
import numpy as np
from pathlib import Path

current_dir = Path.cwd()
def predict_threat(features, model_path=current_dir/".."/"trained_models"/"best_baseline.pkl", anomaly_path=current_dir/'../trained_models/best_baseline.pkl', scaler_path=current_dir/'../trained_models/scaler_standard.pkl', encoder_path=current_dir/'../trained_models/encoder.pkl'):
    model = joblib(model_path)
    iso_forest = joblib.load(anomaly_path)
    scaler = joblib.load(scaler_path)
    encoder = joblib.load(encoder_path)

    features_scaled = scaler.transform(features)
    anomly_score = iso_forest.decision_function(features_scaled)

    if anomly_score < 0:
        return "Anomaly", "medium"
    
    pred = model.predict(features_scaled)
    label = encoder.inverse_transform(np.argmax(pred, axis=1))[0]
    severity = 'high' if label != 'BENIGN' else 'low'

    print("Everything loaded successfully and the directory exists")

    return label, severity, print("Everything loaded successfully and the directory exists")


# Example input
 #DDOS Attack
final_input = np.array([[80.0, 1293792.0, 3.0, 7.0, 26.0, 11607.0, 20.0, 0.0, 8.666666667, 10.26320288,
    5840.0, 0.0, 1658.142857, 2137.29708, 8991.398927, 7.72921768, 143754.6667, 430865.8067,
    1292730.0, 2.0, 747.0, 373.5, 523.9661249, 744.0, 3.0, 1293746.0, 215624.3333, 527671.9348,
    1292730.0, 2.0, 0.0, 0.0, 0.0, 0.0, 72.0, 152.0, 2.318765304, 5.410452376, 0.0, 5840.0,
    1057.545455, 1853.437529, 3435230.673, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 2.0,
    1163.3, 8.666666667, 1658.142857, 72.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 26.0, 7.0,
    11607.0, 8192.0, 229.0, 2.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])


predict_threat(final_input)