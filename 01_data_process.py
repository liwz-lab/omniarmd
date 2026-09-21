import os
import pandas as pd


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_cohort.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/00_microbiology_cultures_cohort.csv')
UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_cohort.csv')

print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())


Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'


print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())


Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
print(Stanford1.columns.tolist())

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/01_combined_culture_cohort.csv', index=False)

#######02microbiology_cultures_adi_scores
import os
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_adi_scores.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/01_microbiology_cultures_adi_scores.csv')
#UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_adi_scores.csv')
# 查看前几行
print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# 确认列名
print(Stanford1.columns.tolist())

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/02_combined_microbiology_cultures_adi_scores.csv', index=False)
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/01_combined_culture_cohort.csv')
MGB1= pd.read_csv('./ARMD-MGB/microbiology_cohort_deid_tj_updated.csv')
MGB1['source'] = 'MGB'








print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())
# 统一列名
MGB1 = MGB1.rename(columns={'order_time_jittered_utc_shifted': 'order_time_jittered'})
MGB1 = MGB1.rename(columns={'order_time_jittered_utc_shifted': 'order_time_jittered'})
# 确认列名
print(MGB1.columns.tolist())

combined_df2 = pd.concat([combined_df, MGB1], ignore_index=True)
# 检查结果
print(combined_df2.head())
print(combined_df2['source'].value_counts())
combined_df2.to_csv('./merge2/01_combined_culture_cohort2.csv', index=False)

#######03microbiology_cultures_antibiotic_class_exposure
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_antibiotic_class_exposure.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/02_microbiology_cultures_antibiotic_class_exposure.csv')
UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_antibiotic_class_exposure.csv')
# 查看前几行
print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# 确认列名
print(Stanford1.columns.tolist())

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/03_combined_microbiology_cultures_antibiotic_class_exposure.csv', index=False)


###4microbiology_cultures_antibiotic_class_exposure.csv
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_antibiotic_subtype_exposure.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/03_microbiology_cultures_antibiotic_subtype_exposure.csv')
UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_antibiotic_subtype_exposure.csv')
# 查看前几行
print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# 确认列名
print(Stanford1.columns.tolist())

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/04_combined_microbiology_cultures_antibiotic_subtype_exposure.csv', index=False)

#########5microbiology_cultures_comorbidity
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_comorbidity.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/04_microbiology_cultures_comorbidity.csv')
UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_comorbidity.csv')
# 查看前几行
print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# 确认列名
print(Stanford1.columns.tolist())

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/05_combined_microbiology_cultures_comorbidity.csv', index=False)

#########6microbiology_cultures_demographics
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_demographics.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/05_microbiology_cultures_demographics.csv')
UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_demographics.csv')
# 查看前几行
print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# 确认列名
print(Stanford1.columns.tolist())

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/06_combined_microbiology_cultures_demographics.csv', index=False)

#########7microbiology_cultures_labs
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_labs.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/06_microbiology_cultures_labs.csv')
UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_labs.csv')
# 查看前几行
print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# 确认列名
print(Stanford1.columns.tolist())

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/07_combined_microbiology_cultures_labs.csv', index=False)


###########8microbiology_cultures_microbial_resistance
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_microbial_resistance.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/07_microbiology_cultures_microbial_resistance.csv')
UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_microbial_resistance.csv')
# 查看前几行
print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# 确认列名
print(Stanford1.columns.tolist())

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/08_combined_microbiology_cultures_microbial_resistance.csv', index=False)


##############9microbiology_cultures_nursing_home_visits
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_nursing_home_visits.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/08_microbiology_cultures_nursing_home_visits.csv')
UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_nursing_home_visits.csv')
# 查看前几行
print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# 确认列名
print(Stanford1.columns.tolist())

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/09_combined_microbiology_cultures_nursing_home_visits.csv', index=False)

##############10_microbiology_cultures_prior_med
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_prior_med.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/010_microbiology_cultures_prior_med.csv')
UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_prior_med.csv')
# 查看前几行
print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# 确认列名
print(Stanford1.columns.tolist())

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/10_combined_microbiology_cultures_prior_med.csv', index=False)


##############11microbiology_cultures_prior_procedures
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_priorprocedures.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/011_microbiology_cultures_prior_procedures.csv')
UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_prior_procedures.csv')
# 查看前几行
print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# 确认列名
print(Stanford1.columns.tolist())

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/11_combined_microbiology_cultures_prior_procedures.csv', index=False)


