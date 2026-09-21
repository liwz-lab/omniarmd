import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
df.susceptibility.unique().tolist()
df.susceptibility.unique().value_counts
df['susceptibility'].value_counts
mapping = {
    'Susceptible': 'S',
    'Resistant': 'R',
    'Intermediate': 'I',
    'Susceptible dose-dependent': 'I',  
    'Non-susceptible': 'R',
    'Inconclusive': 'nan',  
    'Null': 'nan',
    'NaN': 'nan',
    'Synergism': 'nan'

}
df['susceptibility_std'] = df['susceptibility'].map(mapping)
df['susceptibility_std'].value_counts(dropna=False)
df['susceptibility_std'] = df['susceptibility_std'].replace(
    ['nan', 'NaN', 'NULL', 'Null', 'None', ''],
    np.nan
)
df['susceptibility_std'].value_counts(dropna=False)
df.to_csv('./01_combined_culture_cohort_std.csv', index=False)
