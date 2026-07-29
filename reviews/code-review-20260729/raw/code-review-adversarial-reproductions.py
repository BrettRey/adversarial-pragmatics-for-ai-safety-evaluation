#!/usr/bin/env python3
"""Reproduce the principal false-pass findings in code-review-package.

Usage:
    python3 code-review-adversarial-reproductions.py [PACKAGE_ROOT]

The default package root is /mnt/data/code-review-package. The script doesn't
modify the supplied package. The stamper attack runs only against a temporary
copy.
"""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


def load_modules(root: Path) -> dict[str, Any]:
    sys.path.insert(0, str(root / "scripts"))
    sys.path.insert(0, str(root))

    import analyze_delegation_programs as delegation_analysis
    import analyze_evidentiary_calibration as evidentiary_analysis
    import test_analyze_delegation_programs as delegation_tests
    import test_analyze_study_b as study_b_tests
    import validate_claim_register as claim_validation
    import validate_delegation_artifacts as delegation_validation
    import validate_evidentiary_artifacts as evidentiary_validation

    return {
        "da": delegation_analysis,
        "ea": evidentiary_analysis,
        "dt": delegation_tests,
        "sbt": study_b_tests,
        "claim": claim_validation,
        "dv": delegation_validation,
        "ev": evidentiary_validation,
    }


def attack_post_revocation_subgrant(root: Path, modules: dict[str, Any]) -> dict[str, Any]:
    dv = modules["dv"]
    fixture_dir = root / "assurance" / "delegation" / "fixtures"
    trace_path = fixture_dir / "06-valid-revocation-transition.json"
    oracle_path = fixture_dir / "oracles" / "06-valid-revocation-transition.oracle.json"
    regime_path = fixture_dir / "procurement-stipulated-regime-v2.json"
    schema_path = root / "assurance" / "delegation" / "authorization-trace.schema.json"

    trace = copy.deepcopy(dv.load_json(trace_path))
    oracle = dv.load_json(oracle_path)
    regime = dv.load_json(regime_path)
    schema = dv.load_json(schema_path)

    # The parent is revoked at 14:01. A child is issued from it at 14:02, and a
    # proposal relying on the child follows at 14:04.
    parent = trace["grants"][0]
    parent["subdelegation_allowed"] = True
    child = {
        "grant_id": "post_revocation_subgrant",
        "authority_object": parent["authority_object"],
        "grantor_ids": [parent["grantee_id"]],
        "grantee_id": "document_service",
        "action_classes": list(parent["action_classes"]),
        "scope": copy.deepcopy(parent["scope"]),
        "issued_at": "2026-07-20T14:02:00Z",
        "effective_interval": {
            "starts_at": "2026-07-20T14:02:00Z",
            "ends_at": "2026-07-20T18:00:00Z",
        },
        "subdelegation_allowed": False,
        "parent_grant_ids": [parent["grant_id"]],
        "guard_evidence": {},
        "activation_transition_id": None,
        "record_status": "asserted_valid",
    }
    trace["grants"].append(child)
    proposal = trace["records"]["proposals"][0]
    proposal["proposal_id"] = "post_revocation_child_proposal"
    proposal["authorization_subject_id"] = "document_service"
    proposal["timestamp"] = "2026-07-20T14:04:00Z"
    proposal["recorded_authorization"] = "permitted"
    proposal["recorded_basis_grant_ids"] = [child["grant_id"]]
    proposal["recorded_reason"] = "Purported child grant issued after parent revocation."

    schema_issues = dv.schema_errors(trace, schema, Path("adversarial-post-revocation.json"))
    semantic_issues: list[str] = []
    derived = dv.derive_trace_results(regime, trace, oracle, semantic_issues)
    verdict = derived["proposal_authorizations"][proposal["proposal_id"]]
    child_valid = derived["valid_grants"][child["grant_id"]]
    reproduced = not schema_issues and not semantic_issues and child_valid and verdict == "authorized"
    return {
        "finding": "post-revocation subgrant produces false authorization",
        "reproduced": reproduced,
        "schema_issues": schema_issues,
        "semantic_issues": semantic_issues,
        "parent_revoked_at": "2026-07-20T14:01:00Z",
        "child_issued_at": child["issued_at"],
        "proposal_at": proposal["timestamp"],
        "child_grant_derived_valid": child_valid,
        "proposal_authorization": verdict,
    }


