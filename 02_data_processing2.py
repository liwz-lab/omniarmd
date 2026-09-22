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
print(f"列交集: {common_cols}")

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
ARMD.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/14_combined_microbiology_cultures_prior_infecting_organism2_std.csv')
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
# 检查 demo 表是否有重复键，防止合并后行数爆炸
if demo.select(keys).is_duplicated().any():
    print("警告：Demographics 表中存在重复的样本键，请检查数据！")

demo = demo.unique(subset=keys, keep="first")
step1_df = cohort.join(demo, on=keys, how="left")

# 实时检查
print(f"合并 Demo 后行数: {step1_df.height} (预期应为 {original_count})")

# --- 第三步：合并 ADI Scores ---
adi = pl.read_csv("02_combined_microbiology_cultures_adi_scores3.csv", schema_overrides={"order_proc_id_coded": pl.Utf8})
# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
if adi.select(keys).is_duplicated().any():
    print("警告：adi 表中存在重复的样本键，请检查数据！")
####
duplicates = adi.filter(adi.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))

# 1. 先排序：将含有有效 adi_score 的行排在前面
# 注意：Polars 默认 null 会排在后面，所以我们直接升序/降序排列即可确保有效值在前
adi_cleaned = (
    adi
    .sort(
        # 核心在于对 adi_score 进行排序，并强制 null 放在最后
        by=["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded", "order_time_jittered", "adi_score"],
        descending=[False, False, False, False, True],
        nulls_last=True  # 👈 关键：强制把 null 赶到后面
    )
    .unique(subset=keys, keep="first")
)

# 再次验证那几个 ID
check_ids_int = [int(i) for i in ["444133", "551755", "79735"]]
print("修正后的检查结果：")
print(adi_cleaned.filter(pl.col("order_proc_id_coded").is_in(check_ids_int)))

# 确保之前合好的主表叫 step1_df (包含 Cohort + Demographics)
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded", "order_time_jittered"]
# 1. 在合并前重命名 adi 表里的 source，并只选取我们需要的列
adi_to_join = adi_cleaned.select([
    *keys,
    pl.col("adi_score"),
    pl.col("adi_state_rank"),
    pl.col("source").alias("source_adi") # 给它一个明确的名字
])

# 2. 执行合并
final_base_df = step1_df.join(adi_to_join, on=keys, how="left")

# 3. 验证
print(f"主表行数: {cohort.height}")
print(f"合并后行数: {final_base_df.height}")
print(f"当前列名: {final_base_df.columns}")

# --- 第四步：保存中间结果 (Parquet格式便于下一步加载) ---
final_base_df.write_parquet("./merge_all/culture_cohort_demographics_adi.parquet")
print("阶段一合并完成，文件已保存为 master_step_1_base.parquet")

#####################阶段二：病房信息整合 (Ward Info)
import polars as pl
# 读取 Parquet 文件
final_base_df = pl.read_parquet('./merge_all/culture_cohort_demographics_adi.parquet')
# 快速验证
print(f"读取成功，行数: {final_base_df.height}, 列数: {len(final_base_df.columns)}")
print(final_base_df.head())

#####################阶段二：病房信息整合 (Ward Info)
# 1. 加载 Ward 表
ward = pl.read_csv("12_combined_microbiology_cultures_ward_info3.csv",schema_overrides={"order_proc_id_coded": pl.Utf8})
# 检查 demo 表是否有重复键，防止合并后行数爆炸
# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
if ward.select(keys).is_duplicated().any():
    print("警告：ward 表中存在重复的样本键，请检查数据！")
####
duplicates = ward.filter(adi.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))


# 2. 预处理：排序、去重、重命名
ward_to_join = (
    ward
    .sort(keys, nulls_last=True)
    .unique(subset=keys, keep="first")
    .select([
        *keys,
        # 自动选取所有病房相关的特征列
        pl.col("^hosp_ward.*$"),
        # 同样避免 source 冲突
        pl.col("source").alias("source_ward")
    ])
)

# 3. 合并到你的大表中
master_v2 = final_base_df.join(ward_to_join, on=keys, how="left")

