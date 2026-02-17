#!/bin/bash

set -euo pipefail

# Running hormone therapies script
echo "Starting hormone therapies processing..."
python3 src/prep/drugs/hormone_therapies.py
echo "Hormone therapies processing completed."

# Running targeted therapies script
echo "Starting targeted therapies processing..."
python3 src/prep/drugs/targeted_therapies.py
echo "Targeted therapies processing completed."

# Running drug mapping creation script
echo "Starting drug mapping creation..."
python3 src/prep/drugs/create_drug_mapping.py
echo "Drug mapping creation completed."

# Running drug field cleaning script
echo "Starting drug field cleaning..."
python3 src/prep/drugs/clean_drug_field.py
echo "Drug field cleaning completed."