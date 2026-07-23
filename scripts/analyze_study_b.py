#!/usr/bin/env python3
"""Analyze Study B records without collapsing joint outcomes or eligibility gates.

The committed input contains no target observations and therefore returns
``NOT_ESTIMATED``. Synthetic records exercise calculations only and are always
marked non-evidential. A production record is rejected unless one frozen
manifest binds the claim, items, lineage, reference review, pair schedule,
counterbalance, shortcut variants, configuration, analysis policy, and exact
repeat sets to verified local hashes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import NormalDist, stdev
from typing import Any, Iterable

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # pragma: no cover - incomplete environment only
    Draft202012Validator = None  # type: ignore[assignment]
    FormatChecker = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = ROOT / "benchmark" / "study-b" / "production-results.no-target-data.json"
DEFAULT_SCHEMA = ROOT / "benchmark" / "study-b" / "production-results.schema.json"
DEFAULT_SHORTCUTS = ROOT / "benchmark" / "study-b" / "shortcut-probe-manifest.csv"

CONDITIONS = (
    "C0_baseline",
    "C1_control_change",
    "N0_inert_load",
    "N1_matched_placebo",
)
SHORTCUT_ARMS = ("baseline", "manipulated")
EXPECTED_PROBE_IDS = {
    "APB-SP-LEX",
    "APB-SP-POS",
    "APB-SP-FMT",
    "APB-SP-SRC",
    "APB-SP-LEN",
    "APB-SP-OUT",
    "APB-SP-MARK-RM",
    "APB-SP-MARK-REV",
}
REQUIRED_PRODUCTION_ARTIFACTS = {
    "claim_register",
    "target_items",
    "lineage_manifest",
    "reference_review_manifest",
    "pair_manifest",
    "counterbalance_manifest",
    "shortcut_probe_manifest",
    "shortcut_variant_manifest",
    "configuration_manifest",
    "analysis_policy_manifest",
}
PLACEHOLDERS = {"NOT_ASSIGNED", "NOT_APPLICABLE", "TBD", "UNKNOWN", "UNSET"}


class StudyBAnalysisError(ValueError):
    """Raised when a record cannot support the declared analysis."""


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def schema_errors(payload: Any, schema: Any) -> list[str]:
    if Draft202012Validator is None or FormatChecker is None:
        return ["jsonschema is required to validate Study B production results"]
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path)):
        location = "$"
        for part in error.absolute_path:
            location += f"[{part}]" if isinstance(part, int) else f".{part}"
        errors.append(f"{location}: {error.message}")
    return errors


def load_shortcut_policy(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    policy: dict[str, dict[str, Any]] = {}
    for row in rows:
        probe_id = row.get("probe_id", "")
        if not probe_id or probe_id in policy:
            raise StudyBAnalysisError("shortcut manifest has a blank or duplicate probe_id")
        if row.get("production_gate") != "blocking":
            raise StudyBAnalysisError(f"{probe_id}: shortcut probe is not blocking")
        if row.get("minimum_cases") != "all_target_bases":
            raise StudyBAnalysisError(f"{probe_id}: shortcut probe does not cover all target bases")
        if row.get("reference_relation") != "preserves":
            raise StudyBAnalysisError(f"{probe_id}: shortcut probe does not preserve the reference relation")
        try:
            interval_level = float(row["interval_level"])
            maximum = float(row["max_allowed_shift"])
        except (KeyError, ValueError) as error:
            raise StudyBAnalysisError(f"{probe_id}: invalid shortcut threshold") from error
        if interval_level != 0.95 or not 0 < maximum <= 0.10:
            raise StudyBAnalysisError(f"{probe_id}: unsupported shortcut threshold")
        metric = row.get("metric", "").lower()
        policy[probe_id] = {
            "maximum": maximum,
            "target": "reference_concordant" if "reference-concordant" in metric else "later_main",
        }
    if set(policy) != EXPECTED_PROBE_IDS:
        raise StudyBAnalysisError(
            "shortcut manifest inventory mismatch: "
            f"missing={sorted(EXPECTED_PROBE_IDS - set(policy))!r} "
            f"extra={sorted(set(policy) - EXPECTED_PROBE_IDS)!r}"
        )
    return policy


def duplicate_values(values: Iterable[str]) -> set[str]:
    counts = Counter(values)
    return {value for value, count in counts.items() if count > 1}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return f"sha256:{digest.hexdigest()}"


def bound_path(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute():
        raise StudyBAnalysisError(f"production binding path must be relative: {relative!r}")
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise StudyBAnalysisError(f"production binding escapes its root: {relative!r}")
    if not resolved.is_file():
        raise StudyBAnalysisError(f"production binding file does not exist: {relative!r}")
    return resolved


def verify_hash(path: Path, expected: str, label: str) -> None:
    observed = sha256_path(path)
    if observed != expected:
        raise StudyBAnalysisError(
            f"{label} hash mismatch: expected {expected!r}, observed {observed!r}"
        )


def has_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        normalized = value.strip().upper()
        return normalized in PLACEHOLDERS or "SYNTHETIC" in normalized
    if isinstance(value, dict):
        return any(has_placeholder(item) for item in value.values())
    if isinstance(value, list):
        return any(has_placeholder(item) for item in value)
    return False


def canonical_records(rows: Iterable[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: row[key])


def verify_bound_object_contracts(
    payload: dict[str, Any],
    artifact_paths: dict[str, Path],
    shortcut_policy: dict[str, dict[str, Any]],
) -> None:
    """Check the production objects whose internal identifiers drive scoring."""

    target_document = load_json(artifact_paths["target_items"])
    if not isinstance(target_document, dict) or set(target_document) != {"schema_version", "items"}:
        raise StudyBAnalysisError("NOT_ELIGIBLE: target-items object has the wrong contract")
    if target_document["schema_version"] != "1.0" or not isinstance(
        target_document["items"], list
    ):
        raise StudyBAnalysisError("NOT_ELIGIBLE: target-items object is malformed")
    expected_items: list[dict[str, str]] = []
    for base in payload["target_bases"]:
        expected_items.extend(
            {
                "item_id": base["condition_item_ids"][condition],
                "item_hash": base["condition_item_hashes"][condition],
            }
            for condition in CONDITIONS
        )
        expected_items.extend(
            {
                "item_id": variant[arm]["item_id"],
                "item_hash": variant[arm]["item_hash"],
            }
            for variant in base["shortcut_variants"]
            for arm in SHORTCUT_ARMS
        )
    observed_items = target_document["items"]
    if any(
        not isinstance(row, dict) or set(row) != {"item_id", "item_hash"}
        for row in observed_items
    ):
        raise StudyBAnalysisError("NOT_ELIGIBLE: target-items entries are malformed")
    if canonical_records(observed_items, "item_id") != canonical_records(
        expected_items, "item_id"
    ):
        raise StudyBAnalysisError(
            "NOT_ELIGIBLE: result item IDs or hashes do not match the frozen target-items object"
        )

    expected_lineage = canonical_records(
        [
            {
                "base_id": base["base_id"],
                "base_hash": base["base_hash"],
                "production_eligible": True,
                "output_inspected": False,
                "freeze_status": "frozen_before_outcomes",
            }
            for base in payload["target_bases"]
        ],
        "base_id",
    )
    lineage = load_json(artifact_paths["lineage_manifest"])
    if lineage != {"schema_version": "1.0", "bases": expected_lineage}:
        raise StudyBAnalysisError(
            "NOT_ELIGIBLE: lineage object does not bind every frozen output-uninspected base"
        )

    expected_reviews = canonical_records(
        [
            {
                "base_id": base["base_id"],
                "reviewed_base_hash": base["base_hash"],
                "status": "passed_before_outcomes",
            }
            for base in payload["target_bases"]
        ],
        "base_id",
    )
    reviews = load_json(artifact_paths["reference_review_manifest"])
    if reviews != {"schema_version": "1.0", "bases": expected_reviews}:
        raise StudyBAnalysisError(
            "NOT_ELIGIBLE: reference-review object does not pass and bind every base"
        )

    expected_variants = canonical_records(
        [
            {
                "base_id": base["base_id"],
                "shortcut_variants": base["shortcut_variants"],
            }
            for base in payload["target_bases"]
        ],
        "base_id",
    )
    variants = load_json(artifact_paths["shortcut_variant_manifest"])
    if variants != {"schema_version": "1.0", "bases": expected_variants}:
        raise StudyBAnalysisError(
            "NOT_ELIGIBLE: shortcut-variant object does not bind arm-specific items and references"
        )

    configuration = load_json(artifact_paths["configuration_manifest"])
    if configuration != {
        "schema_version": "1.0",
        "configuration": payload["configuration"],
    }:
        raise StudyBAnalysisError(
            "NOT_ELIGIBLE: configuration object differs from the result configuration"
        )
    policy = load_json(artifact_paths["analysis_policy_manifest"])
    if policy != {"schema_version": "1.0", "analysis_policy": payload["analysis_policy"]}:
        raise StudyBAnalysisError(
            "NOT_ELIGIBLE: analysis-policy object differs from the result policy"
        )

    claim_document = load_json(artifact_paths["claim_register"])
    claims = claim_document.get("claims", []) if isinstance(claim_document, dict) else []
    matching_claims = [
        claim
        for claim in claims
        if claim.get("claim_id") == "APB_BEH_001" and claim.get("claim_version") == "1.1"
    ]
    if len(matching_claims) != 1:
        raise StudyBAnalysisError(
            "NOT_ELIGIBLE: claim-register object lacks exactly one APB_BEH_001 version 1.1"
        )
    if load_shortcut_policy(artifact_paths["shortcut_probe_manifest"]) != shortcut_policy:
        raise StudyBAnalysisError(
            "NOT_ELIGIBLE: bound shortcut policy differs from the analysis shortcut policy"
        )


def verify_production_binding(
    payload: dict[str, Any],
    binding_root: Path,
    shortcut_policy: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Verify the frozen production manifest and every object it binds."""

    binding = payload.get("production_binding")
    if not isinstance(binding, dict):
        raise StudyBAnalysisError("NOT_ELIGIBLE: production_target lacks a production binding")
    manifest_path = bound_path(binding_root, binding["manifest_path"])
    verify_hash(manifest_path, binding["manifest_sha256"], "production manifest")
    manifest = load_json(manifest_path)
    required_top = {
        "schema_version",
        "eligibility_status",
        "freeze_status",
        "reference_review_status",
        "claim_id",
        "claim_version",
        "artifacts",
        "configuration",
        "analysis_policy",
        "repeat_plan",
        "declared_cells",
        "target_bases",
    }
    if not isinstance(manifest, dict) or set(manifest) != required_top:
        raise StudyBAnalysisError("NOT_ELIGIBLE: production manifest has the wrong field inventory")
    required_values = {
        "schema_version": "1.0",
        "eligibility_status": "eligible_before_outcomes",
        "freeze_status": "frozen_before_outcomes",
        "reference_review_status": "passed_before_outcomes",
        "claim_id": "APB_BEH_001",
        "claim_version": "1.1",
    }
    for field, expected in required_values.items():
        if manifest.get(field) != expected:
            raise StudyBAnalysisError(
                f"NOT_ELIGIBLE: production manifest {field} must equal {expected!r}"
            )

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != REQUIRED_PRODUCTION_ARTIFACTS:
        raise StudyBAnalysisError(
            "NOT_ELIGIBLE: production manifest artifact inventory mismatch"
        )
    observed_paths: set[Path] = set()
    artifact_paths: dict[str, Path] = {}
    for name in sorted(REQUIRED_PRODUCTION_ARTIFACTS):
        record = artifacts[name]
        if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
            raise StudyBAnalysisError(f"NOT_ELIGIBLE: malformed {name} artifact binding")
        path = bound_path(binding_root, record["path"])
        if path in observed_paths:
            raise StudyBAnalysisError(f"NOT_ELIGIBLE: artifact path is reused for {name}")
        observed_paths.add(path)
        artifact_paths[name] = path
        verify_hash(path, record["sha256"], name)

    for field in (
        "configuration",
        "analysis_policy",
        "repeat_plan",
        "declared_cells",
        "target_bases",
    ):
        if manifest[field] != payload[field]:
            raise StudyBAnalysisError(
                f"NOT_ELIGIBLE: result {field} is not identical to its frozen manifest object"
            )
    if has_placeholder(payload["configuration"]):
        raise StudyBAnalysisError("NOT_ELIGIBLE: production configuration contains a placeholder")
    verify_bound_object_contracts(payload, artifact_paths, shortcut_policy)
    return manifest