print(f"合并 Ward 后行数: {master_v2.height} (预期应保持不变)")
master_v2.write_parquet("./merge_all/culture_cohort_demographics_adi_ward.parquet")

######################阶段三：实验室检查（Labs）的多对一合并################################
# 加载 Labs 表
labs = pl.read_csv("07_combined_microbiology_cultures_labs.csv")
# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]
if labs.select(keys).is_duplicated().any():
    print("警告：labs 表中存在重复的样本键，请检查数据！")
####
duplicates = labs.filter(labs.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))
labs_cleaned = labs.unique(subset=keys, keep="first")

# 执行左连接：保留 1200 万行的队列，只在有匹配的地方填入实验数据
# master_v3 = master_v2.join(
#     labs_cleaned.rename({"source": "source_labs"}),
#     on=keys,
#     how="left"
# )
master_v3 = master_v2.join(
    labs_cleaned.rename({"source": "source_labs"}),
    on=keys,
    how="left",
    suffix="_labs"
)
print(f"最终主表行数: {master_v3.height}")
print(f"当前总列数: {len(master_v3.columns)}")
master_v3.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs.parquet")



#######################Prior Medications (既往用药史)###################################
# 加载既往用药表
prior_med = pl.read_csv("10_combined_microbiology_cultures_prior_med3.csv",schema_overrides={"order_proc_id_coded": pl.Utf8})
# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
if prior_med.select(keys).is_duplicated().any():
    print("警告：prior_med 表中存在重复的样本键，请检查数据！")
####
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


# prior_bugs_wide = (
#     prior_med
#     .filter(pl.col("prior_org").is_not_null())
#     .group_by([*keys, "prior_org"])
#     .agg(pl.len().alias("count"))
#     .pivot(
#         index=keys,
#         on="prior_org",
#         values="count"
#     )
#     .fill_null(0)
# )

prior_bugs_wide = prior_bugs_wide.with_columns([
    pl.col(c).alias(f"prior_med_{c}")
    for c in prior_bugs_wide.columns if c not in keys
]).select([*keys, pl.col("^prior_med_.*$")])

print(f"全量聚合后的prior_med列数: {len(prior_bugs_wide.columns) - len(keys)}")

# 最终合并
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

print(f"Master v4 最终维度: {master_v4.shape}")
master_v4.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed.parquet")

# 计算每种历史菌种的非零覆盖率
bug_summary = master_v4.select(pl.col("^prior_med_.*$")).sum() / master_v4.height
# 看看哪些菌种太罕见
rare_bugs = [c for c in bug_summary.columns if bug_summary[c][0] < 0.0001] # 覆盖率低于万分之一
print(f"prior_med数量: {len(rare_bugs)}")
#4


################################下一阶段实操：整合 Vitals (生命体征)
# 1. 加载 Vitals
vitals = pl.read_csv("13_combined_microbiology_cultures_vitals3.csv",schema_overrides={"order_proc_id_coded": pl.Utf8})
# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]
if vitals.select(keys).is_duplicated().any():
    print("警告：prior_med 表中存在重复的样本键，请检查数据！")
####
duplicates = vitals.filter(vitals.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))

import polars as pl

# 1. 定义键和特征列
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]
# 排除掉 keys 和 source，剩下的全是生理指标特征
feature_cols = [c for c in vitals.columns if c not in keys + ["source"]]

# 2. 计算每一行的“信息完整度分数”
vitals_with_score = vitals.with_columns(
    pl.sum_horizontal([
        pl.col(c).is_not_null().cast(pl.Int32)
        for c in feature_cols
    ]).alias("info_score")
)

# 3. 执行去重
# 排序逻辑：
# 第一优先级：info_score (降序，保留指标最全的)
# 第二优先级：last_temp (降序，假设数值大通常代表有记录，nulls_last)
vitals_deduplicated = (
    vitals_with_score
    .sort(
        by=["info_score", "last_temp"],
        descending=[True, True],
        nulls_last=True
    )
    .unique(subset=keys, keep="first")
    .drop("info_score") # 删掉临时分数列
)

print(f"去重前行数: {vitals.height}")
print(f"去重后行数: {vitals_deduplicated.height}")