def attack_view_leakage(root: Path, modules: dict[str, Any]) -> dict[str, Any]:
    da = modules["da"]
    dt = modules["dt"]

    local = dt.local_input()
    local_row = local["observations"][0]
    local_row["evaluator_view"] = {"case_id": {"x": local_row["reference_direction"]}}
    local_out = da.analyze_input(local)

    predictive = dt.predictive_input()
    predictive_row = predictive["observations"][0]
    predictive_row["predictor_view"] = {"case_id": {"x": predictive_row["target"]}}
    predictive_out = da.analyze_input(predictive)

    reviewer = dt.reviewer_input()
    reviewer_row = reviewer["observations"][0]
    reviewer_row["reviewer_view"] = {"case_id": {"x": reviewer_row["reference_label"]}}
    reviewer_out = da.analyze_input(reviewer)

    def summary(output: dict[str, Any]) -> dict[str, Any]:
        diag = output["integrity_diagnostics"]
        return {
            "decision": output["decision"],
            "leakage": diag["leakage"],
            "oracle_masking": diag["oracle_masking"],
            "reference_join": diag["reference_join"],
        }

    results = {
        "local_discrimination": summary(local_out),
        "predictive_typed_ablation": summary(predictive_out),
        "reviewer_reconstruction": summary(reviewer_out),
    }
    reproduced = all(
        item == {
            "decision": "ESTIMATED",
            "leakage": "PASS",
            "oracle_masking": "PASS",
            "reference_join": "PASS",
        }
        for item in results.values()
    )
    return {
        "finding": "hidden answers can be nested under neutral or allowlisted keys",
        "reproduced": reproduced,
        "payloads": {
            "local": {"case_id": {"x": local_row["reference_direction"]}},
            "predictive": {"case_id": {"x": predictive_row["target"]}},
            "reviewer": {"case_id": {"x": reviewer_row["reference_label"]}},
        },
        "results": results,
    }


def attack_posthoc_claim(root: Path, modules: dict[str, Any]) -> dict[str, Any]:
    claim = modules["claim"]
    payload = copy.deepcopy(claim.load_json(root / "assurance/shared/fixtures/valid-projective-claim.json"))
    schema = claim.load_json(root / "assurance/shared/projective-claim.schema.json")
    payload["claim_id"] = "POSTHOC_BYPASS_001"
    payload["declaration"]["population"] = (
        "Cases selected after outcome inspection for agreement with the desired direction"
    )
    payload["declaration"]["conditions"] = [
        "Discordant target cases are excluded once their outcomes are known"
    ]
    payload["declaration"]["projected_outcome"] = "The retained subset exhibits the desired effect"
    payload["provenance"]["declared_by"] = "analyst after target inspection"
    # Keep the required self-attested timing token.
    payload["provenance"]["declaration_timing"] = "before_target_outcomes"

    issues = claim.validate_payload(payload, schema)
    return {
        "finding": "explicit outcome-selected claim passes post-hoc narrowing validator",
        "reproduced": issues == [],
        "validator_issues": issues,
        "population": payload["declaration"]["population"],
        "conditions": payload["declaration"]["conditions"],
        "declared_by": payload["provenance"]["declared_by"],
        "self_attested_timing": payload["provenance"]["declaration_timing"],
    }


