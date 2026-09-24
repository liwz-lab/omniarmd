
import pandas as pd
import numpy as np
import polars as pl

import os
ks = knowledge_summary.copy()
ks.columns

ks["gene_prevalence_in_R"] = ks["R"] / ks["total_R"]
ks["gene_prevalence_in_S"] = ks["S"] / ks["total_S"]
ks["gene_prevalence_in_Non_S"] = ks["gene_non_s"] / ks["total_non_s"]
ks["R_rate_among_gene_positive"] = ks["R"] / ks["gene_total"]
ks["Non_S_rate_among_gene_positive"] = ks["gene_non_s"] / ks["gene_total"]
cols = [
    "gene_prevalence_in_R",
    "gene_prevalence_in_S",
    "gene_prevalence_in_Non_S",
    "R_rate_among_gene_positive",
    "Non_S_rate_among_gene_positive",
]

for c in cols:
    ks[c] = ks[c].replace([np.inf, -np.inf], np.nan).fillna(0)

ks["evidence_n"] = ks["total_all"]
ks = ks.rename(columns={
    "final_score": "GPAS"
})


ks["organism_std"] = (
    ks["organism_std"]
    .astype(str)
    .str.strip()
    .str.lower()
)

ks["antimicrobial_std"] = (
    ks["antimicrobial_std"]
    .astype(str)
    .str.strip()
    .str.lower()
)

ks["gene_symbol"] = (
    ks["gene_symbol"]
    .astype(str)
    .str.strip()
)


bridge_keys = ["organism_std", "antimicrobial_std"]

def top_resistance_genes(g, n=5):
    sub = g[g["GPAS"] > 0].copy()
    if sub.empty:
        return ""
    sub = sub.sort_values(
        ["GPAS", "evidence_n"],
        ascending=[False, False]
    )
    return ";".join(sub["gene_symbol"].drop_duplicates().head(n).tolist())


def top_susceptibility_genes(g, n=5):
    sub = g[g["GPAS"] < 0].copy()
    if sub.empty:
        return ""
    sub = sub.sort_values(
        ["GPAS", "evidence_n"],
        ascending=[True, False]
    )
    return ";".join(sub["gene_symbol"].drop_duplicates().head(n).tolist())


top_resistance = (
    ks
    .groupby(bridge_keys)
    .apply(lambda g: pd.Series({
        "ebi_top_resistance_genes": top_resistance_genes(g, n=5)
    }))
    .reset_index()
)

top_susceptibility = (
    ks
    .groupby(bridge_keys)
    .apply(lambda g: pd.Series({
        "ebi_top_susceptibility_genes": top_susceptibility_genes(g, n=5)
    }))
    .reset_index()
)

bridge_features = (
    ks
    .groupby(bridge_keys)
    .agg(
        ebi_gene_count=("gene_symbol", "nunique"),

        ebi_evidence_n_sum=("evidence_n", "sum"),
        ebi_evidence_n_max=("evidence_n", "max"),
        ebi_evidence_n_mean=("evidence_n", "mean"),

        ebi_max_GPAS=("GPAS", "max"),
        ebi_min_GPAS=("GPAS", "min"),
        ebi_mean_GPAS=("GPAS", "mean"),
        ebi_median_GPAS=("GPAS", "median"),

        ebi_max_R_rate_among_gene_positive=(
            "R_rate_among_gene_positive",
            "max"
        ),
        ebi_mean_R_rate_among_gene_positive=(
            "R_rate_among_gene_positive",
            "mean"
        ),

        ebi_max_Non_S_rate_among_gene_positive=(
            "Non_S_rate_among_gene_positive",
            "max"
        ),
        ebi_mean_Non_S_rate_among_gene_positive=(
            "Non_S_rate_among_gene_positive",
            "mean"
        ),

        ebi_max_gene_prevalence_in_R=(
            "gene_prevalence_in_R",
            "max"
        ),
        ebi_mean_gene_prevalence_in_R=(
            "gene_prevalence_in_R",
            "mean"
        ),

        ebi_max_gene_prevalence_in_Non_S=(
            "gene_prevalence_in_Non_S",
            "max"
        ),
        ebi_mean_gene_prevalence_in_Non_S=(
            "gene_prevalence_in_Non_S",
            "mean"
        ),
    )
    .reset_index()
)

label_counts = (
    ks
    .pivot_table(
        index=bridge_keys,
        columns="resistance_evidence_label",
        values="gene_symbol",
        aggfunc="count",
        fill_value=0
    )
    .reset_index()
)