# 只提取最关键的“最后一次测量值”进入主表
vitals_final_features = vitals_deduplicated.select([
    *keys,
    pl.col("^last_.*$"),
    pl.col("^median_.*$") # 中位数代表了该时段的平均生理水平
])

master_v5 = master_v4.join(vitals_final_features, on=keys, how="left")

print(f"Master v5 形状: {master_v5.shape}")
master_v5.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals.parquet")

#########antibiotic_class_exposure
abx_exp = pl.read_csv("03_combined_microbiology_cultures_antibiotic_class_exposure3.csv",schema_overrides={"order_proc_id_coded": pl.Utf8})
# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
if abx_exp.select(keys).is_duplicated().any():
    print("警告：abx_exp 表中存在重复的样本键，请检查数据！")
####
duplicates = abx_exp.filter(abx_exp.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))

import polars as pl

# 1. 核心去重与聚合逻辑
# 目标：每个 keys 只保留一行，列变成各种 drug_code 的最小天数
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

# 2. 特征修饰
# 现在的列名是原始的 drug_code（如 AMC, CRO），我们给它加个前缀方便识别
abx_final = abx_features.rename({
    col: f"abx_exp_{col}"
    for col in abx_features.columns if col not in keys
})

print(f"去重聚合后行数: {abx_final.height}")
print(f"生成的抗生素特征列数: {len(abx_final.columns) - len(keys)}")

# 只保留采样前的暴露史（time_to_culturetime >= 0）
abx_exp_cleaned = abx_exp.filter(pl.col("time_to_culturetime") >= 0)
# 基于清理后的数据 (time_to_culturetime >= 0) 构建特征
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

# 重新命名
abx_final_cleaned = abx_features_cleaned.rename({
    col: f"abx_exp_{col}"
    for col in abx_features_cleaned.columns if col not in keys
})

print(f"最终抗生素特征表行数: {abx_final_cleaned.height}")


# 合并入主表
master_v6 = master_v5.join(abx_final_cleaned, on=keys, how="left")

# 1. 创建“是否暴露”的布尔列并填 0
# 2. 对原有的天数列填充 3650 (代表长期未接触)
abx_cols = [c for c in master_v6.columns if c.startswith("abx_exp_")]

master_v6 = master_v6.with_columns([
    pl.col(c).fill_null(3650) for c in abx_cols
]).with_columns([
    (pl.col(c) < 3650).cast(pl.Int32).alias(f"any_{c}") for c in abx_cols
])

print(f"Master v6 构建完成！总列数: {len(master_v6.columns)}")
master_v6.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class.parquet")

###############04_combined_microbiology_cultures_antibiotic_subtype_exposure2
import polars as pl
import gc

# 1. 加载并过滤
sub_exp = pl.read_csv("04_combined_microbiology_cultures_antibiotic_subtype_exposure3.csv",schema_overrides={"order_proc_id_coded": pl.Utf8})
# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
if sub_exp.select(keys).is_duplicated().any():
    print("警告：sub_exp 表中存在重复的样本键，请检查数据！")
####
duplicates = sub_exp.filter(sub_exp.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))

# 1. 清理数据：确保时间列为 Float 并过滤采样后的记录 (Future leakage)
# 注意：这里使用你预览中显示的列名 'medication_time_to_culturetime'
sub_exp_cleaned = (
    sub_exp
    .filter(
        (pl.col("time_to_culturetime").is_not_null()) &
        (pl.col("time_to_culturetime") >= 0) &
        (pl.col("antibiotic_subtype").is_not_null()) &
        (pl.col("antibiotic_subtype").is_in(["null", "Null", "NULL", ""]).not_())
    )
)

print(f"有效暴露记录行数: {sub_exp_cleaned.height}")

if sub_exp_cleaned.height > 0:
    # 2. 聚合逻辑：每个样本键取每种药物的“最近距离”
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

    # 3. 增加前缀以区分特征
    sub_final = sub_features.rename({
        col: f"sub_exp_{col}"
        for col in sub_features.columns if col not in keys
    })
if sub_final.height > 0:
    print(f"子类特征构建成功！行数: {sub_final.height}, 新增特征数: {len(sub_final.columns) - len(keys)}")