########12microbiology_cultures_ward_info
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_ward_info.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/012_microbiology_cultures_ward_info.csv')
UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_ward_info.csv')
# 查看前几行
print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# 确认列名
print(Stanford1.columns.tolist())

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/12_combined_microbiology_cultures_ward_info.csv', index=False)

#####13microbiology_cultures_vitals
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_vitals.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/013_microbiology_cultures_vitals.csv')
#UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_vitals.csv')
# 查看前几行
print(Stanford1.head())
print(ECUH1.head())
#print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
#UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
#print("UTSW columns:\n", UTSW1.columns.tolist())

# # 统一时间列名
# Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# # 确认列名
# print(Stanford1.columns.tolist())

#combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df = pd.concat([Stanford1, ECUH1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/13_combined_microbiology_cultures_vitals.csv', index=False)


##############14microbiology_cultures_prior_infecting_organism
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_prior_infecting_organism.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/09_microbiology_cultures_prior_infecting_organism.csv')
UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_prior_infecting_organism.csv')
# 查看前几行
#print(Stanford1.head())
print(ECUH1.head())
print(UTSW1.head())

# 添加来源列
#Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
#print("Stanford columns:\n", Stanford1.columns.tolist())
print("ECUH columns:\n", ECUH1.columns.tolist())
print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
# Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# # 确认列名
# print(Stanford1.columns.tolist())

#combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df = pd.concat([ECUH1, UTSW1], ignore_index=True)
# 检查结果
print(combined_df.head())
print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/14_combined_microbiology_cultures_prior_infecting_organism.csv', index=False)


######15microbiology_cultures_implied_susceptibility.csv
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_implied_susceptibility.csv')
# ECUH1 = pd.read_csv('./ARMD-ECUH/09_microbiology_cultures_prior_infecting_organism.csv')
# UTSW1= pd.read_csv('./ARMD-UTSW/microbiology_cultures_prior_infecting_organism.csv')
# 查看前几行
print(Stanford1.head())
# print(ECUH1.head())
# print(UTSW1.head())

# 添加来源列
Stanford1['source'] = 'Stanford'
# ECUH1['source'] = 'ECUH'
# UTSW1['source'] = 'UTSW'

# 打印每个数据集的列名
print("Stanford columns:\n", Stanford1.columns.tolist())
# print("ECUH columns:\n", ECUH1.columns.tolist())
# print("UTSW columns:\n", UTSW1.columns.tolist())

# 统一时间列名
# Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
# # 确认列名
# print(Stanford1.columns.tolist())

#combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
# combined_df = pd.concat([ECUH1, UTSW1], ignore_index=True)
# 检查结果
# print(combined_df.head())
# print(combined_df['source'].value_counts())
combined_df.to_csv('./merge/15_Stanford_microbiology_cultures_implied_susceptibility.csv', index=False)
Stanford1.to_csv('./merge/15_Stanford_microbiology_cultures_implied_susceptibility.csv', index=False)


#############+MGB######################################
#########################01_combined_culture_cohort
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/01_combined_culture_cohort.csv')
MGB1= pd.read_csv('./ARMD-MGB/microbiology_cohort_deid_tj_updated.csv')
MGB1['source'] = 'MGB'
MGB1['susceptibility'] = MGB1['CLSI_2022_pheno']
print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())
combined_df['susceptibility'].unique().tolist()
MGB1['CLSI_2022_pheno'].unique().tolist()
MGB1['AST_pheno'].unique().tolist()

# 统一列名
import pandas as pd
import numpy as np
# 统一列名
MGB1_renamed = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered'
})

# 假设 MGB1_renamed 是 MGB 表，combined_df 是 Stanford 表
# 1️ MGB 有而 combined_df 没有的列 -> 补 NaN 到 combined_df
mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA
# 2️ combined_df 有而 MGB 没有的列 -> 补 NaN 到 MGB
combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

# 3️ 按 combined_df 的列顺序排列
final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns]
MGB1_renamed = MGB1_renamed[final_columns]

# 4重置索引
combined_df = combined_df.reset_index(drop=True)
MGB1_renamed = MGB1_renamed.reset_index(drop=True)

# 5️合并
final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)
final_df['susceptibility'].unique().tolist()
final_df['susceptibility'] = final_df['susceptibility'].replace({
    'Susceptible dose dependent': 'Susceptible dose-dependent',
    'Susceptible dose-dependent': 'Susceptible dose-dependent'
})