label_counts = label_counts.rename(columns={
    "strong_resistance": "ebi_n_strong_resistance_genes",
    "moderate_resistance": "ebi_n_moderate_resistance_genes",
    "weak_or_neutral":"ebi_n_weak_neutral_resistance_genes",
    "moderate_susceptibility": "ebi_n_moderate_susceptibility_genes",
    "strong_susceptibility": "ebi_n_strong_susceptibility_genes",
})


expected_label_cols = [
    "ebi_n_strong_resistance_genes",
    "ebi_n_moderate_resistance_genes",
    "ebi_n_weak_neutral_resistance_genes",
    "ebi_n_moderate_susceptibility_genes",
    "ebi_n_strong_susceptibility_genes",
]

for col in expected_label_cols:
    if col not in label_counts.columns:
        label_counts[col] = 0

bridge_features = bridge_features.merge(
    label_counts,
    on=bridge_keys,
    how="left",
    validate="1:1"
)

bridge_features = bridge_features.merge(
    top_resistance,
    on=bridge_keys,
    how="left",
    validate="1:1"
)

bridge_features = bridge_features.merge(
    top_susceptibility,
    on=bridge_keys,
    how="left",
    validate="1:1"
)



df = bridge_features.copy()

df["direction_score"] = (
    0.6 * df["ebi_mean_GPAS"] +
    0.4 * df["ebi_median_GPAS"]
)

df["evidence_score"] = np.log1p(df["ebi_evidence_n_sum"])

def risk_realistic(row):
    d = row["direction_score"]
    e = row["evidence_score"]

    if d > 1:
        return "high_resistant" if e > 2 else "weak_resistant"
    elif d < -1:
        return "high_susceptible" if e > 2 else "weak_susceptible"
    else:
        return "neutral"


def risk_real_v3(row):
    d = row["direction_score"]
    e = row["evidence_score"]


    if d > 1:
        return "high_resistant"
    elif d > 0.2:
        return "weak_resistant"

    elif d < -1:
        return "high_susceptible"
    elif d < -0.2:
        return "weak_susceptible"
    else:
        return "neutral"

df["bridge_direction"] = df.apply(risk_real_v3, axis=1)
df["bridge_direction"].value_counts()

df["knowledge_matched"] = 1

# ============================================================
bridge_features=df
dup_bridge = bridge_features.duplicated(subset=bridge_keys).sum()

print("Duplicated bridge keys:", dup_bridge)
assert dup_bridge == 0

print("Bridge features shape:", bridge_features.shape)
print("Bridge organism-antibiotic pairs:", bridge_features[bridge_keys].drop_duplicates().shape[0])
bridge_features.to_csv('./03_armd_resistance_evidence_deidentification.csv')

#################################################
import numpy as np
from scipy.stats import spearmanr

df["score_mean"] = df["ebi_mean_GPAS"]
df["score_median"] = df["ebi_median_GPAS"]
df["score_combo"] = 0.6*df["ebi_mean_GPAS"] + 0.4*df["ebi_median_GPAS"]

for col in ["score_mean", "score_median", "score_combo"]:
    rho, _ = spearmanr(df[col], df["evidence_score"])
    print(col, rho)


import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

weights = np.linspace(0, 1, 21)  # 0.0 → 1.0 step 0.05

results = []

for w in weights:
    score = w * df["ebi_mean_GPAS"] + (1 - w) * df["ebi_median_GPAS"]
    rho, _ = spearmanr(score, df["evidence_score"])
    std = score.std()
    def categorize(x):
        if x > 1:
            return "high_resistant"
        elif x > 0.2:
            return "weak_resistant"
        elif x >= -0.2:
            return "neutral"
        elif x >= -1:
            return "weak_susceptible"
        else:
            return "high_susceptible"


    cat = score.apply(categorize)

    results.append({
        "weight_mean": w,
        "spearman_rho": rho,
        "std": std,
        "score": score,
        "category": cat
    })

res_df = pd.DataFrame(results)
plt.figure()
plt.plot(res_df["weight_mean"], res_df["spearman_rho"], marker='o')
plt.axvline(0.6, linestyle='--')  
plt.xlabel("Weight on Mean GPAS")
plt.ylabel("Spearman correlation with evidence_score")
plt.title("Sensitivity analysis of weight parameter")
plt.savefig('Sensitivity.png')
plt.show()

idx = (res_df["weight_mean"] - 0.6).abs().idxmin()
baseline = res_df.loc[idx, "category"]

stability = []
for i, row in res_df.iterrows():
    same = (row["category"] == baseline).mean()
    stability.append(same)

