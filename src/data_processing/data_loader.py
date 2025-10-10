import pandas as pd
from pathlib import Path

def load_data(file_path):
    """
    Load data from CSV or JSON file.
    """
    file_path = Path(file_path)
    if file_path.suffix == '.csv':
        return pd.read_csv(file_path)
    elif file_path.suffix == '.json':
        return pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file format. Use CSV or JSON.")

def load_cicids_data(data_dir='data'):
    """
    Load CICIDS2017 dataset.
    """
    data_dir = Path(data_dir)
    files = list(data_dir.glob('*.csv'))
    if not files:
        raise FileNotFoundError("No CSV files found in data directory.")
    # Load and concatenate all CSV files
    dfs = [pd.read_csv(f) for f in files]
    return pd.concat(dfs, ignore_index=True)
