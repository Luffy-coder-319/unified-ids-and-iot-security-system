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