else:
    print("警告：筛选后仍无有效数据。请检查 drug_code 列是否存在有效的非空字符串。")


# 1. 执行左连接
master_v7 = master_v6.join(sub_final, on=keys, how="left")

# 2. 批量填充缺失值
# 子类特征同样使用 3650 (10年) 作为“从未接触”的默认值
sub_cols = [c for c in master_v7.columns if c.startswith("sub_exp_")]

master_v7 = master_v7.with_columns([
    pl.col(c).fill_null(3650) for c in sub_cols
])

# 3. 释放内存
del sub_final, sub_features, sub_exp, sub_exp_cleaned
gc.collect()

print(f"Master v7 构建完成！")
print(f"当前总列数: {len(master_v7.columns)}")
print(f"样本行数: {master_v7.height}")

master_v7.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub.parquet")

####################合并症表
import polars as pl
import gc
# 1. 载入刚刚保存的大表
master_v7= pl.read_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub.parquet")

#cmbd = pl.read_csv("05_combined_microbiology_cultures_comorbidity2.csv")
# 使用 null_values 参数将字符串 "Null" 映射为真正的 Null
cmbd = pl.read_csv(
    "05_combined_microbiology_cultures_comorbidity3.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    infer_schema_length=10000  # 增加推断长度以提高鲁棒性
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
# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
if cmbd.select(keys).is_duplicated().any():
    print("警告：cmbd 表中存在重复的样本键，请检查数据！")
####
duplicates = cmbd.filter(cmbd.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))
cmbd.columns


import polars as pl
import gc

# 1. 筛选并清理有效记录
# 我们只需要知道在采样时，这个 comorbidity_component 存不存在
cmbd_cleaned = (
    cmbd
    .filter(pl.col("comorbidity_mid").is_not_null())
    .select([*keys, "comorbidity_mid"])
)

# 2. Pivot 转换：将合并症名称变为特征列
# 如果某个 key 对应某个合并症，值设为 1，缺失则后面填充 0
cmbd_features = (
    cmbd_cleaned
    .with_columns(pl.lit(1).alias("val"))
    .group_by([*keys, "comorbidity_mid"])
    .agg(pl.col("val").max())  # 确保同一个样本的同一个病只计一次
    .pivot(
        index=keys,
        on="comorbidity_mid",
        values="val"
    )
)

# 3. 规范化列名：小写、下划线、加 cmbd_ 前缀
# 这样能清晰区分哪些特征来自合并症表
cmbd_final = cmbd_features.rename({
    col: f"cmbd_{col.lower().replace(' ', '_').replace(',', '').replace('-', '_')}"
    for col in cmbd_features.columns if col not in keys
})

print(f"合并症特征提取完成！样本数: {cmbd_final.height}, 合并症种类: {len(cmbd_final.columns) - len(keys)}")

# 4. 合并入 Master v7 -> 升级为 Master v8
master_v8 = master_v7.join(cmbd_final, on=keys, how="left")

# 5. 填充缺失值并优化类型
# 合并症缺失通常代表“无该病记录”，统一填充为 0
cmbd_cols = [c for c in master_v8.columns if c.startswith("cmbd_")]
master_v8 = master_v8.with_columns([
    pl.col(c).fill_null(0).cast(pl.Int8)
    for c in cmbd_cols
])

# 6. 清理内存
del cmbd, cmbd_cleaned, cmbd_features, cmbd_final
gc.collect()

print(f"Master v8 构建完成！当前总列数: {len(master_v8.columns)}")

master_v8.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub_comorbidity.parquet")



###########################microbiology_cultures_nursing_home_visit
import polars as pl
import gc
# 1. 载入刚刚保存的大表
master_v8 = pl.read_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub_comorbidityvv.parquet")

# 1. 修正读取：统一处理各类 Null 字符串
# 2. 读取护理院数据，显式指定类型以解决 3.0 解析问题
import polars as pl

