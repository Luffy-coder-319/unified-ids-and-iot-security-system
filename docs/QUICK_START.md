# Quick Start Guide - IoT Intrusion Detection Training

**Get started with model training in 5 minutes!**

---

## 🚀 Step 1: Download Dataset (10-20 minutes)

```bash
cd /mnt/d/project/unified-ids-and-iot-security-system
mkdir -p data/raw/CICIoT2023/CSV
cd data/raw/CICIoT2023
wget -r -np -nH --cut-dirs=3 -A "*.csv" http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/CSV/
```

**Verify:** `ls CSV/*.csv | wc -l` should show **169 files**

---

## 🔧 Step 2: Setup Environment

```bash
cd /mnt/d/project/unified-ids-and-iot-security-system
source venv/bin/activate
pip install -r requirements.txt
pip install optuna
```

---

## 📓 Step 3: Start Jupyter

```bash
jupyter notebook
```

Browser will open at `http://localhost:8888`

**Or use VSCode:** Just open the `.ipynb` files in VSCode

---

## ▶️ Step 4: Run Notebooks in Order

Execute these notebooks one by one:

1. **01_data_consolidation_and_label_engineering.ipynb**
   - Loads and merges 169 CSV files
   - Time: 5-10 minutes

2. **02_advanced_preprocessing_and_feature_engineering.ipynb**
   - Scales features and creates train/test splits
   - Time: 3-5 minutes

3. **03_addressing_class_imbalance.ipynb**
   - Handles imbalanced attack classes
   - Time: 5-15 minutes

4. **04_baseline_model_and_evaluation.ipynb**
   - Trains classical ML models
   - Time: 20-40 minutes

5. **05_deep_learning_model_development.ipynb**
   - Trains neural networks
   - Time: 30-60 minutes

6. **06_hyperparameter_tuning_and_optimization.ipynb**
   - Optimizes model parameters
   - Time: 40-90 minutes

7. **07_model_comparison_dashboard.ipynb**
   - Compares all models and creates ensembles
   - Time: 20-40 minutes

**Total Time:** 2.5-4.5 hours

---

## ✅ Success Indicators

After each notebook, you should see:

**Notebook 01:** ✓ Data consolidation complete!
- File created: `data/processed/CICIoT2023/combined.csv`

**Notebook 02:** ✓ Phase 2 complete!
- Files created: `data/processed/ml_ready/X_train_standard.csv`, etc.

**Notebook 03:** ✓ Saved all variants
- Files created: `data/processed/ml_balance/train_*.csv`

**Notebook 04:** ✓ Baseline models trained
- File created: `trained_models/best_baseline.pkl`

**Notebook 05:** ✓ Deep learning models saved
- Files created: `trained_models/dl_models/*.keras`

**Notebook 06:** ✓ Optimization complete!
- Files created: `trained_models/final_*_optuna.pkl`

**Notebook 07:** ✓ Dashboard generated
- Files created: `trained_models/model_comparison_enhanced.csv`

---

## 📊 Expected Results

After training, your best model should achieve:

- **Accuracy:** 98-99%
- **F1-Score:** 97.5-98.5%
- **Inference Speed:** 10,000-50,000 predictions/second

**Best Models Usually:**
1. Stacking Ensemble (98.5-98.7% accuracy)
2. XGBoost Optimized (98.0-98.5% accuracy)
3. LightGBM Optimized (97.8-98.2% accuracy)

---

## 🎯 What to Do Next

After training:

1. **Check Results:**
   ```bash
   cat trained_models/model_comparison_enhanced.csv
   ```

2. **View Dashboard:**
   ```bash
   open trained_models/model_comparison_dashboard.png
   ```

3. **Deploy Best Model:**
   - Copy best model to production
   - Integrate with `src/network/packet_sniffer.py`
   - Set up real-time detection

---

## 📚 Need More Details?

- **Full Training Guide:** See `MODEL_TRAINING_GUIDE.md`
- **Dataset Info:** See `RECOMMENDED_DATASETS.md`
- **Setup Help:** See `DATASET_SETUP.md`
- **Notebook Help:** See `HOW_TO_RUN_NOTEBOOKS.md`

---

## ⚠️ Common Issues

**Out of memory?**
```python
# In notebook 01, sample 10% of data:
df = df.sample(frac=0.1, random_state=42)
```

**Training too slow?**
```python
# In notebook 06, reduce trials:
n_trials=10  # Instead of 25-30
```

**No CSV files found?**
```bash
# Verify path:
ls data/raw/CICIoT2023/CSV/*.csv
```

---

## 🏁 You're All Set!

Run the notebooks in order and you'll have trained models in 3-5 hours.

**Questions?** Check the full documentation or troubleshooting sections in the guides.
