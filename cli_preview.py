#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compatibility wrapper for statusline.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statusline import main

if __name__ == "__main__":
    main()
