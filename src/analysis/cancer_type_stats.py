# %% [markdown]
# <table>
#   <tr>
#     <th></th>
#     <th colspan="4">AE</th>
#   </tr>
#   <tr>
#     <th rowspan="4">Tumor Type</th>
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
df = pd.read_csv('data/processed/data.csv', sep='$')



# %% [markdown]
# #### Setup

# %%
tumor_type_series = df['tumor_type'].fillna('').astype(str)
ae_series = df['AE'].fillna('').astype(str)

tumorTypeSet = set(
    tumor_type_series.str.split(',').explode().str.strip()
) - {'Other', 'nan', ''}

AESet = set(
    ae_series.str.split(',').explode().str.strip()
) - {'Other', 'nan', ''}

tumorTypeList = list(tumorTypeSet)
AEList = list(AESet)

tumor_type_masks = {
    tumorType: tumor_type_series.str.contains(tumorType, regex=False, na=False).to_numpy()
    for tumorType in tumorTypeList
}

ae_masks = {
    AE: ae_series.str.contains(AE, regex=False, na=False).to_numpy()
    for AE in AEList
}

statTable = pd.DataFrame()


# %%
def compute_stats(tumorType, AE, num_tumor_types, num_aes):
    filterCount = 5

    cancer_mask = tumor_type_masks[tumorType]
    ae_mask = ae_masks[AE]
    not_cancer_mask = np.logical_not(cancer_mask)
    not_ae_mask = np.logical_not(ae_mask)

    a = int(np.count_nonzero(cancer_mask & ae_mask))
    b = int(np.count_nonzero(cancer_mask & not_ae_mask))
    c = int(np.count_nonzero(not_cancer_mask & ae_mask))
    d = int(np.count_nonzero(not_cancer_mask & not_ae_mask))
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
    adjpvalue = pvalue * num_tumor_types * num_aes

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
        'tumor_type': tumorType,
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
num_tumor_types = len(tumorTypeList)
num_aes = len(AEList)
combinations = [
    (tumorType, AE, num_tumor_types, num_aes)
    for tumorType in tumorTypeList
    for AE in AEList
]

# Run in parallel
num_cores = min(32, num_tumor_types * num_aes)
results = Parallel(
    n_jobs=num_cores,
    batch_size=256,
    pre_dispatch='all'
)(
    delayed(compute_stats)(*args) for args in tqdm(combinations)
    )

# Convert to DataFrame
statTable = pd.DataFrame(results)
# statTable = statTable.sort_values(by='N', ascending=False)
# statTable.to_csv(f'data/processed/statistics/tumor_type_stats.csv', sep=',', index=False)

# %%
statTable = statTable.sort_values(by='N', ascending=False)
statTable.to_csv(f'data/processed/statistics/tumor_type_stats.csv', sep=',', index=False)



