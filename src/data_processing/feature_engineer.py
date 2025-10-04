import pandas as pd

def engineer_features(df):
    '''Select and engineer key features from CICIDS2017 (78 total, select top for efficiency).'''
    # List of key features from dataset (based on analysis)
    key_features = [
        'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
        'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std',
        'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std',
        'Flow Bytes/s', 'Flow Packets/s', 'PSH Flag Count', 'ACK Flag Count', 'URG Flag Count',
        'Avg Packet Size', 'Fwd Header Length', 'Bwd Header Length', 'Down/Up Ratio'
        # Add more as needed, up to 78
    ]

    # Engineer new if needed, e.g., ratios
    if 'Flow Bytes/s' not in df.columns:
        df['Flow Bytes/s'] = (df['Total Length of Fwd Packets'] + df['Total Length of Bwd Packets']) / df['Flow Duration']
        
    return df[key_features]