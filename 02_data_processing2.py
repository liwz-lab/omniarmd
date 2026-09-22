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
CNSZ = CNSZ.rename(columns={'住院号': 'anon_id'})
CNSZ = CNSZ.rename(columns={'就诊流水号': 'pat_enc_csn_id_coded'})
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

####################
df = ARMD.copy()

df['medication_name_clean'] = (
    df['medication_name']
    .str.lower()
    .str.strip()
    .str.replace('-', '/', regex=False)
    .str.replace(r'\s+', ' ', regex=True)
)
import pandas as pd

# Raw → Standard mapping
alias_map = {
    # =========================
    # β-lactams / penicillins
    # =========================
    'amoxicillin/clavulanate': 'amoxicillin/clavulanic acid',
    'amoxicillin pot clavulanate': 'amoxicillin/clavulanic acid',
    'augmentin': 'amoxicillin/clavulanic acid',

    'amoxicillin': 'amoxicillin',

    'ampicillin/sulbactam': 'ampicillin/sulbactam',
    'ampicillin sodium': 'ampicillin',
    'ampicillin': 'ampicillin',

    'piperacillin/tazobactam': 'piperacillin/tazobactam',
    'piperacillin tazobactam dextrs': 'piperacillin/tazobactam',
    'piperacillin tazobactam': 'piperacillin/tazobactam',
    'piperacillin': 'piperacillin',

    'ticarcillin': 'ticarcillin',
    'ticarcillin/clavulanic acid': 'ticarcillin/clavulanic acid',

    'dicloxacillin': 'dicloxacillin',
    'nafcillin': 'nafcillin',
    'oxacillin': 'oxacillin',
    'penicillin': 'penicillin',


    # =========================
    # Cephalosporins
    # =========================
    'cefadroxil': 'cefadroxil',
    'cefazolin': 'cefazolin',
    'cefazolin in dextrose': 'cefazolin',

    'cephalexin': 'cephalexin',
    'cephalexin/cephalothin': 'cephalexin',
    'cephalothin': 'cephalothin',

    'cefuroxime': 'cefuroxime',
    'cefuroxime axetil': 'cefuroxime',

    'ceftriaxone': 'ceftriaxone',
    'cefotaxime': 'cefotaxime',
    'cefotetan': 'cefotetan',

    'cefdinir': 'cefdinir',
    'cefpodoxime': 'cefpodoxime',
    'cefixime': 'cefixime',

    'cefoxitin': 'cefoxitin',
    'cefepime': 'cefepime',
    'cefepime in': 'cefepime',

    'ceftazidime': 'ceftazidime',
    'ceftazidime-dextrose': 'ceftazidime',
    'ceftazidime/avibactam': 'ceftazidime/avibactam',

    'ceftolozane/tazobactam': 'ceftolozane/tazobactam',

    'ceftaroline': 'ceftaroline',
    'cefiderocol': 'cefiderocol',


    # =========================
    # Carbapenems
    # =========================
    'ertapenem': 'ertapenem',
    'meropenem': 'meropenem',
    'meropenem-vaborbactam': 'meropenem/vaborbactam',

    'imipenem': 'imipenem',
    'imipenem-relebactam': 'imipenem/relebactam',

    'doripenem': 'doripenem',


    # =========================
    # Monobactams
    # =========================
    'aztreonam': 'aztreonam',
    'aztreonam in': 'aztreonam',
    'aztreonam/avibactam': 'aztreonam/avibactam',


    # =========================
    # Aminoglycosides
    # =========================
    'gentamicin': 'gentamicin',
    'gentamicin in nacl': 'gentamicin',
    'gentamicin/sodium citrate': 'gentamicin',

    'amikacin': 'amikacin',
    'tobramycin': 'tobramycin',
    'tobramycin sulfate': 'tobramycin',
    'tobramycin/dexamethasone': 'tobramycin',

    'streptomycin': 'streptomycin',
    'kanamycin': 'kanamycin',
    'plazomicin': 'plazomicin',


    # =========================
    # Fluoroquinolones
    # =========================
    'ciprofloxacin': 'ciprofloxacin',
    'cipro': 'ciprofloxacin',
    'ciprofloxacin in': 'ciprofloxacin',
    'ciprofloxacin dexamethasone': 'ciprofloxacin',
    'ciprofloxacin/dexamethasone': 'ciprofloxacin',
    'ciprofloxacin hcl': 'ciprofloxacin',

    'levofloxacin': 'levofloxacin',
    'levaquin': 'levofloxacin',
    'levofloxacin in': 'levofloxacin',

    'moxifloxacin': 'moxifloxacin',
    'moxifloxacin/sod.chloride(iso)': 'moxifloxacin',

    'gatifloxacin': 'gatifloxacin',
    'norfloxacin': 'norfloxacin',
    'ofloxacin': 'ofloxacin',
    'nalidixic acid': 'nalidixic acid',

    'delafloxacin': 'delafloxacin',


    # =========================
    # Macrolides / Lincosamides
    # =========================
    'erythromycin': 'erythromycin',
    'erythromycin ethylsuccinate': 'erythromycin',

    'clarithromycin': 'clarithromycin',
    'azithromycin': 'azithromycin',
    'zithromax': 'azithromycin',

    'clindamycin': 'clindamycin',
    'clindamycin in': 'clindamycin',
    'clindamycin hcl': 'clindamycin',
    'clindamycin phosphate': 'clindamycin',

    'quinupristin/dalfopristin': 'quinupristin/dalfopristin',


    # =========================
    # Tetracyclines
    # =========================
    'doxycycline': 'doxycycline',
    'doxycycline hyclate': 'doxycycline',
    'doxycycline monohydrate': 'doxycycline',

    'minocycline': 'minocycline',
    'tetracycline': 'tetracycline',

    'omadacycline': 'omadacycline',
    'eravacycline': 'eravacycline',


    # =========================
    # Sulfonamides / TMP
    # =========================
    'trimethoprim/sulfamethoxazole': 'trimethoprim/sulfamethoxazole',
    'bactrim': 'trimethoprim/sulfamethoxazole',
    'bactrim ds': 'trimethoprim/sulfamethoxazole',
    'sulfamethoxazole-trimethoprim': 'trimethoprim/sulfamethoxazole',
    'trimethoprim-sulfamethoxazole': 'trimethoprim/sulfamethoxazole',
    'sulfamethoxazole trimethoprim': 'trimethoprim/sulfamethoxazole',

    'trimethoprim': 'trimethoprim',


    # =========================
    # Glycopeptides
    # =========================
    'vancomycin': 'vancomycin',
    'vancomycin in': 'vancomycin',
    'vancomycin in dextrose': 'vancomycin',
    'vancomycin/diluent combo': 'vancomycin',


    # =========================
    # Oxazolidinones
    # =========================
    'linezolid': 'linezolid',
    'linezolid in dextrose': 'linezolid',
    'zyvox': 'linezolid',

    'tedizolid': 'tedizolid',


    # =========================
    # Other antibiotics
    # =========================
    'tigecycline': 'tigecycline',
    'daptomycin': 'daptomycin',

    'fosfomycin': 'fosfomycin',
    'fosfomycin tromethamine': 'fosfomycin',

    'metronidazole': 'metronidazole',
    'metronidazole in nacl': 'metronidazole',
    'flagyl': 'metronidazole',

    'rifampin': 'rifampin',
    'rifabutin': 'rifabutin',
    'rifaximin': 'rifaximin',
    'xifaxan': 'rifaximin',

    'methenamine': 'methenamine',
    'methenamine hippurate': 'methenamine',
    'methenamine mandelate': 'methenamine',
    'hiprex': 'methenamine',

    'nitrofurantoin': 'nitrofurantoin',
    'macrobid': 'nitrofurantoin',
    'macrodantin': 'nitrofurantoin',

    'dapsone': 'dapsone',
    'fidaxomicin': 'fidaxomicin',
    'silver sulfadiazine': 'silver sulfadiazine',

    'colistin': 'colistin',

    # =========================
    # Antifungals
    # =========================
    'fluconazole': 'fluconazole',
    'voriconazole': 'voriconazole',
    'posaconazole': 'posaconazole',
    'itraconazole': 'itraconazole',

    'micafungin': 'micafungin',
    'caspofungin': 'caspofungin',

    'amphotericin b': 'amphotericin b',
    'amphotericin': 'amphotericin b',

    'flucytosine': 'flucytosine',


    # =========================
    # TB / special drugs
    # =========================
    'isoniazid': 'isoniazid',
    'ethambutol': 'ethambutol',
    'pyrazinamide': 'pyrazinamide',
    'bedaquiline': 'bedaquiline',

    'clofazimine': 'clofazimine',
    'capreomycin': 'capreomycin',
    'cycloserine': 'cycloserine',
    'ethionamide': 'ethionamide'
}


df['medication_name_clean_std'] = df['medication_name_clean'].map(alias_map).fillna(df['medication_name_clean'])

df['medication_name_clean_std'].unique()

fix_map = {
    'keflex': 'cephalexin',
    'amoxicillin/pot clavulanate': 'amoxicillin/clavulanic acid',
    'ceftazidime/dextrose': 'ceftazidime',
    'piperacillin/tazobactam/dextrs': 'piperacillin/tazobactam',
    'amphotericin/b': 'amphotericin b',
    'nitrofurantoin macrocrystal': 'nitrofurantoin'
}

df['medication_name_clean_std'] = df['medication_name_clean_std'].replace(fix_map)

df['medication_name_clean_std'].unique()


###############class
import pandas as pd
# 1. 定义映射字典
class_mapping = {
    # 目标类别中已有的，保持原样
    'Beta Lactam': 'Beta Lactam',
    'Antitubercular': 'Antitubercular',
    'Combination Antibiotic': 'Combination Antibiotic',
    'Aminoglycoside': 'Aminoglycoside',
    'Macrolide Lincosamide': 'Macrolide Lincosamide',
    'Tetracycline': 'Tetracycline',
    'Fluoroquinolone': 'Fluoroquinolone',
    'Oxazolidinone': 'Oxazolidinone',
    'Fosfomycin': 'Fosfomycin',
    'Folate Synthesis Inhibitor': 'Folate Synthesis Inhibitor',
    'Monobactam': 'Monobactam',
    'Sulfonamide': 'Sulfonamide',
    'Nitrofuran': 'Nitrofuran',
    'Urinary Antiseptic': 'Urinary Antiseptic',
    'Ansamycin': 'Ansamycin',
    'Glycopeptide': 'Glycopeptide',
    'Nitroimidazole': 'Nitroimidazole',
    'Polymyxin, Lipopeptide': 'Polymyxin, Lipopeptide',

    # 需要转换的细分类别
    'extended_spectrum_penicillin': 'Beta Lactam',
    'glycopeptide': 'Glycopeptide',
    'tetracycline': 'Tetracycline',
    'extended_spectrum_cephalosporin': 'Beta Lactam',
    'lincosamide': 'Macrolide Lincosamide',
    'macrolide': 'Macrolide Lincosamide',
    'cephalosporin': 'Beta Lactam',
    'sulfonamide': 'Sulfonamide',
    'anti_staph_beta_lactam': 'Beta Lactam',
    'fluoroquinolone': 'Fluoroquinolone',
    'carbapenem': 'Beta Lactam',
    'penicillin': 'Beta Lactam',
    'aminoglycoside': 'Aminoglycoside',
    'beta_lactam_combo': 'Combination Antibiotic',
    'monobactam': 'Monobactam',
    'polymyxin': 'Polymyxin, Lipopeptide',
    'anti_UTI': 'Urinary Antiseptic',

    # 特殊/边缘类别处理
    'anti_anaerobe': 'Nitroimidazole',  # 临床抗厌氧菌常指硝基咪唑类（如甲硝唑），或根据需要调整
    'anti_staph_other': 'Combination Antibiotic',  # 或者是其他特定类别
    'azole': 'Combination Antibiotic',  # 抗真菌药，若无对应分类暂归为 Combo 或单独处理
    'echinocandin': 'Combination Antibiotic',  # 抗真菌药
    'polyene': 'Combination Antibiotic'  # 抗真菌药
}

