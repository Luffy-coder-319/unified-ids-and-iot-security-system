# How to Run the Training Notebooks

## Prerequisites

You have Python 3.12.3 installed. You need to install Jupyter and the required packages.

---

## Step 1: Install Jupyter Notebook

### Option A: Using pip (Recommended)
```bash
# Install Jupyter
python3 -m pip install --user jupyter notebook

# Or if you have pip working:
pip install jupyter notebook
```

### Option B: Using conda (if you have Anaconda/Miniconda)
```bash
conda install jupyter notebook
```

---

## Step 2: Install Required Dependencies

Make sure all required packages from `requirements.txt` are installed:

```bash
# Navigate to project directory
cd /mnt/d/project/unified-ids-and-iot-security-system

# Install all dependencies
python3 -m pip install --user -r requirements.txt

# Install Optuna (for improved hyperparameter tuning)
python3 -m pip install --user optuna
```

**Key packages needed:**
- pandas
- numpy
- scikit-learn
- tensorflow
- xgboost
- lightgbm
- imbalanced-learn
- matplotlib
- seaborn
- joblib
- optuna (new requirement)

---

## Step 3: Launch Jupyter Notebook

### Method 1: Start Jupyter Server

```bash
# Navigate to project directory
cd /mnt/d/project/unified-ids-and-iot-security-system

# Start Jupyter Notebook
jupyter notebook

# Or if the command is not found:
python3 -m notebook
```

This will:
1. Start a Jupyter server
2. Open your default browser to `http://localhost:8888`
3. Show the file browser

### Method 2: Use VSCode (You Already Have It Open!)

Since you're using VSCode (I can see you opened the notebook file):

1. **Click on the notebook file** in VSCode explorer
   - `notebooks/02_advanced_preprocessing_and_feature_engineering.ipynb`

2. **VSCode will open it in notebook mode**

3. **Select Python Kernel**
   - Click "Select Kernel" in top-right
   - Choose your Python 3.12.3 environment

4. **Run cells**
   - Click the ▶️ play button next to each cell
   - Or use `Shift + Enter` to run cell and move to next

---

## Step 4: Run Notebooks in Order

**IMPORTANT**: Run notebooks in this specific order (each depends on previous outputs):

```bash
1. notebooks/01_data_consolidation_and_label_engineering.ipynb
2. notebooks/02_advanced_preprocessing_and_feature_engineering.ipynb  ← Start here
3. notebooks/03_addressing_class_imbalance.ipynb
4. notebooks/04_baseline_model_and_evaluation.ipynb
5. notebooks/05_deep_learning_model_development.ipynb
6. notebooks/06_hyperparameter_tuning_and_optimization.ipynb
7. notebooks/07_model_comparison_dashboard.ipynb
```

### Running Order Explained

**Notebook 01** → Consolidates raw CICIDS2017 CSV files
- Input: `data/raw/CICIDS2017/*.csv`
- Output: `data/processed/CICIDS2017/combined.csv`

**Notebook 02** → Feature engineering and scaling
- Input: `data/processed/CICIDS2017/combined.csv`
- Output: `data/processed/ml_ready/X_train_*.csv`, `y_train.csv`, etc.

**Notebook 03** → Address class imbalance
- Input: `data/processed/ml_ready/X_train_standard.csv`
- Output: `data/processed/ml_balance/train_*.csv`, `class_weights.pkl`

**Notebook 04** → Train baseline models
- Input: `data/processed/ml_balance/train_balanced.csv`
- Output: `trained_models/best_baseline.pkl`

**Notebook 05** → Train deep learning models
- Input: `data/processed/ml_balance/train_balanced.csv`
- Output: `trained_models/dl_models/final_*.keras`

**Notebook 06** → Hyperparameter tuning with Optuna
- Input: `data/processed/ml_balance/train_original.csv`
- Output: `trained_models/final_*_optuna.pkl`

**Notebook 07** → Compare all models + ensembles
- Input: All trained models from notebooks 04-06
- Output: `model_comparison_enhanced.csv`, dashboard visualizations

---

## Quick Start Guide (VSCode Method)

Since you already have VSCode open:

1. **Install Jupyter extension in VSCode** (if not already installed)
   ```
   Extensions (Ctrl+Shift+X) → Search "Jupyter" → Install
   ```

