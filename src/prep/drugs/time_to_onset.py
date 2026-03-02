import pandas as pd
import numpy as np
import swifter

# Load your dataframes
DRUG = pd.read_csv('data/processed/cleaned/DRUG.csv', sep='$', date_format='%Y-%m-%d')
DEMO = pd.read_csv('data/processed/cleaned/DEMO.csv', sep='$', date_format='%Y-%m-%d')

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

# For each caseid, select the minimum positive time_to_onset if any exist,
# otherwise keep the minimum (most negative) value.
def select_time_to_onset(group):
    positives = group[group['time_to_onset'] > 0]
    if not positives.empty:
        return positives['time_to_onset'].min()
    else:
        return group['time_to_onset'].min()

time_to_onset_per_case = (
    merged[['caseid', 'time_to_onset']]
    .dropna(subset=['time_to_onset'])
    .groupby('caseid')
    .apply(select_time_to_onset)
    .reset_index(name='time_to_onset')
)

# Merge this back into DEMO (will not duplicate rows)
DEMO = DEMO.merge(time_to_onset_per_case, on='caseid', how='left')

# Save or inspect the updated DEMO dataframe
DEMO.to_csv('data/processed/cleaned/DEMO.csv', index=False, sep='$')