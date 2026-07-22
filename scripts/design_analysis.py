#!/usr/bin/env python3
"""Design analysis by simulation for the three delegation-assurance programmes.

Before a sample size is frozen, a design analysis asks what that sample buys
under a plausible data-generating process: not just whether an effect can reach
a threshold, but the sign and magnitude errors incurred when a decision
conditions on that threshold \\citep{gelmanCarlin2014}. Nothing here uses target
data. Each programme's data-generating process encodes a declared effect and
declared nuisance and clustering structure; the estimators are the ones the
frozen version-1 specifications prescribe, together with the multilevel
alternative this revision recommends.

Three findings drive the revision:

1. Local discrimination. Conditioning a family verdict on a one-sided
   ``lower bound above zero`` gate exaggerates the reported authority effect
   (a Type M error). The exaggeration ratio is reported at the frozen 30 pairs.
   The ``subtract the largest of three nuisance sensitivities`` rule is also a
   biased estimand: the maximum of noisy nonnegative quantities is inflated, so
   the rule over-subtracts.

2. Predictive ablation. A ten-bin expected calibration error computed on 30
   held-out observations is a positively biased, high-variance statistic. A
   perfectly calibrated predictor fails the ``ECE at most 0.10`` gate a large
   fraction of the time from binning noise alone. A normal cluster interval over
   ten trace families undercovers.

3. Reviewer reconstruction. Taking ``the larger of the case-cluster and
   reviewer-cluster standard errors`` ignores one variance component of a
   crossed design and undercovers when both components are non-negligible; with
   six reviewers the reviewer-cluster term is itself unstable.

The point isn't the specific numbers, which depend on the declared design
parameters exposed below. It's that the frozen thresholds were never checked
against a design analysis, and that a multilevel estimand with reported
uncertainty replaces each threshold gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE.parent / "assurance" / "delegation" / "empirical" / "design-analysis"

PROFILES = {
    "smoke": {"reps": 2000},
    "standard": {"reps": 20000},
}

# Declared design assumptions. These are inputs to the analysis, not findings.
LOCAL = {
    "true_family_effect": 0.15,   # the frozen minimum selective margin
    "between_pair_sd": 0.18,      # heterogeneity of the effect across base pairs
    "pair_measure_sd": 0.16,      # per-pair measurement noise on the 0-1 endpoint
    "nuisance_mean": 0.05,        # true placebo/order/shortcut sensitivity
    "nuisance_sd": 0.06,          # noise in each estimated nuisance sensitivity
    "n_pairs": 30,                # frozen minimum observations per family
}
PRED = {
    "true_family_improvement": 0.05,  # frozen minimum mean Brier improvement
    "between_family_sd": 0.05,
    "n_families": 10,                 # frozen minimum trace families per family
    "ece_bins": 10,
    "ece_n": 30,                      # frozen minimum held-out observations
}
REVIEW = {
    "true_concordance_gain": 0.15,  # frozen minimum typed-minus-degraded gain
    "reviewer_sd": 0.10,
    "case_sd": 0.10,
    "residual_sd": 0.10,
    "n_reviewers": 6,               # frozen reviewers per arm
    "n_cases": 10,                  # frozen matched held-out cases
}


def local_discrimination(reps: int, rng: np.random.Generator) -> dict:
    """Type M exaggeration under the one-sided gate, and nuisance-rule bias."""
    p = LOCAL
    n = p["n_pairs"]
    z = stats.norm.ppf(0.975)

    est_naive = np.empty(reps)   # subtract the largest of three nuisances
    est_model = np.empty(reps)   # subtract the modelled common nuisance mean
    lcb_naive = np.empty(reps)
    lcb_model = np.empty(reps)
    for r in range(reps):
        pair_effects = rng.normal(p["true_family_effect"], p["between_pair_sd"], n)
        # three nonnegative nuisance sensitivities, each estimated with noise
        nuis = np.abs(rng.normal(p["nuisance_mean"], p["nuisance_sd"], (n, 3)))
        raw = pair_effects + nuis.mean(axis=1) + rng.normal(0, p["pair_measure_sd"], n)
        signed_naive = raw - nuis.max(axis=1)
        signed_model = raw - p["nuisance_mean"]  # model the common mean instead
        est_naive[r] = signed_naive.mean()
        est_model[r] = signed_model.mean()
        lcb_naive[r] = est_naive[r] - z * signed_naive.std(ddof=1) / np.sqrt(n)
        lcb_model[r] = est_model[r] - z * signed_model.std(ddof=1) / np.sqrt(n)

    truth = p["true_family_effect"]
    pass_naive = lcb_naive > 0.0
    pass_model = lcb_model > 0.0
    # Type M on the near-unbiased modelled estimator isolates the gate's effect
    exagg_model = est_model[pass_model].mean() / truth if pass_model.any() else float("nan")
    type_s = float((est_model[pass_model] < 0).mean()) if pass_model.any() else float("nan")
    return {
        "programme": "local_discrimination",
        "true_effect": truth,
        "n_per_family": n,
        "gate_pass_rate_modelled": float(pass_model.mean()),
        "type_m_exaggeration_given_gate_modelled": float(exagg_model),
        "type_s_rate_given_gate_modelled": type_s,
        "naive_bias_subtract_max_nuisance": float(est_naive.mean() - truth),
        "naive_bias_as_fraction_of_effect": float((est_naive.mean() - truth) / truth),
        "modelled_bias_subtract_mean_nuisance": float(est_model.mean() - truth),
    }


def predictive_ablation(reps: int, rng: np.random.Generator) -> dict:
    """Cluster-interval coverage, and ten-bin ECE false-fail under calibration."""
    p = PRED
    z = stats.norm.ppf(0.975)
    tcrit = stats.t.ppf(0.975, df=p["n_families"] - 1)

    cov_normal = np.empty(reps)
    cov_t = np.empty(reps)
    ece_vals = np.empty(reps)
    for r in range(reps):
        fam = rng.normal(p["true_family_improvement"], p["between_family_sd"], p["n_families"])
        m = fam.mean()
        se = fam.std(ddof=1) / np.sqrt(p["n_families"])
        cov_normal[r] = (m - z * se) <= p["true_family_improvement"] <= (m + z * se)
        cov_t[r] = (m - tcrit * se) <= p["true_family_improvement"] <= (m + tcrit * se)
        # perfectly calibrated predictor: labels ~ Bernoulli(prob)
        prob = rng.uniform(0, 1, p["ece_n"])
        y = rng.binomial(1, prob)
        edges = np.linspace(0, 1, p["ece_bins"] + 1)
        idx = np.clip(np.digitize(prob, edges) - 1, 0, p["ece_bins"] - 1)
        ece = 0.0
        for b in range(p["ece_bins"]):
            sel = idx == b
            if sel.any():
                ece += (sel.mean()) * abs(y[sel].mean() - prob[sel].mean())
        ece_vals[r] = ece

    return {
        "programme": "predictive_ablation",
        "n_trace_families": p["n_families"],
        "normal_lcb_coverage": float(cov_normal.mean()),
        "t_interval_coverage": float(cov_t.mean()),
        "ece_n": p["ece_n"],
        "mean_ece_under_perfect_calibration": float(ece_vals.mean()),
        "ece_gate_false_fail_rate_at_0.10": float((ece_vals > 0.10).mean()),
    }


def reviewer_reconstruction(reps: int, rng: np.random.Generator) -> dict:
    """Coverage of max-of-two-SEs vs a crossed variance estimate."""
    p = REVIEW
    z = stats.norm.ppf(0.975)
    nr, nc = p["n_reviewers"], p["n_cases"]
    truth = p["true_concordance_gain"]

    cov_max = np.empty(reps)
    cov_crossed = np.empty(reps)
    for r in range(reps):
        rev = rng.normal(0, p["reviewer_sd"], nr)
        case = rng.normal(0, p["case_sd"], nc)
        resid = rng.normal(0, p["residual_sd"], (nr, nc))
        y = truth + rev[:, None] + case[None, :] + resid
        m = y.mean()
        # frozen rule: larger of the two one-way cluster SEs of the grand mean
        rev_means = y.mean(axis=1)
        case_means = y.mean(axis=0)
        se_rev = rev_means.std(ddof=1) / np.sqrt(nr)
        se_case = case_means.std(ddof=1) / np.sqrt(nc)
        se_max = max(se_rev, se_case)
        # crossed grand-mean SE with the true variance components (an upper bound
        # on what any fitted crossed model achieves at these n): the six-reviewer
        # constraint, not estimator choice, sets the ceiling
        se_crossed = np.sqrt(
            p["reviewer_sd"] ** 2 / nr
            + p["case_sd"] ** 2 / nc
            + p["residual_sd"] ** 2 / (nr * nc)
        )
        cov_max[r] = (m - z * se_max) <= truth <= (m + z * se_max)
        cov_crossed[r] = (m - z * se_crossed) <= truth <= (m + z * se_crossed)

    return {
        "programme": "reviewer_reconstruction",
        "n_reviewers": nr,
        "n_cases": nc,
        "max_of_two_ses_coverage": float(cov_max.mean()),
        "crossed_known_components_coverage": float(cov_crossed.mean()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES, default="standard")
    parser.add_argument("--seed", type=int, default=20260722)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    reps = PROFILES[args.profile]["reps"]
    rng = np.random.default_rng(args.seed)
    results = [
        local_discrimination(reps, rng),
        predictive_ablation(reps, rng),
        reviewer_reconstruction(reps, rng),
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.json_normalize(results)
    frame.to_csv(args.output_dir / "design_analysis_summary.csv", index=False)
    metadata = {
        "profile": args.profile,
        "reps": reps,
        "seed": args.seed,
        "design_assumptions": {"local": LOCAL, "predictive": PRED, "reviewer": REVIEW},
        "results": results,
    }
    (args.output_dir / "design_analysis.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    for row in results:
        print(f"\n[{row['programme']}]")
        for k, v in row.items():
            if k == "programme":
                continue
            print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
    print(f"\nWrote design analysis ({args.profile}, {reps} reps) to {args.output_dir}")


if __name__ == "__main__":
    main()
