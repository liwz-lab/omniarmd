# ---****----utf-8---****----
# @File  : 10_ARMD_H2O_ready.py
# @Author: Tang Hai
# @email : tangh25@mail2.sysu.edu.cn
# @Date  :  2026/06/10
#####################################
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/h2o_automl_inputs')

############################
import pandas as pd
# 设置显示的最大列数，None 表示显示所有列
pd.set_option('display.max_columns', None)
# 设置每行显示的宽度，防止自动换行
pd.set_option('display.width', 1000)
import polars as pl
# 读取 Parquet 文件

master_v9 = pl.read_parquet('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/omni_bridge/0730/master_v13_bridge_deidentification_mapping0730.parquet')
master_v9.columns
#########检查结果
master_v9=df14
master_v9[['organism_std', 'antimicrobial_std', 'susceptibility_std']]

master_v9[["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded", "order_time_jittered","organism_std", "age", "gender", "median_wbc", "antimicrobial_std", "susceptibility_std"]].unique()

# 计算完全重复的行数（不包括第一次出现的行）
duplicate_count = master_v9.height - master_v9.unique().height
print(f"完全重复的冗余行数: {duplicate_count}")
# 计算重复行占总数据的比例
print(f"重复率: {duplicate_count / master_v9.height:.2%}")
# 完全重复的冗余行数: 26641
# 重复率: 0.22%

# 1. 彻底去重
master_v10 = master_v9.unique()
# 2. 验证去重后的行数是否等于 11,931,861 (11,958,502 - 26,641)
print(f"去重后行数: {master_v10.height}")

import polars as pl

master_v10 = master_v10.filter(
    pl.col("organism_std").is_not_null() &

    ~pl.col("organism_std")
    .str.strip_chars()
    .str.to_lowercase()
    .str.replace_all(r"\s+", "")
    .is_in(["na", "nan", "null", "none", "",
    "n/a", "na ", " null", "nan "])
)

# master_v10 = master_v10.filter(
#     pl.col("organism_std").is_not_null() &
#     pl.col("antimicrobial_std").is_not_null() &
#     pl.col("susceptibility_std").is_not_null()
# )
# master_v10.columns
# master_v10["antimicrobial_std"].unique().to_list()
master_v10 = master_v10.filter(
    ~pl.col("antimicrobial_std")
    .str.to_lowercase()
    .is_in(["ecim", "mcim"])
)
# 3. 检查药敏结果列的空值情况 (这是转宽表前的最后一道坎)
# 如果某一行没有 antimicrobial_std 或 susceptibility_std，这类行在模型训练中通常是无效的
invalid_ast = master_v10.filter(
    pl.col("antimicrobial_std").is_null() | pl.col("susceptibility_std").is_null() | pl.col("organism_std").is_null()
).height
print(f"无效药敏记录数: {invalid_ast}")


# 去重后行数: 11931861
# 无效药敏记录数: 4179360
# 剔除无效 AST 记录，只保留有 菌-药-结果 的行
master_v11 = master_v10.filter(
    pl.col("antimicrobial_std").is_not_null() &
    pl.col("susceptibility_std").is_not_null()
)

print(f"最终进入 Pivot 的有效行数: {master_v11.height}")


df=master_v10
# 将数据列中的 'I' 完美替换为 'R'
# 1. 完美将 'I' 替换为 'R' (使用 Polars 的 with_columns 表达式)
df = df.with_columns(
    pl.col("susceptibility_std").replace("I", "R", default=pl.col("susceptibility_std"))
)

df = df.with_columns([
    (pl.col("organism_std") + "_" + pl.col("antimicrobial_std")).alias("org_abx"),
    (pl.col("susceptibility_std") == "R").cast(pl.Int8).alias("label")
])

