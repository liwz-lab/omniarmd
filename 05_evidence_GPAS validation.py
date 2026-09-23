from __future__ import annotations
import json
import math
import sys
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, spearmanr
from statsmodels.stats.multitest import multipletests


import os

# ============================================================================
# PyCharm settings
# ============================================================================
RUN_INDEPENDENTLY = True
SUMMARY_INPUT = r"ebi_knowledge_summary_0730.csv"  # Used only when RUN_INDEPENDENTLY=True
GOLD_STANDARD_INPUT = r""  # Optional independent known AMR relationships
OUTPUT_DIR = r"gpas_validation"
DEFAULT_K = 10.0
DEFAULT_EPSILON = 0.5
MODULE_VERSION = "GPAS-validation-2026-09-01-kappa-direct-counts-selfcheck"

REQUIRED_SUMMARY_COLUMNS = {
    "organism_std", "antimicrobial_std", "gene_symbol",
    "S", "R", "total_S", "total_R",
}


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if path.suffix.lower() in {".tsv", ".txt"}:
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path)


def _numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            out[col] = 0.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
    return out


def prepare_summary(summary: pd.DataFrame) -> pd.DataFrame:
    """Convert the original summary into auditable 2x2 counts."""
    missing = REQUIRED_SUMMARY_COLUMNS.difference(summary.columns)
    if missing:
        raise ValueError(f"knowledge_summary is missing columns: {sorted(missing)}")

    # CSV exports from earlier runs may contain repeated derived columns (for
    # example, an existing GPAS column followed by a newly calculated GPAS).
    # Keep the first occurrence and rebuild all derived quantities below.
    d = summary.loc[:, ~summary.columns.duplicated()].copy()
    stale_derived = [
        "gene_non_s", "total_non_s", "gene_total", "a", "b", "c", "d",
        "evidence_n", "total_all", "OR_corrected", "logOR", "logOR_SE",
        "logOR_CI_low", "logOR_CI_high", "fisher_p", "chi2", "chi2_p",
        "mutual_information", "confidence_weight", "GPAS",
        "evidence_direction", "GPAS_label",
    ]
    d = d.drop(columns=[c for c in stale_derived if c in d.columns])
    for col in ["organism_std", "antimicrobial_std", "gene_symbol"]:
        d[col] = d[col].astype(str).str.strip()

    # Original code defines gene_non_s = I + R and total_non_s = total_I + total_R.
    d = _numeric(d, ["S", "I", "R", "total_S", "total_I", "total_R"])
    d["gene_non_s"] = d["I"] + d["R"]
    d["total_non_s"] = d["total_I"] + d["total_R"]
    d["gene_total"] = d["S"] + d["I"] + d["R"]

    # Explicit 2x2 table:
    # a = gene-positive non-susceptible; b = gene-positive susceptible;
    # c = gene-negative non-susceptible; d = gene-negative susceptible.
    d["a"] = d["gene_non_s"]
    d["b"] = d["S"]
    d["c"] = d["total_non_s"] - d["a"]
    d["d"] = d["total_S"] - d["b"]

    if (d[["a", "b", "c", "d"]] < 0).any().any():
        bad = d.loc[(d[["a", "b", "c", "d"]] < 0).any(axis=1)]
        raise ValueError(
            "Negative 2x2 cells detected. Check whether total_S/total_R are "
            "complete phenotype denominators:\n" + bad.head().to_string(index=False)
        )

    d["evidence_n"] = d["gene_total"]
    d["total_all"] = d["total_S"] + d["total_non_s"]
    key_cols = ["organism_std", "antimicrobial_std", "gene_symbol"]
    if d.duplicated(key_cols).any():
        duplicated = d.loc[d.duplicated(key_cols, keep=False), key_cols]
        raise ValueError(
            "knowledge_summary must contain one row per organism-antimicrobial-gene "
            "combination; duplicate keys were found:\n"
            + duplicated.head(10).to_string(index=False)
        )
    return d


def mutual_information(a: float, b: float, c: float, d: float) -> float:
    table = np.asarray([[a, b], [c, d]], dtype=float)
    total = table.sum()
    if total <= 0:
        return np.nan
    p = table / total
    p_row = p.sum(axis=1, keepdims=True)
    p_col = p.sum(axis=0, keepdims=True)
    expected = p_row @ p_col
    mask = p > 0
    return float(np.sum(p[mask] * np.log(p[mask] / expected[mask])))


def add_statistics(d: pd.DataFrame, epsilon: float = 0.5) -> pd.DataFrame:
    out = d.copy()
    rows = []
    for a, b, c, dd in out[["a", "b", "c", "d"]].itertuples(index=False):
        a, b, c, dd = map(float, [a, b, c, dd])
        aa, bb, cc, ddc = [x + epsilon for x in [a, b, c, dd]]
        or_corrected = (aa * ddc) / (bb * cc)
        log_or = math.log(or_corrected)
        se = math.sqrt(1 / aa + 1 / bb + 1 / cc + 1 / ddc)
        try:
            _, fisher_p = fisher_exact([[a, b], [c, dd]], alternative="two-sided")
        except (ValueError, ZeroDivisionError):
            fisher_p = np.nan
        try:
            chi2, chi2_p, _, _ = chi2_contingency(
                [[a, b], [c, dd]], correction=False
            )
        except (ValueError, ZeroDivisionError):
            chi2, chi2_p = np.nan, np.nan
        rows.append({
            "OR_corrected": or_corrected,
            "logOR": log_or,
            "logOR_SE": se,
            "logOR_CI_low": log_or - 1.96 * se,
            "logOR_CI_high": log_or + 1.96 * se,
            "fisher_p": fisher_p,
            "chi2": chi2,
            "chi2_p": chi2_p,
            "mutual_information": mutual_information(a, b, c, dd),
        })
    return pd.concat([out.reset_index(drop=True), pd.DataFrame(rows)], axis=1)


def add_gpas(d: pd.DataFrame, k: float = DEFAULT_K,
             epsilon: float = DEFAULT_EPSILON) -> pd.DataFrame:
    out = add_statistics(d, epsilon=epsilon)
    n_gene = out["gene_total"]
    min_group = np.minimum(out["total_S"], out["total_non_s"])
    w_n = np.sqrt(n_gene / (n_gene + k))
    w_balance = np.sqrt(min_group / (min_group + k))
    out["confidence_weight"] = w_n * (0.5 + 0.5 * w_balance)
    out["GPAS"] = out["logOR"] * out["confidence_weight"]
    out["evidence_direction"] = np.select(
        [out["GPAS"] > 0.1, out["GPAS"] < -0.1],
        ["resistance", "susceptibility"],
        default="neutral",
    )
    out["GPAS_label"] = np.select(
        [
            out["GPAS"] >= 0.6,
            out["GPAS"] >= 0.3,
            out["GPAS"] >= 0.1,
            out["GPAS"] > -0.1,
            out["GPAS"] > -0.3,
            out["GPAS"] > -0.6,
        ],
        [
            "strong_resistance", "moderate_resistance", "weak_resistance",
            "neutral_or_uncertain", "weak_susceptibility",
            "moderate_susceptibility",
        ],
        default="strong_susceptibility",
    )
    return out


def add_fdr(d: pd.DataFrame) -> pd.DataFrame:
    out = d.copy()
    for p_col, q_col in [("fisher_p", "fisher_fdr"), ("chi2_p", "chi2_fdr")]:
        has_p_value = out[p_col].notna()
        out[q_col] = np.nan
        if has_p_value.any():
            out.loc[has_p_value, q_col] = multipletests(
                out.loc[has_p_value, p_col].astype(float), method="fdr_bh"
            )[1]
    return out


