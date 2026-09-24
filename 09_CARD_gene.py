
import pandas as pd
import json

aro = pd.read_csv("./card_data/aro_index.tsv", sep="\t")
aro.columns
aro['CARD Short Name'].unique().tolist()
aro['CARD Short Name'].value_counts()

aro['ARO Name'].unique().tolist()
aro.rename(columns={'CARD Short Name': 'gene_symbol'}, inplace=True)

ebi=pd.read_csv('./ebi_knowledge_summary.csv')
ebi.columns
ebi['resistance_evidence_label_cn'].unique().tolist()
ebi_resistance = ebi[
    ebi['resistance_evidence_label_cn'].isin([
        'Strong evidence of resistance',
        'Moderate evidence of resistance'
    ])
].copy()
ebi['gene_symbol'].unique().tolist()
aro['gene_symbol'].unique()
aro['gene_symbol'].unique().tolist()
aro.to_csv('./CARD_ARO_Gene_mechanism.csv')


ebi_res = ebi[
    ebi['resistance_evidence_label_cn'].isin([
        'Strong evidence of resistance',
        'Moderate evidence of resistance'
    ])
].copy()

import re

def normalize_gene(g):
    if pd.isna(g):
        return None
    g = g.lower()
    g = re.sub(r'[^a-z0-9]', '', g)
    return g

ebi_res['gene_std'] = ebi_res['gene_symbol'].apply(normalize_gene)
aro['gene_std'] = aro['gene_symbol'].apply(normalize_gene)

# 1. exact
map_exact = dict(zip(aro['gene_std'], aro['gene_symbol']))
ebi_res['card_gene_exact'] = ebi_res['gene_std'].map(map_exact)

# 2. fuzzy
def map_fuzzy(g):
    if pd.isna(g):
        return None
    m = aro[aro['gene_std'].str.contains(g, na=False)]
    if len(m) == 1:
        return m.iloc[0]['gene_symbol']
    elif len(m) > 1:
        return "|".join(m['gene_symbol'].head(3))
    return None

ebi_res['card_gene_fuzzy'] = ebi_res['gene_std'].apply(map_fuzzy)

# 3. prefix
def map_prefix(g):
    if pd.isna(g):
        return None
    m = aro[aro['gene_std'].str.startswith(g)]
    if len(m) > 0:
        return "|".join(m['gene_symbol'].head(3))
    return None

ebi_res['card_gene_prefix'] = ebi_res['gene_std'].apply(map_prefix)

ebi_res['card_gene'] = (
    ebi_res['card_gene_exact']
    .fillna(ebi_res['card_gene_fuzzy'])
    .fillna(ebi_res['card_gene_prefix'])
)

mapping = ebi_res.merge(
    aro,
    left_on='card_gene',
    right_on='gene_symbol',
    how='left'
)

mapping.to_csv('./EBI_AMR_mechanism.csv')
mapping.columns
mapping.rename(columns={
    'gene_symbol_x': 'gene_symbol',
    'Resistance Mechanism': 'resistance_mechanism'
}, inplace=True)

cols = [
    'organism_std',
    'antimicrobial_std',
    'gene_symbol',
    'GPAS',
    'resistance_evidence_label_cn',
    'resistance_mechanism',   
    'resistance_evidence_label_cn'
]

mapping_subset = mapping[[c for c in cols if c in mapping.columns]]
mapping_subset.to_csv('./EBI_AMR_mechanism.csv')

rt11_sub = mapping[cols].copy()
rt11_sub.to_csv('./EBI_AMR_mechanism_clean.csv')
rt11_sub.columns

#############################
rt11=pd.read_excel('./EBI_AMR_mechanism.xlsx')
rt11.columns

rt11.rename(columns={
    'gene_symbol_x': 'gene_symbol',
    'Resistance Mechanism': 'resistance_mechanism'
}, inplace=True)

cols = [
    'organism_std',
    'antimicrobial_std',
    'gene_symbol',
    'Non_S_rate_among_gene_positive',
    'resistance_evidence_label_cn',
    'resistance_mechanism',   
    'resistance_evidence_label_cn'
]
rt11_sub = rt11[cols].copy()
rt11_sub.to_csv('./EBI_AMR_mechanism_clean.csv')
rt11_sub.columns