# 2. 执行映射转换
df['antibiotic_class_std'] = df['antibiotic_class'].map(class_mapping)

# 3. 检查转换后的唯一值，确保都在你的目标数组中
print(df['antibiotic_class_std'].unique())

ARMD=df

# 4️⃣ 查看结果
print(df[['medication_name_clean_std','antibiotic_class_std']].drop_duplicates().sort_values('antibiotic_class_std'))
rt=df[['medication_name_clean_std','antibiotic_class_std']].drop_duplicates().sort_values('antibiotic_class_std')
rt.to_csv('medication_name_antibiotic_class_std.csv')
ARMD=df
ARMD.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/03_combined_microbiology_cultures_antibiotic_class_exposure2_std.csv')
ARMD['antibiotic_class'] =ARMD['antibiotic_class_std']
ARMD['medication_name'] =ARMD['medication_name_clean_std']
ARMD[['antibiotic_class_std', 'medication_name_clean_std']].drop_duplicates().sort_values('antibiotic_class_std')

ARMD.head()
CNSZ.head()
###########################################CNSZ
CNSZ['medication_name'].unique()
df2 = CNSZ.copy()
df2['medication_name_clean'] = (
    df2['medication_name']
    .str.lower()
    .str.strip()
    .str.replace('-', '/', regex=False)
    .str.replace(r'\s+', ' ', regex=True)
)

cnsz_to_std_map = {
    # β-lactams
    'cefoperazone/sulbactam': 'cefoperazone/sulbactam',
    'piperacillin/tazobactam': 'piperacillin/tazobactam',
    'amoxicillin': 'amoxicillin',
    'amoxicillin/clavulanate': 'amoxicillin/clavulanic acid',
    'amoxicillin/clavulanic acid': 'amoxicillin/clavulanic acid',
    'cefuroxime axetil': 'cefuroxime',
    'cefuroxime': 'cefuroxime',
    'ceftriaxone': 'ceftriaxone',
    'cefixime': 'cefixime',
    'cefaclor': 'cefaclor',
    'cefprozil': 'cefprozil',
    'cefazolin': 'cefazolin',
    'ceftazidime': 'ceftazidime',
    'ceftazidime/dextrose': 'ceftazidime',
    'ceftazidime/avibactam': 'ceftazidime/avibactam',
    'cefoxitin': 'cefoxitin',
    'latamoxef': 'latamoxef',
    'penicillin': 'penicillin',

    # carbapenems
    'meropenem': 'meropenem',
    'imipenem/cilastatin': 'imipenem/cilastatin',
    'imipenem': 'imipenem',

    # monobactam
    'aztreonam': 'aztreonam',

    # aminoglycosides
    'gentamicin': 'gentamicin',
    'amikacin': 'amikacin',
    'tobramycin': 'tobramycin',

    # fluoroquinolones
    'levofloxacin': 'levofloxacin',
    'moxifloxacin': 'moxifloxacin',
    'ciprofloxacin': 'ciprofloxacin',
    'gatifloxacin': 'gatifloxacin',
    'ofloxacin': 'ofloxacin',

    # macrolides / lincosamides
    'azithromycin': 'azithromycin',
    'clarithromycin': 'clarithromycin',
    'clindamycin': 'clindamycin',
    'clindamycin palmitate': 'clindamycin',

    # tetracyclines
    'doxycycline': 'doxycycline',
    'minocycline': 'minocycline',
    'tigecycline': 'tigecycline',

    # glycopeptides
    'vancomycin': 'vancomycin',
    'teicoplanin': 'teicoplanin',

    # antifungals
    'fluconazole': 'fluconazole',
    'voriconazole': 'voriconazole',
    'posaconazole': 'posaconazole',
    'isavuconazole': 'isavuconazole',
    'caspofungin': 'caspofungin',
    'amphotericin b': 'amphotericin b',
    'amphotericin b cholesteryl sulfate complex': 'amphotericin b',
    'flucytosine': 'flucytosine',
    'nystatin': 'nystatin',

    # antivirals
    'acyclovir': 'acyclovir',
    'valacyclovir': 'valacyclovir',
    'ganciclovir': 'ganciclovir',
    'foscarnet': 'foscarnet',
    'oseltamivir': 'oseltamivir',
    'nirmatrelvir/ritonavir': 'nirmatrelvir/ritonavir',
    'sofosbuvir/velpatasvir': 'sofosbuvir/velpatasvir',
    'tenofovir disoproxil': 'tenofovir disoproxil',
    'tenofovir alafenamide': 'tenofovir alafenamide',
    'tenofovir amibufenamide': 'tenofovir amibufenamide',
    'entecavir': 'entecavir',
    'azvudine': 'azvudine',

    # TB drugs
    'isoniazid': 'isoniazid',
    'rifampin': 'rifampin',
    'ethambutol': 'ethambutol',
    'pyrazinamide': 'pyrazinamide',

    # others
    'metronidazole': 'metronidazole',
    'ornidazole': 'metronidazole',
    'fosfomycin trometamol': 'fosfomycin',
    'fosfomycin tromethamine': 'fosfomycin',
    'polymyxin b': 'polymyxin b',
    'berberine': 'berberine',
    'thalidomide': 'thalidomide',
    'oseltamivir': 'oseltamivir'
}

df2['medication_name_clean_std'] = (
    df2['medication_name_clean']
    .map(cnsz_to_std_map)
    .fillna(df2['medication_name_clean'])
)

df2['medication_name_clean_std'].unique()

ARMD['antibiotic_class'].unique()
# 当前已标准化的抗微生物药物列表
antimicrobials = [
    'cefoperazone/sulbactam', 'piperacillin/tazobactam', 'amoxicillin',
    'amoxicillin/clavulanic acid', 'cefuroxime', 'ceftriaxone', 'cefixime',
    'cefaclor', 'cefprozil', 'cefazolin', 'ceftazidime', 'ceftazidime/avibactam',
    'cefoxitin', 'latamoxef', 'meropenem', 'imipenem/cilastatin', 'imipenem',
    'aztreonam', 'gentamicin', 'amikacin', 'tobramycin', 'levofloxacin',
    'moxifloxacin', 'ciprofloxacin', 'azithromycin', 'clarithromycin',
    'clindamycin', 'doxycycline', 'minocycline', 'tigecycline',
    'vancomycin', 'teicoplanin', 'fluconazole', 'voriconazole', 'posaconazole',
    'isavuconazole', 'caspofungin', 'amphotericin b', 'flucytosine', 'nystatin',
    'acyclovir', 'valacyclovir', 'ganciclovir', 'foscarnet', 'oseltamivir',
    'nirmatrelvir/ritonavir', 'sofosbuvir/velpatasvir', 'tenofovir disoproxil',
    'tenofovir alafenamide', 'tenofovir amibufenamide', 'entecavir', 'azvudine',
    'isoniazid', 'rifampin', 'ethambutol', 'pyrazinamide', 'fosfomycin',
    'metronidazole', 'ornidazole', 'polymyxin b', 'colistin', 'ceftolozane/tazobactam',
    'imipenem/relebactam', 'meropenem/vaborbactam', 'ceftaroline', 'cefiderocol',
    'cefpodoxime', 'cefepime', 'ampicillin', 'ampicillin/sulbactam', 'penicillin',
    'ceftazidime/dextrose', 'ceftazidime/avibactam'
]

# 将非抗微生物药物标记为 NA
df2['medication_name_clean_std'] = df2['medication_name_clean_std'].apply(
    lambda x: x if x in antimicrobials else None
)


CNSZ=df2

CNSZ['medication_name_clean_std'].unique()
###############class
import pandas as pd
import numpy as np

# 1. 建立具体药物到 18 个标准大类的映射字典
medication_mapping = {
    # === Beta Lactam ===
    'cefoperazone/sulbactam': 'Beta Lactam',      # 头孢哌酮舒巴坦
    'meropenem': 'Beta Lactam',                   # 美罗培南
    'cefuroxime': 'Beta Lactam',                  # 头孢呋辛
    'piperacillin/tazobactam': 'Beta Lactam',     # 哌拉西林他唑巴坦
    'amoxicillin': 'Beta Lactam',                 # 阿莫西林
    'ceftriaxone': 'Beta Lactam',                 # 头孢曲松
    'cefixime': 'Beta Lactam',                    # 头孢克肟
    'amoxicillin/clavulanic acid': 'Beta Lactam', # 阿莫西林克拉维酸钾
    'latamoxef': 'Beta Lactam',                   # 拉氧头孢（氧头孢烯类，临床归入广谱β-内酰胺）
    'cefaclor': 'Beta Lactam',                    # 头孢克洛
    'imipenem/cilastatin': 'Beta Lactam',         # 亚胺培南西司他丁
    'penicillin': 'Beta Lactam',                  # 青霉素
    'ceftazidime': 'Beta Lactam',                 # 头孢他啶
    'cefprozil': 'Beta Lactam',                   # 头孢丙烯
    'cefazolin': 'Beta Lactam',                   # 头孢唑林
    'cefpodoxime': 'Beta Lactam',                 # 头孢泊肟
    'cefoxitin': 'Beta Lactam',                   # 头孢西丁

    # === Macrolide Lincosamide ===
    'azithromycin': 'Macrolide Lincosamide',      # 阿奇霉素
    'clindamycin': 'Macrolide Lincosamide',       # 克林霉素
    'clarithromycin': 'Macrolide Lincosamide',     # 克拉霉素

    # === Fluoroquinolone ===
    'levofloxacin': 'Fluoroquinolone',            # 左氧氟沙星
    'moxifloxacin': 'Fluoroquinolone',            # 莫西沙星
    'ciprofloxacin': 'Fluoroquinolone',           # 环丙沙星

    # === Tetracycline ===
    'doxycycline': 'Tetracycline',                # 多西环素
    'minocycline': 'Tetracycline',                # 米诺环素
    'tigecycline': 'Tetracycline',                # 替加环素

    # === Aminoglycoside ===
    'gentamicin': 'Aminoglycoside',               # 庆大霉素
    'amikacin': 'Aminoglycoside',                 # 阿米卡星
    'tobramycin': 'Aminoglycoside',               # 妥布霉素

    # === Glycopeptide ===
    'vancomycin': 'Glycopeptide',                 # 万古霉素
    'teicoplanin': 'Glycopeptide',                # 替考拉宁

    # === Monobactam ===
    'aztreonam': 'Monobactam',                    # 氨曲南

    # === Nitroimidazole ===
    'metronidazole': 'Nitroimidazole',            # 甲硝唑

    # === Polymyxin, Lipopeptide ===
    'polymyxin b': 'Polymyxin, Lipopeptide',      # 多黏菌素B

    # === Fosfomycin ===
    'fosfomycin': 'Fosfomycin',                   # 磷霉素（若临床无特殊要求，直接映射单药大类）

    # === Antitubercular ===
    'ethambutol': 'Antitubercular',               # 乙胺丁醇
    'pyrazinamide': 'Antitubercular',             # 吡嗪酰胺
    'rifampin': 'Antitubercular',                 # 利福平
    'isoniazid': 'Antitubercular',                # 异烟肼

    # === Combination Antibiotic (包含：抗真菌药、抗病毒药、新型超级复方) ===
    # 1. 新型抗细菌复方
    'ceftazidime/avibactam': 'Combination Antibiotic', # 头孢他啶阿维巴坦
    # 2. 抗真菌药 (Antifungals)
    'voriconazole': 'Combination Antibiotic',     # 伏立康唑
    'fluconazole': 'Combination Antibiotic',      # 氟康唑
    'posaconazole': 'Combination Antibiotic',     # 泊沙康唑
    'nystatin': 'Combination Antibiotic',         # 制霉菌素
    'caspofungin': 'Combination Antibiotic',      # 卡泊芬净
    'isavuconazole': 'Combination Antibiotic',    # 艾沙康唑
    'amphotericin b': 'Combination Antibiotic',   # 两性霉素B
    'flucytosine': 'Combination Antibiotic',      # 氟胞嘧啶
    # 3. 抗病毒药 (Antivirals - 目标18类中无对应抗病毒大类，暂清洗至此)
    'acyclovir': 'Combination Antibiotic',        # 阿昔洛韦
    'oseltamivir': 'Combination Antibiotic',      # 奥司他韦
    'entecavir': 'Combination Antibiotic',        # 恩替卡韦
    'valacyclovir': 'Combination Antibiotic',     # 伐昔洛韦
    'tenofovir alafenamide': 'Combination Antibiotic', # TAF
    'ganciclovir': 'Combination Antibiotic',      # 更昔洛韦
    'azvudine': 'Combination Antibiotic',         # 阿兹夫定
    'tenofovir disoproxil': 'Combination Antibiotic',  # TDF
    'foscarnet': 'Combination Antibiotic',        # 膦甲酸钠
    'sofosbuvir/velpatasvir': 'Combination Antibiotic',# 丙通沙
    'tenofovir amibufenamide': 'Combination Antibiotic',# 艾米替诺福韦
    'nirmatrelvir/ritonavir': 'Combination Antibiotic', # Paxlovid
}

