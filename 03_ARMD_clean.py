
#########################01_combined_culture_cohort
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/')
import pandas as pd
# 设置显示的最大列数，None 表示显示所有列
pd.set_option('display.max_columns', None)
# 设置每行显示的宽度，防止自动换行
pd.set_option('display.width', 1000)

#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
df = pd.read_csv('./01_combined_culture_cohort2.csv')
# 查看
print(df)
# 读取映射表
map_df = pd.read_csv('./clean/organism_rename.txt', sep='\t', encoding='gbk')
# 查看
print(map_df.head())

# 2. 构建字典（统一大写匹配）
mapping_dict = dict(zip(
    map_df['organism'].str.strip().str.upper(),
    map_df['organism_new'].str.strip()
))

# 3. 创建新列（不覆盖原始数据）
df['organism_std'] = (
    df['organism']
    .str.strip()
    .str.upper()
    .map(mapping_dict)
    .fillna(df['organism'])   # 未匹配保持原值（原始写法）
)

#查看未匹配项
df.loc[
    df['organism'].str.upper().isin(mapping_dict.keys()) == False,
    'organism'
].value_counts().head(20)

df['organism_std'].unique().tolist()

##########drug
# 读取映射表
map_dr = pd.read_csv('./clean/drug_rename.txt', sep='\t', encoding='gbk')
# 查看
print(map_dr.head())

# 2. 构建字典（统一大写匹配）
mapping_dict = dict(zip(
    map_dr['antibiotic'].str.strip().str.upper(),
    map_dr['antibiotic_new'].str.strip()
))

# 3. 创建新列（不覆盖原始数据）
df['antibiotic_std'] = (
    df['antibiotic']
    .str.strip()
    .str.upper()
    .map(mapping_dict)
    .fillna(df['antibiotic'])   # 未匹配保持原值（原始写法）
)

#查看未匹配项
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
# 筛选所有属于假单胞菌属的记录
# 设置显示的最大列数，None 表示显示所有列
pd.set_option('display.max_columns', None)
# 设置每行显示的宽度，防止自动换行
pd.set_option('display.width', 1000)

df.susceptibility.unique().tolist()
df.susceptibility.unique().value_counts
df['susceptibility'].value_counts

#分类	含义
# S	敏感（可治疗）
# I	中介 / 增加暴露仍可能有效
# R	耐药
# Non-susceptible	❗ I + R

