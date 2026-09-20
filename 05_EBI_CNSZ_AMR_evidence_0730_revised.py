import os
import pandas as pd
import os
from pathlib import Path
import hashlib
import pandas as pd
# 设置显示的最大列数，None 表示显示所有列
pd.set_option('display.max_columns', None)
# 设置每行显示的宽度，防止自动换行
pd.set_option('display.width', 1000)

os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ')
meta=pd.read_excel('2024-FQ-菌株编号（医院版）.xlsx')
card=pd.read_csv('/public8/lilab/student/htang/SMART/card/batch_outputs/txt/merge/combined_amr_results_strict_sampleID.csv')
card['BioSample_ID'].nunique()

meta = meta.rename(columns={'菌株编号': 'BioSample_ID'})
merged = pd.merge(
    meta,
    card,
    on="BioSample_ID",
    how="inner"
)
merged.to_csv('CNSZ_card_meta.csv')
merged.columns
subset = merged[['BioSample_ID', '住院号', '门诊号', '取样日期', '临床诊断', '标本类型']]
subset = subset.drop_duplicates(subset=['BioSample_ID'])
subset.to_csv('CNSZ_card_meta_subset.csv')

org=subset['BioSample_ID'].unique()
org = pd.DataFrame(subset['BioSample_ID'].unique(), columns=['BioSample_ID'])
merged2 = pd.merge(
    meta,
    org,
    on="BioSample_ID",
    how="inner"
)
merged2.to_csv('CNSZ_meta_select.csv')

meta2=pd.read_excel('CNSZ_meta_select.xlsx')
meta2 = meta2.rename(columns={'取样日期': 'order_time_jittered_std'})
meta2['order_time_jittered_std'].unique()
rt3 = pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/std/01_culture_cohort_std.csv')
rt3['organism_std'] = (
    rt3['organism_std']
    .replace({
        'Acinetobacter baumannii complex': 'Acinetobacter baumannii'
    })
)
rt3['organism_std'] = (
    rt3['organism_std']
    .replace({
        'Klebsiella pneumoniae subsp. pneumoniae': 'Klebsiella pneumoniae'
    })
)


rt3.columns
rt3['order_time_jittered_std'].unique()
#只需要日期
meta2['order_time_jittered'] = pd.to_datetime(
    meta2['order_time_jittered_std']
).dt.date


rt3['order_time_jittered'] = pd.to_datetime(
    rt3['order_time_jittered_std']
).dt.date
meta2.columns
print(rt3[['anon_id','order_proc_id_coded','organism_std']].dtypes)

print(meta2[['anon_id','order_proc_id_coded','organism_std']].dtypes)
merge_cols = [
    'anon_id',
    'order_proc_id_coded',
    'organism_std'
]

for col in merge_cols:
    rt3[col] = rt3[col].astype(str)
    meta2[col] = meta2[col].astype(str)


rt3_merged_df = pd.merge(
    rt3,
    meta2,
    on=['anon_id', 'order_proc_id_coded','organism_std'],
    how='inner'   # 只保留匹配上的
)

rt3_merged_df.to_csv('CNSZ_merge_sample_meta.csv')

rt3_merged_df.columns
check_cols = [
    'anon_id',
    'pat_enc_csn_id_coded',
    'order_proc_id_coded',
    'organism_std',
    'antibiotic_std',
    'susceptibility_std',
    'BioSample_ID'
]


rt3_clean = rt3_merged_df.dropna(
    subset=[
        'organism_std',
        'antibiotic_std',
        'susceptibility_std'
    ]
).reset_index(drop=True)

print("原始数据:", rt3_merged_df.shape)
print("清除空值后:", rt3_clean.shape)
rt3_clean[
    [
        'organism_std',
        'antibiotic_std',
        'susceptibility_std'
    ]
].isna().sum()


rt3_unique = rt3_clean.drop_duplicates(
    subset=[
        'anon_id',
        'pat_enc_csn_id_coded',
        'order_proc_id_coded',
        'organism_std',
        'antibiotic_std',
        'susceptibility_std',
        'BioSample_ID'
    ]
).reset_index(drop=True)

rt3_unique.to_csv('CNSZ_merge_sample_meta_clean.csv')
rt3_unique['BioSample_ID'].nunique()
rt3_unique = rt3_unique.rename(columns={'culture_description': 'isolation_source'})
###########################################
rt3_unique = rt3_unique.rename(columns={'order_time_jittered_std_x': 'order_time_jittered_std'})
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
df_ast_unique = rt3_unique[ast_meta_cols].drop_duplicates(
    subset=["BioSample_ID", 'order_proc_id_coded',"organism_std", "antibiotic_std", "susceptibility_std"]
)

# 3. 此时再与 card 进行关联
# 场景 A：如果只做样本级别的临床背景关联（保留 card 所有基因行）
card_merged_clinical = pd.merge(card, df_ast_unique, on="BioSample_ID", how="left")

print(f"去重后的药敏表型参考行数: {df_ast_unique.shape[0]}")
print(f"临床背景关联后的基因表行数: {card_merged_clinical.shape[0]}")
card_merged_clinical.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/CNSZ_SIR_gene_deidentification_0730.csv')
card_merged_clinical = card_merged_clinical.dropna(subset=[
    'organism_std',
    'antibiotic_std',
    'susceptibility_std'
])
card_merged_clinical.columns
card_merged_clinical.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/CNSZ_SIR_gene_deidentification_0730_clean.csv')

check = (
    card_merged_clinical
    .groupby('BioSample_ID')['organism_std']
    .nunique()
    .reset_index(name='organism_count')
)
multi_org = check[check['organism_count'] > 1]

print("多菌样本数:", len(multi_org))
multi_org.head()

######################################################
########################################CNSZ-EBI MERGE#############################################################
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ')
import pandas as pd
import numpy as np
# 设置显示的最大列数，None 表示显示所有列
pd.set_option('display.max_columns', None)
# 设置每行显示的宽度，防止自动换行
pd.set_option('display.width', 1000)