def benchmark_methods(d: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = d.copy()
    out["signed_neglog10_fisher"] = (
        np.sign(out["logOR"])
        * -np.log10(out["fisher_p"].clip(lower=np.finfo(float).tiny))
    )
    out["signed_chi2"] = np.sign(out["logOR"]) * out["chi2"]
    methods = {
        "GPAS": "GPAS",
        "logOR": "logOR", "OR_corrected": "OR_corrected",
        "signed_-log10_Fisher": "signed_neglog10_fisher",
        "signed_chi2": "signed_chi2",
        "mutual_information": "mutual_information",
    }
    # All organism-antimicrobial-gene combinations are retained. Methods are
    # compared on the same rows; rows with a method-specific missing statistic
    # are excluded only from that method's ranking.
    analysis = out.copy()
    rows = []
    for name, col in methods.items():
        has_score = analysis[col].notna()
        for frac in [0.01, 0.05, 0.10]:
            n_top = max(1, int(math.ceil(has_score.sum() * frac)))
            ranked = analysis.loc[has_score].nlargest(n_top, col)
            rows.append({
                "method": name,
                "top_fraction": frac,
                "n_associations": int(len(analysis)),
                "n_ranked": int(has_score.sum()),
                "n_top": n_top,
                "positive_direction_fraction": float(
                    (ranked["logOR"] > 0).mean()
                ),
            })

    corr = []
    for name, col in methods.items():
        # Self-correlation is not a benchmark and can return a matrix when
        # duplicate column names exist in legacy exports. Keep GPAS in the
        # ranking benchmark above, but omit it from the correlation table.
        if name == "GPAS":
            continue
        paired = analysis[["GPAS", col]].dropna()
        rho, p = (spearmanr(paired["GPAS"].to_numpy(), paired[col].to_numpy())
                  if len(paired) >= 3 else (np.nan, np.nan))
        corr.append({
            "method": name,
            "n_pairs": int(len(paired)),
            "Spearman_rho_vs_GPAS": rho,
            "p_value": p,
        })
    return pd.DataFrame(rows), pd.DataFrame(corr)


def binary_cohen_kappa(y_true: pd.Series, y_pred: pd.Series) -> tuple[float, float]:
    """Return Cohen's kappa and observed agreement for binary labels.

    The calculation uses the four cells directly rather than relying on the
    shape of a pandas crosstab. This guarantees a numeric result when one
    category is absent and returns kappa=1 for exactly identical labels.
    """
    pair = pd.DataFrame({"true": y_true, "pred": y_pred}).dropna()
    if pair.empty:
        return np.nan, np.nan
    true = pair["true"].astype(bool).to_numpy()
    pred = pair["pred"].astype(bool).to_numpy()
    n = float(len(pair))
    n00 = float((~true & ~pred).sum())
    n01 = float((~true & pred).sum())
    n10 = float((true & ~pred).sum())
    n11 = float((true & pred).sum())
    observed = (n00 + n11) / n
    expected = ((n00 + n01) * (n00 + n10) +
                (n10 + n11) * (n01 + n11)) / (n * n)
    if np.isclose(1.0 - expected, 0.0):
        # If both label vectors are identical, perfect agreement is the only
        # scientifically meaningful result even when both are constant.
        kappa = 1.0 if np.array_equal(true, pred) else np.nan
    else:
        kappa = (observed - expected) / (1.0 - expected)
    return float(kappa), float(observed)


def kappa_agreement(d: pd.DataFrame) -> pd.DataFrame:
    """Agreement of directional and top-K categorical decisions with GPAS.

    Directional Kappa uses a binary, explicitly defined category: score > 0
    versus score <= 0. Mutual information is excluded because it is unsigned.
    Top-K Kappa compares membership in each method's top 1%, 5% and 10% on
    the same pairwise-complete set.
    """
    out = d.copy()
    out["signed_neglog10_fisher"] = (
        np.sign(out["logOR"])
        * -np.log10(out["fisher_p"].clip(lower=np.finfo(float).tiny))
    )
    out["signed_chi2"] = np.sign(out["logOR"]) * out["chi2"]
    methods = {
        "logOR": "logOR",
        # OR and logOR have identical ordering; use log(OR) for direction.
        "OR_corrected": "logOR",
        "signed_-log10_Fisher": "signed_neglog10_fisher",
        "signed_chi2": "signed_chi2",
    }
    rows = []
    for name, col in methods.items():
        pair = out[["GPAS", col]].dropna()
        direction_kappa, direction_agreement = binary_cohen_kappa(
            pair["GPAS"] > 0, pair[col] > 0
        )
        rows.append({
            "comparison": name,
            "kappa_type": "positive_direction",
            "top_fraction": np.nan,
            "n_pairs": int(len(pair)),
            "cohen_kappa": direction_kappa,
            "observed_agreement": direction_agreement,
            "kappa_status": "computed" if pd.notna(direction_kappa) else "undefined_constant_margins",
        })
        for frac in [0.01, 0.05, 0.10]:
            n_top = max(1, int(math.ceil(len(pair) * frac)))
            gpas_top = pd.Series(False, index=pair.index)
            method_top = pd.Series(False, index=pair.index)
            gpas_top.loc[pair["GPAS"].nlargest(n_top).index] = True
            method_top.loc[pair[col].nlargest(n_top).index] = True
            rank_kappa, rank_agreement = binary_cohen_kappa(gpas_top, method_top)
            rows.append({
                "comparison": name,
                "kappa_type": "top_rank_membership",
                "top_fraction": frac,
                "n_pairs": int(len(pair)),
                "cohen_kappa": rank_kappa,
                "observed_agreement": rank_agreement,
                "kappa_status": "computed" if pd.notna(rank_kappa) else "undefined_constant_margins",
            })
    return pd.DataFrame(rows)


def load_gold(path: str | Path | None) -> pd.DataFrame | None:
    if not path:
        return None
    gold = read_table(Path(path))
    required = {
        "organism_std", "antimicrobial_std", "gene_symbol",
        "known_resistance", "reference",
    }
    missing = required.difference(gold.columns)
    if missing:
        raise ValueError(f"Gold-standard file missing columns: {sorted(missing)}")
    for col in ["organism_std", "antimicrobial_std", "gene_symbol"]:
        gold[col] = gold[col].astype(str).str.strip()
    gold["organism_std"] = gold["organism_std"].str.lower()
    gold["antimicrobial_std"] = gold["antimicrobial_std"].str.lower()
    gold["known_resistance"] = pd.to_numeric(
        gold["known_resistance"], errors="coerce"
    ).fillna(0).astype(int)
    return gold.drop_duplicates(
        ["organism_std", "antimicrobial_std", "gene_symbol"]
    )


def recover_known_relationships(d: pd.DataFrame, gold: pd.DataFrame) -> pd.DataFrame:
    keys = ["organism_std", "antimicrobial_std", "gene_symbol"]
    # Use the same complete association set for GPAS and comparator scores.
    x = d.merge(gold[keys + ["known_resistance", "reference"]],
                on=keys, how="left", validate="many_to_one")
    x["known_positive"] = x["known_resistance"].eq(1)
    n_pos = int(x["known_positive"].sum())
    if n_pos == 0:
        return pd.DataFrame([{"status": "no_gold_positive_matched"}])

    rows = []
    for score in ["GPAS", "logOR", "OR_corrected"]:
        ranked = x.dropna(subset=[score]).sort_values(score, ascending=False)
        n_ranked = len(ranked)
        for frac in [0.01, 0.05, 0.10]:
            n_top = max(1, int(math.ceil(n_ranked * frac)))
            top = ranked.head(n_top)
            hits = int(top["known_positive"].sum())
            expected = n_top * n_pos / n_ranked
            rows.append({
                "score": score, "top_fraction": frac,
                "n_ranked": n_ranked, "n_top": n_top,
                "known_positive_total": n_pos,
                "known_positive_hits": hits,
                "recall_at_top": hits / n_pos,
                "precision_at_top": hits / n_top,
                "enrichment_vs_random": hits / expected if expected else np.nan,
            })
        positions = np.flatnonzero(ranked["known_positive"].to_numpy()) + 1
        rows.append({
            "score": score, "top_fraction": np.nan,
            "n_ranked": n_ranked, "n_top": np.nan,
            "known_positive_total": n_pos,
            "median_rank_percentile": float(np.median(positions) / n_ranked)
            if len(positions) else np.nan,
        })
    return pd.DataFrame(rows)


def run_validation(summary: pd.DataFrame, output_dir: str | Path,
                   gold_path: str | Path | None = None) -> None:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[GPAS MODULE] {MODULE_VERSION}")
    print(f"[GPAS MODULE] output directory: {out_dir.resolve()}")

    summary = prepare_summary(summary)
    result = add_gpas(summary)
    result = add_fdr(result)
    result.to_csv(out_dir / "association_2x2_gpas_validated.tsv",
                  sep="\t", index=False)

    top_summary, correlations = benchmark_methods(result)
    top_summary.to_csv(out_dir / "conventional_method_benchmark.tsv",
                       sep="\t", index=False)
    correlations.to_csv(out_dir / "method_spearman_correlations.tsv",
                        sep="\t", index=False)
    kappa_result = kappa_agreement(result)
    required_kappa_columns = {
        "comparison", "kappa_type", "top_fraction", "n_pairs",
        "cohen_kappa", "observed_agreement", "kappa_status",
    }
    if not required_kappa_columns.issubset(kappa_result.columns):
        raise RuntimeError("Kappa output is missing required audit columns.")
    if kappa_result["cohen_kappa"].isna().all():
        raise RuntimeError(
            "All Cohen's kappa values are undefined. This is unexpected for "
            "the present GPAS comparison and indicates that the executed code "
            "or input columns do not match this validation module."
        )
    kappa_path = out_dir / "method_kappa_agreement.tsv"
    kappa_result.to_csv(kappa_path, sep="\t", index=False)
    print(
        "[GPAS MODULE] Kappa self-check: "
        f"{int(kappa_result['cohen_kappa'].notna().sum())}/"
        f"{len(kappa_result)} numeric; wrote {kappa_path}"
    )
    print(
        "[GPAS MODULE] benchmark methods: "
        + ", ".join(top_summary["method"].drop_duplicates().tolist())
    )

    # Full GPAS formula sensitivity, not the simplified evidence_n/(evidence_n+c)
    # approximation used in the original smoothing plot.
    sensitivity = []
    for epsilon in [0.1, 0.5, 1.0]:
        for k in [5.0, 10.0, 20.0]:
            x = add_gpas(summary, k=k, epsilon=epsilon)
            n_strong = int(x["GPAS_label"].eq("strong_resistance").sum())
            sensitivity.append({
                "epsilon": epsilon, "k": k,
                "mean_GPAS": x["GPAS"].mean(),
                "median_GPAS": x["GPAS"].median(),
                "n_associations": len(x),
                "n_positive_GPAS": int((x["GPAS"] > 0).sum()),
                "n_strong_resistance": n_strong,
                "strong_rate": n_strong / len(x) if len(x) else np.nan,
            })
    pd.DataFrame(sensitivity).to_csv(
        out_dir / "gpas_parameter_sensitivity.tsv", sep="\t", index=False
    )

    gold = load_gold(gold_path)
    if gold is not None:
        recover_known_relationships(result, gold).to_csv(
            out_dir / "known_relationship_recovery.tsv",
            sep="\t", index=False,
        )
        result.merge(
            gold,
            on=["organism_std", "antimicrobial_std", "gene_symbol"],
            how="left", validate="many_to_one",
        ).to_csv(out_dir / "association_with_gold_labels.tsv",
                 sep="\t", index=False)

    n_strong = int(result["GPAS_label"].eq("strong_resistance").sum())
    def package_version(name: str) -> str:
        try:
            return version(name)
        except PackageNotFoundError:
            return "not-installed"

    manifest = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "software_versions": {
            "pandas": package_version("pandas"),
            "numpy": package_version("numpy"),
            "scipy": package_version("scipy"),
            "statsmodels": package_version("statsmodels"),
        },
        "n_associations": int(len(result)),
        "n_strong_resistance": n_strong,
        "strong_rate": n_strong / len(result) if len(result) else None,
        "n_organisms": int(result["organism_std"].nunique()),
        "n_antimicrobials": int(result["antimicrobial_std"].nunique()),
        "n_genes": int(result["gene_symbol"].nunique()),
        "epsilon": DEFAULT_EPSILON,
        "k": DEFAULT_K,
        "non_susceptible_definition": "I + R",
        "evidence_n_definition": "S + I + R gene-positive isolates",
        "logOR_correction": "Haldane-Anscombe epsilon=0.5",
        "gpas_formula": (
            "logOR_HA * sqrt(n_gene/(n_gene+k)) * "
            "(0.5 + 0.5*sqrt(min(n_S,n_nonS)/(min(n_S,n_nonS)+k)))"
        ),
        "association_filter": "none; all non-negative 2x2 count rows retained",
        "gold_standard_provided": bool(gold is not None),
        "gold_standard_validation": (
            "known_relationship_recovery.tsv generated"
            if gold is not None else "not performed; no gold-standard input"
        ),
        "outputs": sorted(p.name for p in out_dir.iterdir()),
    }
    (out_dir / "gpas_validation_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


def _get_summary_for_pycharm() -> pd.DataFrame:
    if RUN_INDEPENDENTLY:
        if not SUMMARY_INPUT.strip():
            raise ValueError("Set SUMMARY_INPUT before independent PyCharm run.")
        return read_table(Path(SUMMARY_INPUT))
    if "knowledge_summary" not in globals():
        raise RuntimeError(
            "knowledge_summary is unavailable. Append this module after the "
            "original script or set RUN_INDEPENDENTLY=True."
        )
    return globals()["knowledge_summary"]


if __name__ == "__main__":
    run_validation(
        _get_summary_for_pycharm(),
        OUTPUT_DIR,
        GOLD_STANDARD_INPUT or None,
    )



###########################################################
from __future__ import annotations
import json
import math
import sys
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, spearmanr
from statsmodels.stats.multitest import multipletests


import os
os.chdir('/public8/lilab/student/htang/SMART/临床重要耐药菌基因型表型数据库/ARMD/merge2/merge3/EBI_CNSZ_AMR/0730')
# ============================================================================
# PyCharm settings
# ============================================================================
RUN_INDEPENDENTLY = True
SUMMARY_INPUT = r"ebi_knowledge_summary_0730.csv"  # Used only when RUN_INDEPENDENTLY=True
GOLD_STANDARD_INPUT = r""  # Optional independent known AMR relationships
OUTPUT_DIR = r"gpas_validation"
DEFAULT_K = 10.0
DEFAULT_EPSILON = 0.5
MODULE_VERSION = "GPAS-validation-2026-09-01-kappa-direct-counts-selfcheck"

REQUIRED_SUMMARY_COLUMNS = {
    "organism_std", "antimicrobial_std", "gene_symbol",
    "S", "R", "total_S", "total_R",
}


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if path.suffix.lower() in {".tsv", ".txt"}:
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path)


