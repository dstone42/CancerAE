#!/bin/bash

# Base URL for downloading the zip files
base_url="https://fis.fda.gov/content/Exports/faers_ascii_"
# Base directory for storing the downloaded files
base_dir="data/raw/FAERS_quarters"

# Function to download and process a single quarter
download_and_process() {
    year=$1
    quarter=$2

    quarter_dir="${base_dir}/${year}q${quarter}"

    # Skip if already downloaded
    if [ -d "$quarter_dir/ASCII" ]; then
        echo "Already downloaded: $quarter_dir"
        return 0
    fi

    file_url="${base_url}${year}q${quarter}.zip"
    file_name="faers_ascii_${year}q${quarter}.zip"

    # Create the directory for the quarter
    mkdir -p "$quarter_dir"

    # Download the zip file into the quarter directory
    echo "Downloading $file_url to $quarter_dir..."
    curl -f -o "${quarter_dir}/${file_name}" "$file_url"
    if [ $? -ne 0 ]; then
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

    # Rename files to uppercase if DEMO file is not found
    if [ ! -f "${quarter_dir}/ASCII/DEMO${year}.txt" ]; then
        for file in "${quarter_dir}/ASCII"/*; do
            mv "$file" "${quarter_dir}/ASCII/$(basename "$file" | tr '[:lower:]' '[:upper:]')"
        done
    fi

    # Special case for 2018Q1
    if [ "${year}q${quarter}" == "2018q1" ]; then
        mv "${quarter_dir}/ASCII/DEMO18Q1_NEW.txt" "${quarter_dir}/ASCII/DEMO18Q1.txt"
    fi

    # Remove the original zip file
    echo "Removing ${quarter_dir}/${file_name}..."
    rm "${quarter_dir}/${file_name}"
    return 0
}

start_year=2012
start_quarter=4
current_year=$(date +"%Y")

for year in $(seq $start_year $current_year); do
    for quarter in {1..4}; do
        # Skip quarters before 2012q4
        if [ "$year" -eq "$start_year" ] && [ "$quarter" -lt "$start_quarter" ]; then
            continue
        fi

        # Run the download and process function in the background
        download_and_process "$year" "$quarter" &
        wait $!
        # If download failed (no data), break out of the quarter loop for this year
        if [ $? -ne 0 ]; then
            break
        fi
    done
done

echo "All files downloaded, unzipped, and original zip files removed."