CNSZ_AMR=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/CNSZ_SIR_gene_deidentification_0730_clean.csv')
CNSZ_AMR['source']='CNSZ'
EBI_AMR = pd.read_csv('/public8/lilab/student/htang/SMART/EMBL/phenotype_genotype_merged_susceptibility_std.csv')
EBI_AMR['source']='EMBL-EBI-AMR'
EBI_AMR = EBI_AMR.dropna(subset=[
    'species',
    'resistance_phenotype',
    'antibiotic_name'
])
EBI_AMR['species'].unique()
EBI_AMR['resistance_phenotype'].unique()
EBI_AMR['antibiotic_name'].unique()
###################clean CNSZ_AMR['Best_Hit_ARO']
import re
import pandas as pd

def clean_amr_genes_keep_case(aro_series):
    """
    统一 CARD 数据库 Best_Hit_ARO 基因名称，同时保持原始习惯大小写
    """
    # 1. 复杂长文本到标准习惯大小写基因名的专家映射
    manual_mapping = {
        r".*soxR with mutation.*": "soxR",
        r".*soxS with mutation.*": "soxS",
        r".*AcrAB-TolC with AcrR mutation.*": "acrR",
        r".*AcrAB-TolC with MarR mutations.*": "marR",
        r".*PBP3 conferring resistance.*": "pbp3",
        r".*EF-Tu mutants.*": "tufA",  # 习惯用小写
        r".*nfsA mutations.*": "nfsA",
        r".*liaR mutant.*": "liaR",
        r".*liaS mutant.*": "liaS",
        r".*acrR with mutation.*": "acrR",
        r".*ramR mutants.*": "ramR",
        r".*gyrA with mutation.*": "gyrA",
        r".*GlpT with mutation.*": "glpT",
        r".*murA with mutation.*": "murA",
        r".*rpoB mutants.*": "rpoB",
        r".*ampR with mutation.*": "ampR",
        r"Type B NfxB": "nfxB",
        r"catII from Escherichia coli K-12": "catII"
    }

    cleaned_list = []

    for item in aro_series:
        if pd.isna(item):
            cleaned_list.append(item)
            continue

        original_item = item.strip()
        matched = False

        # 阶段一：匹配硬编码的复杂突变基因
        for pattern, replacement in manual_mapping.items():
            if re.match(pattern, original_item, re.IGNORECASE):
                cleaned_name = replacement
                matched = True
                break

        if not matched:
            cleaned_name = original_item

            # 阶段二：通用的层级正则过滤
            # (1) 移除物种前缀
            cleaned_name = re.sub(
                r'^(Escherichia coli|Klebsiella pneumoniae|Acinetobacter baumannii|Staphylococcus aureus|Pseudomonas aeruginosa|Salmonella enterica|Salmonella isangi|Shigella flexneri|Morganella morganii|Haemophilus influenzae|Enterococcus faecium)\s+',
                '', cleaned_name, flags=re.IGNORECASE)

            # (2) 清洗 van 基因簇的冗余文本 (如 "vanT gene in vanG cluster" -> "vanT")
            cleaned_name = re.sub(r'\s+gene\s+in\s+van[A-Z_a-z]+\s+cluster', '', cleaned_name, flags=re.IGNORECASE)

            # (3) 移除后缀形式的 "conferring resistance to..."
            cleaned_name = re.sub(r'\s+conferring\s+resistance.*$', '', cleaned_name, flags=re.IGNORECASE)

            # (4) 移除 beta-lactamase 等描述性词汇 (如 "ampC beta-lactamase" -> "ampC")
            cleaned_name = re.sub(r'\s+beta-lactamase.*$', '', cleaned_name, flags=re.IGNORECASE)

        # 阶段三：微调首字母大小写，使其符合三字小写习惯
        # 如果前三个字母是全大写，且后面紧跟一个小写字母（例如 ErmA -> ermA, ErmB -> ermB）
        if re.match(r'^[A-Z][a-z]{2}[A-Z]', cleaned_name):
            cleaned_name = cleaned_name[0].lower() + cleaned_name[1:]
        # 如果是全大写简短基因名（如 ACRF -> acrF, PC1 -> pc1），但排除 AAC/APH/OXA/TEM/SHV 等特异性抗性酶
        elif cleaned_name.isupper() and len(cleaned_name) <= 5:
            if not any(cleaned_name.startswith(x) for x in
                       ['AAC', 'APH', 'ANT', 'OXA', 'TEM', 'SHV', 'CTX', 'DHA', 'ADC', 'CMY']):
                cleaned_name = cleaned_name.lower()

        cleaned_list = [] if cleaned_list is None else cleaned_list
        cleaned_list.append(cleaned_name)

    return cleaned_list


# 1. 调用之前的清洗函数，将转换后的基因列表赋给新列
CNSZ_AMR['gene_symbol'] = clean_amr_genes_keep_case(CNSZ_AMR['Best_Hit_ARO'])

# 2. 检查新列是否成功生成
print(CNSZ_AMR[['Best_Hit_ARO', 'gene_symbol']].head())

CNSZ_AMR[ 'gene_symbol'].unique()

import re
def ultimate_clean_amr_genes(gene_array):
    refined_list = []

    # 进一步精细化特定映射
    extra_mapping = {
        r"uhpT with mutation": "uhpT",
        r"ptsI with mutation": "ptsI",
        r"cyaA with mutation": "cyaA",
        r"Mrx": "mrx",
        r"Erm\(42\)": "erm(42)",
        r"AAC\(6'\)-Ie-APH\(2''\)-Ia bifunctional protein": "AAC(6')-Ie-APH(2'')-Ia"
    }

    for gene in gene_array:
        if not isinstance(gene, str):
            refined_list.append(gene)
            continue

        # 1. 匹配特别顽固的文本
        matched = False
        for pattern, replacement in extra_mapping.items():
            if re.match(pattern, gene, re.IGNORECASE):
                refined_list.append(replacement)
                matched = True
                break
        if matched:
            continue

        # 2. 兜底清洗：如果仍有 "with mutation" 遗漏，直接强行切除
        gene = re.sub(r'\s+with\s+mutation.*$', '', gene, flags=re.IGNORECASE)

        refined_list.append(gene)

    return refined_list


# 直接清洗并覆盖你 DataFrame 中的那一列
CNSZ_AMR['gene_symbol'] = ultimate_clean_amr_genes(CNSZ_AMR['gene_symbol'])
# 打印最终完美版
print(CNSZ_AMR['gene_symbol'].unique())