def _numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            out[col] = 0.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
    return out


def prepare_summary(summary: pd.DataFrame) -> pd.DataFrame:
    """Convert the original summary into auditable 2x2 counts."""
    missing = REQUIRED_SUMMARY_COLUMNS.difference(summary.columns)
    if missing:
        raise ValueError(f"knowledge_summary is missing columns: {sorted(missing)}")

    # CSV exports from earlier runs may contain repeated derived columns (for
    # example, an existing GPAS column followed by a newly calculated GPAS).
    # Keep the first occurrence and rebuild all derived quantities below.
    d = summary.loc[:, ~summary.columns.duplicated()].copy()
    stale_derived = [
        "gene_non_s", "total_non_s", "gene_total", "a", "b", "c", "d",
        "evidence_n", "total_all", "OR_corrected", "logOR", "logOR_SE",
        "logOR_CI_low", "logOR_CI_high", "fisher_p", "chi2", "chi2_p",
        "mutual_information", "confidence_weight", "GPAS",
        "evidence_direction", "GPAS_label",
    ]
    d = d.drop(columns=[c for c in stale_derived if c in d.columns])
    for col in ["organism_std", "antimicrobial_std", "gene_symbol"]:
        d[col] = d[col].astype(str).str.strip()

    # Original code defines gene_non_s = I + R and total_non_s = total_I + total_R.
    d = _numeric(d, ["S", "I", "R", "total_S", "total_I", "total_R"])
    d["gene_non_s"] = d["I"] + d["R"]
    d["total_non_s"] = d["total_I"] + d["total_R"]
    d["gene_total"] = d["S"] + d["I"] + d["R"]

    # Explicit 2x2 table:
    # a = gene-positive non-susceptible; b = gene-positive susceptible;
    # c = gene-negative non-susceptible; d = gene-negative susceptible.
    d["a"] = d["gene_non_s"]
    d["b"] = d["S"]
    d["c"] = d["total_non_s"] - d["a"]
    d["d"] = d["total_S"] - d["b"]

    if (d[["a", "b", "c", "d"]] < 0).any().any():
        bad = d.loc[(d[["a", "b", "c", "d"]] < 0).any(axis=1)]
        raise ValueError(
            "Negative 2x2 cells detected. Check whether total_S/total_R are "
            "complete phenotype denominators:\n" + bad.head().to_string(index=False)
        )

    d["evidence_n"] = d["gene_total"]
    d["total_all"] = d["total_S"] + d["total_non_s"]
    key_cols = ["organism_std", "antimicrobial_std", "gene_symbol"]
    if d.duplicated(key_cols).any():
        duplicated = d.loc[d.duplicated(key_cols, keep=False), key_cols]
        raise ValueError(
            "knowledge_summary must contain one row per organism-antimicrobial-gene "
            "combination; duplicate keys were found:\n"
            + duplicated.head(10).to_string(index=False)
        )
    return d


def mutual_information(a: float, b: float, c: float, d: float) -> float:
    table = np.asarray([[a, b], [c, d]], dtype=float)
    total = table.sum()
    if total <= 0:
        return np.nan
    p = table / total
    p_row = p.sum(axis=1, keepdims=True)
    p_col = p.sum(axis=0, keepdims=True)
    expected = p_row @ p_col
    mask = p > 0
    return float(np.sum(p[mask] * np.log(p[mask] / expected[mask])))


def add_statistics(d: pd.DataFrame, epsilon: float = 0.5) -> pd.DataFrame:
    out = d.copy()
    rows = []
    for a, b, c, dd in out[["a", "b", "c", "d"]].itertuples(index=False):
        a, b, c, dd = map(float, [a, b, c, dd])
        aa, bb, cc, ddc = [x + epsilon for x in [a, b, c, dd]]
        or_corrected = (aa * ddc) / (bb * cc)
        log_or = math.log(or_corrected)
        se = math.sqrt(1 / aa + 1 / bb + 1 / cc + 1 / ddc)
        try:
            _, fisher_p = fisher_exact([[a, b], [c, dd]], alternative="two-sided")
        except (ValueError, ZeroDivisionError):
            fisher_p = np.nan
        try:
            chi2, chi2_p, _, _ = chi2_contingency(
                [[a, b], [c, dd]], correction=False
            )
        except (ValueError, ZeroDivisionError):
            chi2, chi2_p = np.nan, np.nan
        rows.append({
            "OR_corrected": or_corrected,
            "logOR": log_or,
            "logOR_SE": se,
            "logOR_CI_low": log_or - 1.96 * se,
            "logOR_CI_high": log_or + 1.96 * se,
            "fisher_p": fisher_p,
            "chi2": chi2,
            "chi2_p": chi2_p,
            "mutual_information": mutual_information(a, b, c, dd),
        })
    return pd.concat([out.reset_index(drop=True), pd.DataFrame(rows)], axis=1)


def add_gpas(d: pd.DataFrame, k: float = DEFAULT_K,
             epsilon: float = DEFAULT_EPSILON) -> pd.DataFrame:
    out = add_statistics(d, epsilon=epsilon)
    n_gene = out["gene_total"]
    min_group = np.minimum(out["total_S"], out["total_non_s"])
    w_n = np.sqrt(n_gene / (n_gene + k))
    w_balance = np.sqrt(min_group / (min_group + k))
    out["confidence_weight"] = w_n * (0.5 + 0.5 * w_balance)
    out["GPAS"] = out["logOR"] * out["confidence_weight"]
    out["evidence_direction"] = np.select(
        [out["GPAS"] > 0.1, out["GPAS"] < -0.1],
        ["resistance", "susceptibility"],
        default="neutral",
    )
    out["GPAS_label"] = np.select(
        [
            out["GPAS"] >= 0.6,
            out["GPAS"] >= 0.3,
            out["GPAS"] >= 0.1,
            out["GPAS"] > -0.1,
            out["GPAS"] > -0.3,
            out["GPAS"] > -0.6,
        ],
        [
            "strong_resistance", "moderate_resistance", "weak_resistance",
            "neutral_or_uncertain", "weak_susceptibility",
            "moderate_susceptibility",
        ],
        default="strong_susceptibility",
    )
    return out


def add_fdr(d: pd.DataFrame) -> pd.DataFrame:
    out = d.copy()
    for p_col, q_col in [("fisher_p", "fisher_fdr"), ("chi2_p", "chi2_fdr")]:
        has_p_value = out[p_col].notna()
        out[q_col] = np.nan
        if has_p_value.any():
            out.loc[has_p_value, q_col] = multipletests(
                out.loc[has_p_value, p_col].astype(float), method="fdr_bh"
            )[1]
    return out