# 2. 执行映射清洗
#CNSZ['antibiotic_class_std'] = CNSZ['medication_name_clean_std'].map(medication_mapping)
# 执行映射清洗，未匹配上的用原始名称填充
CNSZ['antibiotic_class_std'] = CNSZ['medication_name_clean_std'].map(medication_mapping).fillna(CNSZ['medication_name_clean_std'])
# 3. 打印检查映射后的唯一值
print(CNSZ['antibiotic_class_std'].dropna().unique())
CNSZ.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/03.microbiology_cultures_prior_med_std_time_anon_antibiotic_class_std.csv')

CNSZ['order_time_jittered'] = CNSZ['order_time_jittered_std']
CNSZ['antibiotic_class'] = CNSZ['antibiotic_class_std']
ARMD['antibiotic_class'] = ARMD['antibiotic_class_std']
CNSZ['antibiotic_class'].unique()
# 1. 定义需要保留的 10 个标准列
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

# 2. 提取 ARMD 数据（排在前面）
# 如果你想把 ARMD 的 source 列统一改成 "ARMD"，可以加上后面那句注释
df_armd_sub = ARMD[target_columns].copy()
# df_armd_sub['source'] = 'ARMD'  # 如果需要强制统一来源名称，请取消本行注释

# 3. 提取 CNSZ 数据（排在后面）
df_cnsz_sub = CNSZ[target_columns].copy()

# 4. 纵向合并：ARMD 在前，CNSZ 在后
# ignore_index=True 可以确保重新生成从 0 到 1200+ 万的干净连续行索引
merged_df = pd.concat([df_armd_sub, df_cnsz_sub], ignore_index=True)

# 5. 验证结果
print(f"合并后的数据集形状 (Shape): {merged_df.shape}")
print("\n数据前 3 行 (应全为 ARMD 数据):")
print(merged_df.head(3))
print("\n数据后 3 行 (应全为 CNSZ 数据):")
print(merged_df.tail(3))

merged_df.to_csv('./merge3/03_combined_microbiology_cultures_antibiotic_class_exposure3.csv')

##################################microbiology_cultures_antibiotic_subtype_exposure.csv
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2')

import pandas as pd
import numpy as np
# 设置显示的最大列数，None 表示显示所有列
pd.set_option('display.max_columns', None)
# 设置每行显示的宽度，防止自动换行
pd.set_option('display.width', 1000)
ARMD=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/04_combined_microbiology_cultures_antibiotic_subtype_exposure2.csv')
ARMD2=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/03_combined_microbiology_cultures_antibiotic_class_exposure2_std.csv')
ARMD['order_time_jittered_std']=ARMD2['order_time_jittered_std']
ARMD['medication_name_clean_std']=ARMD2['medication_name_clean_std']
ARMD['antibiotic_class_std'] = ARMD2['antibiotic_class_std']
CNSZ=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/03.microbiology_cultures_prior_med_std_time_anon_antibiotic_class_std.csv')
ARMD.head()
ARMD.loc[ARMD['source'] == 'Stanford', 'antibiotic_subtype'].unique()
ARMD['antibiotic_subtype_category'].unique()
ARMD.loc[ARMD['source'] == 'Stanford', 'antibiotic_subtype_category'].unique()
CNSZ.head()
CNSZ['medication_name_clean_std'].unique()

import pandas as pd
import numpy as np

# ==========================================
# 1. 定义全量药物成分（Medication）到 34个标准小类（Subtype）的映射字典
# ==========================================
med_to_subtype_mapping = {
    # ------------------ 抗细菌药 (Antibiotics - 25类) ------------------
    # 青霉素类
    'amoxicillin': 'Penicillin',
    'penicillin': 'Penicillin',
    'ampicillin': 'Penicillin',
    'oxacillin': 'Penicillin',
    'nafcillin': 'Penicillin',
    'dicloxacillin': 'Penicillin',

    # β-内酰胺复合制剂
    'cefoperazone/sulbactam': 'Beta Lactam Combo',
    'piperacillin/tazobactam': 'Beta Lactam Combo',
    'amoxicillin/clavulanic acid': 'Beta Lactam Combo',
    'ampicillin/sulbactam': 'Beta Lactam Combo',
    'ceftazidime/avibactam': 'Beta Lactam Combo',
    'ceftolozane/tazobactam': 'Beta Lactam Combo',
    'meropenem/vaborbactam': 'Beta Lactam Combo',
    'imipenem/relebactam': 'Beta Lactam Combo',

    # 碳青霉烯类
    'meropenem': 'Carbapenem',
    'imipenem': 'Carbapenem',
    'ertapenem': 'Carbapenem',
    'imipenem/cilastatin': 'Carbapenem',

    # 单环 β-内酰胺类
    'aztreonam': 'Monobactam',

    # 头孢菌素类（分代）
    'cefaclor': 'Cephalosporin Gen1',
    'cefazolin': 'Cephalosporin Gen1',
    'postalexin': 'Cephalosporin Gen1',
    'cefuroxime': 'Cephalosporin Gen2',
    'cefprozil': 'Cephalosporin Gen2',
    'cefoxitin': 'Cephalosporin Gen2',
    'cefotetan': 'Cephalosporin Gen2',
    'ceftriaxone': 'Cephalosporin Gen3',
    'cefixime': 'Cephalosporin Gen3',
    'ceftazidime': 'Cephalosporin Gen3',
    'cefpodoxime': 'Cephalosporin Gen3',
    'cefdinir': 'Cephalosporin Gen3',
    'cefotaxime': 'Cephalosporin Gen3',
    'latamoxef': 'Cephalosporin Gen3',  # 拉氧头孢临床常视作广谱三代头孢
    'cefepime': 'Cephalosporin Gen4',
    'ceftaroline': 'Cephalosporin Gen4',
    'cefiderocol': 'Cephalosporin Gen4',

    # 大环内酯类与林可酰胺类
    'azithromycin': 'Macrolide',
    'clarithromycin': 'Macrolide',
    'erythromycin': 'Macrolide',
    'fidaxomicin': 'Macrolide',
    'clindamycin': 'Lincosamide',

    # 氟喹诺酮类
    'levofloxacin': 'Fluoroquinolone',
    'moxifloxacin': 'Fluoroquinolone',
    'ciprofloxacin': 'Fluoroquinolone',
    'ofloxacin': 'Fluoroquinolone',
    'gatifloxacin': 'Fluoroquinolone',
    'delafloxacin': 'Fluoroquinolone',

    # 四环素类
    'doxycycline': 'Tetracycline',
    'minocycline': 'Tetracycline',
    'tigecycline': 'Tetracycline',
    'omadacycline': 'Tetracycline',
    'eravacycline': 'Tetracycline',

    # 氨基糖苷类
    'gentamicin': 'Aminoglycoside',
    'amikacin': 'Aminoglycoside',
    'tobramycin': 'Aminoglycoside',

    # 糖肽类
    'vancomycin': 'Glycopeptide',
    'teicoplanin': 'Glycopeptide',
    'dalbavancin': 'Glycopeptide',

    # 磺胺类与叶酸抑制剂
    'silver sulfadiazine': 'Sulfonamide',
    'dapsone': 'Sulfonamide',
    'trimethoprim/sulfamethoxazole': 'Sulfonamide Combo',
    'sulfamethoxazole/trimethoprim': 'Sulfonamide Combo',
    'trimethoprim': 'Folate Synthesis Inhibitor',

    # 多黏菌素类
    'polymyxin b': 'Polymyxin',
    'colistin': 'Polymyxin',

    # 其他抗细菌单药类别
    'metronidazole': 'Nitroimidazole',
    'fosfomycin': 'Fosfomycin',
    'nitrofurantoin': 'Nitrofuran',
    'methenamine': 'Urinary Antiseptic',
    'ethambutol': 'Antitubercular',
    'pyrazinamide': 'Antitubercular',
    'rifampin': 'Ansamycin',
    'rifabutin': 'Ansamycin',
    'rifaximin': 'Ansamycin',
    'isoniazid': 'Antitubercular',
    'linezolid': 'Oxazolidinone',
    'tedizolid': 'Oxazolidinone',

    # ------------------ 抗真菌药 (Antifungals - 4类) ------------------
    'voriconazole': 'Azole Antifungal',
    'fluconazole': 'Azole Antifungal',
    'posaconazole': 'Azole Antifungal',
    'isavuconazole': 'Azole Antifungal',
    'caspofungin': 'Echinocandin',
    'nystatin': 'Polyene Antifungal',
    'amphotericin b': 'Polyene Antifungal',
    'flucytosine': 'Pyrimidine Analog',

    # ------------------ 抗病毒药 (Antivirals - 5类) ------------------
    'nirmatrelvir/ritonavir': 'Anti-SARS-CoV-2',
    'azvudine': 'Anti-SARS-CoV-2',
    'oseltamivir': 'Neuraminidase Inhibitor',
    'acyclovir': 'Anti-Herpesvirus',
    'valacyclovir': 'Anti-Herpesvirus',
    'ganciclovir': 'Anti-Herpesvirus',
    'foscarnet': 'Anti-Herpesvirus',
    'entecavir': 'Anti-HBV Nucleoside/Nucleotide',
    'tenofovir disoproxil': 'Anti-HBV Nucleoside/Nucleotide',
    'tenofovir alafenamide': 'Anti-HBV Nucleoside/Nucleotide',
    'tenofovir amibufenamide': 'Anti-HBV Nucleoside/Nucleotide',
    'sofosbuvir/velpatasvir': 'Direct-Acting Antiviral (HCV)'
}

# ==========================================
# 2. 定义 34个标准小类（Subtype）到 英文缩写（Category）的映射字典
# ==========================================
subtype_to_category_mapping = {
    # 抗细菌药缩写 (25类)
    'Aminoglycoside': 'AMG',
    'Beta Lactam Combo': 'BLC',
    'Penicillin': 'PEN',
    'Cephalosporin Gen1': 'CEP1',
    'Cephalosporin Gen2': 'CEP2',
    'Cephalosporin Gen3': 'CEP3',
    'Cephalosporin Gen4': 'CEP4',
    'Carbapenem': 'CAR',
    'Monobactam': 'MON',
    'Macrolide': 'MAC',
    'Lincosamide': 'LIN',
    'Sulfonamide': 'SUL',
    'Sulfonamide Combo': 'SULC',
    'Folate Synthesis Inhibitor': 'FSI',
    'Fluoroquinolone': 'FLQ',
    'Tetracycline': 'TET',
    'Fosfomycin': 'FOS',
    'Nitrofuran': 'NIT',
    'Antitubercular': 'AT',
    'Urinary Antiseptic': 'UA',
    'Ansamycin': 'ANS',
    'Glycopeptide': 'GLY',
    'Oxazolidinone': 'OXA',
    'Nitroimidazole': 'NIM',
    'Polymyxin': 'POL',

    # 抗真菌药缩写 (4类)
    'Azole Antifungal': 'AZA',
    'Echinocandin': 'ECH',
    'Polyene Antifungal': 'POL-F',
    'Pyrimidine Analog': 'PYR',

    # 抗病毒药缩写 (5类)
    'Anti-SARS-CoV-2': 'COV',
    'Neuraminidase Inhibitor': 'NEU',
    'Anti-Herpesvirus': 'HER',
    'Anti-HBV Nucleoside/Nucleotide': 'HBV',
    'Direct-Acting Antiviral (HCV)': 'HCV'
}