EBI_AMR['gene_symbol'].unique()
#############################
import re
import pandas as pd
import numpy as np


def clean_ebi_amr_genes(gene_series):
    """
    统一并清洗 EBI 体系下的耐药基因名称，去除拷贝数后缀，规范括号格式
    """
    cleaned_list = []

    for gene in gene_series:
        if pd.isna(gene):
            cleaned_list.append(np.nan)
            continue

        # 转为字符串并去除两端空格
        name = str(gene).strip()

        # 1. 专门处理特殊的复合变体 (如 mecA-ceftar_1 -> mecA)
        if name.startswith('mecA-ceftar'):
            cleaned_list.append('mecA')
            continue

        # 2. 去除末尾的拷贝数/等位基因后缀 (如 _1, _2, _27)
        # 注意：使用正则捕获，防止把 mcr-1.1_1 中的 1.1 错杀
        name = re.sub(r'_\d+$', '', name)

        # 3. 规范化四环素类等带括号的基因 (如 tetM -> tet(M), tetO -> tet(O))
        # 捕获类似 tetM, tetO, tetK, tetL, tetS, msrD, msrE, msrA, msrC
        name = re.sub(r'^(tet|msr)([A-Z_a-z])$', lambda m: f"{m.group(1)}({m.group(2).upper()})", name)

        # 4. 去除一些特殊抗性基因尾部的单引号或残余描述 (如 ermC' -> ermC)
        name = name.rstrip("'")

        # 5. 特殊处理：将 dhfrI 规范化为通用的 dfrA 家族或保持其习惯名（通常 dhfrI 即 dfrA1）
        # 这里选择保持原基因名但去除后缀

        cleaned_list.append(name)

    return cleaned_list


# --- 直接应用到你的 DataFrame 中 ---
# 假设你的原始 DataFrame 变量名为 EBI_AMR
EBI_AMR['gene_symbol2'] = clean_ebi_amr_genes(EBI_AMR['gene_symbol'])

# 查看最终去重后的完美结果
print(EBI_AMR['gene_symbol2'].unique())

EBI_AMR['gene_symbol']=EBI_AMR['gene_symbol2']

print(EBI_AMR['species'].unique())
print(CNSZ_AMR['organism_std'].unique())

#############################species
import re
import pandas as pd
import numpy as np


def standardize_organism_names(org_series):
    """
    统一并标准化 CNSZ 和 EBI 的物种名称，收敛至标准双名法（种级）
    """
    standardized_list = []

    # 定义特定复合群和泛化群的清洗映射
    complex_mapping = {
        r'.*Acinetobacter baumannii.*complex.*': 'Acinetobacter baumannii',
        r'.*Enterobacter cloacae.*complex.*': 'Enterobacter cloacae',
        r'.*Bacillus cereus.*group.*': 'Bacillus cereus',
        r'Streptococcus mitis/oralis': 'Streptococcus mitis',  # 习惯性归类到主导种
        r'Aeromonas hydrophila/caviae': 'Aeromonas hydrophila'
    }

    for item in org_series:
        if pd.isna(item):
            standardized_list.append(np.nan)
            continue

        org = str(item).strip()

        # 1. 拦截并处理特定的复合群 (Complex / Group)
        matched = False
        for pattern, replacement in complex_mapping.items():
            if re.match(pattern, org, re.IGNORECASE):
                standardized_list.append(replacement)
                matched = True
                break
        if matched:
            continue

        # 2. 强行切除亚种后缀 (如 Klebsiella pneumoniae subsp. pneumoniae -> Klebsiella pneumoniae)
        if 'subsp.' in org:
            org = org.split('subsp.')[0].strip()

        # 3. 基于正规双名法提取 (保留前两个核心单词：属名 + 种名)
        # 这能有效清除类似 "Salmonella enterica strain XYZ" 或末尾的变体噪声
        words = org.split()
        if len(words) >= 2:
            # 如果第二个词是 'sp.' 或 'species' 或者是未明确的描述，则保留属名
            if words[1] in ['sp.', 'sp', 'species', 'group', 'complex'] or words[0] in ['Anaerobic']:
                org = words[0]
            else:
                org = f"{words[0]} {words[1]}"
        else:
            org = words[0]

        standardized_list.append(org)

    return standardized_list


# --- 推进清洗并生成统一列 ---
CNSZ_AMR['species_std'] = standardize_organism_names(CNSZ_AMR['organism_std'])
EBI_AMR['species_std'] = standardize_organism_names(EBI_AMR['species'])
print(EBI_AMR['species_std'].unique())
print(CNSZ_AMR['species_std'].unique())

#########################antibiotic_std
print(EBI_AMR['antibiotic_name'].unique())
print(CNSZ_AMR['antibiotic_std'].unique())
EBI_AMR['antibiotic_std']=EBI_AMR['antibiotic_name']
EBI_AMR['antibiotic_std'].unique()

########CNSZ_AMR
import pandas as pd
import numpy as np

import pandas as pd
import numpy as np

