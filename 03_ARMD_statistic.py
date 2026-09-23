
import os
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

df = pd.read_csv('./01_combined_culture_cohort3.csv')
print(df)

df_plot = df.copy()

patient_counts = (
    df_plot.groupby('source')['anon_id']
    .nunique()
    .reset_index(name='patient_count')
)

patient_counts['ratio'] = patient_counts['patient_count'] / patient_counts['patient_count'].sum()

print(patient_counts)
patient_counts.to_csv('./results/01_combined_culture_cohort.csv', index=False)

import pandas as pd
df_tmp = df.copy()
total_records = len(df_tmp)
overall = pd.DataFrame({
    'source': ['All'],
    'year': ['All'],
    'record_count': [total_records]
})

overall['record_ratio'] = overall['record_count'] / total_records
by_source = (
    df_tmp.groupby('source')
    .size()
    .reset_index(name='record_count')
)

by_source['year'] = 'All'
by_source['record_ratio'] = by_source['record_count'] / total_records
by_year = (
    df_tmp.groupby('order_time_year')
    .size()
    .reset_index(name='record_count')
)

by_year['source'] = 'All'
by_year = by_year.rename(columns={'order_time_year': 'year'})

by_year['record_ratio'] = by_year['record_count'] / total_records
by_year_source = (
    df_tmp.groupby(['order_time_year', 'source'])
    .size()
    .reset_index(name='record_count')
)

by_year_source = by_year_source.rename(
    columns={'order_time_year': 'year'}
)

by_year_source['record_ratio'] = (
    by_year_source['record_count'] / total_records
)

final_stats = pd.concat(
    [
        overall,
        by_source,
        by_year,
        by_year_source
    ],
    ignore_index=True
)

final_stats = final_stats[
    ['source', 'year', 'record_count', 'record_ratio']
]

print(final_stats)


final_stats.to_csv(
    './results/02AMRD_record_count_ratio.csv',
    index=False
)
import pandas as pd
df_tmp = df.copy()
overall = pd.DataFrame({
    'source': ['All'],
    'year': ['All'],
    'patient_count': [df_tmp['anon_id'].nunique()]
})
overall['patient_ratio'] = overall['patient_count'] / df_tmp['anon_id'].nunique()
by_source = (
    df_tmp.groupby('source')['anon_id']
    .nunique()
    .reset_index(name='patient_count')
)
by_source['year'] = 'All'
by_source['patient_ratio'] = by_source['patient_count'] / df_tmp['anon_id'].nunique()
by_year = (
    df_tmp.groupby('order_time_year')['anon_id']
    .nunique()
    .reset_index(name='patient_count')
)
by_year['source'] = 'All'
by_year = by_year.rename(columns={'order_time_year': 'year'})
by_year['patient_ratio'] = by_year['patient_count'] / df_tmp['anon_id'].nunique()

by_year_source = (
    df_tmp.groupby(['order_time_year', 'source'])['anon_id']
    .nunique()
    .reset_index(name='patient_count')
)
by_year_source = by_year_source.rename(columns={'order_time_year': 'year'})
by_year_source['patient_ratio'] = by_year_source['patient_count'] / df_tmp['anon_id'].nunique()
final_stats = pd.concat([overall, by_source, by_year, by_year_source], ignore_index=True)
print(final_stats)
final_stats.to_csv('./results/02AMRD_patient_count_ratio.csv')

import pandas as pd
df_tmp = df.copy()
df_tmp['patient_id'] = (
    df_tmp['source'].astype(str).str.strip() + '_' +
    df_tmp['anon_id'].astype(str).str.strip()
)

total_patients = df_tmp['patient_id'].nunique()

print(f"Total unique patients: {total_patients}")


overall = pd.DataFrame({
    'source': ['All'],
    'year': ['All'],
    'patient_count': [total_patients]
})

overall['patient_ratio'] = (
    overall['patient_count'] / total_patients
)

by_source = (
    df_tmp.groupby('source')['patient_id']
    .nunique()
    .reset_index(name='patient_count')
)