res_df["stability"] = stability
plt.figure()
plt.plot(res_df["weight_mean"], res_df["stability"], marker='o')
plt.axvline(0.6, linestyle='--')
plt.xlabel("Weight on Mean GPAS")
plt.ylabel("Agreement with w=0.6")
plt.title("Classification Stability")
plt.savefig('bridge_stability.pdf')
plt.show()
res_df.to_csv('GPAS_stability.csv')


import matplotlib.pyplot as plt

plt.hist(df["direction_score"], bins=50)
plt.axvline(1, linestyle='--')
plt.axvline(0.2, linestyle='--')
plt.axvline(-0.2, linestyle='--')
plt.axvline(-1, linestyle='--')
plt.title("Distribution of direction_score")
plt.savefig('Distribution of direction_score.png')
plt.show()


import seaborn as sns
sns.histplot(df["direction_score"], bins=50, kde=True)

bins = {
    "high_resistant": (df["direction_score"] > 1).mean(),
    "weak_resistant": ((df["direction_score"] > 0.2) & (df["direction_score"] <= 1)).mean(),
    "neutral": ((df["direction_score"] >= -0.2) & (df["direction_score"] <= 0.2)).mean(),
    "weak_susceptible": ((df["direction_score"] < -0.2) & (df["direction_score"] >= -1)).mean(),
    "high_susceptible": (df["direction_score"] < -1).mean()
}
print(bins)

import polars as pl
bridge_features_pl = pl.from_pandas(bridge_features)
master_v12 = pl.read_parquet('master_v12_infecting_organism_deidentification.parquet')
master_v12.columns
master_v12 = master_v12.with_columns([
    pl.col("organism_std").replace("NA", None),
    pl.col("antimicrobial_std").replace("NA", None),
    pl.col("susceptibility_std").replace("NA", None),
])
master_v12 = master_v12.filter(
    pl.col("organism_std").is_not_null() &
    pl.col("antimicrobial_std").is_not_null() &
    pl.col("susceptibility_std").is_not_null()
)
# master_v12 = master_v12.drop_nulls(
#     ["organism_std", "antimicrobial_std", "susceptibility_std"]
# )
master_v12['susceptibility_std'].unique()
antimicrobial_std=master_v12['antimicrobial_std'].unique()
antimicrobial_std=antimicrobial_std.to_pandas()
antimicrobial_std.to_csv('antimicrobial_std.csv')
master_v12
import polars as pl
master_v12 = master_v12.with_columns(
    pl.col("antimicrobial_std")
    .replace({
        "Mcim": "NA",
        "Ecim": "NA"
    })
)
master_v12.write_parquet('master_v12_infecting_organism_deidentification.parquet')
master_v12 = pl.read_parquet('master_v12_infecting_organism_deidentification.parquet')
# master_v12 = master_v12.rename({
#     "antibiotic_std": "antimicrobial_std"
# })
master_v12_bridge_ready = master_v12.with_columns([
    pl.col("organism_std")
      .cast(pl.Utf8)
      .str.strip_chars()
      .str.to_lowercase(),

    pl.col("antimicrobial_std")
      .cast(pl.Utf8)
      .str.strip_chars()
      .str.to_lowercase(),
])


import polars as pl
if not isinstance(bridge_features, pl.DataFrame):
    bridge_features = pl.from_pandas(bridge_features)

old_n = master_v12_bridge_ready.height

master_v13_omni_bridge = (
    master_v12_bridge_ready
    .with_row_index("_master_row_id")
    .join(
        bridge_features,
        on=bridge_keys,
        how="left"
    )
    .sort("_master_row_id")
    .drop("_master_row_id")
)

assert master_v13_omni_bridge.height == old_n

print("master_v12 rows:", old_n)
print("master_v13_omni_bridge rows:", master_v13_omni_bridge.height)
print("master_v13_omni_bridge shape:", master_v13_omni_bridge.shape)

count_cols = [
    "ebi_gene_count",
    "ebi_evidence_n_sum",
    "ebi_evidence_n_max",
    "ebi_evidence_n_mean",

    "ebi_n_strong_resistance_genes",
    "ebi_n_moderate_resistance_genes",
    "ebi_n_weak_neutral_resistance_genes",
    # "ebi_n_weak_resistance_genes",
    # "ebi_n_neutral_genes",
    # "ebi_n_weak_susceptibility_genes",

    "ebi_n_moderate_susceptibility_genes",
    "ebi_n_strong_susceptibility_genes",
    "ebi_knowledge_matched",
]

