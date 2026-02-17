
import pandas as pd
import os

faers_quarters_path = 'data/raw/FAERS_quarters'

# Function to parse the date field
# The date field is in the format YYYYMMDD. However, it is sometimes missing the day part and sometimes the month part.
# This function will handle those cases and return a standardized date format.
# Some dates also have errors, such as 10201009, which is technically valid, but not a real date to be in this dataset.
# We will return pd.NA for those cases.
def parse_date(date_str):
    if pd.isna(date_str):
        return pd.NA
    date_str = str(int(date_str))
    if len(date_str) == 8:
        # Check if the date is valid
        try:
            return pd.to_datetime(date_str, format='%Y%m%d')
        except ValueError:
            # If the date is not valid, return pd.NA
            return pd.NA
    elif len(date_str) == 6:
        # Check if the date is valid
        try:
            return pd.to_datetime(date_str, format='%Y%m')
        except ValueError:
            # If the date is not valid, return pd.NA
            return pd.NA
    elif len(date_str) == 4:
        # Check if the date is valid
        try:
            return pd.to_datetime(date_str, format='%Y')
        except ValueError:
            # If the date is not valid, return pd.NA
            return pd.NA
    else:
        return pd.NA


if __name__ == '__main__':
    
    # Read in cancer cases
    cancer_cases = pd.read_csv('data/processed/cleaned/INDI_mapped.csv', sep='$')

    def process_quarter(quarter):

        quarter_cancer_cases = cancer_cases[cancer_cases['quarter'] == quarter]
        quarter_cancer_cases_set = set(quarter_cancer_cases['caseid'])

        year_suffix = quarter[2:]
        demo_file_path = os.path.join(faers_quarters_path, quarter, 'ASCII', f'DEMO{year_suffix}.TXT')
        # Read the DEMO file
        # The columns in the DEMO file have changed over time, so we need to handle that
        # The columns we are interested in are 'caseid', 'event_dt', and 'gndr_cod' or 'sex' in the more recent files
        # Read the first line to get the column names
        with open(demo_file_path, 'r') as f:
            header = f.readline().strip().split('$')
        # Check if 'gndr_cod' is in the header
        if 'gndr_cod' in header:
            demo_df = pd.read_csv(demo_file_path, delimiter='$', usecols=['caseid', 'event_dt', 'gndr_cod'])
            # Rename 'gndr_cod' to 'sex'
            demo_df.rename(columns={'gndr_cod':'sex'}, inplace=True)
        else:
            demo_df = pd.read_csv(demo_file_path, delimiter='$', usecols=['caseid', 'event_dt', 'sex'])

        # Filter the DEMO file to only include rows with caseid in cancer_cases
        demo_df = demo_df[demo_df['caseid'].isin(quarter_cancer_cases_set)]

        # Parse the date field
        demo_df['event_dt'] = demo_df['event_dt'].apply(parse_date)

        return demo_df

    # Process each quarter and collect results
    results = []
    for quarter in cancer_cases['quarter'].unique():
        results.append(process_quarter(quarter))

    # Concatenate all results
    final_results = pd.concat(results, ignore_index=True)

    # Ensure 'event_dt' is of datetime64 type before formatting
    final_results['event_dt'] = pd.to_datetime(final_results['event_dt'], errors='coerce')

    final_results['event_dt'] = final_results['event_dt'].dt.strftime('%Y-%m-%d')

    # Output the results
    final_results.to_csv('data/processed/cleaned/DEMO_mapped.csv', sep='$', index=False)