# ==========================================
# 3. 执行核心数据清洗流水线
# ==========================================

# 第一步：根据标准化药名生成标准小类全称（使用 replace 确保未匹配项和 nan 安全原样保留）
CNSZ['antibiotic_subtype'] = CNSZ['medication_name_clean_std'].replace(med_to_subtype_mapping)

# 第二步：基于生成的小类全称，映射出标准的缩写代码列
CNSZ['antibiotic_subtype_category'] = CNSZ['antibiotic_subtype'].map(subtype_to_category_mapping)

# 如果原始的非标准小类也需要被同步更新，可直接映射更新（保持前后列逻辑统一）
if 'antibiotic_subtype_category' in CNSZ.columns:
    CNSZ['antibiotic_subtype_category'] = CNSZ['antibiotic_subtype_category'].fillna(CNSZ['antibiotic_subtype'])

# ==========================================
# 4. 自动化一致性审计与数据验证
# ==========================================
print("======= 🚀 CNSZ 数据集清洗完成报告 =======")
print("1. 清洗后包含的非空小类全称总数:", CNSZ['antibiotic_subtype'].dropna().nunique())
print("2. 清洗后包含的非空缩写代码总数:", CNSZ['antibiotic_subtype_category'].dropna().nunique())

# 检查是否存在全称有值但缩写丢失的冲突情况
leak_check = CNSZ[
    CNSZ['antibiotic_subtype'].isin(subtype_to_category_mapping.keys()) & CNSZ['antibiotic_subtype_category'].isna()]
if len(leak_check) == 0:
    print("✨ [审计成功]：所有已分类的药物成分均已成功对齐全称与英文缩写！")
else:
    print(f"⚠️ [发现异常]：有 {len(leak_check)} 行映射漏网，请检查逻辑。")

CNSZ.head()
CNSZ.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/03.microbiology_cultures_prior_med_std_time_anon_antibiotic_class_std_antibiotic_subtype.csv')
ARMD.head()
ARMD['medication_name_clean_std'].unique()

#ARMD med_to_subtype_mapping
import pandas as pd
import numpy as np
# ==========================================
# 1. 定义 ARMD/CNSZ 全量药物成分到 34个标准小类的映射字典
# ==========================================
med_to_subtype_mapping = {
    # ------------------ 抗细菌药 (Antibiotics - 25类) ------------------
    # 青霉素类 (PEN)
    'penicillin': 'Penicillin',
    'ampicillin': 'Penicillin',
    'amoxicillin': 'Penicillin',
    'dicloxacillin': 'Penicillin',
    'oxacillin': 'Penicillin',
    'nafcillin': 'Penicillin',

    # β-内酰胺复合制剂 (BLC)
    'amoxicillin/clavulanic acid': 'Beta Lactam Combo',
    'piperacillin/tazobactam': 'Beta Lactam Combo',
    'cefoperazone/sulbactam': 'Beta Lactam Combo',
    'ceftazidime/avibactam': 'Beta Lactam Combo',
    'ampicillin/sulbactam': 'Beta Lactam Combo',
    'ceftolozane/tazobactam': 'Beta Lactam Combo',
    'meropenem/vaborbactam': 'Beta Lactam Combo',
    'imipenem/relebactam': 'Beta Lactam Combo',

    # 碳青霉烯类 (CAR)
    'meropenem': 'Carbapenem',
    'ertapenem': 'Carbapenem',
    'imipenem': 'Carbapenem',
    'imipenem/cilastatin': 'Carbapenem',

    # 单环 β-内酰胺类 (MON)
    'aztreonam': 'Monobactam',

    # 头孢菌素类（分代）
    # 一代头孢 (CEP1)
    'cefadroxil': 'Cephalosporin Gen1',
    'cephalexin': 'Cephalosporin Gen1',
    'cefazolin': 'Cephalosporin Gen1',
    'ceaclor': 'Cephalosporin Gen1',
    'postalexin': 'Cephalosporin Gen1',
    # 二代头孢 (CEP2)
    'cefoxitin': 'Cephalosporin Gen2',
    'cefuroxime': 'Cephalosporin Gen2',
    'cefotetan': 'Cephalosporin Gen2',
    'cefprozil': 'Cephalosporin Gen2',
    # 三代头孢 (CEP3)
    'ceftazidime': 'Cephalosporin Gen3',
    'cefdinir': 'Cephalosporin Gen3',
    'cefpodoxime': 'Cephalosporin Gen3',
    'ceftriaxone': 'Cephalosporin Gen3',
    'cefixime': 'Cephalosporin Gen3',
    'cefotaxime': 'Cephalosporin Gen3',
    'latamoxef': 'Cephalosporin Gen3',
    # 四代及新型头孢 (CEP4)
    'cefepime': 'Cephalosporin Gen4',
    'ceftaroline': 'Cephalosporin Gen4',
    'cefiderocol': 'Cephalosporin Gen4',

    # 大环内酯类 (MAC) 与 林可酰胺类 (LIN)
    'erythromycin': 'Macrolide',
    'clarithromycin': 'Macrolide',
    'fidaxomicin': 'Macrolide',
    'azithromycin': 'Macrolide',
    'clindamycin': 'Lincosamide',

    # 氟喹诺酮类 (FLQ)
    'ofloxacin': 'Fluoroquinolone',
    'ciprofloxacin': 'Fluoroquinolone',
    'levofloxacin': 'Fluoroquinolone',
    'gatifloxacin': 'Fluoroquinolone',
    'moxifloxacin': 'Fluoroquinolone',
    'delafloxacin': 'Fluoroquinolone',

    # 四环素类 (TET)
    'minocycline': 'Tetracycline',
    'doxycycline': 'Tetracycline',
    'tetracycline': 'Tetracycline',
    'tigecycline': 'Tetracycline',
    'eravacycline': 'Tetracycline',
    'omadacycline': 'Tetracycline',

    # 氨基糖苷类 (AMG)
    'tobramycin': 'Aminoglycoside',
    'amikacin': 'Aminoglycoside',
    'gentamicin': 'Aminoglycoside',

    # 糖肽类 (GLY)
    'vancomycin': 'Glycopeptide',
    'teicoplanin': 'Glycopeptide',
    'dalbavancin': 'Glycopeptide',

    # 磺胺类与复方 (SUL / SULC)
    'trimethoprim/sulfamethoxazole': 'Sulfonamide Combo',
    'sulfamethoxazole/trimethoprim': 'Sulfonamide Combo',
    'silver sulfadiazine': 'Sulfonamide',
    'dapsone': 'Sulfonamide',
    'sulfonamide': 'Sulfonamide',

    # 叶酸合成抑制剂 (FSI)
    'trimethoprim': 'Folate Synthesis Inhibitor',

    # 多黏菌素及脂肽类 (POL)
    'colistin': 'Polymyxin',
    'polymyxin b': 'Polymyxin',
    'daptomycin': 'Polymyxin',  # 达托霉素依归类习惯收拢至 POL 小类

    # 其他特定抗细菌小类
    'linezolid': 'Oxazolidinone',
    'tedizolid': 'Oxazolidinone',
    'fosfomycin': 'Fosfomycin',
    'nitrofurantoin': 'Nitrofuran',
    'methenamine': 'Urinary Antiseptic',
    'metronidazole': 'Nitroimidazole',
    'ethambutol': 'Antitubercular',
    'isoniazid': 'Antitubercular',
    'pyrazinamide': 'Antitubercular',
    'rifabutin': 'Ansamycin',
    'rifaximin': 'Ansamycin',
    'rifampin': 'Ansamycin',

    # ------------------ 抗真菌药 (Antifungals - 4类) ------------------
    'fluconazole': 'Azole Antifungal',
    'itraconazole': 'Azole Antifungal',
    'voriconazole': 'Azole Antifungal',
    'posaconazole': 'Azole Antifungal',
    'isavuconazole': 'Azole Antifungal',
    'micafungin': 'Echinocandin',
    'caspofungin': 'Echinocandin',
    'amphotericin b': 'Polyene Antifungal',
    'nystatin': 'Polyene Antifungal',
    'flucytosine': 'Pyrimidine Analog',

    # ------------------ 抗病毒药 (Antivirals - 5类) ------------------
    'nirmatrelvir/ritonavir': 'Anti-SARS-CoV-2',
    'azvudine': 'Anti-SARS-CoV-2',
    'oseltamivir': 'Neuraminidase Inhibitor',
    'acyclovir': 'Anti-Herpesvirus',
    'valacyclovir': 'Anti-Herpesvirus',
    'ganciclovir': 'Anti-Herpesvirus',
    'foscarnet': 'Anti-Herpesvirus',
    'entecavir': 'Anti-HBV Nucleoside/Nucleotide',
    'tenofovir disoproxil': 'Anti-HBV Nucleoside/Nucleotide',
    'tenofovir alafenamide': 'Anti-HBV Nucleoside/Nucleotide',
    'tenofovir amibufenamide': 'Anti-HBV Nucleoside/Nucleotide',
    'sofosbuvir/velpatasvir': 'Direct-Acting Antiviral (HCV)'
}

# ==========================================
# 2. 定义 34个标准小类（Subtype）到 英文缩写（Category）的映射字典
# ==========================================
subtype_to_category_mapping = {
    # 抗细菌药 (25类)
    'Aminoglycoside': 'AMG', 'Beta Lactam Combo': 'BLC', 'Penicillin': 'PEN',
    'Cephalosporin Gen1': 'CEP1', 'Cephalosporin Gen2': 'CEP2',
    'Cephalosporin Gen3': 'CEP3', 'Cephalosporin Gen4': 'CEP4',
    'Carbapenem': 'CAR', 'Monobactam': 'MON', 'Macrolide': 'MAC', 'Lincosamide': 'LIN',
    'Sulfonamide': 'SUL', 'Sulfonamide Combo': 'SULC', 'Folate Synthesis Inhibitor': 'FSI',
    'Fluoroquinolone': 'FLQ', 'Tetracycline': 'TET', 'Fosfomycin': 'FOS', 'Nitrofuran': 'NIT',
    'Antitubercular': 'AT', 'Urinary Antiseptic': 'UA', 'Ansamycin': 'ANS', 'Glycopeptide': 'GLY',
    'Oxazolidinone': 'OXA', 'Nitroimidazole': 'NIM', 'Polymyxin': 'POL',

    # 抗真菌药 (4类)
    'Azole Antifungal': 'AZA', 'Echinocandin': 'ECH', 'Polyene Antifungal': 'POL-F', 'Pyrimidine Analog': 'PYR',

    # 抗病毒药 (5类)
    'Anti-SARS-CoV-2': 'COV', 'Neuraminidase Inhibitor': 'NEU', 'Anti-Herpesvirus': 'HER',
    'Anti-HBV Nucleoside/Nucleotide': 'HBV', 'Direct-Acting Antiviral (HCV)': 'HCV'
}

# ==========================================
# 3. 运行数据清洗流与局部值保持机制
# ==========================================

# 映射生成小类全称（使用 replace 保证字典之外的杂项和原始 nan 能够填充映射前的值）
ARMD['antibiotic_subtype_std'] = ARMD['medication_name_clean_std'].replace(med_to_subtype_mapping)

# 映射生成标准小类英文缩写代码
ARMD['antibiotic_subtype_category_std'] = ARMD['antibiotic_subtype_std'].map(subtype_to_category_mapping)