score_cols = [
    "ebi_max_GPAS",
    "ebi_min_GPAS",
    "ebi_mean_GPAS",
    "ebi_median_GPAS",

    "ebi_max_R_rate_among_gene_positive",
    "ebi_mean_R_rate_among_gene_positive",
    "ebi_max_Non_S_rate_among_gene_positive",
    "ebi_mean_Non_S_rate_among_gene_positive",
    "ebi_max_gene_prevalence_in_R",
    "ebi_mean_gene_prevalence_in_R",
    "ebi_max_gene_prevalence_in_Non_S",
    "ebi_mean_gene_prevalence_in_Non_S",
]

text_cols = [
    "ebi_top_resistance_genes",
    "ebi_top_susceptibility_genes",
    "ebi_bridge_direction",
]

# count 列补 0
master_v13_omni_bridge = master_v13_omni_bridge.with_columns([
    pl.col(c).fill_null(0)
    for c in count_cols
    if c in master_v13_omni_bridge.columns
])


master_v13_omni_bridge = master_v13_omni_bridge.with_columns([
    pl.col(c).fill_null(0)
    for c in score_cols
    if c in master_v13_omni_bridge.columns
])

master_v13_omni_bridge = master_v13_omni_bridge.with_columns([
    pl.col("ebi_top_resistance_genes").fill_null(""),
    pl.col("ebi_top_susceptibility_genes").fill_null(""),
    pl.col("bridge_direction").fill_null("no_external_evidence"),
])

bridge_qc = master_v13_omni_bridge.select([
    pl.len().alias("n_rows"),
    pl.col("knowledge_matched").sum().alias("n_matched_rows"),
    pl.col("knowledge_matched").mean().alias("bridge_match_rate"),
    pl.col("organism_std").n_unique().alias("n_organisms"),
    pl.col("antimicrobial_std").n_unique().alias("n_antibiotics"),
])

print(bridge_qc)

bridge_match_by_organism = (
    master_v13_omni_bridge
    .group_by("organism_std")
    .agg([
        pl.len().alias("n_rows"),
        pl.col("knowledge_matched").sum().alias("n_matched_rows"),
        pl.col("knowledge_matched").mean().alias("match_rate"),
    ])
    .sort("n_rows", descending=True)
)

bridge_match_by_antibiotic = (
    master_v13_omni_bridge
    .group_by("antimicrobial_std")
    .agg([
        pl.len().alias("n_rows"),
        pl.col("knowledge_matched").sum().alias("n_matched_rows"),
        pl.col("knowledge_matched").mean().alias("match_rate"),
    ])
    .sort("n_rows", descending=True)
)

master_v13_omni_bridge = master_v13_omni_bridge.with_columns(
    pl.col("knowledge_matched").fill_null(0)
)
unmatched_priority_pairs = (
    master_v13_omni_bridge
    .filter(pl.col("knowledge_matched") == 0)
    .group_by(["organism_std", "antimicrobial_std"])
    .agg([
        pl.len().alias("n_unmatched_rows"),
    ])
    .sort("n_unmatched_rows", descending=True)
)

print("Top unmatched pairs:")
print(unmatched_priority_pairs.head(30))

base_out_dir = ('./omni_bridge/')


bridge_features.write_csv(
    base_out_dir + "omni_bridge_species_antibiotic_features_deidentification.csv"
)
bridge_match_by_organism.write_csv(
    base_out_dir + "bridge_match_by_organism0730.csv"
)

bridge_match_by_antibiotic.write_csv(
    base_out_dir + "bridge_match_by_antibiotic0730.csv"
)

unmatched_priority_pairs.write_csv(
    base_out_dir + "unmatched_priority_pairs0730.csv"
)

master_v13_omni_bridge.write_parquet(
    base_out_dir + "master_v13_omni_bridge_deidentfication0730.parquet"
)

print("Saved bridge features:")
print(base_out_dir + "omni_bridge_species_antibiotic_features0727.csv")

print("Saved master_v13:")
print(base_out_dir + "master_v13_omni_bridge_0727.parquet")

################################################################
import pandas as pd
import numpy as np
import polars as pl
import os

os.chdir('')

master_v13_omni_bridge = pl.read_parquet('master_v13_bridge_deidentification_mapping0730.parquet')
import polars as pl

master_v13_omni_bridge = master_v13_omni_bridge.filter(
    pl.col("organism_std").is_not_null() &

    ~pl.col("organism_std")
    .str.strip_chars()
    .str.to_lowercase()
    .str.replace_all(r"\s+", "")
    .is_in(["na", "nan", "null", "none", "",
    "n/a", "na ", " null", "nan "])
)
master_v13_omni_bridge = master_v13_omni_bridge.filter(
    ~pl.col("antimicrobial_std")
    .str.to_lowercase()
    .is_in(["ecim", "mcim"])
)


