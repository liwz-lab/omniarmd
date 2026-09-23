#################################microbiology_cultures_priorprocedures
import os
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
ARMD=pd.read_csv('./11_combined_microbiology_cultures_prior_procedures2.csv')
CNSZ=pd.read_excel('./12.microbiology_cultures_priorprocedures.xlsx')
ARMD.head()
CNSZ.head()
CNSZ["order_time_jittered"] = CNSZ["order_time_jittered_std"]
CNSZ["source"] = "CNSZ"
CNSZ.to_csv('./12.microbiology_cultures_priorprocedures_std.csv')
target_columns = [
    "anon_id",
    "pat_enc_csn_id_coded",
    "order_proc_id_coded",
    "order_time_jittered",
    "order_time_jittered_std",
    "procedure_description",
    'procedure_time_to_culturetime',
    "source",
]
df_armd_sub = ARMD[target_columns].copy()
# df_armd_sub['source'] = 'ARMD'
df_cnsz_sub = CNSZ[target_columns].copy()
merged_df = pd.concat([df_armd_sub, df_cnsz_sub], ignore_index=True)
merged_df.to_csv('./merge3/11_combined_microbiology_cultures_prior_procedures3.csv')

#########################03_combined_microbiology_cultures_antibiotic_class_exposure2
import os
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
ARMD=pd.read_csv('./03_combined_microbiology_cultures_antibiotic_class_exposure2.csv')
CNSZ=pd.read_csv('./03.microbiology_cultures_prior_med_std.csv')
CNSZ['pat_enc_csn_id_coded'].unique()
CNSZ.to_csv('./03.microbiology_cultures_prior_med_std_time.csv')

cnsz_mapping = CNSZ[
    [
        "anon_id",
        "pat_enc_csn_id_coded",
        "order_proc_id_coded",
        "order_time_jittered_std",
    ]
].drop_duplicates(subset=["anon_id", "pat_enc_csn_id_coded"])

CNSZ_subset = CNSZ.drop(
    columns=["order_proc_id_coded", "order_time_jittered_std"], errors="ignore"
)

CNSZ_cleaned = pd.merge(
    CNSZ_subset,
    cnsz_mapping,
    on=["anon_id", "pat_enc_csn_id_coded"],
    how="inner",
)

CNSZ_cleaned.head()

shared_anon_ids = set(CNSZ["anon_id"]).intersection(set(cnsz_mapping["anon_id"]))
CNSZ_intersected = CNSZ[CNSZ["anon_id"].isin(shared_anon_ids)].copy()
CNSZ_intersected = CNSZ_intersected.drop(
    columns=["order_proc_id_coded", "order_time_jittered_std"], errors="ignore"
)
CNSZ_cleaned = pd.merge(
    CNSZ_intersected, cnsz_mapping, on="anon_id", how="left"
)

mismatches = (
    CNSZ_cleaned["pat_enc_csn_id_coded_x"].astype(str)
    != CNSZ_cleaned["pat_enc_csn_id_coded_y"].astype(str)
).sum()

CNSZ_cleaned["pat_enc_csn_id_coded"] = CNSZ_cleaned["pat_enc_csn_id_coded_x"]
CNSZ_cleaned = CNSZ_cleaned.drop(
    columns=["pat_enc_csn_id_coded_x", "pat_enc_csn_id_coded_y"],
    errors="ignore",
)

CNSZ_cleaned["order_time_jittered_std"] = pd.to_datetime(
    CNSZ_cleaned["order_time_jittered_std"]
)

CNSZ_cleaned["medication_time_to_culturetime"] = (
    CNSZ_cleaned["order_time_jittered_std"] - CNSZ_cleaned["医嘱时间"]
).dt.total_seconds() / 86400.0


CNSZ_cleaned.head()
CNSZ_cleaned.to_csv('./03.microbiology_cultures_prior_med_std_time_anon.csv')