# 检查是否合并成功
print(final_df['susceptibility'].unique().tolist())
final_df.to_csv('./merge2/01_combined_culture_cohort2.csv', index=False)


#############2ADI
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/02_combined_microbiology_cultures_adi_scores.csv')
MGB1= pd.read_csv('./ARMD-MGB/ADI_deid_tj.csv')
MGB1['source'] = 'MGB'
print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())
# 统一时间列名
MGB1 = MGB1.rename(columns={'order_time_jittered_utc_shifted': 'order_time_jittered'})
# 确认列名
print(MGB1.columns.tolist())

final_df = pd.concat([combined_df, MGB1], ignore_index=True)
# 检查结果
print(final_df.head())
print(final_df['source'].value_counts())
final_df.to_csv('./merge2/02_combined_microbiology_cultures_adi_scores2.csv', index=False)

################03_combined_microbiology_cultures_antibiotic_class_exposure
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/03_combined_microbiology_cultures_antibiotic_class_exposure.csv')
MGB1= pd.read_csv('./ARMD-MGB/prior_abx_deid_tj.csv')
MGB1['source'] = 'MGB'
print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())

# 统一 MGB 列名
# 统一列名
MGB1_renamed = MGB1.rename(columns={
    'drug_class': 'antibiotic_class',  # MGB中的 drug_class -> antibiotic_class
    'last_dose_to_culture': 'time_to_culturetime',  # MGB中的 last_dose_to_culture -> time_to_culturetime
    'order_time_jittered_utc_shifted': 'order_time_jittered'  # MGB中的 order_time_jittered_utc_shifted -> order_time_jittered
})

# 处理 combined_df 的缺失列，补 NaN
extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in extra_cols:
    if c not in combined_df.columns:
        combined_df[c] = pd.NA

# 处理 MGB1_renamed 的缺失列，补 NaN
for c in combined_df.columns:
    if c not in MGB1_renamed.columns:
        MGB1_renamed[c] = pd.NA

# 保持列顺序一致，确保最终的列顺序与 combined_df 相同
MGB1_renamed = MGB1_renamed[combined_df.columns.tolist() + extra_cols]

# 重置索引，确保索引唯一
combined_df = combined_df.reset_index(drop=True)
MGB1_renamed = MGB1_renamed.reset_index(drop=True)

# 合并两个数据集
final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)

# 查看结果
print(final_df.head())
print(final_df.columns.tolist())
# 检查结果
print(final_df.head())
print(final_df['source'].value_counts())
final_df.to_csv('./merge2/03_combined_microbiology_cultures_antibiotic_class_exposure2.csv', index=False)

##########04_combined_microbiology_cultures_antibiotic_subtype_exposure
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/04_combined_microbiology_cultures_antibiotic_subtype_exposure.csv')
MGB1= pd.read_csv('./ARMD-MGB/prior_abx_deid_tj.csv.csv')
MGB1['source'] = 'MGB'
print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())

# 统一列名
MGB1_renamed = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered'
})


# 统一列名
MGB1_renamed = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered',
    'prior_org': 'prior_organism',
    'prior_org_days_to_culture': 'prior_infecting_organism_days_to_culture'
})

# 假设 MGB1_renamed 是 MGB 表，combined_df 是 Stanford 表
# 1️ MGB 有而 combined_df 没有的列 -> 补 NaN 到 combined_df
mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA
# 2️ combined_df 有而 MGB 没有的列 -> 补 NaN 到 MGB
combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

# 3️ 按 combined_df 的列顺序排列
final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns]
MGB1_renamed = MGB1_renamed[final_columns]

# 4重置索引
combined_df = combined_df.reset_index(drop=True)
MGB1_renamed = MGB1_renamed.reset_index(drop=True)

# 5️合并
final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)

final_df.to_csv('./merge2/14_combined_microbiology_cultures_prior_infecting_organism2.csv', index=False)




# 假设 MGB1_renamed 是 MGB 表，combined_df 是 Stanford 表
# 1️ MGB 有而 combined_df 没有的列 -> 补 NaN 到 combined_df
mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA
# 2️ combined_df 有而 MGB 没有的列 -> 补 NaN 到 MGB
combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

# 3️ 按 combined_df 的列顺序排列
final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns]
MGB1_renamed = MGB1_renamed[final_columns]

# 4重置索引
combined_df = combined_df.reset_index(drop=True)
MGB1_renamed = MGB1_renamed.reset_index(drop=True)

