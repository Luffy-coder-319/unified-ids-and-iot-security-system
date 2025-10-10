import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer

def preprocess_data(df, target_column='Label'):
    """
    Preprocess the dataset: handle missing values, encode labels, scale features.
    """
    # Separate features and target
    X = df.drop(target_column, axis=1)
    y = df[target_column]

    # Handle missing values
    imputer = SimpleImputer(strategy='mean')
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

    # Encode target if categorical
    if y.dtype == 'object':
        encoder = LabelEncoder()
        y_encoded = encoder.fit_transform(y)
        return X_imputed, y_encoded, encoder
    else:
        return X_imputed, y, None

def scale_features(X_train, X_test=None):
    """
    Scale features using StandardScaler.
    """
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    if X_test is not None:
        X_test_scaled = scaler.transform(X_test)
        return X_train_scaled, X_test_scaled, scaler
    return X_train_scaled, scaler
