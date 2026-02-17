# %%

import pandas as pd
import os
from datetime import datetime
from datetime import timedelta
from concurrent.futures import ProcessPoolExecutor

# %%

def parseDuration(num, unit):
    duration = 0
    try:
        if unit == 'YR':
            duration = int(num) * 365
        elif unit == 'MON':
            duration = int(num) * 30
        elif unit == 'WK':
            duration = int(num) * 7
        elif unit == 'DAY':
            duration = int(num)
        elif unit == 'HR':
            duration = int(num) / 24
        elif unit == 'SEC':
            duration = int(num) / 86400
    except ValueError:
        # Handle the case where num is not a valid integer
        duration = 0
    
    if duration < 1:
        duration = 0
    duration = round(duration)

    return duration


def parseDate(start, end, num, unit):
    startDate = pd.NaT
    endDate = pd.NaT

    if pd.notna(start):
        start = str(int(start))
    if pd.notna(end):
        end = str(int(end))

    if pd.notna(start) and len(start) >= 4:  # Handle partial start dates
        try:
            startDate = datetime.strptime(start, '%Y%m%d'[:len(start)])
        except ValueError:
            startDate = pd.NaT

    if pd.notna(end) and len(end) >= 4:  # Handle partial end dates
        try:
            endDate = datetime.strptime(end, '%Y%m%d'[:len(end)])
        except ValueError:
            endDate = pd.NaT

    if pd.notna(startDate) and pd.isna(endDate) and num and unit:
        days = parseDuration(num, unit)
        endDate = startDate + timedelta(days=days)
    elif pd.notna(endDate) and pd.isna(startDate) and num and unit:
        days = parseDuration(num, unit)
        startDate = endDate - timedelta(days=days)

    return startDate, endDate

# %%

# Read in the processed file
cancer_patients_df = pd.read_csv('data/processed/cleaned/INDI_mapped.csv', sep='$')

# Read in the drug mapping file
drug_mapping_df = pd.read_csv('data/processed/drugs/drug_mapping.csv')

# Create maps from DrugName to DrugCategory and DetailedDrugCategory
drug_mapping_dict = dict(zip(drug_mapping_df['DrugName'], drug_mapping_df['DrugCategory']))
detailed_drug_mapping_dict = dict(zip(drug_mapping_df['DrugName'], drug_mapping_df['DetailedDrugCategory']))

# Extract cancer drug names and brand names
cancer_drug_names = set(drug_mapping_df['DrugName'].dropna().unique())
cancer_brand_names = set(drug_mapping_df['BrandName'].dropna().unique())

# Initialize an empty dataframe to store all cleaned drug data
all_drug_data = pd.DataFrame()

# %%

