#!/bin/bash

set -euo pipefail

# Run data preparation
echo "Starting data preparation..."
if bash src/prep/prepare_data.sh; then
	prep_status=0
else
	prep_status=$?
fi

if [ "$prep_status" -eq 10 ]; then
	echo "No new FAERS data detected. Exiting without running analysis."
	exit 0
fi

if [ "$prep_status" -ne 0 ]; then
	echo "Data preparation failed with status $prep_status"
	exit "$prep_status"
fi

echo "Data preparation completed."

# Run analysis
echo "Starting analysis..."
sh src/analysis/analysis.sh
echo "Analysis completed."