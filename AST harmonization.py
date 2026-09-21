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
