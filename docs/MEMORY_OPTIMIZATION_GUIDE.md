# Memory Optimization Guide

## Problem
When processing the CIC-IoT-2023 dataset (~46.6 million rows, 47 columns), you may encounter `MemoryError` due to high memory requirements (16+ GB for operations like `dropna()`).

## Solutions Implemented

### 1. **Data Type Optimization**
- Load numeric data as `float32` instead of `float64` (saves 50% memory)
- Use appropriate integer types (`int8`, `int16`, `int32`) based on value ranges
- Expected memory reduction: **50-60%**

### 2. **Memory Monitoring**
Added utilities to track memory usage:
```python
import psutil

def get_memory_usage():
    """Get current process memory in GB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024**3
```

### 3. **Garbage Collection**
- Explicitly delete large objects after use (`del dfs`)
- Call `gc.collect()` periodically during data loading
- Clear memory between processing steps

### 4. **Avoid Unnecessary Copies**
- Replace `df.dropna(inplace=True)` with masked filtering
- Use boolean indexing to avoid intermediate copies

### 5. **Install Required Package**
```bash
pip install psutil
```

## Memory Estimates

| Dataset Size | Original (float64) | Optimized (float32) |
|--------------|-------------------|---------------------|
| 46M rows, 47 cols | ~16 GB | ~8 GB |

## Alternative Approaches

If you still encounter memory issues:

### Option A: Process in Chunks
```python
# Save to parquet with chunking
chunk_size = 1_000_000
for i, chunk_df in enumerate(pd.read_csv('data.csv', chunksize=chunk_size)):
    chunk_df.to_parquet(f'data_chunk_{i}.parquet')
```

### Option B: Use Dask for Out-of-Core Processing
```python
import dask.dataframe as dd

# Load with Dask (lazy evaluation)
df = dd.read_csv('data/*.csv', dtype=np.float32)
df = df.dropna()
df.to_parquet('output/', engine='pyarrow')
```

### Option C: Sample the Dataset
For development/testing:
```python
# Load only a fraction of data
df = pd.read_csv('data.csv', skiprows=lambda i: i > 0 and np.random.rand() > 0.1)
```

## Best Practices

1. **Monitor memory** before and after each major operation
2. **Use profiling** to identify memory bottlenecks:
   ```python
   %load_ext memory_profiler
   %memit df.dropna()
   ```
3. **Close/restart kernel** between runs to clear memory
4. **Use 64-bit Python** (32-bit limited to ~2-4GB)
5. **Increase swap space** if RAM is limited (slower but prevents crashes)

## System Requirements

**Recommended:**
- RAM: 16 GB minimum, 32 GB recommended
- Python: 64-bit version
- OS: Enable virtual memory/swap

**Minimum (with optimizations):**
- RAM: 8-12 GB
- Virtual memory: 16+ GB

## Troubleshooting

### Still getting MemoryError?
1. Check available RAM: `psutil.virtual_memory().available`
2. Close other applications
3. Process dataset in smaller chunks
4. Use Dask for distributed computing
5. Consider cloud computing (AWS, GCP, Azure) with larger instances

### Slow performance?
- Ensure you're using SSD (not HDD)
- Enable swap on SSD
- Use `pyarrow` engine for parquet files
- Consider sampling for development

## Notebook-Specific Optimizations

All notebooks now include memory optimization utilities. Here's what was added to each:

### Notebook 01: Data Consolidation and Label Engineering
**Memory Impact:** CRITICAL (processes 46M+ rows)
- ✅ Smart CSV loading with dtype detection
- ✅ Uses `float32` for numeric columns
- ✅ Memory-efficient dropna() without copies
- ✅ Garbage collection during file loading
- **Expected memory usage:** ~8-10 GB

