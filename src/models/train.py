import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os
from pathlib import Path

def train_model(data_path='data/cicids2017.csv', model_dir='trained_models'):
    """
    Train a basic RandomForest classifier on CICIDS2017 data.
    """
    os.makedirs(model_dir, exist_ok=True)

    # Load data
    df = pd.read_csv(data_path)

    # Assume 'Label' is the target column
    X = df.drop('Label', axis=1)
    y = df['Label']

    # Encode labels
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    # Scale features
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train_scaled = pd.DataFrame(scaler.transform(X_train), columns=X_train.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Save model and artifacts
    joblib.dump(model, Path(model_dir) / 'best_baseline.pkl')
    joblib.dump(scaler, Path(model_dir) / 'scaler_standard.pkl')
    joblib.dump(encoder, Path(model_dir) / 'encoder.pkl')

    print("Model trained and saved.")

if __name__ == "__main__":
    train_model()