by_source['year'] = 'All'

by_source['patient_ratio'] = (
    by_source['patient_count'] / total_patients
)

by_year = (
    df_tmp.groupby('order_time_year')['patient_id']
    .nunique()
    .reset_index(name='patient_count')
)

by_year['source'] = 'All'

by_year = by_year.rename(
    columns={'order_time_year': 'year'}
)

by_year['patient_ratio'] = (
    by_year['patient_count'] / total_patients
)

by_year_source = (
    df_tmp.groupby(
        ['order_time_year', 'source']
    )['patient_id']
    .nunique()
    .reset_index(name='patient_count')
)

by_year_source = by_year_source.rename(
    columns={'order_time_year': 'year'}
)

by_year_source['patient_ratio'] = (
    by_year_source['patient_count'] / total_patients
)

final_stats = pd.concat(
    [
        overall,
        by_source,
        by_year,
        by_year_source
    ],
    ignore_index=True
)

print(final_stats)
print("\nSource-specific patient counts:")
print(by_source)
print(f"\nTotal unique patients: {total_patients}")

final_stats.to_csv(
    './results/02AMRD_patient_count_ratio_0811.csv',
    index=False
)

import pandas as pd
df_proc_unique = df[['order_proc_id_coded', 'source', 'order_time_year']]
total_procs = len(df_proc_unique)

def get_proc_stats(df_in, group_cols, source_val='All', year_val='All'):
    res = df_in.groupby(group_cols)['order_proc_id_coded'].nunique().reset_index(name='proc_count')
    if 'source' not in res.columns: res['source'] = source_val
    if 'order_time_year' not in res.columns:
        res['year'] = year_val
    else:
        res = res.rename(columns={'order_time_year': 'year'})

    return res

overall = pd.DataFrame({
    'source': ['All'], 'year': ['All'], 'proc_count': [total_procs]
})

by_source = get_proc_stats(df_proc_unique, ['source'], year_val='All')
by_year = get_proc_stats(df_proc_unique, ['order_time_year'], source_val='All')
by_year_source = get_proc_stats(df_proc_unique, ['order_time_year', 'source'])


final_proc_stats = pd.concat([overall, by_source, by_year, by_year_source], ignore_index=True)
final_proc_stats['proc_ratio'] = final_proc_stats['proc_count'] / total_procs

final_proc_stats['year'] = final_proc_stats['year'].astype(str)
final_proc_stats = final_proc_stats.sort_values(
    by=['source', 'year'],
    key=lambda x: x.map(lambda val: '0000' if val == 'All' else str(val))
)

print(final_proc_stats)
final_proc_stats.to_csv('results/AMRD_count_ratio_order_proc_id_coded.csv', index=False)


###########################culture
import pandas as pd
# 直接使用 df，不进行 drop_duplicates()
df_stats = df[['source', 'order_time_year', 'culture_description']].copy()
# 统一格式（可选，防止因为大小写导致同类被拆分）
#df_stats['culture_description'] = df_stats['culture_description'].str.upper().fillna('UNKNOWN')
# 2. 修复后的统计函数
def get_culture_counts(df_in, group_cols, source_label='All', year_label='All'):
    # 计算各类型的数量
    stats = df_in.groupby(group_cols + ['culture_description']).size().reset_index(name='record_count')

    # 修复 ValueError: No group keys passed!
    if not group_cols:
        group_totals = stats['record_count'].sum()
    else:
        group_totals = stats.groupby(group_cols)['record_count'].transform('sum')

    stats['record_ratio'] = stats['record_count'] / group_totals

    # 填充标签，确保 All 被正确标记
    if 'source' not in stats.columns:
        stats['source'] = source_label

    if 'order_time_year' not in stats.columns:
        stats['year'] = year_label
    else:
        stats = stats.rename(columns={'order_time_year': 'year'})

    return stats