bridge_overall = master_v13_omni_bridge.select([
    pl.len().alias("n_rows"),
    pl.col("knowledge_matched").sum().alias("n_matched"),
    pl.col("knowledge_matched").mean().alias("match_rate"),
])
bridge_overall = pd.DataFrame([bridge_overall])
bridge_overall.to_csv("01_bridge_overall_0727.csv", index=False)

#######bridge_by_organism
bridge_by_organism = (
    master_v13_omni_bridge
    .group_by("organism_std")
    .agg([
        pl.len().alias("n_records"),
        pl.col("knowledge_matched").mean().alias("match_rate"),
    ])
    .sort("n_records", descending=True)
)
bridge_by_organism.write_csv("01_bridge_by_organism2_0730.csv")


##################bridge_by_antibiotic
bridge_by_antibiotic = (
    master_v13_omni_bridge
    .group_by("antimicrobial_std")
    .agg([
        pl.len().alias("n_records"),
        pl.col("knowledge_matched").mean().alias("match_rate"),
    ])
    .sort("n_records", descending=True)
)
bridge_by_antibiotic.write_csv("01_bridge_by_antibiotic3_0730.csv")

import polars as pl

all_pairs = (
    master_v13_omni_bridge
    .filter(
        pl.col("organism_std").is_not_null() &
        pl.col("antimicrobial_std").is_not_null()
    )
    .select([
        "organism_std",
        "antimicrobial_std"
    ])
    .unique()
)


supported_pairs = (
    master_v13_omni_bridge
    .filter(
        pl.col("organism_std").is_not_null() &
        pl.col("antimicrobial_std").is_not_null() &
        (pl.col("knowledge_matched") == 1)
    )
    .select([
        "organism_std",
        "antimicrobial_std"
    ])
    .unique()
)

n_total_pairs = all_pairs.height
n_supported_pairs = supported_pairs.height

pair_coverage = (
    n_supported_pairs / n_total_pairs * 100
)

print("Total unique organism-antimicrobial pairs:",
      n_total_pairs)

print("Supported unique organism-antimicrobial pairs:",
      n_supported_pairs)

print("Pair-level molecular coverage:",
      f"{pair_coverage:.2f}%")


##############################
pair_level = (
    master_v13_omni_bridge
    .filter(
        pl.col("organism_std").is_not_null() &
        pl.col("antimicrobial_std").is_not_null()
    )
    .group_by([
        "organism_std",
        "antimicrobial_std"
    ])
    .agg([
        pl.len().alias("n_records"),
        pl.col("knowledge_matched")
          .sum()
          .alias("n_matched_records"),
        pl.col("knowledge_matched")
          .mean()
          .alias("record_match_rate")
    ])
    .with_columns(
        (
            pl.col("record_match_rate") * 100
        ).alias("record_match_rate_pct")
    )
    .sort(
        ["n_records"],
        descending=True
    )
)

pair_level.write_csv(
    "OmniBridge_organism_antimicrobial_coverage.csv"
)
####################
bridge_by_organism = (
    master_v13_omni_bridge
    .filter(
        pl.col("organism_std").is_not_null()
    )
    .group_by("organism_std")
    .agg([
        pl.len().alias("n_records"),
        pl.col("knowledge_matched")
          .sum()
          .alias("n_records_supported"),
        pl.col("knowledge_matched")
          .mean()
          .alias("record_coverage")
    ])
    .with_columns(
        (
            pl.col("record_coverage") * 100
        ).alias("record_coverage_pct")
    )
    .sort("n_records", descending=True)
)

bridge_by_organism.write_csv(
    "OmniBridge_organism_record_coverage2.csv"
)


##################antimicrobial
bridge_by_organism = (
    master_v13_omni_bridge
    .filter(
        pl.col("antimicrobial_std").is_not_null()
    )
    .group_by("antimicrobial_std")
    .agg([
        pl.len().alias("n_records"),
        pl.col("knowledge_matched")
          .sum()
          .alias("n_records_supported"),
        pl.col("knowledge_matched")
          .mean()
          .alias("record_coverage")
    ])
    .with_columns(
        (
            pl.col("record_coverage") * 100
        ).alias("record_coverage_pct")
    )
    .sort("n_records", descending=True)
)

bridge_by_organism.write_csv(
    "OmniBridge_antimicrobial_record_coverage2.csv"
)



#########################
# Pair-level status
pair_status = (
    master_v13_omni_bridge
    .filter(
        pl.col("organism_std").is_not_null() &
        pl.col("antimicrobial_std").is_not_null()
    )
    .select([
        "organism_std",
        "antimicrobial_std",
        "knowledge_matched"
    ])
    .unique()
)

