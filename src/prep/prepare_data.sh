#!/bin/bash

set -euo pipefail

# Download data
echo "Downloading data..."
sh src/prep/download_FAERS.sh
echo "Data download completed."

# Clean Cancer Types
echo "Cleaning cancer types..."
python src/prep/cancer_types/clean_cancer_types.py
echo "Cancer types cleaning completed."

# Clean AEs
echo "Cleaning adverse events..."
python src/prep/AEs/asco.py
python src/prep/AEs/clean_aes.py
python src/prep/AEs/clean_outcomes.py
echo "Adverse events cleaning completed."

# Clean Demographics
echo "Cleaning demographics..."
python src/prep/demographics/clean_demo.py
echo "Demographics cleaning completed."

# Clean Drugs
echo "Cleaning drugs..."
sh src/prep/drugs/clean_drug_field.sh
echo "Drugs cleaning completed."

# Time to Onset
echo "Adding time to onset..."
python src/prep/drugs/time_to_onset.py
echo "Time to onset added."

# Join Data
echo "Joining data..."
python src/prep/join_files.py
echo "Data joining completed."

# Format Data
echo "Formatting data..."
python src/prep/format_data.py
echo "Data formatting completed."