# 5️合并
final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)

final_df.to_csv('./merge2/04_combined_microbiology_cultures_antibiotic_subtype_exposure2.csv', index=False)

##########05_combined_microbiology_cultures_comorbidity
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/05_combined_microbiology_cultures_comorbidity.csv')
MGB1= pd.read_csv('./ARMD-MGB/comorbidity_deid_tj.csv')
MGB1['source'] = 'MGB'
print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())

MGB1 = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered',
    'category': 'comorbidity_component'
})

# 构造时间窗口（统一）
MGB1['comorbidity_component_start_days_culture'] = pd.NA
MGB1['comorbidity_component_end_days_culture'] = pd.NA

# 按 combined_df 列顺序
MGB1 = MGB1[combined_df.columns]

final_df = pd.concat([combined_df, MGB1], ignore_index=True)
final_df.to_csv('./merge2/05_combined_microbiology_cultures_comorbidity2.csv', index=False)

############06_combined_microbiology_cultures_demographics.csv
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/06_combined_microbiology_cultures_demographics.csv')
MGB1= pd.read_csv('./ARMD-MGB/demographics_deid_tj.csv')
MGB1['source'] = 'MGB'
print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())
# 按 combined_df 列顺序
MGB1 = MGB1[combined_df.columns]

final_df = pd.concat([combined_df, MGB1], ignore_index=True)
final_df.to_csv('./merge2/06_combined_microbiology_cultures_demographics2.csv', index=False)

############07_combined_microbiology_cultures_labs.csv


###############08_combined_microbiology_cultures_microbial_resistance.csv    ????
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/08_combined_microbiology_cultures_microbial_resistance.csv')
MGB1= pd.read_csv('./ARMD-MGB/microbiology_cohort_deid_tj_updated.csv')
MGB1['source'] = 'MGB'
print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())

# 统一列名
MGB1_renamed = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered'  # MGB中的 order_time_jittered_utc_shifted -> order_time_jittered
})

# 假设 MGB1_renamed 是 MGB 表，combined_df 是 Stanford 表
# 1️ MGB 有而 combined_df 没有的列 -> 补 NaN 到 combined_df
mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA
# 2️ combined_df 有而 MGB 没有的列 -> 补 NaN 到 MGB
combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

# 3️ 按 combined_df 的列顺序排列
final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns]
MGB1_renamed = MGB1_renamed[final_columns]

# 4重置索引
combined_df = combined_df.reset_index(drop=True)
MGB1_renamed = MGB1_renamed.reset_index(drop=True)

# 5️合并
final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)

final_df.to_csv('./merge2/08_combined_microbiology_cultures_microbial_resistance2.csv', index=False)

#############09_combined_microbiology_cultures_nursing_home_visits
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/09_combined_microbiology_cultures_nursing_home_visits.csv')
MGB1= pd.read_csv('./ARMD-MGB/nursing_home_visits_deid_tj.csv')
MGB1['source'] = 'MGB'
print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())

# 统一列名
MGB1_renamed = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered'  # MGB中的 order_time_jittered_utc_shifted -> order_time_jittered
})

# 假设 MGB1_renamed 是 MGB 表，combined_df 是 Stanford 表
# 1️ MGB 有而 combined_df 没有的列 -> 补 NaN 到 combined_df
mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA
# 2️ combined_df 有而 MGB 没有的列 -> 补 NaN 到 MGB
combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

# 3️ 按 combined_df 的列顺序排列
final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns]
MGB1_renamed = MGB1_renamed[final_columns]

# 4重置索引
combined_df = combined_df.reset_index(drop=True)
MGB1_renamed = MGB1_renamed.reset_index(drop=True)

# 5️合并
final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)

final_df.to_csv('./merge2/09_combined_microbiology_cultures_nursing_home_visits2.csv', index=False)

###########10_combined_microbiology_cultures_prior_med.csv
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/10_combined_microbiology_cultures_prior_med.csv')
MGB1= pd.read_csv('./ARMD-MGB/prior_org_deid_tj.csv')
MGB1['source'] = 'MGB'
print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())

# 统一列名
MGB1_renamed = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered'  # MGB中的 order_time_jittered_utc_shifted -> order_time_jittered
})

