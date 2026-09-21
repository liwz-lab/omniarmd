import pandas as pd
import polars as pl
pd.set_option('display.max_columns', None)
# Set the display width to prevent automatic line wrapping
pd.set_option('display.width', 1000)
master_v9 = pl.read_parquet(
    './bridge_deidentification_mapping.parquet'
)
master_v9.columns
master_v9[['organism_std', 'antimicrobial_std', 'susceptibility_std']]

master_v9[
    ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded",
     "order_time_jittered", "organism_std", "age", "gender",
     "median_wbc", "antimicrobial_std", "susceptibility_std"]
].unique()

duplicate_count = master_v9.height - master_v9.unique().height
print(f"Completely duplicated redundant rows: {duplicate_count}")
print(f"Duplicate rate: {duplicate_count / master_v9.height:.2%}")

master_v10 = master_v9.unique()
print(f"Rows after deduplication: {master_v10.height}")

import polars as pl

master_v10 = master_v10.filter(
    pl.col("organism_std").is_not_null() &

    ~pl.col("organism_std")
    .str.strip_chars()
    .str.to_lowercase()
    .str.replace_all(r"\s+", "")
    .is_in([
        "na", "nan", "null", "none", "",
        "n/a", "na ", " null", "nan "
    ])
)

master_v10 = master_v10.filter(
    ~pl.col("antimicrobial_std")
    .str.to_lowercase()
    .is_in(["ecim", "mcim"])
)

invalid_ast = master_v10.filter(
    pl.col("antimicrobial_std").is_null() |
    pl.col("susceptibility_std").is_null() |
    pl.col("organism_std").is_null()
).height

print(f"Invalid AST records: {invalid_ast}")

master_v11 = master_v10.filter(
    pl.col("antimicrobial_std").is_not_null() &
    pl.col("susceptibility_std").is_not_null()
)

print(f"Final number of valid rows entering Pivot: {master_v11.height}")


df = master_v10

df = df.with_columns(
    pl.col("susceptibility_std").replace(
        "I",
        "NS",
        default=pl.col("susceptibility_std")
    )
)

df = df.with_columns(
    pl.col("susceptibility_std").replace(
        "I",
        "NS",
        default=pl.col("susceptibility_std")
    )
)
df = df.with_columns([
    (
        pl.col("organism_std") +
        "_" +
        pl.col("antimicrobial_std")
    ).alias("org_abx"),

    (pl.col("susceptibility_std") == "NS")
    .cast(pl.Int8)
    .alias("label")
])

clinical_cols = [
    'anon_id',
    'pat_enc_csn_id_coded',
    'order_proc_id_coded',
    'order_time_jittered',
    'order_time_jittered_std',
    "age",
    'culture_description',
    'source',
    "adi_score",
    "adi_state_rank",
    'hosp_ward_IP',
    'hosp_ward_OP',
    'hosp_ward_ER',
    'hosp_ward_ICU',
    'order_time_year',
    'order_time_month',
    'Period_Day',
    "median_wbc",
    'median_neutrophils',
    'median_lymphocytes',
    "median_cr",
    "median_hgb",
    "median_plt",
    'median_hco3',
    'median_bun',
    "median_lactate",
    "median_procalcitonin",
    "median_temp",
    "median_sysbp",
    "median_diasbp",
    "median_heartrate",
    "median_resprate",
    'has_prior_procedure',
    'nh_visit_binary',
    'nh_recent_days',
    'clinical_R_rate',
]

prior_inf_features = [
    # Burden
    "has_prior_infecting_organism",
    "prior_infecting_organism_n_records",
    "prior_infecting_organism_n_unique",

    # Time signal
    "prior_infecting_organism_median_days",
    "prior_infecting_organism_min_days",
    'nearest_prior_infecting_organism',
    "nearest_prior_infecting_organism_days",
    'nearest_prior_infecting_organism_source',
]

procedure_features = [
    # Exposure burden
    "has_prior_procedure",
    "prior_procedure_n_records",
    "prior_procedure_n_unique",

    # Timing (safe version)
    "prior_procedure_median_time_to_culture",
    "prior_procedure_min_time_to_culture"
]

abx_cols = [
    c for c in df.columns
    if c.startswith("prior_med_")
]

abx_subclass_cols = [
    c for c in df.columns
    if c.startswith("sub_exp_")
]

#ebi_cols = [c for c in df.columns if c.startswith("ebi_")]

ebi_cols = [

    "ebi_gene_count",
    "ebi_mean_final_score",
    "ebi_mean_Non_S_rate_among_gene_positive",
    "ebi_max_gene_prevalence_in_Non_S",
    "ebi_evidence_n_sum",
    "ebi_evidence_n_mean",
    "ebi_n_strong_resistance_genes",
    "ebi_n_weak_neutral_resistance_genes",
    # "ebi_n_weak_resistance_genes",
    # "ebi_n_neutral_genes",
    "ebi_dominant_label_cn",
    "ebi_knowledge_matched"
]

cmbd_cols = [
    c for c in df.columns
    if c.startswith("cmbd_")
]

df = df.with_columns(
    pl.sum_horizontal([
        pl.col(c)
        for c in cmbd_cols
    ]).alias("comorbidity_score")
)

feature_cols = (
    clinical_cols +
    abx_cols +
    #abx_class_cols +
    abx_subclass_cols +
    prior_inf_features +
    prior_inf_features +
    ["comorbidity_score"] +
    ebi_cols
)

feature_cols = [
    c for c in feature_cols
    if c in df.columns
]

feature_cols = list(dict.fromkeys(feature_cols))

print("rows:", df.shape[0])
print("cols:", df.shape[1])
print("duplicate cols:", len(df.columns) - len(set(df.columns)))


df2 = df[
    feature_cols +
    ['organism_std'] +
    ['antimicrobial_std'] +
    ['org_abx'] +
    ['label']
]

df2 = df2.rename({
    c: c.lower()
    for c in df2.columns
})

df2.write_csv(
    "omni_bridge_h2o_deidentification.csv",
    batch_size=100000
)


df = pd.read_csv(
    "merge2/merge3/h2o_automl_inputs/omni_bridge_h2o_deidentification0730.csv"
)
