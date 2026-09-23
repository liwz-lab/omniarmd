import os
import pandas as pd
import os
from pathlib import Path
import hashlib
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
os.chdir('')
meta=pd.read_excel('2024-FQ.xlsx')
card=pd.read_csv('combined_amr_results_strict_sampleID.csv')
card['BioSample_ID'].nunique()
merged = pd.merge(
    meta,
    card,
    on="BioSample_ID",
    how="inner"
)
merged.to_csv('CNSZ_card_meta.csv')
merged.columns
subset = subset.drop_duplicates(subset=['BioSample_ID'])
subset.to_csv('CNSZ_card_meta_subset.csv')

org=subset['BioSample_ID'].unique()
org = pd.DataFrame(subset['BioSample_ID'].unique(), columns=['BioSample_ID'])
merged2 = pd.merge(
    meta,
    org,
    on="BioSample_ID",
    how="inner"
)
merged2.to_csv('CNSZ_meta_select.csv')

meta2=pd.read_excel('CNSZ_meta_select.xlsx')
meta2['order_time_jittered_std'].unique()
rt3 = pd.read_csv('01_culture_cohort_std.csv')
rt3['organism_std'] = (
    rt3['organism_std']
    .replace({
        'Acinetobacter baumannii complex': 'Acinetobacter baumannii'
    })
)
rt3['organism_std'] = (
    rt3['organism_std']
    .replace({
        'Klebsiella pneumoniae subsp. pneumoniae': 'Klebsiella pneumoniae'
    })
)


rt3.columns
rt3['order_time_jittered_std'].unique()
meta2['order_time_jittered'] = pd.to_datetime(
    meta2['order_time_jittered_std']
).dt.date


rt3['order_time_jittered'] = pd.to_datetime(
    rt3['order_time_jittered_std']
).dt.date
meta2.columns
print(rt3[['anon_id','order_proc_id_coded','organism_std']].dtypes)

print(meta2[['anon_id','order_proc_id_coded','organism_std']].dtypes)
merge_cols = [
    'anon_id',
    'order_proc_id_coded',
    'organism_std'
]

for col in merge_cols:
    rt3[col] = rt3[col].astype(str)
    meta2[col] = meta2[col].astype(str)


