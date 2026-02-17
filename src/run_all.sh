#!/bin/bash

set -euo pipefail

# Run data preparation
echo "Starting data preparation..."
sh src/prep/prepare_data.sh
echo "Data preparation completed."

# Run analysis
echo "Starting analysis..."
sh src/analysis/analysis.sh
echo "Analysis completed."