# 3. 分步执行统计
print("正在计算各项指标...")
# 1️⃣ 总体 (All Source, All Year)
overall = get_culture_counts(df_stats, [], 'All', 'All')

# 2️⃣ 分地区 (By Source, All Year)
by_source = get_culture_counts(df_stats, ['source'], None, 'All')

# 3️⃣ 分年份 (All Source, By Year)
by_year = get_culture_counts(df_stats, ['order_time_year'], 'All', None)

# 4️⃣ 分年份 + 地区 (By Source, By Year)
by_year_source = get_culture_counts(df_stats, ['order_time_year', 'source'], None, None)

# 4. 合并所有结果
final_culture_distribution = pd.concat([overall, by_source, by_year, by_year_source], ignore_index=True)

# 5. 格式化输出：将 'year' 统一为字符串，方便排序和 CSV 保存
final_culture_distribution['year'] = final_culture_distribution['year'].astype(str)

# 6. 排序逻辑：让 'All' 排在前面，年份按顺序排，每个组内按数量降序
# 我们通过一个自定义排序权重来实现
final_culture_distribution['s_sort'] = final_culture_distribution['source'].apply(
    lambda x: '0' if x == 'All' else '1' + x)
final_culture_distribution['y_sort'] = final_culture_distribution['year'].apply(
    lambda x: '0' if x == 'All' else '1' + x)

final_culture_distribution = final_culture_distribution.sort_values(
    ['s_sort', 'y_sort', 'record_count'],
    ascending=[True, True, False]
).drop(columns=['s_sort', 'y_sort'])

# 7. 保存
final_culture_distribution.to_csv('results/AMRD_culture_record_distribution_final.csv', index=False)

# 验证结果
print("\n--- 验证总体合并 (All + All) ---")
print(final_culture_distribution[
          (final_culture_distribution['source'] == 'All') & (final_culture_distribution['year'] == 'All')].head())

print("\n--- 验证地区合并 (Source + All) ---")
print(final_culture_distribution[
          (final_culture_distribution['source'] != 'All') & (final_culture_distribution['year'] == 'All')].head())

print("\n--- 验证年份合并 (All + Year) ---")
print(final_culture_distribution[
          (final_culture_distribution['source'] == 'All') & (final_culture_distribution['year'] != 'All')].head())

##不同organism_std 反映的是物种覆盖度。只要不同地区都在测同一种病原体，这个比例的和就一定会大于 1
import pandas as pd
# 1. 预筛选：既然只统计 organism_std 的种类，先去重可以极大提升速度
# 只保留对统计有用的列，并去重
df_stats = df[['source', 'order_time_year', 'organism_std']].drop_duplicates()

# 全局总种类数（作为分母）
total_species = df_stats['organism_std'].nunique()

# 定义统计辅助函数减少重复代码
def get_stats(df_in, group_cols, source_val, year_val):
    res = (
        df_in.groupby(group_cols)['organism_std']
        .nunique()
        .reset_index(name='organism_count')
    )
    if 'source' not in res.columns: res['source'] = source_val
    if 'order_time_year' not in res.columns: res['year'] = year_val
    else: res = res.rename(columns={'order_time_year': 'year'})
    return res

# 执行多维度统计
overall = pd.DataFrame({
    'source': ['All'], 'year': ['All'], 'organism_count': [total_species]
})

by_source = get_stats(df_stats, ['source'], None, 'All')
by_year = get_stats(df_stats, ['order_time_year'], 'All', None)
by_year_source = get_stats(df_stats, ['order_time_year', 'source'], None, None)

# 合并
final_stats = pd.concat([overall, by_source, by_year, by_year_source], ignore_index=True)

# 计算比例
final_stats['organism_ratio'] = final_stats['organism_count'] / total_species

# 调整列顺序使其更美观
final_stats = final_stats[['source', 'year', 'organism_count', 'organism_ratio']]

print(final_stats)
final_stats.to_csv('results/AMRD_organism_std_count_ratio.csv', index=False)

##