# Function to clean drug data for a specific quarter
def clean_drug_data_for_quarter(quarter, case_ids):
    
    year_suffix = quarter[2:]
    quarter_df = pd.read_csv(f'data/raw/FAERS_quarters/{quarter}/ASCII/DRUG{year_suffix}.TXT', sep='$', encoding_errors='ignore')
    quarter_df = quarter_df[quarter_df['caseid'].isin(case_ids)]

    quarter_therapies = pd.read_csv(f'data/raw/FAERS_quarters/{quarter}/ASCII/THER{year_suffix}.TXT', sep='$', encoding_errors='ignore', usecols=["caseid", "dsg_drug_seq", "start_dt", "end_dt", "dur", "dur_cod"])
    
    # Function to find the cancer drug name
    def find_cancer_drug(row):
        drugname = row['drugname']
        prod_ai = row.get('prod_ai', None)
        if pd.notna(drugname):
            drugname = drugname.upper()
        if pd.notna(prod_ai):
            prod_ai = prod_ai.upper()

        matched_drugs = set()

        if pd.notna(drugname) or pd.notna(prod_ai):
            for drug in cancer_drug_names:
                if (pd.notna(drugname) and drug in drugname) or (pd.notna(prod_ai) and drug in prod_ai):
                    matched_drugs.add(drug)
            for brand in cancer_brand_names:
                if (pd.notna(drugname) and brand in drugname) or (pd.notna(prod_ai) and brand in prod_ai):
                    # Find the associated drug name for the brand
                    associated_drug = drug_mapping_df[drug_mapping_df['BrandName'] == brand]['DrugName'].values
                    if len(associated_drug) > 0:
                        matched_drugs.add(associated_drug[0])

        if matched_drugs:
            return ','.join(matched_drugs)
        return ''
    
    # Apply the function to find the cancer drug name
    quarter_df['cancer_drug_name'] = quarter_df.apply(find_cancer_drug, axis=1)

    quarter_df = quarter_df[['caseid', 'drug_seq', 'role_cod', 'drugname', 'cancer_drug_name']]

    # Rename drugname to 'other_drug_name'
    quarter_df.rename(columns={'drugname': 'other_drug_name'}, inplace=True)
    
    # Update 'other_drug_name' based on 'cancer_drug_name'
    quarter_df['other_drug_name'] = quarter_df.apply(
        lambda row: "" if row['cancer_drug_name'] != "" else row['other_drug_name'], axis=1
    )

    # Function to map to drug category
    def map_to_drug_category(drugs, mapping_dict=drug_mapping_dict):
        if drugs == '':
            return ''
        drugs = drugs.split(',')
        drug_categories = set()
        for drug in drugs:
            if drug in mapping_dict:
                drug_categories.add(mapping_dict[drug])
        return ','.join(sorted(drug_categories)) if drug_categories else ''
    
    # Apply the mapping function
    quarter_df['drug_category'] = quarter_df['cancer_drug_name'].apply(map_to_drug_category, mapping_dict=drug_mapping_dict)
    quarter_df['detailed_drug_category'] = quarter_df['cancer_drug_name'].apply(map_to_drug_category, mapping_dict=detailed_drug_mapping_dict)

    # Merge therapies with drug data
    quarter_df = pd.merge(quarter_df, quarter_therapies, left_on=['caseid', 'drug_seq'], right_on=['caseid', 'dsg_drug_seq'], how='left')

    # Parse start and end dates
    quarter_df['start_dt'], quarter_df['end_dt'] = zip(*quarter_df.apply(lambda row: parseDate(row['start_dt'], row['end_dt'], row['dur'], row['dur_cod']), axis=1))

    # Drop unnecessary columns
    quarter_df.drop(columns=['dsg_drug_seq', 'dur', 'dur_cod'], inplace=True)

    return quarter_df

# %%

# Function to process each quarter
def process_quarter(quarter):
    case_ids = set(cancer_patients_df[cancer_patients_df['quarter'] == quarter]['caseid'].unique())
    return clean_drug_data_for_quarter(quarter, case_ids)

# %%

if __name__ == '__main__':

    # Process each quarter using multiprocessing
    quarters = cancer_patients_df['quarter'].unique()
    with ProcessPoolExecutor() as executor:
        results = executor.map(process_quarter, quarters)

    # Combine the results
    for cleaned_drug_data in results:
        all_drug_data = pd.concat([all_drug_data, cleaned_drug_data], ignore_index=True)

    # Ensure date columns are of datetime type
    all_drug_data['start_dt'] = pd.to_datetime(all_drug_data['start_dt'], format='%Y%m%d', errors='coerce')
    all_drug_data['end_dt'] = pd.to_datetime(all_drug_data['end_dt'], format='%Y%m%d', errors='coerce')

    # Format the date fields
    all_drug_data['start_dt'] = all_drug_data['start_dt'].dt.strftime('%Y-%m-%d')
    all_drug_data['end_dt'] = all_drug_data['end_dt'].dt.strftime('%Y-%m-%d')

    # Save the combined cleaned drug data to a new file
    all_drug_data.to_csv('data/processed/cleaned/DRUG_mapped.csv', sep='$', index=False)