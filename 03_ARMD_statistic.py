
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

import pandas as pd
df_stats = df[['source', 'order_time_year', 'culture_description']].copy()

def get_culture_counts(df_in, group_cols, source_label='All', year_label='All'):
    stats = df_in.groupby(group_cols + ['culture_description']).size().reset_index(name='record_count')
    if not group_cols:
        group_totals = stats['record_count'].sum()
    else:
        group_totals = stats.groupby(group_cols)['record_count'].transform('sum')

    stats['record_ratio'] = stats['record_count'] / group_totals
    if 'source' not in stats.columns:
        stats['source'] = source_label

    if 'order_time_year' not in stats.columns:
        stats['year'] = year_label
    else:
        stats = stats.rename(columns={'order_time_year': 'year'})

    return stats

print("正在计算各项指标...")
overall = get_culture_counts(df_stats, [], 'All', 'All')
by_source = get_culture_counts(df_stats, ['source'], None, 'All')
by_year = get_culture_counts(df_stats, ['order_time_year'], 'All', None)
by_year_source = get_culture_counts(df_stats, ['order_time_year', 'source'], None, None)
final_culture_distribution = pd.concat([overall, by_source, by_year, by_year_source], ignore_index=True)
final_culture_distribution['year'] = final_culture_distribution['year'].astype(str)

final_culture_distribution['s_sort'] = final_culture_distribution['source'].apply(
    lambda x: '0' if x == 'All' else '1' + x)
final_culture_distribution['y_sort'] = final_culture_distribution['year'].apply(
    lambda x: '0' if x == 'All' else '1' + x)

final_culture_distribution = final_culture_distribution.sort_values(
    ['s_sort', 'y_sort', 'record_count'],
    ascending=[True, True, False]
).drop(columns=['s_sort', 'y_sort'])

final_culture_distribution.to_csv('results/AMRD_culture_record_distribution_final.csv', index=False)

print(final_culture_distribution[
          (final_culture_distribution['source'] == 'All') & (final_culture_distribution['year'] == 'All')].head())
print(final_culture_distribution[
          (final_culture_distribution['source'] != 'All') & (final_culture_distribution['year'] == 'All')].head())
print(final_culture_distribution[
          (final_culture_distribution['source'] == 'All') & (final_culture_distribution['year'] != 'All')].head())

import pandas as pd
df_stats = df[['source', 'order_time_year', 'organism_std']].drop_duplicates()
total_species = df_stats['organism_std'].nunique()
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

overall = pd.DataFrame({
    'source': ['All'], 'year': ['All'], 'organism_count': [total_species]
})

by_source = get_stats(df_stats, ['source'], None, 'All')
by_year = get_stats(df_stats, ['order_time_year'], 'All', None)
by_year_source = get_stats(df_stats, ['order_time_year', 'source'], None, None)
final_stats = pd.concat([overall, by_source, by_year, by_year_source], ignore_index=True)
final_stats['organism_ratio'] = final_stats['organism_count'] / total_species
final_stats = final_stats[['source', 'year', 'organism_count', 'organism_ratio']]

print(final_stats)
final_stats.to_csv('results/AMRD_organism_std_count_ratio.csv', index=False)

import pandas as pd
df_tmp = df.copy()
df_tmp = df_tmp.dropna(subset=['order_time_year'])
trend = (
    df_tmp.groupby(['order_time_year', 'source'])['anon_id']
    .nunique()
    .reset_index(name='patient_count')
)
trend_total = (
    df_tmp.groupby('order_time_year')['anon_id']
    .nunique()
    .reset_index(name='patient_count')
)
trend_total['source'] = 'All'

trend_all = pd.concat([trend, trend_total], ignore_index=True)
trend_all.to_csv('results/AMRD_trend_all_time.csv')

df['susceptibility_std'].value_counts()


import pandas as pd
df_tmp = df.copy()
df_tmp = df_tmp.dropna(subset=['order_time_year'])
trend = (
    df_tmp.groupby(['order_time_year', 'source'])
    .size() 
    .reset_index(name='record_count')
)
trend_total = (
    df_tmp.groupby('order_time_year')
    .size()
    .reset_index(name='record_count')
)
trend_total['source'] = 'All'
trend_all = pd.concat([trend, trend_total], ignore_index=True)

trend_all['is_all'] = trend_all['source'] == 'All'
trend_all = trend_all.sort_values(
    ['order_time_year', 'is_all'],
    ascending=[True, False]
).drop(columns=['is_all'])

