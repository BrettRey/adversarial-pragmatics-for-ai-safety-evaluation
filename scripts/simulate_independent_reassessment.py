#!/usr/bin/env python3
"""Run the complete Study A workflow on deterministic synthetic data.

This script exists to exercise the blindness boundary, schema, response
ingestion, disagreement handling, and analysis before anyone is recruited. It
does not call a model and does not create empirical benchmark evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build_independent_reassessment.py"
INGEST = ROOT / "scripts" / "ingest_independent_reassessment.py"
ANALYZE = ROOT / "scripts" / "analyze_independent_reassessment.py"
SCHEMA_PATH = ROOT / "benchmark" / "study-a" / "schema.json"
EXPECTED_SCHEMA_VERSION = 6
TASK_GIVER_ROLE = "task_giver_contribution"
DEPRECATED_TASK_GIVER_ROLE = "task_giver_directive"

PHENOMENA = [
    "embedded_command",
    "mention_use",
    "authority_hierarchy",
    "scope_negation",
    "deixis_reference_hijack",
    "indirect_speech_act",
    "agent_transcript_interpretation",
    "policy_boundary_ambiguity",
    "embedded_command",
]
MODELS = ["synthetic-system-a", "synthetic-system-b", "synthetic-system-c"]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        schema = json.load(handle)
    if schema.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        raise SystemExit(
            f"synthetic workflow requires Study A schema v{EXPECTED_SCHEMA_VERSION}"
        )
    return schema


def schema_field(schema: dict[str, Any], role: str, name: str) -> dict[str, Any]:
    for field in schema["roles"][role]["fields"]:
        if field["name"] == name:
            return field
    raise SystemExit(f"Study A schema is missing {role}/{name}")


def base_labels(item_index: int, model_index: int, phenomenon: str) -> dict[str, str]:
    value = item_index * 3 + model_index
    task = "failure" if value % 11 == 0 else "partial" if value % 5 == 0 else "success"
    noncompliant = value % 9 == 0 or (phenomenon == "policy_boundary_ambiguity" and model_index == 1)
    policy = "noncompliant" if noncompliant else "compliant"
    risk = "medium" if noncompliant else "not_applicable"
    risk_type = "confidentiality" if value % 4 == 0 and noncompliant else "integrity" if noncompliant else "none"
    refusal = (
        "under_refusal_probe"
        if noncompliant and phenomenon == "policy_boundary_ambiguity"
        else "not_a_refusal"
    )
    return {
        "task_success": task,
        "policy_compliance": policy,
        "safety_risk": risk,
        "risk_type": risk_type,
        "refusal_outcome": refusal,
    }


def linguistic_fields(labels: dict[str, str], phenomenon: str) -> dict[str, Any]:
    source_roles = {
        "embedded_command": [TASK_GIVER_ROLE, "untrusted_embedded_directive"],
        "mention_use": [TASK_GIVER_ROLE, "quoted_or_reported_directive"],
        "authority_hierarchy": [TASK_GIVER_ROLE, "policy_or_constraint"],
        "scope_negation": [TASK_GIVER_ROLE, "policy_or_constraint"],
        "deixis_reference_hijack": [TASK_GIVER_ROLE],
        "indirect_speech_act": [TASK_GIVER_ROLE],
        "agent_transcript_interpretation": [
            TASK_GIVER_ROLE,
            "untrusted_embedded_directive",
            "data_or_tool_output",
        ],
        "policy_boundary_ambiguity": [TASK_GIVER_ROLE, "policy_or_constraint"],
    }[phenomenon]
    source_role_clarity = {
        "deixis_reference_hijack": "genuinely_ambiguous",
        "policy_boundary_ambiguity": "insufficient_context",
    }.get(phenomenon, "clear")
    return {
        "task_success": labels["task_success"],
        "source_roles": source_roles,
        "source_role_clarity": source_role_clarity,
        "scope_reference": "unresolved_or_ambiguous" if phenomenon == "deixis_reference_hijack" else "not_applicable",
        "clarification_required": "yes" if phenomenon == "deixis_reference_hijack" else "no",
        "response_act_performed": {"success": "yes", "partial": "partly", "failure": "no"}[labels["task_success"]],
    }


def policy_fields(labels: dict[str, str], phenomenon: str) -> dict[str, str]:
    noncompliant = labels["policy_compliance"] == "noncompliant"
    visible_type = {
        "confidentiality": "confidentiality_or_disclosure",
        "integrity": "integrity_or_source_handling",
    }.get(labels["risk_type"], "policy_or_hierarchy")
    boundary_phenomena = {
        "embedded_command",
        "authority_hierarchy",
        "scope_negation",
        "agent_transcript_interpretation",
        "policy_boundary_ambiguity",
    }
    return {
        "policy_compliance": labels["policy_compliance"],
        "visible_boundary_status": (
            "visible_boundary_violation"
            if noncompliant
            else "boundary_stated_no_visible_violation"
            if phenomenon in boundary_phenomena
            else "no_boundary_stated"
        ),
        "visible_boundary_type": visible_type if noncompliant else "none",
        "refusal_outcome": labels["refusal_outcome"],
        "information_flow_action_licensing": "violation" if noncompliant else "no_violation",
    }


def perturb(
    role: str, values: dict[str, Any], row_number: int, rater_number: int
) -> dict[str, Any]:
    """Create a small, documented amount of synthetic disagreement."""
    output = dict(values)
    # Raw multiselect order is not semantically meaningful. Reverse some valid
    # responses so ingestion must canonicalize them before CSV/analysis.
    if role == "linguistic_task" and rater_number == 2:
        source_roles = output.get("source_roles", [])
        if len(source_roles) > 1:
            output["source_roles"] = list(reversed(source_roles))
    # Both synthetic raters depart from the provisional author label on a few
    # rows, so the author-comparison branch is tested as well as disagreement.
    if row_number % 19 == 0:
        if role == "linguistic_task":
            output["task_success"] = "partial" if output["task_success"] == "success" else "failure"
            output["response_act_performed"] = "partly" if output["task_success"] == "partial" else "no"
        else:
            output["policy_compliance"] = "noncompliant"
            output["visible_boundary_status"] = "visible_boundary_violation"
            output["visible_boundary_type"] = "integrity_or_source_handling"
            output["information_flow_action_licensing"] = "violation"
    if rater_number == 2 and row_number % 13 == 0:
        if role == "linguistic_task":
            output["task_success"] = "partial" if output["task_success"] == "success" else "success"
        else:
            output["policy_compliance"] = "policy_ambiguous"
            output["visible_boundary_status"] = "insufficient_visible_context"
            output["visible_boundary_type"] = "mixed_or_unclear"
    if rater_number == 2 and row_number % 17 == 0:
        if role == "linguistic_task":
            output["clarification_required"] = "reasonable_but_not_required"
        else:
            output["visible_boundary_status"] = "insufficient_visible_context"
            output["visible_boundary_type"] = "mixed_or_unclear"
    return output


def run(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT, text=True, check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def check_practice_assets(package_dir: Path) -> None:
    """Assert that synthetic packaging includes the separate practice experience."""
    audit_path = package_dir / "training-package-audit.json"
    if not audit_path.exists():
        raise SystemExit("synthetic package did not produce training-package-audit.json")
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if audit.get("status") != "pass" or not audit.get("practice_only"):
        raise SystemExit("synthetic package training audit did not pass")
    for role in ("linguistic_task", "policy_safety"):
        path = package_dir / "training" / role / "index.html"
        if not path.exists():
            raise SystemExit(f"synthetic package is missing practice form for {role}")
        html = path.read_text(encoding="utf-8")
        if "Practice only" not in html or "This is not a study row" not in html:
            raise SystemExit(f"synthetic package practice form is incomplete for {role}")


def check_partial_coverage(processed_dir: Path) -> None:
    """Verify that completed partial returns are preserved and marked as such."""
    coverage_path = processed_dir / "rater-role-coverage.csv"
    if not coverage_path.exists():
        raise SystemExit("synthetic ingestion did not produce rater-role coverage")
    with coverage_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    partial = [row for row in rows if row.get("coverage_status") == "partial"]
    if len(partial) != 2:
        raise SystemExit("synthetic partial returns were not retained as expected")


def check_raw_source_role_responses(response_dir: Path, schema: dict[str, Any]) -> None:
    """Exercise array shape, multiple selections, and order normalization."""
    roles_field = schema_field(schema, "linguistic_task", "source_roles")
    clarity_field = schema_field(schema, "linguistic_task", "source_role_clarity")
    if roles_field.get("type") != "multiselect":
        raise SystemExit("source_roles is not declared as a multiselect")
    options = roles_field.get("options", [])
    allowed = set(options)
    if TASK_GIVER_ROLE not in allowed or DEPRECATED_TASK_GIVER_ROLE in allowed:
        raise SystemExit("Study A v6 source-role options do not use the current task-giver value")
    clarity_options = set(clarity_field.get("options", []))
    seen_clarities: set[str] = set()
    saw_single = False
    saw_multiple = False
    saw_noncanonical_order = False
    rationale_states: set[str] = set()
    deprecated = {"pragmatic_status", "source_interpretation"}
    for role in schema["roles"]:
        if schema_field(schema, role, "rationale").get("required", True):
            raise SystemExit(f"{role} rationale is not declared optional")
    paths = sorted(response_dir.glob("synthetic-*.json"))
    if not paths:
        raise SystemExit("synthetic workflow produced no response JSON")
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for response in payload["responses"]:
            if "rationale" not in response:
                rationale_states.add("omitted")
            elif response["rationale"] == "":
                rationale_states.add("blank")
            elif isinstance(response["rationale"], str) and response["rationale"].strip():
                rationale_states.add("nonblank")
            if deprecated.intersection(response):
                raise SystemExit(f"{path.name} retains a deprecated Study A role field")
            if payload["role"] != "linguistic_task":
                if "source_roles" in response or "source_role_clarity" in response:
                    raise SystemExit(f"{path.name} leaks linguistic fields into policy responses")
                continue
            selected = response.get("source_roles")
            if (
                not isinstance(selected, list)
                or not selected
                or any(not isinstance(value, str) for value in selected)
                or len(selected) != len(set(selected))
                or any(value not in allowed for value in selected)
            ):
                raise SystemExit(f"{path.name} has an invalid synthetic source_roles array")
            if DEPRECATED_TASK_GIVER_ROLE in selected:
                raise SystemExit(f"{path.name} retains the deprecated v5 task-giver value")
            canonical = [option for option in options if option in set(selected)]
            saw_noncanonical_order |= selected != canonical
            saw_single |= len(selected) == 1
            saw_multiple |= len(selected) > 1
            clarity = response.get("source_role_clarity")
            if clarity not in clarity_options:
                raise SystemExit(f"{path.name} has invalid source_role_clarity {clarity!r}")
            seen_clarities.add(clarity)
    if not saw_single or not saw_multiple:
        raise SystemExit("synthetic source_roles did not exercise single and multiple selections")
    if not saw_noncanonical_order:
        raise SystemExit("synthetic source_roles did not exercise reversed raw option order")
    if clarity_options - seen_clarities:
        raise SystemExit(
            "synthetic source_role_clarity did not exercise: "
            + ", ".join(sorted(clarity_options - seen_clarities))
        )
    if rationale_states != {"omitted", "blank", "nonblank"}:
        raise SystemExit(
            "synthetic rationales did not exercise omitted, blank, and nonblank values"
        )


def check_ingested_source_roles(processed_dir: Path, schema: dict[str, Any]) -> None:
    """Assert compact canonical JSON in CSV and blank cross-role cells."""
    roles_field = schema_field(schema, "linguistic_task", "source_roles")
    options = roles_field.get("options", [])
    clarity_options = schema_field(
        schema, "linguistic_task", "source_role_clarity"
    ).get("options", [])
    path = processed_dir / "ratings-long.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        rows = list(reader)
    required = {"source_roles", "source_role_clarity"}
    if not required.issubset(fieldnames):
        raise SystemExit("ingested ratings are missing v6 source-role columns")
    if {"pragmatic_status", "source_interpretation"}.intersection(fieldnames):
        raise SystemExit("ingested ratings retain deprecated Study A role columns")
    if not any(row.get("rationale", "") == "" for row in rows):
        raise SystemExit("ingested ratings did not retain blank optional rationales")
    if not any(row.get("rationale", "").strip() for row in rows):
        raise SystemExit("ingested ratings did not retain nonblank optional rationales")
    for row in rows:
        cell = row.get("source_roles", "")
        if row["role"] == "policy_safety":
            if cell or row.get("source_role_clarity", ""):
                raise SystemExit("policy ratings must have blank source-role CSV cells")
            continue
        try:
            selected = json.loads(cell)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"source_roles is not JSON in {path}: {cell!r}") from exc
        if (
            not isinstance(selected, list)
            or not selected
            or any(not isinstance(value, str) for value in selected)
            or len(selected) != len(set(selected))
        ):
            raise SystemExit(f"source_roles is not a nonempty unique string array: {cell!r}")
        if DEPRECATED_TASK_GIVER_ROLE in selected:
            raise SystemExit("ingested ratings retain the deprecated v5 task-giver value")
        canonical = [option for option in options if option in set(selected)]
        compact = json.dumps(canonical, ensure_ascii=False, separators=(",", ":"))
        if selected != canonical or cell != compact:
            raise SystemExit(f"source_roles is not canonical compact JSON: {cell!r}")
        clarity = row.get("source_role_clarity", "")
        if clarity not in clarity_options:
            raise SystemExit(f"source_role_clarity is invalid after ingestion: {clarity!r}")


def check_deprecated_source_role_rejection(private_dir: Path, response_dir: Path) -> None:
    """Verify that v6 ingestion rejects the retired v5 task-giver machine value."""
    source_path = next(response_dir.glob("synthetic-linguistic_task-*.json"), None)
    if source_path is None:
        raise SystemExit("cannot test deprecated source-role rejection without a linguistic response")
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    replaced = False
    for response in payload["responses"]:
        selected = response.get("source_roles", [])
        if TASK_GIVER_ROLE in selected:
            response["source_roles"] = [
                DEPRECATED_TASK_GIVER_ROLE if value == TASK_GIVER_ROLE else value
                for value in selected
            ]
            replaced = True
            break
    if not replaced:
        raise SystemExit("synthetic responses do not exercise the current task-giver value")
    with tempfile.TemporaryDirectory(prefix="study-a-v6-deprecated-") as temp_dir:
        invalid_path = Path(temp_dir) / "deprecated-v5-response.json"
        invalid_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(INGEST),
                "--private-dir",
                str(private_dir),
                "--responses",
                str(invalid_path),
                "--out-dir",
                str(Path(temp_dir) / "processed"),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    output = completed.stdout + completed.stderr
    if completed.returncode == 0 or "deprecated v5 selected value" not in output:
        raise SystemExit("v6 ingestion did not reject task_giver_directive as expected")


def check_analysis_source_role_outputs(
    analysis_dir: Path, schema: dict[str, Any]
) -> None:
    """Ensure scalar clarity and dedicated multilabel analyses are retained."""
    paths = {
        "scalar_reference": analysis_dir / "independent-reference-labels.csv",
        "scalar_agreement": analysis_dir / "agreement-by-criterion.csv",
        "exact_reference": analysis_dir / "source-roles-exact-set-reference.csv",
        "exact_agreement": analysis_dir / "source-roles-exact-set-agreement.csv",
        "label_reference": analysis_dir / "source-roles-per-label-reference.csv",
        "label_agreement": analysis_dir / "source-roles-per-label-agreement.csv",
        "clarity_diagnostic": analysis_dir
        / "source-role-clarity-vs-exact-set-stability.csv",
    }
    for path in paths.values():
        if not path.exists():
            raise SystemExit(f"synthetic analysis is missing {path.name}")
    with paths["scalar_reference"].open(encoding="utf-8", newline="") as handle:
        reference_rows = list(csv.DictReader(handle))
    with paths["scalar_agreement"].open(encoding="utf-8", newline="") as handle:
        agreement_rows = list(csv.DictReader(handle))
    reference_criteria = {
        row["criterion"] for row in reference_rows if row["role"] == "linguistic_task"
    }
    agreement_criteria = {
        row["criterion"] for row in agreement_rows if row["role"] == "linguistic_task"
    }
    if "source_role_clarity" not in reference_criteria or "source_role_clarity" not in agreement_criteria:
        raise SystemExit("synthetic analysis dropped scalar source_role_clarity")
    if "source_roles" in reference_criteria or "source_roles" in agreement_criteria:
        raise SystemExit("synthetic analysis treated source_roles as a scalar criterion")

    with paths["exact_reference"].open(encoding="utf-8", newline="") as handle:
        exact_rows = list(csv.DictReader(handle))
    stable_role_rows = [
        row
        for row in exact_rows
        if row["criterion"] == "source_roles_exact_set"
        and row["stability"] in {"unanimous", "majority"}
    ]
    if not stable_role_rows:
        raise SystemExit("synthetic analysis produced no stable source_roles reference")
    schema_order = schema_field(schema, "linguistic_task", "source_roles").get(
        "options", []
    )
    declared_roles = set(schema_order)
    if TASK_GIVER_ROLE not in declared_roles or DEPRECATED_TASK_GIVER_ROLE in declared_roles:
        raise SystemExit("synthetic analysis is not using the v6 task-giver source role")
    for row in stable_role_rows:
        label = row["exact_set_reference"]
        try:
            parsed = json.loads(label)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"analyzed source_roles reference is not JSON: {label!r}") from exc
        valid_list = isinstance(parsed, list) and all(
            isinstance(value, str) for value in parsed
        )
        canonical = (
            [option for option in schema_order if option in set(parsed)]
            if valid_list
            else []
        )
        if (
            not valid_list
            or not parsed
            or parsed != canonical
            or label != json.dumps(parsed, ensure_ascii=False, separators=(",", ":"))
        ):
            raise SystemExit(f"analyzed source_roles reference is not compact JSON: {label!r}")

    with paths["exact_agreement"].open(encoding="utf-8", newline="") as handle:
        exact_agreement_rows = list(csv.DictReader(handle))
    if not any(
        row.get("criterion") == "source_roles_exact_set" for row in exact_agreement_rows
    ):
        raise SystemExit("synthetic analysis dropped exact-set agreement")
    with paths["label_reference"].open(encoding="utf-8", newline="") as handle:
        label_rows = list(csv.DictReader(handle))
    with paths["label_agreement"].open(encoding="utf-8", newline="") as handle:
        label_agreement_rows = list(csv.DictReader(handle))
    if {row.get("source_role", "") for row in label_rows} != declared_roles:
        raise SystemExit("synthetic per-label references do not cover all source roles")
    if {row.get("source_role", "") for row in label_agreement_rows} != declared_roles:
        raise SystemExit("synthetic per-label agreement does not cover all source roles")
    with paths["clarity_diagnostic"].open(encoding="utf-8", newline="") as handle:
        diagnostic_rows = list(csv.DictReader(handle))
    if not diagnostic_rows or not any(
        row.get("clarity_reference") in {"genuinely_ambiguous", "insufficient_context"}
        for row in diagnostic_rows
    ):
        raise SystemExit("synthetic analysis did not retain source-role clarity diagnostics")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "benchmark" / "study-a" / "_runs" / "synthetic",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir.resolve()
    if out_dir.exists() and any(out_dir.iterdir()):
        if not args.overwrite:
            raise SystemExit(f"synthetic output exists: {out_dir}; pass --overwrite")
        shutil.rmtree(out_dir)
    source_dir = out_dir / "source"
    comparison_dir = out_dir / "comparison"
    package_dir = out_dir / "blind-packages"
    private_dir = out_dir / "private"
    response_dir = private_dir / "responses"
    output_rows: list[dict[str, str]] = []
    author_rows: list[dict[str, str]] = []
    judge_rows: list[dict[str, str]] = []
    for item_index in range(18):
        phenomenon = PHENOMENA[item_index // 2]
        item_id = f"SYN-{item_index + 1:03d}"
        for model_index, model in enumerate(MODELS):
            labels = base_labels(item_index, model_index, phenomenon)
            output_rows.append(
                {
                    "item_id": item_id,
                    "model": model,
                    "pair_id": f"SP{item_index // 2 + 1:02d}",
                    "phenomenon": phenomenon,
                    "variant": "a" if item_index % 2 == 0 else "b",
                    "prompt": (
                        f"Synthetic fixture {item_id}: interpret the visible request under the stated "
                        "constraints. This fixture contains no real user data."
                    ),
                    "response": (
                        f"Synthetic response {item_id}/{model_index + 1}. "
                        "The text is generated only to test the Study A workflow."
                    ),
                }
            )
            author_rows.append(
                {
                    "item_id": item_id,
                    "model": model,
                    **labels,
                }
            )
            judge = dict(labels)
            if labels["safety_risk"] != "not_applicable":
                judge["safety_risk"] = "not_applicable"
                judge["policy_compliance"] = "compliant"
            judge_rows.append({"item_id": item_id, "model": model, **judge})
    output_path = source_dir / "synthetic-outputs.csv"
    author_path = comparison_dir / "synthetic-author-labels.csv"
    judge_path = comparison_dir / "synthetic-judge-labels.csv"
    write_csv(output_path, list(output_rows[0]), output_rows)
    write_csv(author_path, list(author_rows[0]), author_rows)
    write_csv(judge_path, list(judge_rows[0]), judge_rows)
    run(
        [
            sys.executable,
            str(BUILD),
            "--source",
            str(output_path),
            "--out-dir",
            str(package_dir),
            "--private-dir",
            str(private_dir),
            "--author-labels",
            str(author_path),
            "--judge-labels",
            str(judge_path),
            "--row-salt",
            "synthetic-study-a-salt-v1",
            "--overwrite",
        ]
    )
    metadata_path = private_dir / "study-private-metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["synthetic"] = True
    metadata["synthetic_notice"] = "All source rows, labels, and ratings in this run are synthetic test data."
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    check_practice_assets(package_dir)

    schema = load_schema()
    with (private_dir / "row_map.tsv").open(encoding="utf-8", newline="") as handle:
        row_map = list(csv.DictReader(handle, delimiter="\t"))
    labels_by_key = {(row["item_id"], row["model"]): row for row in author_rows}
    block_size = 18
    blocks = [row_map[index : index + block_size] for index in range(0, len(row_map), block_size)]
    for role, role_schema in schema["roles"].items():
        for rater_number in (1, 2, 3):
            rater_id = ("LING" if role == "linguistic_task" else "POL") + f"-{rater_number:02d}"
            rater_blocks = blocks if rater_number in (1, 2) else blocks[:1]
            for block_index, block in enumerate(rater_blocks, start=1):
                responses: list[dict[str, Any]] = []
                for offset, mapped in enumerate(block, start=1):
                    row_number = (block_index - 1) * block_size + offset
                    labels = labels_by_key[(mapped["item_id"], mapped["model"])]
                    values = (
                        linguistic_fields(labels, mapped["phenomenon"])
                        if role == "linguistic_task"
                        else policy_fields(labels, mapped["phenomenon"])
                    )
                    values = perturb(role, values, row_number, rater_number)
                    response = {"row_id": mapped["row_id"], **values, "confidence": "high" if row_number % 6 else "medium"}
                    if (row_number + rater_number) % 6 == 0:
                        pass
                    elif (row_number + rater_number) % 4 == 0:
                        response["rationale"] = ""
                    else:
                        response["rationale"] = "Synthetic fixture rating used only to test the independent re-adjudication workflow."
                    responses.append(response)
                payload = {
                    "schema_version": schema["schema_version"],
                    "study_id": "AP-STUDY-A-INDEPENDENT-READJUDICATION",
                    "role": role,
                    "block_id": f"block-{block_index:02d}-of-{len(blocks):02d}",
                    "rater_id": rater_id,
                    "started_at": (datetime.now(timezone.utc) - timedelta(seconds=420 + row_number)).isoformat(),
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "elapsed_seconds": 420 + row_number,
                    "saved_at": datetime.now(timezone.utc).isoformat(),
                    "responses": responses,
                }
                response_dir.mkdir(parents=True, exist_ok=True)
                (response_dir / f"synthetic-{role}-{payload['block_id']}-{rater_id}.json").write_text(
                    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
                )
    check_raw_source_role_responses(response_dir, schema)
    check_deprecated_source_role_rejection(private_dir, response_dir)
    run(
        [
            sys.executable,
            str(INGEST),
            "--private-dir",
            str(private_dir),
        ]
    )
    check_partial_coverage(private_dir / "processed")
    check_ingested_source_roles(private_dir / "processed", schema)
    run(
        [
            sys.executable,
            str(ANALYZE),
            "--private-dir",
            str(private_dir),
        ]
    )
    check_analysis_source_role_outputs(private_dir / "analysis", schema)
    (out_dir / "SYNTHETIC-NOT-EMPIRICAL.md").write_text(
        "# Synthetic Workflow Run\n\n"
        "All source outputs, author labels, judge labels, and rater responses in this "
        "directory are deterministic synthetic test data. They must not be quoted as "
        "model, evaluator, or benchmark results.\n",
        encoding="utf-8",
    )
    print(f"Synthetic Study A workflow complete: {out_dir}")


if __name__ == "__main__":
    main()
