# %%

import pandas as pd
import os
import json

# Paths to the files
indications = 'data/processed/cleaned/INDI_mapped.csv'
faers_quarters_path = 'data/raw/FAERS_quarters'
meddra_file_path = 'data/raw/AEs/MedDRA_28_0_English/MedAscii/pt.asc'

# %%

# Read the cleaned file
cancer_cases = pd.read_csv(indications, sep='$')

# Read the MedDRA files
meddra_df = pd.read_csv(meddra_file_path, delimiter='$', names=['pt_code', 'pt_name', 'soc_code'], usecols=[0,1,3])
meddra_hlt = pd.read_csv('data/raw/AEs/MedDRA_28_0_English/MedAscii/hlt_pt.asc', delimiter='$', names=['hlt_code', 'pt_code'], usecols=[0,1])
meddra_hlgt = pd.read_csv('data/raw/AEs/MedDRA_28_0_English/MedAscii/hlgt_hlt.asc', delimiter='$', names=['hlgt_code', 'hlt_code'], usecols=[0,1])

meddra_hlt_dict = dict(zip(meddra_hlt['pt_code'], meddra_hlt['hlt_code']))
meddra_hlgt_dict = dict(zip(meddra_hlgt['hlt_code'], meddra_hlgt['hlgt_code']))

meddra_pt_dict = dict(zip(meddra_df['pt_name'], meddra_df['pt_code']))
meddra_soc_dict = dict(zip(meddra_df['pt_name'], meddra_df['soc_code']))

# Create a reverse mapping for MedDRA codes to names
meddra_pt_dict_reverse = {v: k for k, v in meddra_pt_dict.items()}

# Read the CTCAE file
ctcae_df = pd.read_excel('data/raw/AEs/CTCAE_v5.0.xlsx', sheet_name='CTCAE v5.0 Clean Copy')

# Filter out rows where MedDRA SOC is in list of unwanted SOCs
unwanted_socs = ['Congenital, familial and genetic disorders', 'Injury, poisoning and procedural complications', 'Investigations', 'Pregnancy, puerperium and perinatal conditions', 'Social circumstances', 'Surgical and medical procedures']
ctcae_df = ctcae_df[~ctcae_df['MedDRA SOC'].isin(unwanted_socs)]

ctcae_dict = dict(zip(ctcae_df['MedDRA Code'], ctcae_df['CTCAE Term']))

ctcae_meddra_soc_dict = dict(zip(ctcae_df['CTCAE Term'], ctcae_df['MedDRA SOC']))

# Read the ASCO file
asco_df = pd.read_csv('data/processed/AEs/ASCO_with_Meddra.csv')

# Create a mapping from Meddra terms to ASCO terms
asco_meddra_dict = dict(zip(asco_df['Meddra Term'], asco_df['Adverse Event']))

# %%

# Function to process each quarter
def process_quarter(quarter):

    quarter_cancer_cases = cancer_cases[cancer_cases['quarter'] == quarter]
    quarter_cancer_cases_set = set(quarter_cancer_cases['caseid'])

    year_suffix = quarter[2:]
    reac_file_path = os.path.join(faers_quarters_path, quarter, 'ASCII', f'REAC{year_suffix}.TXT')

    reac_df = pd.read_csv(reac_file_path, delimiter='$', usecols=['caseid', 'pt'])
    # Filter to rows that are cancer cases
    cancer_reac_df = reac_df[reac_df['caseid'].isin(quarter_cancer_cases_set)]

    # Add meddra codes to cancer_reac_df
    cancer_reac_df['pt_code'] = cancer_reac_df['pt'].map(meddra_pt_dict)
    cancer_reac_df['soc_code'] = cancer_reac_df['pt'].map(meddra_soc_dict)

    cancer_reac_df['hlt_code'] = cancer_reac_df['pt_code'].map(meddra_hlt_dict)
    cancer_reac_df['hlgt_code'] = cancer_reac_df['hlt_code'].map(meddra_hlgt_dict)
    
    # Map CTCAE Term based on meddra codes
    cancer_reac_df['CTCAE Term'] = cancer_reac_df['pt_code'].map(ctcae_dict)
    cancer_reac_df['CTCAE Term'].fillna(cancer_reac_df['hlt_code'].map(ctcae_dict), inplace=True)
    cancer_reac_df['CTCAE Term'].fillna(cancer_reac_df['hlgt_code'].map(ctcae_dict), inplace=True)
    cancer_reac_df['CTCAE Term'].fillna(cancer_reac_df['soc_code'].map(ctcae_dict), inplace=True)

    # Map MedDRA SOC based on CTCAE Term
    cancer_reac_df['MedDRA SOC'] = cancer_reac_df['CTCAE Term'].map(ctcae_meddra_soc_dict)

    # Map ASCO terms based on MedDRA terms
    cancer_reac_df['irAE'] = cancer_reac_df['pt'].map(asco_meddra_dict)

    return cancer_reac_df

# %%

# Process each quarter and collect results
results = []
for quarter in cancer_cases['quarter'].unique():
    results.append(process_quarter(quarter))

# %%

# Concatenate all results
final_results = pd.concat(results, ignore_index=True)

# %%

final_results = final_results[['caseid', 'CTCAE Term', 'MedDRA SOC', 'irAE']]
# Rename columns
final_results.columns = ['caseid', 'AE', 'AE_Category', 'irAE']

# %%

# Remove commas from the AE and AE_Category columns
final_results['AE'] = final_results['AE'].str.replace(',', '', regex=False)
final_results['AE_Category'] = final_results['AE_Category'].str.replace(',', '', regex=False)

# %%

# Output the results
final_results.to_csv('data/processed/cleaned/REAC_mapped.csv', sep='$', index=False)


# %%
