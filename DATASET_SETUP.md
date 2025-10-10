# CIC-IoT-2023 Dataset Setup Guide

Quick guide to download and prepare the CIC-IoT-2023 dataset for training.

---

## 📥 Option 1: Direct Download (Recommended)

```bash
# Navigate to project root
cd /mnt/d/project/unified-ids-and-iot-security-system

# Create directory structure
mkdir -p data/raw/CICIoT2023/CSV

# Download CSV files
cd data/raw/CICIoT2023
wget -r -np -nH --cut-dirs=3 -A "*.csv" http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/CSV/

# Verify download
cd CSV
ls -lh *.csv | wc -l  # Should output: 169
```

**Download Size:** ~2.7 GB compressed, ~13 GB uncompressed

---

## 📥 Option 2: Kaggle Download

```bash
# Install Kaggle CLI
pip install kaggle

# Configure Kaggle API (one-time setup)
# 1. Go to https://www.kaggle.com/settings
# 2. Click "Create New API Token"
# 3. Save kaggle.json to ~/.kaggle/

# Download dataset
cd /mnt/d/project/unified-ids-and-iot-security-system/data/raw
kaggle datasets download -d madhavmalhotra/unb-cic-iot-dataset

# Extract
unzip unb-cic-iot-dataset.zip -d CICIoT2023/CSV/
```

---

## ✅ Verify Setup

```bash
# Check file count
cd /mnt/d/project/unified-ids-and-iot-security-system
ls data/raw/CICIoT2023/CSV/*.csv | wc -l
# Expected output: 169

# Check total size
du -sh data/raw/CICIoT2023/CSV/
# Expected output: ~13G

# List sample files
ls data/raw/CICIoT2023/CSV/ | head -10
```

**Expected Files:**
```
DDoS-ACK_Fragmentation.csv
DDoS-HTTP_Flood.csv
DDoS-ICMP_Flood.csv
DDoS-SlowLoris.csv
DDoS-SYN_Flood.csv
DDoS-UDP_Flood.csv
DoS-HTTP_Flood.csv
DoS-SYN_Flood.csv
DoS-TCP_Flood.csv
DoS-UDP_Flood.csv
...
```

---

## 🏗️ Final Directory Structure

```
unified-ids-and-iot-security-system/
├── data/
│   ├── raw/
│   │   └── CICIoT2023/
│   │       └── CSV/
│   │           ├── DDoS-ACK_Fragmentation.csv
│   │           ├── DDoS-UDP_Flood.csv
│   │           ├── ... (167 more files)
│   │           └── benign-traffic.csv
│   └── processed/  (will be created by notebooks)
├── notebooks/
│   ├── 01_data_consolidation_and_label_engineering.ipynb
│   ├── 02_advanced_preprocessing_and_feature_engineering.ipynb
│   └── ...
└── trained_models/  (will be created during training)
```

---

## 🚀 Next Steps

After downloading the dataset:

1. **Open Jupyter Notebook**
   ```bash
   cd /mnt/d/project/unified-ids-and-iot-security-system
   source venv/bin/activate
   jupyter notebook
   ```

2. **Run Notebook 01**
   - Open `notebooks/01_data_consolidation_and_label_engineering.ipynb`
   - Make sure `DATASET = "CICIoT2023"` is set (line 11)
   - Click "Run All" or execute cells one by one

3. **Verify Output**
   - Check for `data/processed/CICIoT2023/combined.csv`
   - Should see message: "✓ Data consolidation complete!"

---

## 📊 Dataset Overview

| Property | Value |
|----------|-------|
| **Files** | 169 CSV files |
| **Total Samples** | ~46.6 million |
| **Features** | 46 network flow features |
| **Benign Samples** | ~1.1 million |
| **Attack Samples** | ~45.5 million |
| **Attack Types** | 33 unique attacks |
| **Total Classes** | 34 (33 attacks + benign) |

### Attack Categories

1. **DDoS** (8 types): ACK fragmentation, UDP flood, SlowLoris, ICMP flood, SYN flood, etc.
2. **DoS** (3 types): HTTP flood, SYN flood, TCP flood
3. **Reconnaissance** (3 types): Host discovery, OS fingerprinting, Port scanning
4. **Web-based** (4 types): SQL injection, XSS, Command injection, Backdoor malware
5. **Brute Force** (1 type): Dictionary brute force
6. **Spoofing** (2 types): ARP spoofing, DNS spoofing
7. **Mirai Botnet** (12 types): Various flooding attacks

---

## ⚠️ Troubleshooting

### Issue: wget not found
```bash
# Ubuntu/Debian
sudo apt-get install wget

# Or download manually from browser:
# http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/CSV/
```

### Issue: Download interrupted
```bash
# Resume download with -c flag
cd data/raw/CICIoT2023
wget -c -r -np -nH --cut-dirs=3 http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/CSV/
```

### Issue: Permission denied
```bash
# Make sure directory is writable
chmod 755 data/raw/CICIoT2023/CSV
```

### Issue: Not enough disk space
```bash
# Check available space
df -h

# Clean up if needed
# Minimum required: 15 GB free space
# Recommended: 30 GB free space
```

### Issue: Files have different names
```bash
# The notebook will work as long as files are in:
# data/raw/CICIoT2023/CSV/*.csv

# If files are in subdirectories, move them:
find data/raw/CICIoT2023 -name "*.csv" -exec mv {} data/raw/CICIoT2023/CSV/ \;
```

---

## 💡 Tips

**For faster processing:**
- Use SSD storage if available
- Close other applications to free RAM
- Consider sampling 10% of data for initial testing

**To test with smaller dataset:**
```python
# In notebook 01, add after loading:
df = df.sample(frac=0.1, random_state=42)  # Use 10% of data
```

**To speed up download:**
```bash
# Use parallel downloads
aria2c -x 16 http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/CSV/
```

---

## ✅ Ready to Train!

Once you see:
```
✓ 169 files downloaded
✓ ~13 GB total size
✓ Files in data/raw/CICIoT2023/CSV/
```

You're ready to start training! Open `MODEL_TRAINING_GUIDE.md` for the complete training workflow.
