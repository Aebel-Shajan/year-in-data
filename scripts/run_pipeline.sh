#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# === CONFIG ===
PIPELINE_DIR="pipeline" 

# Set up environment (this assumes Python 3.10 is already available in your runner)
echo "📁 Navigating to $PIPELINE_DIR"
cd "$PIPELINE_DIR"

echo "📦 Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "🪠 Running pipeline..."
python main.py  

echo "✅ Pipeline run complete."