CNSZ['order_time_jittered'] = CNSZ['order_time_jittered_std']
CNSZ['antibiotic_class'] = CNSZ['antibiotic_class_std']
ARMD['antibiotic_class'] = ARMD['antibiotic_class_std']
CNSZ['antibiotic_class'].unique()

target_columns = [
    "anon_id",
    "pat_enc_csn_id_coded",
    "order_proc_id_coded",
    "order_time_jittered",
    "order_time_jittered_std",
    "antibiotic_class",
    'time_to_culturetime',
    "source",
]

df_armd_sub = ARMD[target_columns].copy()

df_cnsz_sub = CNSZ[target_columns].copy()

merged_df = pd.concat([df_armd_sub, df_cnsz_sub], ignore_index=True)
print(merged_df.head(3))
print(merged_df.tail(3))
merged_df.to_csv('./merge3/03_combined_microbiology_cultures_antibiotic_class_exposure3.csv')

##################################microbiology_cultures_antibiotic_subtype_exposure.csv
import os
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
ARMD=pd.read_csv('04_combined_microbiology_cultures_antibiotic_subtype_exposure2.csv')
ARMD2=pd.read_csv('03_combined_microbiology_cultures_antibiotic_class_exposure2_std.csv')
ARMD['order_time_jittered_std']=ARMD2['order_time_jittered_std']
ARMD['medication_name_clean_std']=ARMD2['medication_name_clean_std']
ARMD['antibiotic_class_std'] = ARMD2['antibiotic_class_std']
CNSZ=pd.read_csv('03.microbiology_cultures_prior_med_std_time_anon_antibiotic_class_std.csv')
ARMD.head()
ARMD.loc[ARMD['source'] == 'Stanford', 'antibiotic_subtype'].unique()
ARMD['antibiotic_subtype_category'].unique()
ARMD.loc[ARMD['source'] == 'Stanford', 'antibiotic_subtype_category'].unique()
CNSZ.head()
CNSZ['medication_name_clean_std'].unique()

#########
ARMD['antibiotic_subtype'] = ARMD['antibiotic_subtype_std']
ARMD['antibiotic_subtype_category'] = ARMD['antibiotic_subtype_category_std']
target_columns = [
    "anon_id",
    "pat_enc_csn_id_coded",
    "order_proc_id_coded",
    "order_time_jittered",
    "order_time_jittered_std",
    "antibiotic_subtype",
    "antibiotic_subtype_category",
    'time_to_culturetime',
    "source",
]
df_armd_sub = ARMD[target_columns].copy()

df_cnsz_sub = CNSZ[target_columns].copy()
merged_df = pd.concat([df_armd_sub, df_cnsz_sub], ignore_index=True)
print(merged_df.head(3))
print(merged_df.tail(3))

merged_df.to_csv('./merge3/04_combined_microbiology_cultures_antibiotic_subtype_exposure3.csv')

##########################################08_combined_microbiology_cultures_microbial_resistance2
import os
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
ARMD=pd.read_csv('08_combined_microbiology_cultures_microbial_resistance2.csv')
ARMD2=pd.read_csv('03_combined_microbiology_cultures_antibiotic_class_exposure2_std.csv')
ARMD['order_time_jittered_std']=ARMD2['order_time_jittered_std']
ARMD['medication_name_clean_std']=ARMD2['medication_name_clean_std']
ARMD['antibiotic_class_std'] = ARMD2['antibiotic_class_std']
CNSZ=pd.read_csv('03.microbiology_cultures_prior_med_std_time_anon_antibiotic_class_std.csv')
ARMD.head()
ARMD.loc[ARMD['source'] == 'Stanford', 'antibiotic'].unique()
ARMD.loc[ARMD['source'] == 'Stanford', 'organism'].unique()
ARMD['antibiotic'].unique()
ARMD['organism'].unique()
ARMD.loc[ARMD['source'] == 'Stanford', 'antibiotic_subtype_category'].unique()
CNSZ.head()
CNSZ['medication_name_clean_std'].unique()
ARMD.to_csv('08_combined_microbiology_cultures_microbial_resistance2_resistant_antibiotic_std_organism_std.csv')
ARMD['resistant_organism_std']=ARMD['organism_std']