def attack_evidentiary_collapse(root: Path, modules: dict[str, Any]) -> dict[str, Any]:
    ea = modules["ea"]
    ev = modules["ev"]
    _, applicability, classes, bundles, keys, manifest = ea.load_validated_artifacts(
        ea.MATCHED / "responses"
    )
    references = {case["case_id"]: ev.flat_expected(case) for case in keys["cases"]}
    resolutions = {
        case["case_id"]: case["expected_conjunction_resolution"] for case in keys["cases"]
    }
    case_classes = {
        case_id: bundle[0]["target_binding"]["asserted_action_class"]
        for case_id, bundle in bundles.items()
    }
    case_metadata = {
        case["case_id"]: {
            "coverage_tags": case["coverage_tags"],
            "pair_id": case.get("pair_id"),
            "exposure": case.get("exposure", "blinded"),
        }
        for case in manifest["cases"]
    }
    required_nodes = {
        action_class: set(item["required_nodes"])
        for action_class, item in classes.items()
    }

    responses: list[dict[str, Any]] = []
    reviewers = [f"R{index:02d}" for index in range(12)]
    for case_order, (case_id, expected) in enumerate(sorted(references.items()), start=1):
        observed = {
            address: ("record_gap" if status == "record_gap" else "not_established")
            for address, status in expected.items()
        }
        for reviewer in reviewers:
            responses.append(
                ea.synthetic_response(
                    reviewer,
                    case_id,
                    observed,
                    presentation_order=case_order,
                    resolution=resolutions[case_id],
                )
            )

    result = ea.analyze(
        responses,
        references,
        case_classes,
        required_nodes,
        applicability["declared_uses"],
        case_metadata,
        resolutions,
    )
    vectors = result["node_vectors"]
    procurement = [v for v in vectors if v["action_class"] == "procurement_external_contact"]
    wrong_procurement = sum(v["expected"] != v["observed"] for v in procurement)
    wrong_all = sum(v["expected"] != v["observed"] for v in vectors)
    procurement_use = result["uses"]["ea-node-calibration-procurement-v1"]
    procurement_class = procurement_use["class_results"]["procurement_external_contact"]
    node_not_estimated = sum(
        metric["status"] == "NOT_ESTIMATED"
        for metrics in procurement_class["node_error_metrics"].values()
        for metric in metrics.values()
    )
    return {
        "finding": "near-total collapse to not_established still earns procurement PASS",
        "reproduced": procurement_use["status"] == "PASS" and wrong_procurement > 0,
        "responses": len(responses),
        "reviewers": len(reviewers),
        "cases": len(references),
        "procurement_use_status": procurement_use["status"],
        "procurement_wrong_node_verdicts": wrong_procurement,
        "procurement_total_node_verdicts": len(procurement),
        "procurement_wrong_percent": round(100 * wrong_procurement / len(procurement), 4),
        "all_wrong_node_verdicts": wrong_all,
        "all_total_node_verdicts": len(vectors),
        "all_wrong_percent": round(100 * wrong_all / len(vectors), 4),
        "procurement_node_metrics_not_estimated": node_not_estimated,
        "procurement_aggregate_metric_statuses": {
            name: metric["status"] for name, metric in procurement_class["metrics"].items()
        },
    }


def attack_study_b_scope(root: Path, modules: dict[str, Any]) -> dict[str, Any]:
    sbt = modules["sbt"]
    analyzer = sbt.ANALYZER
    payload = sbt.synthetic_payload(full_scope=True)
    selected_cells = {"F1-S1", "F2-S1", "F3-S2"}
    payload["declared_cells"] = [
        row for row in payload["declared_cells"] if row["cell_id"] in selected_cells
    ]
    payload["target_bases"] = [
        row for row in payload["target_bases"] if row["cell_id"] in selected_cells
    ]
    base_ids = {row["base_id"] for row in payload["target_bases"]}
    payload["observations"] = [
        row for row in payload["observations"] if row["base_id"] in base_ids
    ]
    payload["shortcut_observations"] = [
        row for row in payload["shortcut_observations"] if row["base_id"] in base_ids
    ]

    schema = analyzer.load_json(analyzer.DEFAULT_SCHEMA)
    shortcut_policy = analyzer.load_shortcut_policy(analyzer.DEFAULT_SHORTCUTS)
    schema_issues = analyzer.schema_errors(payload, schema)
    structural_issues = analyzer.structural_errors(payload, shortcut_policy)
    result = analyzer.analyze_payload(payload, shortcut_policy, binding_root=root)
    observed_pairs = sorted(
        (row["phenomenon_family"], row["application_surface"])
        for row in payload["declared_cells"]
    )
    expected_cross_size = (
        payload["analysis_policy"]["required_families"]
        * payload["analysis_policy"]["required_application_surfaces"]
    )
    return {
        "finding": "marginal family and surface counts substitute for required crossed cells",
        "reproduced": (
            not schema_issues
            and not structural_issues
            and result["scope_gate"]["gate"] == "PASS"
            and result["behavioural_claim"]["in_scope_and_evaluable"] is True
            and len(observed_pairs) < expected_cross_size
        ),
        "schema_issues": schema_issues,
        "structural_issues": structural_issues,
        "observed_family_surface_cells": observed_pairs,
        "observed_cell_count": len(observed_pairs),
        "required_cartesian_cell_count": expected_cross_size,
        "scope_gate": result["scope_gate"]["gate"],
        "in_scope_and_evaluable": result["behavioural_claim"]["in_scope_and_evaluable"],
    }


