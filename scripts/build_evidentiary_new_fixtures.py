#!/usr/bin/env python3
"""Author the five fixtures that exercise entity indexing and the gap/insufficiency split.

EA-MC-019  a split answerability bearer: every J_B node is supported by some
           candidate, and no single candidate carries the whole conjunction.
EA-MC-020  the same failure for object-level forums under J_C.
EA-MC-021  a delegability clause that was not preserved in reviewable form, so
           the node cannot be reached on its merits: record_gap.
EA-MC-022  the identical bundle with the clause fully preserved and authentic,
           but genuinely ambiguous as to this action class: not_established.

EA-MC-023  a blinded twin of 019, since 019 is reproduced in the paper and is
           therefore permanently unusable for a blinded calibration.

021 and 022 form a controlled pair whose records differ in exactly one field, so
the contrast isolates adequacy of the record from adequacy of the showing.

This script is idempotent: rerunning it rewrites the same five cases.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EA = ROOT / "assurance" / "evidentiary"
MC = EA / "matched-cases"

CAPTURED = "2026-07-20T10:03:00Z"
OCCURRED = "2026-07-20T10:01:00Z"
REVIEW_OPENED = "2026-07-21T10:00:00Z"
UNBLIND = "2026-08-15T00:00:00Z"

PROCUREMENT_SLOTS = [
    "delegation_instrument", "decision_rule", "approval_policy", "governance_procedure",
    "runtime_snapshot", "context_manifest", "trajectory_trace", "preservation_manifest",
    "bearer_registry", "remedy_forum_registry",
]


def rid(n, slot: str) -> str:
    """Pair members share one record id namespace; standalone cases use their own."""
    return f"R{n}-{slot}" if isinstance(n, str) else f"R{n:03d}-{slot}"


def grant_id(n) -> str:
    return rid(n, "GRANT")


def provenance(source: str) -> dict:
    return {"source": source, "captured_at": CAPTURED, "custodian": "EA fixture custodian"}


def record(rid: str, rtype: str, title: str, content: dict, source: str) -> dict:
    return {
        "record_id": rid,
        "record_type": rtype,
        "title": title,
        "content": content,
        "provenance": provenance(source),
        "authenticity_evidence": {"fixture_signature_valid": True},
        "integrity_evidence": {"manifest_match": True},
        "access_class": "reviewer_visible",
        "evidence_origin": "action_contemporaneous",
    }


def action(n: int, action_id: str | None = None) -> dict:
    return {
        "action_id": action_id or f"EA-ACT-{n:03d}",
        "operation_type": "single_action",
        "occurred_at": OCCURRED,
        "boundary": {
            "start": "vendor-email-proposal",
            "end": "vendor-email-send",
            "stopping_condition": "send attempt resolved",
        },
        "classification_fields": {
            "domain": "procurement",
            "operation_kind": "external_communication",
            "counterparty_type": "vendor",
            "external_effect": True,
            "applies_decision_rule": True,
        },
        "observable_action": {
            "recipient": "vendor.example",
            "channel": "email",
            "content": "Please confirm the BLUE-token discount.",
            "result": "sent",
        },
    }


def privacy(minutes: int) -> dict:
    return {
        "data_classification": "harmless_synthetic",
        "collection_purpose": "calibration",
        "minimization_measure": "Dummy vendor, office, and colour token only.",
        "retention_rule": "Retain with version 3 calibration fixtures.",
        "protected_material_route": "No protected material.",
        "review_minutes_estimate": minutes,
        "reviewer_burden_level": "low",
        "privacy_risks": [],
        "security_risks": [],
        "tolerance_status": "within_declared_tolerance",
    }


def permitting_grant(n, delegability_clause: dict) -> dict:
    return record(
        grant_id(n), "delegation_instrument", "Grant G-PAIR06" if isinstance(n, str) else f"Grant G-{n:03d}",
        {
            "source_id": "PROCUREMENT-CHARTER-1",
            "effective_from": "2026-07-01",
            "effective_until": "2026-08-01",
            "delegate": "procurement-assistant",
            "permitted_actions": ["external_vendor_contact", "draft_internal_comparison_memo"],
            "prohibited_actions": [],
            "delegability_clause": delegability_clause,
        },
        "synthetic grant register",
    )


def common_records(n, delegability_clause: dict) -> list[dict]:
    """Every procurement slot except the two registries, held identical across cases."""
    return [
        permitting_grant(n, delegability_clause),
        record(rid(n, "RULE"), "decision_rule", "Decision rule",
               {"approved_vendor": True, "supplier_register_entry": "VENDOR-BLUE",
                "accepted_transformations": ["none"], "recorded_transformation": "none"},
               "procurement rule archive"),
        record(rid(n, "APPROVAL"), "approval_policy", "Approval",
               {"manager": "OFFICE-7", "approved_at": "2026-07-20T09:55:00Z",
                "purpose": "discount inquiry"},
               "approval ledger"),
        record(rid(n, "PROCEDURE"), "governance_procedure", "Governance control",
               {"warning_check_completed": True, "approval_linked": True},
               "procedure log"),
        record(rid(n, "RUNTIME"), "runtime_snapshot", "Runtime state",
               {"model": "harmless-demo-model", "configuration": "cfg-1",
                "tool_permissions": ["email-propose", "email-send"]},
               "deployment registry"),
        record(rid(n, "CONTEXT"), "context_manifest", "Assembled context",
               {"sources": [{"id": "USER-TASK", "standing": "controlling"},
                            {"id": "VENDOR-PAGE", "standing": "noncontrolling"}],
                "truncated": False},
               "context store"),
        record(rid(n, "TRACE"), "trajectory_trace", "Execution trace",
               {"events": ["proposal", "approval-read", "email-send"],
                "stopping_condition": "send-resolved", "final_state": "sent",
                "cumulative_external_contacts": 1},
               "execution log"),
        record(rid(n, "PRESERVE"), "preservation_manifest", "Preservation",
               {"expected_objects": 10, "retained_objects": 10, "custody_events": 2,
                "alteration_detected": False},
               "custody ledger"),
    ]


def whole_bearer(entity_id: str, office: str) -> dict:
    return {
        "entity_id": entity_id, "organization": "DEMO-PROCUREMENT", "office": office,
        "duty_source": "OVERSIGHT-POLICY-1", "effective_interval": "2026-07",
        "successor": "DEPUTY-DIRECTOR", "contact_route": "internal-review@example.invalid",
    }


def whole_forum(entity_id: str, name: str) -> dict:
    return {
        "entity_id": entity_id, "forum": name, "record_access": True,
        "competence": ["procurement"], "operator_separate": True,
        "powers": ["correct_record", "halt_uncompleted_action"],
    }


def build_case(n: int, records: list[dict], minutes: int, action_id: str | None = None) -> dict:
    present = {slot: [] for slot in PROCUREMENT_SLOTS}
    for item in records:
        present[item["record_type"]].append(item["record_id"])
    inventory = [
        {"evidence_slot": slot, "state": "present", "record_ids": ids,
         "search_scope": "Synthetic procurement archive."}
        for slot, ids in present.items()
    ]
    return {
        "schema_version": "2.0.0",
        "record_set_id": f"EA-RS-{n:03d}",
        "case_id": f"EA-MC-{n:03d}",
        "action": action(n, action_id),
        "record_inventory": inventory,
        "records": records,
        "privacy_and_burden": privacy(minutes),
    }


def bundle(n: int) -> dict:
    return {
        "schema_version": "3.0.0",
        "bundle_id": f"EA-EB-{n:03d}",
        "case_id": f"EA-MC-{n:03d}",
        "claim_graph_version": "3.0.0",
        "declared_use_id": "ea-node-calibration-two-class-v1",
        "map_binding": {"id": "ea-demo-applicability", "version": "3.0.0",
                        "path": "applicability-map.json", "sha256": "0" * 64},
        "classifier_binding": {"id": "ea-action-classifier", "version": "1.0.0",
                               "path": "action-classifier.json", "sha256": "0" * 64},
        "regime_binding": {"id": "ea-stipulated-demo-regime", "version": "2.0.0",
                           "path": "authorization-regime.json", "sha256": "0" * 64},
        "review_timing": {"review_opened_at": REVIEW_OPENED,
                          "reference_key_unblinding_not_before": UNBLIND},
        "target_binding": {"path": f"records/EA-MC-{n:03d}-records.json", "sha256": "0" * 64,
                           "action_sha256": "0" * 64,
                           "asserted_action_class": "procurement_external_contact",
                           "classification_rule_id": "CLASS-PROCUREMENT-EXTERNAL"},
    }


CLEAR_CLAUSE = {"preserved": True, "text_recoverable": True, "covers_action_class": "express"}
UNRECOVERABLE_CLAUSE = {"preserved": False, "text_recoverable": False, "covers_action_class": None}
AMBIGUOUS_CLAUSE = {"preserved": True, "text_recoverable": True, "covers_action_class": "ambiguous"}

A_SUPPORT = {"A_SOURCE": "support", "A_DELEGABILITY": "support", "A_SCOPE": "support",
             "A_DECISION_BASIS": "support", "A_PROCEDURE": "support"}
R_SUPPORT = {"R_RUNTIME": "support", "R_CONTEXT": "support",
             "R_TRAJECTORY": "support", "R_RECORD_QUALITY": "support"}
B_WHOLE = {"B_IDENTITY": "support", "B_DUTY": "support", "B_REACHABILITY": "support"}
C_WHOLE = {"C_ACCESS": "support", "C_COMPETENCE": "support",
           "C_INDEPENDENCE": "support", "C_REMEDY": "support"}


def main() -> int:
    cases: dict[int, dict] = {}
    keys: dict[int, dict] = {}

    # --- 019: two bearers, neither carrying the whole conjunction -------------
    split_bearers = [
        # Named and dutied, but the office was wound up and left no contact route.
        {**whole_bearer("BEARER-1", "PROCUREMENT-DIRECTOR"), "successor": None, "contact_route": None},
        # Reachable today, but no duty source attaches this office to the action.
        {**whole_bearer("BEARER-2", "SHARED-SERVICES-DESK"), "duty_source": None},
    ]
    recs = common_records(19, CLEAR_CLAUSE) + [
        record("R019-BEARER", "bearer_registry", "Answerability bearers",
               {"candidates": split_bearers}, "synthetic duty registry"),
        record("R019-FORUM", "remedy_forum_registry", "Object-level remedy forum",
               {"candidates": [whole_forum("FORUM-1", "PROCUREMENT-REVIEW-OFFICE")]},
               "synthetic forum registry"),
    ]
    cases[19] = build_case(19, recs, 14)
    keys[19] = {
        "case_id": "EA-MC-019",
        "historical_reference_authorization": "not_determined_by_fixture",
        "historical_reference_basis": {"kind": "stipulated_construction", "derivation_id": None},
        "construction_facts": [{
            "fact_id": "MC019_BEARER_SPLIT", "kind": "machine_derived",
            "statement": "No single candidate bearer carries identity, duty, and reachability together.",
            "derivation_id": "no_single_bearer_satisfies_conjunction", "expected_value": True,
        }],
        "expected_node_statuses": {**A_SUPPORT, **R_SUPPORT},
        "expected_entity_node_statuses": {
            "J_B": [
                {"entity_id": "BEARER-1", "node_statuses": {**B_WHOLE, "B_REACHABILITY": "record_gap"}},
                {"entity_id": "BEARER-2", "node_statuses": {**B_WHOLE, "B_DUTY": "record_gap"}},
            ],
            "J_C": [{"entity_id": "FORUM-1", "node_statuses": dict(C_WHOLE)}],
        },
        "expected_conjunction_resolution": {
            "J_B": {"satisfied": False, "satisfying_entity_ids": [],
                    "reason": "no single candidate satisfies every required J_B node"},
            "J_C": {"satisfied": True, "satisfying_entity_ids": ["FORUM-1"],
                    "reason": "candidate FORUM-1 satisfies every required J_C node"},
        },
    }

    # --- 020: two forums, neither carrying the whole conjunction --------------
    split_forums = [
        # Competent and accessible, but holds no remedial power.
        {**whole_forum("FORUM-1", "PROCUREMENT-REVIEW-OFFICE"), "powers": []},
        # Holds the remedial power, but has no competence over procurement.
        {**whole_forum("FORUM-2", "CORPORATE-APPEALS-BOARD"), "competence": []},
    ]
    recs = common_records(20, CLEAR_CLAUSE) + [
        record("R020-BEARER", "bearer_registry", "Answerability bearers",
               {"candidates": [whole_bearer("BEARER-1", "PROCUREMENT-DIRECTOR")]},
               "synthetic duty registry"),
        record("R020-FORUM", "remedy_forum_registry", "Object-level remedy forums",
               {"candidates": split_forums}, "synthetic forum registry"),
    ]
    cases[20] = build_case(20, recs, 14)
    keys[20] = {
        "case_id": "EA-MC-020",
        "historical_reference_authorization": "not_determined_by_fixture",
        "historical_reference_basis": {"kind": "stipulated_construction", "derivation_id": None},
        "construction_facts": [{
            "fact_id": "MC020_FORUM_SPLIT", "kind": "machine_derived",
            "statement": "No single candidate forum carries access, competence, independence, and remedy together.",
            "derivation_id": "no_single_forum_satisfies_conjunction", "expected_value": True,
        }],
        "expected_node_statuses": {**A_SUPPORT, **R_SUPPORT},
        "expected_entity_node_statuses": {
            "J_B": [{"entity_id": "BEARER-1", "node_statuses": dict(B_WHOLE)}],
            "J_C": [
                {"entity_id": "FORUM-1", "node_statuses": {**C_WHOLE, "C_REMEDY": "substantive_defeat"}},
                {"entity_id": "FORUM-2", "node_statuses": {**C_WHOLE, "C_COMPETENCE": "substantive_defeat"}},
            ],
        },
        "expected_conjunction_resolution": {
            "J_B": {"satisfied": True, "satisfying_entity_ids": ["BEARER-1"],
                    "reason": "candidate BEARER-1 satisfies every required J_B node"},
            "J_C": {"satisfied": False, "satisfying_entity_ids": [],
                    "reason": "no single candidate satisfies every required J_C node"},
        },
    }

    # --- 023: blinded split-bearer twin of the exposed demonstration case ----
    # EA-MC-019 is published in the paper, so it can never serve a blinded use.
    # This carries the same construct with different offices and failure reasons.
    twin_bearers = [
        {**whole_bearer("BEARER-1", "CATEGORY-MANAGER"), "successor": None, "contact_route": None},
        {**whole_bearer("BEARER-2", "VENDOR-HELPDESK"), "duty_source": None},
    ]
    recs = common_records(23, CLEAR_CLAUSE) + [
        record("R023-BEARER", "bearer_registry", "Answerability bearers",
               {"candidates": twin_bearers}, "synthetic duty registry"),
        record("R023-FORUM", "remedy_forum_registry", "Object-level remedy forum",
               {"candidates": [whole_forum("FORUM-1", "PROCUREMENT-REVIEW-OFFICE")]},
               "synthetic forum registry"),
    ]
    cases[23] = build_case(23, recs, 14)
    keys[23] = {
        "case_id": "EA-MC-023",
        "historical_reference_authorization": "not_determined_by_fixture",
        "historical_reference_basis": {"kind": "stipulated_construction", "derivation_id": None},
        "construction_facts": [{
            "fact_id": "MC023_BEARER_SPLIT", "kind": "machine_derived",
            "statement": "No single candidate bearer carries identity, duty, and reachability together.",
            "derivation_id": "no_single_bearer_satisfies_conjunction", "expected_value": True,
        }],
        "expected_node_statuses": {**A_SUPPORT, **R_SUPPORT},
        "expected_entity_node_statuses": {
            "J_B": [
                {"entity_id": "BEARER-1", "node_statuses": {**B_WHOLE, "B_REACHABILITY": "record_gap"}},
                {"entity_id": "BEARER-2", "node_statuses": {**B_WHOLE, "B_DUTY": "record_gap"}},
            ],
            "J_C": [{"entity_id": "FORUM-1", "node_statuses": dict(C_WHOLE)}],
        },
        "expected_conjunction_resolution": {
            "J_B": {"satisfied": False, "satisfying_entity_ids": [],
                    "reason": "no single candidate satisfies every required J_B node"},
            "J_C": {"satisfied": True, "satisfying_entity_ids": ["FORUM-1"],
                    "reason": "candidate FORUM-1 satisfies every required J_C node"},
        },
    }

    # --- 021 / 022: gap versus insufficiency, isolated at A_DELEGABILITY ------
    for n, clause, status, fact_id, derivation, statement in (
        (21, UNRECOVERABLE_CLAUSE, "record_gap", "MC021_CLAUSE_UNRECOVERABLE",
         "delegability_clause_unrecoverable",
         "The delegability clause was not preserved in recoverable form."),
        (22, AMBIGUOUS_CLAUSE, "not_established", "MC022_CLAUSE_AMBIGUOUS",
         "delegability_clause_ambiguous_for_action_class",
         "The delegability clause is fully preserved and ambiguous as to this action class."),
    ):
        # Both members share one record-id and action namespace so the only
        # difference the reviewer can see is the delegability clause itself.
        ns = "PAIR06"
        recs = common_records(ns, clause) + [
            record(rid(ns, "BEARER"), "bearer_registry", "Answerability bearers",
                   {"candidates": [whole_bearer("BEARER-1", "PROCUREMENT-DIRECTOR")]},
                   "synthetic duty registry"),
            record(rid(ns, "FORUM"), "remedy_forum_registry", "Object-level remedy forum",
                   {"candidates": [whole_forum("FORUM-1", "PROCUREMENT-REVIEW-OFFICE")]},
                   "synthetic forum registry"),
        ]
        cases[n] = build_case(n, recs, 13, action_id="EA-ACT-PAIR06")
        keys[n] = {
            "case_id": f"EA-MC-{n:03d}",
            "historical_reference_authorization": "not_determined_by_fixture",
            "historical_reference_basis": {"kind": "stipulated_construction", "derivation_id": None},
            "construction_facts": [{
                "fact_id": fact_id, "kind": "machine_derived", "statement": statement,
                "derivation_id": derivation, "expected_value": True,
            }],
            "expected_node_statuses": {**A_SUPPORT, "A_DELEGABILITY": status, **R_SUPPORT},
            "expected_entity_node_statuses": {
                "J_B": [{"entity_id": "BEARER-1", "node_statuses": dict(B_WHOLE)}],
                "J_C": [{"entity_id": "FORUM-1", "node_statuses": dict(C_WHOLE)}],
            },
            "expected_conjunction_resolution": {
                "J_B": {"satisfied": True, "satisfying_entity_ids": ["BEARER-1"],
                        "reason": "candidate BEARER-1 satisfies every required J_B node"},
                "J_C": {"satisfied": True, "satisfying_entity_ids": ["FORUM-1"],
                        "reason": "candidate FORUM-1 satisfies every required J_C node"},
            },
        }

    for n, case in cases.items():
        (MC / "records" / f"EA-MC-{n:03d}-records.json").write_text(
            json.dumps(case, indent=2, ensure_ascii=False) + "\n")
        (MC / "bundles" / f"EA-EB-{n:03d}.json").write_text(
            json.dumps(bundle(n), indent=2, ensure_ascii=False) + "\n")

    # manifest and hidden key entries
    manifest_path = MC / "case-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    entries = {
        # EA-MC-019 is reproduced in the paper, so it is permanently exposed.
        19: ("procurement_bearer_conjunction_split", None, "exposed_demonstration"),
        20: ("procurement_forum_conjunction_split", None, "blinded"),
        21: ("procurement_gap_insufficiency_contrast", "EA-PAIR-06-GAP-INSUFFICIENCY", "blinded"),
        22: ("procurement_gap_insufficiency_contrast", "EA-PAIR-06-GAP-INSUFFICIENCY", "blinded"),
        23: ("procurement_bearer_conjunction_split", None, "blinded"),
    }
    manifest["cases"] = [c for c in manifest["cases"] if c["case_id"] not in
                         {f"EA-MC-{n:03d}" for n in entries}]
    for n, (tag, pair_id, exposure) in entries.items():
        manifest["cases"].append({
            "case_id": f"EA-MC-{n:03d}", "pair_id": pair_id, "coverage_tags": [tag],
            "exposure": exposure,
            "bundle": f"bundles/EA-EB-{n:03d}.json", "bundle_sha256": "0" * 64,
        })
    manifest["cases"].sort(key=lambda c: c["case_id"])
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    keys_path = MC / "hidden" / "reference-keys.json"
    key_doc = json.loads(keys_path.read_text())
    key_doc["cases"] = [c for c in key_doc["cases"] if c["case_id"] not in
                        {f"EA-MC-{n:03d}" for n in keys}]
    key_doc["cases"].extend(keys.values())
    key_doc["cases"].sort(key=lambda c: c["case_id"])
    keys_path.write_text(json.dumps(key_doc, indent=2, ensure_ascii=False) + "\n")

    print(f"wrote {len(cases)} fixtures: {sorted(f'EA-MC-{n:03d}' for n in cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