#####trend time
import pandas as pd
df_tmp = df.copy()
# ⚠️ 处理时间（去掉NA，比如ECUH）
df_tmp = df_tmp.dropna(subset=['order_time_year'])
# 1️⃣ 每年 × 每中心（去重患者数）
trend = (
    df_tmp.groupby(['order_time_year', 'source'])['anon_id']
    .nunique()
    .reset_index(name='patient_count')
)
# 2️⃣ 总体趋势（所有中心合并）
trend_total = (
    df_tmp.groupby('order_time_year')['anon_id']
    .nunique()
    .reset_index(name='patient_count')
)
trend_total['source'] = 'All'

# 合并
trend_all = pd.concat([trend, trend_total], ignore_index=True)
trend_all.to_csv('results/AMRD_trend_all_time.csv')

df['susceptibility_std'].value_counts()
########order_proc_id_coded
# import pandas as pd
# df_tmp = df.copy()
# # ⚠️ 处理时间（去掉NA，比如ECUH）
# df_tmp = df_tmp.dropna(subset=['order_time_year'])
# # 1️⃣ 每年 × 每中心（去重患者数）
# trend = (
#     df_tmp.groupby(['order_time_year', 'source'])['order_proc_id_coded']
#     .nunique()
#     .reset_index(name='proc_count')
# )
# # 2️⃣ 总体趋势（所有中心合并）
# trend_total = (
#     df_tmp.groupby('order_time_year')['order_proc_id_coded']
#     .nunique()
#     .reset_index(name='proc_count')
# )
# trend_total['source'] = 'All'
#
# # 合并
# trend_all = pd.concat([trend, trend_total], ignore_index=True)
# # 将年份转为统一格式，并按照年份、source 排序
# trend_all['order_time_year'] = trend_all['order_time_year'].astype(int)
# trend_all = trend_all.sort_values(['order_time_year', 'source'], ascending=[True, True])
#
# # 把 'All' 放到每个年份组的最前面（可选）
# trend_all['is_total'] = trend_all['source'] == 'All'
# trend_all = trend_all.sort_values(['order_time_year', 'is_total'], ascending=[True, False]).drop(columns='is_total')
# trend_all.to_csv('AMRD_trend_all_time_proc.csv')
#根据CLSI（临床和实验室标准协会）的标准，细菌耐药率的计算通常采用公式：（R + I）/（R + I + S）

import pandas as pd
df_tmp = df.copy()
# 1️⃣ 处理时间（去掉 NA）
df_tmp = df_tmp.dropna(subset=['order_time_year'])
# 2️⃣ 每年 × 每中心（统计记录行数，不使用 nunique）
trend = (
    df_tmp.groupby(['order_time_year', 'source'])
    .size()  # .size() 会统计包含 NaN 在内的所有行数
    .reset_index(name='record_count')
)
# 3️⃣ 总体趋势（所有中心合并）
trend_total = (
    df_tmp.groupby('order_time_year')
    .size()
    .reset_index(name='record_count')
)
trend_total['source'] = 'All'
# 4️⃣ 合并结果
trend_all = pd.concat([trend, trend_total], ignore_index=True)
# 5️⃣ 排序（按年份升序，All 放在该年份组的第一行）
trend_all['is_all'] = trend_all['source'] == 'All'
trend_all = trend_all.sort_values(
    ['order_time_year', 'is_all'],
    ascending=[True, False]
).drop(columns=['is_all'])
# 导出
trend_all.to_csv('results/AMRD_trend_all_time_records.csv', index=False)
print("统计完成！此时统计的是行数（Records），而非唯一 ID 数。")
print(trend_all.head(10))


