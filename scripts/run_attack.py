#!/usr/bin/env python3
"""
Wrapper script to run attack generation from the scripts directory.
This adds the project root to the Python path and runs the attack generator.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import and run the attack generator
from tests.generate_anomalies import main

if __name__ == "__main__":
    main()
