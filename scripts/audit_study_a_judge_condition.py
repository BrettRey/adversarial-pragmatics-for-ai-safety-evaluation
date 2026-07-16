#!/usr/bin/env python3
"""Audit the retained Study A judge condition and visible-rule diagnostics.

The two existing Mistral files are retained as canonical comparator outputs.
This audit checks their structure and the elicitation code without calling a
model.  The visible-rule sentinels are deliberately reported separately: they
were selected after the comparator output was visible and therefore diagnose
particular labels but do not validate, invalidate, or estimate the accuracy of
either comparator.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import inspect
import json
from pathlib import Path
from typing import Any

import run_study_a_judge as judge


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_PATH = (
    ROOT / "benchmark" / "results" / "local-pilot-20260630-185417" / "outputs.csv"
)
SENTINEL_PATH = (
    ROOT / "benchmark" / "study-a" / "judge-comparators" / "visible-rule-sentinels.json"
)
AUDIT_PATH = (
    ROOT / "benchmark" / "study-a" / "judge-comparators" / "judge-condition-audit.json"
)
PROMPT_VARIANT = "option_a_v7_roleseparated"
EXPECTED_CRITERIA_BY_ROLE = {
    "linguistic": ["task_success"],
    "policy": ["policy_compliance", "refusal_outcome"],
}
COMPARATORS = [
    {
        "path": "benchmark/study-a/judge-comparators/judge-labels-mistral-7b.csv",
        "judge_model": "mistral:7b-instruct-v0.3-q4_K_M",
        "judge_run_id": "study-a-judge-20260716T095320Z",
    },
    {
        "path": "benchmark/study-a/judge-comparators/judge-labels-mistral-24b.csv",
        "judge_model": "mistral-small:24b-instruct-2501-q4_K_M",
        "judge_run_id": "study-a-judge-20260716T095536Z",
    },
]
FORBIDDEN_METADATA_FIELDS = [
    "expected_behavior",
    "control_dimension",
    "context_source",
    "source_role",
    "authority_level",
    "pragmatic_status",
    "response_act",
    "item_id",
    "variant",
    "model",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def add_check(
    checks: dict[str, bool], errors: list[str], name: str, passed: bool, detail: str
) -> None:
    checks[name] = bool(passed)
    if not passed:
        errors.append(f"{name}: {detail}")


def audit_prompt_structure(
    source_rows: list[dict[str, str]], codebook: dict[str, dict[str, Any]]
) -> tuple[dict[str, bool], list[str]]:
    checks: dict[str, bool] = {}
    errors: list[str] = []
    add_check(
        checks,
        errors,
        "criteria_constant_is_outcome_only",
        list(judge.CRITERIA) == ["task_success", "policy_compliance", "refusal_outcome"],
        f"found {judge.CRITERIA!r}",
    )
    add_check(
        checks,
        errors,
        "criteria_are_role_separated",
        judge.CRITERIA_BY_ROLE == EXPECTED_CRITERIA_BY_ROLE,
        f"found {judge.CRITERIA_BY_ROLE!r}",
    )
    add_check(
        checks,
        errors,
        "codebook_is_exactly_three_outcomes",
        set(codebook) == set(judge.CRITERIA),
        f"found {sorted(codebook)!r}",
    )
    add_check(
        checks,
        errors,
        "build_prompt_accepts_only_visible_record_codebook_and_role_criteria",
        list(inspect.signature(judge.build_prompt).parameters)
        == ["user_prompt", "model_response", "codebook", "criteria"],
        f"signature is {inspect.signature(judge.build_prompt)}",
    )

    visible_prompt = "__VISIBLE_USER_PROMPT_SENTINEL__"
    visible_response = "__VISIBLE_MODEL_RESPONSE_SENTINEL__"
    hidden_values = {
        field: f"__HIDDEN_{field.upper()}_SENTINEL__"
        for field in FORBIDDEN_METADATA_FIELDS
    }
    role_prompts: dict[str, str] = {}
    for role, criteria in EXPECTED_CRITERIA_BY_ROLE.items():
        prompt = judge.build_prompt(visible_prompt, visible_response, codebook, criteria)
        role_prompts[role] = prompt
        add_check(
            checks,
            errors,
            f"{role}_prompt_contains_visible_prompt_and_response",
            visible_prompt in prompt and visible_response in prompt,
            "one or both visible-record sentinels are absent",
        )
        own_markers = [f"\n{name} --" for name in criteria]
        other = [name for name in judge.CRITERIA if name not in criteria]
        add_check(
            checks,
            errors,
            f"{role}_prompt_contains_only_its_outcome_fields",
            all(marker in prompt for marker in own_markers)
            and all(f"\n{name} --" not in prompt and f'"{name}"' not in prompt for name in other),
            "another role's outcome field appears or an own-role field is absent",
        )
        add_check(
            checks,
            errors,
            f"{role}_prompt_excludes_synthetic_hidden_metadata_values",
            all(value not in prompt for value in hidden_values.values()),
            "a hidden metadata sentinel appears",
        )

    runner_source = inspect.getsource(judge.main)
    add_check(
        checks,
        errors,
        "runner_calls_build_prompt_with_prompt_and_response_only",
        'build_prompt(row["prompt"], row["response"], codebook, criteria)' in runner_source,
        "the expected visible-record-only call was not found in runner main",
    )

    identifiers_absent = True
    leaked_identifiers: list[str] = []
    metadata_values_absent = True
    leaked_metadata_values: list[str] = []
    for row in source_rows:
        for role, criteria in EXPECTED_CRITERIA_BY_ROLE.items():
            prompt = judge.build_prompt(row["prompt"], row["response"], codebook, criteria)
            for field in ("item_id", "model"):
                value = row[field]
                if value and value in prompt:
                    identifiers_absent = False
                    leaked_identifiers.append(f"{row['item_id']}/{row['model']}/{role}:{field}")
            scaffold = prompt.replace(row["prompt"], "", 1).replace(row["response"], "", 1)
            for field in FORBIDDEN_METADATA_FIELDS:
                value = row.get(field, "").strip()
                # A design value can lexically collide with authorized generic
                # wording or a role codebook value (for example, ``ambiguous``).
                # Count it as a leak only if it is added outside the visible
                # record and is not already part of the fixed role scaffold.
                if value and value in scaffold and value not in role_prompts[role]:
                    metadata_values_absent = False
                    leaked_metadata_values.append(
                        f"{row['item_id']}/{row['model']}/{role}:{field}={value!r}"
                    )
    add_check(
        checks,
        errors,
        "actual_item_and_model_identifiers_absent_from_prompts",
        identifiers_absent,
        ", ".join(leaked_identifiers[:5]),
    )
    add_check(
        checks,
        errors,
        "actual_metadata_values_absent_outside_visible_record",
        metadata_values_absent,
        ", ".join(leaked_metadata_values[:5]),
    )

    # These are metadata keys, not ordinary English words.  `model` is checked
    # above by its concrete identifier because the visible heading necessarily
    # says "Model response".
    forbidden_key_tokens = [field for field in FORBIDDEN_METADATA_FIELDS if field != "model"]
    add_check(
        checks,
        errors,
        "metadata_field_names_absent_from_prompt_scaffold",
        all(token not in prompt for prompt in role_prompts.values() for token in forbidden_key_tokens),
        "a forbidden metadata field name appears in the generated scaffold",
    )
    return checks, errors


def audit_comparator(
    spec: dict[str, str],
    source_keys: set[tuple[str, str]],
    allowed: dict[str, set[str]],
) -> tuple[dict[str, Any], dict[tuple[str, str], dict[str, str]], list[str]]:
    path = ROOT / spec["path"]
    errors: list[str] = []
    rows_by_key: dict[tuple[str, str], dict[str, str]] = {}
    if not path.exists():
        return {
            "path": spec["path"],
            "status": "fail",
            "errors": ["file is missing"],
        }, rows_by_key, [f"{spec['path']}: file is missing"]
    rows = read_csv(path)
    required = {
        "item_id",
        "model",
        "judge_run_id",
        "judge_model",
        "prompt_variant",
        "judge_task_success",
        "judge_policy_compliance",
        "judge_refusal_outcome",
        "parse_error",
        "raw_response",
    }
    columns = set(rows[0]) if rows else set()
    if not rows:
        errors.append("file has no rows")
    if missing := sorted(required - columns):
        errors.append(f"missing columns: {missing}")
    duplicates: list[tuple[str, str]] = []
    for row in rows:
        key = (row.get("item_id", ""), row.get("model", ""))
        if key in rows_by_key:
            duplicates.append(key)
        rows_by_key[key] = row
    if len(rows) != 54:
        errors.append(f"expected 54 rows, found {len(rows)}")
    if duplicates:
        errors.append(f"duplicate keys: {duplicates[:5]!r}")
    if set(rows_by_key) != source_keys:
        missing_keys = sorted(source_keys - set(rows_by_key))
        extra_keys = sorted(set(rows_by_key) - source_keys)
        errors.append(f"key mismatch; missing={missing_keys[:5]!r}, extra={extra_keys[:5]!r}")
    run_ids = {row.get("judge_run_id", "") for row in rows}
    judge_models = {row.get("judge_model", "") for row in rows}
    variants = {row.get("prompt_variant", "") for row in rows}
    if run_ids != {spec["judge_run_id"]}:
        errors.append(f"judge_run_id values are {sorted(run_ids)!r}")
    if judge_models != {spec["judge_model"]}:
        errors.append(f"judge_model values are {sorted(judge_models)!r}")
    if variants != {PROMPT_VARIANT}:
        errors.append(f"prompt_variant values are {sorted(variants)!r}")
    parse_errors = [index for index, row in enumerate(rows, 2) if row.get("parse_error", "").strip()]
    blank_raw = [index for index, row in enumerate(rows, 2) if not row.get("raw_response", "").strip()]
    if parse_errors:
        errors.append(f"nonblank parse_error at CSV lines {parse_errors[:10]!r}")
    if blank_raw:
        errors.append(f"blank raw_response at CSV lines {blank_raw[:10]!r}")
    invalid_labels: list[str] = []
    for row in rows:
        for criterion in judge.CRITERIA:
            raw_value = row.get(f"judge_{criterion}", "")
            value = raw_value.strip()
            if raw_value != value:
                invalid_labels.append(
                    f"{row.get('item_id')}/{row.get('model')} {criterion} has surrounding whitespace"
                )
            if value not in allowed[criterion]:
                invalid_labels.append(
                    f"{row.get('item_id')}/{row.get('model')} {criterion}={value!r}"
                )
    if invalid_labels:
        errors.append("invalid or blank labels: " + "; ".join(invalid_labels[:10]))
    summary = {
        "path": spec["path"],
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "row_count": len(rows),
        "unique_key_count": len(rows_by_key),
        "judge_model": spec["judge_model"],
        "judge_run_id": spec["judge_run_id"],
        "prompt_variant": PROMPT_VARIANT,
        "parse_error_count": len(parse_errors),
        "blank_raw_response_count": len(blank_raw),
        "status": "pass" if not errors else "fail",
        "errors": errors,
    }
    return summary, rows_by_key, [f"{spec['path']}: {error}" for error in errors]


def expand_models(
    sentinel: dict[str, Any], source_models_by_item: dict[str, list[str]]
) -> list[str]:
    declared = sentinel.get("models")
    if declared == "*":
        return source_models_by_item.get(str(sentinel.get("item_id", "")), [])
    if isinstance(declared, list):
        return sorted(str(value) for value in declared)
    return []


def validate_sentinel_definition(
    definition: dict[str, Any],
    source_models_by_item: dict[str, list[str]],
    allowed: dict[str, set[str]],
) -> list[str]:
    errors: list[str] = []
    if definition.get("study") != "A":
        errors.append("sentinel definition study is not A")
    if definition.get("status") != "diagnostic_only":
        errors.append("sentinel definition status is not diagnostic_only")
    if definition.get("selection_timing") != "post_comparator_output_pre_freeze":
        errors.append("sentinel definition does not disclose post-output/pre-freeze selection")
    if definition.get("invalidates_comparator_on_mismatch") is not False:
        errors.append("sentinel definition incorrectly permits mismatch invalidation")
    if not str(definition.get("selection_disclosure", "")).strip():
        errors.append("sentinel definition lacks a selection disclosure")
    sentinels = definition.get("sentinels")
    if not isinstance(sentinels, list) or not sentinels:
        return errors + ["sentinel definition has no sentinel list"]
    identifiers = [str(sentinel.get("sentinel_id", "")) for sentinel in sentinels]
    if "" in identifiers or len(set(identifiers)) != len(identifiers):
        errors.append("sentinel identifiers are blank or duplicated")
    expanded_keys: set[tuple[str, str, str]] = set()
    for sentinel in sentinels:
        sentinel_id = str(sentinel.get("sentinel_id", ""))
        item_id = str(sentinel.get("item_id", ""))
        criterion = str(sentinel.get("criterion", ""))
        expected = str(sentinel.get("expected_visible_rule_label", ""))
        models = expand_models(sentinel, source_models_by_item)
        if item_id not in source_models_by_item:
            errors.append(f"{sentinel_id}: unknown item_id")
        if criterion not in allowed:
            errors.append(f"{sentinel_id}: unknown criterion")
        elif expected not in allowed[criterion]:
            errors.append(f"{sentinel_id}: expected label is outside the schema")
        if not models or not set(models).issubset(source_models_by_item.get(item_id, [])):
            errors.append(f"{sentinel_id}: model selection is empty or outside the source grid")
        if not str(sentinel.get("basis", "")).strip():
            errors.append(f"{sentinel_id}: missing visible-rule basis")
        for model in models:
            key = (item_id, model, criterion)
            if key in expanded_keys:
                errors.append(f"{sentinel_id}: duplicate expanded item/model/criterion check")
            expanded_keys.add(key)
    return errors


def sentinel_diagnostics(
    definition: dict[str, Any],
    source_models_by_item: dict[str, list[str]],
    comparator_rows: dict[str, dict[tuple[str, str], dict[str, str]]],
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    by_comparator: list[dict[str, Any]] = []
    total_matches = 0
    total_mismatches = 0
    for spec in COMPARATORS:
        path = spec["path"]
        rows = comparator_rows.get(path, {})
        matches = 0
        mismatches = 0
        for sentinel in definition.get("sentinels", []):
            item_id = str(sentinel.get("item_id", ""))
            criterion = str(sentinel.get("criterion", ""))
            expected = str(sentinel.get("expected_visible_rule_label", ""))
            for model in expand_models(sentinel, source_models_by_item):
                row = rows.get((item_id, model))
                actual = row.get(f"judge_{criterion}", "") if row else ""
                matched = actual == expected
                matches += int(matched)
                mismatches += int(not matched)
                results.append(
                    {
                        "sentinel_id": sentinel.get("sentinel_id"),
                        "comparator": path,
                        "judge_model": spec["judge_model"],
                        "item_id": item_id,
                        "source_model": model,
                        "criterion": criterion,
                        "expected_visible_rule_label": expected,
                        "actual_comparator_label": actual,
                        "match": matched,
                    }
                )
        total_matches += matches
        total_mismatches += mismatches
        by_comparator.append(
            {
                "comparator": path,
                "judge_model": spec["judge_model"],
                "check_count": matches + mismatches,
                "match_count": matches,
                "mismatch_count": mismatches,
            }
        )
    return {
        "status": "diagnostic_mismatches_present" if total_mismatches else "all_selected_checks_match",
        "selection_timing": definition.get("selection_timing"),
        "selection_disclosure": definition.get("selection_disclosure"),
        "invalidates_comparator_on_mismatch": False,
        "independent_accuracy_estimate": False,
        "check_count": total_matches + total_mismatches,
        "match_count": total_matches,
        "mismatch_count": total_mismatches,
        "by_comparator": by_comparator,
        "results": results,
    }


def build_audit() -> dict[str, Any]:
    structural_errors: list[str] = []
    source_rows = read_csv(OUTPUTS_PATH)
    source_keys = {(row["item_id"], row["model"]) for row in source_rows}
    source_models_by_item: dict[str, list[str]] = {}
    for item_id in sorted({row["item_id"] for row in source_rows}):
        source_models_by_item[item_id] = sorted(
            row["model"] for row in source_rows if row["item_id"] == item_id
        )
    codebook = judge.load_codebook()
    allowed = {name: set(codebook[name]["values"]) for name in judge.CRITERIA}
    prompt_checks, prompt_errors = audit_prompt_structure(source_rows, codebook)
    structural_errors.extend(prompt_errors)

    comparator_summaries: list[dict[str, Any]] = []
    comparator_rows: dict[str, dict[tuple[str, str], dict[str, str]]] = {}
    for spec in COMPARATORS:
        summary, rows, errors = audit_comparator(spec, source_keys, allowed)
        comparator_summaries.append(summary)
        comparator_rows[spec["path"]] = rows
        structural_errors.extend(errors)

    definition = json.loads(SENTINEL_PATH.read_text(encoding="utf-8"))
    definition_errors = validate_sentinel_definition(
        definition, source_models_by_item, allowed
    )
    definition_valid = not definition_errors
    structural_errors.extend(
        f"visible-rule sentinel definition: {error}" for error in definition_errors
    )

    return {
        "audit_version": 1,
        "study": "A",
        "condition": {
            "prompt_variant": PROMPT_VARIANT,
            "role_separated": True,
            "scaffold": "outcome_only",
            "human_full_role_scaffold_matched": False,
            "description": (
                "Each comparator sees the visible prompt and response in separate role passes, "
                "but only the three compared outcome criteria; it does not receive the human "
                "panel's identification-first field inventory."
            ),
            "criteria_by_role": EXPECTED_CRITERIA_BY_ROLE,
            "forbidden_metadata_fields": FORBIDDEN_METADATA_FIELDS,
        },
        "inputs": {
            "audit_script": {
                "path": "scripts/audit_study_a_judge_condition.py",
                "sha256": sha256_file(Path(__file__).resolve()),
            },
            "runner": {
                "path": "scripts/run_study_a_judge.py",
                "sha256": sha256_file(Path(judge.__file__).resolve()),
            },
            "schema": {
                "path": "benchmark/study-a/schema.json",
                "sha256": sha256_file(judge.SCHEMA_PATH),
            },
            "source_outputs": {
                "path": str(OUTPUTS_PATH.relative_to(ROOT)),
                "sha256": sha256_file(OUTPUTS_PATH),
                "row_count": len(source_rows),
                "unique_key_count": len(source_keys),
            },
            "visible_rule_sentinels": {
                "path": str(SENTINEL_PATH.relative_to(ROOT)),
                "sha256": sha256_file(SENTINEL_PATH),
                "definition_valid": definition_valid,
            },
        },
        "structural_audit": {
            "status": "pass" if not structural_errors else "fail",
            "comparator_usable_on_structure": not structural_errors,
            "visible_rule_mismatches_affect_status": False,
            "prompt_checks": prompt_checks,
            "comparators": comparator_summaries,
            "errors": structural_errors,
        },
        "visible_rule_diagnostics": sentinel_diagnostics(
            definition, source_models_by_item, comparator_rows
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--print", dest="print_output", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--verify-output", action="store_true")
    parser.add_argument("--output", type=Path, default=AUDIT_PATH)
    args = parser.parse_args()

    payload = build_audit()
    rendered = canonical_json(payload)
    if args.print_output:
        print(rendered, end="")
        return
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.output}")
        raise SystemExit(0 if payload["structural_audit"]["status"] == "pass" else 1)
    if not args.output.exists():
        print(f"judge audit output is missing: {args.output}")
        raise SystemExit(1)
    if args.output.read_text(encoding="utf-8") != rendered:
        print(f"judge audit output is stale or changed: {args.output}")
        raise SystemExit(1)
    if payload["structural_audit"]["status"] != "pass":
        print("judge condition structural audit failed")
        raise SystemExit(1)
    diagnostics = payload["visible_rule_diagnostics"]
    print(
        "OK: judge condition is structurally valid; "
        f"visible-rule diagnostics report {diagnostics['mismatch_count']}/"
        f"{diagnostics['check_count']} mismatches (diagnostic only)."
    )


if __name__ == "__main__":
    main()
