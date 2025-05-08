#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Set up environment (this assumes Python 3.10 is already available in your runner)
cd pipeline

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Running pipeline..."
python main.py  

echo "Preparing to push output to data-output branch..."
cd ..
git config --global user.name "github-actions[bot]"
git config --global user.email "github-actions[bot]@users.noreply.github.com"
git checkout --orphan data-output-temp

echo "Moving pipeline data output to ./data ..."
mkdir -p ./data/
mv ./pipeline/data/output/* ./data
git restore --staged .
git add ./data
echo $(ls)

echo "Commiting changes to git.."
git commit -m "Update pipeline output"
echo "Pushing changes to repo..."
git push -f origin data-output-temp:data-output
