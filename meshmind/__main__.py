#!/usr/bin/env python3
"""
Entrypoint script: runs MeshMind CLI
"""
import os
import sys
# Add project root to path so imports within package work when running script
root = os.path.dirname(os.path.dirname(__file__))
if root not in sys.path:
    sys.path.insert(0, root)
from meshmind.cli.__main__ import main

if __name__ == "__main__":
    main()