# 1️⃣ 统一 key（全部小写）
cnsz_atb_master_mapping = {
    k.lower(): v for k, v in {
        # Beta-lactams
        'ampicillin': ('Penicillin', 'Beta-lactams'),
        'penicillin': ('Penicillin', 'Beta-lactams'),
        'oxacillin': ('Penicillin', 'Beta-lactams'),

        'cefoperazone/sulbactam': ('Beta Lactam Combo', 'Beta-lactams'),
        'piperacillin/tazobactam': ('Beta Lactam Combo', 'Beta-lactams'),
        'amoxicillin/clavulanic acid': ('Beta Lactam Combo', 'Beta-lactams'),
        'ampicillin/sulbactam': ('Beta Lactam Combo', 'Beta-lactams'),
        'ceftazidime/avibactam': ('Beta Lactam Combo', 'Beta-lactams'),
        'ticarcillin/clavulanic acid': ('Beta Lactam Combo', 'Beta-lactams'),

        'meropenem': ('Carbapenem', 'Beta-lactams'),
        'imipenem': ('Carbapenem', 'Beta-lactams'),
        'ertapenem': ('Carbapenem', 'Beta-lactams'),

        'aztreonam': ('Monobactam', 'Beta-lactams'),

        'cefuroxime': ('Cephalosporin Gen2', 'Beta-lactams'),
        'cefoxitin': ('Cephalosporin Gen2', 'Beta-lactams'),
        'ceftriaxone': ('Cephalosporin Gen3', 'Beta-lactams'),
        'ceftazidime': ('Cephalosporin Gen3', 'Beta-lactams'),
        'cefotaxime': ('Cephalosporin Gen3', 'Beta-lactams'),
        'cefepime': ('Cephalosporin Gen4', 'Beta-lactams'),
        'ceftaroline': ('Cephalosporin Gen4', 'Beta-lactams'),

        # MLS
        'erythromycin': ('Macrolide', 'Macrolides/Lincosamides'),
        'clindamycin': ('Lincosamide', 'Macrolides/Lincosamides'),

        # Quinolones
        'levofloxacin': ('Fluoroquinolone', 'Quinolones'),
        'ciprofloxacin': ('Fluoroquinolone', 'Quinolones'),
        'moxifloxacin': ('Fluoroquinolone', 'Quinolones'),

        # Tetracyclines
        'tetracycline': ('Tetracycline', 'Tetracyclines'),
        'doxycycline': ('Tetracycline', 'Tetracyclines'),
        'minocycline': ('Tetracycline', 'Tetracyclines'),
        'tigecycline': ('Tetracycline', 'Tetracyclines'),

        # Aminoglycosides
        'gentamicin': ('Aminoglycoside', 'Aminoglycosides'),
        'amikacin': ('Aminoglycoside', 'Aminoglycosides'),
        'tobramycin': ('Aminoglycoside', 'Aminoglycosides'),
        'streptomycin': ('Aminoglycoside', 'Aminoglycosides'),

        # Glyco/Lipo
        'vancomycin': ('Glycopeptide', 'Glycopeptides/Lipopeptides'),
        'teicoplanin': ('Glycopeptide', 'Glycopeptides/Lipopeptides'),
        'daptomycin': ('Lipopeptide', 'Glycopeptides/Lipopeptides'),

        # Others
        'trimethoprim/sulfamethoxazole': ('Sulfonamide Combo', 'Folate Pathway Inhibitors'),

        'polymyxin b': ('Polymyxin', 'Polymyxins'),
        'colistin': ('Polymyxin', 'Polymyxins'),

        'chloramphenicol': ('Phenicol', 'Phenicols'),
        'nitrofurantoin': ('Nitrofuran', 'Nitrofurans'),
        'rifampin': ('Ansamycin', 'Ansamycins'),
        'linezolid': ('Oxazolidinone', 'Oxazolidinones'),
        'quinupristin/dalfopristin': ('Streptogramin', 'Streptogramins'),

        # Antifungals
        'voriconazole': ('Azole Antifungal', 'Antifungals'),
        'fluconazole': ('Azole Antifungal', 'Antifungals'),
        'itraconazole': ('Azole Antifungal', 'Antifungals'),
        'caspofungin': ('Echinocandin', 'Antifungals'),
        'micafungin': ('Echinocandin', 'Antifungals'),
        'amphotericin b': ('Polyene Antifungal', 'Antifungals'),
        'flucytosine': ('Pyrimidine Analog', 'Antifungals')
    }.items()
}

# 2️⃣ 标准化字段
CNSZ_AMR['antibiotic_std_clean'] = (
    CNSZ_AMR['antibiotic_std']
    .astype(str)
    .str.strip()
    .str.lower()
)

# 3️⃣ 映射
mapped = CNSZ_AMR['antibiotic_std_clean'].map(cnsz_atb_master_mapping)

# 4️⃣ 拆分成两列
CNSZ_AMR[['atb_subtype_std', 'atb_class_std']] = pd.DataFrame(
    mapped.tolist(),
    index=CNSZ_AMR.index
)

# 5️⃣ 处理未匹配
CNSZ_AMR['atb_subtype_std'] = CNSZ_AMR['atb_subtype_std'].fillna('Unknown')
CNSZ_AMR['atb_class_std'] = CNSZ_AMR['atb_class_std'].fillna('Unknown')

missing = CNSZ_AMR.loc[
    CNSZ_AMR['atb_class_std'] == 'Unknown',
    'antibiotic_std'
].unique()

print("❗未覆盖的抗生素：")
print(missing)


###############################EBI
import pandas as pd
import numpy as np

# 1️⃣ 统一 key（全部小写）
ebi_atb_master_mapping = {
    k.lower(): v for k, v in {
        # Aminoglycosides
        'spectinomycin': ('Aminocyclitol', 'Aminoglycosides'),
        'streptomycin': ('Aminoglycoside', 'Aminoglycosides'),
        'kanamycin': ('Aminoglycoside', 'Aminoglycosides'),
        'gentamicin': ('Aminoglycoside', 'Aminoglycosides'),
        'tobramycin': ('Aminoglycoside', 'Aminoglycosides'),
        'amikacin': ('Aminoglycoside', 'Aminoglycosides'),

        # Macrolides / Lincosamides
        'erythromycin': ('Macrolide', 'Macrolides/Lincosamides'),
        'azithromycin': ('Macrolide', 'Macrolides/Lincosamides'),
        'clindamycin': ('Lincosamide', 'Macrolides/Lincosamides'),

        # Tetracyclines
        'tetracycline': ('Tetracycline', 'Tetracyclines'),
        'tigecycline': ('Glycylcycline', 'Tetracyclines'),

        # Beta-lactams
        'ampicillin': ('Penicillin', 'Beta-lactams'),
        'aztreonam': ('Monobactam', 'Beta-lactams'),
        'methicillin': ('Penicillin', 'Beta-lactams'),
        'cefiderocol': ('Cephalosporin siderophore', 'Beta-lactams'),

        # Glycopeptides / Lipoglycopeptides
        'daptomycin': ('Lipopeptide', 'Glycopeptides/Lipopeptides'),

        # Polymyxins
        'colistin': ('Polymyxin', 'Polymyxins'),

        # Phenicols
        'chloramphenicol': ('Phenicol', 'Phenicols'),
        'florfenicol': ('Phenicol', 'Phenicols'),

        # Others
        'linezolid': ('Oxazolidinone', 'Oxazolidinones'),
        'rifampin': ('Ansamycin', 'Ansamycins'),

        # Folate pathway
        'trimethoprim': ('DHFR inhibitor', 'Folate Pathway Inhibitors'),

        # Cell wall
        'fosfomycin': ('Epoxide', 'Cell Wall Synthesis Inhibitors'),

        # Topical
        'mupirocin': ('Isoleucyl-tRNA synthetase inhibitor', 'Topical antibiotics'),
        'fusidic acid': ('Elongation factor inhibitor', 'Protein synthesis inhibitors'),

        # Nitrofurans
        'nitrofurantoin': ('Nitrofuran', 'Nitrofurans'),
    }.items()
}

