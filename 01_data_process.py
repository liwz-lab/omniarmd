#Stanford,ECUH, UTSW and MGB
import os
import pandas as pd
Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_cohort.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/00_microbiology_cultures_cohort.csv')
UTSW1 = pd.read_csv('./ARMD-UTSW/microbiology_cultures_cohort.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df.to_csv('./merge/01_combined_culture_cohort.csv', index=False)


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_adi_scores.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/01_microbiology_cultures_adi_scores.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})
combined_df = pd.concat([Stanford1, ECUH1], ignore_index=True)
combined_df.to_csv('./merge/02_combined_microbiology_cultures_adi_scores.csv', index=False)

combined_df = pd.read_csv('./merge/01_combined_culture_cohort.csv')
MGB1 = pd.read_csv('./ARMD-MGB/microbiology_cohort_deid_tj_updated.csv')
MGB1['source'] = 'MGB'

MGB1 = MGB1.rename(columns={'order_time_jittered_utc_shifted': 'order_time_jittered'})

combined_df2 = pd.concat([combined_df, MGB1], ignore_index=True)
combined_df2.to_csv('./merge2/01_combined_culture_cohort2.csv', index=False)

Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_antibiotic_class_exposure.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/02_microbiology_cultures_antibiotic_class_exposure.csv')
UTSW1 = pd.read_csv('./ARMD-UTSW/microbiology_cultures_antibiotic_class_exposure.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df.to_csv('./merge/03_combined_microbiology_cultures_antibiotic_class_exposure.csv', index=False)


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_antibiotic_subtype_exposure.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/03_microbiology_cultures_antibiotic_subtype_exposure.csv')
UTSW1 = pd.read_csv('./ARMD-UTSW/microbiology_cultures_antibiotic_subtype_exposure.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df.to_csv('./merge/04_combined_microbiology_cultures_antibiotic_subtype_exposure.csv', index=False)


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_comorbidity.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/04_microbiology_cultures_comorbidity.csv')
UTSW1 = pd.read_csv('./ARMD-UTSW/microbiology_cultures_comorbidity.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df.to_csv('./merge/05_combined_microbiology_cultures_comorbidity.csv', index=False)


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_demographics.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/05_microbiology_cultures_demographics.csv')
UTSW1 = pd.read_csv('./ARMD-UTSW/microbiology_cultures_demographics.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df.to_csv('./merge/06_combined_microbiology_cultures_demographics.csv', index=False)


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_labs.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/06_microbiology_cultures_labs.csv')
UTSW1 = pd.read_csv('./ARMD-UTSW/microbiology_cultures_labs.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df.to_csv('./merge/07_combined_microbiology_cultures_labs.csv', index=False)


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_microbial_resistance.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/07_microbiology_cultures_microbial_resistance.csv')
UTSW1 = pd.read_csv('./ARMD-UTSW/microbiology_cultures_microbial_resistance.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df.to_csv('./merge/08_combined_microbiology_cultures_microbial_resistance.csv', index=False)


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_nursing_home_visits.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/08_microbiology_cultures_nursing_home_visits.csv')
UTSW1 = pd.read_csv('./ARMD-UTSW/microbiology_cultures_nursing_home_visits.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df.to_csv('./merge/09_combined_microbiology_cultures_nursing_home_visits.csv', index=False)


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_prior_med.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/010_microbiology_cultures_prior_med.csv')
UTSW1 = pd.read_csv('./ARMD-UTSW/microbiology_cultures_prior_med.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df.to_csv('./merge/10_combined_microbiology_cultures_prior_med.csv', index=False)


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_priorprocedures.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/011_microbiology_cultures_prior_procedures.csv')
UTSW1 = pd.read_csv('./ARMD-UTSW/microbiology_cultures_prior_procedures.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df.to_csv('./merge/11_combined_microbiology_cultures_prior_procedures.csv', index=False)


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_ward_info.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/012_microbiology_cultures_ward_info.csv')
UTSW1 = pd.read_csv('./ARMD-UTSW/microbiology_cultures_ward_info.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

Stanford1 = Stanford1.rename(columns={'order_time_jittered_utc': 'order_time_jittered'})

combined_df = pd.concat([Stanford1, ECUH1, UTSW1], ignore_index=True)
combined_df.to_csv('./merge/12_combined_microbiology_cultures_ward_info.csv', index=False)


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_vitals.csv')
ECUH1 = pd.read_csv('./ARMD-ECUH/013_microbiology_cultures_vitals.csv')

Stanford1['source'] = 'Stanford'
ECUH1['source'] = 'ECUH'

combined_df = pd.concat([Stanford1, ECUH1], ignore_index=True)
combined_df.to_csv('./merge/13_combined_microbiology_cultures_vitals.csv', index=False)


ECUH1 = pd.read_csv('./ARMD-ECUH/09_microbiology_cultures_prior_infecting_organism.csv')
UTSW1 = pd.read_csv('./ARMD-UTSW/microbiology_cultures_prior_infecting_organism.csv')

ECUH1['source'] = 'ECUH'
UTSW1['source'] = 'UTSW'

combined_df = pd.concat([ECUH1, UTSW1], ignore_index=True)
combined_df.to_csv('./merge/14_combined_microbiology_cultures_prior_infecting_organism.csv', index=False)


Stanford1 = pd.read_csv('./ARMD-Stanford/microbiology_cultures_implied_susceptibility.csv')

Stanford1['source'] = 'Stanford'

Stanford1.to_csv('./merge/15_Stanford_microbiology_cultures_implied_susceptibility.csv', index=False)


combined_df = pd.read_csv('./merge/01_combined_culture_cohort.csv')
MGB1 = pd.read_csv('./ARMD-MGB/microbiology_cohort_deid_tj_updated.csv')
MGB1['source'] = 'MGB'
MGB1['susceptibility'] = MGB1['CLSI_2022_pheno']

MGB1_renamed = MGB1.rename(columns={'order_time_jittered_utc_shifted': 'order_time_jittered'})

mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA

combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns].reset_index(drop=True)
MGB1_renamed = MGB1_renamed[final_columns].reset_index(drop=True)

final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)
final_df['susceptibility'] = final_df['susceptibility'].replace({
    'Susceptible dose dependent': 'Susceptible dose-dependent'
})

final_df.to_csv('./merge2/01_combined_culture_cohort2.csv', index=False)


combined_df = pd.read_csv('./merge/02_combined_microbiology_cultures_adi_scores.csv')
MGB1 = pd.read_csv('./ARMD-MGB/ADI_deid_tj.csv')
MGB1['source'] = 'MGB'

MGB1 = MGB1.rename(columns={'order_time_jittered_utc_shifted': 'order_time_jittered'})

final_df = pd.concat([combined_df, MGB1], ignore_index=True)
final_df.to_csv('./merge2/02_combined_microbiology_cultures_adi_scores2.csv', index=False)


combined_df = pd.read_csv('./merge/03_combined_microbiology_cultures_antibiotic_class_exposure.csv')
MGB1 = pd.read_csv('./ARMD-MGB/prior_abx_deid_tj.csv')
MGB1['source'] = 'MGB'

MGB1_renamed = MGB1.rename(columns={
    'drug_class': 'antibiotic_class',
    'last_dose_to_culture': 'time_to_culturetime',
    'order_time_jittered_utc_shifted': 'order_time_jittered'
})

extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in extra_cols:
    combined_df[c] = pd.NA

for c in combined_df.columns:
    if c not in MGB1_renamed.columns:
        MGB1_renamed[c] = pd.NA

MGB1_renamed = MGB1_renamed[combined_df.columns.tolist() + extra_cols]

combined_df = combined_df.reset_index(drop=True)
MGB1_renamed = MGB1_renamed.reset_index(drop=True)

final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)
final_df.to_csv('./merge2/03_combined_microbiology_cultures_antibiotic_class_exposure2.csv', index=False)


combined_df = pd.read_csv('./merge/04_combined_microbiology_cultures_antibiotic_subtype_exposure.csv')
MGB1 = pd.read_csv('./ARMD-MGB/prior_abx_deid_tj.csv')
MGB1['source'] = 'MGB'

MGB1_renamed = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered'
})

mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA

combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns].reset_index(drop=True)
MGB1_renamed = MGB1_renamed[final_columns].reset_index(drop=True)

final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)
final_df.to_csv('./merge2/04_combined_microbiology_cultures_antibiotic_subtype_exposure2.csv', index=False)


combined_df = pd.read_csv('./merge/05_combined_microbiology_cultures_comorbidity.csv')
MGB1 = pd.read_csv('./ARMD-MGB/comorbidity_deid_tj.csv')
MGB1['source'] = 'MGB'

MGB1 = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered',
    'category': 'comorbidity_component'
})

MGB1['comorbidity_component_start_days_culture'] = pd.NA
MGB1['comorbidity_component_end_days_culture'] = pd.NA

MGB1 = MGB1[combined_df.columns]

final_df = pd.concat([combined_df, MGB1], ignore_index=True)
final_df.to_csv('./merge2/05_combined_microbiology_cultures_comorbidity2.csv', index=False)


combined_df = pd.read_csv('./merge/06_combined_microbiology_cultures_demographics.csv')
MGB1 = pd.read_csv('./ARMD-MGB/demographics_deid_tj.csv')
MGB1['source'] = 'MGB'

MGB1 = MGB1[combined_df.columns]

final_df = pd.concat([combined_df, MGB1], ignore_index=True)
final_df.to_csv('./merge2/06_combined_microbiology_cultures_demographics2.csv', index=False)


combined_df = pd.read_csv('./merge/08_combined_microbiology_cultures_microbial_resistance.csv')
MGB1 = pd.read_csv('./ARMD-MGB/microbiology_cohort_deid_tj_updated.csv')
MGB1['source'] = 'MGB'

MGB1_renamed = MGB1.rename(columns={'order_time_jittered_utc_shifted': 'order_time_jittered'})

mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA

combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns].reset_index(drop=True)
MGB1_renamed = MGB1_renamed[final_columns].reset_index(drop=True)

