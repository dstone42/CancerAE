# %%

import pandas as pd

# %%

# Read in the data
df = pd.read_csv('data/raw/drugs/MedicationAdministration.csv')
immunotherapies = pd.read_csv('data/raw/drugs/immunotherapies.csv')
targeted_antibodies = pd.read_csv('data/raw/drugs/targeted_antibodies.csv')
targeted = pd.read_csv('data/processed/drugs/targeted.csv')
chemotherapies = pd.read_csv('data/raw/drugs/chemotherapies.csv')
hormone_therapies = pd.read_csv('data/processed/drugs/hormone_therapies.csv')

# %%

df = df[['DrugName', 'CommonDrugName', 'DrugCategory', 'DetailedDrugCategory']].drop_duplicates()
df['DrugName'] = df['DrugName'].str.upper()
df['CommonDrugName'] = df['CommonDrugName'].str.upper()
df['DrugCategory'] = df['DrugCategory'].str.upper()
df['DetailedDrugCategory'] = df['DetailedDrugCategory'].str.upper()

df = df[df['DrugCategory'] == 'ANTINEOPLASTIC']
df = df[df['DrugName'] != 'CLINICAL STUDY DRUG']

# Add an empty column 'BrandName'
df['BrandName'] = ''

df = df[['CommonDrugName', 'BrandName', 'DetailedDrugCategory']]

df.columns = ['DrugName', 'BrandName', 'DetailedDrugCategory']

# %%

# Dictionary to map longer drug names to their shorter equivalents
drug_name_mapping = {
    'SUNITINIB MALATE': 'SUNITINIB',
    'LENVATINIB MESYLATE': 'LENVATINIB',
    'CABOZANTINIB-S-MALATE': 'CABOZANTINIB',
    'RITUXIMAB AND HYALURONIDASE HUMAN': 'RITUXIMAB',
    'TRASTUZUMAB EMTANSINE': 'EMTANSINE',
    'TRASTUZUMAB DERUXTECAN': 'DERUXTECAN',
    'PERTUZUMAB TRASTUZUMAB AND HYALURONIDASE-ZZXF': 'PERTUZUMAB',
    'LENVATINIB MESYLATE': 'LENVATINIB',
    'PONATINIB HYDROCHLORIDE': 'PONATINIB',
    'SORAFENIB TOSYLATE': 'SORAFENIB',
    'ATEZOLIZUMAB AND HYALURONIDASE-TQJS': 'ATEZOLIZUMAB',
    'RADIUM 223 DICHLORIDE': 'RADIUM-223',
    'PAZOPANIB HYDROCHLORIDE': 'PAZOPANIB',
    'DARATUMUMAB AND HYALURONIDASE-FIHJ': 'DARATUMUMAB',
    'MECHLORETHAMINE HYDROCHLORIDE': 'MECHLORETHAMINE',
    'DABRAFENIB MESYLATE': 'DABRAFENIB',
    'TRAMETINIB DIMETHYL SULFOXIDE': 'TRAMETINIB',
    'CABOZANTINIB-S-MALATE': 'CABOZANTINIB',
    'COBIMETINIB FUMARATE': 'COBIMETINIB',
    'RUXOLITINIB PHOSPHATE': 'RUXOLITINIB',
    'AFATINIB DIMALEATE': 'AFATINIB',
    'GILTERITINIB FUMARATE': 'GILTERITINIB',
    'IBRITUMOMAB TIUXETAN': 'IBRITUMOMAB',
    'OSIMERTINIB MESYLATE': 'OSIMERTINIB',
    'CAPMATINIB HYDROCHLORIDE': 'CAPMATINIB',
    'MITOMYCIN C': 'MITOMYCIN',
    'TIVOZANIB HYDROCHLORIDE': 'TIVOZANIB',
    'ASCIMINIB HYDROCHLORIDE': 'ASCIMINIB',
    'LUTETIUM LU 177 VIPIVOTIDE TETRAXETAN': 'VIPIVOTIDE TETRAXETAN',
    'TEPOTINIB HYDROCHLORIDE': 'TEPOTINIB',
    'FEDRATINIB HYDROCHLORIDE': 'FEDRATINIB',
    'LONCASTUXIMAB TESIRINE-LPYL': 'LONCASTUXIMAB TESIRINE',
    'TECLISTAMAB-CQYV': 'TECLISTAMAB'
}

# Function to map longer drug names to their shorter equivalents
def map_drug_name(drug_name):
    return drug_name_mapping.get(drug_name, drug_name)

# Function to update or add drugs from another dataframe
def update_or_add_drugs(source_df, target_df):
    for _, row in source_df.iterrows():
        drug_name = map_drug_name(row['drug'].upper())
        brand_name = row['brand_name']
        drug_category = row['type'].upper()
        
        # Check if the drug_name is a substring of any drug in the target_df
        match = target_df[target_df['DrugName'].str.contains(drug_name)]
        
        if not match.empty:
            target_df.loc[match.index, ['DrugName', 'BrandName', 'DetailedDrugCategory']] = [drug_name, brand_name, drug_category]
        else:
            new_row = pd.DataFrame({'DrugName': [drug_name], 'DetailedDrugCategory': [drug_category], 'BrandName': [brand_name]})
            target_df = pd.concat([target_df, new_row], ignore_index=True)
    return target_df

# Update or add drugs from the other dataframes
df = update_or_add_drugs(targeted_antibodies, df)
df = update_or_add_drugs(targeted, df)
df = update_or_add_drugs(chemotherapies, df)
df = update_or_add_drugs(hormone_therapies, df)
df = update_or_add_drugs(immunotherapies, df)

# %%

# Add more general drug categories
drug_groups = pd.read_csv('data/raw/drugs/drug_groups.csv')
drug_dict = dict(zip(drug_groups['DetailedDrugCategory'], drug_groups['DrugCategory']))

df['DrugCategory'] = df['DetailedDrugCategory'].apply(lambda x: drug_dict[x])

# %%

df.to_csv('data/processed/drugs/drug_mapping.csv', index=False)

# %%