# 保留未映射项的原始信息至缩写代码列，实现数据闭环
ARMD['antibiotic_subtype_category_std'] = ARMD['antibiotic_subtype_category_std'].fillna(ARMD['antibiotic_subtype_std'])

# ==========================================
# 4. 自动化对齐审计
# ==========================================
print("======= 🚀 ARMD 数据集（包含Stanford源）清洗完成报告 =======")
print("1. 清洗后的小类全称总数 (去空):", ARMD['antibiotic_subtype'].dropna().nunique())
print("2. 清洗后的英文缩写总数 (去空):", ARMD['antibiotic_subtype_category'].dropna().nunique())

# 检查是否有漏网之鱼
leak_count = ARMD[ARMD['antibiotic_subtype_std'].isin(subtype_to_category_mapping.keys()) & ARMD[
    'antibiotic_subtype_category_std'].isna()].shape[0]
if leak_count == 0:
    print("✨ [双向映射同步成功]：78 种异质源药物成分已完美规整对齐至 34 个核心标准层级！")
else:
    print(f"⚠️ [系统提示]：仍有 {leak_count} 行全称没有成功绑定至英文缩写，请检查拼写。")

ARMD.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/03_combined_microbiology_cultures_antibiotic_class_exposure2_std_subtype.csv')

# 4️⃣ 查看结果
print(ARMD[['medication_name','medication_name_clean_std','medication_category','antibiotic_class_std','antibiotic_subtype','antibiotic_subtype_std','antibiotic_subtype_category','antibiotic_subtype_category_std']].drop_duplicates().sort_values('antibiotic_class_std'))
rt=ARMD[['medication_name','medication_name_clean_std','medication_category','antibiotic_class_std','antibiotic_subtype','antibiotic_subtype_std','antibiotic_subtype_category','antibiotic_subtype_category_std']].drop_duplicates().sort_values('antibiotic_class_std')
ARMD.to_csv('medication_name_antibiotic_class_subtype_std_ARMD.csv')

ARMD['antibiotic_subtype'] = ARMD['antibiotic_subtype_std']
ARMD['antibiotic_subtype_category'] = ARMD['antibiotic_subtype_category_std']

# 1. 定义需要保留的 10 个标准列
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

# 2. 提取 ARMD 数据（排在前面）
# 如果你想把 ARMD 的 source 列统一改成 "ARMD"，可以加上后面那句注释
df_armd_sub = ARMD[target_columns].copy()
# df_armd_sub['source'] = 'ARMD'  # 如果需要强制统一来源名称，请取消本行注释

# 3. 提取 CNSZ 数据（排在后面）
df_cnsz_sub = CNSZ[target_columns].copy()

# 4. 纵向合并：ARMD 在前，CNSZ 在后
# ignore_index=True 可以确保重新生成从 0 到 1200+ 万的干净连续行索引
merged_df = pd.concat([df_armd_sub, df_cnsz_sub], ignore_index=True)

# 5. 验证结果
print(f"合并后的数据集形状 (Shape): {merged_df.shape}")
print("\n数据前 3 行 (应全为 ARMD 数据):")
print(merged_df.head(3))
print("\n数据后 3 行 (应全为 CNSZ 数据):")
print(merged_df.tail(3))

merged_df.to_csv('./merge3/04_combined_microbiology_cultures_antibiotic_subtype_exposure3.csv')

##########################################08_combined_microbiology_cultures_microbial_resistance2
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2')

import pandas as pd
import numpy as np
# 设置显示的最大列数，None 表示显示所有列
pd.set_option('display.max_columns', None)
# 设置每行显示的宽度，防止自动换行
pd.set_option('display.width', 1000)
ARMD=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/08_combined_microbiology_cultures_microbial_resistance2.csv')
ARMD2=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/03_combined_microbiology_cultures_antibiotic_class_exposure2_std.csv')
ARMD['order_time_jittered_std']=ARMD2['order_time_jittered_std']
ARMD['medication_name_clean_std']=ARMD2['medication_name_clean_std']
ARMD['antibiotic_class_std'] = ARMD2['antibiotic_class_std']
CNSZ=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/03.microbiology_cultures_prior_med_std_time_anon_antibiotic_class_std.csv')
ARMD.head()
ARMD.loc[ARMD['source'] == 'Stanford', 'antibiotic'].unique()
ARMD.loc[ARMD['source'] == 'Stanford', 'organism'].unique()
ARMD['antibiotic'].unique()
ARMD['organism'].unique()
ARMD.loc[ARMD['source'] == 'Stanford', 'antibiotic_subtype_category'].unique()
CNSZ.head()
CNSZ['medication_name_clean_std'].unique()

organism_std = pd.read_csv(
    '/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/ARMD_organism2.txt',
    sep='\t',
    encoding='gb18030'  # 兼容 GBK 并涵盖更多生僻字
)

# 关键列统一小写 + 去空格
organism_std['raw'] = organism_std['organism'].str.strip().str.lower()
organism_std['standard'] = organism_std['organism_std'].str.strip().str.lower()
ARMD['organism_clean'] = (
    ARMD['organism']
    .astype(str)
    .str.strip()
    .str.lower()
)
mapping_dict = dict(zip(organism_std['raw'], organism_std['standard']))
ARMD['organism_std'] = ARMD['organism_clean'].map(mapping_dict)
unmatched = ARMD.loc[ARMD['organism_std'].isna(), 'organism_clean'].unique()
print(len(unmatched))
print(unmatched)

import pandas as pd

# =================================================================
# 1. 核心映射统计审计
# =================================================================
total_raw_unique = ARMD['organism_clean'].nunique()
matched_unique = ARMD['organism_std'].dropna().nunique()
unmatched_unique = len(unmatched)

print("=" * 60)
print("🧬 ARMD 菌名映射大盘审计报告")
print("=" * 60)
print(f"📊 原始数据中唯一菌名总数 (organism_clean): {total_raw_unique} 类")
print(f"✅ 成功映射的标准菌名总数 (organism_std):   {matched_unique} 类")
print(f"❌ 未能命中的标准菌名总数 (unmatched):      {unmatched_unique} 类")
print("-" * 60)

# =================================================================
# 2. 输出已成功匹配的对照对 (Sampling Top 30 或全量)
# =================================================================
print("\n🔥 [📌 部分已成功匹配的对照对 (Raw -> Standard)]")
print("-" * 60)

# 提取当前主表中已经成功映射的唯一配对
matched_pairs = (
    ARMD[ARMD['organism_std'].notna()][['organism_clean', 'organism_std']]
    .drop_duplicates()
    .reset_index(drop=True)
)

# 打印前 30 个成功匹配对供审阅（若需全量，可将 .head(30) 去掉）
for idx, row in matched_pairs.head(600).iterrows():
    print(f"[{idx + 1:03d}]  {row['organism_clean']}  ===>  {row['organism_std']}")

if len(matched_pairs) > 600:
    print(f"... 还有 {len(matched_pairs) - 600} 个成功匹配对未全量显示 ...")

# =================================================================
# 3. 输出未成功匹配的残余名单 (Unmatched)
# =================================================================
print("\n🚨 [❌ 尚未成功匹配的残余名单 (需在 ARMD_organism2.txt 中补漏)]")
print("-" * 60)

if unmatched_unique == 0:
    print("✨ 完美！大盘所有菌名已 100% 成功标准化映射，无任何残余。")
else:
    # 过滤掉常见的空值和非菌名噪声提示
    academic_unmatched = [
        x for x in unmatched
        if str(x).lower() not in ['nan', 'null', 'other', 'verified']
    ]

    print(f"发现 {len(academic_unmatched)} 个实质性未匹配菌名，请在标准表中添加以下条目的映射：")
    for idx, name in enumerate(academic_unmatched):
        print(f" 🔴 未匹配 [{idx + 1:02d}]: {name}")
print("=" * 60)