mapping = {
    'Susceptible': 'S',
    'Resistant': 'R',
    'Intermediate': 'I',
    'Susceptible dose-dependent': 'I',   # CLSI规则
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

###########time 处理
#去除时区
df_final['order_time_jittered_std'] = (
    df_final['order_time_jittered']
    .astype(str)
    .str.replace('T', ' ')
    .str.replace('Z', '')
    .str.slice(0, 19)
)

df_final['order_time_jittered_std'].value_counts()

import pandas as pd
from datetime import datetime

# 1. 确保 mask 定义正确
mask_mgb = df_final['source'] == 'MGB'
# 2. 定义转换函数：将各种格式的字符串转为 Unix 秒数
def to_seconds_robust(val):
    if pd.isna(val):
        return None
    s = str(val).replace('T', ' ').replace('Z', '')[:19]
    try:
        # 尝试带时间的格式
        return datetime.strptime(s, '%Y-%m-%d %H:%M:%S').timestamp()
    except ValueError:
        try:
            # 尝试纯日期格式
            return datetime.strptime(s, '%Y-%m-%d').timestamp()
        except ValueError:
            return None

print("正在处理 MGB 极端时间...")
# 直接对原始列 order_time_jittered 进行处理，避免 KeyError
mgb_seconds = df_final.loc[mask_mgb, 'order_time_jittered'].apply(to_seconds_robust)

# 3. 计算极值
s_min = mgb_seconds.min()
s_max = mgb_seconds.max()

# 4. 定义目标映射范围 (2015-2024)
target_min = datetime(2015, 1, 1).timestamp()
target_max = datetime(2024, 12, 31).timestamp()

# 5. 执行线性拉伸
print("正在执行线性映射...")
# 加上处理，防止除以 0（虽然在你的数据集中不太可能）
if s_max != s_min:
    mgb_mapped_seconds = (
        (mgb_seconds - s_min) / (s_max - s_min) * (target_max - target_min) + target_min
    )
    # 6. 转回 datetime 并填回 order_time_jittered_std
    # 这一步会自动处理 ns 范围限制，因为映射后的值都在 2015 年后
    df_final.loc[mask_mgb, 'order_time_jittered_std'] = pd.to_datetime(mgb_mapped_seconds, unit='s')
else:
    # 如果 MGB 只有一个时间点，直接设为目标起始点
    df_final.loc[mask_mgb, 'order_time_jittered_std'] = pd.Timestamp('2015-01-01')

# 6. 转回 datetime 并强制舍去秒以下的小数点
# 我们先转成 datetime，然后用 floor('s') 把纳秒、微秒全部抹平
df_final.loc[mask_mgb, 'order_time_jittered_std'] = (
    pd.to_datetime(mgb_mapped_seconds, unit='s')
    .dt.floor('s')
)

# 7. 同样，对于非 MGB 的数据（Stanford, UTSW 等），也统一抹平精度
mask_others = ~mask_mgb
df_final.loc[mask_others, 'order_time_jittered_std'] = (
    pd.to_datetime(df_final.loc[mask_others, 'order_time_jittered_std'], errors='coerce')
    .dt.floor('s')
)
print("处理完成！")
df_final.to_csv('./01_combined_culture_cohort2_std_time.csv', index=False)

# 1. 强制将该列转换为 datetime 类型
df_final['order_time_jittered_std'] = pd.to_datetime(df_final['order_time_jittered_std'])
df_final['order_time_year'] = df_final['order_time_jittered_std'].dt.year.astype('Int64')
df_final['order_time_month'] = df_final['order_time_jittered_std'].dt.month.astype('Int64')

df_final.to_csv('./01_combined_culture_cohort2_std_clean_time.csv', index=False)
###MGB order_time_jittered_utc_shifted Description: Microbiology culture order timestamp (anonymized but internally consistent)
# For MGB data, timestamps were anonymized but internally consistent.
# We applied linear rescaling to align the temporal range with the Stanford dataset,
# preserving relative temporal structure while avoiding direct calendar-based comparisons.
# 分析类型	是否可行
# 趋势对比	✅
# 建模	✅
# 绝对时间比较	❌
# 政策/疫情分析	❌
# 时间先后关系	❌

#转为宽数据
# | anon_id | organism_std          | ertapenem | meropenem | ciprofloxacin | ... |
# | ------- | --------------------- | --------- | --------- | ------------- | --- |
# | JCxxx   | Klebsiella pneumoniae | S         | R         | I             | ... |
# 检查是否存在重复的 Index 组合
# 1. 定义唯一标识一个“采样及其鉴定结果”的列
# 包含时间、机构、就诊ID、医嘱ID、细菌种类
# 2. 检查在这些标识下，是否存在对同一种抗生素的多次测试
# 1. 定义“核心标识列”（决定哪些行属于同一次细菌药敏测试）
# 0. 只保留有效数据（提前过滤）
df = df[
    df['antibiotic_std'].notna() &
    df['susceptibility_std'].isin(['R','I','S'])
]

# 1. 定义核心列
core_id_cols = [
    'anon_id',
    'pat_enc_csn_id_coded',
    'order_proc_id_coded',
    'order_time_jittered',
    'organism_std'
]

# 2. 定义优先级
priority_map = {'R': 3, 'I': 2, 'S': 1}
df['priority'] = df['susceptibility_std'].map(priority_map)

# 3. 排序（R优先）
df_sorted = df.sort_values(
    by=core_id_cols + ['antibiotic_std', 'priority'],
    ascending=[True]*len(core_id_cols + ['antibiotic_std']) + [False]
)

# 4. 去重
df_cleaned = df_sorted.drop_duplicates(
    subset=core_id_cols + ['antibiotic_std'],
    keep='first'
)

# 5. 转宽表
df_wide = df_cleaned[
    core_id_cols + ['antibiotic_std', 'susceptibility_std']
].pivot(
    index=core_id_cols,
    columns='antibiotic_std',
    values='susceptibility_std'
).reset_index()

print("最终宽表 shape:", df_wide.shape)

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
df_final.to_csv('./01_combined_culture_cohort2_std_clean_time_wide.csv', index=False)


##############################整合所有表############################################################################
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/')
import pandas as pd
import polars as pl

# --- 第一步：加载主表 (Cohort) ---
# 它是所有关联的基准，行数必须严格锁定
cohort = pl.read_csv("01_combined_culture_cohort2_std_clean_time.csv")
original_count = cohort.height
print(f"主表原始行数: {original_count}")

# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]

# --- 第二步：合并 Demographics ---
demo = pl.read_csv("06_combined_microbiology_cultures_demographics2.csv")
# 检查 demo 表是否有重复键，防止合并后行数爆炸
if demo.select(keys).is_duplicated().any():
    print("警告：Demographics 表中存在重复的样本键，请检查数据！")

step1_df = cohort.join(demo, on=keys, how="left")

# 实时检查
print(f"合并 Demo 后行数: {step1_df.height} (预期应为 {original_count})")

# --- 第三步：合并 ADI Scores ---
adi = pl.read_csv("02_combined_microbiology_cultures_adi_scores2.csv")
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
print(f"读取成功，行数: {df.height}, 列数: {len(df.columns)}")
print(df.head())

#####################阶段二：病房信息整合 (Ward Info)
# 1. 加载 Ward 表
ward = pl.read_csv("12_combined_microbiology_cultures_ward_info2.csv")
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

# 执行左连接：保留 1200 万行的队列，只在有匹配的地方填入实验数据
master_v3 = master_v2.join(
    labs_cleaned.rename({"source": "source_labs"}),
    on=keys,
    how="left"
)

print(f"最终主表行数: {master_v3.height}")
print(f"当前总列数: {len(master_v3.columns)}")
master_v3.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs.parquet")



#######################Prior Medications (既往用药史)###################################
# 加载既往用药表
prior_med = pl.read_csv("10_combined_microbiology_cultures_prior_med2.csv")
# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded","order_time_jittered"]
if prior_med.select(keys).is_duplicated().any():
    print("警告：prior_med 表中存在重复的样本键，请检查数据！")
####
duplicates = prior_med.filter(prior_med.select(keys).is_duplicated()).sort(keys)
print(duplicates.head(10))

# 观察列名 prior_org_days_to_culture 和 prior_org_specific，这张表记录的是：在当前这次细菌培养之前，该患者过去还检出过什么菌。
#
# 重复的原因：一个人在本次感染之前，可能在过去 3 年内有过 5 次不同的感染记录（比如 1951 年一次大肠杆菌，1952 年又一次）。所以同一个 order_proc_id_coded 会对应多行历史记录。
#
# 临床价值：这是预测耐药性的“核武器”。如果患者 3 个月前感染过“耐药铜绿假单胞菌”，那么他今天这次感染大概率还是同一种菌或具有类似的耐药谱。

# 处理策略：从“序列”到“特征”
# 我们不能把这些历史记录直接 Join 进去（会导致行数爆炸），必须把它们扁平化（Flatten）。我们需要构建几个关键特征：
# 最近一次感染距今多久（取 prior_org_days_to_culture 的最小值）。
# 过去是否感染过某种特定高危菌（如 MRSA, VRE, 或大肠杆菌）。
# 历史感染的总次数。

# 1. 预处理：转换天数为数值
# 1. 聚合逻辑（DataFrame 模式直接运行）
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

# 2. 批量加前缀（使用表达式更优雅，避免手动数索引）
# 我们排除 keys 列表中的列，给剩下的列（菌种名）加上 hist_bug_ 前缀
prior_bugs_wide = prior_bugs_wide.with_columns([
    pl.col(c).alias(f"hist_bug_{c}")
    for c in prior_bugs_wide.columns if c not in keys
]).select([*keys, pl.col("^hist_bug_.*$")])

print(f"全量聚合后的菌种列数: {len(prior_bugs_wide.columns) - len(keys)}")

# 最终合并
master_v4 = master_v3.join(
    prior_bugs_wide.rename({"source": "source_prior_bugs"}),
    on=keys,
    how="left"
)

# 填充合并后的缺失值
# 历史上没出现过的菌，统计值自然应该是 0
master_v4 = master_v4.with_columns([
    pl.col("^hist_bug_.*$").fill_null(0)
])

print(f"Master v4 最终维度: {master_v4.shape}")
master_v4.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed.parquet")

# 计算每种历史菌种的非零覆盖率
bug_summary = master_v4.select(pl.col("^hist_bug_.*$")).sum() / master_v4.height
# 看看哪些菌种太罕见
rare_bugs = [c for c in bug_summary.columns if bug_summary[c][0] < 0.0001] # 覆盖率低于万分之一
print(f"罕见菌种数量: {len(rare_bugs)}")
#4


################################下一阶段实操：整合 Vitals (生命体征)
# 1. 加载 Vitals
vitals = pl.read_csv("13_combined_microbiology_cultures_vitals.csv")
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

# 将字符串 "Null" 转换为真正的 Polars Null，并转为浮点型
vitals = vitals.with_columns([
    pl.col(c).replace("Null", None).cast(pl.Float64, strict=False)
    for c in feature_cols
])

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
abx_exp = pl.read_csv("03_combined_microbiology_cultures_antibiotic_class_exposure2.csv")
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
    .filter(pl.col("drug_code").is_not_null()) # 过滤掉没有药物代码的记录
    .group_by([*keys, "drug_code"])
    .agg(pl.col("time_to_culturetime").min()) # 聚合：取最近的一次暴露
    .pivot(
        index=keys,
        on="drug_code",
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
    .filter(pl.col("drug_code").is_not_null())
    .group_by([*keys, "drug_code"])
    .agg(pl.col("time_to_culturetime").min().alias("min_days"))
    .pivot(
        index=keys,
        on="drug_code",
        values="min_days"
    )
)

# 重新命名
abx_final_cleaned = abx_features_cleaned.rename({
    col: f"abx_exp_{col}"
    for col in abx_features_cleaned.columns if col not in keys
})

print(f"最终抗生素特征表行数: {abx_final_cleaned.height}")

# 合并时，我们面临一个关键决策：如何填充缺失值？
#
# abx_exp_any_XXX (布尔列)：如果缺失，说明从未用过，填 0。
#
# abx_exp_XXX (天数列)：如果缺失，说明距离“无穷远”。在机器学习中，填一个比数据集最大跨度还大的常数（比如 3650 天，即 10 年）通常比填 0 更合理，因为 0 代表“正在使用”。

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
sub_exp = pl.read_csv("04_combined_microbiology_cultures_antibiotic_subtype_exposure2.csv")
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
        (pl.col("drug_code").is_not_null()) &
        (pl.col("drug_code").is_in(["null", "Null", "NULL", ""]).not_())
    )
)