def benchmark_methods(d: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = d.copy()
    out["signed_neglog10_fisher"] = (
        np.sign(out["logOR"])
        * -np.log10(out["fisher_p"].clip(lower=np.finfo(float).tiny))
    )
    out["signed_chi2"] = np.sign(out["logOR"]) * out["chi2"]
    methods = {
        "GPAS": "GPAS",
        "logOR": "logOR", "OR_corrected": "OR_corrected",
        "signed_-log10_Fisher": "signed_neglog10_fisher",
        "signed_chi2": "signed_chi2",
        "mutual_information": "mutual_information",
    }
    # All organism-antimicrobial-gene combinations are retained. Methods are
    # compared on the same rows; rows with a method-specific missing statistic
    # are excluded only from that method's ranking.
    analysis = out.copy()
    rows = []
    for name, col in methods.items():
        has_score = analysis[col].notna()
        for frac in [0.01, 0.05, 0.10]:
            n_top = max(1, int(math.ceil(has_score.sum() * frac)))
            ranked = analysis.loc[has_score].nlargest(n_top, col)
            rows.append({
                "method": name,
                "top_fraction": frac,
                "n_associations": int(len(analysis)),
                "n_ranked": int(has_score.sum()),
                "n_top": n_top,
                "positive_direction_fraction": float(
                    (ranked["logOR"] > 0).mean()
                ),
            })

    corr = []
    for name, col in methods.items():
        # Self-correlation is not a benchmark and can return a matrix when
        # duplicate column names exist in legacy exports. Keep GPAS in the
        # ranking benchmark above, but omit it from the correlation table.
        if name == "GPAS":
            continue
        paired = analysis[["GPAS", col]].dropna()
        rho, p = (spearmanr(paired["GPAS"].to_numpy(), paired[col].to_numpy())
                  if len(paired) >= 3 else (np.nan, np.nan))
        corr.append({
            "method": name,
            "n_pairs": int(len(paired)),
            "Spearman_rho_vs_GPAS": rho,
            "p_value": p,
        })
    return pd.DataFrame(rows), pd.DataFrame(corr)


def binary_cohen_kappa(y_true: pd.Series, y_pred: pd.Series) -> tuple[float, float]:
    """Return Cohen's kappa and observed agreement for binary labels.

    The calculation uses the four cells directly rather than relying on the
    shape of a pandas crosstab. This guarantees a numeric result when one
    category is absent and returns kappa=1 for exactly identical labels.
    """
    pair = pd.DataFrame({"true": y_true, "pred": y_pred}).dropna()
    if pair.empty:
        return np.nan, np.nan
    true = pair["true"].astype(bool).to_numpy()
    pred = pair["pred"].astype(bool).to_numpy()
    n = float(len(pair))
    n00 = float((~true & ~pred).sum())
    n01 = float((~true & pred).sum())
    n10 = float((true & ~pred).sum())
    n11 = float((true & pred).sum())
    observed = (n00 + n11) / n
    expected = ((n00 + n01) * (n00 + n10) +
                (n10 + n11) * (n01 + n11)) / (n * n)
    if np.isclose(1.0 - expected, 0.0):
        # If both label vectors are identical, perfect agreement is the only
        # scientifically meaningful result even when both are constant.
        kappa = 1.0 if np.array_equal(true, pred) else np.nan
    else:
        kappa = (observed - expected) / (1.0 - expected)
    return float(kappa), float(observed)


def kappa_agreement(d: pd.DataFrame) -> pd.DataFrame:
    """Agreement of directional and top-K categorical decisions with GPAS.

    Directional Kappa uses a binary, explicitly defined category: score > 0
    versus score <= 0. Mutual information is excluded because it is unsigned.
    Top-K Kappa compares membership in each method's top 1%, 5% and 10% on
    the same pairwise-complete set.
    """
    out = d.copy()
    out["signed_neglog10_fisher"] = (
        np.sign(out["logOR"])
        * -np.log10(out["fisher_p"].clip(lower=np.finfo(float).tiny))
    )
    out["signed_chi2"] = np.sign(out["logOR"]) * out["chi2"]
    methods = {
        "logOR": "logOR",
        # OR and logOR have identical ordering; use log(OR) for direction.
        "OR_corrected": "logOR",
        "signed_-log10_Fisher": "signed_neglog10_fisher",
        "signed_chi2": "signed_chi2",
    }
    rows = []
    for name, col in methods.items():
        pair = out[["GPAS", col]].dropna()
        direction_kappa, direction_agreement = binary_cohen_kappa(
            pair["GPAS"] > 0, pair[col] > 0
        )
        rows.append({
            "comparison": name,
            "kappa_type": "positive_direction",
            "top_fraction": np.nan,
            "n_pairs": int(len(pair)),
            "cohen_kappa": direction_kappa,
            "observed_agreement": direction_agreement,
            "kappa_status": "computed" if pd.notna(direction_kappa) else "undefined_constant_margins",
        })
        for frac in [0.01, 0.05, 0.10]:
            n_top = max(1, int(math.ceil(len(pair) * frac)))
            gpas_top = pd.Series(False, index=pair.index)
            method_top = pd.Series(False, index=pair.index)
            gpas_top.loc[pair["GPAS"].nlargest(n_top).index] = True
            method_top.loc[pair[col].nlargest(n_top).index] = True
            rank_kappa, rank_agreement = binary_cohen_kappa(gpas_top, method_top)
            rows.append({
                "comparison": name,
                "kappa_type": "top_rank_membership",
                "top_fraction": frac,
                "n_pairs": int(len(pair)),
                "cohen_kappa": rank_kappa,
                "observed_agreement": rank_agreement,
                "kappa_status": "computed" if pd.notna(rank_kappa) else "undefined_constant_margins",
            })
    return pd.DataFrame(rows)


def load_gold(path: str | Path | None) -> pd.DataFrame | None:
    if not path:
        return None
    gold = read_table(Path(path))
    required = {
        "organism_std", "antimicrobial_std", "gene_symbol",
        "known_resistance", "reference",
    }
    missing = required.difference(gold.columns)
    if missing:
        raise ValueError(f"Gold-standard file missing columns: {sorted(missing)}")
    for col in ["organism_std", "antimicrobial_std", "gene_symbol"]:
        gold[col] = gold[col].astype(str).str.strip()
    gold["organism_std"] = gold["organism_std"].str.lower()
    gold["antimicrobial_std"] = gold["antimicrobial_std"].str.lower()
    gold["known_resistance"] = pd.to_numeric(
        gold["known_resistance"], errors="coerce"
    ).fillna(0).astype(int)
    return gold.drop_duplicates(
        ["organism_std", "antimicrobial_std", "gene_symbol"]
    )


def recover_known_relationships(d: pd.DataFrame, gold: pd.DataFrame) -> pd.DataFrame:
    keys = ["organism_std", "antimicrobial_std", "gene_symbol"]
    # Use the same complete association set for GPAS and comparator scores.
    x = d.merge(gold[keys + ["known_resistance", "reference"]],
                on=keys, how="left", validate="many_to_one")
    x["known_positive"] = x["known_resistance"].eq(1)
    n_pos = int(x["known_positive"].sum())
    if n_pos == 0:
        return pd.DataFrame([{"status": "no_gold_positive_matched"}])

    rows = []
    for score in ["GPAS", "logOR", "OR_corrected"]:
        ranked = x.dropna(subset=[score]).sort_values(score, ascending=False)
        n_ranked = len(ranked)
        for frac in [0.01, 0.05, 0.10]:
            n_top = max(1, int(math.ceil(n_ranked * frac)))
            top = ranked.head(n_top)
            hits = int(top["known_positive"].sum())
            expected = n_top * n_pos / n_ranked
            rows.append({
                "score": score, "top_fraction": frac,
                "n_ranked": n_ranked, "n_top": n_top,
                "known_positive_total": n_pos,
                "known_positive_hits": hits,
                "recall_at_top": hits / n_pos,
                "precision_at_top": hits / n_top,
                "enrichment_vs_random": hits / expected if expected else np.nan,
            })
        positions = np.flatnonzero(ranked["known_positive"].to_numpy()) + 1
        rows.append({
            "score": score, "top_fraction": np.nan,
            "n_ranked": n_ranked, "n_top": np.nan,
            "known_positive_total": n_pos,
            "median_rank_percentile": float(np.median(positions) / n_ranked)
            if len(positions) else np.nan,
        })
    return pd.DataFrame(rows)



def calculate_ranking_stability(
    summary: pd.DataFrame,
    output_dir: str | Path,
    epsilons: list[float] | None = None,
    k_values: list[float] | None = None,
    default_epsilon: float = DEFAULT_EPSILON,
    default_k: float = DEFAULT_K,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Evaluate GPAS ranking stability across epsilon/k parameter settings.

    The default configuration (epsilon=0.5, k=10) is used as the reference.
    For each alternative configuration, report:
      - Spearman rho versus the default GPAS ranking
      - overlap of the default top 1%, 5%, and 10% sets

    Top-k overlap is defined as:
        |TopK_alternative ∩ TopK_default| / |TopK_default| * 100
    """
    if epsilons is None:
        epsilons = [0.1, 0.5, 1.0]
    if k_values is None:
        k_values = [5.0, 10.0, 20.0]

    key_cols = ["organism_std", "antimicrobial_std", "gene_symbol"]
    top_fracs = {
        "Top_1pct_overlap": 0.01,
        "Top_5pct_overlap": 0.05,
        "Top_10pct_overlap": 0.10,
    }

    # Default GPAS
    default = add_gpas(
        summary,
        k=default_k,
        epsilon=default_epsilon,
    )[key_cols + ["GPAS"]].copy()

    default = (
        default
        .sort_values("GPAS", ascending=False, kind="mergesort")
        .reset_index(drop=True)
    )

    n_total = len(default)

    def top_key_set(df: pd.DataFrame, fraction: float) -> set[tuple]:
        n_top = max(1, int(math.ceil(len(df) * fraction)))
        return set(map(tuple, df.loc[:n_top - 1, key_cols].to_numpy()))

    default_top_sets = {
        label: top_key_set(default, frac)
        for label, frac in top_fracs.items()
    }

    ranking_rows = []
    ranking_tables = {}

    for epsilon in epsilons:
        for k in k_values:
            current = add_gpas(
                summary,
                k=k,
                epsilon=epsilon,
            )[key_cols + ["GPAS"]].copy()

            current = (
                current
                .sort_values("GPAS", ascending=False, kind="mergesort")
                .reset_index(drop=True)
            )

            # Audit that every parameter setting contains the same association set.
            if len(current) != n_total:
                raise RuntimeError(
                    f"Association count changed for epsilon={epsilon}, k={k}: "
                    f"{len(current)} vs default {n_total}."
                )

            default_keys = set(map(tuple, default[key_cols].to_numpy()))
            current_keys = set(map(tuple, current[key_cols].to_numpy()))

            if default_keys != current_keys:
                raise RuntimeError(
                    f"Association keys changed for epsilon={epsilon}, k={k}."
                )

            merged = default.merge(
                current,
                on=key_cols,
                how="inner",
                validate="one_to_one",
                suffixes=("_default", "_current"),
            )

            if len(merged) != n_total:
                raise RuntimeError(
                    f"Ranking merge incomplete for epsilon={epsilon}, k={k}: "
                    f"{len(merged)} vs {n_total}."
                )

            rho, p_value = spearmanr(
                merged["GPAS_default"].to_numpy(),
                merged["GPAS_current"].to_numpy(),
            )

            current_top_sets = {
                label: top_key_set(current, frac)
                for label, frac in top_fracs.items()
            }

            overlaps = {}
            for label in top_fracs:
                ref_set = default_top_sets[label]
                alt_set = current_top_sets[label]
                overlaps[label] = (
                    len(ref_set & alt_set) / len(ref_set) * 100
                    if ref_set else np.nan
                )

            ranking_rows.append({
                "epsilon": float(epsilon),
                "k": float(k),
                "n_associations": int(len(current)),
                "mean_GPAS": float(current["GPAS"].mean()),
                "median_GPAS": float(current["GPAS"].median()),
                "n_positive_GPAS": int((current["GPAS"] > 0).sum()),
                "n_strong_resistance": int(
                    add_gpas(summary, k=k, epsilon=epsilon)["GPAS_label"]
                    .eq("strong_resistance")
                    .sum()
                ),
                "strong_rate": float(
                    add_gpas(summary, k=k, epsilon=epsilon)["GPAS_label"]
                    .eq("strong_resistance")
                    .mean()
                ),
                "Spearman_rho_vs_default": float(rho),
                "Spearman_p_vs_default": float(p_value),
                "Top_1pct_overlap": float(overlaps["Top_1pct_overlap"]),
                "Top_5pct_overlap": float(overlaps["Top_5pct_overlap"]),
                "Top_10pct_overlap": float(overlaps["Top_10pct_overlap"]),
                "is_default": bool(
                    np.isclose(epsilon, default_epsilon)
                    and np.isclose(k, default_k)
                ),
            })

            ranking_tables[(float(epsilon), float(k))] = current

    stability_df = (
        pd.DataFrame(ranking_rows)
        .sort_values(["epsilon", "k"])
        .reset_index(drop=True)
    )

    # ------------------------------------------------------------
    # All-vs-all Spearman correlation matrix across 9 settings
    # ------------------------------------------------------------
    settings = list(ranking_tables.keys())
    labels = [f"eps{eps:g}_k{k:g}" for eps, k in settings]

    rank_matrix = pd.DataFrame(index=labels, columns=labels, dtype=float)

    for i, setting_i in enumerate(settings):
        for j, setting_j in enumerate(settings):
            if i == j:
                rho = 1.0
            else:
                left = ranking_tables[setting_i]["GPAS"].to_numpy()
                right = ranking_tables[setting_j]["GPAS"].to_numpy()
                rho, _ = spearmanr(left, right)
            rank_matrix.iloc[i, j] = rho

    rank_matrix.index.name = "parameter_setting"
    rank_matrix.columns.name = "parameter_setting"

    out_dir = Path(output_dir)
    stability_df.to_csv(
        out_dir / "gpas_parameter_sensitivity_ranking_stability.tsv",
        sep="\t",
        index=False,
    )
    rank_matrix.to_csv(
        out_dir / "gpas_parameter_ranking_spearman_matrix.tsv",
        sep="\t",
    )

    return stability_df, rank_matrix


def plot_ranking_stability_heatmap(
    rank_matrix: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    """
    Save a publication-oriented Spearman correlation heatmap.
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(
        figsize=(9, 8),
        constrained_layout=True,
    )

    im = ax.imshow(
        rank_matrix.to_numpy(dtype=float),
        vmin=0.0,
        vmax=1.0,
        aspect="auto",
    )

    labels = list(rank_matrix.index)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)

    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(
                j,
                i,
                f"{rank_matrix.iloc[i, j]:.3f}",
                ha="center",
                va="center",
                fontsize=8,
            )

    ax.set_xlabel("GPAS parameter setting")
    ax.set_ylabel("GPAS parameter setting")
    ax.set_title("GPAS ranking stability across parameter settings")
    fig.colorbar(im, ax=ax, label="Spearman correlation")

    path = Path(output_dir) / "Figure_SxB_GPAS_ranking_stability_heatmap.pdf"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)

