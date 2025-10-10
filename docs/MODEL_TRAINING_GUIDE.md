# Model Training Guide - IoT Intrusion Detection System

**Complete Step-by-Step Guide to Training Machine Learning Models**

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Dataset Setup](#dataset-setup)
3. [Training Pipeline](#training-pipeline)
4. [Notebook Explanations](#notebook-explanations)
5. [Model Architectures](#model-architectures)
6. [Expected Results](#expected-results)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This guide explains how to train machine learning models for detecting network intrusions in IoT environments using the CIC-IoT-2023 dataset.

### What You'll Build

- **Classical ML Models**: Random Forest, XGBoost, LightGBM
- **Deep Learning Models**: FFNN with Residual Connections, CNN
- **Ensemble Models**: Voting and Stacking classifiers

### Training Time

- **Quick test** (~10% data): 30-60 minutes
- **Full training**: 3-5 hours

---

## 📥 Dataset Setup

### Step 1: Download CIC-IoT-2023

```bash
# Create dataset directory
cd /mnt/d/project/unified-ids-and-iot-security-system
mkdir -p data/raw/CICIoT2023/CSV

# Download dataset
cd data/raw/CICIoT2023
wget -r -np -nH --cut-dirs=3 http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/CSV/

# Verify download
cd CSV
ls -lh *.csv | wc -l  # Should show 169 files
```

**Alternative: Download from Kaggle**
```bash
pip install kaggle
kaggle datasets download -d madhavmalhotra/unb-cic-iot-dataset
unzip unb-cic-iot-dataset.zip -d data/raw/CICIoT2023/CSV/
```

### Step 2: Verify Directory Structure

```
data/
└── raw/
    └── CICIoT2023/
        └── CSV/
            ├── DDoS-ACK_Fragmentation.csv
            ├── DDoS-UDP_Flood.csv
            ├── DoS-SYN_Flood.csv
            ├── Mirai-greeth_flood.csv
            ├── ... (165 more files)
```

### Dataset Information

| Property | Value |
|----------|-------|
| **Files** | 169 CSV files |
| **Total Samples** | ~46 million |
| **Features** | 46 network flow features |
| **Attack Types** | 33 different attacks |
| **Classes** | 34 (33 attacks + 1 benign) |
| **Size** | ~13 GB uncompressed |

---

## 🔄 Training Pipeline

### Complete Workflow

```
Raw Data → Consolidation → Preprocessing → Imbalance Handling →
Model Training → Hyperparameter Tuning → Ensemble → Evaluation
```

### Notebooks Execution Order

| # | Notebook | Purpose | Output | Time |
|---|----------|---------|--------|------|
| **01** | Data Consolidation | Load & merge CSVs | `combined.csv` | 5-10 min |
| **02** | Feature Engineering | Scale & clean features | Train/test splits | 3-5 min |
| **03** | Class Imbalance | Handle imbalanced data | Balanced datasets | 5-15 min |
| **04** | Baseline Models | Train initial models | Baseline pkl files | 20-40 min |
| **05** | Deep Learning | Train neural networks | Keras models | 30-60 min |
| **06** | Hyperparameter Tuning | Optimize with Optuna | Optimized models | 40-90 min |
| **07** | Model Comparison | Evaluate & ensemble | Final comparison | 20-40 min |

**Total Time**: 2.5-4.5 hours for full pipeline

---

## 📓 Notebook Explanations

### Notebook 01: Data Consolidation and Label Engineering

**What it does:**
1. Loads all 169 CSV files from CIC-IoT-2023
2. Combines them into single dataset
3. Handles missing values and infinite values
4. Encodes attack labels to numeric IDs
5. Removes non-informative columns (IPs, timestamps)

**Key Concepts:**

```python
# Dataset auto-selection
DATASET = "CICIoT2023"  # or "CICIDS2017"

# Label encoding maps attack names to numbers
# Example:
# "Benign" → 0
# "DDoS-UDP_Flood" → 1
# "Mirai-greeth_flood" → 2
# ... etc
```

**Input:**
- 169 CSV files in `data/raw/CICIoT2023/CSV/`

**Output:**
- `data/processed/CICIoT2023/combined.csv` - Consolidated dataset
- `trained_models/encoder.pkl` - Label encoder for predictions
- `label_distribution.png` - Visualization of attack types

**Why it's important:**
- Raw data has multiple files that need merging
- Attack labels are text strings, models need numbers
- Missing values can crash training

---

### Notebook 02: Advanced Preprocessing & Feature Engineering

**What it does:**
1. Splits data into training (80%) and testing (20%)
2. Identifies and removes highly correlated features (>0.95)
3. Scales features using StandardScaler and MinMaxScaler
4. Analyzes feature importance

**Key Concepts:**

```python
# Train-test split BEFORE scaling (prevents data leakage)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Feature scaling transforms values to similar ranges
# StandardScaler: mean=0, std=1 (for models like SVM, neural nets)
# MinMaxScaler: range [0,1] (for models needing bounded inputs)

# Correlation removal prevents redundant features
# If two features are >95% correlated, keep only one
```

**Input:**
- `data/processed/CICIoT2023/combined.csv`

**Output:**
- `data/processed/ml_ready/X_train_standard.csv` - Scaled training features
- `data/processed/ml_ready/X_test_standard.csv` - Scaled test features
- `data/processed/ml_ready/y_train.csv` - Training labels
- `data/processed/ml_ready/y_test.csv` - Test labels
- `feature_correlation.png` - Heatmap visualization

**Why it's important:**
- Scaling prevents features with large values from dominating
- Removing correlated features reduces noise and training time
- Test set must be separate to evaluate real-world performance

---

### Notebook 03: Addressing Class Imbalance

**What it does:**
1. Computes class weights for imbalanced classes
2. Applies moderate SMOTE to rare attack types
3. Creates multiple dataset variants for different models
4. Generates focal loss function for deep learning

**Key Concepts:**

```python
# Imbalanced data problem:
# Benign: 1,000,000 samples
# Rare Attack: 100 samples
# Model will just predict "Benign" always!

# Solution 1: Class Weights
# Give higher penalty for misclassifying rare classes
# Works best with tree-based models (RF, XGBoost)

# Solution 2: SMOTE (Synthetic Minority Over-sampling)
# Create synthetic samples for rare classes
# More conservative approach than before

# Solution 3: Focal Loss
# Special loss function that focuses on hard-to-classify samples
# Best for deep learning models
```

**Input:**
- `data/processed/ml_ready/X_train_standard.csv`

**Output:**
- `data/processed/ml_balance/train_original.csv` - Original training data
- `data/processed/ml_balance/train_balanced.csv` - SMOTE-balanced data
- `data/processed/ml_balance/class_weights.pkl` - Computed class weights
- `data/processed/ml_balance/focal_loss.py` - Focal loss implementation

**Why it's important:**
- Real network traffic has way more benign than attacks
- Models trained on imbalanced data have poor attack detection
- Different models need different imbalance strategies

---

### Notebook 04: Baseline Model and Evaluation

**What it does:**
1. Trains 4 classical ML models (Random Forest, XGBoost, LogisticRegression, LightGBM)
2. Evaluates each model on validation set
3. Selects and saves best baseline model
4. Generates confusion matrices

**Key Concepts:**

```python
# Random Forest: Multiple decision trees voting together
# - Fast training
# - Good with imbalanced data using class_weight='balanced'
# - Interpretable feature importances

# XGBoost: Gradient boosted decision trees
# - Usually best classical ML model
# - Uses sample_weight for imbalance
# - Very accurate but slower training

# LightGBM: Faster gradient boosting
# - Similar to XGBoost but faster
# - Built-in class_weight support
# - Good for large datasets

# LogisticRegression: Linear model baseline
# - Very fast
# - Good for comparison
# - Usually lowest accuracy but good sanity check
```

**Input:**
- `data/processed/ml_balance/train_balanced.csv`

**Output:**
- `trained_models/best_baseline.pkl` - Best performing classical model
- Confusion matrices for all models

**Expected Accuracy:**
- Random Forest: 96-98%
- XGBoost: 97-99%
- LightGBM: 97-98%
- LogisticRegression: 85-90%

**Why it's important:**
- Baseline models are fast to train
- Often surprisingly good performance
- Provides comparison for deep learning models

---

### Notebook 05: Deep Learning Model Development

**What it does:**
1. Trains FFNN (Feedforward Neural Network) with residual connections
2. Trains CNN (Convolutional Neural Network) with stability improvements
3. Trains Autoencoder for anomaly detection
4. Uses callbacks for early stopping and learning rate scheduling

**Key Concepts:**

```python
# FFNN with Residual Connections
# Input → Dense(512) → BatchNorm → Dropout →
# Residual Block 1 → Residual Block 2 → Output
#
# Residual connections help gradient flow in deep networks
# Formula: output = activation(x) + x

# CNN for Network Traffic
# Treats network features as 1D sequence
# Conv1D → BatchNorm → Conv1D → Flatten → Dense → Output
# Learns local patterns in feature space

# Callbacks:
# - EarlyStopping: Stops when validation loss stops improving
# - ReduceLROnPlateau: Reduces learning rate when stuck
# - ModelCheckpoint: Saves best model automatically

# Why LSTM was removed:
# - 7.5+ hours training time
# - Only 0-1% accuracy improvement
# - Not worth the time cost
```

**Input:**
- `data/processed/ml_balance/train_balanced.csv`

**Output:**
- `trained_models/dl_models/final_ffnn_residual.keras` - FFNN model
- `trained_models/dl_models/final_cnn_stable.keras` - CNN model
- `trained_models/dl_models/anomaly_autoencoder.keras` - Autoencoder
- Training history plots

**Expected Accuracy:**
- FFNN Residual: 96-97.5%
- CNN Stable: 97-98%
- Autoencoder: Anomaly detection (threshold-based)

**Training Tips:**
- Use GPU if available (10x faster)
- Start with 50 epochs, early stopping will stop sooner
- Batch size of 256 works well

**Why it's important:**
- Deep learning can capture complex patterns
- Residual connections improve training stability
- Early stopping prevents overfitting

---

### Notebook 06: Hyperparameter Tuning and Optimization

**What it does:**
1. Uses Optuna for Bayesian hyperparameter optimization
2. Tunes Random Forest, XGBoost, and LightGBM
3. Uses 5-fold cross-validation
4. Optimizes for F1-weighted score (better for imbalanced data)

**Key Concepts:**

```python
# Hyperparameter Tuning
# Models have "knobs" that affect performance:
# - Random Forest: n_estimators, max_depth, min_samples_split
# - XGBoost: learning_rate, max_depth, subsample
# - LightGBM: num_leaves, learning_rate, min_child_samples

# Optuna uses Bayesian optimization
# Smarter than random search or grid search
# Learns which hyperparameters work well and tries similar ones

# Example optimization:
# Trial 1: learning_rate=0.1, max_depth=5 → F1=0.92
# Trial 2: learning_rate=0.05, max_depth=8 → F1=0.95 ← Better!
# Trial 3: learning_rate=0.03, max_depth=10 → F1=0.96 ← Even better!
# Optuna keeps exploring around successful values

# Cross-validation (5-fold)
# Splits training data into 5 parts
# Trains on 4 parts, validates on 1 part
# Repeats 5 times, averages score
# More reliable than single validation split
```

**Input:**
- `data/processed/ml_balance/train_original.csv`
- `data/processed/ml_balance/class_weights.pkl`

**Output:**
- `trained_models/final_rf_optuna.pkl` - Optimized Random Forest
- `trained_models/final_xgb_optuna.pkl` - Optimized XGBoost
- `trained_models/final_lgbm_optuna.pkl` - Optimized LightGBM

**Trials:**
- Random Forest: 25 trials (~10-15 min)
- XGBoost: 30 trials (~15-25 min)
- LightGBM: 25 trials (~10-15 min)

**Expected Improvement:**
- Baseline F1: 96-97%
- After tuning F1: 97.5-98.5%
- Improvement: +1.5-2% F1 score

**Why it's important:**
- Default hyperparameters are rarely optimal
- Proper tuning can boost accuracy by 1-5%
- Optuna is much faster than grid search

---

### Notebook 07: Model Comparison Dashboard & Ensemble Methods

**What it does:**
1. Loads all trained models (classical + deep learning)
2. Evaluates on common test set
3. Creates ensemble models (Voting, Stacking)
4. Generates comprehensive comparison dashboard
5. Analyzes per-class performance

**Key Concepts:**

```python
# Ensemble Methods: Combining multiple models
# Usually better than any single model!

# Voting Ensemble (Soft Voting)
# Each model predicts probabilities
# Average probabilities across all models
# Final prediction = highest average probability
# Example:
#   RF:    [0.8 benign, 0.2 attack]
#   XGB:   [0.7 benign, 0.3 attack]
#   LGBM:  [0.9 benign, 0.1 attack]
#   Vote:  [0.8 benign, 0.2 attack] → Predict: Benign

# Stacking Ensemble
# Train a "meta-model" on predictions from base models
# Meta-model learns which base model to trust
# Usually gives best performance

# Metrics Tracked:
# - Accuracy: Overall correctness
# - F1-Score: Balance of precision and recall
# - Precision: Of predicted attacks, how many are real?
# - Recall: Of real attacks, how many did we catch?
# - Inference Time: How fast can we predict?
# - Model Size: Disk space needed
```

**Input:**
- All trained models from notebooks 04-06
- `data/processed/ml_balance/test.csv`

**Output:**
- `trained_models/voting_ensemble.pkl` - Voting classifier
- `trained_models/stacking_ensemble.pkl` - Stacking classifier
- `trained_models/model_comparison_enhanced.csv` - All metrics
- `trained_models/model_comparison_dashboard.png` - Visual comparison
- `trained_models/per_class_performance.png` - Per-attack analysis

**Expected Results:**

| Model Type | Accuracy | F1-Score | Speed |
|------------|----------|----------|-------|
| XGBoost Optuna | 98.2% | 98.0% | Fast |
| LightGBM Optuna | 98.0% | 97.8% | Very Fast |
| FFNN Residual | 97.2% | 97.0% | Fast |
| CNN Stable | 97.8% | 97.6% | Medium |
| Voting Ensemble | 98.5% | 98.3% | Medium |
| Stacking Ensemble | **98.7%** | **98.5%** | Slow |

**Why it's important:**
- Shows which model performs best
- Identifies weaknesses (which attacks are hard to detect)
- Ensemble usually gives best results
- Helps choose model for deployment

---

## 🏗️ Model Architectures

### 1. Random Forest

```
Decision Tree 1 ┐
Decision Tree 2 ├→ Vote → Final Prediction
Decision Tree 3 ┘

Each tree sees random subset of features
Vote by majority or average probabilities
```

**Parameters:**
- `n_estimators`: Number of trees (200-600)
- `max_depth`: Tree depth (10-50)
- `class_weight='balanced'`: Handle imbalance

### 2. XGBoost

```
Tree 1 → Residual 1 → Tree 2 → Residual 2 → ... → Final Prediction

Each tree corrects errors of previous trees
Gradient-based optimization
```

**Parameters:**
- `learning_rate`: Step size (0.01-0.3)
- `max_depth`: Tree depth (4-15)
- `subsample`: Data sampling (0.6-1.0)

### 3. FFNN with Residual Connections

```
Input (46 features)
    ↓
Dense(512) + ReLU + BatchNorm + Dropout
    ↓
[Residual Block 1]
├─→ Dense(256) + ReLU + BatchNorm ─┐
↓                                   ↓
└───────────── Add ← ───────────────┘
    ↓
[Residual Block 2]
├─→ Dense(128) + ReLU + BatchNorm ─┐
↓                                   ↓
└───────────── Add ← ───────────────┘
    ↓
Dense(34) + Softmax → Output (34 classes)
```

**Architecture Benefits:**
- Residual connections prevent vanishing gradients
- BatchNorm stabilizes training
- Dropout prevents overfitting

### 4. CNN for Network Traffic

```
Input (46 features × 1 channel)
    ↓
Conv1D(128 filters, kernel=3) + ReLU + BatchNorm + Dropout
    ↓
Conv1D(64 filters, kernel=3) + ReLU + BatchNorm + Dropout
    ↓
Flatten
    ↓
Dense(256) + ReLU + BatchNorm + Dropout
    ↓
Dense(128) + ReLU + Dropout
    ↓
Dense(34) + Softmax → Output
```

**Why CNN for Tabular Data:**
- Learns local feature patterns
- Conv1D treats features as sequence
- Can capture feature interactions

---

## 📊 Expected Results

### Performance by Attack Type

| Attack Category | Expected F1-Score | Difficulty |
|----------------|-------------------|------------|
| **DDoS Attacks** | 98-99% | Easy |
| **DoS Attacks** | 97-98% | Easy |
| **Reconnaissance** | 95-97% | Medium |
| **Web Attacks** | 93-96% | Hard |
| **Brute Force** | 96-98% | Medium |
| **Spoofing** | 94-97% | Medium |
| **Mirai Botnet** | 97-99% | Easy |

### Training Resources

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **RAM** | 16 GB | 32 GB |
| **Disk** | 20 GB | 50 GB |
| **CPU** | 4 cores | 8+ cores |
| **GPU** | None | NVIDIA GPU (10x faster DL) |

### Model Sizes

| Model | Disk Size |
|-------|-----------|
| Random Forest | 50-200 MB |
| XGBoost | 20-100 MB |
| LightGBM | 10-50 MB |
| FFNN Residual | 5-15 MB |
| CNN Stable | 5-15 MB |
| Ensemble | 200-400 MB (combined) |

---

## 🔧 Troubleshooting

### Issue: Out of Memory

```python
# In notebook 01, sample the data:
df = df.sample(frac=0.1, random_state=42)  # Use 10% of data
```

### Issue: Training Too Slow

```python
# In notebook 06, reduce trials:
study_rf.optimize(objective_rf, n_trials=10)  # Instead of 25

# In notebook 05, reduce epochs:
epochs=20  # Instead of 50
```

### Issue: "No CSV files found"

```bash
# Verify directory structure:
ls -la data/raw/CICIoT2023/CSV/*.csv

# If empty, download dataset:
cd data/raw/CICIoT2023
wget -r http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/CSV/
```

### Issue: GPU Not Detected

```python
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))

# If empty, install CUDA toolkit:
# https://www.tensorflow.org/install/gpu
```

### Issue: Kernel Crashes

```python
# Reduce batch size in notebook 05:
batch_size=128  # Instead of 256

# Use smaller validation split:
validation_split=0.1  # Instead of 0.2
```

---

## 🚀 Quick Start Commands

```bash
# 1. Activate virtual environment
cd /mnt/d/project/unified-ids-and-iot-security-system
source venv/bin/activate

# 2. Ensure dependencies installed
pip install -r requirements.txt
pip install optuna

# 3. Download dataset (if not done)
mkdir -p data/raw/CICIoT2023/CSV
cd data/raw/CICIoT2023
wget -r http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/CSV/

# 4. Start Jupyter
cd /mnt/d/project/unified-ids-and-iot-security-system
jupyter notebook

# 5. Run notebooks in order: 01 → 02 → 03 → 04 → 05 → 06 → 07
```

---

## 📖 Additional Resources

### Papers
- **CIC-IoT-2023**: "CICIoT2023: A real-time dataset and benchmark for large-scale attacks in IoT environment"
- **XGBoost**: "XGBoost: A Scalable Tree Boosting System"
- **ResNet**: "Deep Residual Learning for Image Recognition" (residual connections)

### Documentation
- **Scikit-learn**: https://scikit-learn.org/
- **XGBoost**: https://xgboost.readthedocs.io/
- **LightGBM**: https://lightgbm.readthedocs.io/
- **TensorFlow/Keras**: https://www.tensorflow.org/guide/keras
- **Optuna**: https://optuna.readthedocs.io/

---

## ✅ Checklist

Before starting training:
- [ ] Downloaded CIC-IoT-2023 dataset
- [ ] Verified 169 CSV files in `data/raw/CICIoT2023/CSV/`
- [ ] Installed all requirements (`pip install -r requirements.txt`)
- [ ] Installed Optuna (`pip install optuna`)
- [ ] Activated virtual environment
- [ ] Have at least 16 GB RAM available
- [ ] Have at least 20 GB disk space available

After training:
- [ ] All 7 notebooks executed successfully
- [ ] `trained_models/` directory has all model files
- [ ] `model_comparison_enhanced.csv` generated
- [ ] Best model identified from dashboard
- [ ] Tested model on sample data

---

## 🎓 Summary

**What You Learned:**

1. **Data Processing**: How to load, clean, and prepare large datasets
2. **Feature Engineering**: Scaling, correlation analysis, importance
3. **Imbalance Handling**: Class weights, SMOTE, focal loss
4. **Classical ML**: Random Forest, XGBoost, LightGBM
5. **Deep Learning**: FFNN, CNN with modern techniques
6. **Hyperparameter Tuning**: Bayesian optimization with Optuna
7. **Ensemble Methods**: Voting and stacking for better accuracy
8. **Model Evaluation**: Comprehensive metrics and visualization

**Best Practices Applied:**

✅ Train-test split before scaling (prevents data leakage)
✅ Stratified sampling (maintains class distribution)
✅ Cross-validation (reliable performance estimates)
✅ Early stopping (prevents overfitting)
✅ Learning rate scheduling (improves convergence)
✅ Residual connections (stable deep networks)
✅ Class weights (handles imbalance)
✅ Ensemble methods (boosts accuracy)

**Next Steps:**

1. Deploy best model for real-time detection
2. Integrate with packet_sniffer.py
3. Set up alerting system
4. Monitor model performance in production
5. Retrain periodically with new data

---

**Need Help?** Check the troubleshooting section or review individual notebook documentation.

**Ready to deploy?** See `RECOMMENDED_DATASETS.md` for integration with Scapy real-time capture.