import pandas as pd
cols_to_save = [
    "anon_id",
    "pat_enc_csn_id_coded",
    "order_proc_id_coded",
    "order_time_jittered",
    "order_time_jittered_std",
    "resistant_antibiotic_std",
    "resistant_organism_std",
    'resistant_time_to_culturetime',
    "source"
]

ARMD_subset = ARMD[cols_to_save]
ARMD_subset.to_csv('08_combined_microbiology_cultures_microbial_resistance3.csv')

###########################13_combined_microbiology_cultures_vitals
import os
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
ARMD=pd.read_csv('13_combined_microbiology_cultures_vitals.csv')
CNSZ=pd.read_csv('07.microbiology_cultures_vitals.csv')
#CNSZ=pd.read_csv('01_culture_cohort_std.csv')
CNSZ2=pd.read_csv('01_culture_cohort_std_demographics_nursing_adi_all_rename_organism_antibiotic_demographics_ward.csv')
ARMD.head()
CNSZ.head()
CNSZ_final['order_time_jittered']=CNSZ_final['order_time_jittered_std']
CNSZ_final['order_time_jittered']
CNSZ_final.to_csv('07.microbiology_cultures_vitals_std.csv')

CNSZ=CNSZ_final
CNSZ['source']='CNSZ'
ARMD.head()
ARMD['source'].unique()
common_cols = [c for c in CNSZ.columns if c in ARMD.columns]

target_columns = [
    'anon_id', 'pat_enc_csn_id_coded', 'Q25_heartrate', 'Q75_heartrate', 'median_heartrate', 'Q25_resprate',
    'Q75_resprate', 'median_resprate', 'Q25_temp', 'Q75_temp', 'median_temp', 'Q25_sysbp', 'Q75_sysbp', 'median_sysbp',
    'Q25_diasbp', 'Q75_diasbp', 'median_diasbp', 'first_diasbp', 'last_diasbp', 'last_sysbp', 'first_sysbp',
    'last_temp', 'first_temp', 'last_resprate', 'first_resprate', 'last_heartrate', 'first_heartrate',
    'order_proc_id_coded', 'source'
]
df_armd_sub = ARMD[target_columns].copy()
# df_armd_sub['source'] = 'ARMD' 

df_cnsz_sub = CNSZ[target_columns].copy()

merged_df = pd.concat([df_armd_sub, df_cnsz_sub], ignore_index=True)

merged_df.to_csv('./merge3/13_combined_microbiology_cultures_vitals3.csv')

#############################14_combined_microbiology_cultures_prior_infecting_organism2.csv
import os
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
ARMD=pd.read_csv('14_combined_microbiology_cultures_prior_infecting_organism2.csv')
CNSZ=pd.read_csv('07.microbiology_cultures_vitals.csv')
ARMD.head()
CNSZ.head()
ARMD['prior_organism'].unique()
ARMD.to_csv('14_combined_microbiology_cultures_prior_infecting_organism2_std.csv')
ARMD.head()
cols_to_keep = [
    "anon_id",
    "pat_enc_csn_id_coded",
    "order_proc_id_coded",
    "order_time_jittered",
    "order_time_jittered_std",
    "prior_organism",
    "prior_infecting_organism_days_to_culture",
    "source",
]
ARMD_subset = ARMD[cols_to_keep]
ARMD_subset.to_csv('14_combined_microbiology_cultures_prior_infecting_organism3.csv')

##############################all############################################################################
import os
import pandas as pd
import polars as pl

cohort = pl.read_csv("01_combined_culture_cohort3.csv")
cohort = pl.read_csv(
    "01_combined_culture_cohort3.csv",
    schema_overrides={
        "order_proc_id_coded": pl.Utf8
    }
)
original_count = cohort.height

keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]

demo = pl.read_csv("06_combined_microbiology_cultures_demographics3.csv", schema_overrides={"order_proc_id_coded": pl.Utf8})
demo = demo.unique(subset=keys, keep="first")
step1_df = cohort.join(demo, on=keys, how="left")
adi = pl.read_csv("02_combined_microbiology_cultures_adi_scores3.csv", schema_overrides={"order_proc_id_coded": pl.Utf8})
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
ward = pl.read_csv("12_combined_microbiology_cultures_ward_info3.csv",schema_overrides={"order_proc_id_coded": pl.Utf8})
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
labs_cleaned = labs.unique(subset=keys, keep="first")

master_v3 = master_v2.join(
    labs_cleaned.rename({"source": "source_labs"}),
    on=keys,
    how="left",
    suffix="_labs"
)
master_v3.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs.parquet")

prior_med = pl.read_csv("10_combined_microbiology_cultures_prior_med3.csv",schema_overrides={"order_proc_id_coded": pl.Utf8})
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
duplicates = prior_med.filter(prior_med.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))

prior_bugs_wide = (
    prior_med
    .filter(pl.col("medication_name").is_not_null())
    .with_columns(pl.col("source").alias("source_prior_med"))  # 先改名
    .group_by([*keys, "medication_name", "source_prior_med"])
    .agg(pl.count().alias("count"))
    .pivot(
        index=keys,
        columns="medication_name",
        values="count"
    )
    .fill_null(0)
)

prior_bugs_wide = prior_bugs_wide.with_columns([
    pl.col(c).alias(f"prior_med_{c}")
    for c in prior_bugs_wide.columns if c not in keys
]).select([*keys, pl.col("^prior_med_.*$")])

prior_bugs_wide = prior_bugs_wide.with_columns(
    pl.col("order_proc_id_coded").cast(pl.Utf8)
)

master_v4 = master_v3.join(
    prior_bugs_wide,
    on=keys,
    how="left"
)

master_v4 = master_v4.with_columns([
    pl.col("^prior_med_.*$").fill_null(0)
])

master_v4.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed.parquet")
bug_summary = master_v4.select(pl.col("^prior_med_.*$")).sum() / master_v4.height
rare_bugs = [c for c in bug_summary.columns if bug_summary[c][0] < 0.0001] # 覆盖率低于万分之一
print(f"prior_med数量: {len(rare_bugs)}")

vitals = pl.read_csv("13_combined_microbiology_cultures_vitals3.csv",schema_overrides={"order_proc_id_coded": pl.Utf8})

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

vitals_final_features = vitals_deduplicated.select([
    *keys,
    pl.col("^last_.*$"),
    pl.col("^median_.*$")
])

master_v5 = master_v4.join(vitals_final_features, on=keys, how="left")
master_v5.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals.parquet")

#########antibiotic_class_exposure
abx_exp = pl.read_csv("03_combined_microbiology_cultures_antibiotic_class_exposure3.csv",schema_overrides={"order_proc_id_coded": pl.Utf8})
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
duplicates = abx_exp.filter(abx_exp.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))