print(f"有效暴露记录行数: {sub_exp_cleaned.height}")

if sub_exp_cleaned.height > 0:
    # 2. 聚合逻辑：每个样本键取每种药物的“最近距离”
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

    # 3. 增加前缀以区分特征
    sub_final = sub_features.rename({
        col: f"sub_exp_{col}"
        for col in sub_features.columns if col not in keys
    })

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
#cmbd = pl.read_csv("05_combined_microbiology_cultures_comorbidity2.csv")
# 使用 null_values 参数将字符串 "Null" 映射为真正的 Null
cmbd = pl.read_csv(
    "05_combined_microbiology_cultures_comorbidity2.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    infer_schema_length=10000  # 增加推断长度以提高鲁棒性
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
    .filter(pl.col("comorbidity_component").is_not_null())
    .select([*keys, "comorbidity_component"])
)

# 2. Pivot 转换：将合并症名称变为特征列
# 如果某个 key 对应某个合并症，值设为 1，缺失则后面填充 0
cmbd_features = (
    cmbd_cleaned
    .with_columns(pl.lit(1).alias("val"))
    .group_by([*keys, "comorbidity_component"])
    .agg(pl.col("val").max())  # 确保同一个样本的同一个病只计一次
    .pivot(
        index=keys,
        on="comorbidity_component",
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

master_v8.write_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub_comorbidityvv.parquet")



###########################microbiology_cultures_nursing_home_visit
import polars as pl
import gc
# 1. 载入刚刚保存的大表
master_v8 = pl.read_parquet("./merge_all/culture_cohort_demographics_adi_ward_labs_priorMed_vitals_antibiotic_class_sub_comorbidityvv.parquet")

# 1. 修正读取：统一处理各类 Null 字符串
# 2. 读取护理院数据，显式指定类型以解决 3.0 解析问题
nh_visits = pl.read_csv(
    "09_combined_microbiology_cultures_nursing_home_visits2.csv",
    null_values=["Null", "NULL", "null", "NaN"],
    schema_overrides={
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
master_v9 = master_v8_compact.join(nh_features, on=keys, how="left")

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
    pl.col("antibiotic_std").is_null() | pl.col("susceptibility_std").is_null()
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
