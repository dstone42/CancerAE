# %% [markdown]
# <table>
#   <tr>
#     <th></th>
#     <th colspan="4">AE</th>
#   </tr>
#   <tr>
#     <th rowspan="4">Drug Category</th>
#     <th></th>
#     <th>yes</th>
#     <th>no</th>
#   </tr>
#   <tr>
#     <th>yes</th>
#     <td>a</td>
#     <td>b</td>
#   </tr>
#   <tr>
#     <th>no</th>
#     <td>c</td>
#     <td>d</td>
#   </tr>
# </table>

# %%
import pandas as pd
import json
import src.analysis.bcpnn as bcpnn
import src.analysis.mhra as mhra
import src.analysis.odds_ratio as odds_ratio
import src.analysis.prr as prr
from scipy.stats import fisher_exact
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm

# import importlib
# importlib.reload(prr)

import os
# os.chdir('../../')

# %% [markdown]
# #### Read in data

# %%
df = pd.read_csv('data/processed/cleaned/merged_formatted.csv', sep='$')


# %% [markdown]
# #### Setup

# %%
drugCategorySet = set()

for cell in df['drug_category']:
    split = str(cell).split(',')
    for item in split:
        if item != 'Other' and item != 'nan':
            drugCategorySet.add(item)
    

AESet = set()

for cell in df['AE']:
    split = str(cell).split(',')
    for item in split:
        if item != 'Other' and item != 'nan':
            AESet.add(item)

statTable = pd.DataFrame()

# %% [markdown]
# #### Main Loop with specific AEs

# %%
def compute_stats(drugCategory, AE, df, drugCategorySet, AESet):
    filterCount = 5

    drug_category_frame = df[[drugCategory in str(x) for x in df['drug_category']]]
    not_drug_category_frame = df[[drugCategory not in str(x) for x in df['drug_category']]]

    if len(drug_category_frame) == 0:
        drug_category_AE_frame = drug_category_frame # a
        drug_category_not_AE_frame = drug_category_frame # b
    else:
        drug_category_AE_frame = drug_category_frame[[AE in str(x) for x in drug_category_frame['AE']]] # a
        drug_category_not_AE_frame = drug_category_frame[[AE not in str(x) for x in drug_category_frame['AE']]] # b

    if len(not_drug_category_frame) == 0:
        not_drug_category_AE_frame = not_drug_category_frame # c
        not_drug_category_not_AE_frame = not_drug_category_frame # d
    else:
        not_drug_category_AE_frame = not_drug_category_frame[[AE in str(x) for x in not_drug_category_frame['AE']]] # c
        not_drug_category_not_AE_frame = not_drug_category_frame[[AE not in str(x) for x in not_drug_category_frame['AE']]] # d

    a = len(drug_category_AE_frame)
    b = len(drug_category_not_AE_frame)
    c = len(not_drug_category_AE_frame)
    d = len(not_drug_category_not_AE_frame)
    N = a + b + c + d

    nn = bcpnn.BCPNN(a, b, c, d)
    bcpnnVal = nn.calcIC()
    bcpnnLB, bcpnnUB = nn.calcICCI()
    chi_squared = mhra.calcChiSquared(a, b, c, d)
    ROR = odds_ratio.calcROR(a, b, c, d)
    RORLB, RORUB = odds_ratio.calcRORCI(ROR, a, b, c, d)
    PRR = prr.calcPRR(a, b, c, d)
    PRRLB, PRRUB = prr.calcPRRCI(PRR, a, b, c, d)

    contTable = pd.DataFrame({'irAE yes': [a, c], 'irAE no': [b, d]})
    result = fisher_exact(contTable)
    pvalue = result.pvalue
    adjpvalue = pvalue * len(drugCategorySet) * len(AESet)

    PRRFilter = 'pass'
    RORFilter = 'pass'
    MHRAFilter = 'pass'
    BCPNNFilter = 'pass'
    PvalueFilter = 'pass'

    if type(PRRUB) == str or PRRUB <= 1:
        PRRFilter = 'PRR 95% Confidence Interval is too low'
        filterCount -= 1
    elif N < 3:
        PRRFilter = 'N is too small'
        filterCount -= 1

    if type(RORUB) == str or RORUB <= 1:
        RORFilter = 'ROR 95% Confidence Interval is too low'
        filterCount -= 1

    if type(PRR) == str or PRR < 2:
        MHRAFilter = 'PRR is too low'
        filterCount -= 1
    elif a < 3:
        MHRAFilter = 'A is too small'
        filterCount -= 1
    elif type(chi_squared) == str or chi_squared < 4:
        MHRAFilter = 'Chi-squared is too low'
        filterCount -= 1

    if type(bcpnnUB) == str or bcpnnUB <= 0:
        BCPNNFilter = 'BCPNN 95% Confidence Interval is too low'
        filterCount -= 1

    if type(adjpvalue) == str or adjpvalue > 0.05:
        PvalueFilter = 'P-value is too high'
        filterCount -= 1

    return {
        'drug_category': drugCategory,
        'AE': AE,
        'BCPNN': bcpnnVal,
        'BCPNN lower bound': bcpnnLB,
        'BCPNN upper bound': bcpnnUB,
        'chi-squared': chi_squared,
        'ROR': ROR,
        'ROR lower bound': RORLB,
        'ROR upper bound': RORUB,
        'PRR': PRR,
        'PRR lower bound': PRRLB,
        'PRR upper bound': PRRUB,
        'p-value': pvalue,
        'adjusted p-value': adjpvalue,
        'N': N,
        'a': a,
        'PRR filter': PRRFilter,
        'ROR filter': RORFilter,
        'MHRA filter': MHRAFilter,
        'BCPNN filter': BCPNNFilter,
        'p-value filter': PvalueFilter,
        'Num passed filters': filterCount
    }

# Prepare all combinations
combinations = [(drugCategory, AE, df, drugCategorySet, AESet) for drugCategory in drugCategorySet for AE in AESet]

# Run in parallel
num_cores = multiprocessing.cpu_count()
results = Parallel(n_jobs=num_cores)(
    delayed(compute_stats)(*args) for args in tqdm(combinations)
)

# Convert to DataFrame
statTable = pd.DataFrame(results)

# %%

statTable = statTable.sort_values(by='N', ascending=False)
statTable.to_csv(f'data/processed/statistics/drug_category_stats.csv', sep=',', index=False)