def run_validation(summary: pd.DataFrame, output_dir: str | Path,
                   gold_path: str | Path | None = None) -> None:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[GPAS MODULE] {MODULE_VERSION}")
    print(f"[GPAS MODULE] output directory: {out_dir.resolve()}")

    summary = prepare_summary(summary)
    result = add_gpas(summary)
    result = add_fdr(result)
    result.to_csv(out_dir / "association_2x2_gpas_validated.tsv",
                  sep="\t", index=False)

    top_summary, correlations = benchmark_methods(result)
    top_summary.to_csv(out_dir / "conventional_method_benchmark.tsv",
                       sep="\t", index=False)
    correlations.to_csv(out_dir / "method_spearman_correlations.tsv",
                        sep="\t", index=False)
    kappa_result = kappa_agreement(result)
    required_kappa_columns = {
        "comparison", "kappa_type", "top_fraction", "n_pairs",
        "cohen_kappa", "observed_agreement", "kappa_status",
    }
    if not required_kappa_columns.issubset(kappa_result.columns):
        raise RuntimeError("Kappa output is missing required audit columns.")
    if kappa_result["cohen_kappa"].isna().all():
        raise RuntimeError(
            "All Cohen's kappa values are undefined. This is unexpected for "
            "the present GPAS comparison and indicates that the executed code "
            "or input columns do not match this validation module."
        )
    kappa_path = out_dir / "method_kappa_agreement.tsv"
    kappa_result.to_csv(kappa_path, sep="\t", index=False)
    print(
        "[GPAS MODULE] Kappa self-check: "
        f"{int(kappa_result['cohen_kappa'].notna().sum())}/"
        f"{len(kappa_result)} numeric; wrote {kappa_path}"
    )
    print(
        "[GPAS MODULE] benchmark methods: "
        + ", ".join(top_summary["method"].drop_duplicates().tolist())
    )

    # Full GPAS formula sensitivity and ranking stability.
    # The default configuration (epsilon=0.5, k=10) is used as the
    # reference for Spearman rank correlation and top-k overlap.
    stability_df, rank_matrix = calculate_ranking_stability(
        summary=summary,
        output_dir=out_dir,
        epsilons=[0.1, 0.5, 1.0],
        k_values=[5.0, 10.0, 20.0],
        default_epsilon=DEFAULT_EPSILON,
        default_k=DEFAULT_K,
    )

    # Keep the original sensitivity output for backward compatibility.
    stability_df.to_csv(
        out_dir / "gpas_parameter_sensitivity.tsv",
        sep="\t",
        index=False,
    )

    # Save the 9 x 9 all-vs-all ranking correlation matrix.
    # A PDF heatmap is generated as an additional supplementary figure.
    plot_ranking_stability_heatmap(
        rank_matrix,
        out_dir,
    )

    print(
        "[GPAS MODULE] ranking stability table: "
        f"{out_dir / 'gpas_parameter_sensitivity_ranking_stability.tsv'}"
    )
    print(
        "[GPAS MODULE] all-vs-all Spearman matrix: "
        f"{out_dir / 'gpas_parameter_ranking_spearman_matrix.tsv'}"
    )
    print(
        "[GPAS MODULE] ranking stability heatmap: "
        f"{out_dir / 'Figure_SxB_GPAS_ranking_stability_heatmap.pdf'}"
    )

    gold = load_gold(gold_path)
    if gold is not None:
        recover_known_relationships(result, gold).to_csv(
            out_dir / "known_relationship_recovery.tsv",
            sep="\t", index=False,
        )
        result.merge(
            gold,
            on=["organism_std", "antimicrobial_std", "gene_symbol"],
            how="left", validate="many_to_one",
        ).to_csv(out_dir / "association_with_gold_labels.tsv",
                 sep="\t", index=False)

    n_strong = int(result["GPAS_label"].eq("strong_resistance").sum())
    def package_version(name: str) -> str:
        try:
            return version(name)
        except PackageNotFoundError:
            return "not-installed"

    manifest = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "software_versions": {
            "pandas": package_version("pandas"),
            "numpy": package_version("numpy"),
            "scipy": package_version("scipy"),
            "statsmodels": package_version("statsmodels"),
        },
        "n_associations": int(len(result)),
        "n_strong_resistance": n_strong,
        "strong_rate": n_strong / len(result) if len(result) else None,
        "n_organisms": int(result["organism_std"].nunique()),
        "n_antimicrobials": int(result["antimicrobial_std"].nunique()),
        "n_genes": int(result["gene_symbol"].nunique()),
        "epsilon": DEFAULT_EPSILON,
        "k": DEFAULT_K,
        "non_susceptible_definition": "I + R",
        "evidence_n_definition": "S + I + R gene-positive isolates",
        "logOR_correction": "Haldane-Anscombe epsilon=0.5",
        "gpas_formula": (
            "logOR_HA * sqrt(n_gene/(n_gene+k)) * "
            "(0.5 + 0.5*sqrt(min(n_S,n_nonS)/(min(n_S,n_nonS)+k)))"
        ),
        "association_filter": "none; all non-negative 2x2 count rows retained",
        "ranking_stability_reference": "epsilon=0.5, k=10",
        "ranking_stability_metrics": (
            "Spearman rank correlation and top 1%, 5%, and 10% overlap "
            "relative to the default parameter setting"
        ),
        "gold_standard_provided": bool(gold is not None),
        "gold_standard_validation": (
            "known_relationship_recovery.tsv generated"
            if gold is not None else "not performed; no gold-standard input"
        ),
        "outputs": sorted(p.name for p in out_dir.iterdir()),
    }
    (out_dir / "gpas_validation_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


def _get_summary_for_pycharm() -> pd.DataFrame:
    if RUN_INDEPENDENTLY:
        if not SUMMARY_INPUT.strip():
            raise ValueError("Set SUMMARY_INPUT before independent PyCharm run.")
        return read_table(Path(SUMMARY_INPUT))
    if "knowledge_summary" not in globals():
        raise RuntimeError(
            "knowledge_summary is unavailable. Append this module after the "
            "original script or set RUN_INDEPENDENTLY=True."
        )
    return globals()["knowledge_summary"]


if __name__ == "__main__":
    run_validation(
        _get_summary_for_pycharm(),
        OUTPUT_DIR,
        GOLD_STANDARD_INPUT or None,
    )



#######################################################################################
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# 1. Read GPAS sensitivity summary
# ============================================================

input_file = "./gpas_validation/gpas_parameter_sensitivity.tsv"

df_gpas = pd.read_csv(
    input_file,
    sep="\t"
)

print(df_gpas)


# ============================================================
# 2. Create parameter labels
# ============================================================

df_gpas["Setting"] = (
    "ε=" +
    df_gpas["epsilon"].map(lambda x: f"{x:g}") +
    ", k=" +
    df_gpas["k"].map(lambda x: f"{x:g}")
)

# 保持 epsilon -> k 的固定顺序
df_gpas = df_gpas.sort_values(
    ["epsilon", "k"]
).reset_index(drop=True)

labels = df_gpas["Setting"].tolist()


# ============================================================
# 3. Identify default
# ============================================================

default_row = df_gpas[df_gpas["is_default"] == True]

if len(default_row) != 1:
    raise ValueError(
        f"Expected exactly one default setting, "
        f"but found {len(default_row)}"
    )

default_label = default_row.iloc[0]["Setting"]

print("\nDefault setting:", default_label)


# ============================================================
# 4. Output summary
# ============================================================

print("\nGPAS parameter sensitivity:")
print(
    df_gpas[
        [
            "Setting",
            "mean_GPAS",
            "median_GPAS",
            "strong_rate",
            "Spearman_rho_vs_default",
            "Top_1pct_overlap",
            "Top_5pct_overlap",
            "Top_10pct_overlap"
        ]
    ].to_string(index=False)
)


# ============================================================
# 5. Figure
# ============================================================

fig, axes = plt.subplots(
    1,
    2,
    figsize=(13, 5.5)
)


# ============================================================
# Panel A
# Median GPAS
# ============================================================

ax = axes[0]

sns.barplot(
    data=df_gpas,
    x="Setting",
    y="median_GPAS",
    order=labels,
    errorbar=None,
    ax=ax
)

ax.axhline(
    default_row.iloc[0]["median_GPAS"],
    linestyle="--",
    linewidth=1.2,
    label=f"Default: {default_label}"
)

ax.set_xlabel("")
ax.set_ylabel("Median GPAS", fontsize=12)

ax.set_title(
    "GPAS score sensitivity",
    fontsize=13,
    fontweight="bold",
    loc="left"
)

ax.set_xticklabels(
    labels,
    rotation=45,
    ha="right"
)

ax.tick_params(
    axis="both",
    labelsize=10
)

ax.grid(
    axis="y",
    linestyle="--",
    linewidth=0.5,
    alpha=0.4
)

ax.legend(
    frameon=False,
    fontsize=9
)

sns.despine(ax=ax)


# ============================================================
# Add median values
# ============================================================

for i, row in df_gpas.iterrows():

    ax.text(
        i,
        row["median_GPAS"],
        f'{row["median_GPAS"]:.3f}',
        ha="center",
        va="bottom",
        fontsize=8
    )


# ============================================================
# Panel B
# Ranking stability
# ============================================================

ax = axes[1]

sns.barplot(
    data=df_gpas,
    x="Setting",
    y="Spearman_rho_vs_default",
    order=labels,
    errorbar=None,
    ax=ax
)

ax.axhline(
    1.0,
    linestyle="--",
    linewidth=1,
    alpha=0.6
)

ax.set_ylim(
    min(0.90, df_gpas["Spearman_rho_vs_default"].min() - 0.01),
    1.005
)

ax.set_xlabel("")
ax.set_ylabel("Spearman correlation (ρ)", fontsize=12)

ax.set_title(
    "Ranking stability",
    fontsize=13,
    fontweight="bold",
    loc="left"
)

ax.set_xticklabels(
    labels,
    rotation=45,
    ha="right"
)

ax.tick_params(
    axis="both",
    labelsize=10
)

ax.grid(
    axis="y",
    linestyle="--",
    linewidth=0.5,
    alpha=0.4
)

sns.despine(ax=ax)


# ============================================================
# Add rho values
# ============================================================

for i, row in df_gpas.iterrows():

    ax.text(
        i,
        row["Spearman_rho_vs_default"] + 0.001,
        f'{row["Spearman_rho_vs_default"]:.3f}',
        ha="center",
        va="bottom",
        fontsize=8
    )


# ============================================================
# Panel labels
# ============================================================

axes[0].text(
    -0.12,
    1.05,
    "A",
    transform=axes[0].transAxes,
    fontsize=16,
    fontweight="bold",
    va="top"
)

axes[1].text(
    -0.12,
    1.05,
    "B",
    transform=axes[1].transAxes,
    fontsize=16,
    fontweight="bold",
    va="top"
)


# ============================================================
# Layout
# ============================================================

plt.tight_layout()


# ============================================================
# Save
# ============================================================

outdir = "./gpas_validation"

plt.savefig(
    os.path.join(
        outdir,
        "Supplementary_Figure_Sx_GPAS_parameter_sensitivity.pdf"
    ),
    bbox_inches="tight"
)

plt.savefig(
    os.path.join(
        outdir,
        "Supplementary_Figure_Sx_GPAS_parameter_sensitivity.tiff"
    ),
    dpi=600,
    bbox_inches="tight"
)

plt.savefig(
    os.path.join(
        outdir,
        "Supplementary_Figure_Sx_GPAS_parameter_sensitivity.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()




############################################reviewer 4########################################################
# ============================================================
# GPAS percentile-based classification validation
# Reviewer #4 validation
#
# Analyses:
#   1. GPAS percentile vs absolute effect size
#   2. Literature support rate across GPAS percentile groups
#   3. Literature enrichment of high-GPAS groups
#   4. Threshold sensitivity: P80/P85/P90/P95
#   5. Three-panel supplementary figure
#
# Input:
#   ebi_knowledge_summary_0730.csv
#
# Optional literature validation input:
#   literature_validation.tsv
#
# Expected literature columns:
#   organism_std
#   antimicrobial_std
#   gene_symbol
#   known_resistance
#   reference
#
# known_resistance:
#   1 = supported
#   0 = not supported / no supporting evidence identified
#
# ============================================================

from __future__ import annotations

import os
import math
from pathlib import Path

import numpy as np
import pandas as pd

from scipy.stats import (
    spearmanr,
    fisher_exact,
    mannwhitneyu,
)

import matplotlib.pyplot as plt


# ============================================================
# 1. Configuration
# ============================================================

INPUT_FILE = Path("ebi_knowledge_summary_0730.csv")

# 如果你已有 literature validation 文件，在这里填写
# 例如：
# LITERATURE_FILE = Path("top100_literature_validation.tsv")
#
# 如果暂时没有，设为 None
LITERATURE_FILE = Path("literature_validation.tsv")

OUTPUT_DIR = Path("gpas_percentile_validation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# GPAS parameters
DEFAULT_K = 10.0
DEFAULT_EPSILON = 0.5

# Percentile groups
PERCENTILE_BINS = [
    (0, 10, "Bottom 10%"),
    (10, 25, "P10–P25"),
    (25, 75, "P25–P75"),
    (75, 90, "P75–P90"),
    (90, 100, "Top 10%"),
]

# Absolute effect-size thresholds
LOGOR_THRESHOLDS = [0.5, 1.0, 2.0]

# Threshold sensitivity
HIGH_GPAs_THRESHOLDS = [80, 85, 90, 95]


# ============================================================
# 2. Utility functions
# ============================================================

def find_column(df, candidates, required=True):
    """
    Find the first matching column from candidate names.
    """
    for c in candidates:
        if c in df.columns:
            return c

    if required:
        raise ValueError(
            f"Could not find any of these columns: {candidates}\n"
            f"Available columns:\n{list(df.columns)}"
        )

    return None


def safe_log10(x):
    x = np.asarray(x, dtype=float)
    return -np.log10(np.maximum(x, np.finfo(float).tiny))


# ============================================================
# 3. Load knowledge summary
# ============================================================

print("=" * 80)
print("Loading GPAS knowledge summary")
print("=" * 80)

df = pd.read_csv(INPUT_FILE)

print(f"Input shape: {df.shape}")
print("Columns:")
print(df.columns.tolist())


# ============================================================
# 4. Identify required columns
# ============================================================

# Expected columns based on your current GPAS pipeline
COL_GENE_TOTAL = find_column(
    df,
    ["gene_total", "gene_n", "gene_positive_total"]
)

COL_GENE_S = find_column(
    df,
    ["gene_S", "gene_s", "gene_susceptible", "gene_positive_S"]
)

COL_GENE_NON_S = find_column(
    df,
    ["gene_non_s", "gene_nonS", "gene_non_susceptible", "gene_positive_nonS"]
)

COL_TOTAL_S = find_column(
    df,
    ["total_S", "total_s", "total_susceptible"]
)

COL_TOTAL_NON_S = find_column(
    df,
    ["total_non_s", "total_nonS", "total_non_susceptible"]
)

COL_ORGANISM = find_column(
    df,
    ["organism_std", "organism"]
)

COL_ANTIMICROBIAL = find_column(
    df,
    ["antimicrobial_std", "antimicrobial", "drug"]
)

COL_GENE = find_column(
    df,
    ["gene_symbol", "gene", "gene_name"]
)


# ============================================================
# 5. Prepare 2 × 2 contingency table
# ============================================================

print("\nPreparing 2 × 2 contingency tables...")

df["gene_total_calc"] = (
    df[COL_GENE_S].astype(float)
    + df[COL_GENE_NON_S].astype(float)
)

df["total_total_calc"] = (
    df[COL_TOTAL_S].astype(float)
    + df[COL_TOTAL_NON_S].astype(float)
)

# 2x2:
#
#                 Non-S       S
# Gene+             a         b
# Gene-             c         d
#
# a = gene-positive non-susceptible
# b = gene-positive susceptible
# c = gene-negative non-susceptible
# d = gene-negative susceptible

df["a"] = df[COL_GENE_NON_S].astype(float)

df["b"] = df[COL_GENE_S].astype(float)

df["c"] = (
    df[COL_TOTAL_NON_S].astype(float)
    - df["gene_non_s"].astype(float)
    if "gene_non_s" in df.columns
    else
    df[COL_TOTAL_NON_S].astype(float)
    - df[COL_GENE_NON_S].astype(float)
)

df["d"] = (
    df[COL_TOTAL_S].astype(float)
    - df[COL_GENE_S].astype(float)
)


# ============================================================
# 6. Haldane–Anscombe corrected logOR
# ============================================================

epsilon = DEFAULT_EPSILON

df["a_HA"] = df["a"] + epsilon
df["b_HA"] = df["b"] + epsilon
df["c_HA"] = df["c"] + epsilon
df["d_HA"] = df["d"] + epsilon

df["OR_corrected"] = (
    df["a_HA"] * df["d_HA"]
    / (df["b_HA"] * df["c_HA"])
)

df["logOR_HA"] = np.log(df["OR_corrected"])


# ============================================================
# 7. Calculate GPAS
# ============================================================

print("Calculating GPAS...")

# Evidence weight
df["w_evidence"] = np.sqrt(
    df[COL_GENE_TOTAL].astype(float)
    /
    (
        df[COL_GENE_TOTAL].astype(float)
        + DEFAULT_K
    )
)

# phenotype balance
min_group = np.minimum(
    df[COL_GENE_S].astype(float),
    df[COL_GENE_NON_S].astype(float)
)

df["min_group"] = min_group

df["w_balance"] = np.sqrt(
    min_group / (min_group + DEFAULT_K)
)

# Overall confidence weight
df["confidence_weight"] = (
    df["w_evidence"]
    *
    (
        0.5
        +
        0.5 * df["w_balance"]
    )
)

# GPAS
df["GPAS"] = (
    df["logOR_HA"]
    *
    df["confidence_weight"]
)


# ============================================================
# 8. Basic filtering
# ============================================================

# Same conceptual validity criteria as your existing GPAS workflow:
# gene_total >= 5
# gene_S >= 2
# gene_non_s >= 2

# valid_mask = (
#     (df[COL_GENE_TOTAL] >= 5)
#     &
#     (df[COL_GENE_S] >= 2)
#     &
#     (df[COL_GENE_NON_S] >= 2)
#     &
#     np.isfinite(df["GPAS"])
#     &
#     np.isfinite(df["logOR_HA"])
# )

#analysis = df.loc[valid_mask].copy()
analysis = df
print("\nValid GPAS associations:")
print(len(analysis))


# ============================================================
# 9. Calculate GPAS percentiles
# ============================================================

analysis["GPAS_percentile"] = (
    analysis["GPAS"].rank(
        method="average",
        pct=True
    ) * 100
)


def assign_percentile_group(x):
    if x <= 10:
        return "Bottom 10%"
    elif x <= 25:
        return "P10–P25"
    elif x <= 75:
        return "P25–P75"
    elif x <= 90:
        return "P75–P90"
    else:
        return "Top 10%"


analysis["GPAS_category"] = (
    analysis["GPAS_percentile"]
    .apply(assign_percentile_group)
)


# ordered category
category_order = [
    "Bottom 10%",
    "P10–P25",
    "P25–P75",
    "P75–P90",
    "Top 10%",
]

analysis["GPAS_category"] = pd.Categorical(
    analysis["GPAS_category"],
    categories=category_order,
    ordered=True
)


# ============================================================
# 10. Analysis 1:
#     GPAS percentile vs absolute effect size
# ============================================================

print("\n" + "=" * 80)
print("Analysis 1: GPAS percentile vs absolute effect size")
print("=" * 80)

analysis["abs_logOR"] = analysis["logOR_HA"].abs()
analysis["abs_OR"] = np.exp(analysis["abs_logOR"])

rows = []

for category in category_order:

    sub = analysis.loc[
        analysis["GPAS_category"] == category
    ].copy()

    row = {
        "GPAS_category": category,
        "n": len(sub),
        "median_GPAS": sub["GPAS"].median(),
        "median_abs_logOR": sub["abs_logOR"].median(),
        "Q1_abs_logOR": sub["abs_logOR"].quantile(0.25),
        "Q3_abs_logOR": sub["abs_logOR"].quantile(0.75),
        "median_OR_magnitude": sub["abs_OR"].median(),
    }

    for threshold in LOGOR_THRESHOLDS:
        row[
            f"proportion_abs_logOR_ge_{threshold}"
        ] = (
            (sub["abs_logOR"] >= threshold).mean()
        )

    rows.append(row)


effect_summary = pd.DataFrame(rows)

effect_summary.to_csv(
    OUTPUT_DIR / "gpas_percentile_effect_size_summary.tsv",
    sep="\t",
    index=False
)

print(effect_summary.to_string(index=False))


# ============================================================
# 11. Overall correlation:
#     GPAS vs logOR
# ============================================================

rho_signed, p_signed = spearmanr(
    analysis["GPAS"],
    analysis["logOR_HA"]
)

rho_abs, p_abs = spearmanr(
    analysis["GPAS"].abs(),
    analysis["logOR_HA"].abs()
)

print("\nOverall Spearman correlations:")
print(
    f"GPAS vs logOR: "
    f"rho={rho_signed:.6f}, "
    f"p={p_signed:.3e}"
)

print(
    f"|GPAS| vs |logOR|: "
    f"rho={rho_abs:.6f}, "
    f"p={p_abs:.3e}"
)


with open(
    OUTPUT_DIR / "gpas_effect_size_correlation.txt",
    "w"
) as f:

    f.write(
        "GPAS vs logOR\n"
        f"Spearman rho = {rho_signed:.8f}\n"
        f"P = {p_signed:.8e}\n\n"
    )

    f.write(
        "|GPAS| vs |logOR|\n"
        f"Spearman rho = {rho_abs:.8f}\n"
        f"P = {p_abs:.8e}\n"
    )


# ============================================================
# 12. Statistical comparison:
#     Top 10% vs remaining 90%
# ============================================================

top10 = analysis.loc[
    analysis["GPAS_percentile"] > 90,
    "abs_logOR"
]

remaining90 = analysis.loc[
    analysis["GPAS_percentile"] <= 90,
    "abs_logOR"
]

u_stat, mw_p = mannwhitneyu(
    top10,
    remaining90,
    alternative="two-sided"
)

print("\nTop 10% vs remaining 90%:")
print(
    f"Median |logOR|: "
    f"{top10.median():.4f} vs "
    f"{remaining90.median():.4f}"
)

print(
    f"Mann–Whitney U P = {mw_p:.3e}"
)


# ============================================================
# 13. Effect-size threshold table
# ============================================================

effect_threshold_rows = []

for category in category_order:

    sub = analysis.loc[
        analysis["GPAS_category"] == category
    ]

    for threshold in LOGOR_THRESHOLDS:

        effect_threshold_rows.append({
            "GPAS_category": category,
            "logOR_threshold": threshold,
            "n": len(sub),
            "n_meeting_threshold": (
                sub["abs_logOR"] >= threshold
            ).sum(),
            "proportion": (
                sub["abs_logOR"] >= threshold
            ).mean()
        })


effect_threshold_summary = pd.DataFrame(
    effect_threshold_rows
)

effect_threshold_summary.to_csv(
    OUTPUT_DIR / "gpas_percentile_effect_thresholds.tsv",
    sep="\t",
    index=False
)


# ============================================================
# 14. Load literature validation data
# ============================================================

literature_available = False

if LITERATURE_FILE.exists():

    print("\n" + "=" * 80)
    print("Loading literature validation data")
    print("=" * 80)

    lit = pd.read_csv(
        LITERATURE_FILE,
        sep="\t"
    )

    print(f"Literature table shape: {lit.shape}")
    print(lit.head())

    # Identify columns
    lit_org = find_column(
        lit,
        ["organism_std", "organism"]
    )

    lit_drug = find_column(
        lit,
        ["antimicrobial_std", "antimicrobial", "drug"]
    )

    lit_gene = find_column(
        lit,
        ["gene_symbol", "gene", "gene_name"]
    )

    lit_supported = find_column(
        lit,
        [
            "known_resistance",
            "literature_supported",
            "supported",
            "evidence_supported"
        ]
    )

    # standardize keys
    analysis["_org_key"] = (
        analysis[COL_ORGANISM]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    analysis["_drug_key"] = (
        analysis[COL_ANTIMICROBIAL]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    analysis["_gene_key"] = (
        analysis[COL_GENE]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    lit["_org_key"] = (
        lit[lit_org]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    lit["_drug_key"] = (
        lit[lit_drug]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    lit["_gene_key"] = (
        lit[lit_gene]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    lit[lit_supported] = pd.to_numeric(
        lit[lit_supported],
        errors="coerce"
    )

    # Keep one record per association
    lit_key = [
        "_org_key",
        "_drug_key",
        "_gene_key"
    ]

    lit_small = (
        lit[lit_key + [lit_supported]]
        .dropna(subset=[lit_supported])
        .groupby(lit_key, as_index=False)
        [lit_supported]
        .max()
    )

    lit_small = lit_small.rename(
        columns={
            lit_supported: "literature_supported"
        }
    )

    analysis = analysis.merge(
        lit_small,
        on=lit_key,
        how="left"
    )

    # Missing = not evaluated, NOT automatically unsupported
    literature_available = (
        analysis["literature_supported"]
        .notna()
        .any()
    )

    print(
        f"Associations with literature assessment: "
        f"{analysis['literature_supported'].notna().sum()}"
    )

else:

    print("\nNo literature validation file found.")
    print(
        f"Expected file: {LITERATURE_FILE}"
    )


# ============================================================
# 15. Literature support across GPAS categories
# ============================================================

if literature_available:

    print("\n" + "=" * 80)
    print("Analysis 2: Literature support across GPAS categories")
    print("=" * 80)

    lit_analysis = analysis.loc[
        analysis["literature_supported"].notna()
    ].copy()

    lit_rows = []

    for category in category_order:

        sub = lit_analysis.loc[
            lit_analysis["GPAS_category"] == category
        ].copy()

        n_total = len(sub)

        n_supported = (
            sub["literature_supported"] == 1
        ).sum()

        support_rate = (
            n_supported / n_total
            if n_total > 0
            else np.nan
        )

        lit_rows.append({
            "GPAS_category": category,
            "n_assessed": n_total,
            "n_supported": n_supported,
            "support_rate": support_rate
        })

    literature_summary = pd.DataFrame(
        lit_rows
    )

    literature_summary.to_csv(
        OUTPUT_DIR /
        "gpas_percentile_literature_support.tsv",
        sep="\t",
        index=False
    )

    print(
        literature_summary.to_string(
            index=False
        )
    )


# ============================================================
# 16. Literature enrichment:
#     Top 10% vs remaining
# ============================================================

if literature_available:

    lit_analysis = analysis.loc[
        analysis["literature_supported"].notna()
    ].copy()

    lit_analysis["high_gpas"] = (
        lit_analysis["GPAS_percentile"] > 90
    )

    #                    supported   unsupported
    #
    # high GPAS
    # remaining

    contingency = pd.crosstab(
        lit_analysis["high_gpas"],
        lit_analysis["literature_supported"]
    )

    # Ensure 2x2 structure
    for row in [False, True]:
        if row not in contingency.index:
            contingency.loc[row] = 0

    for col in [0, 1]:
        if col not in contingency.columns:
            contingency[col] = 0

    contingency = contingency.loc[
        [True, False],
        [1, 0]
    ]

    table = contingency.values

    odds_ratio, fisher_p = fisher_exact(
        table,
        alternative="two-sided"
    )

    # support rates
    high_supported = table[0, 0]
    high_total = table[0].sum()

    background_supported = table[1, 0]
    background_total = table[1].sum()

    high_rate = (
        high_supported / high_total
        if high_total > 0
        else np.nan
    )

    background_rate = (
        background_supported / background_total
        if background_total > 0
        else np.nan
    )

    enrichment = (
        high_rate / background_rate
        if background_rate > 0
        else np.nan
    )

    enrichment_result = pd.DataFrame([{
        "comparison": "Top 10% vs remaining 90%",
        "high_n": high_total,
        "high_supported": high_supported,
        "high_support_rate": high_rate,
        "background_n": background_total,
        "background_supported": background_supported,
        "background_support_rate": background_rate,
        "odds_ratio": odds_ratio,
        "fisher_p": fisher_p,
        "enrichment": enrichment
    }])

    enrichment_result.to_csv(
        OUTPUT_DIR /
        "gpas_top10_literature_enrichment.tsv",
        sep="\t",
        index=False
    )

    print("\nTop 10% literature enrichment:")
    print(
        enrichment_result.to_string(
            index=False
        )
    )


# ============================================================
# 17. Threshold sensitivity:
#     P80 / P85 / P90 / P95
# ============================================================

print("\n" + "=" * 80)
print("Analysis 3: Percentile threshold sensitivity")
print("=" * 80)

threshold_rows = []

for threshold in HIGH_GPAs_THRESHOLDS:

    high = analysis.loc[
        analysis["GPAS_percentile"] >= threshold
    ].copy()

    row = {
        "threshold": f"P{threshold}",
        "percentile_threshold": threshold,
        "n": len(high),
        "median_GPAS": high["GPAS"].median(),
        "median_abs_logOR": high["abs_logOR"].median(),
        "median_OR_magnitude": high["abs_OR"].median(),
    }

    for effect_threshold in LOGOR_THRESHOLDS:

        row[
            f"proportion_abs_logOR_ge_{effect_threshold}"
        ] = (
            high["abs_logOR"] >= effect_threshold
        ).mean()

    # literature support
    if literature_available:

        high_lit = high.loc[
            high["literature_supported"].notna()
        ]

        if len(high_lit) > 0:

            row["literature_n"] = len(high_lit)

            row["literature_supported_n"] = (
                high_lit["literature_supported"] == 1
            ).sum()

            row["literature_support_rate"] = (
                high_lit["literature_supported"] == 1
            ).mean()

            # Compare with all remaining evaluated associations
            remaining_lit = lit_analysis.loc[
                lit_analysis["GPAS_percentile"] < threshold
            ]

            a = (
                high_lit["literature_supported"] == 1
            ).sum()

            b = (
                high_lit["literature_supported"] == 0
            ).sum()

            c = (
                remaining_lit["literature_supported"] == 1
            ).sum()

            d = (
                remaining_lit["literature_supported"] == 0
            ).sum()

            table = np.array([
                [a, b],
                [c, d]
            ])

            or_value, p_value = fisher_exact(
                table,
                alternative="two-sided"
            )

            high_rate = (
                a / (a + b)
                if (a + b) > 0
                else np.nan
            )

            remaining_rate = (
                c / (c + d)
                if (c + d) > 0
                else np.nan
            )

            row["literature_odds_ratio"] = or_value
            row["literature_fisher_p"] = p_value

            row["literature_enrichment"] = (
                high_rate / remaining_rate
                if remaining_rate > 0
                else np.nan
            )

        else:

            row["literature_n"] = 0
            row["literature_supported_n"] = 0
            row["literature_support_rate"] = np.nan
            row["literature_odds_ratio"] = np.nan
            row["literature_fisher_p"] = np.nan
            row["literature_enrichment"] = np.nan

    threshold_rows.append(row)


threshold_summary = pd.DataFrame(
    threshold_rows
)

threshold_summary.to_csv(
    OUTPUT_DIR /
    "gpas_percentile_threshold_sensitivity.tsv",
    sep="\t",
    index=False
)

print(
    threshold_summary.to_string(
        index=False
    )
)


# ============================================================
# 18. Save full analysis table
# ============================================================

analysis.to_csv(
    OUTPUT_DIR /
    "gpas_percentile_validation_associations.tsv",
    sep="\t",
    index=False
)


# ============================================================
# 19. Figure A:
#     GPAS percentile vs absolute logOR
# ============================================================

fig = plt.figure(
    figsize=(8, 5)
)

data_for_box = []

for category in category_order:

    values = analysis.loc[
        analysis["GPAS_category"] == category,
        "abs_logOR"
    ].dropna().values

    data_for_box.append(values)


plt.boxplot(
    data_for_box,
    labels=category_order,
    showfliers=False
)

plt.xlabel(
    "GPAS percentile category"
)

plt.ylabel(
    "Absolute Haldane–Anscombe-corrected logOR"
)

plt.title(
    "Absolute effect size across GPAS percentile categories"
)

plt.xticks(
    rotation=25,
    ha="right"
)

plt.tight_layout()

fig.savefig(
    OUTPUT_DIR /
    "Figure_A_GPAS_percentile_vs_abs_logOR.pdf",
    dpi=300,
    bbox_inches="tight"
)

fig.savefig(
    OUTPUT_DIR /
    "Figure_A_GPAS_percentile_vs_abs_logOR.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# 20. Figure B:
#     Effect-size threshold proportions
# ============================================================

fig = plt.figure(
    figsize=(8, 5)
)

plot_df = effect_threshold_summary.pivot(
    index="GPAS_category",
    columns="logOR_threshold",
    values="proportion"
).reindex(category_order)

x = np.arange(
    len(plot_df.index)
)

width = 0.24

for i, threshold in enumerate(
    LOGOR_THRESHOLDS
):

    plt.bar(
        x + (i - 1) * width,
        plot_df[threshold].values,
        width=width,
        label=f"|logOR| ≥ {threshold}"
    )

plt.xticks(
    x,
    plot_df.index,
    rotation=25,
    ha="right"
)

plt.ylabel(
    "Proportion of associations"
)

plt.xlabel(
    "GPAS percentile category"
)

plt.ylim(
    0,
    1
)

plt.legend(
    frameon=False
)

plt.title(
    "Absolute effect-size thresholds across GPAS categories"
)

plt.tight_layout()

fig.savefig(
    OUTPUT_DIR /
    "Figure_B_effect_size_thresholds.pdf",
    dpi=300,
    bbox_inches="tight"
)

fig.savefig(
    OUTPUT_DIR /
    "Figure_B_effect_size_thresholds.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# 21. Figure C:
#     Literature support rate
# ============================================================

if literature_available:

    lit_plot = literature_summary.copy()

    fig = plt.figure(
        figsize=(8, 5)
    )

    x = np.arange(
        len(lit_plot)
    )

    rates = (
        lit_plot["support_rate"]
        .astype(float)
        .values
    )

    plt.bar(
        x,
        rates
    )

    plt.xticks(
        x,
        lit_plot["GPAS_category"],
        rotation=25,
        ha="right"
    )

    plt.ylabel(
        "Literature-supported proportion"
    )

    plt.xlabel(
        "GPAS percentile category"
    )

    plt.ylim(
        0,
        1
    )

    plt.title(
        "Literature support across GPAS percentile categories"
    )

    plt.tight_layout()

    fig.savefig(
        OUTPUT_DIR /
        "Figure_C_literature_support.pdf",
        dpi=300,
        bbox_inches="tight"
    )

    fig.savefig(
        OUTPUT_DIR /
        "Figure_C_literature_support.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)


# ============================================================
# 22. Combined three-panel figure
# ============================================================

if literature_available:

    fig = plt.figure(
        figsize=(15, 5)
    )

    # --------------------------------------------------------
    # Panel A
    # --------------------------------------------------------

    ax1 = fig.add_subplot(1, 3, 1)

    data_for_box = []

    for category in category_order:

        values = analysis.loc[
            analysis["GPAS_category"] == category,
            "abs_logOR"
        ].dropna().values

        data_for_box.append(values)

    ax1.boxplot(
        data_for_box,
        showfliers=False
    )

    ax1.set_xticklabels(
        category_order,
        rotation=30,
        ha="right"
    )

    ax1.set_xlabel(
        "GPAS percentile"
    )

    ax1.set_ylabel(
        "|logOR|"
    )

    ax1.set_title(
        "A. Absolute effect size"
    )

    # --------------------------------------------------------
    # Panel B
    # --------------------------------------------------------

    ax2 = fig.add_subplot(1, 3, 2)

    plot_df = effect_threshold_summary.pivot(
        index="GPAS_category",
        columns="logOR_threshold",
        values="proportion"
    ).reindex(category_order)

    x = np.arange(
        len(plot_df.index)
    )

    width = 0.24

    for i, threshold in enumerate(
        LOGOR_THRESHOLDS
    ):

        ax2.bar(
            x + (i - 1) * width,
            plot_df[threshold].values,
            width=width,
            label=f"|logOR| ≥ {threshold}"
        )

    ax2.set_xticks(x)

    ax2.set_xticklabels(
        plot_df.index,
        rotation=30,
        ha="right"
    )

    ax2.set_ylim(
        0,
        1
    )

    ax2.set_xlabel(
        "GPAS percentile"
    )

    ax2.set_ylabel(
        "Proportion"
    )

    ax2.set_title(
        "B. Effect-size thresholds"
    )

    ax2.legend(
        frameon=False,
        fontsize=8
    )

    # --------------------------------------------------------
    # Panel C
    # --------------------------------------------------------

    ax3 = fig.add_subplot(1, 3, 3)

    x = np.arange(
        len(lit_plot)
    )

    rates = (
        lit_plot["support_rate"]
        .astype(float)
        .values
    )

    ax3.bar(
        x,
        rates
    )

    ax3.set_xticks(x)

    ax3.set_xticklabels(
        lit_plot["GPAS_category"],
        rotation=30,
        ha="right"
    )

    ax3.set_ylim(
        0,
        1
    )

    ax3.set_xlabel(
        "GPAS percentile"
    )

    ax3.set_ylabel(
        "Literature-supported proportion"
    )

    ax3.set_title(
        "C. Literature support"
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR /
        "Figure_GPAS_percentile_validation.pdf",
        dpi=300,
        bbox_inches="tight"
    )

    fig.savefig(
        OUTPUT_DIR /
        "Figure_GPAS_percentile_validation.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)


# ============================================================
# 23. Final summary
# ============================================================

print("\n" + "=" * 80)
print("GPAS percentile validation completed")
print("=" * 80)

print(
    f"Number of valid associations: {len(analysis)}"
)

print(
    f"Spearman |GPAS| vs |logOR|: "
    f"rho={rho_abs:.4f}, "
    f"P={p_abs:.3e}"
)

print(
    f"Top 10% median |logOR|: "
    f"{top10.median():.4f}"
)

print(
    f"Remaining 90% median |logOR|: "
    f"{remaining90.median():.4f}"
)

print(
    f"Top 10% vs remaining 90% "
    f"Mann–Whitney P={mw_p:.3e}"
)

if literature_available:

    top10_lit = literature_summary.loc[
        literature_summary["GPAS_category"] == "Top 10%"
    ]

    if len(top10_lit) > 0:

        print(
            "Top 10% literature support rate: "
            f"{top10_lit.iloc[0]['support_rate']:.3f}"
        )

print(
    f"\nAll results saved to:\n"
    f"{OUTPUT_DIR.resolve()}"
)

print("\nGenerated files:")

for file in sorted(
    OUTPUT_DIR.iterdir()
):

    print(
        "  ",
        file.name
    )