nh_visits = pl.read_csv(
    "09_combined_microbiology_cultures_nursing_home_visits3.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    infer_schema_length=10000,
    dtypes={
        "order_proc_id_coded": pl.Utf8,  # 👈 关键修复
        "nursing_home_visit_culture": pl.Float64,
        "nursing_home_visit_time_to_culture": pl.Float64
    }
)

# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
if nh_visits.select(keys).is_duplicated().any():
    print("警告：nh_visits 表中存在重复的样本键，请检查数据！")
####
duplicates = nh_visits.filter(nh_visits.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))
nh_visits.columns
master_v9.columns
master_v9["anon_id"].unique()
master_v8[["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered","source"]].unique()
# 1. 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded", "order_time_jittered"]

# 2. 聚合 NH 表：将“一对多”变成“一对一”
# 假设时间列名为 'nursing_home_visit_culture' (对应你预览中的 1.0, 0.0)
time_col = "nursing_home_visit_culture"

nh_features = (
    nh_visits
    .filter(
        (pl.col(time_col).is_not_null()) &
        (pl.col(time_col) >= 0)  # 过滤掉未来记录
    )
    .group_by(keys)
    .agg([
        pl.lit(1).alias("nh_visit_binary"), # 只要出现在表里就标记为 1
        pl.col(time_col).min().alias("nh_recent_days") # 取最近的一次访问（天数最小）
    ])
)

print(f"NH 特征聚合完成，唯一样本数: {nh_features.height}")
# 2. 清理与过滤（防止数据泄漏，只看采样前的记录）
# 假设列名为 nh_visit_time_to_culturetime (Float64)
# 如果列名不同，请根据之前的经验调整
# 4. 合并入 Master v8 -> 升级为 Master v9
master_v9 = master_v8.join(nh_features, on=keys, how="left")

# 5. 填充缺失值
# 对于没去过护理院的人：binary 填 0，天数填 3650 (极大值)
master_v9 = master_v9.with_columns([
    pl.col("nh_visit_binary").fill_null(0).cast(pl.Int8),
    pl.col("nh_recent_days").fill_null(3650)
])

# 6. 清理内存
del nh_visits, nh_cleaned, nh_features
gc.collect()

master_v9.write_parquet("./merge_all/ARMD_Master_v9_Final_Cleaned.parquet")
print(f"Master v9 构建完成！护理院特征已集成。")
print(f"最终行数: {master_v9.height}, 总特征数: {len(master_v9.columns)}")

#####################################08_combined_microbiology_cultures_microbial_resistance3.csv
import polars as pl

microbial_resistance = pl.read_csv(
    "08_combined_microbiology_cultures_microbial_resistance3.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    infer_schema_length=10000,
    dtypes={
        "order_proc_id_coded": pl.Utf8,  # 👈 关键修复
    }
)
# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]
if microbial_resistance.select(keys).is_duplicated().any():
    print("警告：microbial_resistance 表中存在重复的样本键，请检查数据！")
####
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
# =========================
# 9. 保存结果
# =========================
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

# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
if prior_procedures.select(keys).is_duplicated().any():
    print("警告：prior_procedures 表中存在重复的样本键，请检查数据！")

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
# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]
if infecting_organism.select(keys).is_duplicated().any():
    print("警告：infecting_organism 表中存在重复的样本键，请检查数据！")

###########
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
# 核心去重
master_v9_clean = master_v9.unique(subset=keys)
print(f"去重后真实样本数: {master_v9_clean.height}")

# 计算每列缺失率
null_stats = master_v9_clean.select([
    (pl.col(c).is_null().sum() / pl.count() * 100).alias(c)
    for c in master_v9_clean.columns
]).melt(variable_name="feature", value_name="null_percentage")

# 查看缺失最严重的 30 个特征
print("--- 缺失率最高的特征 (Top 30) ---")
print(null_stats.sort("null_percentage", descending=True).head(30))

# 统计完全没有缺失的特征数量
clean_features_count = null_stats.filter(pl.col("null_percentage") == 0).height
print(f"\n完全无缺失的特征数: {clean_features_count} / {len(master_v9_clean.columns)}")


############################
import polars as pl
# 读取 Parquet 文件
master_v9 = pl.read_parquet('./merge_all/ARMD_Master_v9_Final_Cleaned.parquet')
master_v9.columns
master_v9[['organism_std', 'antibiotic_std', 'susceptibility_std']]