############病原体分布
####为了统计不同年份、地区以及不同物种（organism_std）的原始记录行数（不去重）及比例
import pandas as pd
# 1. 准备数据：只保留必要列并处理空值
df_stats = df[['source', 'order_time_year', 'organism_std']].copy()
df_stats['organism_std'] = df_stats['organism_std'].fillna('Unknown')
df_stats = df_stats.dropna(subset=['order_time_year'])  # 剔除无年份数据
def get_organism_distribution(df_in, group_cols, source_label='All', year_label='All'):
    """
    计算特定分组下，各物种的记录行数及占比
    """
    # 统计每个物种出现的行数
    stats = df_in.groupby(group_cols + ['organism_std']).size().reset_index(name='record_count')

    # 计算该分组（如某年某中心）的总行数作为分母
    if not group_cols:
        group_totals = stats['record_count'].sum()
    else:
        group_totals = stats.groupby(group_cols)['record_count'].transform('sum')

    # 计算占比
    stats['record_ratio'] = stats['record_count'] / group_totals

    # 补充标签
    if 'source' not in stats.columns: stats['source'] = source_label
    if 'order_time_year' not in stats.columns:
        stats['year'] = year_label
    else:
        stats = stats.rename(columns={'order_time_year': 'year'})

    return stats


# 2. 多维度并行统计
print("正在执行分层统计...")
# 2.1 总体物种分布
overall = get_organism_distribution(df_stats, [], 'All', 'All')
# 2.2 各地区物种分布（不分年）
by_source = get_organism_distribution(df_stats, ['source'], None, 'All')
# 2.3 各年份物种分布（不分中心）
by_year = get_organism_distribution(df_stats, ['order_time_year'], 'All', None)
# 2.4 年份 + 地区交叉分布
by_year_source = get_organism_distribution(df_stats, ['order_time_year', 'source'], None, None)
# 3. 合并与整理
final_org_dist = pd.concat([overall, by_source, by_year, by_year_source], ignore_index=True)
# 4. 排序：确保汇总行(All)靠前，各组内按物种数量降序
final_org_dist['year'] = final_org_dist['year'].astype(str)
final_org_dist['s_sort'] = final_org_dist['source'].apply(lambda x: '0' if x == 'All' else '1' + x)
final_org_dist['y_sort'] = final_org_dist['year'].apply(lambda x: '0' if x == 'All' else '1' + x)
final_org_dist = final_org_dist.sort_values(
    ['s_sort', 'y_sort', 'record_count'],
    ascending=[True, True, False]
).drop(columns=['s_sort', 'y_sort'])
# 5. 导出结果
final_org_dist.to_csv('results/AMRD_organism_record_distribution.csv', index=False)
print("统计完成！结果已保存至 AMRD_organism_record_distribution.csv")

#################R
#####不同年份和地区耐药率
import pandas as pd
# 1. 准备数据：只保留必要列并处理空值
# 过滤掉抗生素或物种缺失的行，以及药敏结果缺失的行
df_ast = df[['source', 'order_time_year', 'organism_std', 'antibiotic_std', 'susceptibility_std']].copy()
df_ast = df_ast.dropna(subset=['order_time_year', 'organism_std', 'antibiotic_std', 'susceptibility_std'])
# 2. 定义统计函数
def get_resistance_stats(df_in, group_cols, source_label='All', year_label='All'):
    """
    计算特定分组下，每个物种对每种抗生素的耐药率
    """
    # 统计每个 [分组 + 物种 + 抗生素 + 结果] 的数量
    counts = df_in.groupby(group_cols + ['organism_std', 'antibiotic_std', 'susceptibility_std']).size().reset_index(
        name='n')

    # 转换为透视表结构，方便计算 R/(S+I+R)
    # columns=['S', 'I', 'R']，缺失的结果填 0
    pivot_stats = counts.pivot_table(
        index=group_cols + ['organism_std', 'antibiotic_std'],
        columns='susceptibility_std',
        values='n',
        fill_value=0
    ).reset_index()

    # 确保 S, I, R 列都存在（防止某些分组下完全没出现某个结果）
    for col in ['S', 'I', 'R']:
        if col not in pivot_stats.columns:
            pivot_stats[col] = 0

    # 计算总数和耐药率
    pivot_stats['total_tested'] = pivot_stats['S'] + pivot_stats['I'] + pivot_stats['R']

    # 过滤掉测试样本量太少的情况（例如少于 10 个样本的结果通常不具备统计意义）
    pivot_stats = pivot_stats[pivot_stats['total_tested'] > 0].copy()

    pivot_stats['resistance_rate'] = (pivot_stats['R'] + pivot_stats['I'])/ pivot_stats['total_tested']

    # 填充标签
    if 'source' not in pivot_stats.columns: pivot_stats['source'] = source_label
    if 'order_time_year' not in pivot_stats.columns:
        pivot_stats['year'] = year_label
    else:
        pivot_stats = pivot_stats.rename(columns={'order_time_year': 'year'})

    return pivot_stats


