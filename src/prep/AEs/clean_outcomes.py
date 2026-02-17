
# %%

import pandas as pd
import os


faers_quarters_path = 'data/raw/FAERS_quarters'

# %%

def mostSevereOutcome(outcomeList):
    if not pd.isna(outcomeList):
        outcomeList = outcomeList.split(',')
    else:
        return pd.NA
    if 'DE' in outcomeList:
        return 'DE'
    elif 'LT' in outcomeList:
        return 'LT'
    elif 'HO' in outcomeList:
        return 'HO'
    elif 'DS' in outcomeList:
        return 'DS'
    elif 'CA' in outcomeList:
        return 'CA'
    elif 'RI' in outcomeList:
        return 'RI'
    elif 'OT' in outcomeList:
        return 'OT'
    else:
        return pd.NA

# %%

if __name__ == '__main__':

    cancer_cases = pd.read_csv('data/processed/cleaned/INDI_mapped.csv', sep='$')

    def process_quarter(quarter):

        quarter_cancer_cases = cancer_cases[cancer_cases['quarter'] == quarter]
        quarter_cancer_cases_set = set(quarter_cancer_cases['caseid'])

        year_suffix = quarter[2:]
        outc_file_path = os.path.join(faers_quarters_path, quarter, 'ASCII', f'OUTC{year_suffix}.TXT')
        outc_df = pd.read_csv(outc_file_path, delimiter='$', usecols=[1, 2])
        outc_df.columns = ['caseid', 'outc_cod']
        # Filter the OUTC file to only include rows with caseid in cancer_cases
        outc_df = outc_df[outc_df['caseid'].isin(quarter_cancer_cases_set)]
        outc_df = outc_df.groupby('caseid').agg({'outc_cod': lambda x: ','.join(x)}).reset_index()
        outc_df['outc_cod'] = outc_df['outc_cod'].apply(mostSevereOutcome)

        return outc_df

    # Process each quarter and collect results
    results = []
    for quarter in cancer_cases['quarter'].unique():
        results.append(process_quarter(quarter))

    # Concatenate all results
    final_results = pd.concat(results, ignore_index=True)

    # Output the results
    final_results.to_csv('data/processed/cleaned/OUTC_mapped.csv', sep='$', index=False)