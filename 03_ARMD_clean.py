
#########################01_combined_culture_cohort
import os
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
df = pd.read_csv('./01_combined_culture_cohort2.csv')
map_df = pd.read_csv('./clean/organism_mapping.csv')
print(map_df.head())

mapping_dict = dict(zip(
    map_df['organism'].str.strip().str.upper(),
    map_df['organism_new'].str.strip()
))

df['organism_std'] = (
    df['organism']
    .str.strip()
    .str.upper()
    .map(mapping_dict)
    .fillna(df['organism']) 
)

df.loc[
    df['organism'].str.upper().isin(mapping_dict.keys()) == False,
    'organism'
].value_counts().head(20)

df['organism_std'].unique().tolist()

##########drug mapping
map_dr = pd.read_csv('./clean/antimicrobial_mapping.csv')
print(map_dr.head())

mapping_dict = dict(zip(
    map_dr['antibiotic'].str.strip().str.upper(),
    map_dr['antibiotic_new'].str.strip()
))

df['antibiotic_std'] = (
    df['antibiotic']
    .str.strip()
    .str.upper()
    .map(mapping_dict)
    .fillna(df['antibiotic'])   
)

df.loc[
    df['antibiotic'].str.upper().isin(mapping_dict.keys()) == False,
    'antibiotic'
].value_counts().head(20)

df['antibiotic_std'].unique().tolist()
df['antibiotic'].unique().tolist()

df['antibiotic_std'] = df['antibiotic_std'].str.replace('\xa0', ' ', regex=False)

df['antibiotic_std'] = df['antibiotic_std'].replace({
    'Ceftazidime/avibactam': 'ceftazidime/avibactam'
})
df['antibiotic_std'] = df['antibiotic_std'].replace({
    'NA': 'nan',
    'Ecim': 'ecim',
    'Mcim': 'mcim',
})
df['antibiotic_std'].unique().tolist()

df['antibiotic'].unique().tolist()


df.susceptibility.unique().tolist()
df.susceptibility.unique().value_counts
df['susceptibility'].value_counts


mapping = {
    'Susceptible': 'S',
    'Resistant': 'R',
    'Intermediate': 'I',
    'Susceptible dose-dependent': 'I',   
    'Non-susceptible': 'R',
    'Inconclusive': 'nan',  #NA
    'Null': 'nan',
    'NaN': 'nan',
    'Synergism': 'nan'

}

df['susceptibility_std'] = df['susceptibility'].map(mapping)

df['susceptibility_std'].value_counts(dropna=False)
import numpy as np
df['susceptibility_std'] = df['susceptibility_std'].replace(
    ['nan', 'NaN', 'NULL', 'Null', 'None', ''],
    np.nan
)
df['susceptibility_std'].value_counts(dropna=False)
df.to_csv('./01_combined_culture_cohort2_std.csv', index=False)


df = pd.read_csv('./01_combined_culture_cohort2_std.csv')
df_final=df


df = df[
    df['antibiotic_std'].notna() &
    df['susceptibility_std'].isin(['R','I','S'])
]

core_id_cols = [
    'anon_id',
    'pat_enc_csn_id_coded',
    'order_proc_id_coded',
    'order_time_jittered',
    'organism_std'
]

df_wide = dfd[
    core_id_cols + ['antibiotic_std', 'susceptibility_std']
].pivot(
    index=core_id_cols,
    columns='antibiotic_std',
    values='susceptibility_std'
).reset_index()


df_meta = df[core_id_cols + [
    'ordering_mode',
    'culture_description',
    'was_positive',
    'mult_org_ast',
    'has_AST',
    'prelim_AST',
    'AST_panel',
    'enzyme_class',
    'enzyme',
    'AST_code',
    'AST_inequality',
    'AST_val1',
    'AST_val2',
    'AST_pheno',
    'CLSI_2022_pheno',
    'source'
]].drop_duplicates(subset=core_id_cols)

df_final = df_wide.merge(
    df_meta,
    on=['anon_id', 'pat_enc_csn_id_coded', 'order_proc_id_coded', 'order_time_jittered', 'organism_std'],
    how='left'
)
df_final['antimicrobial_std']=df_final['antibiotic_std']
df_final.to_csv('./01_combined_culture_cohort2_std_clean_time_wide.csv', index=False)


##############################all############################################################################
import os
import pandas as pd
import polars as pl

cohort = pl.read_csv("01_combined_culture_cohort2_std_clean_time.csv")
original_count = cohort.height

keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]