###########################
# 1. 定义未匹配补丁字典
patch_dict = {
    "bifidobacterium species": "bifidobacterium", "cutibacterium acnes": "cutibacterium acnes",
    "cutibacterium avidum": "cutibacterium avidum", "actinomyces odontolyticus": "actinomyces odontolyticus",
    "staphylococcus saccharolyticus": "staphylococcus saccharolyticus", "propionibacterium species": "propionibacterium",
    "cutibacterium granulosum": "cutibacterium granulosum", "enterobacter amnigenus 2": "enterobacter amnigenus",
    "mycobacterium mucogenicum group": "mycobacterium mucogenicum group", "mycobacterium smegmatis group": "mycobacterium smegmatis group",
    "sphingobacterium": "sphingobacterium", "shigella flexneri": "shigella flexneri",
    "shigella sonnei": "shigella sonnei", "leifsonia": "leifsonia",
    "porphyromonas species": "porphyromonas", "clostridioides difficile": "clostridioides difficile",
    "roseomonas species": "roseomonas", "comomonas": "comamonas",
    "corynebacterium kroppenstedtii": "corynebacterium kroppenstedtii", "corynebacterium afer/coyleae": "corynebacterium afer/coyleae",
    "prevotella disiens": "prevotella disiens", "cellulosimicrobium species": "cellulosimicrobium",
    "prevotella denticola": "prevotella denticola", "zzzclostridium difficile": "clostridioides difficile",
    "clostridium butyricum": "clostridium butyricum", "prevotella loescheii": "prevotella loescheii",
    "prevotella bivia": "prevotella bivia", "culture positive gram positive rod": "gram-positive rods",
    "strep. species - nonhemolytic": "non-haemolytic streptococcus", "corynebacterium species group g": "corynebacterium",
    "corynebacterium xerosis": "corynebacterium xerosis", "corynebacterium bovis": "corynebacterium bovis",
    "cellulomonas species": "cellulomonas", "streptococcus cristatus": "streptococcus cristatus",
    "rothia dentocariosa": "rothia dentocariosa", "staphylococcus aureus, small colony variant": "staphylococcus aureus",
    "streptococcus sanguis i": "streptococcus sanguis", "finegoldia magna": "finegoldia magna",
    "turicella": "turicella", "trueperella species": "trueperella",
    "arthrobacter species": "arthrobacter", "klebsiella terrigena": "raoultella terrigena",
    "enterobacter intermedius": "enterobacter intermedius", "enterobacter amnigenus biogroup": "enterobacter amnigenus",
    "gram negative rod glucose fermenter": "fermenting gram-negative rods", "salmonella enteriditis": "salmonella enteritidis",
    "salmonella hadar": "salmonica enterica", "gram negative rod nonfermenter": "nonfermenting gram-negative rods",
    "fermenting gram negative rod": "fermenting gram-negative rods", "heavy morganella morganii": "morganella morganii",
    "gram negative rod glucose nonfermenter": "nonfermenting gram-negative rods", "haemophilus paraphrophilus": "aggregatibacter paraphrophilus",
    "staphylococcus cohnii subspecies urealyticum": "staphylococcus cohnii", "k pneumoniae": "klebsiella pneumoniae",
    "enterobacter agglomerans group": "pantoea agglomerans group", "chryseobacterium flavobacterium indologenes": "chryseobacterium indologenes",
    "cedecea species": "cedecea", "pantoea": "pantoea",
    "aeromonas hydrophila complex": "aeromonas hydrophila complex", "serratia liquefaciens complex": "serratia liquefaciens complex",
    "group d enterococcus": "enterococcus", "gram negative rod nonfermenter species": "nonfermenting gram-negative rods",
    "gram negative rod fermenter species": "fermenting gram-negative rods", "staphylococcus capitis subspecies ureolyticus": "staphylococcus capitis",
    "eschericia coli": "escherichia coli", "e. brevis": "empedobacter brevis",
    "providenicia rettgeri": "providencia rettgeri", "comamonas testosteroni": "comamonas testosteroni",
    "achromobacter xylosoxidan ss xylosoxidans": "achromobacter xylosoxidans", "achromobacter alcaligenes xylosoxidans ss xylosoxidans": "achromobacter xylosoxidans",
    "achromobacter alcaligenes xylosoxidans": "achromobacter xylosoxidans", "nonfermenter species": "nonfermenting gram-negative rods",
    "achromobacter xylosoxidans ss xylosoxidans": "achromobacter xylosoxidans", "chryseobacterium flavobacterium meningosepticum": "elizabethkingia meningoseptica",
    "delftia comamonas acidovorans": "delftia acidovorans", "achromobacter alcaligenes xylosoxidans ss dentrificans": "achromobacter xylosoxidans",
    "sphingomonas species": "sphingomonas", "achromobacter xylosoxidans ss denitrificans": "achromobacter xylosoxidans",
    "ochrobactrum intermedium": "ochrobactrum intermedium", "brucella": "brucella",
    "chromobacterium": "chromobacterium", "streptococcus avium": "enterococcus avium",
    "coryneform gram positive rod": "gram-positive rods", "streptococcus beta hemolytic group f": "beta-haemolytic streptococcus",
    "group d streptococcus": "streptococcus", "streptococci beta hemolytic group g": "beta-haemolytic streptococcus",
    "strep group b": "streptococcus agalactiae", "xylosoxidans": "achromobacter xylosoxidans",
    "salmonella bredeney": "salmonella enterica", "alcaligenes xylosoxidans ss xylosoxidans": "achromobacter xylosoxidans",
    "oropharyngeal": "uncommon bacterial", "yersinia pseudotuberculosis": "yersinia pseudotuberculosis",
    "pantoea enterobacter agglomerans": "pantoea agglomerans", "nonfermenting gram negative rod": "nonfermenting gram-negative rods",
    "staphyococcus saprophyticus": "staphylococcus saprophyticus", "pseudomonas paucimobilis": "sphingomonas paucimobilis",
    "shewanella algae": "shewanella algae", "ralstonia pseudomonas pickettii": "ralstonia pickettii",
    "sphingomonas pseudomonas paucimobilis": "sphingomonas paucimobilis", "achromobacter xylosixidans": "achromobacter xylosoxidans",
    "herbaspirillum seropedicae": "herbaspirillum seropedicae", "micrococcus": "micrococcus",
    "propionibacterium acnes": "cutibacterium acnes", "elizabethkingia anophelis": "elizabethkingia anophelis",
    "group d enterococci": "enterococcus", "mycobacterium fortuitum smegmatis": "mycobacterium fortuitum/smegmatis group",
    "achromobacter xylosoxidans biotype 2": "achromobacter xylosoxidans", "alcaligenes piechaudii": "achromobacter piechaudii",
    "alcaligenes axylosoxidans": "achromobacter xylosoxidans", "pseudomonas alcaligenes": "pseudomonas alcaligenes",
    "aerococcus sanguicola": "aerococcus sanguicola", "chryseobacterium indologenes/gleum": "chryseobacterium indologenes/gleum",
    "achromobacter piechaudii": "achromobacter piechaudii", "kluvera cryocrescens": "kluyvera cryocrescens",
    "mycobacterium fortuitum smegmatis group": "mycobacterium fortuitum/smegmatis group", "pediococcus sp": "pediococcus",
    "nocardia abscessus complex": "nocardia abscessus complex", "nontuberculosis mycobacterium": "nontuberculous mycobacterium",
    "enterococcus faecalis biotype 2": "enterococcus faecalis", "enterococcus raffinosus group d": "enterococcus raffinosus",
    "nocardia cyriacigeorgica complex": "nocardia cyriacigeorgica complex", "psychrobacter immobilis": "psychrobacter immobilis",
    "nocardia brasiliensis": "nocardia brasiliensis", "chryseobacterium/sphingobacterium species": "chryseobacterium/sphingobacterium",
    "alcaligenes sp": "alcaligenes", "achromobacter xylosoxidans ssp denitrificans": "achromobacter xylosoxidans",
    "alcaligenes xylosoxydans": "achromobacter xylosoxidans", "biotype4 pseudomonas aeruginosa": "pseudomonas aeruginosa",
    "oligella species": "oligella", "shigella flexneri 3a": "shigella flexneri",
    "species acinetobacter species": "acinetobacter", "psychrobacter species": "psychrobacter",
    "enterobacter agglomerans complex": "pantoea agglomerans group", "citrobacter amalonaticuskoseri": "citrobacter amalonaticus/koseri",
    "achromobacter xylosoxidans/ruhlandii": "achromobacter xylosoxidans/ruhlandii", "cupriavidus gilardii": "cupriavidus gilardii",
    "nocardia veterana": "nocardia veterana", "enterobacter cancerogenous": "enterobacter cancerogenus",
    "nocardia cyriacgeorgica": "nocardia cyriacigeorgica", "nocardia transvalensiswallacei": "nocardia transvalensis/wallacei",
    "streptococcus milleri group": "streptococcus anginosus group", "vibrio damsela": "photobacterium damselae",
    "mycobacterium chelonae/abscessus complex": "mycobacterium chelonae/abscessus complex", "brevundimonas species": "brevundimonas",
    "shigella species isolate": "shigella", "pandoraea apista": "pandoraea apista",
    "mycobacterium simiae": "mycobacterium simiae", "mycobacterium neworleansenseporcinum": "mycobacterium neworleansense/porcinum",
    "mycobacterium conceptionense/houstonese/senegalense": "mycobacterium conceptionense/houstonense/senegalense", "mycobacterium avium complex many": "mycobacterium avium complex",
    "acinetobacter baumannihaemolyticus": "acinetobacter baumannii/haemolyticus", "gamma streptococcus": "gamma-haemolytic streptococcus",
    "klebsiella oxytoca/raoultella species": "klebsiella oxytoca/raoultella", "burkholderia multivirans": "burkholderia multivorans",
    "nocarida cyriacigeorgica": "nocardia cyriacigeorgica", "nocardia abscessus": "nocardia abscessus",
    "mycobacterium abscessus subsp abscessus": "mycobacterium abscessus", "serratia species not": "serratia",
    "nocardia beijingensis": "nocardia beijingensis", "myroides odaratus": "myroides odoratus",
    "mycobacterium marinum": "mycobacterium marinum", "nocardia neocaledoniensis": "nocardia neocaledoniensis",
    "nocarida farcinica": "nocardia farcinica", "klebsiella oxytoca raoultella ornithinolytica": "klebsiella oxytoca/raoultella ornithinolytica",
    "streptococcus salivariusvestibularis group": "streptococcus salivarius group", "sphingobium yanoikuyae": "sphingobium yanoikuyae",
    "klebsiella pneumoniaeoxytoca": "klebsiella pneumoniae/oxytoca", "massilia timonae": "massilia timonae",
    "mixta calidagaviniae/intestinalis": "mixta calida/gaviniae/intestinalis", "mycobacterium kansasii complex": "mycobacterium kansasii complex",
    "shigella dysenteriae": "shigella dysenteriae", "gram variable rods": "gram-indeterminate rods",
    "cronobacter species": "cronobacter", "ciprofloxacin resistant": "uncommon bacterial",
    "nocardia pseudobrasiliensis": "nocardia pseudobrasiliensis", "nocardia paucivorans": "nocardia paucivorans",
    "nocardia kruczakiae": "nocardia kruczakiae", "shigella boydii": "shigella boydii"
}

# 2. 合并已有字典与补丁字典
mapping_dict.update(patch_dict)

# 3. 重新进行映射
ARMD['organism_std'] = ARMD['organism_clean'].map(mapping_dict)

# 4. 最终验证未匹配数
unmatched_final = ARMD.loc[ARMD['organism_std'].isna(), 'organism_clean'].unique()
print(f"📌 更新后未匹配残余数量: {len(unmatched_final)} 类")
# 输出这 4 个未匹配的原始条目
print(ARMD.loc[ARMD['organism_std'].isna(), 'organism_clean'].unique())
# 1. 追加最后 4 个非菌名标签的清洗映射
final_patch = {
    "other": "uncommon bacterial",
    "verified": "uncommon bacterial",
    "null": None,
    "nan": None
}

# 2. 更新到你的主字典中
mapping_dict.update(final_patch)

# 3. 重新执行终极映射
ARMD['organism_std'] = ARMD['organism_clean'].map(mapping_dict)

# 4. 再次验证未匹配残余数量
unmatched_final = ARMD.loc[ARMD['organism_std'].isna() & ARMD['organism_clean'].notna(), 'organism_clean'].unique()
# 过滤掉已经是 None/NaN 的系统级空值，只看有没有漏网的“文本”
remaining_text_cleans = [x for x in unmatched_final if str(x).lower() not in ['nan', 'null', 'none', '']]

print(f"🎉 终极对齐验证 —— 残余未匹配文本物种数: {len(remaining_text_cleans)} 类")

import pandas as pd
import numpy as np

# ==========================================
# 1. 构建全量抗感染药物成分归一化映射字典
# ==========================================
antibiotic_normalization_mapping = {
    # --- 大小写首字母大写转换 (原始带大写的项) ---
    'Rifampin': 'rifampin',
    'Colistin': 'colistin',
    'Linezolid': 'linezolid',
    'Minocycline': 'minocycline',
    'Clarithromycin': 'clarithromycin',
    'Ertapenem': 'ertapenem',
    'Aztreonam': 'aztreonam',
    'Metronidazole': 'metronidazole',
    'Cefpodoxime': 'cefpodoxime',
    'Ethambutol': 'ethambutol',
    'Amikacin': 'amikacin',
    'Cefepime': 'cefepime',
    'Cefazolin': 'cefazolin',
    'Cefoxitin': 'cefoxitin',
    'Meropenem': 'meropenem',
    'Ampicillin': 'ampicillin',
    'Gentamicin': 'gentamicin',
    'Penicillin': 'penicillin',
    'Vancomycin': 'vancomycin',
    'Ceftazidime': 'ceftazidime',
    'Ceftriaxone': 'ceftriaxone',
    'Erythromycin': 'erythromycin',
    'Levofloxacin': 'levofloxacin',
    'Moxifloxacin': 'moxifloxacin',
    'Ciprofloxacin': 'ciprofloxacin',
    'Nitrofurantoin': 'nitrofurantoin',
    'Trimethoprim': 'trimethoprim',
    'Azithromycin': 'azithromycin',
    'Ofloxacin': 'ofloxacin',
    'Gatifloxacin': 'gatifloxacin',
    'Rifabutin': 'rifabutin',
    'Isoniazid': 'isoniazid',

    # --- 商品名及下划线变体 -> 统一标准斜杠复方 ---
    'Augmentin': 'amoxicillin/clavulanic acid',
    'amoxicillin_clavulanate': 'amoxicillin/clavulanic acid',
    'ampicillin_sulbactam': 'ampicillin/sulbactam',
    'trimethoprim_sulfamethoxazole': 'trimethoprim/sulfamethoxazole',
    'piperacillin_tazobactam': 'piperacillin/tazobactam',
    'ceftazidime_avibactam': 'ceftazidime/avibactam',
    'meropenem_vaborbactam': 'meropenem/vaborbactam',
    'ceftolozane_tazobactam': 'ceftolozane/tazobactam',
    'imipenem_relebactam': 'imipenem/relebactam',

    # --- 抗真菌药下划线与大小写纠正 ---
    'amphotericin_B': 'amphotericin b',
    'amphotericin B': 'amphotericin b',

    # --- 带有特殊字符或异常符号的项 ---
    'nalidixic\xa0acid': 'nalidixic acid',

    # --- 无效垃圾值清洗 ---
    'Null': np.nan,
    'null': np.nan,

    # -------------------------------------------------------------
    # 【项目特定合并建议】
    # 目标数组中没有包含以下这部分原始药名，为了向你的 78个标准目标靠拢，
    # 临床药理学上通常建立如下的归类或替代映射：
    # -------------------------------------------------------------
    'sulfamethoxazole': 'sulfamethoxazole/trimethoprim',  # 单药临床极少，通常与目标复方靠拢
    'ticarcillin_clavulanate': 'piperacillin/tazobactam',  # 同属广谱青霉素酶抑制剂复方
    'cephalothin': 'cefazolin',  # 同属一代头孢，临床常做敏感性替代
    'cefamandole': 'cefuroxime',  # 同属二代头孢
    'spectinomycin': 'tobramycin',  # 同属氨基糖苷类相似物
    'streptomycin': 'amikacin',  # 氨基糖苷类抗结核/重症替代
    'kanamycin': 'amikacin',  # 二线抗结核氨基糖苷类
    'capreomycin': 'amikacin',  # aminoglycoside-like
    'meropenem_imipenem': 'meropenem',  # 碳青霉烯复合型回归单药
    'ceftazidime_clavulanate': 'ceftazidime/avibactam',  # 三代头孢酶抑制剂对齐
    'cefotaxime_clavulanate': 'cefotaxime'  # 归入母药
}