master_v9[["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded", "order_time_jittered","organism_std", "age", "gender", "median_wbc", "antibiotic_std", "susceptibility_std"]].unique()

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


# 3. 检查药敏结果列的空值情况 (这是转宽表前的最后一道坎)
# 如果某一行没有 antibiotic_std 或 susceptibility_std，这类行在模型训练中通常是无效的
invalid_ast = master_v10.filter(
    pl.col("antibiotic_std").is_null() | pl.col("susceptibility_std").is_null() | pl.col("organism_std").is_null()
).height
print(f"无效药敏记录数: {invalid_ast}")


# 去重后行数: 11931861
# 无效药敏记录数: 4179360
# 剔除无效 AST 记录，只保留有 菌-药-结果 的行
master_v11 = master_v10.filter(
    pl.col("antibiotic_std").is_not_null() &
    pl.col("susceptibility_std").is_not_null()
)

print(f"最终进入 Pivot 的有效行数: {master_v11.height}")
master_v11.write_parquet("master_v11_before_Pivot.parquet", compression="zstd")

#最终进入 Pivot 的有效行数: 7752501
#建议采用“先宽后合”的策略：
# 1. 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded", "order_time_jittered"]
# 构造复合列名
# 我们需要将 organism_std 和 antibiotic_std 拼接起来。
# 构造一个临时列，用于 pivot 的 'on' 参数
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

print(f"全局宽表维度: {ast_pivot_global.shape}")

# 提取唯一的临床背景特征
# 修正：将 master_v11(...) 改为 master_v11[...]
clinical_features = master_v11[
    keys + [c for c in master_v11.columns if c.startswith(("age", "gender", "cmbd_", "med_", "lab_"))]
].unique(subset=keys)

print(f"唯一临床特征样本数: {clinical_features.height}")

# 必须排除的字段（这些字段在每个 order 下是变动的，不排除会导致 unique() 失败或产生冗余行）
exclude_for_unique = [
    "antibiotic_std", "susceptibility_std", "organism_std",
    "bug_drug_pair", "antibiotic", "susceptibility", "organism"
]

# 选取除上述字段外的所有 800+ 列
clinical_features_full = master_v11.select([
    col for col in master_v11.columns if col not in exclude_for_unique
]).unique(subset=keys)

print(f"全量特征表维度: {clinical_features_full.shape}")
# 最终大合并
# 将 Wide AST 结果与全量临床特征进行左连接
omni_armd_final = ast_pivot_global.join(clinical_features_full, on=keys, how="left")

print(f"Omni-ARMD 最终矩阵维度: {omni_armd_final.shape}")
omni_armd_final.write_parquet("omni_armd_final.parquet", compression="zstd")
# 找出非空值比例太低的列（例如非空样本数少于 10 的）
threshold = 10
non_null_counts = omni_armd_final.select(
    [pl.all().count() - pl.all().null_count()]
)

# 筛选出有意义的列名
meaningful_cols = [
    col for col in omni_armd_final.columns
    if col in keys or (omni_armd_final.select(pl.col(col).count() - pl.col(col).null_count()).item() >= threshold)
]

omni_armd_compact = omni_armd_final.select(meaningful_cols)
print(f"压缩后维度: {omni_armd_compact.shape}")

# 1. 计算每列的缺失数
missing_stats = omni_armd_final.select([
    (pl.col(c).null_count() / pl.count() * 100).alias(c)
    for c in omni_armd_final.columns
])

# 2. 转置并排序，方便观察
missing_rate_df = missing_stats.transpose(
    include_header=True,
    header_name="column_name",
    column_names=["missing_rate_pct"]
).sort("missing_rate_pct", descending=True)

# 3. 查看缺失率最高的前 50 列和最低的前 50 列
print("--- 缺失率最高的 20 列 (极其稀疏的菌药组合) ---")
print(missing_rate_df.head(20))

print("\n--- 缺失率最低的 20 列 (最扎实的临床特征) ---")
print(missing_rate_df.tail(20))