# 2️⃣ 标准化字段
EBI_AMR['antibiotic_std_clean'] = (
    EBI_AMR['antibiotic_std']
    .astype(str)
    .str.strip()
    .str.lower()
)

# 3️⃣ 映射
mapped = EBI_AMR['antibiotic_std_clean'].map(ebi_atb_master_mapping)

# 4️⃣ 拆分成两列
EBI_AMR[['atb_subtype_std', 'atb_class_std']] = pd.DataFrame(
    mapped.tolist(),
    index=EBI_AMR.index
)

# 5️⃣ 处理未匹配
EBI_AMR['atb_subtype_std'] = EBI_AMR['atb_subtype_std'].fillna('Unknown')
EBI_AMR['atb_class_std'] = EBI_AMR['atb_class_std'].fillna('Unknown')

missing = EBI_AMR.loc[
    EBI_AMR['atb_class_std'] == 'Unknown',
    'antibiotic_std'
].unique()

print("❗未覆盖的抗生素：")
print(missing)

#######################
########################
print(EBI_AMR['susceptibility_std'].unique())
print(CNSZ_AMR['susceptibility_std'].unique())

EBI_AMR['source']='EMBL-EBI-AMR'
CNSZ_AMR['source']='CNSZ'
CNSZ_AMR['source']='CNSZ'
CNSZ_AMR['ast_standard']='CLSI'
CNSZ_AMR['country']='China'
CNSZ_AMR['geographical_region']='Asia'
CNSZ_AMR['geographical_subregion']='Eastern Asia'
EBI_AMR['geographical_region'].unique()
EBI_AMR['geographical_subregion'].unique()
EBI_AMR['class'].unique()


########################merge#############################
# 1. 定义需要保留的 10 个标准列
target_columns = [
    "BioSample_ID",
    "gene_symbol",
    "species_std",
    'antibiotic_std',
    "susceptibility_std",
    "ast_standard",
    "country",
    'geographical_region',
    "geographical_subregion",
    "atb_subtype_std",
    "atb_class_std",
    'source'
]

# 2. 提取 ARMD 数据（排在前面）
# 如果你想把 ARMD 的 source 列统一改成 "ARMD"，可以加上后面那句注释
df_armd_sub = EBI_AMR[target_columns].copy()
# df_armd_sub['source'] = 'ARMD'  # 如果需要强制统一来源名称，请取消本行注释

# 3. 提取 CNSZ 数据（排在后面）
df_cnsz_sub = CNSZ_AMR[target_columns].copy()

# 4. 纵向合并：ARMD 在前，CNSZ 在后
# ignore_index=True 可以确保重新生成从 0 到 1200+ 万的干净连续行索引
merged_df = pd.concat([df_armd_sub, df_cnsz_sub], ignore_index=True)

# 5. 验证结果
print(f"合并后的数据集形状 (Shape): {merged_df.shape}")
print("\n数据前 3 行 (应全为 ARMD 数据):")
print(merged_df.head(3))
print("\n数据后 3 行 (应全为 CNSZ 数据):")
print(merged_df.tail(3))


merged_df['gene_family'] = merged_df['gene_symbol'].str.extract(r'^([a-zA-Z]+)')
merged_df.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/0730/EBI_CNSZ_AMR2_deidentification.csv')
merged_df['source'].value_counts()

merged_df=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/0730/EBI_CNSZ_AMR2_deidentification.csv')

##########################################################
import pandas as pd
import numpy as np

# 1. 预处理 EBI 数据
# 只保留有明确耐药/敏感表型的数据
ebi_df=merged_df
# mapping = {
#     'susceptible': 'S',
#     'resistant': 'R',
#     'intermediate': 'I',
#     'susceptible-dose dependent': 'I',   # CLSI规则
# }
# ebi_df['susceptibility_std'] = ebi_df['resistance_phenotype'].map(mapping)
# ebi_df.to_csv('phenotype_genotype_merged_susceptibility_std.csv')
#ebi_clean = ebi_df.dropna(subset=['organism_std','susceptibility_std', 'gene_symbol', 'antimicrobial_std'])
ebi_clean = ebi_df.dropna(subset=['species_std','susceptibility_std', 'gene_symbol', 'antibiotic_std'])
ebi_clean['source'].value_counts()
# 统一大小写防止匹配失败
ebi_clean = ebi_clean.rename(columns={'species_std': 'organism_std'})
ebi_clean = ebi_clean.rename(columns={'antibiotic_std': 'antimicrobial_std'})
ebi_clean['organism_std'] = ebi_clean['organism_std'].str.lower()
ebi_clean['antimicrobial_std'] = ebi_clean['antimicrobial_std'].str.lower()
ebi_clean['susceptibility_std'].unique()
ebi_clean.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/EBI_CNSZ_AMR_deidentification_0730.csv')
ebi_clean=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/EBI_CNSZ_AMR_deidentification_0730.csv')

###################################################################################################################
import pandas as pd
import numpy as np

# ============================================================
# 1. 数据准备
# ============================================================

ebi_df = ebi_clean.copy()

required_cols = [
    "BioSample_ID",
    "organism_std",
    "antimicrobial_std",
    "susceptibility_std",
    "gene_symbol",
]

ebi_clean = ebi_df.dropna(subset=required_cols).copy()

ebi_clean["organism_std"] = (
    ebi_clean["organism_std"].astype(str).str.strip().str.lower()
)

ebi_clean["antimicrobial_std"] = (
    ebi_clean["antimicrobial_std"].astype(str).str.strip().str.lower()
)

