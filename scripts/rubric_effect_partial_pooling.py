#!/usr/bin/env python3
"""Partially pooled estimate of the rubric (expected-behaviour) effect.

The judge matrix reports, for each of three judge models, the change in
agreement when the item's expected-behaviour field is withheld. Read as three
separate numbers, one of them (mistral-small:24b, policy compliance) is large,
+16.7 points. But it is the largest of three noisy estimates from 18 clustered
items, exactly the regime in which the largest observed effect overstates the
true one (a Type-M error; Gelman and Carlin).

The right correction is not to test whether it clears zero but to pool. This
fits Gelman's eight-schools normal-normal hierarchical model to the three
per-judge effects:

    d_j  ~ Normal(theta_j, se_j^2)            # observed effect, known se
    theta_j ~ Normal(mu, tau^2)               # true effects share a mean
    p(mu) flat,  p(tau) = HalfNormal(0, s)    # weakly informative on tau

se_j is the item-cluster bootstrap standard error of the paired effect, so the
few-cluster dependence structure is carried into the pooling. The posterior for
(mu, tau) is computed exactly by 1-D quadrature over tau (mu and the theta_j are
integrated / updated conjugately), so the result is deterministic. Shrunken
theta_j are summarised by seeded posterior draws.

Usage:  python3 scripts/rubric_effect_partial_pooling.py
"""

from __future__ import annotations

import csv
from collections import defaultdict

import numpy as np

BASE = "benchmark/results/local-pilot-20260630-185417/judge_validation"
CELLS = {
    "glm-4.7-flash": (
        f"{BASE}/judge-validation-glm-compact-20260701/judge_labels.csv",
        f"{BASE}/judge-glm-norubric-20260722/judge_labels.csv",
    ),
    "mistral:7b": (
        f"{BASE}/judge-mistral7b-compact-20260722/judge_labels.csv",
        f"{BASE}/judge-mistral7b-norubric-20260722/judge_labels.csv",
    ),
    "mistral-small:24b": (
        f"{BASE}/judge-mistral24b-compact-20260722/judge_labels.csv",
        f"{BASE}/judge-mistral24b-norubric-20260722/judge_labels.csv",
    ),
}
CRITERIA = ["task_success", "policy_compliance", "failure_attribution"]
N_BOOT = 10000
SEED = 20260722
TAU_PRIOR_SCALE = 0.15  # half-normal sd on tau, in proportion units (15 points)


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return {(r["item_id"], r["model"]): r for r in csv.DictReader(fh)}


def paired_indicators(vis, wit, fam):
    """Per shared object: (item_id, agree_visible, agree_withheld)."""
    out = []
    for key in sorted(set(vis) & set(wit)):
        rv, rw = vis[key], wit[key]
        av = int(rv[f"judge_{fam}"] == rv[f"human_{fam}"])
        aw = int(rw[f"judge_{fam}"] == rw[f"human_{fam}"])
        out.append((key[0], av, aw))
    return out


def effect(rows):
    return float(np.mean([av - aw for _, av, aw in rows]))


def cluster_boot_se(rows, n_boot=N_BOOT, seed=SEED):
    by_item = defaultdict(list)
    for it, av, aw in rows:
        by_item[it].append(av - aw)
    items = sorted(by_item)
    rng = np.random.default_rng(seed)
    idx = np.arange(len(items))
    vals = np.empty(n_boot)
    for b in range(n_boot):
        draw = rng.choice(idx, size=len(items), replace=True)
        diffs = [d for i in draw for d in by_item[items[i]]]
        vals[b] = np.mean(diffs)
    return float(np.std(vals, ddof=1))


def eight_schools(d, se, prior_scale=TAU_PRIOR_SCALE, seed=SEED):
    """Exact normal-normal pooling by quadrature over tau. Returns dict."""
    d = np.asarray(d, float)
    se = np.asarray(se, float)
    taus = np.linspace(1e-4, max(0.60, 4 * prior_scale), 4000)
    # p(tau | d): integrate out mu (flat) and theta (conjugate).
    logpost = np.empty_like(taus)
    for k, tau in enumerate(taus):
        V = se ** 2 + tau ** 2
        prec = 1.0 / V
        mu_hat = np.sum(d * prec) / np.sum(prec)
        # marginal after integrating mu with flat prior (BDA):
        ll = (
            -0.5 * np.log(np.sum(prec))
            - 0.5 * np.sum(np.log(V))
            - 0.5 * np.sum((d - mu_hat) ** 2 * prec)
        )
        lprior = -0.5 * (tau / prior_scale) ** 2  # half-normal
        logpost[k] = ll + lprior
    w = np.exp(logpost - logpost.max())
    w /= w.sum()

    rng = np.random.default_rng(seed)
    n = 40000
    tk = rng.choice(len(taus), size=n, p=w)
    tau_s = taus[tk]
    V = se[None, :] ** 2 + tau_s[:, None] ** 2
    prec = 1.0 / V
    mu_hat = np.sum(d[None, :] * prec, axis=1) / np.sum(prec, axis=1)
    mu_var = 1.0 / np.sum(prec, axis=1)
    mu_s = rng.normal(mu_hat, np.sqrt(mu_var))
    # theta_j | mu, tau conjugate update
    post_prec = 1.0 / se[None, :] ** 2 + 1.0 / tau_s[:, None] ** 2
    post_mean = (
        d[None, :] / se[None, :] ** 2 + mu_s[:, None] / tau_s[:, None] ** 2
    ) / post_prec
    theta_s = rng.normal(post_mean, np.sqrt(1.0 / post_prec))

    def ci(x):
        return float(np.mean(x)), float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))

    return {
        "mu": ci(mu_s),
        "tau_median": float(np.percentile(tau_s, 50)),
        "theta": [ci(theta_s[:, j]) for j in range(len(d))],
    }


def pp(x):
    return f"{x * 100:+.1f}"


def main():
    print(f"Item-cluster bootstrap se ({N_BOOT} reps, seed {SEED}); "
          f"half-normal({TAU_PRIOR_SCALE:.2f}) prior on tau.\n")
    for fam in CRITERIA:
        judges = list(CELLS)
        d, se, vis_a, wit_a = [], [], [], []
        for j in judges:
            vpath, wpath = CELLS[j]
            rows = paired_indicators(load(vpath), load(wpath), fam)
            d.append(effect(rows))
            se.append(cluster_boot_se(rows))
            vis_a.append(np.mean([av for _, av, _ in rows]))
            wit_a.append(np.mean([aw for _, _, aw in rows]))
        res = eight_schools(d, se)
        print(f"=== {fam} ===")
        print(f"{'judge':<19}{'visible':>9}{'withheld':>10}{'raw diff':>10}{'raw se':>9}"
              f"{'pooled diff (95%)':>30}")
        for i, j in enumerate(judges):
            tm, tlo, thi = res["theta"][i]
            print(f"{j:<19}{vis_a[i]*100:>8.1f}%{wit_a[i]*100:>9.1f}%{pp(d[i]):>10}"
                  f"{se[i]*100:>8.1f}"
                  f"{f'{pp(tm)} [{pp(tlo)}, {pp(thi)}]':>30}")
        mm, mlo, mhi = res["mu"]
        print(f"{'POOLED MEAN mu':<19}{'':>19}{'':>10}{'':>9}"
              f"{f'{pp(mm)} [{pp(mlo)}, {pp(mhi)}]':>30}")
        print(f"between-judge sd tau (posterior median): {res['tau_median']*100:.1f} points\n")


if __name__ == "__main__":
    main()
