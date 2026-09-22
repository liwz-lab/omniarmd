import pandas as pd

mapping_df = pd.read_excel('ARMD_organism_mapping.xlsx')

data = data.merge(
    mapping_df,
    left_on='organism_std',   
    right_on='organism', 
    how='left'
)



import pandas as pd

mapping_df = pd.read_excel('ARMD_antimicrobial_mapping.xlsx')

data = data.merge(
    mapping_df,
    left_on='antimicrobial_std',   
    right_on='antimicrobial', 
    how='left'
)