ebi_clean["gene_symbol"] = (
    ebi_clean["gene_symbol"].astype(str).str.strip()
)

ebi_clean["susceptibility_std"] = (
    ebi_clean["susceptibility_std"].astype(str).str.strip().str.upper()
)

ebi_clean = ebi_clean[
    ebi_clean["susceptibility_std"].isin(["S", "I", "R"])
].copy()

ebi_clean["isolate_id"] = ebi_clean["BioSample_ID"].astype(str)

# ============================================================
# 2. 去重
# ============================================================

pheno_base = ebi_clean.drop_duplicates([
    "isolate_id",
    "organism_std",
    "antimicrobial_std",
    "susceptibility_std",
])

gene_base = ebi_clean.drop_duplicates([
    "isolate_id",
    "organism_std",
    "antimicrobial_std",
    "gene_symbol",
    "susceptibility_std",
])

# ============================================================
# 3. 分母（phenotype）
# ============================================================

pheno_denominators = (
    pheno_base
    .groupby([
        "organism_std",
        "antimicrobial_std",
        "susceptibility_std",
    ])
    .agg(total_isolates=("isolate_id", "nunique"))
    .reset_index()
)

den_wide = pheno_denominators.pivot_table(
    index=["organism_std", "antimicrobial_std"],
    columns="susceptibility_std",
    values="total_isolates",
    fill_value=0
).reset_index()

den_wide = den_wide.rename(columns={
    "S": "total_S",
    "I": "total_I",
    "R": "total_R",
})

for col in ["total_S", "total_I", "total_R"]:
    if col not in den_wide.columns:
        den_wide[col] = 0

# ============================================================
# 4. 分子（gene）
# ============================================================

gene_counts = (
    gene_base
    .groupby([
        "organism_std",
        "antimicrobial_std",
        "gene_symbol",
        "susceptibility_std",
    ])
    .agg(gene_isolates=("isolate_id", "nunique"))
    .reset_index()
)

gene_wide = gene_counts.pivot_table(
    index=["organism_std", "antimicrobial_std", "gene_symbol"],
    columns="susceptibility_std",
    values="gene_isolates",
    fill_value=0
).reset_index()

for col in ["S", "I", "R"]:
    if col not in gene_wide.columns:
        gene_wide[col] = 0

# ============================================================
# 5. 合并
# ============================================================

knowledge_summary = gene_wide.merge(
    den_wide,
    on=["organism_std", "antimicrobial_std"],
    how="left",
)

# ============================================================
# 6. 基础统计
# ============================================================

knowledge_summary["gene_total"] = (
    knowledge_summary["S"] +
    knowledge_summary["I"] +
    knowledge_summary["R"]
)

knowledge_summary["gene_non_s"] = (
    knowledge_summary["I"] + knowledge_summary["R"]
)
knowledge_summary["gene_S"] = (
    knowledge_summary["gene_total"] - knowledge_summary["gene_non_s"])

knowledge_summary["total_non_s"] = (
    knowledge_summary["total_I"] + knowledge_summary["total_R"])

knowledge_summary["total_all"] = (
    knowledge_summary["total_S"] +
    knowledge_summary["total_I"] +
    knowledge_summary["total_R"]
)

# ============================================================
# 7. log_odds（始终计算）
# ============================================================

epsilon = 0.5

odds_non_s = (
    (knowledge_summary["gene_non_s"] + epsilon)
    / (knowledge_summary["total_non_s"] - knowledge_summary["gene_non_s"] + epsilon)
)

odds_s = (
    (knowledge_summary["S"] + epsilon)
    / (knowledge_summary["total_S"] - knowledge_summary["S"] + epsilon)
)

knowledge_summary["log_odds_non_s_vs_s"] = np.log(
    odds_non_s / odds_s
)

# ============================================================
# 8. Confidence Weight（⭐核心优化）
# ============================================================

def compute_confidence_weight(n, total_s, total_ns, k=10):
    if pd.isna(n) or n <= 0:
        return 0.0

    # 样本量权重
    w_n = np.sqrt(n / (n + k))

    # 组平衡（弱化）
    min_group = np.minimum(total_s, total_ns)
    w_balance = np.sqrt(min_group / (min_group + k))

    # ⭐关键：只部分影响（避免压死信号）
    return w_n * (0.5 + 0.5 * w_balance)


knowledge_summary["confidence_weight"] = knowledge_summary.apply(
    lambda row: compute_confidence_weight(
        row["gene_total"],
        row["total_S"],
        row["total_non_s"]
    ),
    axis=1
)

# ============================================================
# 9. Final Score
# ============================================================

knowledge_summary["final_score"] = (
    knowledge_summary["log_odds_non_s_vs_s"] *
    knowledge_summary["confidence_weight"]
)

# ============================================================
# 10. Evidence Level
# ============================================================

def evidence_level(n):
    if n >= 20:
        return "high"
    elif n >= 10:
        return "moderate"
    elif n >= 3:
        return "low"
    else:
        return "very_low"

knowledge_summary["evidence_level"] = (
    knowledge_summary["gene_total"].apply(evidence_level)
)

knowledge_summary["evidence_level"].value_counts()
# ============================================================
# 11. Label（⭐阈值优化）
# ============================================================
# knowledge_summary2 = knowledge_summary[
#     (knowledge_summary["gene_total"] >= 3) &
#     (knowledge_summary["total_all"] >= 3)
# ]
knowledge_summary2 = knowledge_summary
q90 = knowledge_summary2["final_score"].quantile(0.9)
q75 = knowledge_summary2["final_score"].quantile(0.75)
q25 = knowledge_summary2["final_score"].quantile(0.25)
q10 = knowledge_summary2["final_score"].quantile(0.1)

def resistance_label(row):
    score = row["final_score"]
    n = row["gene_total"]

    if n < 3:
        return "insufficient"

    if score >= q90:
        return "strong_resistance"
    elif score >= q75:
        return "moderate_resistance"
    elif score <= q10:
        return "strong_susceptibility"
    elif score <= q25:
        return "moderate_susceptibility"
    else:
        return "weak_or_neutral"

knowledge_summary2["resistance_evidence_label"] = (
    knowledge_summary2.apply(resistance_label, axis=1)
)
knowledge_summary2["resistance_evidence_label"].value_counts()