trend_all.to_csv('results/AMRD_trend_all_time_records.csv', index=False)
print(trend_all.head(10))

import pandas as pd
df_stats = df[['source', 'order_time_year', 'organism_std']].copy()
df_stats['organism_std'] = df_stats['organism_std'].fillna('Unknown')
df_stats = df_stats.dropna(subset=['order_time_year'])  # 剔除无年份数据
def get_organism_distribution(df_in, group_cols, source_label='All', year_label='All'):
    stats = df_in.groupby(group_cols + ['organism_std']).size().reset_index(name='record_count')
    if not group_cols:
        group_totals = stats['record_count'].sum()
    else:
        group_totals = stats.groupby(group_cols)['record_count'].transform('sum')

    stats['record_ratio'] = stats['record_count'] / group_totals

    if 'source' not in stats.columns: stats['source'] = source_label
    if 'order_time_year' not in stats.columns:
        stats['year'] = year_label
    else:
        stats = stats.rename(columns={'order_time_year': 'year'})

    return stats


overall = get_organism_distribution(df_stats, [], 'All', 'All')

by_source = get_organism_distribution(df_stats, ['source'], None, 'All')

by_year = get_organism_distribution(df_stats, ['order_time_year'], 'All', None)

by_year_source = get_organism_distribution(df_stats, ['order_time_year', 'source'], None, None)

final_org_dist = pd.concat([overall, by_source, by_year, by_year_source], ignore_index=True)

final_org_dist['year'] = final_org_dist['year'].astype(str)
final_org_dist['s_sort'] = final_org_dist['source'].apply(lambda x: '0' if x == 'All' else '1' + x)
final_org_dist['y_sort'] = final_org_dist['year'].apply(lambda x: '0' if x == 'All' else '1' + x)
final_org_dist = final_org_dist.sort_values(
    ['s_sort', 'y_sort', 'record_count'],
    ascending=[True, True, False]
).drop(columns=['s_sort', 'y_sort'])

final_org_dist.to_csv('results/AMRD_organism_record_distribution.csv', index=False)


import pandas as pd

df_ast = df[['source', 'order_time_year', 'organism_std', 'antibiotic_std', 'susceptibility_std']].copy()
df_ast = df_ast.dropna(subset=['order_time_year', 'organism_std', 'antibiotic_std', 'susceptibility_std'])

def get_resistance_stats(df_in, group_cols, source_label='All', year_label='All'):
    counts = df_in.groupby(group_cols + ['organism_std', 'antibiotic_std', 'susceptibility_std']).size().reset_index(
        name='n')
    pivot_stats = counts.pivot_table(
        index=group_cols + ['organism_std', 'antibiotic_std'],
        columns='susceptibility_std',
        values='n',
        fill_value=0
    ).reset_index()

    for col in ['S', 'I', 'R']:
        if col not in pivot_stats.columns:
            pivot_stats[col] = 0

    pivot_stats['total_tested'] = pivot_stats['S'] + pivot_stats['I'] + pivot_stats['R']

    pivot_stats = pivot_stats[pivot_stats['total_tested'] > 0].copy()

    pivot_stats['resistance_rate'] = (pivot_stats['R'] + pivot_stats['I'])/ pivot_stats['total_tested']

    if 'source' not in pivot_stats.columns: pivot_stats['source'] = source_label
    if 'order_time_year' not in pivot_stats.columns:
        pivot_stats['year'] = year_label
    else:
        pivot_stats = pivot_stats.rename(columns={'order_time_year': 'year'})

    return pivot_stats


overall_ast = get_resistance_stats(df_ast, [], 'All', 'All')
by_source_ast = get_resistance_stats(df_ast, ['source'], None, 'All')
by_year_ast = get_resistance_stats(df_ast, ['order_time_year'], 'All', None)
by_year_source_ast = get_resistance_stats(df_ast, ['order_time_year', 'source'], None, None)
final_ast_report = pd.concat([overall_ast, by_source_ast, by_year_ast, by_year_source_ast], ignore_index=True)

final_ast_report = final_ast_report.sort_values(
    ['source', 'year', 'organism_std', 'resistance_rate'],
    ascending=[True, True, True, False]
)

final_ast_report.to_csv('results/AMRD_resistance_rate_report.csv', index=False)

