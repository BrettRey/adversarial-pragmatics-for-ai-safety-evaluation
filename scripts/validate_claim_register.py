#!/usr/bin/env python3
"""Validate prospective projective claims and reject semantic level errors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "assurance/shared/projective-claim.schema.json"
DEFAULT_VALID = ROOT / "assurance/shared/fixtures/valid-projective-claim.json"
DEFAULT_INVALID = ROOT / "assurance/shared/fixtures/invalid-posthoc-narrowing.json"


class ClaimValidationError(ValueError):
    """Raised when a claim is structurally valid but scientifically incoherent."""


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def iter_claims(payload: Any) -> Iterable[dict[str, Any]]:
    if isinstance(payload, dict) and "claims" in payload:
        claims = payload["claims"]
        if not isinstance(claims, list) or not claims:
            raise ClaimValidationError("register claims must be a non-empty list")
        for claim in claims:
            if not isinstance(claim, dict):
                raise ClaimValidationError("each register claim must be an object")
            yield claim
        return
    if not isinstance(payload, dict):
        raise ClaimValidationError("claim payload must be an object")
    yield payload


def semantic_checks(claim: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    claim_id = claim.get("claim_id", "<unknown>")
    declaration = claim.get("declaration", {})
    inquiry = claim.get("inquiry_use", {})
    warrant = claim.get("warrant_plan", {})
    revision = claim.get("revision_rule", {})
    provenance = claim.get("provenance", {})

    if provenance.get("declaration_timing") != "before_target_outcomes":
        errors.append(f"{claim_id}: declaration must precede target outcomes")

    population = str(declaration.get("population", "")).lower()
    conditions = " ".join(declaration.get("conditions", [])).lower()
    if "only successful" in population or "failures removed" in conditions:
        errors.append(f"{claim_id}: population/conditions encode post hoc rescue")

    if revision.get("posthoc_scope_change_policy") != "new_claim_required":
        errors.append(f"{claim_id}: post hoc scope changes must create a new claim")
    if revision.get("independent_retest_required") is not True:
        errors.append(f"{claim_id}: a demoted fallback requires independent retest")

    excluded_uses = [str(item).strip().lower() for item in inquiry.get("excluded_uses", [])]
    if excluded_uses == ["none"]:
        errors.append(f"{claim_id}: excluded uses must be substantively declared")

    minimum_reach = str(inquiry.get("minimum_useful_reach", "")).lower()
    if minimum_reach in {"one case", "one surviving case", "any success"}:
        errors.append(f"{claim_id}: minimum useful reach is trivial")

    validity = warrant.get("assessment_validity", {})
    if not any(validity.get(aspect) for aspect in validity):
        errors.append(f"{claim_id}: assessment-validity plan is empty")

    world = warrant.get("world_side", {})
    commitments = set(world.get("commitments", []))
    evidence = world.get("evidence", [])
    if commitments and not evidence:
        errors.append(f"{claim_id}: world-side commitments lack separate evidence")
    if "corrective_control" in commitments:
        joined = " ".join(str(item).lower() for item in evidence)
        required = ("perturb", "response", "preserv")
        if not all(token in joined for token in required):
            errors.append(
                f"{claim_id}: corrective-control evidence must name a perturbation, "
                "response pathway, and preserved relation"
            )

    source = str(declaration.get("source_result", "")).strip().lower()
    outcome = str(declaration.get("projected_outcome", "")).strip().lower()
    if source and outcome and source == outcome:
        errors.append(f"{claim_id}: projected outcome merely repeats the source result")

    return errors


def validate_payload(payload: Any, schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for claim in iter_claims(payload):
        for issue in sorted(validator.iter_errors(claim), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in issue.path) or "<root>"
            errors.append(f"{claim.get('claim_id', '<unknown>')}:{location}: {issue.message}")
        if not errors or not any(
            item.startswith(f"{claim.get('claim_id', '<unknown>')}:") for item in errors
        ):
            errors.extend(semantic_checks(claim))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="claim or register JSON files")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="check that the valid fixture passes and the post hoc fixture fails",
    )
    args = parser.parse_args()

    schema = load_json(args.schema)
    failures = 0

    if args.self_test:
        valid_errors = validate_payload(load_json(DEFAULT_VALID), schema)
        invalid_errors = validate_payload(load_json(DEFAULT_INVALID), schema)
        if valid_errors:
            failures += 1
            print("FAIL valid fixture:")
            print("\n".join(f"  {item}" for item in valid_errors))
        if not invalid_errors:
            failures += 1
            print("FAIL invalid fixture was accepted")
        if failures == 0:
            print(f"PASS valid fixture: {DEFAULT_VALID.relative_to(ROOT)}")
            print(
                "PASS rejected post hoc fixture: "
                f"{DEFAULT_INVALID.relative_to(ROOT)} ({len(invalid_errors)} issue(s))"
            )

    for path in args.paths:
        errors = validate_payload(load_json(path), schema)
        if errors:
            failures += 1
            print(f"FAIL {path}:")
            print("\n".join(f"  {item}" for item in errors))
        else:
            print(f"PASS {path}")

    if not args.self_test and not args.paths:
        parser.error("supply at least one path or --self-test")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