knowledge_summary2["resistance_evidence_label"].value_counts()

# ============================================================
# 12. Label 映射
# ============================================================

label_cn_map = {
    "strong_resistance": "Strong evidence of resistance",
    "moderate_resistance": "Moderate evidence of resistance",
    "weak_or_neutral": "Weak or neutral",
    "moderate_susceptibility": "Moderate evidence of sensitive",
    "strong_susceptibility": "Strong evidence of sensitive",
    "insufficient": "Insufficient evidence",
}

knowledge_summary2["resistance_evidence_label_cn"] = (
    knowledge_summary2["resistance_evidence_label"].map(label_cn_map)
)

# ============================================================
# 13. 软筛选
# ============================================================
# knowledge_summary_valid = knowledge_summary2[
#     (knowledge_summary2["gene_total"] >= 5) &
#     (knowledge_summary2["gene_S"] >= 2) &
#     (knowledge_summary2["gene_non_s"] >= 2)
# ]
# knowledge_summary_valid['valid']='True'
# knowledge_summary2['valid'] = False
# knowledge_summary2.loc[knowledge_summary_valid.index, 'valid'] = True
# knowledge_summary_valid['antimicrobial_std'].nunique()
# ============================================================
# 14. 输出
# ============================================================

print("=== Evidence Summary ===")
print(knowledge_summary2["resistance_evidence_label"].value_counts())
# print("\n=== Valid Evidence Size ===")
# print(knowledge_summary_valid.shape)
knowledge_summary2.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/0730/ebi_knowledge_summary_0730.csv', index=False)
# knowledge_summary_valid.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/0726/ebi_knowledge_summary_valid_0730.csv', index=False)
knowledge_summary=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/0730/ebi_knowledge_summary_0730.csv')
ebi_clean.columns
ebi_clean = ebi_clean.drop(columns=['isolate_id'])

#############################################
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/0730')

cols = list(ebi_clean.columns)

if 'gene_family' in cols and 'gene_symbol' in cols:
    cols.remove('gene_family')
    cols.insert(cols.index('gene_symbol') + 1, 'gene_family')
    ebi_clean = ebi_clean[cols]
ebi_clean.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/0730/EBI_CNSZ_AMR_0730.csv', index=False)

####################################1. 总体证据质量统计
knowledge_summary=knowledge_summary2
valid_rate = len(knowledge_summary_valid) / len(knowledge_summary)

summary_overall = {
    "n_all_combinations": len(knowledge_summary),
    "n_valid_combinations": len(knowledge_summary_valid),
    "valid_rate": valid_rate,
    "n_species": knowledge_summary["organism_std"].nunique(),
    "n_antibiotics": knowledge_summary["antimicrobial_std"].nunique(),
    "n_genes": knowledge_summary["gene_symbol"].nunique(),
}

summary_overall
import pandas as pd
summary_df = pd.DataFrame([summary_overall])
summary_df.to_csv("01_overall_evidence_summary_deidentification.csv", index=False)
# summary_overall
# {'n_all_combinations': 94201, 'n_valid_combinations': 13504, 'valid_rate': 0.14335304296132736, 'n_species': 122, 'n_antibiotics': 61, 'n_genes': 375}

####################################evidence_level 分布图
evidence_level_stats = (
    knowledge_summary
    .groupby("evidence_level")
    .size()
    .reset_index(name="n")
)

evidence_level_stats["ratio"] = (
    evidence_level_stats["n"] / evidence_level_stats["n"].sum()
)

evidence_level_stats.to_csv('02_evidence_level_distribution_deidentification.csv')
# very_low: 75,304
# low: 12,556
# moderate: 4,740
# high: 1,601

##############################3. valid / invalid 原因分析
# 哪些组合无法计算 log odds？
# 是因为缺 S 对照，还是缺 Non-S 病例，还是基因阳性样本太少？
comparison_status_stats = (
    knowledge_summary
    .groupby("comparison_status")
    .size()
    .reset_index(name="n")
)

comparison_status_stats["ratio"] = (
    comparison_status_stats["n"] / comparison_status_stats["n"].sum()
)

comparison_status_stats.to_csv('03_comparison_status_distribution_deidentification.csv')

###############################4. 耐药/敏感证据标签分布
# 强耐药证据
# 中等耐药证据
# 弱耐药证据
# 中性或不确定
# 强敏感证据
label_stats_valid = (
    knowledge_summary_valid
    .groupby("resistance_evidence_label")
    .size()
    .reset_index(name="n")
)

label_stats_valid["ratio"] = (
    label_stats_valid["n"] / label_stats_valid["n"].sum()
)

label_stats_valid.to_csv('04_resistance_label_distribution_deidentification.csv')

# #############################5. 按物种统计证据覆盖
# 哪些菌种有最多外部证据？
# 哪些菌种的强耐药证据最多？
# 哪些菌种证据不足？
species_coverage = (
    knowledge_summary
    .groupby("organism_std")
    .agg(
        n_valid_pairs=("gene_symbol", "size"),
        n_antibiotics=("antimicrobial_std", "nunique"),
        n_genes=("gene_symbol", "nunique"),
        mean_final_score=("final_score", "mean"),
        max_final_score=("final_score", "max"),
        n_strong_resistance=(
            "resistance_evidence_label",
            lambda x: (x == "strong_resistance").sum()
        ),
        n_strong_susceptibility=(
            "resistance_evidence_label",
            lambda x: (x == "strong_susceptibility").sum()
        ),
    )
    .reset_index()
    .sort_values("n_valid_pairs", ascending=False)
)

species_coverage.head(30)
species_coverage.to_csv('05_species_coverage_deidentification.csv')

##############################6. 按抗生素统计证据覆盖
# 抗生素证据覆盖排行榜
# 高风险抗生素排行榜
antibiotic_coverage = (
    knowledge_summary_valid
    .groupby("antimicrobial_std")
    .agg(
        n_valid_pairs=("gene_symbol", "size"),
        n_species=("organism_std", "nunique"),
        n_genes=("gene_symbol", "nunique"),
        mean_final_score=("final_score", "mean"),
        max_final_score=("final_score", "max"),
        n_strong_resistance=(
            "resistance_evidence_label",
            lambda x: (x == "strong_resistance").sum()
        ),
    )
    .reset_index()
    .sort_values("n_valid_pairs", ascending=False)
)