import pandas as pd
df_ast = df[['source', 'order_time_month', 'organism_std', 'antibiotic_std', 'susceptibility_std']].copy()
df_ast = df_ast.dropna(subset=['order_time_month', 'organism_std', 'antibiotic_std', 'susceptibility_std'])
def get_resistance_stats(df_in, group_cols, source_label='All', year_label='All'):
    counts = df_in.groupby(group_cols + ['organism_std', 'antibiotic_std', 'susceptibility_std']).size().reset_index(
        name='n')
    pivot_stats = counts.pivot_table(
        index=group_cols + ['organism_std', 'antibiotic_std'],
        columns='susceptibility_std',
        values='n',
        fill_value=0
    ).reset_index()

    for col in ['S', 'I', 'R']:
        if col not in pivot_stats.columns:
            pivot_stats[col] = 0

    pivot_stats['total_tested'] = pivot_stats['S'] + pivot_stats['I'] + pivot_stats['R']

    pivot_stats = pivot_stats[pivot_stats['total_tested'] > 0].copy()

    pivot_stats['resistance_rate'] = (pivot_stats['R']+pivot_stats['S']) / pivot_stats['total_tested']
    if 'source' not in pivot_stats.columns: pivot_stats['source'] = source_label
    if 'order_time_month' not in pivot_stats.columns:
        pivot_stats['month'] = year_label
    else:
        pivot_stats = pivot_stats.rename(columns={'order_time_month': 'month'})

    return pivot_stats

overall_ast = get_resistance_stats(df_ast, [], 'All', 'All')
by_source_ast = get_resistance_stats(df_ast, ['source'], None, 'All')

by_year_ast = get_resistance_stats(df_ast, ['order_time_month'], 'All', None)

by_year_source_ast = get_resistance_stats(df_ast, ['order_time_month', 'source'], None, None)

final_ast_report = pd.concat([overall_ast, by_source_ast, by_year_ast, by_year_source_ast], ignore_index=True)

final_ast_report = final_ast_report.sort_values(
    ['source', 'month', 'organism_std', 'resistance_rate'],
    ascending=[True, True, True, False]
)

final_ast_report.to_csv('results/AMRD_resistance_rate_report_month.csv', index=False)


import pandas as pd
df_ast = df[['source', 'order_time_year', 'organism_std', 'antibiotic_std', 'susceptibility_std']].copy()
df_ast = df_ast.dropna(subset=['order_time_year', 'organism_std', 'antibiotic_std', 'susceptibility_std'])


def get_sir_distribution(df_in, group_cols, source_label='All', year_label='All'):
    counts = df_in.groupby(group_cols + ['organism_std', 'antibiotic_std', 'susceptibility_std']).size().reset_index(
        name='n')
    sir_stats = counts.pivot_table(
        index=group_cols + ['organism_std', 'antibiotic_std'],
        columns='susceptibility_std',
        values='n',
        fill_value=0
    ).reset_index()
    for col in ['S', 'I', 'R']:
        if col not in sir_stats.columns:
            sir_stats[col] = 0

    sir_stats['total_tested'] = sir_stats['S'] + sir_stats['I'] + sir_stats['R']

    sir_stats['S_ratio'] = sir_stats['S'] / sir_stats['total_tested']
    sir_stats['I_ratio'] = sir_stats['I'] / sir_stats['total_tested']
    sir_stats['R_ratio'] = sir_stats['R'] / sir_stats['total_tested']

    if 'source' not in sir_stats.columns: sir_stats['source'] = source_label
    if 'order_time_year' not in sir_stats.columns:
        sir_stats['year'] = year_label
    else:
        sir_stats = sir_stats.rename(columns={'order_time_year': 'year'})

    return sir_stats

overall_sir = get_sir_distribution(df_ast, [], 'All', 'All')
by_source_sir = get_sir_distribution(df_ast, ['source'], None, 'All')
by_year_sir = get_sir_distribution(df_ast, ['order_time_year'], 'All', None)
by_year_source_sir = get_sir_distribution(df_ast, ['order_time_year', 'source'], None, None)

final_sir_report = pd.concat([overall_sir, by_source_sir, by_year_sir, by_year_source_sir], ignore_index=True)

final_sir_report = final_sir_report.sort_values(
    ['source', 'year', 'organism_std', 'total_tested'],
    ascending=[True, True, True, False]
)

final_sir_report.to_csv('results/AMRD_SIR_distribution_report.csv', index=False)


