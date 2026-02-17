import pandas as pd
import numpy as np
import swifter

# Load your dataframes
DRUG = pd.read_csv('data/processed/cleaned/DRUG_mapped.csv', sep='$', date_format='%Y-%m-%d')
DEMO = pd.read_csv('data/processed/cleaned/DEMO_mapped.csv', sep='$', date_format='%Y-%m-%d')

# Ensure date columns are in datetime format
DRUG['start_dt'] = pd.to_datetime(DRUG['start_dt'], errors='coerce')
DRUG['end_dt'] = pd.to_datetime(DRUG['end_dt'], errors='coerce')
DEMO['event_dt'] = pd.to_datetime(DEMO['event_dt'], errors='coerce')

# Replace dates outside a valid range with NaT
valid_date_range = pd.Timestamp('1900-01-01'), pd.Timestamp('2100-01-01')
DRUG.loc[(DRUG['start_dt'] < valid_date_range[0]) | (DRUG['start_dt'] > valid_date_range[1]), 'start_dt'] = pd.NaT
DRUG.loc[(DRUG['end_dt'] < valid_date_range[0]) | (DRUG['end_dt'] > valid_date_range[1]), 'end_dt'] = pd.NaT
DEMO.loc[(DEMO['event_dt'] < valid_date_range[0]) | (DEMO['event_dt'] > valid_date_range[1]), 'event_dt'] = pd.NaT

# Filter DRUG to only include rows with cancer_drug_name
DRUG = DRUG[DRUG['cancer_drug_name'].notna()]

# Merge DEMO and DRUG on 'caseid' to avoid row-wise filtering
merged = DEMO.merge(DRUG, on='caseid', suffixes=('_demo', '_drug'))

# Calculate time differences using vectorized operations
merged['time_to_onset'] = (merged['event_dt'] - merged['start_dt']).dt.days

# Replace invalid time differences with NaN
# merged.loc[merged['start_dt'] > merged['event_dt'], 'time_to_onset'] = np.nan

# Group by 'caseid' and find the closest drugs
def aggregate_closest_drugs(group):
    if group['time_to_onset'].isna().all():
        # If all time_diff values are NaN, return all drugs
        closest_drugs = group['cancer_drug_name'].dropna().unique().tolist()
        return pd.Series({
            'closest_drugs': ','.join(sorted(closest_drugs)),
            'time_to_onset': np.nan
        })
    else:
        # Find the minimum time difference
        min_time_diff = group['time_to_onset'].min()
        closest_drugs = group[group['time_to_onset'] == min_time_diff]['cancer_drug_name'].dropna().unique().tolist()
        return pd.Series({
            'closest_drugs': ','.join(sorted(closest_drugs)),
            'time_to_onset': min_time_diff
        })

result = merged.swifter.groupby('caseid').apply(aggregate_closest_drugs).reset_index()

# Merge the result back into DEMO
DEMO = DEMO.drop(columns=['closest_drugs', 'time_to_onset'], errors='ignore')  # Drop if they already exist
DEMO = DEMO.merge(result, on='caseid', how='left')

# Save or inspect the updated DEMO dataframe
DEMO.to_csv('data/processed/cleaned/DEMO_mapped.csv', index=False, sep='$')