#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

switch_or_create_orphan_branch() {
  local branch="$1"

  git fetch

  if git show-ref --quiet refs/heads/"$branch"; then
    echo "Branch '$branch' exists. Switching to it."
    git reset --hard
    git switch "$branch"
  else
    echo "Branch '$branch' does not exist. Creating orphan branch."
    git reset --hard
    git switch --orphan "$branch"
    git reset --hard
  fi
}

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
switch_or_create_orphan_branch data-output

echo "Moving pipeline data output to ./data ..."
mkdir -p ./data/
mv ./pipeline/data/output/* ./data
mv ./data/metadata ./
git add ./data
git add ./metadata
echo $(ls)


echo "Commiting changes to git.."
git commit -m "Update pipeline output"
