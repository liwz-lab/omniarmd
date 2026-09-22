import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
mapping_df = pd.read_excel('ARMD_organism_mapping.xlsx')

data = data.merge(
    mapping_df,
    left_on='organism_std',   
    right_on='organism', 
    how='left'
)
data.to_csv('./data_deidentification.csv')


import pandas as pd

mapping_df = pd.read_excel('ARMD_antimicrobial_mapping.xlsx')

data = data.merge(
    mapping_df,
    left_on='antimicrobial_std',   
    right_on='antimicrobial', 
    how='left'
)
data.to_csv('./data_deidentification.csv')
