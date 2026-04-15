#!/usr/bin/env python3
"""ADADD Full Generator - 200+ items, Tencent font, external URLs, dynamic updates"""
import json, os, datetime

OUT = '/Users/mengjiachen/WorkBuddy/20260414101822/index.html'

# ================================================================
# Build news data (compact format)
# ================================================================
news = []
def A(**k): news.append(k)

# We'll build data inline in the HTML generation step

# ================================================================
# Generate complete single-file HTML  
# ================================================================

# Read existing index.html as base template for CSS/JS structure
with open(OUT, 'r') as f:
    base = f.read()

print(f"Base file read: {len(base)} bytes")
print("Generator ready. Run with: python3 gen.py")