import polars as pl
abx_features = (
    abx_exp
    .filter(pl.col("antibiotic_class").is_not_null()) # 过滤掉没有药物代码的记录
    .group_by([*keys, "antibiotic_class"])
    .agg(pl.col("time_to_culturetime").min()) # 聚合：取最近的一次暴露
    .pivot(
        index=keys,
        on="antibiotic_class",
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
    .filter(pl.col("antibiotic_class").is_not_null())
    .group_by([*keys, "antibiotic_class"])
    .agg(pl.col("time_to_culturetime").min().alias("min_days"))
    .pivot(
        index=keys,
        on="antibiotic_class",
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
sub_exp = pl.read_csv("04_combined_microbiology_cultures_antibiotic_subtype_exposure3.csv",schema_overrides={"order_proc_id_coded": pl.Utf8})
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
duplicates = sub_exp.filter(sub_exp.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))
sub_exp_cleaned = (
    sub_exp
    .filter(
        (pl.col("time_to_culturetime").is_not_null()) &
        (pl.col("time_to_culturetime") >= 0) &
        (pl.col("antibiotic_subtype").is_not_null()) &
        (pl.col("antibiotic_subtype").is_in(["null", "Null", "NULL", ""]).not_())
    )
)

if sub_exp_cleaned.height > 0:
    sub_features = (
        sub_exp_cleaned
        .group_by([*keys, "antibiotic_subtype"])
        .agg(pl.col("time_to_culturetime").min().alias("min_days"))
        .pivot(
            index=keys,
            on="antibiotic_subtype",
            values="min_days"
        )
    )

    sub_final = sub_features.rename({
        col: f"sub_exp_{col}"
        for col in sub_features.columns if col not in keys
    })
if sub_final.height > 0:
    print(f"{sub_final.height}")
else:
    print("drug_code")

master_v7 = master_v6.join(sub_final, on=keys, how="left")

sub_cols = [c for c in master_v7.columns if c.startswith("sub_exp_")]

master_v7 = master_v7.with_columns([
    pl.col(c).fill_null(3650) for c in sub_cols
])

master_v7.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub.parquet")


import polars as pl
import gc
master_v7= pl.read_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub.parquet")
cmbd = pl.read_csv(
    "05_combined_microbiology_cultures_comorbidity3.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    infer_schema_length=10000 
)

import polars as pl
cmbd = pl.read_csv(
    "05_combined_microbiology_cultures_comorbidity3.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    infer_schema_length=10000,
    dtypes={
        "order_proc_id_coded": pl.Utf8
    }
)

keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
duplicates = cmbd.filter(cmbd.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))
cmbd.columns


import polars as pl
import gc

cmbd_cleaned = (
    cmbd
    .filter(pl.col("comorbidity_mid").is_not_null())
    .select([*keys, "comorbidity_mid"])
)

cmbd_features = (
    cmbd_cleaned
    .with_columns(pl.lit(1).alias("val"))
    .group_by([*keys, "comorbidity_mid"])
    .agg(pl.col("val").max()) 
    .pivot(
        index=keys,
        on="comorbidity_mid",
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
master_v8.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub_comorbidity.parquet")

###########################microbiology_cultures_nursing_home_visit
import polars as pl
import gc

master_v8 = pl.read_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub_comorbidityvv.parquet")
import polars as pl

nh_visits = pl.read_csv(
    "09_combined_microbiology_cultures_nursing_home_visits3.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    infer_schema_length=10000,
    dtypes={
        "order_proc_id_coded": pl.Utf8, 
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

master_v9 = master_v8.join(nh_features, on=keys, how="left")

master_v9 = master_v9.with_columns([
    pl.col("nh_visit_binary").fill_null(0).cast(pl.Int8),
    pl.col("nh_recent_days").fill_null(3650)
])
master_v9.write_parquet("./merge_all/ARMD_Master_v9_Final_Cleaned.parquet")

#####################################08_combined_microbiology_cultures_microbial_resistance3.csv
import polars as pl

microbial_resistance = pl.read_csv(
    "08_combined_microbiology_cultures_microbial_resistance3.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    infer_schema_length=10000,
    dtypes={
        "order_proc_id_coded": pl.Utf8,
    }
)
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]
duplicates = microbial_resistance.filter(microbial_resistance.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]
microbial_clean = microbial_resistance.with_columns([
    pl.col("anon_id").cast(pl.Utf8),
    pl.col("pat_enc_csn_id_coded").cast(pl.Int64),
    pl.col("order_proc_id_coded").cast(pl.Utf8),
])

microbial_features = (
    microbial_clean
    .group_by(keys)
    .agg([
        pl.len().alias("microbial_resistance_n_records"),

        pl.col("resistant_antibiotic_std")
          .drop_nulls()
          .unique()
          .sort()
          .alias("resistant_antibiotic_list"),

        pl.col("resistant_organism_std")
          .drop_nulls()
          .unique()
          .sort()
          .alias("resistant_organism_list"),

        pl.col("resistant_time_to_culturetime")
          .min()
          .alias("resistance_min_time_to_culture"),

        pl.col("resistant_time_to_culturetime")
          .max()
          .alias("resistance_max_time_to_culture"),

        pl.col("source")
          .drop_nulls()
          .unique()
          .sort()
          .alias("resistance_source_list"),
    ])
    .with_columns([
        (pl.col("microbial_resistance_n_records") > 0)
        .cast(pl.Int8)
        .alias("has_microbial_resistance")
    ])
)

master_v10= master_v9.join(
    microbial_features,
    on=keys,
    how="left"
)

master_v10.write_parquet(
    "./merge_all/master_v10_with_microbial_resistance.parquet"
)

##########################11_combined_microbiology_cultures_prior_procedures3.csv
import polars as pl
prior_procedures = pl.read_csv(
    "11_combined_microbiology_cultures_prior_procedures3.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    infer_schema_length=10000,
    schema_overrides={
        "order_proc_id_coded": pl.Utf8,
        "procedure_time_to_culturetime": pl.Float64
    }
)

keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
keys = [
    "anon_id",
    "pat_enc_csn_id_coded",
    "order_proc_id_coded",
]

prior_procedures2 = prior_procedures.with_columns([
    pl.col("anon_id").cast(pl.Utf8),
    pl.col("pat_enc_csn_id_coded").cast(pl.Int64),
    pl.col("order_proc_id_coded").cast(pl.Utf8),
])

prior_procedure_features = (
    prior_procedures2
    .group_by(keys)
    .agg([
        pl.len().alias("prior_procedure_n_records"),

        pl.col("procedure_description")
          .drop_nulls()
          .unique()
          .sort()
          .alias("prior_procedure_list"),

        pl.col("procedure_description")
          .drop_nulls()
          .n_unique()
          .alias("prior_procedure_n_unique"),

        pl.col("procedure_time_to_culturetime")
          .min()
          .alias("prior_procedure_min_time_to_culture"),

        pl.col("procedure_time_to_culturetime")
          .max()
          .alias("prior_procedure_max_time_to_culture"),

        pl.col("procedure_time_to_culturetime")
          .median()
          .alias("prior_procedure_median_time_to_culture"),

        pl.col("source")
          .drop_nulls()
          .unique()
          .sort()
          .alias("prior_procedure_source_list"),
    ])
    .with_columns([
        (pl.col("prior_procedure_n_records") > 0)
        .cast(pl.Int8)
        .alias("has_prior_procedure")
    ])
)

master_v11 = master_v10.join(
    prior_procedure_features,
    on=keys,
    how="left"
)
master_v11.write_parquet(
    "./merge_all/master_v11_prior_procedure_features.parquet"
)

#################################14_combined_microbiology_cultures_prior_infecting_organism3.csv
import polars as pl
infecting_organism2 = pl.read_csv(
    "14_combined_microbiology_cultures_prior_infecting_organism3.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    infer_schema_length=10000,
    schema_overrides={
        "order_proc_id_coded": pl.Utf8,
    }
)
infecting_organism = pl.read_csv(
    "../14_combined_microbiology_cultures_prior_infecting_organism2_std.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    infer_schema_length=10000,
    schema_overrides={
        "order_proc_id_coded": pl.Utf8,
    }
)
infecting_organism2 = infecting_organism2.with_columns(
    infecting_organism["prior_org_std"].alias("prior_organism")
)
infecting_organism2.write_csv(
    "14_combined_microbiology_cultures_prior_infecting_organism3.csv"
)
infecting_organism=infecting_organism2
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]

infecting_organism2 = infecting_organism.with_columns([
    pl.col("anon_id").cast(pl.Utf8),
    pl.col("pat_enc_csn_id_coded").cast(pl.Int64),
    pl.col("order_proc_id_coded").cast(pl.Utf8),
    pl.col("prior_organism").cast(pl.Utf8),
])

days_col = "prior_infecting_organism_days_to_culture"

infecting_organism_features = (
    infecting_organism2
    .group_by(keys)
    .agg([
        pl.len().alias("prior_infecting_organism_n_records"),

        pl.col("prior_organism")
          .drop_nulls()
          .unique()
          .sort()
          .alias("prior_infecting_organism_list"),

        pl.col("prior_organism")
          .drop_nulls()
          .n_unique()
          .alias("prior_infecting_organism_n_unique"),

        pl.col(days_col)
          .min()
          .alias("prior_infecting_organism_min_days"),

        pl.col(days_col)
          .max()
          .alias("prior_infecting_organism_max_days"),

        pl.col(days_col)
          .median()
          .alias("prior_infecting_organism_median_days"),

        pl.col("source")
          .drop_nulls()
          .unique()
          .sort()
          .alias("prior_infecting_organism_source_list"),
    ])
    .with_columns([
        (pl.col("prior_infecting_organism_n_records") > 0)
        .cast(pl.Int8)
        .alias("has_prior_infecting_organism")
    ])
)

nearest_prior_infecting_organism = (
    infecting_organism2
    .filter(
        pl.col(days_col).is_not_null() &
        (pl.col(days_col) >= 0)
    )
    .sort(keys + [days_col])
    .group_by(keys)
    .agg([
        pl.col("prior_organism")
          .first()
          .alias("nearest_prior_infecting_organism"),

        pl.col(days_col)
          .first()
          .alias("nearest_prior_infecting_organism_days"),

        pl.col("source")
          .first()
          .alias("nearest_prior_infecting_organism_source"),
    ])
)


infecting_organism_features = infecting_organism_features.join(
    nearest_prior_infecting_organism,
    on=keys,
    how="left"
)

master_v12 = master_v11.join(
    infecting_organism_features,
    on=keys,
    how="left"
)
master_v12.write_parquet(
    "./merge_all/master_v12_infecting_organism.parquet"
)

master_v12.head()
missing_df = (
    master_v12
    .select(pl.all().null_count())
    .transpose(include_header=True)
    .rename({"column": "feature", "column_0": "n_null"})
    .with_columns([
        pl.lit(master_v12.height).alias("n_total"),
        (pl.col("n_null") / master_v12.height).alias("null_ratio")
    ])
    .sort("null_ratio", descending=True)
)

print(missing_df)

master_v12.columns

############################################
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
    pl.col("antibiotic_std").is_null() | pl.col("susceptibility_std").is_null() | pl.col("organism_std").is_null()
).height

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

valid_labels = [
    c for c in omni_armd_final.columns
    if "_" in c and c not in clinical_cols and c not in keys
]

raw_final_cols = keys + clinical_cols + valid_labels
final_cols_unique = list(dict.fromkeys(raw_final_cols))
existing_cols = [c for c in final_cols_unique if c in omni_armd_final.columns]
omni_armd_v12 = omni_armd_final.select(existing_cols)

final_label_count = len([c for c in valid_labels if c in omni_armd_v12.columns])

print(label_missing.sort("missing_rate_pct").head(10))

omni_armd_v12.write_parquet("omni_armd_v12_final_compact.parquet", compression="zstd")


omni_armd_v12.columns
omni_armd_v12['Klebsiella aerogenes_cefotetan'].unique()
target_label_cols = [c for c in valid_labels if c in omni_armd_v12.columns]

omni_armd_v12 = omni_armd_v12.with_columns([
    pl.col(col).replace("I", "R") for col in target_label_cols
])

omni_armd_v12.write_parquet("omni_armd_v1_2_final_compact_SR.parquet", compression="zstd")