2. **Install Python dependencies**
   ```bash
   cd /mnt/d/project/unified-ids-and-iot-security-system
   python3 -m pip install --user -r requirements.txt
   python3 -m pip install --user optuna jupyter
   ```

3. **Open notebook in VSCode**
   - You already have `02_advanced_preprocessing_and_feature_engineering.ipynb` open
   - But you should start with notebook 01 first!

4. **Run cells sequentially**
   - Click "Run All" button at top, OR
   - Click ▶️ next to each cell, OR
   - Press `Shift + Enter` for each cell

---

## Alternative: Run Notebooks as Python Scripts

If you prefer command-line execution:

```bash
# Convert notebook to Python script
jupyter nbconvert --to script notebooks/02_advanced_preprocessing_and_feature_engineering.ipynb

# Run the script
python3 notebooks/02_advanced_preprocessing_and_feature_engineering.py
```

---

## Troubleshooting

### Issue: "Jupyter not found"
```bash
# Make sure pip is working
python3 -m ensurepip --default-pip

# Install Jupyter
python3 -m pip install --user jupyter notebook
```

### Issue: "No module named 'sklearn'"
```bash
# Install scikit-learn
python3 -m pip install --user scikit-learn
```

### Issue: "No module named 'tensorflow'"
```bash
# Install TensorFlow
python3 -m pip install --user tensorflow
```

### Issue: "Kernel not found" in VSCode
```bash
# Install ipykernel
python3 -m pip install --user ipykernel

# Register kernel
python3 -m ipykernel install --user --name=python3
```

### Issue: Out of Memory
```bash
# Reduce batch size in notebooks
# Or use a subset of data for testing
```

---

## Expected Runtime

| Notebook | Estimated Time | Notes |
|----------|---------------|-------|
| 01 | 5-10 min | Depends on data size |
| 02 | 3-5 min | Feature engineering |
| 03 | 5-15 min | SMOTE can be slow |
| 04 | 20-40 min | Multiple models |
| 05 | 30-60 min | Deep learning (with early stopping) |
| 06 | 40-90 min | Optuna optimization |
| 07 | 20-40 min | Ensemble training |
| **TOTAL** | **2-4 hours** | Run overnight if needed |

---

## Tips for Faster Execution

1. **Use GPU for Deep Learning** (Notebook 05)
   ```bash
   # Check if GPU is available
   python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
   ```

2. **Reduce Optuna Trials** (Notebook 06)
   - Change `n_trials=25` to `n_trials=10` for testing

3. **Use Smaller Dataset** (for testing)
   - Sample data in Notebook 01: `df = df.sample(frac=0.1)`

4. **Run in Background**
   ```bash
   # Run notebook and save output
   jupyter nbconvert --to notebook --execute notebooks/02_*.ipynb --output output.ipynb
   ```

---

## Monitoring Progress

### In Jupyter Notebook
- Look for `[*]` next to cell = running
- Look for `[number]` = completed
- Check output below each cell

### In VSCode
- Progress bar appears for running cells
- Output appears below each cell
- Check bottom status bar for kernel status

---

## After Running All Notebooks

Check these output files:

```bash
# View model comparison
cat trained_models/model_comparison_enhanced.csv

# View best model results
ls -lh trained_models/*.pkl
ls -lh trained_models/dl_models/*.keras

# View visualizations
open trained_models/model_comparison_dashboard.png
open trained_models/per_class_performance.png
```

---

## Quick Command Reference

```bash
# Install everything
python3 -m pip install --user jupyter notebook optuna -r requirements.txt

# Start Jupyter
jupyter notebook

# Or use VSCode (just open .ipynb files)
code notebooks/

# Convert to script
jupyter nbconvert --to script notebook.ipynb

# Run notebook from command line
jupyter nbconvert --to notebook --execute notebook.ipynb
```

---

## Need Help?

- **Jupyter docs**: https://jupyter.org/documentation
- **VSCode Jupyter**: https://code.visualstudio.com/docs/datascience/jupyter-notebooks
- **Requirements issues**: Check `requirements.txt` and install missing packages

---

**Ready to start?**

```bash
# 1. Install dependencies
python3 -m pip install --user jupyter optuna -r requirements.txt

# 2. Open VSCode and run notebooks 01-07 in order
# OR start Jupyter server:
jupyter notebook
```
