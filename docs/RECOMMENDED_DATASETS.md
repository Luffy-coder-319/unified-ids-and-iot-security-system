# Recommended Datasets for Real-Time Intrusion Detection with Scapy

This document provides curated datasets specifically suitable for training models to detect intrusions in real-time from Scapy-captured packets.

---

## 🏆 Top Recommendations

### 1. **CIC-IoT-2023** ⭐ BEST FOR YOUR USE CASE

**Why it's perfect for you:**
- ✅ **Native PCAP files** - Original packet captures (perfect for Scapy)
- ✅ **IoT-focused** - Matches your project's IoT security focus
- ✅ **Modern attacks** (2023) - 33 different attack types
- ✅ **Large scale** - 105 IoT devices
- ✅ **Both formats** - PCAP for real packets + CSV for features
- ✅ **Free download** - No subscription required

**Dataset Details:**
- **Size**: ~15 GB (PCAP files)
- **Devices**: 105 real IoT devices
- **Attack Categories**: 7 major types
  - DDoS (ACK fragmentation, UDP flood, SlowLoris, ICMP flood, SYN flood, etc.)
  - DoS (TCP, UDP, HTTP flood)
  - Reconnaissance (Host discovery, OS fingerprinting, Port scanning)
  - Web-based (SQL injection, XSS, Command injection, Backdoor malware)
  - Brute Force (Dictionary attacks)
  - Spoofing (ARP spoofing, DNS spoofing)
  - Mirai Botnet attacks

**Download:**
```bash
# Direct download link
http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/

# Dataset structure:
CICIoT2023/
├── PCAP/           # Original packet captures (.pcap files)
├── CSV/            # Pre-extracted features
├── Example/        # Jupyter notebook examples
└── Supplementary/  # Collection tools and scripts
```

**Working with Scapy:**
```python
from scapy.all import rdpcap, IP, TCP, UDP

# Read PCAP file
packets = rdpcap('CICIoT2023/PCAP/attack_file.pcap')

# Extract features
for pkt in packets:
    if IP in pkt:
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        protocol = pkt[IP].proto
        # ... extract more features
```

**Official Page:** https://www.unb.ca/cic/datasets/iotdataset-2023.html

---

### 2. **IoT Network Intrusion Dataset** (IEEE DataPort)

**Why it's good:**
- ✅ **42 PCAP files** - Real IoT device captures
- ✅ **Smart home devices** - EZVIZ camera, NUGU speaker
- ✅ **Documented for Scapy** - Explicitly mentions Scapy/dpkt parsing
- ✅ **Free with registration** - IEEE DataPort account
- ✅ **Moderate size** - 823 MB (good for quick testing)

**Dataset Details:**
- **Size**: 823.69 MB
- **Devices**:
  - EZVIZ Wi-Fi Camera (MAC: bc:1c:81:4b:ae:ba)
  - SKT NUGU AI Speaker (MAC: 04:32:f4:45:17:b3)
- **Attack Types**:
  - Man-in-the-Middle (ARP spoofing)
  - DoS (SYN flooding)
  - Network Scanning
  - Mirai Botnet (UDP/ACK/HTTP flooding)
  - Telnet Brute Force

**Download:**
- URL: https://ieee-dataport.org/open-access/iot-network-intrusion-dataset
- Requires: Free IEEE DataPort account
- License: Creative Commons BY 4.0

**Scapy Usage:**
```python
import scapy.all as scapy

# Explicitly documented to work with Scapy
packets = scapy.rdpcap('iot_attack.pcap')

# Filter by device MAC
camera_packets = [p for p in packets if p.src == 'bc:1c:81:4b:ae:ba']
```

---

### 3. **ROSPaCe Dataset** (2024) - For ROS2/IoT Systems

**Why it's relevant:**
- ✅ **Attacks via Scapy** - Attacks implemented using Python & Scapy
- ✅ **PCAP files** - Logged in .pcap format
- ✅ **Cyber-Physical Systems** - ROS2-based (robotic/IoT systems)
- ✅ **Recent** - Published May 2024
- ✅ **Research-grade** - Published in Nature Scientific Data

**Dataset Details:**
- **Focus**: ROS2-based cyber-physical systems
- **Attack Implementation**: Python + Scapy
- **Format**: Raw PCAP files
- **Types**: Penetration testing scenarios on embedded systems

**Best For:**
- IoT devices with embedded systems
- Robotic control systems
- Industrial IoT scenarios

**Access:**
- Paper: https://www.nature.com/articles/s41597-024-03311-2
- Dataset: Available through Nature Scientific Data repository

---

### 4. **UM-NIDS** (Unified Multimodal NIDS) - 2024

**Why it's powerful:**
- ✅ **Aggregates 4 major datasets** - CIC-IDS2017, CIC-IoT2023, UNSW-NB15, CIC-DDoS2019
- ✅ **Pre-processed** - Standardized features
- ✅ **Multimodal** - Network flow + packet payload + context
- ✅ **Tool included** - GitHub repo with processing tools
- ✅ **Large scale** - 18-24 GB per dataset

