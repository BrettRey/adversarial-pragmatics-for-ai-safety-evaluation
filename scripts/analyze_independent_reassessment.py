#!/usr/bin/env python3
"""Analyze role-separated Study A ratings without collapsing criteria."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "benchmark" / "study-a" / "schema.json"
MIN_REFERENCE_RATERS = 2
DEPRECATED_SOURCE_ROLE = "task_giver_directive"
CURRENT_TASK_GIVER_ROLE = "task_giver_contribution"


def read_csv(path: Path, *, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def counts_text(values: Iterable[str]) -> str:
    counts = Counter(value for value in values if value)
    return "; ".join(f"{value}:{counts[value]}" for value in sorted(counts))


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def parse_source_roles(value: str, options: list[str], *, context: str) -> tuple[list[str], str]:
    """Validate and canonicalize a source-role set stored as compact JSON."""
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid source_roles JSON for {context}: {value!r}") from exc
    if not isinstance(parsed, list) or not parsed:
        raise SystemExit(f"source_roles must be a nonempty JSON array for {context}")
    if any(not isinstance(label, str) for label in parsed):
        raise SystemExit(f"source_roles must contain only strings for {context}")
    if len(parsed) != len(set(parsed)):
        raise SystemExit(f"source_roles contains duplicate labels for {context}")
    if DEPRECATED_SOURCE_ROLE in parsed:
        raise SystemExit(
            f"source_roles contains deprecated v5 label {DEPRECATED_SOURCE_ROLE!r} "
            f"for {context}; use {CURRENT_TASK_GIVER_ROLE!r}"
        )
    invalid = sorted(set(parsed) - set(options))
    if invalid:
        raise SystemExit(
            f"source_roles contains undeclared labels for {context}: {', '.join(invalid)}"
        )
    canonical = [option for option in options if option in parsed]
    return canonical, compact_json(canonical)


def source_role_set_counts(signatures: Iterable[str]) -> str:
    counts = Counter(signatures)
    payload = [
        {"source_roles": json.loads(signature), "ratings": count}
        for signature, count in sorted(counts.items())
    ]
    return compact_json(payload)


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def consensus(values: list[str], minimum_raters: int = MIN_REFERENCE_RATERS) -> tuple[str, str, float]:
    """Return label, stability, and modal share without inventing a tie-break."""
    if not values:
        return "", "missing", 0.0
    counts = Counter(values)
    top = max(counts.values())
    winners = sorted(label for label, count in counts.items() if count == top)
    share = top / len(values)
    if len(values) < minimum_raters:
        return "no_consensus", "insufficient_raters", share
    if len(winners) != 1:
        return "no_consensus", "tie", share
    if top == len(values):
        return winners[0], "unanimous", share
    if top > len(values) / 2:
        return winners[0], "majority", share
    return "no_consensus", "no_majority", share


def source_key(row: dict[str, str]) -> tuple[str, str]:
    return row.get("item_id", ""), row.get("model", "")


def load_optional_rows(path: Path) -> list[dict[str, str]]:
    return read_csv(path) if path.exists() else []


def primary_criteria(schema: dict[str, Any]) -> dict[str, list[str]]:
    return {
        role: [
            field["name"]
            for field in role_schema["fields"]
            if field["name"] not in {"confidence", "rationale", "source_roles"}
            and field.get("type") != "multiselect"
        ]
        for role, role_schema in schema["roles"].items()
    }


def analysis_metadata(private_dir: Path) -> dict[str, Any]:
    path = private_dir / "study-private-metadata.json"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-dir", required=True, type=Path)
    parser.add_argument("--ratings", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    private_dir = args.private_dir.resolve()
    ratings_path = (args.ratings or private_dir / "processed" / "ratings-long.csv").resolve()
    if not ratings_path.exists():
        raise SystemExit(f"missing ingested Study A ratings: {ratings_path}")
    map_path = private_dir / "row_map.tsv"
    if not map_path.exists():
        raise SystemExit(f"missing private row map: {map_path}")
    schema = load_schema()
    criteria_by_role = primary_criteria(schema)
    source_role_fields = {
        role: field
        for role, role_schema in schema["roles"].items()
        for field in role_schema["fields"]
        if field["name"] == "source_roles"
    }
    map_rows = read_csv(map_path, delimiter="\t")
    map_by_row = {row["row_id"]: row for row in map_rows}
    ratings = read_csv(ratings_path)
    metadata = analysis_metadata(private_dir)
    synthetic = bool(metadata.get("synthetic", False))
    out_dir = (args.out_dir or private_dir / "analysis").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    sessions: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in ratings:
        sessions[
            (row["role"], row["rater_id"], row["block_id"], row["source_file"])
        ].append(row)
    burden_rows: list[dict[str, Any]] = []
    for (role, rater_id, block_id, source_file), rows in sorted(sessions.items()):
        timing = {
            (row.get("started_at", ""), row.get("completed_at", ""), row.get("elapsed_seconds", ""))
            for row in rows
        }
        if len(timing) != 1:
            raise SystemExit(f"inconsistent timing metadata within {source_file}")
        started_at, completed_at, elapsed_seconds = timing.pop()
        seconds = int(elapsed_seconds)
        burden_rows.append(
            {
                "role": role,
                "rater_id": rater_id,
                "block_id": block_id,
                "source_file": source_file,
                "started_at": started_at,
                "completed_at": completed_at,
                "elapsed_seconds": seconds,
                "rated_rows": len(rows),
                "seconds_per_rated_row": f"{seconds / len(rows):.1f}" if rows else "",
            }
        )
    write_csv(
        out_dir / "evaluator-burden.csv",
        list(burden_rows[0]) if burden_rows else ["role", "rater_id", "block_id"],
        burden_rows,
    )

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in ratings:
        for criterion in criteria_by_role.get(row.get("role", ""), []):
            if row.get(criterion, ""):
                grouped[(row["role"], row["row_id"], criterion)].append(row)

    reference_rows: list[dict[str, Any]] = []
    reference_lookup: dict[tuple[str, str, str], dict[str, Any]] = {}
    for (role, row_id, criterion), rows in sorted(grouped.items()):
        label, stability, modal_share = consensus([row[criterion] for row in rows])
        source = map_by_row[row_id]
        reference = {
            "role": role,
            "row_id": row_id,
            "item_id": source["item_id"],
            "model": source["model"],
            "pair_id": source.get("pair_id", ""),
            "phenomenon": source.get("phenomenon", ""),
            "variant": source.get("variant", ""),
            "criterion": criterion,
            "rater_n": len(rows),
            "rater_ids": ";".join(sorted({row["rater_id"] for row in rows})),
            "label_counts": counts_text(row[criterion] for row in rows),
            "independent_reference": label,
            "stability": stability,
            "modal_share": f"{modal_share:.3f}",
        }
        reference_rows.append(reference)
        reference_lookup[(role, row_id, criterion)] = reference
    reference_fields = list(reference_rows[0]) if reference_rows else [
        "role", "row_id", "item_id", "model", "criterion", "independent_reference", "stability"
    ]
    write_csv(out_dir / "independent-reference-labels.csv", reference_fields, reference_rows)

    agreement_rows: list[dict[str, Any]] = []
    for role, criteria in criteria_by_role.items():
        for criterion in criteria:
            rows = [
                row for row in reference_rows if row["role"] == role and row["criterion"] == criterion
            ]
            if not rows:
                continue
            modal_shares = [float(row["modal_share"]) for row in rows]
            agreement_rows.append(
                {
                    "role": role,
                    "criterion": criterion,
                    "rows": len(rows),
                    "unanimous": sum(row["stability"] == "unanimous" for row in rows),
                    "majority": sum(row["stability"] == "majority" for row in rows),
                    "insufficient_raters": sum(
                        row["stability"] == "insufficient_raters" for row in rows
                    ),
                    "ties_or_no_majority": sum(
                        row["stability"] in {"tie", "no_majority"} for row in rows
                    ),
                    "mean_modal_share": f"{sum(modal_shares) / len(modal_shares):.3f}",
                    "stable_reference_rows": sum(
                        row["stability"] in {"unanimous", "majority"} for row in rows
                    ),
                }
            )
    write_csv(
        out_dir / "agreement-by-criterion.csv",
        list(agreement_rows[0]) if agreement_rows else ["role", "criterion", "rows"],
        agreement_rows,
    )

    source_role_groups: dict[tuple[str, str], list[tuple[dict[str, str], set[str], str]]] = (
        defaultdict(list)
    )
    for row in ratings:
        role = row.get("role", "")
        field = source_role_fields.get(role)
        if field is None:
            continue
        options = list(field.get("options") or [])
        selected, signature = parse_source_roles(
            row.get("source_roles", ""),
            options,
            context=f"{role}/{row.get('rater_id', '')}/{row.get('row_id', '')}",
        )
        source_role_groups[(role, row["row_id"])].append((row, set(selected), signature))

    source_exact_rows: list[dict[str, Any]] = []
    source_exact_lookup: dict[tuple[str, str], dict[str, Any]] = {}
    source_binary_rows: list[dict[str, Any]] = []
    for (role, row_id), rated_sets in sorted(source_role_groups.items()):
        source = map_by_row[row_id]
        signatures = [signature for _, _, signature in rated_sets]
        exact_reference, exact_stability, exact_modal_share = consensus(signatures)
        exact_row = {
            "role": role,
            "row_id": row_id,
            "item_id": source["item_id"],
            "model": source["model"],
            "pair_id": source.get("pair_id", ""),
            "phenomenon": source.get("phenomenon", ""),
            "variant": source.get("variant", ""),
            "criterion": "source_roles_exact_set",
            "rater_n": len(rated_sets),
            "rater_ids": ";".join(sorted({row["rater_id"] for row, _, _ in rated_sets})),
            "set_counts": source_role_set_counts(signatures),
            "exact_set_reference": exact_reference,
            "stability": exact_stability,
            "modal_share": f"{exact_modal_share:.3f}",
        }
        source_exact_rows.append(exact_row)
        source_exact_lookup[(role, row_id)] = exact_row

        options = list(source_role_fields[role].get("options") or [])
        for source_role in options:
            binary_values = [
                "selected" if source_role in selected else "not_selected"
                for _, selected, _ in rated_sets
            ]
            binary_reference, binary_stability, binary_modal_share = consensus(binary_values)
            selected_n = sum(value == "selected" for value in binary_values)
            source_binary_rows.append(
                {
                    "role": role,
                    "row_id": row_id,
                    "item_id": source["item_id"],
                    "model": source["model"],
                    "pair_id": source.get("pair_id", ""),
                    "phenomenon": source.get("phenomenon", ""),
                    "variant": source.get("variant", ""),
                    "source_role": source_role,
                    "rater_n": len(rated_sets),
                    "rater_ids": ";".join(
                        sorted({row["rater_id"] for row, _, _ in rated_sets})
                    ),
                    "selected_n": selected_n,
                    "not_selected_n": len(binary_values) - selected_n,
                    "selection_share": f"{selected_n / len(binary_values):.3f}",
                    "binary_reference": binary_reference,
                    "stability": binary_stability,
                    "modal_share": f"{binary_modal_share:.3f}",
                }
            )

    source_exact_fields = [
        "role",
        "row_id",
        "item_id",
        "model",
        "pair_id",
        "phenomenon",
        "variant",
        "criterion",
        "rater_n",
        "rater_ids",
        "set_counts",
        "exact_set_reference",
        "stability",
        "modal_share",
    ]
    write_csv(
        out_dir / "source-roles-exact-set-reference.csv",
        list(source_exact_rows[0]) if source_exact_rows else source_exact_fields,
        source_exact_rows,
    )

    source_exact_agreement_rows: list[dict[str, Any]] = []
    exact_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_exact_rows:
        exact_groups[row["role"]].append(row)
    for role, rows in sorted(exact_groups.items()):
        modal_shares = [float(row["modal_share"]) for row in rows]
        source_exact_agreement_rows.append(
            {
                "role": role,
                "criterion": "source_roles_exact_set",
                "rows": len(rows),
                "unanimous": sum(row["stability"] == "unanimous" for row in rows),
                "majority": sum(row["stability"] == "majority" for row in rows),
                "insufficient_raters": sum(
                    row["stability"] == "insufficient_raters" for row in rows
                ),
                "ties_or_no_majority": sum(
                    row["stability"] in {"tie", "no_majority"} for row in rows
                ),
                "mean_modal_share": f"{sum(modal_shares) / len(modal_shares):.3f}",
                "stable_reference_rows": sum(
                    row["stability"] in {"unanimous", "majority"} for row in rows
                ),
            }
        )
    write_csv(
        out_dir / "source-roles-exact-set-agreement.csv",
        list(source_exact_agreement_rows[0])
        if source_exact_agreement_rows
        else ["role", "criterion", "rows"],
        source_exact_agreement_rows,
    )

    source_binary_fields = [
        "role",
        "row_id",
        "item_id",
        "model",
        "pair_id",
        "phenomenon",
        "variant",
        "source_role",
        "rater_n",
        "rater_ids",
        "selected_n",
        "not_selected_n",
        "selection_share",
        "binary_reference",
        "stability",
        "modal_share",
    ]
    write_csv(
        out_dir / "source-roles-per-label-reference.csv",
        list(source_binary_rows[0]) if source_binary_rows else source_binary_fields,
        source_binary_rows,
    )

    source_binary_agreement_rows: list[dict[str, Any]] = []
    binary_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in source_binary_rows:
        binary_groups[(row["role"], row["source_role"])].append(row)
    for (role, source_role), rows in sorted(binary_groups.items()):
        selected_ratings = sum(int(row["selected_n"]) for row in rows)
        total_ratings = sum(int(row["rater_n"]) for row in rows)
        modal_shares = [float(row["modal_share"]) for row in rows]
        source_binary_agreement_rows.append(
            {
                "role": role,
                "source_role": source_role,
                "rows": len(rows),
                "selected_ratings": selected_ratings,
                "total_ratings": total_ratings,
                "selection_prevalence": f"{selected_ratings / total_ratings:.3f}"
                if total_ratings
                else "",
                "unanimous": sum(row["stability"] == "unanimous" for row in rows),
                "majority": sum(row["stability"] == "majority" for row in rows),
                "insufficient_raters": sum(
                    row["stability"] == "insufficient_raters" for row in rows
                ),
                "ties_or_no_majority": sum(
                    row["stability"] in {"tie", "no_majority"} for row in rows
                ),
                "stable_selected_reference_rows": sum(
                    row["stability"] in {"unanimous", "majority"}
                    and row["binary_reference"] == "selected"
                    for row in rows
                ),
                "stable_not_selected_reference_rows": sum(
                    row["stability"] in {"unanimous", "majority"}
                    and row["binary_reference"] == "not_selected"
                    for row in rows
                ),
                "stable_reference_rows": sum(
                    row["stability"] in {"unanimous", "majority"} for row in rows
                ),
                "mean_modal_share": f"{sum(modal_shares) / len(modal_shares):.3f}",
            }
        )
    write_csv(
        out_dir / "source-roles-per-label-agreement.csv",
        list(source_binary_agreement_rows[0])
        if source_binary_agreement_rows
        else ["role", "source_role", "rows"],
        source_binary_agreement_rows,
    )

    clarity_exact_rows: list[dict[str, Any]] = []
    for (role, row_id), exact in sorted(source_exact_lookup.items()):
        clarity = reference_lookup.get((role, row_id, "source_role_clarity"))
        if clarity is None:
            continue
        clarity_stable = clarity["stability"] in {"unanimous", "majority"}
        exact_stable = exact["stability"] in {"unanimous", "majority"}
        clarity_uncertain = clarity["independent_reference"] in {
            "genuinely_ambiguous",
            "insufficient_context",
        }
        if not clarity_stable:
            diagnostic = "clarity_no_stable_reference"
        elif clarity_uncertain:
            diagnostic = "clarity_ambiguous_or_insufficient"
        elif exact_stable:
            diagnostic = "clarity_other_stable_and_exact_set_stable"
        else:
            diagnostic = "clarity_other_stable_but_exact_set_unstable"
        clarity_exact_rows.append(
            {
                "role": role,
                "row_id": row_id,
                "item_id": exact["item_id"],
                "model": exact["model"],
                "phenomenon": exact["phenomenon"],
                "clarity_reference": clarity["independent_reference"],
                "clarity_stability": clarity["stability"],
                "exact_set_reference": exact["exact_set_reference"],
                "exact_set_stability": exact["stability"],
                "diagnostic": diagnostic,
            }
        )
    write_csv(
        out_dir / "source-role-clarity-vs-exact-set-stability.csv",
        list(clarity_exact_rows[0])
        if clarity_exact_rows
        else [
            "role",
            "row_id",
            "clarity_reference",
            "clarity_stability",
            "exact_set_reference",
            "exact_set_stability",
            "diagnostic",
        ],
        clarity_exact_rows,
    )

    author_rows = load_optional_rows(private_dir / "author_labels.csv")
    author_by_key = {source_key(row): row for row in author_rows}
    comparable = {
        "linguistic_task": ["task_success"],
        "policy_safety": ["policy_compliance", "refusal_outcome"],
    }
    revision_rows: list[dict[str, Any]] = []
    for reference in reference_rows:
        role, criterion = reference["role"], reference["criterion"]
        if criterion not in comparable.get(role, []):
            continue
        author = author_by_key.get((reference["item_id"], reference["model"]), {})
        author_label = author.get(criterion, "")
        independent = reference["independent_reference"]
        if not author_label:
            status = "author_label_not_available"
        elif reference["stability"] not in {"unanimous", "majority"}:
            status = "no_stable_independent_reference"
        elif author_label == independent:
            status = "retained"
        else:
            status = "candidate_revision"
        revision_rows.append(
            {
                **reference,
                "author_provisional_label": author_label,
                "comparison_status": status,
            }
        )
    revision_fields = list(revision_rows[0]) if revision_rows else ["role", "row_id", "criterion"]
    write_csv(out_dir / "author-label-comparison.csv", revision_fields, revision_rows)
    author_confusion = Counter(
        (
            row["role"],
            row["criterion"],
            row["independent_reference"],
            row["author_provisional_label"],
        )
        for row in revision_rows
        if row["comparison_status"] in {"retained", "candidate_revision"}
    )
    author_confusion_rows = [
        {
            "role": role,
            "criterion": criterion,
            "independent_reference": reference,
            "author_provisional_label": author,
            "rows": count,
        }
        for (role, criterion, reference, author), count in sorted(author_confusion.items())
    ]
    write_csv(
        out_dir / "author-vs-independent-confusion.csv",
        list(author_confusion_rows[0]) if author_confusion_rows else ["role", "criterion", "rows"],
        author_confusion_rows,
    )
    revision_summary: list[dict[str, Any]] = []
    revision_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in revision_rows:
        revision_groups[(row["role"], row["criterion"])].append(row)
    for (role, criterion), rows in sorted(revision_groups.items()):
        comparable_rows = [
            row for row in rows if row["comparison_status"] in {"retained", "candidate_revision"}
        ]
        revised = sum(row["comparison_status"] == "candidate_revision" for row in comparable_rows)
        revision_summary.append(
            {
                "role": role,
                "criterion": criterion,
                "stable_comparable_rows": len(comparable_rows),
                "retained": len(comparable_rows) - revised,
                "candidate_revision": revised,
                "candidate_revision_rate": f"{revised / len(comparable_rows):.3f}"
                if comparable_rows
                else "",
                "no_stable_reference": sum(
                    row["comparison_status"] == "no_stable_independent_reference" for row in rows
                ),
            }
        )
    write_csv(
        out_dir / "author-label-revision-summary.csv",
        list(revision_summary[0]) if revision_summary else ["role", "criterion"],
        revision_summary,
    )

    judge_rows = load_optional_rows(private_dir / "judge_labels.csv")
    judge_by_key = {source_key(row): row for row in judge_rows}
    judge_summary_rows: list[dict[str, Any]] = []
    judge_class_rows: list[dict[str, Any]] = []
    judge_confusion = Counter()
    for role, criteria in comparable.items():
        for criterion in criteria:
            eligible = [
                row
                for row in reference_rows
                if row["role"] == role
                and row["criterion"] == criterion
                and row["stability"] in {"unanimous", "majority"}
                and judge_by_key.get((row["item_id"], row["model"]), {}).get(criterion, "")
            ]
            matched = sum(
                judge_by_key[(row["item_id"], row["model"])][criterion]
                == row["independent_reference"]
                for row in eligible
            )
            for row in eligible:
                judge_confusion[
                    (
                        role,
                        criterion,
                        row["independent_reference"],
                        judge_by_key[(row["item_id"], row["model"])][criterion],
                    )
                ] += 1
            judge_summary_rows.append(
                {
                    "role": role,
                    "criterion": criterion,
                    "stable_reference_rows": len(eligible),
                    "matched": matched,
                    "accuracy": f"{matched / len(eligible):.3f}" if eligible else "",
                    "availability": "available" if judge_rows else "not_available",
                }
            )
            labels = sorted({row["independent_reference"] for row in eligible})
            for label in labels:
                cases = [row for row in eligible if row["independent_reference"] == label]
                recovered = sum(
                    judge_by_key[(row["item_id"], row["model"])][criterion] == label
                    for row in cases
                )
                judge_class_rows.append(
                    {
                        "role": role,
                        "criterion": criterion,
                        "reference_class": label,
                        "reference_rows": len(cases),
                        "judge_recovered": recovered,
                        "class_recall": f"{recovered / len(cases):.3f}" if cases else "",
                    }
                )
    write_csv(
        out_dir / "judge-vs-independent-summary.csv",
        list(judge_summary_rows[0]) if judge_summary_rows else ["role", "criterion"],
        judge_summary_rows,
    )
    write_csv(
        out_dir / "judge-minority-class-recall.csv",
        list(judge_class_rows[0]) if judge_class_rows else ["role", "criterion"],
        judge_class_rows,
    )
    judge_confusion_rows = [
        {
            "role": role,
            "criterion": criterion,
            "independent_reference": reference,
            "judge_label": judge,
            "rows": count,
        }
        for (role, criterion, reference, judge), count in sorted(judge_confusion.items())
    ]
    write_csv(
        out_dir / "judge-vs-independent-confusion.csv",
        list(judge_confusion_rows[0]) if judge_confusion_rows else ["role", "criterion", "rows"],
        judge_confusion_rows,
    )

    by_row: dict[str, dict[tuple[str, str], dict[str, Any]]] = defaultdict(dict)
    for reference in reference_rows:
        by_row[reference["row_id"]][(reference["role"], reference["criterion"])] = reference
    cross_rows: list[dict[str, Any]] = []
    unstable_rows: list[dict[str, Any]] = []
    for row_id, evidence in sorted(by_row.items()):
        task = evidence.get(("linguistic_task", "task_success"), {})
        policy = evidence.get(("policy_safety", "policy_compliance"), {})
        if task and policy:
            relation = "same_direction_or_not_comparable"
            if task["independent_reference"] == "success" and policy["independent_reference"] == "noncompliant":
                relation = "task_success_with_policy_noncompliance"
            elif task["independent_reference"] in {"partial", "failure"} and policy["independent_reference"] == "compliant":
                relation = "task_failure_with_policy_compliance"
            cross_rows.append(
                {
                    "row_id": row_id,
                    "item_id": task["item_id"],
                    "model": task["model"],
                    "phenomenon": task["phenomenon"],
                    "task_success": task["independent_reference"],
                    "task_stability": task["stability"],
                    "policy_compliance": policy["independent_reference"],
                    "policy_stability": policy["stability"],
                    "cross_criterion_pattern": relation,
                }
            )
        for reference in evidence.values():
            if reference["stability"] not in {"unanimous", "majority"} or reference[
                "independent_reference"
            ] in {
                "item_problem",
                "policy_ambiguous",
                "unsure",
                "genuinely_ambiguous",
                "insufficient_context",
            }:
                unstable_rows.append(reference)
    write_csv(
        out_dir / "linguistic-policy-patterns.csv",
        list(cross_rows[0]) if cross_rows else ["row_id", "item_id", "model"],
        cross_rows,
    )
    write_csv(out_dir / "unstable-or-ambiguous-rows.csv", reference_fields, unstable_rows)

    phenomenon_rows: list[dict[str, Any]] = []
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for reference in reference_rows:
        groups[(reference["phenomenon"], reference["role"], reference["criterion"])].append(reference)
    for (phenomenon, role, criterion), rows in sorted(groups.items()):
        phenomenon_rows.append(
            {
                "phenomenon": phenomenon,
                "role": role,
                "criterion": criterion,
                "rows": len(rows),
                "stable_rows": sum(row["stability"] in {"unanimous", "majority"} for row in rows),
                "reference_label_counts": counts_text(row["independent_reference"] for row in rows),
            }
        )
    write_csv(
        out_dir / "phenomenon-summary.csv",
        list(phenomenon_rows[0]) if phenomenon_rows else ["phenomenon", "role", "criterion"],
        phenomenon_rows,
    )

    prefix = "SYNTHETIC TEST RUN. " if synthetic else ""
    candidate_revisions = sum(row["comparison_status"] == "candidate_revision" for row in revision_rows)
    stable = sum(row["stability"] in {"unanimous", "majority"} for row in reference_rows)
    exact_set_stable = sum(
        row["stability"] in {"unanimous", "majority"} for row in source_exact_rows
    )
    source_role_lines = (
        [
            f"- Source-role exact-set reference rows: {len(source_exact_rows)}; stable (unanimous or majority): {exact_set_stable}.",
            f"- Source-role per-label binary reference rows: {len(source_binary_rows)} across {len(source_binary_agreement_rows)} labels.",
            "- Source-role multiplicity, exact-set disagreement, and source-role ambiguity are reported separately.",
        ]
        if source_exact_rows
        else []
    )
    write_markdown(
        out_dir / "analysis-readout.md",
        [
            "# Study A Independent Re-adjudication Readout",
            "",
            f"{prefix}This report preserves role-specific criteria and does not create a combined score.",
            "",
            f"- Ratings ingested: {len(ratings)}.",
            f"- Criterion-level reference rows: {len(reference_rows)}; stable (unanimous or majority): {stable}.",
            *source_role_lines,
            f"- Minimum independent ratings required for a stable reference: {MIN_REFERENCE_RATERS}.",
            "- Historical safety-risk severity and risk-type labels are not compared to the revised visible-boundary fields.",
            f"- Candidate differences from provisional author labels: {candidate_revisions}.",
            f"- Rows requiring ambiguity/instability review: {len(unstable_rows)}.",
            f"- Completed rating blocks with retained burden timing: {len(burden_rows)}.",
            "",
            "The author-label comparison identifies candidates for later documented review; it does not overwrite the frozen author snapshot. Failure attribution remains out of first-pass analysis. Timing estimates describe form burden, not evaluator performance or representativeness.",
        ],
    )
    print(f"Wrote Study A analysis to {out_dir}")
    if synthetic:
        print("Synthetic workflow only: do not treat these outputs as empirical findings.")


if __name__ == "__main__":
    main()
