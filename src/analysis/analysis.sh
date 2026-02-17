#!/bin/bash

set -euo pipefail

# Frequency table
echo "Making frequency table..."
Rscript src/analysis/makeFreqTable.R
echo "Frequency table completed."

# Overlap coefficient
echo "Making overlap coefficient..."
Rscript src/analysis/makeOverlapCoefficient.R
echo "Overlap coefficient completed."

# Drug category stats
echo "Making drug category stats..."
python -m src.analysis.drug_category_stats
echo "Drug category stats completed."

# Cancer type stats
echo "Making cancer type stats..."
python -m src.analysis.cancer_type_stats
echo "Cancer type stats completed."