### Notebook 02: Advanced Preprocessing & Feature Engineering
**Memory Impact:** HIGH (train/test split, scaling, correlation)
- ✅ Memory monitoring utilities added
- ✅ Reads processed data with `float32`
- ✅ Correlation matrix on training set only
- ⚠️ **Tip:** Correlation computation can be memory-intensive. If issues occur, compute on a sample first
- **Expected memory usage:** ~6-8 GB

### Notebook 03: Addressing Class Imbalance
**Memory Impact:** HIGH (SMOTE creates synthetic samples)
- ✅ Memory monitoring utilities added
- ✅ Uses `float32` for all data loading
- ✅ Moderate SMOTE strategy (not aggressive)
- ⚠️ **Tip:** SMOTE can double/triple dataset size. Monitor memory before/after
- **Expected memory usage:** ~8-12 GB (due to SMOTE)

### Notebook 04: Baseline Model and Evaluation
**Memory Impact:** MEDIUM (model training)
- ✅ Memory monitoring utilities added
- ✅ Loads data as `float32`
- ⚠️ **Tip:** Random Forest with many trees can use significant memory. Limit `n_estimators` if needed
- **Expected memory usage:** ~4-6 GB

### Notebook 05: Deep Learning Model Development
**Memory Impact:** HIGH (neural network training)
- ✅ Memory monitoring utilities added
- ✅ Data loaded as `float32`
- ⚠️ **Tip:** TensorFlow/PyTorch can use GPU memory. Monitor both RAM and VRAM
- ⚠️ **Tip:** Use batch training instead of loading entire dataset
- **Expected memory usage:** ~6-10 GB RAM + GPU memory

### Notebook 06: Hyperparameter Tuning and Optimization
**Memory Impact:** VERY HIGH (multiple model instances)
- ✅ Memory monitoring utilities added
- ✅ Data loaded as `float32`
- ⚠️ **Warning:** Grid search creates many model copies
- ⚠️ **Tip:** Use `n_jobs=1` if memory is tight (slower but safer)
- ⚠️ **Tip:** Reduce `cv` folds (e.g., 3 instead of 5) to save memory
- **Expected memory usage:** ~8-16 GB

### Notebook 07: Model Comparison Dashboard
**Memory Impact:** MEDIUM (loading saved models)
- ✅ Memory monitoring utilities added
- ⚠️ **Tip:** Load models one at a time, evaluate, then delete
- **Expected memory usage:** ~4-8 GB

## Memory Monitoring Tips

### Check memory in notebooks:
```python
print(f"Current memory: {get_memory_usage():.2f} GB")
print(f"Available RAM: {psutil.virtual_memory().available / 1024**3:.1f} GB")
```

### Before memory-intensive operations:
```python
# Free memory
import gc
gc.collect()

# Check what's using memory
import sys
for name, obj in locals().items():
    if hasattr(obj, '__len__'):
        print(f"{name}: {sys.getsizeof(obj) / 1024**2:.2f} MB")
```

### Monitor during SMOTE:
```python
print(f"Before SMOTE: {get_memory_usage():.2f} GB")
X_res, y_res = smote.fit_resample(X_train, y_train)
print(f"After SMOTE: {get_memory_usage():.2f} GB")
```

## Modified Files
- `notebooks/01_data_consolidation_and_label_engineering.ipynb` - Memory-optimized data loading
- `notebooks/02_advanced_preprocessing_and_feature_engineering.ipynb` - Added memory utilities
- `notebooks/03_addressing_class_imbalance.ipynb` - Added memory utilities
- `notebooks/04_baseline_model_and_evaluation.ipynb` - Added memory utilities
- `notebooks/05_deep_learning_model_development.ipynb` - Added memory utilities
- `notebooks/06_hyperparameter_tuning_and_optimization.ipynb` - Added memory utilities
- `notebooks/07_model_comparison_dashboard.ipynb` - Added memory utilities
- `requirements.txt` - Added `psutil` dependency
- `add_memory_optimization.py` - Script to add memory utils to notebooks