rt3_merged_df = pd.merge(
    rt3,
    meta2,
    on=['anon_id', 'order_proc_id_coded','organism_std'],
    how='inner'   

rt3_merged_df.to_csv('CNSZ_merge_sample_meta.csv')

rt3_merged_df.columns
check_cols = [
    'anon_id',
    'pat_enc_csn_id_coded',
    'order_proc_id_coded',
    'organism_std',
    'antibiotic_std',
    'susceptibility_std',
    'BioSample_ID'
]


rt3_clean = rt3_merged_df.dropna(
    subset=[
        'organism_std',
        'antibiotic_std',
        'susceptibility_std'
    ]
).reset_index(drop=True)

rt3_clean[
    [
        'organism_std',
        'antibiotic_std',
        'susceptibility_std'
    ]
].isna().sum()


rt3_unique = rt3_clean.drop_duplicates(
    subset=[
        'anon_id',
        'pat_enc_csn_id_coded',
        'order_proc_id_coded',
        'organism_std',
        'antibiotic_std',
        'susceptibility_std',
        'BioSample_ID'
    ]
).reset_index(drop=True)

rt3_unique.to_csv('CNSZ_merge_sample_meta_clean.csv')
rt3_unique['BioSample_ID'].nunique()
rt3_unique = rt3_unique.rename(columns={'culture_description': 'isolation_source'})
###########################################
rt3_unique = rt3_unique.rename(columns={'order_time_jittered_std_x': 'order_time_jittered_std'})
ast_meta_cols = [
    "BioSample_ID",
    'anon_id',
    'pat_enc_csn_id_coded',
    'order_proc_id_coded',
    'order_time_jittered_std',
    'isolation_source',
    'organism_std',
    'antibiotic_std',
    'susceptibility_std',
    'source'
]

df_ast_unique = rt3_unique[ast_meta_cols].drop_duplicates(
    subset=["BioSample_ID", 'order_proc_id_coded',"organism_std", "antibiotic_std", "susceptibility_std"]
)

card_merged_clinical = pd.merge(card, df_ast_unique, on="BioSample_ID", how="left")

card_merged_clinical.to_csv('CNSZ_SIR_gene_deidentification_0730.csv')
card_merged_clinical = card_merged_clinical.dropna(subset=[
    'organism_std',
    'antibiotic_std',
    'susceptibility_std'
])
card_merged_clinical.columns
card_merged_clinical.to_csv('CNSZ_SIR_gene_deidentification_0730_clean.csv')

check = (
    card_merged_clinical
    .groupby('BioSample_ID')['organism_std']
    .nunique()
    .reset_index(name='organism_count')
)
multi_org = check[check['organism_count'] > 1]

multi_org.head()

########################################CNSZ-EBI MERGE#############################################################
import os
os.chdir('')
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

CNSZ_AMR=pd.read_csv('CNSZ_SIR_gene_deidentification_0730_clean.csv')
CNSZ_AMR['source']='CNSZ'
EBI_AMR = pd.read_csv('phenotype_genotype_merged_susceptibility_std.csv')
EBI_AMR['source']='EMBL-EBI-AMR'
EBI_AMR = EBI_AMR.dropna(subset=[
    'species',
    'resistance_phenotype',
    'antibiotic_name'
])
EBI_AMR['species'].unique()
EBI_AMR['resistance_phenotype'].unique()
EBI_AMR['antibiotic_name'].unique()
EBI_AMR['source']='EMBL-EBI-AMR'
CNSZ_AMR['source']='CNSZ'
CNSZ_AMR['source']='CNSZ'
CNSZ_AMR['ast_standard']='CLSI'
CNSZ_AMR['country']='China'
CNSZ_AMR['geographical_region']='Asia'
CNSZ_AMR['geographical_subregion']='Eastern Asia'
EBI_AMR['geographical_region'].unique()
EBI_AMR['geographical_subregion'].unique()
EBI_AMR['class'].unique()


########################merge#############################
target_columns = [
    "BioSample_ID",
    "gene_symbol",
    "species_std",
    'antibiotic_std',
    "susceptibility_std",
    "ast_standard",
    "country",
    'geographical_region',
    "geographical_subregion",
    "atb_subtype_std",
    "atb_class_std",
    'source'
]


df_cnsz_sub = CNSZ_AMR[target_columns].copy()
merged_df = pd.concat([df_armd_sub, df_cnsz_sub], ignore_index=True)
print(merged_df.head(3))
print(merged_df.tail(3))


merged_df['gene_family'] = merged_df['gene_symbol'].str.extract(r'^([a-zA-Z]+)')
merged_df.to_csv('EBI_CNSZ_AMR2_deidentification.csv')
merged_df['source'].value_counts()

merged_df=pd.read_csv('EBI_CNSZ_AMR2_deidentification.csv')

import pandas as pd
import numpy as np

ebi_df=merged_df
ebi_clean = ebi_df.dropna(subset=['species_std','susceptibility_std', 'gene_symbol', 'antibiotic_std'])
ebi_clean['source'].value_counts()

ebi_clean = ebi_clean.rename(columns={'species_std': 'organism_std'})
ebi_clean = ebi_clean.rename(columns={'antibiotic_std': 'antimicrobial_std'})
ebi_clean['organism_std'] = ebi_clean['organism_std'].str.lower()
ebi_clean['antimicrobial_std'] = ebi_clean['antimicrobial_std'].str.lower()
ebi_clean['susceptibility_std'].unique()
ebi_clean.to_csv('EBI_CNSZ_AMR_deidentification_0730.csv')
ebi_clean=pd.read_csv('EBI_CNSZ_AMR_deidentification_0730.csv')


import pandas as pd
import numpy as np
ebi_df = ebi_clean.copy()

required_cols = [
    "BioSample_ID",
    "organism_std",
    "antimicrobial_std",
    "susceptibility_std",
    "gene_symbol",
]

ebi_clean = ebi_df.dropna(subset=required_cols).copy()

ebi_clean["organism_std"] = (
    ebi_clean["organism_std"].astype(str).str.strip().str.lower()
)

ebi_clean["antimicrobial_std"] = (
    ebi_clean["antimicrobial_std"].astype(str).str.strip().str.lower()
)

ebi_clean["gene_symbol"] = (
    ebi_clean["gene_symbol"].astype(str).str.strip()
)

ebi_clean["susceptibility_std"] = (
    ebi_clean["susceptibility_std"].astype(str).str.strip().str.upper()
)

ebi_clean = ebi_clean[
    ebi_clean["susceptibility_std"].isin(["S", "I", "R"])
].copy()

ebi_clean["isolate_id"] = ebi_clean["BioSample_ID"].astype(str)
pheno_base = ebi_clean.drop_duplicates([
    "isolate_id",
    "organism_std",
    "antimicrobial_std",
    "susceptibility_std",
])

gene_base = ebi_clean.drop_duplicates([
    "isolate_id",
    "organism_std",
    "antimicrobial_std",
    "gene_symbol",
    "susceptibility_std",
])

pheno_denominators = (
    pheno_base
    .groupby([
        "organism_std",
        "antimicrobial_std",
        "susceptibility_std",
    ])
    .agg(total_isolates=("isolate_id", "nunique"))
    .reset_index()
)

den_wide = pheno_denominators.pivot_table(
    index=["organism_std", "antimicrobial_std"],
    columns="susceptibility_std",
    values="total_isolates",
    fill_value=0
).reset_index()

den_wide = den_wide.rename(columns={
    "S": "total_S",
    "I": "total_I",
    "R": "total_R",
})

for col in ["total_S", "total_I", "total_R"]:
    if col not in den_wide.columns:
        den_wide[col] = 0

gene_counts = (
    gene_base
    .groupby([
        "organism_std",
        "antimicrobial_std",
        "gene_symbol",
        "susceptibility_std",
    ])
    .agg(gene_isolates=("isolate_id", "nunique"))
    .reset_index()
)

gene_wide = gene_counts.pivot_table(
    index=["organism_std", "antimicrobial_std", "gene_symbol"],
    columns="susceptibility_std",
    values="gene_isolates",
    fill_value=0
).reset_index()

for col in ["S", "I", "R"]:
    if col not in gene_wide.columns:
        gene_wide[col] = 0

knowledge_summary = gene_wide.merge(
    den_wide,
    on=["organism_std", "antimicrobial_std"],
    how="left",
)

knowledge_summary["gene_total"] = (
    knowledge_summary["S"] +
    knowledge_summary["I"] +
    knowledge_summary["R"]
)

knowledge_summary["gene_non_s"] = (
    knowledge_summary["I"] + knowledge_summary["R"]
)
knowledge_summary["gene_S"] = (
    knowledge_summary["gene_total"] - knowledge_summary["gene_non_s"])

knowledge_summary["total_non_s"] = (
    knowledge_summary["total_I"] + knowledge_summary["total_R"])

knowledge_summary["total_all"] = (
    knowledge_summary["total_S"] +
    knowledge_summary["total_I"] +
    knowledge_summary["total_R"]
)

epsilon = 0.5

odds_non_s = (
    (knowledge_summary["gene_non_s"] + epsilon)
    / (knowledge_summary["total_non_s"] - knowledge_summary["gene_non_s"] + epsilon)
)

odds_s = (
    (knowledge_summary["S"] + epsilon)
    / (knowledge_summary["total_S"] - knowledge_summary["S"] + epsilon)
)

knowledge_summary["log_odds_non_s_vs_s"] = np.log(
    odds_non_s / odds_s
)

def compute_confidence_weight(n, total_s, total_ns, k=10):
    if pd.isna(n) or n <= 0:
        return 0.0
    w_n = np.sqrt(n / (n + k))
    min_group = np.minimum(total_s, total_ns)
    w_balance = np.sqrt(min_group / (min_group + k))
    return w_n * (0.5 + 0.5 * w_balance)


knowledge_summary["confidence_weight"] = knowledge_summary.apply(
    lambda row: compute_confidence_weight(
        row["gene_total"],
        row["total_S"],
        row["total_non_s"]
    ),
    axis=1
)

knowledge_summary["final_score"] = (
    knowledge_summary["log_odds_non_s_vs_s"] *
    knowledge_summary["confidence_weight"]
)

def evidence_level(n):
    if n >= 20:
        return "high"
    elif n >= 10:
        return "moderate"
    elif n >= 3:
        return "low"
    else:
        return "very_low"

knowledge_summary["evidence_level"] = (
    knowledge_summary["gene_total"].apply(evidence_level)
)

knowledge_summary["evidence_level"].value_counts()

knowledge_summary2 = knowledge_summary
q90 = knowledge_summary2["final_score"].quantile(0.9)
q75 = knowledge_summary2["final_score"].quantile(0.75)
q25 = knowledge_summary2["final_score"].quantile(0.25)
q10 = knowledge_summary2["final_score"].quantile(0.1)

def resistance_label(row):
    score = row["final_score"]
    n = row["gene_total"]

    if n < 3:
        return "insufficient"

    if score >= q90:
        return "strong_resistance"
    elif score >= q75:
        return "moderate_resistance"
    elif score <= q10:
        return "strong_susceptibility"
    elif score <= q25:
        return "moderate_susceptibility"
    else:
        return "weak_or_neutral"

knowledge_summary2["resistance_evidence_label"] = (
    knowledge_summary2.apply(resistance_label, axis=1)
)
knowledge_summary2["resistance_evidence_label"].value_counts()


knowledge_summary2["resistance_evidence_label"].value_counts()

label_cn_map = {
    "strong_resistance": "Strong evidence of resistance",
    "moderate_resistance": "Moderate evidence of resistance",
    "weak_or_neutral": "Weak or neutral",
    "moderate_susceptibility": "Moderate evidence of sensitive",
    "strong_susceptibility": "Strong evidence of sensitive",
    "insufficient": "Insufficient evidence",
}

knowledge_summary2["resistance_evidence_label_cn"] = (
    knowledge_summary2["resistance_evidence_label"].map(label_cn_map)
)

print(knowledge_summary2["resistance_evidence_label"].value_counts())

knowledge_summary2.to_csv('ebi_knowledge_summary_0730.csv', index=False)
# knowledge_summary_valid.to_csv('ebi_knowledge_summary_valid_0730.csv', index=False)
knowledge_summary=pd.read_csv('ebi_knowledge_summary_0730.csv')
ebi_clean.columns
ebi_clean = ebi_clean.drop(columns=['isolate_id'])

#############################################
import os
os.chdir('')
cols = list(ebi_clean.columns)

if 'gene_family' in cols and 'gene_symbol' in cols:
    cols.remove('gene_family')
    cols.insert(cols.index('gene_symbol') + 1, 'gene_family')
    ebi_clean = ebi_clean[cols]
ebi_clean.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/0730/EBI_CNSZ_AMR_0730.csv', index=False)

knowledge_summary=knowledge_summary2
valid_rate = len(knowledge_summary_valid) / len(knowledge_summary)

summary_overall = {
    "n_all_combinations": len(knowledge_summary),
    #"n_valid_combinations": len(knowledge_summary_valid),
    #"valid_rate": valid_rate,
    "n_species": knowledge_summary["organism_std"].nunique(),
    "n_antibiotics": knowledge_summary["antimicrobial_std"].nunique(),
    "n_genes": knowledge_summary["gene_symbol"].nunique(),
}

summary_overall
import pandas as pd
summary_df = pd.DataFrame([summary_overall])
summary_df.to_csv("01_overall_evidence_summary_deidentification.csv", index=False)

evidence_level_stats = (
    knowledge_summary
    .groupby("evidence_level")
    .size()
    .reset_index(name="n")
)

evidence_level_stats["ratio"] = (
    evidence_level_stats["n"] / evidence_level_stats["n"].sum()
)

evidence_level_stats.to_csv('02_evidence_level_distribution_deidentification.csv')

comparison_status_stats = (
    knowledge_summary
    .groupby("comparison_status")
    .size()
    .reset_index(name="n")
)

comparison_status_stats["ratio"] = (
    comparison_status_stats["n"] / comparison_status_stats["n"].sum()
)

comparison_status_stats.to_csv('03_comparison_status_distribution_deidentification.csv')


label_stats_valid = (
    knowledge_summary_valid
    .groupby("resistance_evidence_label")
    .size()
    .reset_index(name="n")
)

label_stats_valid["ratio"] = (
    label_stats_valid["n"] / label_stats_valid["n"].sum()
)

label_stats_valid.to_csv('04_resistance_label_distribution_deidentification.csv')

species_coverage = (
    knowledge_summary
    .groupby("organism_std")
    .agg(
        n_valid_pairs=("gene_symbol", "size"),
        n_antibiotics=("antimicrobial_std", "nunique"),
        n_genes=("gene_symbol", "nunique"),
        mean_final_score=("final_score", "mean"),
        max_final_score=("final_score", "max"),
        n_strong_resistance=(
            "resistance_evidence_label",
            lambda x: (x == "strong_resistance").sum()
        ),
        n_strong_susceptibility=(
            "resistance_evidence_label",
            lambda x: (x == "strong_susceptibility").sum()
        ),
    )
    .reset_index()
    .sort_values("n_valid_pairs", ascending=False)
)

species_coverage.head(30)
species_coverage.to_csv('05_species_coverage_deidentification.csv')

antibiotic_coverage = (
    knowledge_summary_valid
    .groupby("antimicrobial_std")
    .agg(
        n_valid_pairs=("gene_symbol", "size"),
        n_species=("organism_std", "nunique"),
        n_genes=("gene_symbol", "nunique"),
        mean_final_score=("final_score", "mean"),
        max_final_score=("final_score", "max"),
        n_strong_resistance=(
            "resistance_evidence_label",
            lambda x: (x == "strong_resistance").sum()
        ),
    )
    .reset_index()
    .sort_values("n_valid_pairs", ascending=False)
)

antibiotic_coverage.head(30)

antibiotic_coverage.to_csv('06_antibiotic_coverage_deidentification.csv')

if "evidence_n" not in knowledge_summary_valid.columns:
    knowledge_summary_valid["evidence_n"] = (
        knowledge_summary_valid["S"] +
        knowledge_summary_valid["R"]
    )

top_resistance_genes = (
    knowledge_summary_valid
    .query("resistance_evidence_label == 'strong_resistance'")
    .dropna(subset=["final_score"])   # 防 NaN
    .sort_values(
        ["final_score", "evidence_n"],
        ascending=[False, False]
    )
    .head(50)
)
cols = [
    "organism_std",
    "antimicrobial_std",
    "gene_symbol",
    "final_score",
    "evidence_n",
    "R_rate_among_gene_positive",
    "Non_S_rate_among_gene_positive",
    "gene_prevalence_in_Non_S",
    "gene_prevalence_in_S",
    "resistance_evidence_label_cn",
]

cols = [c for c in cols if c in top_resistance_genes.columns]
top_resistance_genes_display = top_resistance_genes[cols]

print(top_resistance_genes_display.head())

top_resistance_genes_display.to_csv(
    '07_top_strong_resistance_genes_deidentification.csv',
    index=False
)


top_susceptibility_genes = (
    knowledge_summary_valid
    .query("resistance_evidence_label == 'strong_susceptibility'")
    .sort_values(["final_score", "evidence_n"], ascending=[True, False])
    .head(50)
)
top_susceptibility_genes.to_csv('08_top_strong_susceptibility_genes_deidentification.csv')


species_antibiotic_summary = (
    knowledge_summary_valid
    .groupby(["organism_std", "antimicrobial_std"])
    .agg(
        n_genes=("gene_symbol", "nunique"),
        max_final_score=("final_score", "max"),
        mean_final_score=("final_score", "mean"),
        n_strong_resistance=(
            "resistance_evidence_label",
            lambda x: (x == "strong_resistance").sum()
        ),
        n_moderate_resistance=(
            "resistance_evidence_label",
            lambda x: (x == "moderate_resistance").sum()
        ),
        n_strong_susceptibility=(
            "resistance_evidence_label",
            lambda x: (x == "strong_susceptibility").sum()
        ),
    )
    .reset_index()
)

species_antibiotic_summary.head()
species_antibiotic_summary.to_csv('09_species_antibiotic_summary_deidentification.csv')


network_edges = knowledge_summary_valid[
    knowledge_summary_valid["resistance_evidence_label"].isin([
        "strong_resistance",
        "moderate_resistance"
    ])
][
    [
        "gene_symbol",
        "antimicrobial_std",
        "organism_std",
        "final_score",
        "evidence_n",
        "resistance_evidence_label",
    ]
].copy()

network_edges.to_csv('10_network_edges_gene_antibiotic_deidentification.csv')

df=pd.read_csv('EBI_CNSZ_knowledge_summary_valid_deidentification.csv')
df=knowledge_summary_valid

if "gene_prevalence_in_R" not in df.columns:
    df["gene_prevalence_in_R"] = df["R"] / df["total_R"]

if "gene_prevalence_in_S" not in df.columns:
    df["gene_prevalence_in_S"] = df["S"] / df["total_S"]

df["gene_prevalence_in_R"] = df["gene_prevalence_in_R"].fillna(0)
df["gene_prevalence_in_S"] = df["gene_prevalence_in_S"].fillna(0)
df_filtered = df[
    (df["resistance_evidence_label"] == "strong_resistance") &
    (df["gene_prevalence_in_R"] > 0.1) & 
    (df["gene_prevalence_in_S"] < 0.5)    
]
gene_counts = (
    df_filtered["gene_symbol"]
    .value_counts()
    #.head(50)
)
gene_counts.to_csv('strong_resistance_gene_counts.csv')
top20 = gene_counts.head(20)
import matplotlib.pyplot as plt

plt.figure(figsize=(10,6))

top20.plot(kind='bar')

plt.title('Top 20 Strong Resistance Genes')
plt.xlabel('Gene')
plt.ylabel('Count')

plt.xticks(rotation=45, ha='right')

plt.tight_layout()

plt.savefig('top20_resistance_genes.png', dpi=300)
plt.savefig('top20_resistance_genes.pdf', dpi=300)
plt.show()
