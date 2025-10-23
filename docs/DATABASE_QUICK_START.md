# Database Quick Start Guide

Get started with database flow storage in 5 minutes.

---

## Step 1: Enable Database (30 seconds)

Edit [`config.yaml`](../config.yaml):

```yaml
database:
  enabled: true  # Change to true
  type: sqlite
  directory: data/flows
```

## Step 2: Install Requirements (if needed)

```bash
myvenv\Scripts\pip install sqlalchemy
```

Or reinstall all requirements:

```bash
myvenv\Scripts\pip install -r requirements.txt
```

## Step 3: Start Monitoring

```bash
START_SYSTEM.bat
```

The database will be automatically created at:
```
data\flows\network_flows.sqlite
```

## Step 4: Let Data Collect

**Recommendation:** Let the system run for at least 24 hours to collect meaningful data.

- Generates normal traffic by browsing websites
- System automatically captures and stores flows
- Both benign and attack traffic are stored

## Step 5: Export Data

### Option A: Use the Export Script (Easy)

```bash
scripts\export_data.bat
```

Choose from:
1. Export for training (last 30 days)
2. Export attacks only
3. Export labeled data
4. Export balanced samples

### Option B: Command Line (Flexible)

```bash
# Export last 30 days
python -m src.database.export_utils train --output training_data.csv --days 30

# Export attacks only
python -m src.database.export_utils train --output attacks.csv --no-benign

# Export high confidence only
python -m src.database.export_utils train --output high_conf.csv --min-confidence 0.95
```

## What You Get

The exported CSV contains:

- **46 features** (CICIoT2023 format)
- **Flow metadata**: IPs, ports, timestamps
- **Predictions**: Attack type, confidence, severity
- **Anomaly scores**: From autoencoder
- **Labels**: Ground truth (if added)

Perfect for:
- Model retraining
- Dataset augmentation
- Performance analysis
- False positive investigation

---

## Quick Examples

### View Statistics

```python
from src.database.db_manager import DatabaseManager

db = DatabaseManager()
stats = db.get_statistics(hours=24)

print(f"Total flows: {stats['total_flows']}")
print(f"Attacks: {stats['attack_flows']}")
print(f"Benign: {stats['benign_flows']}")
```

### Export to DataFrame

```python
from src.database.db_manager import DatabaseManager

db = DatabaseManager()
df = db.export_to_dataframe(features_only=True)

print(df.shape)  # (num_flows, 46)
print(df.columns)  # All 46 feature names
```

### Query Recent Attacks

```python
from src.database.db_manager import DatabaseManager

db = DatabaseManager()
attacks = db.get_flows_by_attack_type('DDoS', limit=100)

for flow in attacks:
    print(f"{flow.src_ip} -> {flow.dst_ip}: {flow.confidence:.2%}")
```

---

## Configuration Options

### Minimal (Default)

```yaml
database:
  enabled: true
```

### Recommended for Development

```yaml
database:
  enabled: true
  type: sqlite
  directory: data/flows
  retention_days: 30  # Auto-delete old data
  save_benign_flows: true
  save_attack_flows: true
```

### Space-Saving Configuration

```yaml
database:
  enabled: true
  type: sqlite
  directory: data/flows
  retention_days: 7  # Keep only 1 week
  save_benign_flows: false  # Only save attacks
  min_confidence_to_save: 0.8  # Filter low confidence
```

---

## Troubleshooting

### Database Not Creating

Check:
1. `config.yaml` has `enabled: true`
2. `sqlalchemy` is installed
3. Directory exists: `mkdir data\flows`

### No Data Exported

Check:
1. System has been running (data collected)
2. Date range is correct (`--days 30`)
3. Check database: `dir data\flows\network_flows.sqlite`

### Import Error

```bash
# Install SQLAlchemy
myvenv\Scripts\pip install sqlalchemy>=2.0.0
```

---

## Next Steps

1. ✓ Enable database
2. ✓ Start monitoring
3. ✓ Let data collect (24+ hours)
4. ✓ Export data
5. **→ Train/retrain models** (see notebooks)
6. **→ Improve detection accuracy**

---

## Full Documentation

See [DATABASE_GUIDE.md](DATABASE_GUIDE.md) for:
- Complete API reference
- Advanced queries
- PostgreSQL setup
- Model retraining pipeline
- Performance optimization
- Integration examples

---

## Support

- Check [DATABASE_GUIDE.md](DATABASE_GUIDE.md) for detailed docs
- See [FEATURE_VERIFICATION.md](FEATURE_VERIFICATION.md) for feature info
- Read main [README.md](../README.md) for system overview