demo = pl.read_csv("06_combined_microbiology_cultures_demographics2.csv")
adi = pl.read_csv("02_combined_microbiology_cultures_adi_scores2.csv")
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
duplicates = adi.filter(adi.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))
adi_cleaned = (
    adi
    .sort(
        by=["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded", "order_time_jittered", "adi_score"],
        descending=[False, False, False, False, True],
        nulls_last=True
    )
    .unique(subset=keys, keep="first")
)

check_ids_int = [int(i) for i in ["444133", "551755", "79735"]]
print(adi_cleaned.filter(pl.col("order_proc_id_coded").is_in(check_ids_int)))
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded", "order_time_jittered"]
adi_to_join = adi_cleaned.select([
    *keys,
    pl.col("adi_score"),
    pl.col("adi_state_rank"),
    pl.col("source").alias("source_adi") 
])

final_base_df = step1_df.join(adi_to_join, on=keys, how="left")

final_base_df.write_parquet("./merge_all/culture_cohort_demographics_adi.parquet")


import polars as pl
final_base_df = pl.read_parquet('./merge_all/culture_cohort_demographics_adi.parquet')

ward = pl.read_csv("12_combined_microbiology_cultures_ward_info2.csv")

keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
duplicates = ward.filter(adi.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))
ward_to_join = (
    ward
    .sort(keys, nulls_last=True)
    .unique(subset=keys, keep="first")
    .select([
        *keys,
        pl.col("^hosp_ward.*$"),
        pl.col("source").alias("source_ward")
    ])
)

master_v2 = final_base_df.join(ward_to_join, on=keys, how="left")

master_v2.write_parquet("./merge_all/culture_cohort_demographics_adi_ward.parquet")



labs = pl.read_csv("07_combined_microbiology_cultures_labs.csv")

keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]
duplicates = labs.filter(labs.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))
master_v3 = master_v2.join(
    labs_cleaned.rename({"source": "source_labs"}),
    on=keys,
    how="left"
)
master_v3.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs.parquet")


prior_med = pl.read_csv("10_combined_microbiology_cultures_prior_med2.csv")

keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
duplicates = prior_med.filter(prior_med.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))

prior_bugs_wide = (
    prior_med
    .filter(pl.col("prior_org").is_not_null())
    .group_by([*keys, "prior_org"])
    .agg(pl.len().alias("count"))
    .pivot(
        index=keys,
        on="prior_org",
        values="count"
    )
    .fill_null(0)
)

prior_bugs_wide = prior_bugs_wide.with_columns([
    pl.col(c).alias(f"hist_bug_{c}")
    for c in prior_bugs_wide.columns if c not in keys
]).select([*keys, pl.col("^hist_bug_.*$")])

master_v4 = master_v3.join(
    prior_bugs_wide.rename({"source": "source_prior_bugs"}),
    on=keys,
    how="left"
)


master_v4 = master_v4.with_columns([
    pl.col("^hist_bug_.*$").fill_null(0)
])

master_v4.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed.parquet")

bug_summary = master_v4.select(pl.col("^hist_bug_.*$")).sum() / master_v4.height

rare_bugs = [c for c in bug_summary.columns if bug_summary[c][0] < 0.0001] 
print(f"{len(rare_bugs)}")


vitals = pl.read_csv("13_combined_microbiology_cultures_vitals.csv")
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]
duplicates = vitals.filter(vitals.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))

import polars as pl
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]
feature_cols = [c for c in vitals.columns if c not in keys + ["source"]]

vitals_with_score = vitals.with_columns(
    pl.sum_horizontal([
        pl.col(c).is_not_null().cast(pl.Int32)
        for c in feature_cols
    ]).alias("info_score")
)

vitals_deduplicated = (
    vitals_with_score
    .sort(
        by=["info_score", "last_temp"],
        descending=[True, True],
        nulls_last=True
    )
    .unique(subset=keys, keep="first")
    .drop("info_score") 
)

vitals = vitals.with_columns([
    pl.col(c).replace("Null", None).cast(pl.Float64, strict=False)
    for c in feature_cols
])

vitals_final_features = vitals_deduplicated.select([
    *keys,
    pl.col("^last_.*$"),
    pl.col("^median_.*$") 
])

master_v5 = master_v4.join(vitals_final_features, on=keys, how="left")

master_v5.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals.parquet")

#########antibiotic_class_exposure
abx_exp = pl.read_csv("03_combined_microbiology_cultures_antibiotic_class_exposure2.csv")
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
duplicates = abx_exp.filter(abx_exp.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))

import polars as pl
abx_features = (
    abx_exp
    .filter(pl.col("drug_code").is_not_null()) 
    .group_by([*keys, "drug_code"])
    .agg(pl.col("time_to_culturetime").min())
    .pivot(
        index=keys,
        on="drug_code",
        values="time_to_culturetime"
    )
)