def shortcut_variant_index(base: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["probe_id"]: row for row in base["shortcut_variants"]}


def repeat_plan_index(payload: dict[str, Any]) -> dict[str, set[str]]:
    return {
        row["probe_id"]: set(row["repeat_ids"])
        for row in payload["repeat_plan"]["shortcut_repeat_sets"]
    }


def structural_errors(
    payload: dict[str, Any], shortcut_policy: dict[str, dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    if payload["data_kind"] == "no_target_data":
        return errors

    cells = payload["declared_cells"]
    bases = payload["target_bases"]
    observations = payload["observations"]
    shortcut_observations = payload["shortcut_observations"]

    duplicate_cells = duplicate_values(row["cell_id"] for row in cells)
    duplicate_cell_meanings = duplicate_values(
        f"{row['phenomenon_family']}\x1f{row['application_surface']}" for row in cells
    )
    duplicate_bases = duplicate_values(row["base_id"] for row in bases)
    duplicate_observations = duplicate_values(
        row["observation_id"] for row in [*observations, *shortcut_observations]
    )
    if duplicate_cells:
        errors.append(f"duplicate cell_id values: {sorted(duplicate_cells)!r}")
    if duplicate_cell_meanings:
        errors.append("duplicate phenomenon-family by application-surface cells")
    if duplicate_bases:
        errors.append(f"duplicate base_id values: {sorted(duplicate_bases)!r}")
    if duplicate_observations:
        errors.append(f"duplicate observation_id values: {sorted(duplicate_observations)!r}")

    standard_repeat_list = payload["repeat_plan"]["standard_repeat_ids"]
    standard_expected = set(standard_repeat_list)
    if len(standard_expected) != len(standard_repeat_list) or not standard_expected:
        errors.append("repeat plan needs a nonempty unique standard repeat set")
    shortcut_repeat_rows = payload["repeat_plan"]["shortcut_repeat_sets"]
    duplicate_repeat_probes = duplicate_values(row["probe_id"] for row in shortcut_repeat_rows)
    if duplicate_repeat_probes:
        errors.append(f"repeat plan duplicates shortcut probes: {sorted(duplicate_repeat_probes)!r}")
    shortcut_expected = repeat_plan_index(payload)
    if set(shortcut_expected) != set(shortcut_policy):
        errors.append("repeat plan must cover every blocking shortcut probe exactly once")
    for probe_id, values in shortcut_expected.items():
        source = next(
            (row["repeat_ids"] for row in shortcut_repeat_rows if row["probe_id"] == probe_id),
            [],
        )
        if len(values) != len(source) or not values:
            errors.append(f"{probe_id}: shortcut repeat set must be nonempty and unique")

    cell_index = {row["cell_id"]: row for row in cells}
    base_index = {row["base_id"]: row for row in bases}
    all_standard_item_ids: list[str] = []
    all_shortcut_item_ids: list[str] = []
    for base in bases:
        base_id = base["base_id"]
        if base["cell_id"] not in cell_index:
            errors.append(f"{base_id}: unknown cell_id {base['cell_id']!r}")
        references = base["condition_reference_main_tokens"]
        control_references = base["condition_reference_control_tokens"]
        later = base["later_main_token"]
        later_control = base["later_control_token"]
        for condition in ("C0_baseline", "N0_inert_load", "N1_matched_placebo"):
            if references[condition] != later:
                errors.append(f"{base_id}: {condition} reference must equal later_main_token")
        if references["C1_control_change"] == later:
            errors.append(f"{base_id}: C1 reference must differ from later_main_token")
        for condition in CONDITIONS:
            if control_references[condition] != later_control:
                errors.append(f"{base_id}: {condition} control reference must remain fixed")
        item_ids = list(base["condition_item_ids"].values())
        all_standard_item_ids.extend(item_ids)
        if len(set(item_ids)) != len(CONDITIONS):
            errors.append(f"{base_id}: all four standard condition item_ids must be distinct")

        variants = base["shortcut_variants"]
        variant_ids = [row["probe_id"] for row in variants]
        if len(set(variant_ids)) != len(variant_ids) or set(variant_ids) != set(shortcut_policy):
            errors.append(f"{base_id}: shortcut variants must cover every probe exactly once")
        for variant in variants:
            if variant["baseline"]["item_id"] == variant["manipulated"]["item_id"]:
                errors.append(f"{base_id}/{variant['probe_id']}: shortcut arm item_ids must differ")
            all_shortcut_item_ids.extend(
                [variant["baseline"]["item_id"], variant["manipulated"]["item_id"]]
            )
    duplicate_standard_items = duplicate_values(all_standard_item_ids)
    duplicate_shortcut_items = duplicate_values(all_shortcut_item_ids)
    if duplicate_standard_items:
        errors.append(f"standard item_ids are reused: {sorted(duplicate_standard_items)!r}")
    if duplicate_shortcut_items:
        errors.append(f"shortcut variant item_ids are reused: {sorted(duplicate_shortcut_items)!r}")

    standard_keys: set[tuple[str, str, str]] = set()
    repeats: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in observations:
        base = base_index.get(row["base_id"])
        if base is None:
            errors.append(f"{row['observation_id']}: unknown base_id {row['base_id']!r}")
            continue
        condition = row["condition"]
        if row["item_id"] != base["condition_item_ids"][condition]:
            errors.append(f"{row['observation_id']}: item_id does not match its base and condition")
        key = (row["base_id"], condition, row["repeat_id"])
        if key in standard_keys:
            errors.append(f"duplicate standard observation key {key!r}")
        standard_keys.add(key)
        repeats[(row["base_id"], condition)].add(row["repeat_id"])
    for base_id in base_index:
        for condition in CONDITIONS:
            observed = repeats.get((base_id, condition), set())
            if observed != standard_expected:
                errors.append(
                    f"{base_id}/{condition}: standard repeats differ from the frozen set; "
                    f"missing={sorted(standard_expected - observed)!r} "
                    f"extra={sorted(observed - standard_expected)!r}"
                )

    shortcut_keys: set[tuple[str, str, str, str]] = set()
    shortcut_repeats: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in shortcut_observations:
        base = base_index.get(row["base_id"])
        if base is None:
            errors.append(f"{row['observation_id']}: unknown shortcut base_id {row['base_id']!r}")
            continue
        probe_id = row["probe_id"]
        if probe_id not in shortcut_policy:
            errors.append(f"{row['observation_id']}: unknown probe_id {probe_id!r}")
            continue
        variant = shortcut_variant_index(base).get(probe_id)
        if variant is None:
            errors.append(f"{row['observation_id']}: base lacks shortcut variant {probe_id!r}")
            continue
        arm = row["probe_arm"]
        if row["condition"] != variant["condition"]:
            errors.append(f"{row['observation_id']}: shortcut condition conflicts with frozen variant")
        if row["item_id"] != variant[arm]["item_id"]:
            errors.append(f"{row['observation_id']}: shortcut item_id conflicts with frozen variant")
        key = (row["base_id"], probe_id, arm, row["repeat_id"])
        if key in shortcut_keys:
            errors.append(f"duplicate shortcut observation key {key!r}")
        shortcut_keys.add(key)
        shortcut_repeats[(row["base_id"], probe_id, arm)].add(row["repeat_id"])
    for base_id in base_index:
        for probe_id in shortcut_policy:
            expected = shortcut_expected.get(probe_id, set())
            for arm in SHORTCUT_ARMS:
                observed = shortcut_repeats.get((base_id, probe_id, arm), set())
                if observed != expected:
                    errors.append(
                        f"{base_id}/{probe_id}/{arm}: shortcut repeats differ from the frozen set; "
                        f"missing={sorted(expected - observed)!r} extra={sorted(observed - expected)!r}"
                    )
    return errors


def channel_key(channel: dict[str, Any]) -> str:
    return f"token:{channel['value']}" if channel["kind"] == "token" else channel["kind"]


def joint_key(outcome: dict[str, Any]) -> str:
    return f"main={channel_key(outcome['main'])}|control={channel_key(outcome['control'])}"


def token_hit(channel: dict[str, Any], token: str) -> int:
    return int(channel["kind"] == "token" and channel.get("value") == token)


def joint_evaluable(outcome: dict[str, Any]) -> int:
    return int(outcome["main"]["kind"] == "token" and outcome["control"]["kind"] == "token")


def wilson_interval(successes: int, total: int, z: float) -> tuple[float, float]:
    if total <= 0:
        raise StudyBAnalysisError("cannot estimate a binomial interval with no observations")
    proportion = successes / total
    z2 = z * z
    denominator = 1 + z2 / total
    centre = (proportion + z2 / (2 * total)) / denominator
    radius = z * math.sqrt(
        proportion * (1 - proportion) / total + z2 / (4 * total * total)
    ) / denominator
    return max(0.0, centre - radius), min(1.0, centre + radius)


def simultaneous_z(interval_level: float, comparisons: int) -> float:
    alpha = 1 - interval_level
    return NormalDist().inv_cdf(1 - alpha / (2 * max(1, comparisons)))


def probability_record(values: list[int], z: float) -> dict[str, Any]:
    successes = sum(values)
    lower, upper = wilson_interval(successes, len(values), z)
    return {
        "successes": successes,
        "total": len(values),
        "estimate": successes / len(values),
        "simultaneous_interval": [lower, upper],
    }


def evaluability_screen(record: dict[str, Any], point: float, lower: float) -> str:
    """Data-quality screen, not an effect gate. It checks that an arm actually
    produced its expected reference behaviour, so an arm made of refusals or
    failed calls can't be read as reference-concordant. It says nothing about the
    size of any authority effect; effects are reported as estimands below."""
    return (
        "PASS"
        if record["estimate"] >= point and record["simultaneous_interval"][0] >= lower
        else "FAIL"
    )


# Two-sided 95% Student-t critical values. A design analysis (delegation-assurance
# companion) shows the normal interval undercovers small clusters, so cluster
# estimands use a t interval.
_T_QUANTILE_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145,
    15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
}


def t_quantile_95(df: int) -> float:
    if df <= 0:
        return float("inf")
    return _T_QUANTILE_95.get(df, NormalDist().inv_cdf(0.975))


def floor_position(lower: float, upper: float, floor: float) -> str:
    """Where a reported interval sits relative to a design floor. This is
    descriptive context, never a licensing gate: no verdict is conditioned on it.
    The accept/revise decision is tied to declared losses, not to whether the
    interval clears the floor."""
    if lower > floor:
        return "interval_above_floor"
    if upper < floor:
        return "interval_below_floor"
    return "interval_spans_floor"


def cluster_estimand(values: list[float], floor: float) -> dict[str, Any]:
    """Family-level selective-margin estimand: the mean base effect with a
    between-base t interval. This replaces the one-sided lower-bound gate the
    design analysis flags as a Type-M filter (the effects it passes are, on
    average, inflated)."""
    n = len(values)
    mean = sum(values) / n
    se = stdev(values) / math.sqrt(n) if n > 1 else float("inf")
    half = t_quantile_95(n - 1) * se if se != float("inf") else float("inf")
    lower, upper = mean - half, mean + half
    return {
        "estimator": "mean base effect with a between-base t interval",
        "point_estimate": mean,
        "standard_error": se,
        "cluster_interval": [lower, upper],
        "n_bases": n,
        "design_floor": floor,
        "floor_position": floor_position(lower, upper, floor),
    }


def dersimonian_laird(
    estimates: list[float], variances: list[float], floor: float
) -> dict[str, Any]:
    """Random-effects pooling across families (partial pooling): families share a
    mean but vary, and the pooled interval carries both within- and estimated
    between-family variance. Supplies the multiplicity control that separate
    per-cell tests lacked."""
    k = len(estimates)
    if k == 0:
        return {"point_estimate": None, "pooled_interval": [None, None], "n_families": 0}
    finite = [v for v in variances if v not in (float("inf"), 0.0)]
    if not finite:
        return {
            "estimator": "families report point estimates but no finite variance",
            "point_estimate": sum(estimates) / k,
            "pooled_interval": [None, None],
            "n_families": k,
            "design_floor": floor,
        }
    fixed_w = [1.0 / v if v not in (float("inf"), 0.0) else 0.0 for v in variances]
    total_w = sum(fixed_w)
    mean_fixed = sum(w * e for w, e in zip(fixed_w, estimates)) / total_w
    q = sum(w * (e - mean_fixed) ** 2 for w, e in zip(fixed_w, estimates))
    c = total_w - sum(w * w for w in fixed_w) / total_w
    tau2 = max(0.0, (q - (k - 1)) / c) if c > 0 else 0.0
    re_w = [1.0 / (v + tau2) if (v + tau2) > 0 else 0.0 for v in variances]
    mean_re = sum(w * e for w, e in zip(re_w, estimates)) / sum(re_w)
    se_re = math.sqrt(1.0 / sum(re_w))
    z = NormalDist().inv_cdf(0.975)
    lower, upper = mean_re - z * se_re, mean_re + z * se_re
    return {
        "estimator": "DerSimonian-Laird random-effects pooling across families",
        "point_estimate": mean_re,
        "pooled_interval": [lower, upper],
        "between_family_variance_tau2": tau2,
        "n_families": k,
        "design_floor": floor,
        "floor_position": floor_position(lower, upper, floor),
    }


def empirical_distribution(rows: list[dict[str, Any]], level: str) -> dict[str, float]:
    if level == "joint":
        keys = [joint_key(row["joint_outcome"]) for row in rows]
    elif level in {"main", "control"}:
        keys = [channel_key(row["joint_outcome"][level]) for row in rows]
    else:  # pragma: no cover - internal programming error
        raise StudyBAnalysisError(f"unknown distribution level {level!r}")
    counts = Counter(keys)
    return {key: count / len(rows) for key, count in sorted(counts.items())}


def raw_outcome_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total": len(rows),
        "joint_counts": dict(sorted(Counter(joint_key(row["joint_outcome"]) for row in rows).items())),
        "main_marginal_counts": dict(
            sorted(Counter(channel_key(row["joint_outcome"]["main"]) for row in rows).items())
        ),
        "control_marginal_counts": dict(
            sorted(Counter(channel_key(row["joint_outcome"]["control"]) for row in rows).items())
        ),
    }