###################clinical features
clinical_cols = [ 'anon_id',
 'pat_enc_csn_id_coded',
 'order_proc_id_coded',
 'order_time_jittered',
 'order_time_jittered_std',
    "age",'culture_description', 'source',"adi_score", "adi_state_rank",'hosp_ward_IP','hosp_ward_OP','hosp_ward_ER','hosp_ward_ICU','order_time_year',
    'order_time_month','Period_Day',
    "median_wbc",'median_neutrophils','median_lymphocytes', "median_cr", "median_hgb", "median_plt",'median_hco3', 'median_bun',
    "median_lactate", "median_procalcitonin",
    "median_temp", "median_sysbp", "median_diasbp",
    "median_heartrate", "median_resprate", 'has_prior_procedure', 'nh_visit_binary','nh_recent_days', 'clinical_R_rate',
]

prior_inf_features = [
# burden
"has_prior_infecting_organism",
"prior_infecting_organism_n_records",
"prior_infecting_organism_n_unique",

# time signal
"prior_infecting_organism_median_days",
"prior_infecting_organism_min_days",
'nearest_prior_infecting_organism',
"nearest_prior_infecting_organism_days",
'nearest_prior_infecting_organism_source',
]

procedure_features = [
# exposure burden
"has_prior_procedure",
"prior_procedure_n_records",
"prior_procedure_n_unique",

# timing (safe version)
"prior_procedure_median_time_to_culture",
"prior_procedure_min_time_to_culture"
]
###########antibiotic exposure features
abx_cols = [c for c in df.columns if c.startswith("prior_med_")]
#abx_class_cols = [c for c in df.columns if c.startswith("abx_exp_")]
abx_subclass_cols = [c for c in df.columns if c.startswith("sub_exp_")]

##############EBI features（核心）
#ebi_cols = [c for c in df.columns if c.startswith("ebi_")]
ebi_cols = [

# core burden
"ebi_gene_count",
"ebi_mean_final_score",

# resistance signal
"ebi_mean_Non_S_rate_among_gene_positive",
"ebi_max_gene_prevalence_in_Non_S",

# evidence
"ebi_evidence_n_sum",
"ebi_evidence_n_mean",

# gene structure
"ebi_n_strong_resistance_genes",
"ebi_n_weak_neutral_resistance_genes",
# "ebi_n_weak_resistance_genes",
# "ebi_n_neutral_genes",

# knowledge graph
"ebi_dominant_label_cn",
"ebi_knowledge_matched"
]
#comorbidity压缩（必须）
cmbd_cols = [c for c in df.columns if c.startswith("cmbd_")]

df = df.with_columns(
    pl.sum_horizontal([pl.col(c) for c in cmbd_cols]).alias("comorbidity_score")
)

feature_cols = (
    clinical_cols +
    abx_cols +
    #abx_class_cols +
    abx_subclass_cols + prior_inf_features + prior_inf_features + ["comorbidity_score"] +
    ebi_cols
)

feature_cols = [c for c in feature_cols if c in df.columns]
feature_cols = list(dict.fromkeys(feature_cols))

print("rows:", df.shape[0])
print("cols:", df.shape[1])
print("duplicate cols:", len(df.columns) - len(set(df.columns)))


############################gender
# df['gender'].unique()
# df = df.with_columns(
#     pl.when(pl.col("gender").is_in(["Male", "1"]))
#     .then(1)
#     .when(pl.col("gender").is_in(["Female", "0"]))
#     .then(0)
#     .otherwise(None)
#     .alias("gender_binary")
# )

df2=df[feature_cols+ ['organism_std']+
 ['antimicrobial_std']+['org_abx']+['label']]

df2 = df2.rename({c: c.lower() for c in df2.columns})
df2.write_csv(
    "/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/h2o_automl_inputs/omni_bridge_h2o_deidentification0730.csv",
    batch_size=100000
)
df2.write_csv(
    "/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/h2o_automl_inputs/omni_bridge_h2o_deidentification0919.csv",
    batch_size=100000
)
df=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/h2o_automl_inputs/omni_bridge_h2o_deidentification0730.csv')