abx_final = abx_features.rename({
    col: f"abx_exp_{col}"
    for col in abx_features.columns if col not in keys
})

abx_exp_cleaned = abx_exp.filter(pl.col("time_to_culturetime") >= 0)

abx_features_cleaned = (
    abx_exp_cleaned
    .filter(pl.col("drug_code").is_not_null())
    .group_by([*keys, "drug_code"])
    .agg(pl.col("time_to_culturetime").min().alias("min_days"))
    .pivot(
        index=keys,
        on="drug_code",
        values="min_days"
    )
)


abx_final_cleaned = abx_features_cleaned.rename({
    col: f"abx_exp_{col}"
    for col in abx_features_cleaned.columns if col not in keys
})

master_v6 = master_v5.join(abx_final_cleaned, on=keys, how="left")

abx_cols = [c for c in master_v6.columns if c.startswith("abx_exp_")]

master_v6 = master_v6.with_columns([
    pl.col(c).fill_null(3650) for c in abx_cols
]).with_columns([
    (pl.col(c) < 3650).cast(pl.Int32).alias(f"any_{c}") for c in abx_cols
])
master_v6.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class.parquet")

###############04_combined_microbiology_cultures_antibiotic_subtype_exposure2
import polars as pl
import gc

sub_exp = pl.read_csv("04_combined_microbiology_cultures_antibiotic_subtype_exposure2.csv")
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
duplicates = sub_exp.filter(sub_exp.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))
sub_exp_cleaned = (
    sub_exp
    .filter(
        (pl.col("time_to_culturetime").is_not_null()) &
        (pl.col("time_to_culturetime") >= 0) &
        (pl.col("drug_code").is_not_null()) &
        (pl.col("drug_code").is_in(["null", "Null", "NULL", ""]).not_())
    )
)

if sub_exp_cleaned.height > 0:
    sub_features = (
        sub_exp_cleaned
        .group_by([*keys, "drug_code"])
        .agg(pl.col("time_to_culturetime").min().alias("min_days"))
        .pivot(
            index=keys,
            on="drug_code",
            values="min_days"
        )
    )

    sub_final = sub_features.rename({
        col: f"sub_exp_{col}"
        for col in sub_features.columns if col not in keys
    })

    print(f{sub_final.height}")
else:
    print("drug_code")

master_v7 = master_v6.join(sub_final, on=keys, how="left")

sub_cols = [c for c in master_v7.columns if c.startswith("sub_exp_")]

master_v7 = master_v7.with_columns([
    pl.col(c).fill_null(3650) for c in sub_cols
])

master_v7.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub.parquet")

cmbd = pl.read_csv("05_combined_microbiology_cultures_comorbidity2.csv")
cmbd = pl.read_csv(
    "05_combined_microbiology_cultures_comorbidity2.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    infer_schema_length=10000 
)

keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
duplicates = cmbd.filter(cmbd.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))
cmbd.columns


import polars as pl
import gc

cmbd_cleaned = (
    cmbd
    .filter(pl.col("comorbidity_component").is_not_null())
    .select([*keys, "comorbidity_component"])
)

cmbd_features = (
    cmbd_cleaned
    .with_columns(pl.lit(1).alias("val"))
    .group_by([*keys, "comorbidity_component"])
    .agg(pl.col("val").max()) 
    .pivot(
        index=keys,
        on="comorbidity_component",
        values="val"
    )
)

cmbd_final = cmbd_features.rename({
    col: f"cmbd_{col.lower().replace(' ', '_').replace(',', '').replace('-', '_')}"
    for col in cmbd_features.columns if col not in keys
})

master_v8 = master_v7.join(cmbd_final, on=keys, how="left")

cmbd_cols = [c for c in master_v8.columns if c.startswith("cmbd_")]
master_v8 = master_v8.with_columns([
    pl.col(c).fill_null(0).cast(pl.Int8)
    for c in cmbd_cols
])

master_v8.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub_comorbidityvv.parquet")

###########################microbiology_cultures_nursing_home_visit
import polars as pl
import gc
master_v8 = pl.read_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub_comorbidityvv.parquet")

nh_visits = pl.read_csv(
    "09_combined_microbiology_cultures_nursing_home_visits2.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    schema_overrides={
        "nursing_home_visit_culture": pl.Float64,
        "nursing_home_visit_time_to_culture": pl.Float64
    }
)

keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]

duplicates = nh_visits.filter(nh_visits.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))
nh_visits.columns
master_v9.columns
master_v9["anon_id"].unique()
master_v8[["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered","source"]].unique()

keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded", "order_time_jittered"]

time_col = "nursing_home_visit_culture"

