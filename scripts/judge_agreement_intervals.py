#!/usr/bin/env python3
"""Item-clustered uncertainty for LLM-judge agreement on the local seed pilot.

The 54 pilot rows are 18 items crossed with 3 models, so rows are not
independent. Percent agreement and Cohen's kappa computed over 54 rows
understate uncertainty. This script resamples *items* (the clustering unit)
with replacement and recomputes each statistic, giving percentile intervals
that respect the dependence structure.

Usage:
    python3 scripts/judge_agreement_intervals.py
    python3 scripts/judge_agreement_intervals.py --matrix
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict

GLM_LABELS = (
    "benchmark/results/local-pilot-20260630-185417/judge_validation/"
    "judge-validation-glm-compact-20260701/judge_labels.csv"
)
FAMILIES = [
    "task_success",
    "policy_compliance",
    "safety_risk",
    "risk_type",
    "refusal_outcome",
    "failure_attribution",
]
N_BOOT = 10000
SEED = 20260722


def norm(value: str) -> str:
    return (value or "").strip().lower()


def load_rows(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def agreement(rows: list[dict], family: str) -> float | None:
    """Exact match between human and judge label, after normalization."""
    pairs = [
        (norm(r.get(f"human_{family}", "")), norm(r.get(f"judge_{family}", "")))
        for r in rows
        if r.get(f"human_{family}") is not None
    ]
    pairs = [(h, j) for h, j in pairs if h != "" and j != ""]
    if not pairs:
        return None
    return sum(h == j for h, j in pairs) / len(pairs)


def base_rate(rows: list[dict], family: str) -> float | None:
    """Majority-class share of the human labels: the score of a constant judge."""
    labels = [norm(r.get(f"human_{family}", "")) for r in rows]
    labels = [x for x in labels if x != ""]
    if not labels:
        return None
    counts: dict[str, int] = defaultdict(int)
    for x in labels:
        counts[x] += 1
    return max(counts.values()) / len(labels)


def cohen_kappa(rows: list[dict], family: str) -> float | None:
    pairs = [
        (norm(r.get(f"human_{family}", "")), norm(r.get(f"judge_{family}", "")))
        for r in rows
    ]
    pairs = [(h, j) for h, j in pairs if h != "" and j != ""]
    if not pairs:
        return None
    n = len(pairs)
    po = sum(h == j for h, j in pairs) / n
    hc: dict[str, int] = defaultdict(int)
    jc: dict[str, int] = defaultdict(int)
    for h, j in pairs:
        hc[h] += 1
        jc[j] += 1
    pe = sum((hc[k] / n) * (jc.get(k, 0) / n) for k in hc)
    if pe == 1:
        return None
    return (po - pe) / (1 - pe)


def cluster_bootstrap(rows: list[dict], family: str, stat, n_boot: int = N_BOOT):
    """Resample items (not rows) with replacement; return (lo, hi) percentiles."""
    by_item: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_item[r["item_id"]].append(r)
    items = sorted(by_item)
    rng = random.Random(SEED)
    vals = []
    for _ in range(n_boot):
        drawn: list[dict] = []
        for _ in range(len(items)):
            drawn.extend(by_item[items[rng.randrange(len(items))]])
        v = stat(drawn, family)
        if v is not None:
            vals.append(v)
    if not vals:
        return None, None
    vals.sort()
    lo = vals[int(0.025 * (len(vals) - 1))]
    hi = vals[int(0.975 * (len(vals) - 1))]
    return lo, hi


def report(rows: list[dict], title: str) -> None:
    items = len({r["item_id"] for r in rows})
    print(f"\n=== {title} ===")
    print(f"rows={len(rows)}  items(clusters)={items}  bootstrap={N_BOOT}, seed={SEED}")
    print(
        f"{'family':<22}{'agree':>8}{'base':>8}"
        f"{'agree 95% CI (item-clustered)':>34}{'kappa':>8}{'kappa 95% CI':>22}"
    )
    for fam in FAMILIES:
        a = agreement(rows, fam)
        if a is None:
            print(f"{fam:<22}{'n/a':>8}")
            continue
        b = base_rate(rows, fam)
        k = cohen_kappa(rows, fam)
        alo, ahi = cluster_bootstrap(rows, fam, agreement)
        klo, khi = cluster_bootstrap(rows, fam, cohen_kappa)
        kstr = "n/a" if k is None else f"{k:.2f}"
        kci = "n/a" if klo is None else f"[{klo:.2f}, {khi:.2f}]"
        print(
            f"{fam:<22}{a*100:>7.1f}%{b*100:>7.1f}%"
            f"{f'[{alo*100:.1f}%, {ahi*100:.1f}%]':>34}{kstr:>8}{kci:>22}"
        )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--matrix",
        action="store_true",
        help="also report the three-by-two judge model x rubric-condition matrix",
    )
    args = ap.parse_args()

    report(load_rows(GLM_LABELS), "glm-4.7-flash judge (rubric-aided, self-including)")

    if args.matrix:
        judge_matrix()


def judge_matrix() -> None:
    """Reproduce the paper's three-by-two judge matrix.

    Three judge models (one drawn from the evaluated set, two disjoint from it)
    crossed with two rubric conditions on the same 54 objects. `compact` shows
    the item's expected-behaviour field; `compact_no_rubric` withholds it and
    changes nothing else, so the contrast isolates rubric visibility.
    """
    base = "benchmark/results/local-pilot-20260630-185417/judge_validation"
    cells = [
        ("glm-4.7-flash", "yes", "visible", f"{base}/judge-validation-glm-compact-20260701/judge_labels.csv"),
        ("glm-4.7-flash", "yes", "hidden", f"{base}/judge-glm-norubric-20260722/judge_labels.csv"),
        ("mistral:7b", "no", "visible", f"{base}/judge-mistral7b-compact-20260722/judge_labels.csv"),
        ("mistral:7b", "no", "hidden", f"{base}/judge-mistral7b-norubric-20260722/judge_labels.csv"),
        ("mistral-small:24b", "no", "visible", f"{base}/judge-mistral24b-compact-20260722/judge_labels.csv"),
        ("mistral-small:24b", "no", "hidden", f"{base}/judge-mistral24b-norubric-20260722/judge_labels.csv"),
    ]
    shown = ["task_success", "policy_compliance", "failure_attribution"]
    print("\n=== Judge matrix: 3 models x 2 rubric conditions, same 54 objects ===")
    header = f"{'judge':<19}{'in set':<8}{'rubric':<9}"
    header += "".join(f"{f.split('_')[0][:9]:>11}" for f in shown)
    print(header + f"{'noncompl':>10}{'partial':>9}{'emits':>7}")
    for name, inset, cond, path in cells:
        rows = load_rows(path)
        cols = "".join(f"{agreement(rows, f) * 100:>10.1f}%" for f in shown)
        nc = [r for r in rows if r["human_policy_compliance"] == "noncompliant"]
        pa = [r for r in rows if r["human_task_success"] == "partial"]
        ncr = sum(1 for r in nc if r["judge_policy_compliance"] == "noncompliant")
        par = sum(1 for r in pa if r["judge_task_success"] == "partial")
        emits = sum(1 for r in rows if r["judge_task_success"] == "partial")
        print(
            f"{name:<19}{inset:<8}{cond:<9}{cols}"
            f"{f'{ncr}/{len(nc)}':>10}{f'{par}/{len(pa)}':>9}{emits:>7}"
        )
    ref = load_rows(cells[0][3])
    print(
        f"{'base rate (constant judge)':<36}"
        + "".join(f"{base_rate(ref, f) * 100:>10.1f}%" for f in shown)
    )


if __name__ == "__main__":
    main()
