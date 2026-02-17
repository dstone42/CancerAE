
# %%

import pandas as pd
import numpy as np

# %%

# Load the dataset
result = pd.read_csv('data/processed/cleaned/merged.csv', sep='$')

# %%

# Update outc_cod to group "DS", "CA", "RI", "OT" into "Other" and map "LT": "Life Threatening", "HO": "Hospitalization", "DE": "Death"
result['outc_cod'] = np.where(result['outc_cod'].isin(["DS", "CA", "RI", "OT"]), "Other", result['outc_cod'])
result['outc_cod'] = np.where(result['outc_cod'] == "LT", "Life Threatening", result['outc_cod'])
result['outc_cod'] = np.where(result['outc_cod'] == "HO", "Hospitalization", result['outc_cod'])
result['outc_cod'] = np.where(result['outc_cod'] == "DE", "Death", result['outc_cod'])

# %%

# Clean up the sex field
result['sex'] = np.where(~result['sex'].isin(["M", "F"]), "", result['sex'])
result['sex'] = result['sex'].str.replace('M', 'Male')
result['sex'] = result['sex'].str.replace('F', 'Female')

# %%

def deduplicate_definitive_rows(df: pd.DataFrame) -> pd.DataFrame:
    subset_cols = [
        'AE', 'event_dt',
        'cancer_drug_name', 'other_drug_name',
        'outc_cod', 'sex',
        'time_to_onset', 'cancerType'
    ]

    # Build mask for definitive candidates
    mask = (
        df['event_dt'].notna() |
        df['time_to_onset'].notna()
    )

    definitive = df[mask].copy()
    non_definitive = df[~mask].copy()

    # Sort so "keep='first'" is deterministic (earliest start/end, then quarter if present)
    sort_cols = [c for c in ['quarter'] if c in definitive.columns]
    if sort_cols:
        definitive = definitive.sort_values(sort_cols)

    before_count = len(definitive)
    deduped_definitive = definitive.drop_duplicates(subset=subset_cols, keep='first')
    after_count = len(deduped_definitive)
    removed = before_count - after_count
    print(removed)
    # # Update summary counts if available in outer scope
    # if 'summary' in globals():
    #     summary['definitive_candidates'] = int(before_count)
    #     summary['definitive_duplicates_removed'] = int(removed)
    #     summary['post_dedup_count'] = int(len(non_definitive) + after_count)

    # Recombine
    combined = pd.concat([deduped_definitive, non_definitive], ignore_index=True)

    return combined

# Apply de-duplication BEFORE recording the final dataset size
result = deduplicate_definitive_rows(result)

# %%

# Filter out rows where 'time_to_onset' is negative, but keep NaN values
result = result[(result['time_to_onset'] >= 0) | (result['time_to_onset'].isna())]

# Cap values at 365 days
result['time_to_onset'] = np.where(result['time_to_onset'] > 365, 365, result['time_to_onset'])

# Convert days to weeks
result['time_to_onset'] = result['time_to_onset'] / 7

# %%

# Save original AE_Category column as AE_Category_Expanded
result['AE_Category_Expanded'] = result['AE_Category']

# Create a simplified AE_Category column that has any categories with a comma as "Multiple Categories"
result['AE_Category'] = np.where(result['AE_Category'].str.contains(","), "Multiple AE Categories", result['AE_Category'])

# %%

# Update drug_category to replace "Other" with "" and remove duplicates
result['drug_category'] = result['drug_category'].apply(lambda x: x.split(",") if isinstance(x, str) else [])
result['drug_category'] = result['drug_category'].apply(lambda x: list(sorted(set(x))))
result['drug_category'] = result['drug_category'].apply(lambda x: [i.title() for i in x if i != "OTHER"])
result['drug_category'] = result['drug_category'].apply(lambda x: ",".join(x) if len(x) > 0 else "")

# Save original drug_category column as drug_category_expanded
result['drug_category_expanded'] = result['drug_category']

# Create simplified drug_category
result['drug_category'] = np.where(result['drug_category'].str.contains(","), "Multiple Categories", result['drug_category'])

# %%

# Write the cleaned data to a new CSV file
result.to_csv('data/processed/cleaned/merged_formatted.csv', sep='$', index=False)

# %%
