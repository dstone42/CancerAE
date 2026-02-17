
# %%

import pandas as pd

def collapse_dataframe(df, group_by_column):
    """
    Collapse a DataFrame by grouping on a column and concatenating other column values into a comma-separated list.
    """
    return df.groupby(group_by_column).agg(lambda x: ','.join(sorted(set(val for val in x.astype(str) if val != '')))).reset_index()

# Load data frames
DRUG = pd.read_csv('data/processed/cleaned/DRUG_mapped.csv', sep = '$', usecols=['caseid', 'other_drug_name', 'cancer_drug_name', 'drug_category', 'detailed_drug_category'])
INDI = pd.read_csv('data/processed/cleaned/INDI_mapped.csv', sep = '$', usecols=['caseid', 'cancerType', 'quarter'])
OUTC = pd.read_csv('data/processed/cleaned/OUTC_mapped.csv', sep = '$')
REAC = pd.read_csv('data/processed/cleaned/REAC_mapped.csv', sep = '$')
DEMO = pd.read_csv('data/processed/cleaned/DEMO_mapped.csv', sep = '$')

# Fill NaN values with empty strings
DRUG.fillna('', inplace=True)
INDI.fillna('', inplace=True)
REAC.fillna('', inplace=True)

# %%

print('read in data')

# Collapse the data frames
collapsed_DRUG = collapse_dataframe(DRUG, 'caseid')
print('collapsed drug')

# %%

collapsed_INDI = collapse_dataframe(INDI, 'caseid')
print('collapsed indi')

# %%

collapsed_REAC = collapse_dataframe(REAC, 'caseid')
print('collapsed reac')

# %%

# OUTC and DEMO do not need collapsing as they have one row per caseid
# Merge the data frames on caseid
merged_df = collapsed_DRUG.merge(collapsed_INDI, on='caseid', how='outer') \
                          .merge(collapsed_REAC, on='caseid', how='outer') \
                          .merge(OUTC, on='caseid', how='outer') \
                          .merge(DEMO, on='caseid', how='outer')
print('merged all')

# %%

# Save the merged DataFrame to a new CSV file
merged_df.to_csv('data/processed/cleaned/merged.csv', index=False, sep='$')