# 3. 分维度计算
print("正在计算各维度耐药率...")
# 3.1 总体耐药率
overall_ast = get_resistance_stats(df_ast, [], 'All', 'All')

# 3.2 按地区汇总
by_source_ast = get_resistance_stats(df_ast, ['source'], None, 'All')

# 3.3 按年份汇总
by_year_ast = get_resistance_stats(df_ast, ['order_time_year'], 'All', None)

# 3.4 年份 + 地区交叉
by_year_source_ast = get_resistance_stats(df_ast, ['order_time_year', 'source'], None, None)

# 4. 合并结果
final_ast_report = pd.concat([overall_ast, by_source_ast, by_year_ast, by_year_source_ast], ignore_index=True)

# 5. 排序与保存
final_ast_report = final_ast_report.sort_values(
    ['source', 'year', 'organism_std', 'resistance_rate'],
    ascending=[True, True, True, False]
)

final_ast_report.to_csv('results/AMRD_resistance_rate_report.csv', index=False)
print("耐药率统计完成！")

############不同月份和地区耐药率
import pandas as pd
# 1. 准备数据：只保留必要列并处理空值
# 过滤掉抗生素或物种缺失的行，以及药敏结果缺失的行
df_ast = df[['source', 'order_time_month', 'organism_std', 'antibiotic_std', 'susceptibility_std']].copy()
df_ast = df_ast.dropna(subset=['order_time_month', 'organism_std', 'antibiotic_std', 'susceptibility_std'])
# 2. 定义统计函数
def get_resistance_stats(df_in, group_cols, source_label='All', year_label='All'):
    """
    计算特定分组下，每个物种对每种抗生素的耐药率
    """
    # 统计每个 [分组 + 物种 + 抗生素 + 结果] 的数量
    counts = df_in.groupby(group_cols + ['organism_std', 'antibiotic_std', 'susceptibility_std']).size().reset_index(
        name='n')

    # 转换为透视表结构，方便计算 R/(S+I+R)
    # columns=['S', 'I', 'R']，缺失的结果填 0
    pivot_stats = counts.pivot_table(
        index=group_cols + ['organism_std', 'antibiotic_std'],
        columns='susceptibility_std',
        values='n',
        fill_value=0
    ).reset_index()

    # 确保 S, I, R 列都存在（防止某些分组下完全没出现某个结果）
    for col in ['S', 'I', 'R']:
        if col not in pivot_stats.columns:
            pivot_stats[col] = 0

    # 计算总数和耐药率
    pivot_stats['total_tested'] = pivot_stats['S'] + pivot_stats['I'] + pivot_stats['R']

    # 过滤掉测试样本量太少的情况（例如少于 10 个样本的结果通常不具备统计意义）
    pivot_stats = pivot_stats[pivot_stats['total_tested'] > 0].copy()

    pivot_stats['resistance_rate'] = (pivot_stats['R']+pivot_stats['S']) / pivot_stats['total_tested']

    # 填充标签
    if 'source' not in pivot_stats.columns: pivot_stats['source'] = source_label
    if 'order_time_month' not in pivot_stats.columns:
        pivot_stats['month'] = year_label
    else:
        pivot_stats = pivot_stats.rename(columns={'order_time_month': 'month'})

    return pivot_stats