# Organism-level pair coverage
pair_by_organism = (
    pair_status
    .group_by("organism_std")
    .agg([
        pl.len().alias("n_unique_antimicrobial_pairs"),
        pl.col("knowledge_matched")
          .sum()
          .alias("n_supported_pairs")
    ])
    .with_columns(
        (
            pl.col("n_supported_pairs") /
            pl.col("n_unique_antimicrobial_pairs") * 100
        ).alias("pair_coverage_pct")
    )
    .sort(
        "n_unique_antimicrobial_pairs",
        descending=True
    )
)

pair_by_organism.write_csv(
    "OmniBridge_organism_pair_coverage.csv"
)

#######################################
import polars as pl

df = master_v13_omni_bridge

record_by_organism = (
    df
    .filter(
        pl.col("organism_std").is_not_null()
    )
    .group_by("organism_std")
    .agg([
        pl.len().alias("n_records"),

        pl.col("knowledge_matched")
        .sum()
        .alias("n_records_supported"),
    ])
    .with_columns(
        (
            pl.col("n_records_supported")
            / pl.col("n_records")
            * 100
        )
        .alias("record_coverage_pct")
    )
)


pair_status = (
    df
    .filter(
        pl.col("organism_std").is_not_null() &
        pl.col("antimicrobial_std").is_not_null()
    )
    .select([
        "organism_std",
        "antimicrobial_std",
        "knowledge_matched"
    ])
    .unique()
)


pair_by_organism = (
    pair_status
    .group_by("organism_std")
    .agg([
        pl.len()
        .alias("n_unique_antimicrobial_pairs"),

        pl.col("knowledge_matched")
        .sum()
        .alias("n_supported_pairs"),
    ])
    .with_columns(
        (
            pl.col("n_supported_pairs")
            / pl.col("n_unique_antimicrobial_pairs")
            * 100
        )
        .alias("pair_coverage_pct")
    )
)

organism_coverage = (
    record_by_organism
    .join(
        pair_by_organism,
        on="organism_std",
        how="left"
    )
    .sort(
        "n_records",
        descending=True
    )
)



organism_coverage = organism_coverage.select([
    "organism_std",
    "n_records",
    "n_records_supported",
    "record_coverage_pct",
    "n_unique_antimicrobial_pairs",
    "n_supported_pairs",
    "pair_coverage_pct"
])


print(
    organism_coverage.head(5)
)

organism_coverage_display = (
    organism_coverage
    .with_columns([
        pl.format(
            "{}%",
            pl.col("record_coverage_pct").round(2)
        ).alias("record_coverage"),

        pl.format(
            "{}%",
            pl.col("pair_coverage_pct").round(2)
        ).alias("pair_coverage"),
    ])
    .select([
        "organism_std",
        "n_records",
        "n_records_supported",
        "record_coverage",
        "n_unique_antimicrobial_pairs",
        "n_supported_pairs",
        "pair_coverage"
    ])
)

print(organism_coverage_display.head(5))

organism_coverage.write_csv(
    "OmniBridge_organism_coverage.csv"
)

matched_pairs = (
    master_v13_omni_bridge
    .filter(pl.col("knowledge_matched") == 1)
    .group_by(["organism_std", "antimicrobial_std"])
    .agg([
        pl.len().alias("n_matched_records"),
    ])
    .sort("n_matched_records", descending=True)
)
matched_pairs.write_csv("02_matched_pairs_0730.csv")


total_pairs = (
    master_v13_omni_bridge
    .select(["organism_std", "antimicrobial_std"])
    .unique()
    .height
)
matched_pairs_n = (
    master_v13_omni_bridge
    .filter(pl.col("knowledge_matched") == 1)
    .select(["organism_std", "antimicrobial_std"])
    .unique()
    .height
)
coverage_rate = matched_pairs_n / total_pairs
missing_rate = 1 - coverage_rate

print("Coverage:", coverage_rate)
print("Missing:", missing_rate)

matched_pairs_detail = (
    master_v13_omni_bridge
    .filter(pl.col("knowledge_matched") == 1)
    .group_by(["organism_std", "antimicrobial_std"])
    .agg([
        pl.len().alias("n_records"),
        pl.col("ebi_mean_GPAS").mean().alias("mean_score")
    ])
    .sort("n_records", descending=True)
)

matched_pairs_detail.write_csv("matched_pairs_detail.csv")
unmatched_pairs = (
    master_v13_omni_bridge
    .filter(pl.col("knowledge_matched") == 0)
    .group_by(["organism_std", "antimicrobial_std"])
    .agg([
        pl.len().alias("n_unmatched_records"),
    ])
    .sort("n_unmatched_records", descending=True)
)
unmatched_pairs.write_csv("02_unmatched_pairs_0730.csv")


