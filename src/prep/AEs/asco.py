
# %%

import pandas as pd

# %%

asco = pd.read_csv('data/raw/AEs/ASCO.csv')
asco = asco.drop(columns=['Page'])

# %%

# Remove leading numbers, periods, and spaces from the 'Site' and 'Adverse Event' columns
asco['Site'] = asco['Site'].str.replace(r'^\d+(\.\d+)*\.?\s*', '', regex=True)
asco['Adverse Event'] = asco['Adverse Event'].str.replace(r'^\d+(\.\d+)*\.?\s*', '', regex=True)

# %%

# Split rows in the 'Adverse Event' column that are split by ' or ' or ' and '
asco['Adverse Event'] = asco['Adverse Event'].str.replace(r'\s+or\s+', ',', regex=True)
asco['Adverse Event'] = asco['Adverse Event'].str.replace(r'\s+and\s+', ',', regex=True)

# One cell is a list of AEs in that category
# First, split the strings in the 'Adverse Event' column by commas
# Split the 'Adverse Event' column into multiple rows
asco = asco.assign(**{'Adverse Event': asco['Adverse Event'].str.split(',')}).explode('Adverse Event')

# %%

# Remove prefixes of 'Primary', 'Acquired', 'Inflammatory', and 'Bullous' from the 'Adverse Event' column
asco['Adverse Event'] = asco['Adverse Event'].str.replace(r'^\s*Primary\s*', '', regex=True)
asco['Adverse Event'] = asco['Adverse Event'].str.replace(r'^\s*Acquired\s*', '', regex=True)
asco['Adverse Event'] = asco['Adverse Event'].str.replace(r'^\s*Inflammatory\s*', '', regex=True)
asco['Adverse Event'] = asco['Adverse Event'].str.replace(r'^\s*Bullous\s*', '', regex=True)

# Remove suffixes of '-like Syndrome' and 'with' + any text following 'with'
asco['Adverse Event'] = asco['Adverse Event'].str.replace(r'\s*-like Syndrome\s*$', '', regex=True)
asco['Adverse Event'] = asco['Adverse Event'].str.replace(r'\s*with\s*.*$', '', regex=True)

# Change 'Diabetes' to 'Diabetes Mellitus'
asco['Adverse Event'] = asco['Adverse Event'].str.replace(r'\s*Diabetes\s*$', ' Diabetes Mellitus', regex=True)
# Change 'Thyrotoxicosis' to 'Thyrotoxic crisis'
asco['Adverse Event'] = asco['Adverse Event'].str.replace(r'\s*Thyrotoxicosis\s*$', ' Thyrotoxic crisis', regex=True)
# Change 'Impaired Ventricular Function' to 'Ventricular Dysfunction'
asco['Adverse Event'] = asco['Adverse Event'].str.replace(r'\s*Impaired Ventricular Function\s*$', ' Ventricular Dysfunction', regex=True)

# %%

# Filter out rows that do not say Steroid Use
asco = asco[~asco['Site'].str.contains('Steroid Use', na=False)]

# Filter out the 'Acute Kidney Injury Follow-Up' rows
asco = asco[~asco['Adverse Event'].str.contains('Acute Kidney Injury Follow-Up', na=False)]

# %%

# Remove leading and trailing whitespace from the 'Adverse Event' column
asco['Adverse Event'] = asco['Adverse Event'].str.strip()

# %%

# Drop any duplicates in the 'Adverse Event' column
asco = asco.drop_duplicates(subset=['Adverse Event'])

# %%

from rapidfuzz import process, fuzz
import json

# ctcae = pd.read_excel('data/raw/AEs/CTCAE_v5.0.xlsx', sheet_name='CTCAE v5.0 Clean Copy')
meddra_df = pd.read_csv('data/raw/AEs/MedDRA_28_0_English/MedAscii/pt.asc', delimiter='$', names=['pt_code', 'pt_name', 'soc_code'], usecols=[0,1,3])

# Read ctcae to meddra pt name dict
# ctcae_meddra_dict = json.load(open('data/processed/mapping/ctcae_to_pt_name.json'))

# Extract relevant columns
asco_terms = asco["Adverse Event"].dropna().unique()
# ctcae_terms = ctcae["CTCAE Term"].dropna().unique()
meddra_terms = meddra_df["pt_name"].dropna().unique()
# ctcae_terms = ctcae_meddra_dict.keys()
# meddra_terms = ctcae_meddra_dict.values()

# Perform fuzzy matching for each ASCO term against MedDRA terms
matched_terms = []
for term in asco_terms:
    term_lower = term.lower()  # Convert ASCO term to lowercase
    matches = process.extract(term_lower, [meddra_term.lower() for meddra_term in meddra_terms], scorer=fuzz.token_sort_ratio, limit=1)
    if matches:
        best_match_term, score, _ = matches[0]
        # Find the original MedDRA term (case-sensitive) for the matched term
        original_match_term = next(meddra_term for meddra_term in meddra_terms if meddra_term.lower() == best_match_term)
        matched_terms.append(original_match_term)
    else:
        matched_terms.append(None)  # No match found

# Add the matched MedDRA term as a new column in the asco DataFrame
asco['Meddra Term'] = matched_terms

# Save the updated DataFrame to a CSV file
asco.to_csv('data/processed/AEs/ASCO_with_Meddra.csv', index=False)

# %%
