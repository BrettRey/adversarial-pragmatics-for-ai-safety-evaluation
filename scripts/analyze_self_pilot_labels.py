#!/usr/bin/env python3
"""Exploratory, local-only label diagnostics for the Study A self-pilot.

This script deliberately lives outside the independent Study A ingestion and
analysis path. It reads the author's own self-pilot returns (schema v5/v6),
rejoins opaque row IDs privately, and writes exploratory diagnostics under
private/. Its outputs are design rationale, never paper evidence, and never
enter the independent panel results (DECISIONS.md 2026-07-15).
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESPONSES = ROOT / "private" / "study-a" / "self-pilot" / "responses"
V5_DIR = ROOT / "private" / "study-a" / "self-pilot" / "schema-v5-preserved"
ROW_MAP = ROOT / "private" / "study-a" / "self-pilot" / "private" / "row_map.tsv"
AUTHOR_LABELS = (
    ROOT
    / "data"
    / "provisional"
    / "local-pilot-20260630-185417-provisional-author-labels.csv"
)
OUT_DIR = ROOT / "private" / "study-a" / "self-pilot" / "label-diagnostics"

SELF_PILOT_STUDY_ID = "AP-STUDY-A-INDEPENDENT-READJUDICATION-SELF-PILOT"

# v6 self-pilot vocabulary: options that mark uncertainty, ambiguity, or an
# item defect rather than a substantive finding.
UNCERTAINTY_VALUES = {
    "unsure",
    "item_problem",
    "genuinely_ambiguous",
    "insufficient_context",
    "insufficient_visible_context",
    "unclear",
    "mixed_or_unclear",
    "policy_ambiguous",
    "policy_ambiguous_refusal",
}

# Cross-criterion patterns worth a second look. These are review flags, not
# logical errors: the fields are designed to vary independently.
def coherence_flags(role: str, row: dict[str, str]) -> list[str]:
    flags: list[str] = []
    g = row.get
    if role == "policy_safety":
        if g("visible_boundary_status") == "no_boundary_stated" and g("visible_boundary_type") not in {"none", None, ""}:
            flags.append("no_boundary_stated_but_type_selected")
        if g("visible_boundary_status") in {"boundary_stated_no_visible_violation", "visible_boundary_violation"} and g("visible_boundary_type") == "none":
            flags.append("boundary_stated_but_type_none")
        if g("visible_boundary_status") == "visible_boundary_violation" and g("policy_compliance") == "compliant":
            flags.append("boundary_violation_with_policy_compliant")
        if g("information_flow_action_licensing") == "violation" and g("policy_compliance") == "compliant":
            flags.append("info_flow_violation_with_policy_compliant")
        if g("refusal_outcome") == "under_refusal_probe" and g("policy_compliance") == "compliant":
            flags.append("under_refusal_with_policy_compliant")
    else:
        if g("task_success") == "success" and g("response_act_performed") == "no":
            flags.append("task_success_but_act_not_performed")
        if g("task_success") == "failure" and g("response_act_performed") == "yes":
            flags.append("task_failure_but_act_performed")
        if g("source_role_clarity") in {"insufficient_context", "insufficient_visible_context"} and g("clarification_required") == "no":
            flags.append("clarity_insufficient_but_no_clarification_needed")
        if g("scope_reference") == "misresolved_by_model" and g("task_success") == "success":
            flags.append("scope_misresolved_but_task_success")
    return flags


def load_returns() -> list[dict]:
    blocks = []
    for directory, v5 in ((RESPONSES, False), (V5_DIR, True)):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("study_id") != SELF_PILOT_STUDY_ID:
                raise SystemExit(f"{path.name}: unexpected study ID")
            payload["_file"] = path.name
            payload["_v5"] = v5
            blocks.append(payload)
    if not blocks:
        raise SystemExit("no self-pilot returns found")
    return blocks


def load_row_map() -> dict[str, dict[str, str]]:
    with ROW_MAP.open(encoding="utf-8", newline="") as handle:
        return {r["row_id"]: r for r in csv.DictReader(handle, delimiter="\t")}


def load_author_labels() -> dict[tuple[str, str], dict[str, str]]:
    with AUTHOR_LABELS.open(encoding="utf-8", newline="") as handle:
        return {(r["item_id"], r["model"]): r for r in csv.DictReader(handle)}


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()
    out = args.out_dir
    if ROOT not in out.resolve().parents and out.resolve() != ROOT:
        raise SystemExit("out-dir must stay inside the repository private tree")
    if "private" not in out.resolve().parts:
        raise SystemExit("out-dir must live under private/")
    out.mkdir(parents=True, exist_ok=True)

    blocks = load_returns()
    row_map = load_row_map()
    author = load_author_labels()

    distributions: Counter = Counter()
    uncertainty_rows: list[dict] = []
    coherence_rows: list[dict] = []
    versus_rows: list[dict] = []
    versus_summary: dict[str, Counter] = defaultdict(Counter)

    # Rejoin policy and linguistic answers per (item, model) for the
    # author-label comparison.
    for block in blocks:
        role = block["role"]
        schema_version = block["schema_version"]
        for row in block["responses"]:
            row_id = row["row_id"]
            meta = row_map.get(row_id)
            if meta is None:
                raise SystemExit(f"{row_id}: not in private row map")
            base = {
                "item_id": meta["item_id"],
                "model": meta["model"],
                "phenomenon": meta["phenomenon"],
                "variant": meta["variant"],
                "role": role,
                "schema_version": schema_version,
            }
            for field, value in row.items():
                if field in {"row_id", "updated_at", "rationale", "confidence"}:
                    continue
                if isinstance(value, list):
                    value = json.dumps(value)
                distributions[(role, schema_version, field, str(value))] += 1
                if str(value) in UNCERTAINTY_VALUES:
                    uncertainty_rows.append({**base, "field": field, "value": value})
            for flag in coherence_flags(role, row):
                coherence_rows.append({**base, "pattern": flag})
            reference = author.get((meta["item_id"], meta["model"]))
            if reference is None:
                continue
            compare_fields = (
                ["task_success"] if role == "linguistic_task" else ["policy_compliance", "refusal_outcome"]
            )
            for field in compare_fields:
                mine = row.get(field)
                theirs = reference.get(field)
                if mine is None or theirs in (None, ""):
                    continue
                # The pilot rubric used not_applicable where the v6 form says
                # not_a_refusal; harmonize before comparing.
                if field == "refusal_outcome" and theirs == "not_applicable":
                    theirs = "not_a_refusal"
                agree = mine == theirs
                versus_summary[field][
                    "agree" if agree else "disagree"
                ] += 1
                if not agree:
                    versus_rows.append(
                        {
                            **base,
                            "field": field,
                            "self_pilot_blind": mine,
                            "author_provisional": theirs,
                            # Row-level: one confidence rating covers every
                            # question on the form. It cannot be attributed
                            # to this field's answer.
                            "self_row_confidence": row.get("confidence", ""),
                        }
                    )

    write_csv(
        out / "field-value-distributions.csv",
        ["role", "schema_version", "field", "value", "count"],
        [
            {"role": r, "schema_version": s, "field": f, "value": v, "count": c}
            for (r, s, f, v), c in sorted(distributions.items())
        ],
    )
    uncertainty_fields = ["item_id", "model", "phenomenon", "variant", "role", "schema_version", "field", "value"]
    write_csv(out / "uncertainty-rows.csv", uncertainty_fields, uncertainty_rows)
    write_csv(
        out / "coherence-review.csv",
        ["item_id", "model", "phenomenon", "variant", "role", "schema_version", "pattern"],
        coherence_rows,
    )
    write_csv(
        out / "self-vs-author-disagreements.csv",
        uncertainty_fields[:6] + ["field", "self_pilot_blind", "author_provisional", "self_row_confidence"],
        versus_rows,
    )

    lines = [
        "# Self-Pilot Label Diagnostics (EXPLORATORY)",
        "",
        "PRIVATE. Exploratory design diagnostics only: never paper evidence,",
        "never part of the independent Study A panel results (DECISIONS.md",
        "2026-07-15). Blind self-ratings by the item author, compared against",
        "his own frozen provisional labels.",
        "",
        "Confidence is rated once per row and covers every question on the",
        "form; treat it as a row-level covariate only, never as confidence in",
        "any particular field's answer (Brett, 2026-07-15: it was generally",
        "not driven by the compliance judgment).",
        "",
        f"- Blocks read: {len(blocks)} ({sum(len(b['responses']) for b in blocks)} row-ratings)",
        f"- Uncertainty/ambiguity selections: {len(uncertainty_rows)}",
        f"- Coherence review flags: {len(coherence_rows)}",
    ]
    for field, counts in sorted(versus_summary.items()):
        total = counts["agree"] + counts["disagree"]
        lines.append(
            f"- Blind self vs author provisional, `{field}`: "
            f"{counts['agree']}/{total} agree, {counts['disagree']} differ"
        )
    lines.append("")
    lines.append("Files: field-value-distributions.csv, uncertainty-rows.csv,")
    lines.append("coherence-review.csv, self-vs-author-disagreements.csv")
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote exploratory label diagnostics to {out}")
    for line in lines[7:]:
        if line:
            print(line)


if __name__ == "__main__":
    main()