antibiotic_coverage.head(30)

antibiotic_coverage.to_csv('06_antibiotic_coverage_deidentification.csv')

###############################7. Top 强耐药基因
# #高风险 gene-drug-species 证据榜
# top_resistance_genes = (
#     knowledge_summary_valid
#     .query("resistance_evidence_label == 'strong_resistance'")
#     .sort_values(["final_score", "evidence_n"], ascending=[False, False])
#     .head(50)
# )
#
# top_resistance_genes[
#     [
#         "organism_std",
#         "antimicrobial_std",
#         "gene_symbol",
#         "final_score",
#         "evidence_n",
#         "R_rate_among_gene_positive",
#         "Non_S_rate_among_gene_positive",
#         "gene_prevalence_in_Non_S",
#         "gene_prevalence_in_S",
#         "resistance_evidence_label_cn",
#     ]
# ]
# top_resistance_genes.to_csv('07_top_strong_resistance_genes_deidentification.csv')
############################################
# 0. 保证 evidence_n 存在
############################################
if "evidence_n" not in knowledge_summary_valid.columns:
    knowledge_summary_valid["evidence_n"] = (
        knowledge_summary_valid["S"] +
        knowledge_summary_valid["R"]
    )

############################################
# 1. Top 强耐药基因
############################################
top_resistance_genes = (
    knowledge_summary_valid
    .query("resistance_evidence_label == 'strong_resistance'")
    .dropna(subset=["final_score"])   # 防 NaN
    .sort_values(
        ["final_score", "evidence_n"],
        ascending=[False, False]
    )
    .head(50)
)

############################################
# 2. 展示字段（防止列不存在）
############################################
cols = [
    "organism_std",
    "antimicrobial_std",
    "gene_symbol",
    "final_score",
    "evidence_n",
    "R_rate_among_gene_positive",
    "Non_S_rate_among_gene_positive",
    "gene_prevalence_in_Non_S",
    "gene_prevalence_in_S",
    "resistance_evidence_label_cn",
]

# 只保留存在的列（避免再次 KeyError）
cols = [c for c in cols if c in top_resistance_genes.columns]

top_resistance_genes_display = top_resistance_genes[cols]

############################################
# 3. 输出
############################################
print(top_resistance_genes_display.head())

top_resistance_genes_display.to_csv(
    '07_top_strong_resistance_genes_deidentification.csv',
    index=False
)
###############################8. Top 强敏感/负相关基因
##genes negatively associated with non-susceptible phenotypes
top_susceptibility_genes = (
    knowledge_summary_valid
    .query("resistance_evidence_label == 'strong_susceptibility'")
    .sort_values(["final_score", "evidence_n"], ascending=[True, False])
    .head(50)
)
top_susceptibility_genes.to_csv('08_top_strong_susceptibility_genes_deidentification.csv')

######################9. 物种-抗生素热图
# species × antibiotic 的 max_final_score 热图
# species × antibiotic 的 strong_resistance gene count 热图
species_antibiotic_summary = (
    knowledge_summary_valid
    .groupby(["organism_std", "antimicrobial_std"])
    .agg(
        n_genes=("gene_symbol", "nunique"),
        max_final_score=("final_score", "max"),
        mean_final_score=("final_score", "mean"),
        n_strong_resistance=(
            "resistance_evidence_label",
            lambda x: (x == "strong_resistance").sum()
        ),
        n_moderate_resistance=(
            "resistance_evidence_label",
            lambda x: (x == "moderate_resistance").sum()
        ),
        n_strong_susceptibility=(
            "resistance_evidence_label",
            lambda x: (x == "strong_susceptibility").sum()
        ),
    )
    .reset_index()
)

species_antibiotic_summary.head()
species_antibiotic_summary.to_csv('09_species_antibiotic_summary_deidentification.csv')

#######################10. gene-antibiotic 网络分析
network_edges = knowledge_summary_valid[
    knowledge_summary_valid["resistance_evidence_label"].isin([
        "strong_resistance",
        "moderate_resistance"
    ])
][
    [
        "gene_symbol",
        "antimicrobial_std",
        "organism_std",
        "final_score",
        "evidence_n",
        "resistance_evidence_label",
    ]
].copy()

network_edges.to_csv('10_network_edges_gene_antibiotic_deidentification.csv')

# 可以用于 Cytoscape / Gephi / NetworkX：
#
# gene -> antibiotic
# gene -> species
# species -> antibiotic

#######################re耐药相关基因
df=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/EBI_CNSZ_knowledge_summary_valid_deidentification.csv')
df=knowledge_summary_valid
# 1. 计算 prevalence（如果不存在）
############################################
if "gene_prevalence_in_R" not in df.columns:
    df["gene_prevalence_in_R"] = df["R"] / df["total_R"]

if "gene_prevalence_in_S" not in df.columns:
    df["gene_prevalence_in_S"] = df["S"] / df["total_S"]

############################################
# 2. 防止除0
############################################
df["gene_prevalence_in_R"] = df["gene_prevalence_in_R"].fillna(0)
df["gene_prevalence_in_S"] = df["gene_prevalence_in_S"].fillna(0)
df_filtered = df[
    (df["resistance_evidence_label"] == "strong_resistance") &
    (df["gene_prevalence_in_R"] > 0.1) &   # 在耐药中常见
    (df["gene_prevalence_in_S"] < 0.5)     # 在敏感中不常见
]
gene_counts = (
    df_filtered["gene_symbol"]
    .value_counts()
    #.head(50)
)
gene_counts.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/strong_resistance_gene_counts.csv')
top20 = gene_counts.head(20)
import matplotlib.pyplot as plt

plt.figure(figsize=(10,6))

top20.plot(kind='bar')

plt.title('Top 20 Strong Resistance Genes')
plt.xlabel('Gene')
plt.ylabel('Count')

plt.xticks(rotation=45, ha='right')

plt.tight_layout()

plt.savefig('top20_resistance_genes.png', dpi=300)
plt.savefig('top20_resistance_genes.pdf', dpi=300)
plt.show()
