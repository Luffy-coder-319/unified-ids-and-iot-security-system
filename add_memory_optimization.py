#!/usr/bin/env python3
"""
Add memory optimization utilities to Jupyter notebooks
"""
import json
from pathlib import Path

# Memory utilities cell to be added
MEMORY_UTILS_CELL = {
    "cell_type": "code",
    "id": "memory_utils_cell",
    "metadata": {},
    "execution_count": None,
    "outputs": [],
    "source": [
        "# ===================================================================\n",
        "# Memory Optimization Utilities\n",
        "# ===================================================================\n",
        "import psutil\n",
        "import gc\n",
        "\n",
        "def get_memory_usage():\n",
        "    \"\"\"Get current memory usage in GB\"\"\"\n",
        "    process = psutil.Process()\n",
        "    return process.memory_info().rss / 1024**3\n",
        "\n",
        "def optimize_dtypes(df):\n",
        "    \"\"\"Reduce memory usage by optimizing data types\"\"\"\n",
        "    print(\"\\nOptimizing data types...\")\n",
        "    start_mem = df.memory_usage(deep=True).sum() / 1024**3\n",
        "    print(f\"  Initial memory: {start_mem:.2f} GB\")\n",
        "    \n",
        "    for col in df.columns:\n",
        "        col_type = df[col].dtype\n",
        "        \n",
        "        if col_type != object:\n",
        "            c_min = df[col].min()\n",
        "            c_max = df[col].max()\n",
        "            \n",
        "            if str(col_type)[:3] == 'int':\n",
        "                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:\n",
        "                    df[col] = df[col].astype(np.int8)\n",
        "                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:\n",
        "                    df[col] = df[col].astype(np.int16)\n",
        "                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:\n",
        "                    df[col] = df[col].astype(np.int32)\n",
        "            else:\n",
        "                if c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:\n",
        "                    df[col] = df[col].astype(np.float32)\n",
        "    \n",
        "    end_mem = df.memory_usage(deep=True).sum() / 1024**3\n",
        "    saved = start_mem - end_mem\n",
        "    print(f\"  Final memory: {end_mem:.2f} GB\")\n",
        "    print(f\"  Saved: {saved:.2f} GB ({100 * saved / start_mem:.1f}%)\")\n",
        "    \n",
        "    return df\n",
        "\n",
        "print(f\"System RAM: {psutil.virtual_memory().total / 1024**3:.1f} GB\")\n",
        "print(f\"Available RAM: {psutil.virtual_memory().available / 1024**3:.1f} GB\")\n",
        "print(f\"Current process memory: {get_memory_usage():.2f} GB\")"
    ]
}

def add_import_to_cell(cell, imports_to_add):
    """Add imports to an existing cell if not already present"""
    source = ''.join(cell.get('source', []))

    for imp in imports_to_add:
        if imp not in source:
            # Add to the end of imports section
            cell['source'].extend([f'{imp}\n'])

    return cell

def add_memory_utils_to_notebook(notebook_path, force=False):
    """Add memory optimization utilities to a notebook"""

    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # Check if memory utils already exist
    has_memory_utils = any(
        'get_memory_usage' in ''.join(cell.get('source', []))
        for cell in nb['cells']
    )

    if has_memory_utils and not force:
        print(f"  >>  {notebook_path.name}: Already has memory utils")
        return False

    # Find the first code cell with imports
    first_import_idx = None
    for i, cell in enumerate(nb['cells']):
        if cell.get('cell_type') == 'code':
            source_list = cell.get('source', [])
            if isinstance(source_list, str):
                source_list = [source_list]
            source = ''.join(source_list)
            if 'import' in source:
                first_import_idx = i
                break

    if first_import_idx is None:
        print(f"  !  {notebook_path.name}: No import cell found, skipping")
        return False

    # Add psutil and gc imports to the first import cell
    import_cell = nb['cells'][first_import_idx]

    # Handle both list and string source formats
    if isinstance(import_cell['source'], str):
        import_cell['source'] = [import_cell['source']]

    source = ''.join(import_cell.get('source', []))

    needs_psutil = 'psutil' not in source
    needs_gc = 'import gc' not in source

    if needs_psutil or needs_gc:
        if needs_psutil:
            import_cell['source'].append('import psutil\n')
        if needs_gc:
            import_cell['source'].append('import gc\n')

    # Insert memory utils cell after imports
    nb['cells'].insert(first_import_idx + 1, MEMORY_UTILS_CELL.copy())

    # Save notebook
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print(f"  [OK]  {notebook_path.name}: Added memory optimization utilities")
    return True

def optimize_read_csv_calls(notebook_path):
    """Optimize pd.read_csv calls to use dtype=float32"""

    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    modified = False

    for cell in nb['cells']:
        if cell.get('cell_type') != 'code':
            continue

        source = cell.get('source', [])
        new_source = []

        for line in source:
            # Check if line has pd.read_csv without dtype or with dtype=float64
            if 'pd.read_csv' in line or 'read_csv' in line:
                # Add .astype("float32") after read_csv if not already present
                if '.astype(' not in line and 'dtype=' not in line:
                    line = line.rstrip()
                    if line.endswith(')'):
                        # Simple case: pd.read_csv(...)
                        line = line[:-1] + ', dtype=np.float32)\n'
                        modified = True
                    else:
                        # Multi-line case, leave as is
                        new_source.append(line if line.endswith('\n') else line + '\n')
                        continue

            new_source.append(line if line.endswith('\n') else line + '\n')

        cell['source'] = new_source

    if modified:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)

        print(f"  [OK]  {notebook_path.name}: Optimized read_csv calls")
        return True

    return False

def main():
    notebooks_dir = Path('notebooks')

    # Notebooks that need memory optimization
    notebooks_to_optimize = [
        '02_advanced_preprocessing_and_feature_engineering.ipynb',
        '03_addressing_class_imbalance.ipynb',
        '04_baseline_model_and_evaluation.ipynb',
        '05_deep_learning_model_development.ipynb',
        '06_hyperparameter_tuning_and_optimization.ipynb',
    ]

    print("Adding memory optimization to notebooks...\n")

    for nb_name in notebooks_to_optimize:
        nb_path = notebooks_dir / nb_name

        if not nb_path.exists():
            print(f"  ⚠  {nb_name}: Not found")
            continue

        try:
            # Add memory utilities
            add_memory_utils_to_notebook(nb_path)

        except Exception as e:
            print(f"  X  {nb_name}: Error - {e}")

    print("\nMemory optimization complete!")

if __name__ == '__main__':
    main()
