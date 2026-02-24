#!/bin/bash

set -euo pipefail

# Base URL for downloading the zip files
base_url="https://fis.fda.gov/content/Exports/faers_ascii_"
# Base directory for storing the downloaded files
base_dir="data/raw/FAERS_quarters"
any_new_data=0

# Function to download and process a single quarter
download_and_process() {
    year=$1
    quarter=$2

    quarter_dir="${base_dir}/${year}q${quarter}"

    # Skip if already downloaded
    if [ -d "$quarter_dir/ASCII" ]; then
        echo "Already downloaded: $quarter_dir"
        return 2
    fi

    file_url="${base_url}${year}q${quarter}.zip"
    file_name="faers_ascii_${year}q${quarter}.zip"

    # Create the directory for the quarter
    mkdir -p "$quarter_dir"

    # Download the zip file into the quarter directory
    echo "Downloading $file_url to $quarter_dir..."
    if ! curl -f -o "${quarter_dir}/${file_name}" "$file_url"; then
        echo "No data available for ${year}q${quarter}. Stopping for this year."
        rm -rf "$quarter_dir"
        return 1
    fi

    echo "Unzipping ${quarter_dir}/${file_name}..."
    unzip "${quarter_dir}/${file_name}" -d "$quarter_dir"
    
    # Ensure the ASCII directory is properly named
    if [ ! -d "${quarter_dir}/ASCII" ]; then
        mv "${quarter_dir}/ascii" "${quarter_dir}/ASCII"
    fi

    # Normalize file naming to uppercase without failing on already-uppercase files
    for file in "${quarter_dir}/ASCII"/*; do
        upper_file="${quarter_dir}/ASCII/$(basename "$file" | tr '[:lower:]' '[:upper:]')"
        if [ "$file" != "$upper_file" ]; then
            mv "$file" "$upper_file"
        fi
    done

    # Special case for 2018Q1
    if [ "${year}q${quarter}" == "2018q1" ]; then
        if [ -f "${quarter_dir}/ASCII/DEMO18Q1_NEW.TXT" ] && [ ! -f "${quarter_dir}/ASCII/DEMO18Q1.TXT" ]; then
            mv "${quarter_dir}/ASCII/DEMO18Q1_NEW.TXT" "${quarter_dir}/ASCII/DEMO18Q1.TXT"
        fi
    fi

    # Remove the original zip file
    echo "Removing ${quarter_dir}/${file_name}..."
    rm "${quarter_dir}/${file_name}"
    return 0
}

start_year=2012
start_quarter=4
current_year=$(date +"%Y")
current_month=$(date +"%m")
current_quarter=$(( (10#$current_month - 1) / 3 + 1 ))

check_only=0
if [ "${1:-}" = "--check-only" ]; then
    check_only=1
fi

if [ "$check_only" -eq 1 ]; then
    candidate=""
    for year in $(seq $start_year $current_year); do
        max_quarter=4
        if [ "$year" -eq "$current_year" ]; then
            max_quarter=$current_quarter
        fi

        for quarter in $(seq 1 $max_quarter); do
            if [ "$year" -eq "$start_year" ] && [ "$quarter" -lt "$start_quarter" ]; then
                continue
            fi

            quarter_dir="${base_dir}/${year}q${quarter}"
            if [ ! -d "$quarter_dir/ASCII" ]; then
                candidate="${year}q${quarter}"
                break 2
            fi
        done
    done

    if [ -z "$candidate" ]; then
        echo "No missing expected quarter found; no new data expected right now."
        exit 10
    fi

    file_url="${base_url}${candidate}.zip"
    if curl -sfI "$file_url" >/dev/null; then
        echo "New data appears available for $candidate"
        exit 0
    fi

    echo "No new data available yet for $candidate"
    exit 10
fi

for year in $(seq $start_year $current_year); do
    max_quarter=4
    if [ "$year" -eq "$current_year" ]; then
        max_quarter=$current_quarter
    fi

    for quarter in $(seq 1 $max_quarter); do
        # Skip quarters before 2012q4
        if [ "$year" -eq "$start_year" ] && [ "$quarter" -lt "$start_quarter" ]; then
            continue
        fi

        if download_and_process "$year" "$quarter"; then
            status=0
        else
            status=$?
        fi

        if [ "$status" -eq 0 ]; then
            any_new_data=1
        elif [ "$status" -eq 1 ]; then
            break
        fi
    done
done

echo "All files downloaded, unzipped, and original zip files removed."

if [ "$any_new_data" -eq 0 ]; then
    echo "No new FAERS quarter was downloaded."
    exit 10
fi

exit 0