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
import numpy as np
import src.analysis.bcpnn as bcpnn
import src.analysis.mhra as mhra
import src.analysis.odds_ratio as odds_ratio
import src.analysis.prr as prr
from scipy.stats import fisher_exact
from joblib import Parallel, delayed
from tqdm import tqdm

# import importlib
# importlib.reload(prr)

# %% [markdown]
# #### Read in data

# %%
df = pd.read_csv('data/processed/cleaned/merged_formatted.csv', sep='$')


# %% [markdown]
# #### Setup

# %%
drug_category_series = df['drug_category'].fillna('').astype(str)
ae_series = df['AE'].fillna('').astype(str)

drugCategorySet = set(
    drug_category_series.str.split(',').explode().str.strip()
) - {'Other', 'nan', ''}

AESet = set(
    ae_series.str.split(',').explode().str.strip()
) - {'Other', 'nan', ''}

drugCategoryList = list(drugCategorySet)
AEList = list(AESet)

drug_category_masks = {
    drugCategory: drug_category_series.str.contains(drugCategory, regex=False, na=False).to_numpy()
    for drugCategory in drugCategoryList
}

ae_masks = {
    AE: ae_series.str.contains(AE, regex=False, na=False).to_numpy()
    for AE in AEList
}

statTable = pd.DataFrame()

# %% [markdown]
# #### Main Loop with specific AEs

# %%
def compute_stats(drugCategory, AE, num_drug_categories, num_aes):
    filterCount = 5

    drug_mask = drug_category_masks[drugCategory]
    ae_mask = ae_masks[AE]
    not_drug_mask = np.logical_not(drug_mask)
    not_ae_mask = np.logical_not(ae_mask)

    a = int(np.count_nonzero(drug_mask & ae_mask))
    b = int(np.count_nonzero(drug_mask & not_ae_mask))
    c = int(np.count_nonzero(not_drug_mask & ae_mask))
    d = int(np.count_nonzero(not_drug_mask & not_ae_mask))
    N = a + b + c + d

    nn = bcpnn.BCPNN(a, b, c, d)
    bcpnnVal = nn.calcIC()
    bcpnnLB, bcpnnUB = nn.calcICCI()
    chi_squared = mhra.calcChiSquared(a, b, c, d)
    ROR = odds_ratio.calcROR(a, b, c, d)
    RORLB, RORUB = odds_ratio.calcRORCI(ROR, a, b, c, d)
    PRR = prr.calcPRR(a, b, c, d)
    PRRLB, PRRUB = prr.calcPRRCI(PRR, a, b, c, d)

    result = fisher_exact([[a, b], [c, d]])
    pvalue = result.pvalue
    adjpvalue = pvalue * num_drug_categories * num_aes

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
num_drug_categories = len(drugCategoryList)
num_aes = len(AEList)
combinations = [
    (drugCategory, AE, num_drug_categories, num_aes)
    for drugCategory in drugCategoryList
    for AE in AEList
]

# Run in parallel
num_cores = min(32, num_drug_categories * num_aes)
results = Parallel(
    n_jobs=num_cores,
    batch_size=256,
    pre_dispatch='all'
)(
    delayed(compute_stats)(*args) for args in tqdm(combinations)
)

# Convert to DataFrame
statTable = pd.DataFrame(results)

# %%

statTable = statTable.sort_values(by='N', ascending=False)
statTable.to_csv(f'data/processed/statistics/drug_category_stats.csv', sep=',', index=False)


