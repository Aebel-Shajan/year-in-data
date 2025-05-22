#!/bin/bash
set -e

# === CONFIG ===
BRANCH="gh-pages"
TMP_DIR="tmp-deploy" # Should be in .gitignore!
WEBSITE_BUILD_DIR="website/dist"
PIPELINE_OUTPUTS_DIR="pipeline/data/output"

# Delete local branch if exists
if git show-ref --quiet refs/heads/$BRANCH; then
    echo "🧹 Deleting existing local branch $BRANCH"
    git branch -D $BRANCH
fi

# Delete and recreate tmp dir
rm -rf $TMP_DIR
mkdir $TMP_DIR

# Create orphan branch and 
cd $TMP_DIR
git init
git checkout --orphan $BRANCH

# Copy folders into deploy folder

if [ -d "../$WEBSITE_BUILD_DIR" ]; then
    echo "copying $WEBSITE_BUILD_DIR/* to ./"
    cp -r ../$WEBSITE_BUILD_DIR/* ./
else
    echo "folder ../$WEBSITE_BUILD_DIR not found!"
fi

if [ -d "./assets" ]; then 
    echo "Copying pipeline outputs to  assets/data/"
    mkdir -p ./assets/data
    cp -r ../$PIPELINE_OUTPUTS_DIR/* ./assets/data/
else
    echo "Expected assets folder to copy pipeline outputs into!"
fi

 
# Commit changes
git add .
git commit -m "Deploy: $(date)"

# Connect to the main repo and push
git remote add origin "../.git"
git push --force origin $BRANCH

cd ..
rm -rf $TMP_DIR

echo "✅ Cleanly committed to '$BRANCH'"
