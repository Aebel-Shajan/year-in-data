#!/bin/bash
# Used for development.
set -e  # Exit immediately if a command exits with a non-zero status

PIPELINE_OUTPUTS_DIR="pipeline/data/output"
WEBSITE_ASSETS_DIR="website/public"

if [ -d $WEBSITE_ASSETS_DIR ]; then 
    echo "Copying pipeline outputs to $WEBSITE_ASSETS_DIR"
    mkdir -p $WEBSITE_ASSETS_DIR/assets/data
    cp -r $PIPELINE_OUTPUTS_DIR/* $WEBSITE_ASSETS_DIR/assets/data/
else
    echo "Expected assets folder to copy pipeline outputs into!"
fi