**Dataset Details:**
- **Size**:
  - Undersampled version: 394 MB (for quick testing)
  - Full datasets: 8-24 GB each
- **Source PCAPs from**: CIC-IDS2017, CIC-IoT2023, UNSW-NB15, CIC-DDoS2019
- **Format**: CSV (processed from PCAP)

**Download:**
- URL: https://ieee-dataport.org/documents/unified-multimodal-network-intrusion-detection-systems-dataset
- Requires: IEEE DataPort subscription
- GitHub: https://github.com/SyedWaliAbbas/UM-NIDS-Tool

**Best For:**
- Comparing multiple datasets
- Pre-processed features (if you don't want to process PCAP manually)
- Comprehensive attack coverage

---

### 5. **CIC-IDS2017** (Classic Reference)

**Why it's still relevant:**
- ✅ **Industry standard** - Most cited IDS dataset
- ✅ **PCAP files available** - Original packet captures
- ✅ **Well-documented** - Extensive research papers
- ✅ **Realistic traffic** - Benign + attack mixed
- ✅ **Free download**

**Dataset Details:**
- **Duration**: 5 days of capture
- **Attack Types**: Brute Force, DoS, DDoS, Web attacks, Infiltration, Botnet
- **Format**: PCAP + CSV
- **Size**: Several GB

**Download:**
- URL: https://www.unb.ca/cic/datasets/ids-2017.html
- You're already using this! ✅

---

## 📊 Quick Comparison Table

| Dataset | Size | PCAP | IoT Focus | Attacks | Year | Free | Scapy Ready |
|---------|------|------|-----------|---------|------|------|-------------|
| **CIC-IoT-2023** | 15 GB | ✅ | ✅✅✅ | 33 types | 2023 | ✅ | ✅✅✅ |
| **IoT IEEE** | 823 MB | ✅ | ✅✅ | 5 types | 2020 | ✅ | ✅✅✅ |
| **ROSPaCe** | Medium | ✅ | ✅✅ | Multiple | 2024 | ✅ | ✅✅✅ |
| **UM-NIDS** | 8-24 GB | Derived | ✅ | 100+ | 2024 | 💰 | ⚠️ CSV |
| **CIC-IDS2017** | ~7 GB | ✅ | ❌ | 14 types | 2017 | ✅ | ✅ |

Legend: ✅ Yes, ❌ No, ⚠️ Partial, 💰 Requires subscription

---

## 🎯 Recommended Workflow

### For Your Real-Time Scapy Detection System

**Phase 1: Start with CIC-IoT-2023** (Primary)
```bash
# Download
wget -r http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/

# Structure:
cd CIC_IOT_Dataset2023/PCAP/
ls *.pcap  # Your raw packet files
```

**Phase 2: Supplement with IoT IEEE Dataset** (Validation)
```bash
# Smaller dataset for quick testing
# Good for validating your model on different IoT devices
```

**Phase 3: Keep CIC-IDS2017** (Baseline Comparison)
```bash
# You already have this
# Use for comparing traditional network attacks
```

---

## 🔧 Scapy Feature Extraction Template

Here's how to extract features from PCAP files for real-time detection:

```python
from scapy.all import rdpcap, IP, TCP, UDP, ICMP, Raw
import pandas as pd
from collections import defaultdict

def extract_features_from_pcap(pcap_file):
    """Extract features compatible with your trained models"""
    packets = rdpcap(pcap_file)

    flows = defaultdict(lambda: {
        'packet_count': 0,
        'total_bytes': 0,
        'tcp_flags': [],
        'protocols': set(),
        'ports': set(),
        'durations': []
    })

    for pkt in packets:
        if IP in pkt:
            # Flow key (5-tuple)
            flow_key = (
                pkt[IP].src,
                pkt[IP].dst,
                pkt[IP].proto,
                pkt.sport if hasattr(pkt, 'sport') else 0,
                pkt.dport if hasattr(pkt, 'dport') else 0
            )

            # Aggregate flow statistics
            flows[flow_key]['packet_count'] += 1
            flows[flow_key]['total_bytes'] += len(pkt)
            flows[flow_key]['protocols'].add(pkt[IP].proto)

            if TCP in pkt:
                flows[flow_key]['tcp_flags'].append(pkt[TCP].flags)
                flows[flow_key]['ports'].add(pkt[TCP].dport)

            if UDP in pkt:
                flows[flow_key]['ports'].add(pkt[UDP].dport)

    # Convert to features matching CICIDS2017 format
    features = []
    for flow_key, stats in flows.items():
        feature_dict = {
            'src_ip': flow_key[0],
            'dst_ip': flow_key[1],
            'protocol': flow_key[2],
            'src_port': flow_key[3],
            'dst_port': flow_key[4],
            'total_fwd_packets': stats['packet_count'],
            'total_length_of_fwd_packets': stats['total_bytes'],
            # ... add more features to match your model's input
        }
        features.append(feature_dict)

    return pd.DataFrame(features)

# Usage
df = extract_features_from_pcap('CICIoT2023/PCAP/ddos_attack.pcap')
predictions = your_model.predict(df)
```

---

## 💡 Integration with Your Current System

### Update your `packet_sniffer.py`

```python
from scapy.all import sniff, wrpcap
import pandas as pd
from pathlib import Path

class RealTimePacketCollector:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)
        self.packet_buffer = []
        self.buffer_size = 100  # Process every 100 packets

    def packet_callback(self, pkt):
        """Called for each captured packet"""
        self.packet_buffer.append(pkt)

        if len(self.packet_buffer) >= self.buffer_size:
            self.process_buffer()

    def process_buffer(self):
        """Extract features and predict"""
        # Save to temporary PCAP
        temp_pcap = "temp_capture.pcap"
        wrpcap(temp_pcap, self.packet_buffer)

        # Extract features (use function above)
        features = extract_features_from_pcap(temp_pcap)

        # Predict
        predictions = self.model.predict(features)

        # Handle alerts
        for idx, pred in enumerate(predictions):
            if pred != 0:  # Not benign
                self.trigger_alert(features.iloc[idx], pred)

        # Clear buffer
        self.packet_buffer = []

    def start_capture(self, interface="eth0"):
        """Start real-time capture"""
        print(f"Starting capture on {interface}...")
        sniff(iface=interface, prn=self.packet_callback, store=0)

# Usage
collector = RealTimePacketCollector("trained_models/final_xgb_optuna.pkl")
collector.start_capture()
```

---

## 📥 Download Instructions

### CIC-IoT-2023 (Recommended)
```bash
# Method 1: Direct download
wget -r -np -nH --cut-dirs=2 http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/

# Method 2: Selective download (PCAP only)
wget -r -np -nH --cut-dirs=3 -A "*.pcap" http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/PCAP/
```

### IoT Network Intrusion Dataset
```bash
# 1. Create free account at IEEE DataPort
# 2. Visit: https://ieee-dataport.org/open-access/iot-network-intrusion-dataset
# 3. Click "Download Dataset"
# 4. Extract: unzip iot-network-intrusion-dataset.zip
```

### Kaggle Alternative (CIC-IoT-2023)
```bash
# Install Kaggle CLI
pip install kaggle

# Download
kaggle datasets download -d madhavmalhotra/unb-cic-iot-dataset

# Extract
unzip unb-cic-iot-dataset.zip
```

---

## 🚀 Next Steps

1. **Download CIC-IoT-2023** (Primary dataset)
   ```bash
   mkdir -p data/raw/CICIoT2023
   cd data/raw/CICIoT2023
   wget -r http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/
   ```

2. **Create PCAP Processing Pipeline**
   - Extract features from PCAP files using Scapy
   - Match feature format to your current CICIDS2017 pipeline
   - Retrain models on IoT-specific attacks

3. **Validate on IoT IEEE Dataset**
   - Test your model on different IoT devices
   - Ensure generalization across device types

4. **Deploy Real-Time System**
   - Use the `RealTimePacketCollector` template above
   - Integrate with your existing `packet_sniffer.py`
   - Add alert mechanisms

---

## 📚 Additional Resources

### Research Papers
- **CIC-IoT-2023**: "CICIoT2023: A real-time dataset and benchmark for large-scale attacks in IoT environment"
- **ROSPaCe**: "Intrusion Detection Dataset for a ROS2-Based Cyber-Physical System and IoT Networks"

### Tools
- **CICFlowMeter**: Extract CICIDS-style features from PCAP
  ```bash
  git clone https://github.com/ahlashkari/CICFlowMeter
  ```

- **Scapy Documentation**: https://scapy.readthedocs.io/
- **UM-NIDS Tool**: https://github.com/SyedWaliAbbas/UM-NIDS-Tool

### Dataset Surveys
- "Network Intrusion Datasets: A Survey, Limitations, and Recommendations" (2025)
- Check for updated datasets: https://www.unb.ca/cic/datasets/

---

## ❓ FAQ

**Q: Can I mix CIC-IoT-2023 with my current CICIDS2017 training?**
A: Yes! They use similar feature extraction. Just ensure feature names match.

**Q: How do I handle PCAP files in real-time?**
A: Use Scapy's `sniff()` with callback, don't save to disk. See template above.

**Q: Which dataset has the most realistic IoT attacks?**
A: CIC-IoT-2023 with 105 real devices is most comprehensive.

**Q: Do I need to retrain my models?**
A: For IoT-specific attacks, yes. But your architecture can stay the same.

---

**Recommended Choice:** Start with **CIC-IoT-2023** - it's free, comprehensive, IoT-focused, and has native PCAP files perfect for Scapy!