# 假设 MGB1_renamed 是 MGB 表，combined_df 是 Stanford 表
# 1️ MGB 有而 combined_df 没有的列 -> 补 NaN 到 combined_df
mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA
# 2️ combined_df 有而 MGB 没有的列 -> 补 NaN 到 MGB
combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

# 3️ 按 combined_df 的列顺序排列
final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns]
MGB1_renamed = MGB1_renamed[final_columns]

# 4重置索引
combined_df = combined_df.reset_index(drop=True)
MGB1_renamed = MGB1_renamed.reset_index(drop=True)

# 5️合并
final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)

final_df.to_csv('./merge2/10_combined_microbiology_cultures_prior_med2.csv', index=False)

###############11_combined_microbiology_cultures_prior_procedures
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/11_combined_microbiology_cultures_prior_procedures.csv')
MGB1= pd.read_csv('./ARMD-MGB/prior_procedures_deid_tj.csv')
MGB1['source'] = 'MGB'
print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())

# 统一列名
MGB1_renamed = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered'  # MGB中的 order_time_jittered_utc_shifted -> order_time_jittered
})

# 假设 MGB1_renamed 是 MGB 表，combined_df 是 Stanford 表
# 1️ MGB 有而 combined_df 没有的列 -> 补 NaN 到 combined_df
mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA
# 2️ combined_df 有而 MGB 没有的列 -> 补 NaN 到 MGB
combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

# 3️ 按 combined_df 的列顺序排列
final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns]
MGB1_renamed = MGB1_renamed[final_columns]

# 4重置索引
combined_df = combined_df.reset_index(drop=True)
MGB1_renamed = MGB1_renamed.reset_index(drop=True)

# 5️合并
final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)

final_df.to_csv('./merge2/11_combined_microbiology_cultures_prior_procedures2.csv', index=False)

###########12_combined_microbiology_cultures_ward_info.csv
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/12_combined_microbiology_cultures_ward_info.csv')
MGB1= pd.read_csv('./ARMD-MGB/ward_type_deid_tj.csv')
MGB1['source'] = 'MGB'
print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())

# 统一列名
MGB1_renamed = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered'  # MGB中的 order_time_jittered_utc_shifted -> order_time_jittered
})

# 假设 MGB1_renamed 是 MGB 表，combined_df 是 Stanford 表
# 1️ MGB 有而 combined_df 没有的列 -> 补 NaN 到 combined_df
mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA
# 2️ combined_df 有而 MGB 没有的列 -> 补 NaN 到 MGB
combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

# 3️ 按 combined_df 的列顺序排列
final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns]
MGB1_renamed = MGB1_renamed[final_columns]

# 4重置索引
combined_df = combined_df.reset_index(drop=True)
MGB1_renamed = MGB1_renamed.reset_index(drop=True)

# 5️合并
final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)

final_df.to_csv('./merge2/12_combined_microbiology_cultures_ward_info2.csv', index=False)


###########13_combined_microbiology_cultures_vitals.csv


##########14_combined_microbiology_cultures_prior_infecting_organism.csv
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD')
import pandas as pd
#MGB 以 Stanford 为主 schema，对齐同名字段 + 保留 MGB 扩展信息 + 缺失补 NaN
combined_df = pd.read_csv('./merge/14_combined_microbiology_cultures_prior_infecting_organism.csv')
MGB1= pd.read_csv('./ARMD-MGB/ward_type_deid_tj.csv')
MGB1['source'] = 'MGB'
print(combined_df.head())
print(MGB1.head())
print("MGB columns:\n", MGB1.columns.tolist())
print("combined_df columns:\n", combined_df.columns.tolist())

# 统一列名
MGB1_renamed = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered',
    'prior_org': 'prior_organism',
    'prior_org_days_to_culture': 'prior_infecting_organism_days_to_culture'
})

# 假设 MGB1_renamed 是 MGB 表，combined_df 是 Stanford 表
# 1️ MGB 有而 combined_df 没有的列 -> 补 NaN 到 combined_df
mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA
# 2️ combined_df 有而 MGB 没有的列 -> 补 NaN 到 MGB
combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

# 3️ 按 combined_df 的列顺序排列
final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns]
MGB1_renamed = MGB1_renamed[final_columns]

# 4重置索引
combined_df = combined_df.reset_index(drop=True)
MGB1_renamed = MGB1_renamed.reset_index(drop=True)

# 5️合并
final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)

final_df.to_csv('./merge2/14_combined_microbiology_cultures_prior_infecting_organism2.csv', index=False)