unmatched_pairs_detail = (
    master_v13_omni_bridge
    .filter(pl.col("knowledge_matched") == 0)
    .group_by(["organism_std", "antimicrobial_std"])
    .agg([
        pl.len().alias("n_records")
    ])
    .sort("n_records", descending=True)
)

unmatched_pairs_detail.write_csv("unmatched_pairs_detail0730.csv")
high_freq_unmatched = (
    unmatched_pairs_detail
    .filter(pl.col("n_records") >= 500) 
)

high_freq_unmatched.write_csv("high_freq_unmatched0730.csv")

armd_resistance_rate = (
    master_v13_omni_bridge
    .filter(pl.col("susceptibility_std").is_in(["S", "I", "R"]))
    .group_by(["organism_std", "antimicrobial_std"])
    .agg([
        pl.len().alias("n_ast"),
        (pl.col("susceptibility_std") == "S").sum().alias("n_S"),
        (pl.col("susceptibility_std") == "I").sum().alias("n_I"),
        (pl.col("susceptibility_std") == "R").sum().alias("n_R"),
    ])
    .with_columns([
        #(pl.col("n_R") / pl.col("n_ast")).alias("armd_R_rate"),
        ((pl.col("n_I") + pl.col("n_R")) / pl.col("n_ast")).alias("armd_R_rate"),
    ])
    .sort("n_ast", descending=True)
)

ebi_features = (
    master_v13_omni_bridge
    .select([
        "organism_std",
        "antimicrobial_std",
        'ebi_gene_count',
        'ebi_evidence_n_mean',
        'ebi_mean_GPAS',
        'ebi_mean_Non_S_rate_among_gene_positive',
        'ebi_mean_gene_prevalence_in_Non_S',
        'ebi_n_moderate_resistance_genes',
        'ebi_n_moderate_susceptibility_genes',
        'ebi_n_weak_neutral_resistance_genes',
        'ebi_n_strong_resistance_genes',
        'ebi_n_strong_susceptibility_genes',
        'ebi_top_resistance_genes',
        'ebi_top_susceptibility_genes',
        'bridge_direction',
        'knowledge_matched'
    ])
    .unique()
)


merged = (
    armd_resistance_rate
    .join(
        ebi_features,
        on=["organism_std", "antimicrobial_std"],
        how="inner"
    )
    .drop_nulls([
        "ebi_mean_GPAS",
        "ebi_n_strong_resistance_genes"
    ])
)
merged2 = merged.filter(
    pl.col("knowledge_matched") == 1
)

merged2.write_csv("03_armd_resistance_evidence.csv")


armd_vs_ebi = (
    master_v13_omni_bridge
    .filter(pl.col("knowledge_matched") == 1)
    .filter(pl.col("susceptibility_std").is_in(["S", "I", "R"]))
    .group_by(["organism_std", "antimicrobial_std"])
    .agg([
        pl.len().alias("n_armd"),
        #(pl.col("susceptibility_std") == "R").mean().alias("armd_R_rate"),
        (pl.col("susceptibility_std").is_in(["I", "R"])).mean().alias("armd_R_rate"),

        pl.col("ebi_max_R_rate_among_gene_positive").mean().alias("ebi_mean_max_R_rate"),
        pl.col("ebi_mean_R_rate_among_gene_positive").mean().alias("ebi_mean_R_rate"),
        pl.col("ebi_max_GPAS").mean().alias("ebi_mean_max_GPAS"),
    ])
)
armd_vs_ebi.write_csv("04_armd_vs_ebi.csv")
armd_vs_ebi_pd = armd_vs_ebi.to_pandas()

armd_vs_ebi_pd[[
    "armd_R_rate",
    "ebi_mean_R_rate",
    "ebi_mean_max_GPAS"
]].corr()
armd_vs_ebi_pd.to_csv("04_armd_vs_ebi_pd0730.csv")
import polars as pl
strong_resistance_records = (
    master_v13_omni_bridge
    .filter(pl.col("ebi_n_strong_resistance_genes") > 0)
)
strong_resistance_pairs = (
    strong_resistance_records  
    .group_by(["organism_std", "antimicrobial_std"])
    .agg([
        pl.len().alias("n_records"),
        pl.col("ebi_n_strong_resistance_genes").mean().alias("mean_strong_resistance_genes"),
        pl.col("ebi_max_GPAS").mean().alias("mean_ebi_max_GPAS"),
        pl.col("ebi_top_resistance_genes")
        .explode()
        .drop_nulls()
        .unique()
        .alias("genes_list")
    ])
)