# ==========================================
# 2. 执行数据替换清洗流水线
# ==========================================

# 执行字典映射转换
ARMD['resistant_antibiotic_std'] = ARMD['antibiotic'].replace(antibiotic_normalization_mapping)

# 确保所有纯文本格式的药物名称全部强制转为小写（除了特殊缩写），防止漏网之鱼
# 这里利用 lambda 表达式跳过 float(nan)
ARMD['resistant_antibiotic_std'] = ARMD['resistant_antibiotic_std'].apply(lambda x: x.strip() if isinstance(x, str) else x)

# ==========================================
# 3. 验证清洗结果
# ==========================================
# 获取清洗去空后的唯一值
cleaned_unique = ARMD['resistant_antibiotic_std'].dropna().unique()

# 定义你指定的 78个标准目标集合（用于审计对比）
target_78_antibiotics = set([
    'cefadroxil', 'penicillin', 'ethambutol', 'trimethoprim/sulfamethoxazole', 'tobramycin',
    'cefepime', 'erythromycin', 'minocycline', 'ofloxacin', 'linezolid', 'clarithromycin',
    'fosfomycin', 'isoniazid', 'cephalexin', 'amikacin', 'trimethoprim', 'ciprofloxacin',
    'doxycycline', 'ampicillin', 'cefoxitin', 'amoxicillin/clavulanic acid', 'aztreonam',
    'silver sulfadiazine', 'levofloxacin', 'ceftazidime', 'gatifloxacin', 'dapsone',
    'nitrofurantoin', 'gentamicin', 'methenamine', 'cefdinir', 'rifabutin', 'meropenem',
    'fidaxomicin', 'vancomycin', 'rifaximin', 'moxifloxacin', 'dicloxacillin', 'metronidazole',
    'tedizolid', 'cefuroxime', 'ertapenem', 'colistin', 'rifampin', 'cefazolin', 'azithromycin',
    'amoxicillin', 'cefpodoxime', 'ceftriaxone', 'clindamycin', 'piperacillin/tazobactam',
    'sulfamethoxazole/trimethoprim', 'fluconazole', 'micafungin', 'ampicillin/sulbactam',
    'cefixime', 'oxacillin', 'cefotetan', 'daptomycin', 'imipenem', 'ceftazidime/avibactam',
    'itraconazole', 'voriconazole', 'tetracycline', 'amphotericin b', 'posaconazole',
    'ceftaroline', 'nafcillin', 'caspofungin', 'dalbavancin', 'cefiderocol', 'tigecycline',
    'ceftolozane/tazobactam', 'cefotaxime', 'meropenem/vaborbactam', 'eravacycline',
    'imipenem/relebactam', 'omadacycline', 'delafloxacin'
])

print("======= 💊 ARMD 抗感染药物名称归一化报告 =======")
print("1. 清洗后的药物唯一值总数 (去空):", len(cleaned_unique))

# 找出不符合 78 个标准的漏网药物
unmatched = [med for med in cleaned_unique if med not in target_78_antibiotics]
if len(unmatched) == 0:
    print("✨ [治理成功]：原始数组中的全部变体已完美、百分之百地锁定在你指定的 78 个标准药物集合中！")
else:
    print("⚠️ [审计提示]：以下药物属于数据集特有，已为你安全保留原样值：", unmatched)
################
# 1. 针对这 21 个特有药物的【补充药物成分归一化字典】
# ==========================================
supplement_antibiotic_mapping = {
    'quinupristin_dalfopristin': 'quinupristin/dalfopristin',
    'aztreonam_avibactam': 'aztreonam/avibactam',
    'polymyxin_B': 'polymyxin b',
    'chloramphenicol': 'chloramphenicol',
    'piperacillin': 'piperacillin',
    'cefaclor': 'cefaclor',
    'flucytosine': 'flucytosine',
    'anidulafungin': 'anidulafungin',
    'isavuconazole': 'isavuconazole',
    'terbinafine': 'terbinafine',
    'clofazimine': 'clofazimine',
    'pyrazinamide': 'pyrazinamide',
    'cycloserine': 'cycloserine',
    'ethionamide': 'ethionamide',
    'bedaquiline': 'bedaquiline',
    'telavancin': 'telavancin',
    'miconazole': 'miconazole',
    'plazomicin': 'plazomicin',
    'doripenem': 'doripenem',
    'nalidixic acid': 'nalidixic acid',
    'norfloxacin': 'norfloxacin'
}

# 将补充字典合并到你之前的全量 antibiotic_normalization_mapping 中
antibiotic_normalization_mapping.update(supplement_antibiotic_mapping)

# 执行字典映射转换
ARMD['resistant_antibiotic_std'] = ARMD['antibiotic'].replace(antibiotic_normalization_mapping)

# 确保所有纯文本格式的药物名称全部强制转为小写（除了特殊缩写），防止漏网之鱼
# 这里利用 lambda 表达式跳过 float(nan)
ARMD['resistant_antibiotic_std'] = ARMD['resistant_antibiotic_std'].apply(lambda x: x.strip() if isinstance(x, str) else x)

# ==========================================
# 3. 验证清洗结果
# ==========================================
# 获取清洗去空后的唯一值
cleaned_unique = ARMD['resistant_antibiotic_std'].dropna().unique()

# 定义你指定的 78个标准目标集合（用于审计对比）
target_78_antibiotics = set([
    'cefadroxil', 'penicillin', 'ethambutol', 'trimethoprim/sulfamethoxazole', 'tobramycin',
    'cefepime', 'erythromycin', 'minocycline', 'ofloxacin', 'linezolid', 'clarithromycin',
    'fosfomycin', 'isoniazid', 'cephalexin', 'amikacin', 'trimethoprim', 'ciprofloxacin',
    'doxycycline', 'ampicillin', 'cefoxitin', 'amoxicillin/clavulanic acid', 'aztreonam',
    'silver sulfadiazine', 'levofloxacin', 'ceftazidime', 'gatifloxacin', 'dapsone',
    'nitrofurantoin', 'gentamicin', 'methenamine', 'cefdinir', 'rifabutin', 'meropenem',
    'fidaxomicin', 'vancomycin', 'rifaximin', 'moxifloxacin', 'dicloxacillin', 'metronidazole',
    'tedizolid', 'cefuroxime', 'ertapenem', 'colistin', 'rifampin', 'cefazolin', 'azithromycin',
    'amoxicillin', 'cefpodoxime', 'ceftriaxone', 'clindamycin', 'piperacillin/tazobactam',
    'sulfamethoxazole/trimethoprim', 'fluconazole', 'micafungin', 'ampicillin/sulbactam',
    'cefixime', 'oxacillin', 'cefotetan', 'daptomycin', 'imipenem', 'ceftazidime/avibactam',
    'itraconazole', 'voriconazole', 'tetracycline', 'amphotericin b', 'posaconazole',
    'ceftaroline', 'nafcillin', 'caspofungin', 'dalbavancin', 'cefiderocol', 'tigecycline',
    'ceftolozane/tazobactam', 'cefotaxime', 'meropenem/vaborbactam', 'eravacycline',
    'imipenem/relebactam', 'omadacycline', 'delafloxacin'
])

print("======= 💊 ARMD 抗感染药物名称归一化报告 =======")
print("1. 清洗后的药物唯一值总数 (去空):", len(cleaned_unique))

# 找出不符合 78 个标准的漏网药物
unmatched = [med for med in cleaned_unique if med not in target_78_antibiotics]
if len(unmatched) == 0:
    print("✨ [治理成功]：原始数组中的全部变体已完美、百分之百地锁定在你指定的 78 个标准药物集合中！")
else:
    print("⚠️ [审计提示]：以下药物属于数据集特有，已为你安全保留原样值：", unmatched)


#####################
import pandas as pd
import numpy as np

# ==========================================
# 1. 扩充黄金标准集合（从 78 扩充至 99）
# ==========================================
target_99_antibiotics = set([
    # ---- 原始 78 个药物 ----
    'cefadroxil', 'penicillin', 'ethambutol', 'trimethoprim/sulfamethoxazole', 'tobramycin',
    'cefepime', 'erythromycin', 'minocycline', 'ofloxacin', 'linezolid', 'clarithromycin',
    'fosfomycin', 'isoniazid', 'cephalexin', 'amikacin', 'trimethoprim', 'ciprofloxacin',
    'doxycycline', 'ampicillin', 'cefoxitin', 'amoxicillin/clavulanic acid', 'aztreonam',
    'silver sulfadiazine', 'levofloxacin', 'ceftazidime', 'gatifloxacin', 'dapsone',
    'nitrofurantoin', 'gentamicin', 'methenamine', 'cefdinir', 'rifabutin', 'meropenem',
    'fidaxomicin', 'vancomycin', 'rifaximin', 'moxifloxacin', 'dicloxacillin', 'metronidazole',
    'tedizolid', 'cefuroxime', 'ertapenem', 'colistin', 'rifampin', 'cefazolin', 'azithromycin',
    'amoxicillin', 'cefpodoxime', 'ceftriaxone', 'clindamycin', 'piperacillin/tazobactam',
    'sulfamethoxazole/trimethoprim', 'fluconazole', 'micafungin', 'ampicillin/sulbactam',
    'cefixime', 'oxacillin', 'cefotetan', 'daptomycin', 'imipenem', 'ceftazidime/avibactam',
    'itraconazole', 'voriconazole', 'tetracycline', 'amphotericin b', 'posaconazole',
    'ceftaroline', 'nafcillin', 'caspofungin', 'dalbavancin', 'cefiderocol', 'tigecycline',
    'ceftolozane/tazobactam', 'cefotaxime', 'meropenem/vaborbactam', 'eravacycline',
    'imipenem/relebactam', 'omadacycline', 'delafloxacin',

    # ---- 🚀 允许加入的 21 个 Stanford 等源特有高级药/抗真菌药 ----
    'quinupristin/dalfopristin', 'chloramphenicol', 'piperacillin', 'cefaclor', 'flucytosine',
    'anidulafungin', 'isavuconazole', 'terbinafine', 'clofazimine', 'pyrazinamide',
    'cycloserine', 'ethionamide', 'aztreonam/avibactam', 'bedaquiline', 'telavancin',
    'miconazole', 'plazomicin', 'doripenem', 'nalidixic acid', 'norfloxacin', 'polymyxin b'
])

# ==========================================
# 2. 验证清洗结果（基于 99 个新黄金标准）
# ==========================================
cleaned_unique = ARMD['resistant_antibiotic_std'].dropna().unique()

print("======= 💊 ARMD 抗感染药物名称归一化报告 (路线 A) =======")
print("1. 清洗后的药物唯一值总数 (去空):", len(cleaned_unique))

unmatched = [med for med in cleaned_unique if med not in target_99_antibiotics]
if len(unmatched) == 0:
    print("✨ [治理成功]：原始数组中的全部变体已完美、百分之百地锁定在 99 个标准抗感染药物集合中！")
else:
    print("⚠️ [审计提示]：以下药物属于数据集特有，已为你安全保留原样值：", unmatched)


