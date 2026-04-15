#!/usr/bin/env python3
"""Create GitHub repo and push ADADD code"""

import json
import os
import subprocess

# Read the token from cloud service (already connected)
# We'll use subprocess with git commands

REPO_NAME = "adadd"
DESCRIPTION = "ADADD - 广告行业资讯聚合平台 | Full-stack Ad Tech News Aggregator"
WORKSPACE = "/Users/mengjiachen/WorkBuddy/20260414101822"

def run(cmd, check=True):
    print(f"  $ {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=WORKSPACE)
    if r.stdout.strip():
        print(f"    {r.stdout.strip()[:200]}")
    if r.stderr.strip() and 'warning' not in r.stderr.lower() and 'hint' not in r.stderr.lower():
        print(f"    [stderr] {r.stderr.strip()[:200]}")
    if check and r.returncode != 0:
        raise Exception(f"Command failed: {cmd}\n{r.stderr}")
    return r

# Step 1: Init git repo
print("=== Step 1: Initialize Git Repository ===")
run("git init")
run('git config user.email "nelsonmeng@tencent.com"')
run('git config user.name "nelsonmeng"')

# Create .gitignore
gitignore = """__pycache__/
*.pyc
.venv/
*.egg-info/
dist/
build/
data/news_data.json.bak
*.log
.DS_Store
.env"""
with open(os.path.join(WORKSPACE, '.gitignore'), 'w') as f:
    f.write(gitignore)

print("\n=== Step 2: Stage all files ===")
run("git add -A")
result = run("git status --short", check=False)

print("\n=== Step 3: Create initial commit ===")
run('git commit -m "🎉 ADADD V2: Full-stack Ad Tech News Aggregator

Features:
- Flask REST API backend (/api/health, /api/news, /api/stats, /api/search, /api/sources)
- 203 full news items across 2016-2026 (7 sources, 30 categories)
- Dynamic search with real-time source URL generation
- Card view + Timeline view dual mode
- Tencent Blue theme (#0052D9) + Tencent Sans font
- Developer: nelsonmeng"', check=False)

# Check if we have gh CLI or need alternative
gh_available = False
try:
    r = subprocess.run("which gh", shell=True, capture_output=True)
    gh_available = r.returncode == 0
except:
    pass

if not gh_available:
    print("\n=== Note: gh CLI not installed ===")
    print("Please run manually:")
    print(f"  cd {WORKSPACE}")
    print("  gh repo create adadd --public --source=. --push")
    print("  OR create repo on github.com then:")
    print("  git remote add origin git@github.com:nelsonmeng/adadd.git")
    print("  git push -u origin main")
else:
    print("\n=== Step 4: Create GitHub Repo & Push ===")
    run("gh repo create adadd --public --source=. --push --description 'ADADD - 广告行业资讯聚合平台'")

print("\n✅ Done! Repository ready.")
