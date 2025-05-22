#!/bin/bash
set -e  # Exit immediately if any command fails

# === CONFIG ===
WEBSITE_DIR="website"  # Change if your website lives elsewhere

echo "📁 Navigating to $WEBSITE_DIR"
cd "$WEBSITE_DIR"

echo "📦 Installing dependencies..."
npm install

echo "🏗 Building website..."
npm run build

echo "✅ Website build complete."