# 3. 分维度计算
print("正在计算各维度耐药率...")
# 3.1 总体耐药率
overall_ast = get_resistance_stats(df_ast, [], 'All', 'All')

# 3.2 按地区汇总
by_source_ast = get_resistance_stats(df_ast, ['source'], None, 'All')

# 3.3 按年份汇总
by_year_ast = get_resistance_stats(df_ast, ['order_time_month'], 'All', None)

# 3.4 年份 + 地区交叉
by_year_source_ast = get_resistance_stats(df_ast, ['order_time_month', 'source'], None, None)

# 4. 合并结果
final_ast_report = pd.concat([overall_ast, by_source_ast, by_year_ast, by_year_source_ast], ignore_index=True)

# 5. 排序与保存
final_ast_report = final_ast_report.sort_values(
    ['source', 'month', 'organism_std', 'resistance_rate'],
    ascending=[True, True, True, False]
)

final_ast_report.to_csv('results/AMRD_resistance_rate_report_month.csv', index=False)
print("耐药率统计完成！")

###########SIR
import pandas as pd

# 1. 准备数据并剔除缺失关键信息的行
# 包含：来源、年份、菌种、抗生素、敏感性结果
df_ast = df[['source', 'order_time_year', 'organism_std', 'antibiotic_std', 'susceptibility_std']].copy()
df_ast = df_ast.dropna(subset=['order_time_year', 'organism_std', 'antibiotic_std', 'susceptibility_std'])


def get_sir_distribution(df_in, group_cols, source_label='All', year_label='All'):
    """
    计算特定分组下，每种 [菌种-抗生素] 组合的 S/I/R 比例
    """
    # 计数
    counts = df_in.groupby(group_cols + ['organism_std', 'antibiotic_std', 'susceptibility_std']).size().reset_index(
        name='n')

    # 透视表：将 S, I, R 转为列
    sir_stats = counts.pivot_table(
        index=group_cols + ['organism_std', 'antibiotic_std'],
        columns='susceptibility_std',
        values='n',
        fill_value=0
    ).reset_index()

    # 确保 S, I, R 三列都存在
    for col in ['S', 'I', 'R']:
        if col not in sir_stats.columns:
            sir_stats[col] = 0

    # 计算该组合的总测试数
    sir_stats['total_tested'] = sir_stats['S'] + sir_stats['I'] + sir_stats['R']

    # 计算比例
    sir_stats['S_ratio'] = sir_stats['S'] / sir_stats['total_tested']
    sir_stats['I_ratio'] = sir_stats['I'] / sir_stats['total_tested']
    sir_stats['R_ratio'] = sir_stats['R'] / sir_stats['total_tested']

    # 补充维度标签
    if 'source' not in sir_stats.columns: sir_stats['source'] = source_label
    if 'order_time_year' not in sir_stats.columns:
        sir_stats['year'] = year_label
    else:
        sir_stats = sir_stats.rename(columns={'order_time_year': 'year'})

    return sir_stats


# 2. 执行多维度汇总统计
print("开始执行全维度 S/I/R 比例统计...")
overall_sir = get_sir_distribution(df_ast, [], 'All', 'All')
by_source_sir = get_sir_distribution(df_ast, ['source'], None, 'All')
by_year_sir = get_sir_distribution(df_ast, ['order_time_year'], 'All', None)
by_year_source_sir = get_sir_distribution(df_ast, ['order_time_year', 'source'], None, None)

# 3. 合并并格式化结果
final_sir_report = pd.concat([overall_sir, by_source_sir, by_year_sir, by_year_source_sir], ignore_index=True)

# 4. 排序：按地区、年份、菌种、测试数降序
final_sir_report = final_sir_report.sort_values(
    ['source', 'year', 'organism_std', 'total_tested'],
    ascending=[True, True, True, False]
)

# 5. 保存
final_sir_report.to_csv('results/AMRD_SIR_distribution_report.csv', index=False)
print("统计完成！结果已保存至 AMRD_SIR_distribution_report.csv")