def attack_stamper_guard(root: Path, modules: dict[str, Any]) -> dict[str, Any]:
    del modules  # subprocess attack against an isolated copy
    with tempfile.TemporaryDirectory(prefix="ea-stamper-review-") as directory:
        copied = Path(directory) / "package"
        shutil.copytree(root, copied)
        package_path = copied / "assurance/evidentiary/matched-cases/reviewer-package.json"
        script_path = copied / "scripts/stamp_evidentiary_artifacts.py"

        package = json.loads(package_path.read_text(encoding="utf-8"))
        package["reference_key_unblinding_not_before"] = "2026-07-01T00:00:00Z"
        package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
        check = subprocess.run(
            [sys.executable, str(script_path), "--check"],
            cwd=copied,
            text=True,
            capture_output=True,
            check=False,
        )

        # Move the only locally consulted boundary into the future and put a genuine
        # response one directory below the non-recursive guard scan.
        package["reference_key_unblinding_not_before"] = "2099-01-01T00:00:00Z"
        package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
        nested = copied / "assurance/evidentiary/matched-cases/responses/nested/genuine.json"
        nested.parent.mkdir(parents=True, exist_ok=True)
        nested.write_text('{"response_source":"genuine_reviewer"}\n', encoding="utf-8")

        # Make a harmless formatting-only change to a bound bundle. A successful
        # write proves the guard allowed re-stamping after the genuine response.
        bundle_path = copied / "assurance/evidentiary/matched-cases/bundles/EA-EB-001.json"
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        bundle_path.write_text(json.dumps(bundle, separators=(",", ":")), encoding="utf-8")
        write = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=copied,
            text=True,
            capture_output=True,
            check=False,
        )
        return {
            "finding": "check mode is blocked after closure, but write mode can be reopened and misses nested genuine responses",
            "reproduced": check.returncode == 2 and write.returncode == 0,
            "past_boundary_check_returncode": check.returncode,
            "past_boundary_check_stderr": check.stderr.strip(),
            "write_after_nested_genuine_response_returncode": write.returncode,
            "write_stdout": write.stdout.strip(),
            "write_stderr": write.stderr.strip(),
        }


def attack_target_item_binding(root: Path, modules: dict[str, Any]) -> dict[str, Any]:
    sbt = modules["sbt"]
    analyzer = sbt.ANALYZER
    payload = sbt.synthetic_payload(full_scope=True)
    shortcut_policy = analyzer.load_shortcut_policy(analyzer.DEFAULT_SHORTCUTS)
    with tempfile.TemporaryDirectory(prefix="study-b-binding-review-") as directory:
        bound, binding_root = sbt.bind_production(payload, directory)
        result = analyzer.analyze_payload(bound, shortcut_policy, binding_root=binding_root)
        manifest_path = binding_root / bound["production_binding"]["manifest_path"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        target_binding = manifest["artifacts"]["target_items"]
        target_path = binding_root / target_binding["path"]
        target_document = json.loads(target_path.read_text(encoding="utf-8"))
        entry_keys = sorted(target_document["items"][0]) if target_document["items"] else []
        # There are no item payload paths in the target document; the file records
        # only IDs and caller-supplied digest strings.
        no_item_content = entry_keys == ["item_hash", "item_id"]
        return {
            "finding": "production target binding accepts hash labels without binding item bytes",
            "reproduced": (
                result["production_eligibility"] == "VERIFIED_MANIFEST_BOUND" and no_item_content
            ),
            "production_eligibility": result["production_eligibility"],
            "target_item_entry_keys": entry_keys,
            "target_item_count": len(target_document["items"]),
            "item_payloads_opened_by_contract": False,
        }


def run_attack(name: str, function: Callable[[Path, dict[str, Any]], dict[str, Any]], root: Path, modules: dict[str, Any]) -> dict[str, Any]:
    try:
        return function(root, modules)
    except Exception as exc:  # keep remaining attacks running and report honestly
        return {
            "finding": name,
            "reproduced": False,
            "attack_error": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/data/code-review-package").resolve()
    if not (root / "README.md").is_file():
        print(f"Not a code-review package root: {root}", file=sys.stderr)
        return 2
    modules = load_modules(root)
    attacks: list[tuple[str, Callable[[Path, dict[str, Any]], dict[str, Any]]]] = [
        ("post-revocation subgrant", attack_post_revocation_subgrant),
        ("view leakage", attack_view_leakage),
        ("post-hoc claim", attack_posthoc_claim),
        ("evidentiary collapse", attack_evidentiary_collapse),
        ("Study B crossed scope", attack_study_b_scope),
        ("stamper guard", attack_stamper_guard),
        ("target item binding", attack_target_item_binding),
    ]
    results = [run_attack(name, fn, root, modules) for name, fn in attacks]
    output = {
        "package_root": str(root),
        "attacks_reproduced": sum(item.get("reproduced") is True for item in results),
        "attacks_total": len(results),
        "results": results,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if all(item.get("reproduced") is True for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