final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)
final_df.to_csv('./merge2/08_combined_microbiology_cultures_microbial_resistance2.csv', index=False)


combined_df = pd.read_csv('./merge/09_combined_microbiology_cultures_nursing_home_visits.csv')
MGB1 = pd.read_csv('./ARMD-MGB/nursing_home_visits_deid_tj.csv')
MGB1['source'] = 'MGB'

MGB1_renamed = MGB1.rename(columns={'order_time_jittered_utc_shifted': 'order_time_jittered'})

mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA

combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns].reset_index(drop=True)
MGB1_renamed = MGB1_renamed[final_columns].reset_index(drop=True)

final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)
final_df.to_csv('./merge2/09_combined_microbiology_cultures_nursing_home_visits2.csv', index=False)


combined_df = pd.read_csv('./merge/10_combined_microbiology_cultures_prior_med.csv')
MGB1 = pd.read_csv('./ARMD-MGB/prior_org_deid_tj.csv')
MGB1['source'] = 'MGB'

MGB1_renamed = MGB1.rename(columns={'order_time_jittered_utc_shifted': 'order_time_jittered'})

mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA

combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns].reset_index(drop=True)
MGB1_renamed = MGB1_renamed[final_columns].reset_index(drop=True)

final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)
final_df.to_csv('./merge2/10_combined_microbiology_cultures_prior_med2.csv', index=False)


