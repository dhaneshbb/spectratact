#!/usr/bin/env python3
"""
SpectraTact - Module Entry Point
Copyright (c) 2025 dhaneshbb

Entry point for running SpectraTact as a module
Usage: python -m spectratact
"""

import os
import sys

# Add the src directory to Python path for proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)  # Go up one level to src
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from spectratact.main import main  # noqa: E402

if __name__ == "__main__":
    main()