nh_features = (
    nh_visits
    .filter(
        (pl.col(time_col).is_not_null()) &
        (pl.col(time_col) >= 0)
    )
    .group_by(keys)
    .agg([
        pl.lit(1).alias("nh_visit_binary"), 
        pl.col(time_col).min().alias("nh_recent_days") 
    ])
)

master_v9 = master_v8_compact.join(nh_features, on=keys, how="left")

master_v9 = master_v9.with_columns([
    pl.col("nh_visit_binary").fill_null(0).cast(pl.Int8),
    pl.col("nh_recent_days").fill_null(3650)
])

master_v9.write_parquet("./merge_all/ARMD_Master_v9_Final_Cleaned.parquet")

master_v9_clean = master_v9.unique(subset=keys)

null_stats = master_v9_clean.select([
    (pl.col(c).is_null().sum() / pl.count() * 100).alias(c)
    for c in master_v9_clean.columns
]).melt(variable_name="feature", value_name="null_percentage")

print(null_stats.sort("null_percentage", descending=True).head(30))
clean_features_count = null_stats.filter(pl.col("null_percentage") == 0).height

import polars as pl
master_v9 = pl.read_parquet('./merge_all/ARMD_Master_v9_Final_Cleaned.parquet')
master_v9.columns
master_v9[['organism_std', 'antibiotic_std', 'susceptibility_std']]

master_v9[["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded", "order_time_jittered","organism_std", "age", "gender", "median_wbc", "antibiotic_std", "susceptibility_std"]].unique()

duplicate_count = master_v9.height - master_v9.unique().height

master_v10 = master_v9.unique()

invalid_ast = master_v10.filter(
    pl.col("antibiotic_std").is_null() | pl.col("susceptibility_std").is_null()
).height
print(f"{invalid_ast}")

master_v11 = master_v10.filter(
    pl.col("antibiotic_std").is_not_null() &
    pl.col("susceptibility_std").is_not_null()
)

master_v11.write_parquet("master_v11_before_Pivot.parquet", compression="zstd")


keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded", "order_time_jittered"]
master_v12 = master_v11.with_columns(
    (pl.col("organism_std") + "_" + pl.col("antibiotic_std")).alias("bug_drug_pair")
)
# 执行 Pivot
ast_pivot_global = master_v12.pivot(
    values="susceptibility_std",
    index=keys,
    on="bug_drug_pair",
    aggregate_function="first"
)

print(f"{ast_pivot_global.shape}")

clinical_features = master_v11[
    keys + [c for c in master_v11.columns if c.startswith(("age", "gender", "cmbd_", "med_", "lab_"))]
].unique(subset=keys)

exclude_for_unique = [
    "antibiotic_std", "susceptibility_std", "organism_std",
    "bug_drug_pair", "antibiotic", "susceptibility", "organism"
]

clinical_features_full = master_v11.select([
    col for col in master_v11.columns if col not in exclude_for_unique
]).unique(subset=keys)

omni_armd_final = ast_pivot_global.join(clinical_features_full, on=keys, how="left")
omni_armd_final.write_parquet("omni_armd_final.parquet", compression="zstd")
threshold = 10
non_null_counts = omni_armd_final.select(
    [pl.all().count() - pl.all().null_count()]
)

meaningful_cols = [
    col for col in omni_armd_final.columns
    if col in keys or (omni_armd_final.select(pl.col(col).count() - pl.col(col).null_count()).item() >= threshold)
]

omni_armd_compact = omni_armd_final.select(meaningful_cols)

missing_stats = omni_armd_final.select([
    (pl.col(c).null_count() / pl.count() * 100).alias(c)
    for c in omni_armd_final.columns
])

missing_rate_df = missing_stats.transpose(
    include_header=True,
    header_name="column_name",
    column_names=["missing_rate_pct"]
).sort("missing_rate_pct", descending=True)

clinical_cols = clinical_features_full.columns
clinical_missing = missing_rate_df.filter(pl.col("column_name").is_in(clinical_cols))
high_missing_clinical = clinical_missing.filter(pl.col("missing_rate_pct") > 50)
label_missing = missing_rate_df.filter(
    ~pl.col("column_name").is_in(clinical_cols) & ~pl.col("column_name").is_in(keys)
)

raw_final_cols = keys + clinical_cols + valid_labels

final_cols_unique = list(dict.fromkeys(raw_final_cols))

existing_cols = [c for c in final_cols_unique if c in omni_armd_final.columns]
omni_armd_v12 = omni_armd_final.select(existing_cols)

final_label_count = len([c for c in valid_labels if c in omni_armd_v12.columns])


omni_armd_v12.write_parquet("omni_armd_v1_2_final_compact.parquet")