combined_df = pd.read_csv('./merge/14_combined_microbiology_cultures_prior_infecting_organism.csv')
MGB1 = pd.read_csv('./ARMD-MGB/prior_org_deid_tj.csv')
MGB1['source'] = 'MGB'

MGB1_renamed = MGB1.rename(columns={
    'order_time_jittered_utc_shifted': 'order_time_jittered',
    'prior_org': 'prior_organism',
    'prior_org_days_to_culture': 'prior_infecting_organism_days_to_culture'
})

mgb_extra_cols = [c for c in MGB1_renamed.columns if c not in combined_df.columns]
for c in mgb_extra_cols:
    combined_df[c] = pd.NA

combined_extra_cols = [c for c in combined_df.columns if c not in MGB1_renamed.columns]
for c in combined_extra_cols:
    MGB1_renamed[c] = pd.NA

final_columns = combined_df.columns.tolist() + [c for c in mgb_extra_cols if c not in combined_df.columns]
combined_df = combined_df[final_columns].reset_index(drop=True)
MGB1_renamed = MGB1_renamed[final_columns].reset_index(drop=True)

final_df = pd.concat([combined_df, MGB1_renamed], ignore_index=True)
final_df.to_csv('./merge2/14_combined_microbiology_cultures_prior_infecting_organism2.csv', index=False)