clinical_cols = clinical_features_full.columns
clinical_missing = missing_rate_df.filter(pl.col("column_name").is_in(clinical_cols))
print(f"临床特征平均缺失率: {clinical_missing['missing_rate_pct'].mean():.2f}%")
# 找出缺失率超过 50% 的临床指标（可能是一些不常做的化验单）
high_missing_clinical = clinical_missing.filter(pl.col("missing_rate_pct") > 50)
print(f"高缺失(>50%)临床列数: {high_missing_clinical.height}")
# 临床特征平均缺失率: 6.70%
# 高缺失(>50%)临床列数: 83
# 过滤出所有 bug_drug 组合列
label_missing = missing_rate_df.filter(
    ~pl.col("column_name").is_in(clinical_cols) & ~pl.col("column_name").is_in(keys)
)
print(f"药敏标签平均缺失率: {label_missing['missing_rate_pct'].mean():.2f}%")
valid_labels = [
    c for c in omni_armd_final.columns
    if "_" in c and c not in clinical_cols and c not in keys
]
# 药敏标签平均缺失率: 99.77%
# 1. 剔除 100% 缺失的列
# 1. 构造初始列表
raw_final_cols = keys + clinical_cols + valid_labels
# 2. 列表去重 (使用 dict.fromkeys 保持原始顺序)
final_cols_unique = list(dict.fromkeys(raw_final_cols))
# 3. 执行筛选 (确保列确实存在于 omni_armd_final 中)
existing_cols = [c for c in final_cols_unique if c in omni_armd_final.columns]
omni_armd_v12 = omni_armd_final.select(existing_cols)

print(f"脱水后维度: {omni_armd_v12.shape}")

# 看看最终留下了多少个有效的菌药组合
final_label_count = len([c for c in valid_labels if c in omni_armd_v12.columns])
print(f"最终进入模型的有效‘菌-药’标签数: {final_label_count}")

# 看看最‘扎实’（样本量最大）的 10 个标签
print("样本量最丰富的标签 Top 10:")
print(label_missing.sort("missing_rate_pct").head(10))
# 使用 zstd 压缩，既省空间又保证读取速度
omni_armd_v12.write_parquet("omni_armd_v1_2_final_compact.parquet", compression="zstd")
print("✅ Omni-ARMD v1.2 数据集已固化，随时可以开始建模。")

omni_armd_v12.columns
omni_armd_v12['Klebsiella aerogenes_cefotetan'].unique()
# 1. 确定需要转换的药敏列名单 (即之前筛选出的 1960 个有效标签)
target_label_cols = [c for c in valid_labels if c in omni_armd_v12.columns]

# 2. 使用 Polars 的 replace 批量转换
# 我们保留 null 和 "S"，仅将 "I" 映射为 "R"
omni_armd_v12 = omni_armd_v12.with_columns([
    pl.col(col).replace("I", "R") for col in target_label_cols
])

# 3. 验证转换结果（以你提到的列为例）
print("转换后 'Klebsiella aerogenes_cefotetan' 的唯一值:")
print(omni_armd_v12['Klebsiella aerogenes_cefotetan'].unique())
omni_armd_v12.write_parquet("omni_armd_v1_2_final_compact_SR.parquet", compression="zstd")


# 获取所有列名列表
all_columns = omni_armd_v12.columns
# 查找特定列的索引（注意：索引从 0 开始）
try:
    target_col = 'Klebsiella_minocycline'
    col_index = all_columns.index(target_col)
    print(f"列名 '{target_col}' 位于第 {col_index} 位（从 0 开始计数）。")
    print(f"也就是 Excel 视角下的第 {col_index + 1} 列。")
except ValueError:
    print(f"在当前数据框中未找到列名 '{target_col}'，请检查拼写或大小写。")

# 列名 'Klebsiella_minocycline' 位于第 856 位（从 0 开始计数）。
# 也就是 Excel 视角下的第 857 列。
#它前面的为x


import polars as pl
# 读取 Parquet 文件
final_base_df = pl.read_parquet('./omni_armd_v1_2_final_compact_SR.parquet')

EBI = pd.read_csv('/public8/lilab/student/htang/SMART/EMBL/ARMD_EBI_SIR_Gene.csv')