strong_resistance_pairs = strong_resistance_pairs.with_columns(
    pl.col("genes_list")
    .list.join(",")  
    .alias("strong_resistance_genes")
).drop("genes_list")


strong_resistance_pairs = strong_resistance_pairs.sort(
    "mean_ebi_max_GPAS",
    descending=True
)

strong_resistance_pairs.write_csv("05_strong_resistance_pairs0730.csv")


strong_susceptibility_records = (
    master_v13_omni_bridge
    .filter(pl.col("ebi_n_strong_susceptibility_genes") > 0)
)

strong_susceptibility_pairs = (
    strong_susceptibility_records
    .group_by(["organism_std", "antimicrobial_std"])
    .agg([
        pl.len().alias("n_records"),
        pl.col("ebi_n_strong_susceptibility_genes").mean().alias("mean_strong_susceptibility_genes"),
        pl.col("ebi_max_GPAS").mean().alias("mean_ebi_max_GPAS"),

        pl.col("ebi_top_susceptibility_genes")
        .explode()
        .drop_nulls()
        .unique()
        .alias("genes_list")
    ])
)


strong_susceptibility_pairs = strong_susceptibility_pairs.with_columns(
    pl.col("genes_list")
    .list.join(",")   
    .alias("strong_susceptibility_genes")
).drop("genes_list")


strong_susceptibility_pairs = strong_susceptibility_pairs.sort(
    "mean_ebi_max_GPAS",
    descending=True
)

strong_susceptibility_pairs.write_csv("06_strong_susceptibility_pairs.csv")

carbapenem_analysis = (
    master_v13_omni_bridge
    .filter(pl.col("susceptibility_std").is_in(["S", "I", "R"]))
    .group_by(["sub_exp_Carbapenem", "bridge_direction"])
    .agg([
        pl.len().alias("n"),
       # (pl.col("susceptibility_std") == "R").mean().alias("R_rate"),
        (pl.col("susceptibility_std").is_in(["I", "R"])).mean().alias("R_rate"),
    ])
    .sort(["sub_exp_Carbapenem", "bridge_direction"])
)

carbapenem_analysis = pd.DataFrame([carbapenem_analysis])
carbapenem_analysis.to_csv("07_carbapenem_analysis0727.csv", index=False)

prior_infection_analysis = (
    master_v13_omni_bridge
    .filter(pl.col("susceptibility_std").is_in(["S", "I", "R"]))
    .group_by(["has_prior_infecting_organism", "bridge_direction"])
    .agg([
        pl.len().alias("n"),
        #(pl.col("susceptibility_std") == "R").mean().alias("R_rate"),
        (pl.col("susceptibility_std").is_in(["I", "R"])).mean().alias("R_rate"),
    ])
)
prior_infection_analysis = pd.DataFrame([prior_infection_analysis])
prior_infection_analysis.to_csv("08_prior_infection_analysis.csv", index=False)

icu_analysis = (
    master_v13_omni_bridge
    .filter(pl.col("susceptibility_std").is_in(["S", "I", "R"]))
    .group_by(["hosp_ward_ICU", "bridge_direction"])
    .agg([
        pl.len().alias("n"),
        (pl.col("susceptibility_std").is_in(["I", "R"])).mean().alias("R_rate"),
    ])
)
icu_analysis = pd.DataFrame([icu_analysis])
icu_analysis.to_csv("09_icu_analysis.csv", index=False)

yearly_trend = (
    master_v13_omni_bridge
    .filter(pl.col("susceptibility_std").is_in(["S", "I", "R"]))
    .group_by(["order_time_year", "organism_std", "antimicrobial_std"])
    .agg([
        pl.len().alias("n_ast"),
        #(pl.col("susceptibility_std") == "R").mean().alias("R_rate"),
        (pl.col("susceptibility_std").is_in(["I", "R"])).mean().alias("R_rate"),
        pl.col("ebi_max_GPAS").mean().alias("mean_ebi_score"),
    ])
)

yearly_trend = pd.DataFrame([yearly_trend])
yearly_trend.to_csv("10_yearly_trend0727.csv", index=False)


agent_evidence_cases = (
    master_v13_omni_bridge
    .filter(pl.col("knowledge_matched") == 1)
    .select([
        "organism_std",
        "antimicrobial_std",
        "susceptibility_std",
        "bridge_direction",
        "ebi_top_resistance_genes",
        "ebi_top_susceptibility_genes",
        "ebi_max_GPAS",
        "ebi_gene_count",
    ])
)
agent_evidence_cases = pd.DataFrame([agent_evidence_cases])
agent_evidence_cases.to_csv("12_agent_evidence_cases.csv", index=False)



