# ORIGNIALLY WRITTEN BY CHATGPT AND EDITED BY ME. SUBJECT TO ERRORS
# %%

import os
import pandas as pd
import json
import re

# Mapping specific cancer types to broader categories
def map_cancer_types(cancer_list, existing_mapping=None):
    if existing_mapping is None:
        mapping = {}
    else:
        mapping = existing_mapping

    cancer_terms = ['cancer', 'carcinoma', 'neoplasm', 'plasia', 'tumor', 'tumour', 'mass', 'malignancy', 'proliferat']

    for cancer in cancer_list:
        if pd.isna(cancer):
            mapping[cancer] = "Other"
            continue
        cancer = cancer.strip().upper().replace(',', '')
        cancer_lower = cancer.lower()

        if cancer not in mapping.keys():
            # Determine the category for each cancer type based on keywords
            if "metasta" in cancer_lower:
                mapping[cancer] = "Other Cancer"
            elif "endometrial" in cancer_lower and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Endometrial Cancer"
            elif "melanocytoma" in cancer_lower:
                mapping[cancer] = "Melanocytoma"
            elif any([x in cancer_lower for x in ["lentigo maligna", "melanoma", "choroid"]]):
                mapping[cancer] = "Melanoma"
            elif ("colorectal" in cancer_lower or "colon" in cancer_lower or "rect" in cancer_lower) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Colorectal Cancer"
            elif ("peripheral nervous system" in cancer_lower and any([x in cancer_lower for x in cancer_terms])) or "neuroblastoma" in cancer_lower:
                mapping[cancer] = "Peripheral Nervous System Cancer"
            elif ("uterine" in cancer_lower or "endometrial" in cancer_lower) and "sarcoma" in cancer_lower:
                mapping[cancer] = "Uterine Sarcoma"
            elif "medulloblastoma" in cancer_lower:
                # Assumes input specifies if it's desmoplastic/nodular or with extensive nodularity
                mapping[cancer] = "Desmoplastic/Nodular Medulloblastoma" if "desmoplastic" in cancer_lower or "nodular" in cancer_lower else "Medulloblastoma"
            elif any([x in cancer_lower for x in ["t-cell", "t cell", "natural killer"]]) and any([x in cancer_lower for x in ['lymphoma', 'leukemia', 'leukaemia', 'lymphocytosis']]): # Needs to be before other lymphomas
                mapping[cancer] = "Mature T and NK Neoplasms"
            elif any([x in cancer_lower for x in ["lymphoma", "hodgkin", "waldenstrom's macroglobulina", "richter's syndrome"]]): # Needs to be before thymic
                mapping[cancer] = "Non-Hodgkin Lymphoma" if any([x in cancer_lower for x in ["non-hodgkin", "waldenstrom's macroglobulina"]]) else "Hodgkin Lymphoma"
            elif (any([x in cancer_lower for x in ["thymic", "thymus"]]) and any([x in cancer_lower for x in cancer_terms])) or "thymoma" in cancer_lower:
                mapping[cancer] = "Thymic Tumor"
            elif ("skin" in cancer_lower and "non-melanoma" in cancer_lower) or any([x in cancer_lower for x in ["non-melanoma", "bowen's disease", "basal cell carcinoma"]]):
                mapping[cancer] = "Skin Cancer, Non-Melanoma"
            elif "liver" in cancer_lower and "rhabdoid" in cancer_lower:
                mapping[cancer] = "Malignant Rhabdoid Tumor of the Liver"
            elif "leukemia" in cancer_lower or "leukaemia" in cancer_lower:
                # Specific leukemia types will need more detailed mapping based on input
                mapping[cancer] = "Leukemia"
            elif "breast" in cancer_lower and "sarcoma" in cancer_lower:
                mapping[cancer] = "Breast Sarcoma"
            elif any([x in cancer_lower for x in ["esophageal", "stomach", "esophagogastric", "gastric"]]) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Esophageal/Stomach Cancer"
            elif ("pancrea" in cancer_lower and any([x in cancer_lower for x in cancer_terms])) or "insulinoma" in cancer_lower:
                mapping[cancer] = "Pancreatic Cancer"
            elif ("adrenal" in cancer_lower and any([x in cancer_lower for x in cancer_terms])) or "phaeochromocytoma" in cancer_lower:
                mapping[cancer] = "Adrenal Gland Cancer"
            elif (any([x in cancer_lower for x in ["kidney", "renal"]]) and any([x in cancer_lower for x in cancer_terms])) or "nephroblastoma" in cancer_lower:
                mapping[cancer] = "Kidney Cancer"
            elif any([x in cancer_lower for x in ["eye", "ocular"]]) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Eye Cancer"
            elif "mastocytosis" in cancer_lower:
                mapping[cancer] = "Mastocytosis"
            # FIXME Parotid which is currently in head and neck should be in this category
            elif (any([x in cancer_lower for x in ["salivary gland", "mucoepidermoid"]]) and any([x in cancer_lower for x in cancer_terms])) or "pleomorphic adenoma" in cancer_lower or any([x == cancer_lower for x in ["adenoid cystic carcinoma"]]):
                mapping[cancer] = "Salivary Gland Cancer"
            elif "liver" in cancer_lower and not "rhabdoid" in cancer_lower and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Liver Cancer"
            elif "sex cord stromal" in cancer_lower and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Sex Cord Stromal Tumor"
            elif "posttransplant lymphoproliferative" in cancer_lower:
                mapping[cancer] = "Posttransplant Lymphoproliferative Disorders"
            elif any([x in cancer_lower for x in ["bladder", "urinary tract", "urethra"]]) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Bladder/Urinary Tract Cancer"
            elif any([x in cancer_lower for x in ["vulva", "vagin"]]) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Vulvar/Vaginal Cancer"
            elif "histiocytosis" in cancer_lower:
                mapping[cancer] = "Histiocytosis"
            elif "adenocarcinoma in situ" in cancer_lower:
                mapping[cancer] = "Adenocarcinoma In Situ"
            elif ("thyroid" in cancer_lower or "huerthle" in cancer_lower) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Thyroid Cancer"
            elif ("uterine" in cancer_lower or "ureteric" in cancer_lower) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Uterine Cancer"
            elif (any([x in cancer_lower for x in ["brain", "cns", "central nervous system", "Paraganglion"]]) and any([x in cancer_lower for x in cancer_terms])) or any([x in cancer_lower for x in ["meningioma", "ependymoma", "astrocytoma"]]):
                mapping[cancer] = "CNS/Brain Cancer"
            elif (any([x in cancer_lower for x in ["lung", "bronch", "pulmonary", "mediastinum", "respiratory", "thorax", "tracheal"]]) and any([x in cancer_lower for x in cancer_terms])) or any([x in cancer_lower for x in ["pancoast's"]]):
                mapping[cancer] = "Lung Cancer"
            elif any([x in cancer_lower for x in ["ovar", "fallopian tube", "placenta"]]) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Ovarian/Fallopian Tube Cancer"
            elif ("cervical" in cancer_lower or "cervix" in cancer_lower) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Cervical Cancer"
            elif "skin" in cancer_lower and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Skin Cancer"
            elif "breast" in cancer_lower and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Breast Cancer"
            elif "prostate" in cancer_lower and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Prostate Cancer"
            elif any([x in cancer_lower for x in ["testic", "testis", "scrotal"]]) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Testicular Cancer"
            elif "glioma" in cancer_lower or "glioblastoma" in cancer_lower:
                mapping[cancer] = "Glioma"
            elif "gestational trophoblastic" in cancer_lower:
                mapping[cancer] = "Gestational Trophoblastic Disease"
            elif "parathyroid" in cancer_lower and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Parathyroid Cancer"
            elif "gastrointestinal neuroendocrine" in cancer_lower and ("esophagus" in cancer_lower or "stomach" in cancer_lower) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Gastrointestinal Neuroendocrine Tumors of the Esophagus/Stomach"
            elif ("gastrointestinal" in cancer_lower or "caecum" in cancer_lower) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Gastrointestinal Stromal Tumor"
            elif ("myelodysplastic" in cancer_lower and "myeloproliferative" in cancer_lower) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Myelodysplastic/Myeloproliferative Neoplasms"
            elif "rhabdoid" in cancer_lower and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Rhabdoid Cancer"
            elif "adrenocortical carcinoma" in cancer_lower:
                mapping[cancer] = "Adrenocortical Carcinoma"
            elif any([x in cancer_lower for x in ["soft tissue sarcoma", "leiomyosarcoma", "fibroma"]]) or (any([x in cancer_lower for x in ["desmoplastic small round cell", "alveolar"]]) and 'sarcoma' in cancer_lower) or ("pleomorphic" in cancer_lower and "histiocytoma" in cancer_lower): # Needs to be before bone cancer
                mapping[cancer] = "Soft Tissue Sarcoma"
            elif "histiocytoma" in cancer_lower:
                mapping[cancer] = "Angiomatoid Fibrous Histiocytoma"
            elif (any([x in cancer_lower for x in ["bone", "desmoid", "connective tissue"]]) and any([x in cancer_lower for x in cancer_terms])) or any([x in cancer_lower for x in ["chondroma", "paget's disease of penis", "sarcoma", "chordoma"]]):
                mapping[cancer] = "Bone Cancer"
            elif "medulloblastoma with extensive nodularity" in cancer_lower:
                mapping[cancer] = "Medulloblastoma with Extensive Nodularity"
            elif "non-hodgkin lymphoma" in cancer_lower:
                mapping[cancer] = "Non-Hodgkin Lymphoma"
            elif (any([x in cancer_lower for x in ["hepato", "hepatic", "bile duct"]]) and any([x in cancer_lower for x in cancer_terms])) or any([x in cancer_lower for x in ["cholangiocarcinoma"]]):
                mapping[cancer] = "Hepatobiliary Cancer"
            elif ("biliary" in cancer_lower or "gall" in cancer_lower) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Biliary Tract Cancer"
            elif "nerve sheath" in cancer_lower and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Nerve Sheath Tumor"
            elif any([x in cancer_lower for x in ["peritoneal", "pleura"]]) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Peritoneal Cancer NOS"
            elif "malignant glomus" in cancer_lower and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Malignant Glomus Tumor"
            elif ("small bowel" in cancer_lower or "small intestin" in cancer_lower) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Small Bowel Cancer"
            elif ("bowel" in cancer_lower or "intestin" in cancer_lower) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Bowel Cancer"
            elif (any([x in cancer_lower for x in ["soft tissue", "granular cell", "conjunctiva"]]) and any([x in cancer_lower for x in cancer_terms])) or any([x in cancer_lower for x in ["leiomyoma"]]):
                mapping[cancer] = "Soft Tissue Cancer"
            elif ("appendiceal" in cancer_lower or "appendix" in cancer_lower) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Appendiceal Cancer"
            elif "mature b-cell neoplasms" in cancer_lower or "myeloma" in cancer_lower:
                mapping[cancer] = "Mature B-Cell Neoplasms"
            elif any([x in cancer_lower for x in ["penile", "penis"]]) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Penile Cancer"
            elif "myelodysplastic syndrome" in cancer_lower:
                mapping[cancer] = "Myelodysplastic Syndromes"
            elif ("sellar" in cancer_lower or "pituitary" in cancer_lower) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Sellar Tumor"
            elif "mesothelioma" in cancer_lower:
                mapping[cancer] = "Mesothelioma"
            elif "anal" in cancer_lower and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Anal Cancer"
            elif any([x in cancer_lower for x in ["teratoma", "choriocarcinoma"]]) or ("germ cell" in cancer_lower and any([x in cancer_lower for x in cancer_terms])):
                mapping[cancer] = "Germ Cell Tumor"
            elif any([x in cancer_lower for x in ["ampulla"]]) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Ampullary Cancer"
            elif (any([x in cancer_lower for x in ["head and neck", "pharyngeal", "tongue", "oral", "nasal", "gingiv", "tonsil", "pharynx", "laryngeal", "larynx", "parotid", "throat", "ear", "lip", "glotti", "palate", "spinal cord"]]) and any([x in cancer_lower for x in cancer_terms])) or any([x in cancer_lower for x in ["ameloblastoma"]]):
                mapping[cancer] = "Head and Neck Cancer"
            elif any([x in cancer_lower for x in ["neuroe"]]) and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Other Neuroendocrine"
            elif "unknown primary" in cancer_lower and any([x in cancer_lower for x in cancer_terms]):
                mapping[cancer] = "Carcinoma of Unknown Primary"
            elif any([x in cancer_lower for x in cancer_terms]) and 'mass' not in cancer_lower:
                mapping[cancer] = "Other Cancer"
            # Default to "Other" if no specific match found
            else:
                mapping[cancer] = ""
    return mapping