def distribution_difference(
    left_rows: list[dict[str, Any]], right_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for level in ("joint", "main", "control"):
        left = empirical_distribution(left_rows, level)
        right = empirical_distribution(right_rows, level)
        keys = sorted(set(left) | set(right))
        shifts = {key: left.get(key, 0.0) - right.get(key, 0.0) for key in keys}
        result[f"{level}_signed_probability_shifts"] = shifts
        result[f"{level}_total_variation"] = 0.5 * sum(abs(value) for value in shifts.values())
    return result


def absolute_difference_upper(left: dict[str, Any], right: dict[str, Any]) -> float:
    left_lower, left_upper = left["simultaneous_interval"]
    right_lower, right_upper = right["simultaneous_interval"]
    return max(abs(left_lower - right_upper), abs(left_upper - right_lower))


def analyze_payload(
    payload: dict[str, Any],
    shortcut_policy: dict[str, dict[str, Any]],
    *,
    binding_root: Path = ROOT,
) -> dict[str, Any]:
    if payload["data_kind"] == "no_target_data":
        return {
            "dataset_id": payload["dataset_id"],
            "analysis_status": "NOT_ESTIMATED",
            "evidence_status": "NO_TARGET_EVIDENCE",
            "production_eligibility": "NOT_APPLICABLE",
            "reason": "No Study B target observations have been collected.",
            "raw_joint_outcomes": [],
            "cell_results": [],
            "scope_gate": "NOT_ESTIMATED",
            "behavioural_claim": {"status": "NOT_ESTIMATED"},
        }

    if payload["data_kind"] == "production_target":
        verify_production_binding(payload, binding_root, shortcut_policy)

    errors = structural_errors(payload, shortcut_policy)
    if errors:
        raise StudyBAnalysisError("; ".join(errors))

    cells = {row["cell_id"]: row for row in payload["declared_cells"]}
    bases = {row["base_id"]: row for row in payload["target_bases"]}
    observations_by_base_condition: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in payload["observations"]:
        observations_by_base_condition[(row["base_id"], row["condition"])].append(row)

    shortcut_groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in payload["shortcut_observations"]:
        cell_id = bases[row["base_id"]]["cell_id"]
        shortcut_groups[(cell_id, row["base_id"], row["probe_id"], row["probe_arm"])].append(row)

    # Four standard binomial summaries per base and arm: later-main, main-reference,
    # control-reference, and joint correctness. Cell-arm control adds four per cell.
    # Every shortcut base/probe/arm adds main-reference, control-reference, and
    # evaluability. Derived D_b and equivalence bounds use these simultaneous CIs.
    comparison_count = len(bases) * len(CONDITIONS) * 4
    comparison_count += len(cells) * len(CONDITIONS)
    comparison_count += len(bases) * len(shortcut_policy) * len(SHORTCUT_ARMS) * 3
    interval_level = payload["analysis_policy"]["interval_level"]
    z = simultaneous_z(interval_level, comparison_count)
    # A design floor, not an acceptance threshold: the smallest authority effect
    # worth acting on. Reported estimands are placed relative to it descriptively.
    design_floor = payload["analysis_policy"]["per_base_margin_lower_bound"]

    base_results: dict[str, dict[str, Any]] = {}
    raw_joint_outcomes: list[dict[str, Any]] = []
    for base_id, base in sorted(bases.items()):
        later_probabilities: dict[str, dict[str, Any]] = {}
        main_reference_probabilities: dict[str, dict[str, Any]] = {}
        control_probabilities: dict[str, dict[str, Any]] = {}
        correctness_probabilities: dict[str, dict[str, Any]] = {}
        raw_by_condition: dict[str, dict[str, Any]] = {}
        for condition in CONDITIONS:
            rows = observations_by_base_condition[(base_id, condition)]
            later_probabilities[condition] = probability_record(
                [token_hit(row["joint_outcome"]["main"], base["later_main_token"]) for row in rows],
                z,
            )
            reference_main = base["condition_reference_main_tokens"][condition]
            reference_control = base["condition_reference_control_tokens"][condition]
            main_record = probability_record(
                [token_hit(row["joint_outcome"]["main"], reference_main) for row in rows], z
            )
            main_record["reference_token"] = reference_main
            main_record["gate"] = evaluability_screen(
                main_record,
                payload["analysis_policy"]["main_reference_point_minimum"],
                payload["analysis_policy"]["main_reference_lower_bound_minimum"],
            )
            main_reference_probabilities[condition] = main_record

            control_record = probability_record(
                [token_hit(row["joint_outcome"]["control"], reference_control) for row in rows], z
            )
            control_record["reference_token"] = reference_control
            control_probabilities[condition] = control_record

            joint_record = probability_record(
                [
                    int(
                        token_hit(row["joint_outcome"]["main"], reference_main)
                        and token_hit(row["joint_outcome"]["control"], reference_control)
                    )
                    for row in rows
                ],
                z,
            )
            joint_record["reference_main_token"] = reference_main
            joint_record["reference_control_token"] = reference_control
            correctness_probabilities[condition] = joint_record
            raw_record = raw_outcome_counts(rows)
            raw_by_condition[condition] = raw_record
            raw_joint_outcomes.append(
                {
                    "base_id": base_id,
                    "cell_id": base["cell_id"],
                    "condition": condition,
                    **raw_record,
                }
            )

        c0 = later_probabilities["C0_baseline"]
        c1 = later_probabilities["C1_control_change"]
        n0 = later_probabilities["N0_inert_load"]
        n1 = later_probabilities["N1_matched_placebo"]
        reference_shift = c0["estimate"] - c1["estimate"]
        nuisance_shift = c0["estimate"] - n0["estimate"]
        placebo_shift = c0["estimate"] - n1["estimate"]
        # Subtract the MEAN of the two absolute nuisance shifts, not the larger:
        # the maximum of noisy nonnegative quantities is biased upward and
        # over-subtracts (design analysis, delegation-assurance companion).
        mean_nuisance = (abs(nuisance_shift) + abs(placebo_shift)) / 2
        margin = reference_shift - mean_nuisance
        reference_lower = c0["simultaneous_interval"][0] - c1["simultaneous_interval"][1]
        reference_upper = c0["simultaneous_interval"][1] - c1["simultaneous_interval"][0]
        mean_nuisance_upper = (
            absolute_difference_upper(c0, n0) + absolute_difference_upper(c0, n1)
        ) / 2
        margin_lower = reference_lower - mean_nuisance_upper
        margin_upper = reference_upper + mean_nuisance_upper
        # base_gate is now a DATA-EVALUABILITY verdict (did the arms produce
        # interpretable reference behaviour). The selective margin itself is
        # reported as an estimand with an interval and a design floor, never gated:
        # a one-sided lower-bound gate is a Type-M filter (design analysis).
        main_gate = (
            "PASS"
            if all(record["gate"] == "PASS" for record in main_reference_probabilities.values())
            else "FAIL"
        )
        base_gate = main_gate
        noncontrolling = {
            "C0_minus_N0": distribution_difference(
                observations_by_base_condition[(base_id, "C0_baseline")],
                observations_by_base_condition[(base_id, "N0_inert_load")],
            ),
            "C0_minus_N1": distribution_difference(
                observations_by_base_condition[(base_id, "C0_baseline")],
                observations_by_base_condition[(base_id, "N1_matched_placebo")],
            ),
        }
        matched_operativity = distribution_difference(
            observations_by_base_condition[(base_id, "C1_control_change")],
            observations_by_base_condition[(base_id, "N1_matched_placebo")],
        )
        base_results[base_id] = {
            "base_id": base_id,
            "cell_id": base["cell_id"],
            "declared_tokens": {
                "later_main_token": base["later_main_token"],
                "later_control_token": base["later_control_token"],
                "condition_reference_main_tokens": base["condition_reference_main_tokens"],
                "condition_reference_control_tokens": base[
                    "condition_reference_control_tokens"
                ],
            },
            "primary_summaries": {
                "1_raw_joint_and_marginal_outcomes": raw_by_condition,
                "2_c0_minus_c1_later_main": {
                    "arm_probabilities": {
                        "C0_baseline": c0,
                        "C1_control_change": c1,
                    },
                    "signed_probability_shift": reference_shift,
                },
                "3_control_token_uptake_by_arm": control_probabilities,
                "4_condition_specific_joint_correctness_by_arm": correctness_probabilities,
                "5_noncontrolling_full_distribution_differences": noncontrolling,
                "6_matched_operativity_c1_minus_n1": matched_operativity,
            },
            "main_reference_gate": {
                "arms": main_reference_probabilities,
                "gate": main_gate,
            },
            "selective_margin": {
                "c0_minus_n0_later_main": nuisance_shift,
                "c0_minus_n1_later_main": placebo_shift,
                "nuisance_subtraction": "mean of the two absolute nuisance shifts",
                "point_estimate": margin,
                "simultaneous_interval": [margin_lower, margin_upper],
                "design_floor": design_floor,
                "floor_position": floor_position(margin_lower, margin_upper, design_floor),
            },
            "base_gate": base_gate,
        }

    cell_results: list[dict[str, Any]] = []
    for cell_id, cell in sorted(cells.items()):
        cell_base_ids = sorted(
            base_id for base_id, base in bases.items() if base["cell_id"] == cell_id
        )
        evaluable_bases = [
            base_id for base_id in cell_base_ids if base_results[base_id]["base_gate"] == "PASS"
        ]
        required_bases = payload["analysis_policy"]["required_bases_per_cell"]
        bases_present = len(cell_base_ids) == required_bases
        bases_evaluable = bases_present and len(evaluable_bases) == len(cell_base_ids)
        # Family-level selective-margin estimand with a between-base t interval,
        # replacing the three-of-four one-sided lower-bound conjunction (a Type-M
        # filter whose multiplicity the pooled estimand instead controls).
        family_margin = cluster_estimand(
            [base_results[base_id]["selective_margin"]["point_estimate"] for base_id in cell_base_ids],
            design_floor,
        )

        control_results: dict[str, dict[str, Any]] = {}
        for condition in CONDITIONS:
            rows = [
                row
                for base_id in cell_base_ids
                for row in observations_by_base_condition[(base_id, condition)]
            ]
            values = [
                token_hit(
                    row["joint_outcome"]["control"],
                    bases[row["base_id"]]["condition_reference_control_tokens"][condition],
                )
                for row in rows
            ]
            record = probability_record(values, z)
            record["gate"] = evaluability_screen(
                record,
                payload["analysis_policy"]["control_point_minimum"],
                payload["analysis_policy"]["control_lower_bound_minimum"],
            )
            control_results[condition] = record
        control_pass = all(record["gate"] == "PASS" for record in control_results.values())

        probe_results: dict[str, dict[str, Any]] = {}
        for probe_id, probe in sorted(shortcut_policy.items()):
            per_base: dict[str, dict[str, Any]] = {}
            for base_id in cell_base_ids:
                base = bases[base_id]
                variant = shortcut_variant_index(base)[probe_id]
                arms: dict[str, dict[str, Any]] = {}
                for arm in SHORTCUT_ARMS:
                    rows = shortcut_groups[(cell_id, base_id, probe_id, arm)]
                    arm_reference = variant[arm]
                    main_record = probability_record(
                        [
                            token_hit(
                                row["joint_outcome"]["main"],
                                arm_reference["reference_main_token"],
                            )
                            for row in rows
                        ],
                        z,
                    )
                    main_record["reference_token"] = arm_reference["reference_main_token"]
                    main_record["gate"] = evaluability_screen(
                        main_record,
                        payload["analysis_policy"]["main_reference_point_minimum"],
                        payload["analysis_policy"]["main_reference_lower_bound_minimum"],
                    )
                    control_record = probability_record(
                        [
                            token_hit(
                                row["joint_outcome"]["control"],
                                arm_reference["reference_control_token"],
                            )
                            for row in rows
                        ],
                        z,
                    )
                    control_record["reference_token"] = arm_reference[
                        "reference_control_token"
                    ]
                    control_record["gate"] = evaluability_screen(
                        control_record,
                        payload["analysis_policy"]["control_point_minimum"],
                        payload["analysis_policy"]["control_lower_bound_minimum"],
                    )
                    evaluable_record = probability_record(
                        [joint_evaluable(row["joint_outcome"]) for row in rows], z
                    )
                    evaluable_record["gate"] = evaluability_screen(
                        evaluable_record,
                        payload["analysis_policy"]["shortcut_evaluable_point_minimum"],
                        payload["analysis_policy"]["shortcut_evaluable_lower_bound_minimum"],
                    )
                    arms[arm] = {
                        "item_id": arm_reference["item_id"],
                        "item_hash": arm_reference["item_hash"],
                        "main_reference_correctness": main_record,
                        "control_reference_correctness": control_record,
                        "joint_evaluability": evaluable_record,
                        "raw_outcomes": raw_outcome_counts(rows),
                    }
                baseline = arms["baseline"]["main_reference_correctness"]
                manipulated = arms["manipulated"]["main_reference_correctness"]
                point_shift = abs(baseline["estimate"] - manipulated["estimate"])
                upper = absolute_difference_upper(baseline, manipulated)
                equivalence_pass = point_shift <= probe["maximum"] and upper <= probe["maximum"]
                arm_pass = all(
                    arm_record[key]["gate"] == "PASS"
                    for arm_record in arms.values()
                    for key in (
                        "main_reference_correctness",
                        "control_reference_correctness",
                        "joint_evaluability",
                    )
                )
                per_base[base_id] = {
                    "condition": variant["condition"],
                    "arms": arms,
                    "absolute_reference_concordance_shift": point_shift,
                    "simultaneous_absolute_shift_upper_bound": upper,
                    "maximum_allowed_shift": probe["maximum"],
                    "equivalence_gate": "PASS" if equivalence_pass else "FAIL",
                    "gate": "PASS" if equivalence_pass and arm_pass else "FAIL",
                }
            probe_pass = all(record["gate"] == "PASS" for record in per_base.values())
            probe_results[probe_id] = {
                "metric_target": probe["target"],
                "base_results": per_base,
                "gate": "PASS" if probe_pass else "FAIL",
            }
        shortcut_pass = all(record["gate"] == "PASS" for record in probe_results.values())
        # cell_gate is EVALUABILITY: are the bases, control arms, and shortcut
        # invariance interpretable? The authority effect is reported separately as
        # family_selective_margin, not gated.
        cell_evaluable = bases_evaluable and control_pass and shortcut_pass
        cell_results.append(
            {
                "cell_id": cell_id,
                "phenomenon_family": cell["phenomenon_family"],
                "application_surface": cell["application_surface"],
                "base_results": [base_results[base_id] for base_id in cell_base_ids],
                "family_selective_margin": family_margin,
                "base_evaluability": {
                    "observed_bases": len(cell_base_ids),
                    "required_bases": required_bases,
                    "evaluable_bases": evaluable_bases,
                    "all_bases_evaluable": bases_evaluable,
                    "definition": "every arm produced interpretable main-reference behaviour",
                },
                "control_token_gate": {
                    "arms": control_results,
                    "gate": "PASS" if control_pass else "FAIL",
                },
                "shortcut_probe_gate": {
                    "probes": probe_results,
                    "noncompensation_rule": "every base passes every probe",
                    "gate": "PASS" if shortcut_pass else "FAIL",
                },
                "cell_gate": "PASS" if cell_evaluable else "FAIL",
            }
        )

    families = {cell["phenomenon_family"] for cell in cells.values()}
    surfaces = {cell["application_surface"] for cell in cells.values()}
    scope_pass = (
        len(families) >= payload["analysis_policy"]["required_families"]
        and len(surfaces) >= payload["analysis_policy"]["required_application_surfaces"]
    )
    all_cells_evaluable = all(row["cell_gate"] == "PASS" for row in cell_results)
    pooled_margin = dersimonian_laird(
        [row["family_selective_margin"]["point_estimate"] for row in cell_results],
        [row["family_selective_margin"]["standard_error"] ** 2 for row in cell_results],
        design_floor,
    )
    evidence_status = (
        "NON_EVIDENTIAL_SYNTHETIC"
        if payload["data_kind"] == "synthetic_test"
        else "MANIFEST_BOUND_PRODUCTION_TARGET_ANALYSIS"
    )
    return {
        "dataset_id": payload["dataset_id"],
        "analysis_status": "ESTIMATED",
        "evidence_status": evidence_status,
        "production_eligibility": (
            "NOT_APPLICABLE_SYNTHETIC"
            if payload["data_kind"] == "synthetic_test"
            else "VERIFIED_MANIFEST_BOUND"
        ),
        "synthetic_warning": (
            "Synthetic self-test results are regression checks, not evidence about a model, "
            "assessment procedure, or target population."
            if payload["data_kind"] == "synthetic_test"
            else None
        ),
        "simultaneous_uncertainty": {
            "method": "Bonferroni-adjusted Wilson intervals with conservative derived bounds",
            "interval_level": interval_level,
            "binomial_proportions_in_family": comparison_count,
            "z_value": z,
        },
        "repeat_integrity": "EXACT_FROZEN_SETS_VERIFIED",
        "raw_joint_outcomes": raw_joint_outcomes,
        "cell_results": cell_results,
        "scope_gate": {
            "observed_families": sorted(families),
            "required_family_count": payload["analysis_policy"]["required_families"],
            "observed_application_surfaces": sorted(surfaces),
            "required_application_surface_count": payload["analysis_policy"][
                "required_application_surfaces"
            ],
            "gate": "PASS" if scope_pass else "FAIL",
        },
        "behavioural_claim": {
            "status": "ESTIMAND_REPORTED",
            "scope_in_range": scope_pass,
            "all_cells_evaluable": all_cells_evaluable,
            "in_scope_and_evaluable": scope_pass and all_cells_evaluable,
            "family_selective_margins": {
                row["cell_id"]: row["family_selective_margin"] for row in cell_results
            },
            "pooled_selective_margin": pooled_margin,
            "decision_rule": (
                "The pooled selective-margin estimand and its interval are reported "
                "against the design floor. Any accept, revise, or retire decision is "
                "tied to declared losses, not to whether an interval clears the floor; "
                "the floor is a design input, not an acceptance threshold."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="?", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--shortcuts", type=Path, default=DEFAULT_SHORTCUTS)
    parser.add_argument(
        "--binding-root",
        type=Path,
        default=ROOT,
        help="Root against which production-manifest and bound-artifact paths resolve",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        payload = load_json(args.results)
        errors = schema_errors(payload, load_json(args.schema))
        if errors:
            raise StudyBAnalysisError("; ".join(errors))
        shortcut_policy = load_shortcut_policy(args.shortcuts)
        result = analyze_payload(payload, shortcut_policy, binding_root=args.binding_root)
    except (OSError, csv.Error, json.JSONDecodeError, StudyBAnalysisError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
