# %%

import pandas as pd

input_file = 'data/raw/drugs/targeted.txt'
output_file = 'data/processed/drugs/targeted.csv'
immunotherapies_file = 'data/raw/drugs/immunotherapies.csv'
targeted_antibodies_file = 'data/raw/drugs/targeted_antibodies.csv'
hormone_therapies_file = 'data/processed/drugs/hormone_therapies.csv'

# %%

# Read the additional files into dataframes
immunotherapies_df = pd.read_csv(immunotherapies_file)
targeted_antibodies_df = pd.read_csv(targeted_antibodies_file)
hormone_therapies_df = pd.read_csv(hormone_therapies_file)

# %%

# Combine the dataframes and convert to a set for fast lookup
existing_drugs = set(immunotherapies_df['drug'].str.upper()).union(set(targeted_antibodies_df['drug'].str.upper())).union(set(hormone_therapies_df['drug'].str.upper()))
existing_brand_names = set(immunotherapies_df['brand_name'].str.upper()).union(set(targeted_antibodies_df['brand_name'].str.upper())).union(set(hormone_therapies_df['brand_name'].str.upper()))

# %%

written_rows = set()

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    outfile.write("drug,brand_name,type\n")
    for line in infile:
        line = line.strip()
        if line and not line.startswith("Targeted therapy approved for"):
            if ' (' in line:
                drug, brand = line.split(' (')
                brand = brand.rstrip(')')
            else:
                drug = line
                brand = ''
            drug_upper = drug.upper().strip().replace(',', '')
            brand_upper = brand.upper().strip().replace(',', '')
            row = f"{drug_upper},{brand_upper},TARGETED"
            if drug_upper not in existing_drugs and brand_upper not in existing_brand_names and row not in written_rows:
                outfile.write(row + "\n")
                written_rows.add(row)