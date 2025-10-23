# Database Storage for Network Flows - Complete Guide

This guide explains how to use the database system to store network flow features for model training, analysis, and retraining.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Database Schema](#database-schema)
5. [Data Export for Training](#data-export-for-training)
6. [API Integration](#api-integration)
7. [Maintenance](#maintenance)
8. [Advanced Usage](#advanced-usage)

---

## Overview

### What Gets Stored?

The system automatically stores:
- **All 46 extracted features** from CICIoT2023 format
- **Flow metadata**: Source/destination IPs, ports, protocol
- **Predictions**: Attack type, confidence, severity
- **Anomaly scores**: From autoencoder model
- **Timestamps**: For time-series analysis
- **Ground truth labels**: (optional) For supervised learning

### Why Use Database Storage?

1. **Model Retraining**: Collect real-world data to improve models
2. **Historical Analysis**: Track attack patterns over time
3. **False Positive Analysis**: Review and label false positives
4. **Dataset Generation**: Export balanced datasets for training
5. **Forensics**: Investigate security incidents

### Supported Databases

- **SQLite** (default): Local file-based, no setup required
- **PostgreSQL**: Production-ready, high performance, concurrent access

---

## Quick Start

### 1. Enable Database Storage

Edit [`config.yaml`](../config.yaml):

```yaml
database:
  enabled: true  # Enable database storage
  type: sqlite   # Use SQLite (default)
  directory: data/flows  # Database location
  retention_days: 30  # Keep data for 30 days
  save_benign_flows: true
  save_attack_flows: true
```

### 2. Start the System

```bash
# The database will be automatically created when you start monitoring
START_SYSTEM.bat

# Or start monitoring only
python start_live_monitoring.py
```

### 3. Verify Data Collection

Check the database file:
```bash
# Database location: data/flows/network_flows.sqlite
dir data\flows
```

### 4. Export Data for Training

```bash
# Export last 30 days of data
python -m src.database.export_utils train --output training_data.csv --days 30

# Export only attack samples
python -m src.database.export_utils train --output attacks_only.csv --no-benign --days 30

# Export with high confidence filter
python -m src.database.export_utils train --output high_conf.csv --min-confidence 0.9
```

---

## Configuration

### Basic Configuration

```yaml
database:
  enabled: true
  type: sqlite
  directory: data/flows
```

### SQLite Configuration (Recommended for Development)

```yaml
database:
  enabled: true
  type: sqlite
  directory: data/flows  # Creates network_flows.sqlite in this directory
  retention_days: 30
  save_benign_flows: true
  save_attack_flows: true
  min_confidence_to_save: 0.0  # Save all predictions
```

**Pros:**
- No setup required
- Fast for single-user
- Easy to backup (just copy the .sqlite file)

**Cons:**
- Not suitable for multiple concurrent writers
- Limited to local filesystem

### PostgreSQL Configuration (Recommended for Production)

```yaml
database:
  enabled: true
  type: postgresql
  url: postgresql://username:password@localhost:5432/network_flows
  retention_days: 90
  save_benign_flows: true
  save_attack_flows: true
```

**Setup PostgreSQL:**

```bash
# Install PostgreSQL
# Windows: Download from https://www.postgresql.org/download/windows/
# Linux: sudo apt-get install postgresql

# Create database
createdb network_flows

# Or using psql
psql -U postgres
CREATE DATABASE network_flows;
```

**Pros:**
- Production-ready
- Handles concurrent access
- Better performance for large datasets
- Advanced query capabilities

**Cons:**
- Requires PostgreSQL installation
- More complex setup

### Storage Options

```yaml
database:
  # Save all traffic or only attacks?
  save_benign_flows: true   # Recommended for training balanced models
  save_attack_flows: true

  # Filter low-confidence predictions
  min_confidence_to_save: 0.0  # 0.0 = save all, 0.8 = only save high confidence

  # Data retention
  retention_days: 30  # Auto-delete old data (0 = keep forever)
```

---

## Database Schema

### Tables

#### 1. `network_flows` (Main Table)

Stores all network flow features and predictions.

**Key Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `timestamp` | DateTime | When flow was captured |
| `src_ip` | String | Source IP address |
| `dst_ip` | String | Destination IP address |
| `src_port` | Integer | Source port |
| `dst_port` | Integer | Destination port |
| `protocol` | Integer | Protocol (6=TCP, 17=UDP, etc.) |

**Feature Columns (46 total):**
- `flow_duration`, `Header_Length`, `Protocol_Type`, `Duration`
- `Rate`, `Srate`, `Drate`
- `fin_flag_number`, `syn_flag_number`, `rst_flag_number`, etc.
- `HTTP`, `HTTPS`, `DNS`, `SSH`, `TCP`, `UDP`, etc.
- `Tot_sum`, `Min`, `Max`, `AVG`, `Std`, `Tot_size`
- `IAT`, `Number`, `Magnitue`, `Radius`, `Covariance`, `Variance`, `Weight`

**Prediction Columns:**
- `predicted_attack`: Attack type (e.g., "DDoS", "Port Scan")
- `predicted_severity`: low, medium, high
- `confidence`: Model confidence (0.0-1.0)
- `is_anomaly`: Boolean
- `anomaly_score`: Autoencoder reconstruction error

**Label Columns (for supervised learning):**
- `label`: Ground truth label (manual or verified)
- `label_verified`: Boolean

**Indexes:**
- `timestamp` + `predicted_attack`
- `src_ip` + `dst_ip`
- `is_anomaly` + `timestamp`
- `label`

#### 2. `model_training_metadata`

Tracks model training sessions and performance.

#### 3. `dataset_exports`

Records dataset exports for reproducibility.

---

## Data Export for Training

### Export Options

#### 1. Export for Model Training

```bash
# Basic export (last 30 days, all data)
python -m src.database.export_utils train --output training_data.csv

# Custom time range
python -m src.database.export_utils train --output data.csv --days 90

# Only attacks (no benign)
python -m src.database.export_utils train --output attacks.csv --no-benign

# Specific attack types
python -m src.database.export_utils train --output ddos_ssh.csv --attacks "DDoS" "SSH-Brute Force"

# High confidence only
python -m src.database.export_utils train --output high_conf.csv --min-confidence 0.95

# Custom database location
python -m src.database.export_utils train --output data.csv --db data/custom/mydb.sqlite
```

**Output Format:**

CSV file with:
- All 46 features
- Metadata (timestamp, IPs, ports)
- Predictions (attack, confidence, severity)
- Labels (if available)

#### 2. Export Balanced Samples

Export separate files for each attack type:

```bash
# Export 100+ samples per attack type
python -m src.database.export_utils samples --output-dir datasets/balanced

# Custom minimum samples
python -m src.database.export_utils samples --output-dir datasets --min-samples 500
```

**Output:**
- `datasets/balanced/ddos_samples.csv`
- `datasets/balanced/port_scan_samples.csv`
- `datasets/balanced/benign_samples.csv`
- etc.

#### 3. Export Labeled Data

Export only flows with ground truth labels:

```bash
# Export verified labels only
python -m src.database.export_utils labels --output labeled_data.csv

# Include unverified labels
python -m src.database.export_utils labels --output all_labels.csv --include-unverified
```

### Programmatic Export

Use in Python scripts:

```python
from src.database.db_manager import DatabaseManager
from datetime import datetime, timedelta

# Initialize database
db = DatabaseManager()

# Export to DataFrame
df = db.export_to_dataframe(
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now(),
    features_only=True  # Only 46 features
)

# Export to CSV with filters
count = db.export_to_csv(
    output_path='my_dataset.csv',
    attack_types=['DDoS', 'Port Scan'],
    include_benign=True,
    start_date=datetime.now() - timedelta(days=30)
)

print(f"Exported {count} flows")
```

---

## API Integration

### Python API

#### Basic Usage

```python
from src.database.db_manager import DatabaseManager
import pandas as pd

# Initialize (SQLite)
db = DatabaseManager()

# Or PostgreSQL
db = DatabaseManager(db_url="postgresql://user:pass@localhost/network_flows")
```

#### Save Flows

```python
# Save a flow with features
flow_id = db.save_flow(
    features_df=features_dataframe,  # 46 features
    src_ip="192.168.1.100",
    dst_ip="8.8.8.8",
    protocol=6,  # TCP
    src_port=54321,
    dst_port=443,
    prediction={
        'attack': 'DDoS',
        'severity': 'high',
        'confidence': 0.95,
        'method': 'ensemble',
        'anomaly': {'is_anomaly': True, 'mse_normalized': 1.5}
    }
)
```

#### Query Flows

```python
# Get recent flows
recent = db.get_recent_flows(limit=100, hours=24)

# Get flows by attack type
ddos_flows = db.get_flows_by_attack_type('DDoS', limit=1000)

# Get anomalies
anomalies = db.get_anomalies(limit=50, min_score=1.0, hours=24)

# Get statistics
stats = db.get_statistics(hours=24)
print(f"Total flows: {stats['total_flows']}")
print(f"Attacks: {stats['attack_flows']}")
print(f"Benign: {stats['benign_flows']}")
```

#### Update Labels

```python
# Add ground truth label for supervised learning
db.update_flow_label(flow_id=123, label='DDoS', verified=True)
```

---

## Maintenance

### Data Cleanup

#### Automatic Cleanup (Recommended)

Set in `config.yaml`:
```yaml
database:
  retention_days: 30  # Auto-delete flows older than 30 days
```

#### Manual Cleanup

```python
from src.database.db_manager import DatabaseManager

db = DatabaseManager()

# Delete flows older than 60 days
deleted_count = db.cleanup_old_flows(days=60)
print(f"Deleted {deleted_count} old flows")
```

### Database Backup

#### SQLite Backup

```bash
# Simple copy
copy data\flows\network_flows.sqlite data\backups\backup_2025-01-15.sqlite

# With compression
tar -czf flows_backup.tar.gz data/flows/
```

#### PostgreSQL Backup

```bash
# Dump database
pg_dump network_flows > network_flows_backup.sql

# Restore
psql network_flows < network_flows_backup.sql
```

### Monitor Database Size

```python
from pathlib import Path

db_file = Path("data/flows/network_flows.sqlite")
size_mb = db_file.stat().st_size / (1024 * 1024)
print(f"Database size: {size_mb:.2f} MB")
```

---

## Advanced Usage

### Custom Queries

```python
from src.database.db_manager import DatabaseManager
from src.database.models import NetworkFlow
from sqlalchemy import and_, or_

db = DatabaseManager()

with db.get_session() as session:
    # Complex query: High confidence attacks in last hour
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(hours=1)

    flows = session.query(NetworkFlow)\
        .filter(NetworkFlow.timestamp >= cutoff)\
        .filter(NetworkFlow.predicted_attack != 'BENIGN')\
        .filter(NetworkFlow.confidence >= 0.9)\
        .all()

    for flow in flows:
        print(f"{flow.src_ip} -> {flow.dst_ip}: {flow.predicted_attack}")
```

### Integrate with Notebooks

```python
# In Jupyter notebook
from src.database.db_manager import DatabaseManager

db = DatabaseManager()

# Load data for analysis
df = db.export_to_dataframe(features_only=False)

# Now use with scikit-learn, matplotlib, etc.
import matplotlib.pyplot as plt
df['predicted_attack'].value_counts().plot(kind='bar')
plt.title('Attack Distribution')
plt.show()
```

### Model Retraining Pipeline

```python
from src.database.db_manager import DatabaseManager
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Export data
db = DatabaseManager()
df = db.export_to_dataframe()

# 2. Prepare features and labels
X = df[feature_columns]  # 37 or 46 features
y = df['label']  # Use ground truth labels

# 3. Train new model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier()
model.fit(X_train, y_train)

# 4. Save updated model
joblib.dump(model, 'trained_models/retrained_model.pkl')

# 5. Evaluate
accuracy = model.score(X_test, y_test)
print(f"Retrained model accuracy: {accuracy:.2%}")
```

---

## Troubleshooting

### Database Not Creating

**Check:**
1. `config.yaml` has `database.enabled: true`
2. Directory exists: `data/flows/`
3. Write permissions on directory

**Solution:**
```bash
mkdir data\flows
```

### SQLAlchemy Not Installed

```bash
# Install from requirements.txt
myvenv\Scripts\pip install -r requirements.txt

# Or install directly
myvenv\Scripts\pip install sqlalchemy>=2.0.0
```

### Database Locked (SQLite)

**Cause:** Multiple processes trying to write simultaneously

**Solutions:**
1. Use PostgreSQL for concurrent access
2. Reduce write frequency
3. Check for hanging connections

### Export Returns Empty Data

**Check:**
1. Database has data: `dir data\flows\network_flows.sqlite`
2. Date range is correct
3. Filters are not too restrictive

**Debug:**
```python
db = DatabaseManager()
stats = db.get_statistics(hours=720)  # Last 30 days
print(stats)
```

---

## Performance Tips

### For Large Datasets (>1M flows)

1. **Use PostgreSQL** instead of SQLite
2. **Reduce retention period**: Keep only recent data
3. **Filter exports**: Export subsets instead of full database
4. **Batch operations**: Save flows in batches

### Optimize Storage

```yaml
database:
  save_benign_flows: false  # Only save attacks (reduces size by ~90%)
  min_confidence_to_save: 0.8  # Filter low-confidence predictions
  retention_days: 7  # Keep only 1 week
```

### Export Performance

```python
# Use features_only for faster exports
df = db.export_to_dataframe(features_only=True)

# Limit date range
df = db.export_to_dataframe(
    start_date=datetime.now() - timedelta(days=7)
)
```

---

## Integration Examples

### Example 1: Daily Model Retraining

```python
# scripts/retrain_daily.py
from src.database.db_manager import DatabaseManager
from datetime import datetime, timedelta

# Export yesterday's data
db = DatabaseManager()
yesterday = datetime.now() - timedelta(days=1)
today = datetime.now()

db.export_to_csv(
    output_path=f'training_data_{yesterday.strftime("%Y%m%d")}.csv',
    start_date=yesterday,
    end_date=today
)

# Run model training
# ... (your training code)
```

### Example 2: False Positive Analysis

```python
# Get low-severity predictions that were actually benign
with db.get_session() as session:
    false_positives = session.query(NetworkFlow)\
        .filter(NetworkFlow.predicted_attack != 'BENIGN')\
        .filter(NetworkFlow.label == 'BENIGN')\
        .filter(NetworkFlow.label_verified == True)\
        .all()

    print(f"Found {len(false_positives)} false positives")
    for fp in false_positives[:10]:
        print(f"  {fp.src_ip} -> {fp.dst_ip}: {fp.predicted_attack}")
```

### Example 3: Real-time Monitoring Dashboard

```python
# Add to FastAPI endpoints
from fastapi import APIRouter
from src.database.db_manager import DatabaseManager

router = APIRouter()
db = DatabaseManager()

@router.get("/api/flows/recent")
def get_recent_flows():
    flows = db.get_recent_flows(limit=50, hours=1)
    return [flow.to_dict() for flow in flows]

@router.get("/api/stats")
def get_stats():
    return db.get_statistics(hours=24)
```

---

## References

- Database Models: [src/database/models.py](../src/database/models.py)
- Database Manager: [src/database/db_manager.py](../src/database/db_manager.py)
- Export Utilities: [src/database/export_utils.py](../src/database/export_utils.py)
- Configuration: [config.yaml](../config.yaml)
- Feature Verification: [FEATURE_VERIFICATION.md](FEATURE_VERIFICATION.md)

---

## Next Steps

1. **Enable database** in `config.yaml`
2. **Start monitoring** and let data collect
3. **Export data** after a few days
4. **Retrain models** with real-world data
5. **Improve accuracy** iteratively

For questions or issues, refer to the main [README.md](../README.md) or check the documentation.