################################################
import os
rt1=pd.read_excel('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/测序菌株.xlsx')
rt2=pd.read_excel('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/2024-FQ-菌株编号（医院版）.xlsx')
import pandas as pd
# 1. 按 '菌株编号' 内连接
merged_df = pd.merge(rt1, rt2, on='菌株编号', how='inner')
# 2. 查看前几行
print(merged_df.head())
rt3 = pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/std/01_culture_cohort_std.csv')
merged_df = merged_df.rename(columns={'住院号': 'anon_id'})
# 2. 确保类型一致（很重要！）
merged_df['anon_id'] = merged_df['anon_id'].astype(str)
rt3['anon_id'] = rt3['anon_id'].astype(str)

# 3. 合并（建议先用 left，保留菌株数据）
final_df = pd.merge(
    merged_df,
    rt3,
    on='anon_id',
    how='inner'
)

print(final_df.head())
final_df.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/测序菌株_SIR.csv')
final_df = final_df.rename(columns={'菌株编号': 'BioSample_ID'})
final_df = final_df.rename(columns={'culture_description': 'isolation_source'})

final_df[[]]

rt4=pd.read_csv('/public8/lilab/student/htang/SMART/card/batch_outputs/txt/merge/combined_amr_results_strict.csv')
final_df['BioSample_ID'].unique()
rt4['source'].unique()
import re
import pandas as pd


def map_source_to_biosample(source_val):
    if pd.isna(source_val):
        return None

    source_str = str(source_val).strip()

    # 模式 1：处理带有下划线的复合前缀情况 (例如 EBEC2024_FQ_13, CRKP2024_FQ_2)
    if "_" in source_str:
        # 使用正则提取前缀里的字母、年份以及最后的 FQ 编号
        match = re.match(r"([A-Za-z]+)(\d{4})_FQ_(\d+)", source_str)
        if match:
            prefix, year, num = match.groups()
            return f"{prefix}-{year}-FQ-{num}"

    # 模式 2：处理常规临床短简写情况 (例如 EC-4, KP-122, SA-6)
    elif "-" in source_str:
        # 拆分菌名缩写与后台测序/菌株编号
        parts = source_str.split("-")
        if len(parts) == 2:
            prefix, num = parts[0], parts[1]
            # 补齐默认的 2024 年份与 FQ 实验设计批次标签
            return f"{prefix}-2024-FQ-{num}"

    # 如果存在无法解析的特殊噪声，原样返回或打印质控
    return source_str


# 一键应用映射，补充生成 'BioSample_ID' 核心关联列
rt4["BioSample_ID"] = rt4["source"].apply(map_source_to_biosample)

# 验证质控：检查映射后的结果是否在 final_df 的目标白名单中
final_biosamples = set(final_df["BioSample_ID"].unique())
rt4["is_valid_mapping"] = rt4["BioSample_ID"].isin(final_biosamples)

print("🎉 样本源 BioSample_ID 自动化高精度补充映射构建完毕！")
print(
    f"成功完美对齐的唯一样本数: {rt4[rt4['is_valid_mapping']]['BioSample_ID'].nunique()} 个"
)

# 查看一下清洗对齐后的前 10 行效果
print(rt4[["source", "BioSample_ID"]].drop_duplicates().head(10))

rt4.to_csv('/public8/lilab/student/htang/SMART/card/batch_outputs/txt/merge/combined_amr_results_strict_sampleID.csv')

rt4.head()
final_df.head()

# 1. 提取临床核心元数据并去除因药敏测试带来的重复行
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


# 2. 严格基于这四个字段的联合唯一性进行去重
df_ast_unique = final_df[ast_meta_cols].drop_duplicates(
    subset=["BioSample_ID", "organism_std", "antibiotic_std", "susceptibility_std"]
)

# 3. 此时再与 rt4 进行关联
# 场景 A：如果只做样本级别的临床背景关联（保留 rt4 所有基因行）
rt4_merged_clinical = pd.merge(rt4, df_ast_unique, on="BioSample_ID", how="left")
rt4_merged_clinical.to_csv('SIR_gene.csv')
