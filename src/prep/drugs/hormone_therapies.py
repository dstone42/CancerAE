# %%

import pandas as pd

input_file = 'data/raw/drugs/hormone_therapies.txt'
output_file = 'data/processed/drugs/hormone_therapies.csv'

# %%

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    outfile.write("drug,brand_name,type\n")
    for line in infile:
        
        line = line.strip()
        drug, brand = line.split(' (')
        brand = brand.rstrip(')')
        drug_upper = drug.upper()

        outfile.write(f"{drug_upper.strip().replace(',','')},{brand.upper().strip().replace(',','')},HORMONE\n")