# %%

quarters = [q for q in os.listdir('data/raw/FAERS_quarters') if not q.startswith('.')]

all_data = []
combined_mapping = {}

for quarter in quarters:
    
    year_suffix = quarter[2:]
    df = pd.read_csv(f'data/raw/FAERS_quarters/{quarter}/ASCII/INDI{year_suffix}.TXT', sep='$', usecols=['caseid', 'indi_pt'])

    valsToMap = list(df['indi_pt'].unique())
    combined_mapping = map_cancer_types(valsToMap, combined_mapping)

    df['cancerType'] = df['indi_pt'].apply(lambda x: combined_mapping[x.strip().upper().replace(',', '')])
    df['quarter'] = quarter

    all_data.append(df)

# %%

combined_df = pd.concat(all_data, ignore_index=True)
# Filter out rows with empty cancerType
combined_df = combined_df[combined_df['cancerType'] != '']

# %%

# Remove duplicates

# Add a helper column to extract the year and quarter for sorting
combined_df['quarter_numeric'] = combined_df['quarter'].str.extract(r'(\d{4})q(\d)').apply(lambda x: int(x[0]) * 10 + int(x[1]), axis=1)

# Sort by caseid and quarter_numeric to ensure the latest quarter is last
combined_df = combined_df.sort_values(by=['caseid', 'quarter_numeric'], ascending=[True, True])

# Identify the latest quarter for each caseid
latest_quarters = combined_df.groupby('caseid')['quarter_numeric'].transform('max')

# Filter to keep only rows corresponding to the latest quarter for each caseid
combined_df = combined_df[combined_df['quarter_numeric'] == latest_quarters]

# Drop the helper column as it's no longer needed
combined_df = combined_df.drop(columns=['quarter_numeric'])

# %%

combined_df.to_csv('data/processed/cleaned/INDI_mapped.csv', sep='$', index=False)
json.dump(combined_mapping, open('data/processed/cancer_types/cancer_type_map.json', 'w+'), indent=4)

# %%