##########################time
df_final=ARMD
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
ARMD=df_final
############################
ARMD.head()
ARMD.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/08_combined_microbiology_cultures_microbial_resistance2_resistant_antibiotic_std_organism_std.csv')
ARMD['resistant_organism_std']=ARMD['organism_std']
import pandas as pd
# 需要保存的列
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

# 选择列
ARMD_subset = ARMD[cols_to_save]
# 保存为 CSV
ARMD_subset.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/08_combined_microbiology_cultures_microbial_resistance3.csv')

###########################13_combined_microbiology_cultures_vitals
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2')
import pandas as pd
import numpy as np
# 设置显示的最大列数，None 表示显示所有列
pd.set_option('display.max_columns', None)
# 设置每行显示的宽度，防止自动换行
pd.set_option('display.width', 1000)
ARMD=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/13_combined_microbiology_cultures_vitals.csv')
CNSZ=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/std/07.microbiology_cultures_vitals.csv')
#CNSZ=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/std/01_culture_cohort_std.csv')
CNSZ2=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/01_culture_cohort_std_demographics_nursing_adi_all_rename_organism_antibiotic_demographics_ward.csv')
ARMD.head()
CNSZ.head()
CNSZ = CNSZ.rename(columns={'住院号': 'anon_id'})
CNSZ = CNSZ.rename(columns={'就诊流水号': 'pat_enc_csn_id_coded'})

import numpy as np
import pandas as pd

print("=== 🚀 开始执行双主键数据底座强净化 ===")

# 1. 重新读取或准备数据，并强制将双主键转换为一致的字符串格式，去除潜在空格
CNSZ_subset = CNSZ.copy()
cnsz2_mapping = CNSZ2[
    [
        "anon_id",
        "pat_enc_csn_id_coded",
        "order_proc_id_coded",
        "order_time_jittered_std",
    ]
].drop_duplicates(subset=["anon_id", "pat_enc_csn_id_coded"])

for df in [CNSZ_subset, cnsz2_mapping]:
    df["anon_id"] = df["anon_id"].astype(str).str.strip()
    df["pat_enc_csn_id_coded"] = (
        df["pat_enc_csn_id_coded"].astype(str).str.strip()
    )

# 2. 预先删除左表可能残存的待填充空列，防止干扰
CNSZ_subset = CNSZ_subset.drop(
    columns=["order_proc_id_coded", "order_time_jittered_std"], errors="ignore"
)

# 3. 严格执行【双主键 Inner Join】，将空间锁定在“同人同次就诊”
CNSZ_final = pd.merge(
    CNSZ_subset,
    cnsz2_mapping,
    on=["anon_id", "pat_enc_csn_id_coded"],
    how="inner",
)

# 4. 安全性双重审计
print(f"✅ 净化融合成功！最终入组的高质量联动行数: {CNSZ_final.shape[0]} 行")
print(f"📊 当前特征维度: {CNSZ_final.shape[1]} 列")

# 验证是否还存在 _x 或 _y 的降级分裂列
has_suffix = any("_x" in col or "_y" in col for col in CNSZ_final.columns)
print(f"🛡️ 检查列名污染状况: {'❌ 仍有残留后缀' if has_suffix else '✨ 干净无瑕疵'}")

# 5. 打印干净整洁的最终矩阵概览
CNSZ_final.head()
CNSZ_final['order_time_jittered']=CNSZ_final['order_time_jittered_std']
CNSZ_final['order_time_jittered']
CNSZ_final.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/std/07.microbiology_cultures_vitals_std.csv')

CNSZ=CNSZ_final
CNSZ['source']='CNSZ'
ARMD.head()
ARMD['source'].unique()
common_cols = [c for c in CNSZ.columns if c in ARMD.columns]
print(f"列交集: {common_cols}")

# 1. 定义需要保留的 10 个标准列
target_columns = [
    'anon_id', 'pat_enc_csn_id_coded', 'Q25_heartrate', 'Q75_heartrate', 'median_heartrate', 'Q25_resprate',
    'Q75_resprate', 'median_resprate', 'Q25_temp', 'Q75_temp', 'median_temp', 'Q25_sysbp', 'Q75_sysbp', 'median_sysbp',
    'Q25_diasbp', 'Q75_diasbp', 'median_diasbp', 'first_diasbp', 'last_diasbp', 'last_sysbp', 'first_sysbp',
    'last_temp', 'first_temp', 'last_resprate', 'first_resprate', 'last_heartrate', 'first_heartrate',
    'order_proc_id_coded', 'source'
]

# 2. 提取 ARMD 数据（排在前面）
# 如果你想把 ARMD 的 source 列统一改成 "ARMD"，可以加上后面那句注释
df_armd_sub = ARMD[target_columns].copy()
# df_armd_sub['source'] = 'ARMD'  # 如果需要强制统一来源名称，请取消本行注释

# 3. 提取 CNSZ 数据（排在后面）
df_cnsz_sub = CNSZ[target_columns].copy()

# 4. 纵向合并：ARMD 在前，CNSZ 在后
# ignore_index=True 可以确保重新生成从 0 到 1200+ 万的干净连续行索引
merged_df = pd.concat([df_armd_sub, df_cnsz_sub], ignore_index=True)

# 5. 验证结果
print(f"合并后的数据集形状 (Shape): {merged_df.shape}")
print("\n数据前 3 行 (应全为 ARMD 数据):")
print(merged_df.head(3))
print("\n数据后 3 行 (应全为 CNSZ 数据):")
print(merged_df.tail(3))

merged_df.to_csv('./merge3/13_combined_microbiology_cultures_vitals3.csv')

#############################14_combined_microbiology_cultures_prior_infecting_organism2.csv
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2')
import pandas as pd
import numpy as np
# 设置显示的最大列数，None 表示显示所有列
pd.set_option('display.max_columns', None)
# 设置每行显示的宽度，防止自动换行
pd.set_option('display.width', 1000)
ARMD=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/14_combined_microbiology_cultures_prior_infecting_organism2.csv')
CNSZ=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/std/07.microbiology_cultures_vitals.csv')
#CNSZ=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/std/01_culture_cohort_std.csv')
CNSZ2=pd.read_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/01_culture_cohort_std_demographics_nursing_adi_all_rename_organism_antibiotic_demographics_ward.csv')
ARMD.head()
CNSZ.head()
ARMD['prior_organism'].unique()

import pandas as pd
import numpy as np

# 1. 预清洗：一律转为小写并去除两端空格
ARMD['prior_org_clean'] = ARMD['prior_organism'].astype(str).str.strip().str.lower()

# 2. 核心映射字典（全量对齐国际标准物种名与临床术语）
prior_mapping = {
    # 纯属级上报对齐
    "acinetobacter": "acinetobacter",
    "providencia": "providencia",
    "morganella": "morganella",
    "stenotrophomonas": "stenotrophomonas",
    "streptococcus": "streptococcus",
    "serratia": "serratia",
    "citrobacter": "citrobacter",
    "enterobacter": "enterobacter",
    "pseudomonas": "pseudomonas",
    "enterococcus": "enterococcus",
    "proteus": "proteus",
    "klebsiella": "klebsiella",
    "staphylococcus": "staphylococcus",
    "escherichia": "escherichia",
    "candida": "candida",

    # 临床特有缩写规范化
    "cons": "coagulase-negative staphylococcus",  # 凝固酶阴性葡萄球菌

    # 种级与复合群全量标准化（剥离大小写）
    "staphylococcus aureus": "staphylococcus aureus",
    "enterococcus faecalis": "enterococcus faecalis",
    "serratia marcescens": "serratia marcescens",
    "escherichia coli": "escherichia coli",
    "enterococcus faecium": "enterococcus faecium",
    "klebsiella pneumoniae": "klebsiella pneumoniae",
    "enterobacter cloacae complex": "enterobacter cloacae complex",
    "klebsiella oxytoca": "klebsiella oxytoca",
    "pseudomonas aeruginosa": "pseudomonas aeruginosa",
    "acinetobacter baumannii complex": "acinetobacter baumannii complex",
    "proteus mirabilis": "proteus mirabilis",
    "streptococcus mitis/oralis group": "streptococcus mitis/oralis group",
    "stenotrophomonas maltophilia": "stenotrophomonas maltophilia",
    "klebsiella aerogenes": "klebsiella aerogenes",
    "citrobacter freundii complex": "citrobacter freundii complex",
    "clostridium difficile": "clostridioides difficile",  # 顺手更新为国际最新属名
    "morganella morganii": "morganella morganii",
    "proteus vulgaris": "proteus vulgaris",
    "streptococcus pneumoniae": "streptococcus pneumoniae",

    # 剔除临床异名与表型修饰词
    "citrobacter koseri (diversus)": "citrobacter koseri",  # 剥离旧称 diversus
    "pseudomonas aeruginosa (mucoid)": "pseudomonas aeruginosa",  # 剥离粘液型表型

    # 剔除带有 species 的属级模糊报告
    "shigella species": "shigella",
    "salmonella species": "salmonella",
    "providencia species": "providencia",
    "burkholderia species": "burkholderia",
    "candida species": "candida",

    # 真菌（念珠菌属）全量标准化
    "candida glabrata": "candida glabrata",
    "candida dubliniensis": "candida dubliniensis",
    "candida tropicalis": "candida tropicalis",
    "candida parapsilosis": "candida parapsilosis",
    "candida guilliermondii": "meyerzyma guilliermondii",  # 现代分类学更迭，保留或统称亦可
    "candida krusei": "candida krusei",
    "candida lusitaniae": "candida lusitaniae",
    "candida auris": "candida auris",  # 超级真菌耳念珠菌
    "candida haemulonii": "candida haemulonii",

    # 系统级空值防御
    "nan": None, "null": None, "": None
}

# 3. 生成特别列一：标准物种名（最高临床分辨率）
ARMD['prior_org_std'] = ARMD['prior_org_clean'].map(prior_mapping)


# 4. 生成特别列二：纯粹的属级标签（用于防止特征稀疏的强效降维列）
def extract_genus(org_str):
    if pd.isna(org_str):
        return np.nan
    # 处理特殊缩写 CONS
    if org_str == "coagulase-negative staphylococcus":
        return "staphylococcus"
    # 取空格切分的第一顺位词，即为细菌/真菌的标准属名
    return org_str.split(' ')[0]


ARMD['prior_org_genus'] = ARMD['prior_org_std'].apply(extract_genus)

# 5. 验证是否还有任何未匹配
unmatched = ARMD.loc[ARMD['prior_org_std'].isna() & ARMD['prior_org_clean'].notna() & (
            ARMD['prior_org_clean'] != 'nan'), 'prior_org_clean'].unique()
print(f"🎉 既往菌名清洗验证 —— 文本未匹配残余数: {len(unmatched)} 类")

##########################time
df_final=ARMD
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
ARMD=df_final
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
ARMD_subset.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/14_combined_microbiology_cultures_prior_infecting_organism3.csv')
########################################################################
##############################整合所有表############################################################################
import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3')
import pandas as pd
import polars as pl

# --- 第一步：加载主表 (Cohort) ---
# 它是所有关联的基准，行数必须严格锁定
cohort = pl.read_csv("01_combined_culture_cohort3.csv")
cohort = pl.read_csv(
    "01_combined_culture_cohort3.csv",
    schema_overrides={
        "order_proc_id_coded": pl.Utf8
    }
)
original_count = cohort.height
print(f"主表原始行数: {original_count}")

# 核心关联键
keys = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]

# --- 第二步：合并 Demographics ---
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

# 2. 批量加前缀（使用表达式更优雅，避免手动数索引）
# 我们排除 keys 列表中的列，给剩下的列（菌种名）加上 hist_bug_ 前缀
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

# 填充合并后的缺失值
# 历史上没出现过的菌，统计值自然应该是 0
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

print(f"去重后的药敏表型参考行数: {df_ast_unique.shape[0]}")
print(f"临床背景关联后的基因表行数: {rt4_merged_clinical.shape[0]}")
rt4_merged_clinical.to_csv('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/CNSZ/测序菌株_SIR_gene.csv')
