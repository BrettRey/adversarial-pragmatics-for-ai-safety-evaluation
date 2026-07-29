#!/usr/bin/env python3
"""Validate projective claims, including externally anchored prospectivity."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_object(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_bytes(encoded.encode("utf-8"))


def anchored_claim_digest(claim: dict[str, Any]) -> str:
    """Digest the frozen scientific declaration, excluding lifecycle evidence.

    Status and provenance can advance after collection without changing the
    declaration.  Every substantive scope, selection, warrant, and revision
    field remains inside the digest.
    """
    frozen_fields = {
        key: claim[key]
        for key in (
            "schema_version",
            "claim_id",
            "claim_version",
            "declaration",
            "inquiry_use",
            "warrant_plan",
            "revision_rule",
        )
        if key in claim
    }
    return sha256_object(frozen_fields)


def repository_path(raw_path: str) -> tuple[Path | None, str | None]:
    candidate = (ROOT / raw_path).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return None, "path escapes the repository root"
    if candidate == ROOT.resolve():
        return None, "path names the repository root rather than a file"
    return candidate, None


def git_output(*args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ClaimValidationError(detail or f"git {' '.join(args)} failed")
    if binary:
        return result.stdout
    return result.stdout.decode("utf-8").strip()


def git_blob(commit: str, path: str) -> bytes:
    return git_output("show", f"{commit}:{path}", binary=True)  # type: ignore[return-value]


def git_is_ancestor(older: str, newer: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", older, newer],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def json_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise ClaimValidationError("records_pointer must be empty or start with '/'")
    current = document
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            try:
                current = current[int(token)]
            except (ValueError, IndexError) as exc:
                raise ClaimValidationError(
                    f"records_pointer list index {token!r} does not exist"
                ) from exc
        elif isinstance(current, dict) and token in current:
            current = current[token]
        else:
            raise ClaimValidationError(
                f"records_pointer component {token!r} does not exist"
            )
    return current


_MISSING = object()


def field_value(record: Any, field_path: list[str]) -> Any:
    current = record
    for part in field_path:
        if not isinstance(current, dict) or part not in current:
            return _MISSING
        current = current[part]
    return current


def json_equal(left: Any, right: Any) -> bool:
    """Compare JSON values without Python's True == 1 coercion."""
    return json.dumps(left, sort_keys=True, separators=(",", ":")) == json.dumps(
        right, sort_keys=True, separators=(",", ":")
    )


def predicate_matches(record: dict[str, Any], predicate: dict[str, Any]) -> bool:
    observed = field_value(record, predicate["field_path"])
    if observed is _MISSING:
        return False
    operator = predicate["operator"]
    expected = predicate["value"]
    if operator == "equals":
        return json_equal(observed, expected)
    if operator == "not_equals":
        return not json_equal(observed, expected)
    if operator == "in":
        return any(json_equal(observed, candidate) for candidate in expected)
    if operator == "not_in":
        return not any(json_equal(observed, candidate) for candidate in expected)
    raise ClaimValidationError(f"unsupported selection operator {operator!r}")


def evaluate_selection(selection: dict[str, Any], inventory_bytes: bytes) -> list[str]:
    try:
        inventory = json.loads(inventory_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClaimValidationError("target inventory is not valid UTF-8 JSON") from exc
    records = json_pointer(inventory, selection["records_pointer"])
    if not isinstance(records, list):
        raise ClaimValidationError("records_pointer must resolve to a JSON array")

    selected: list[str] = []
    seen_ids: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ClaimValidationError(f"target inventory record {index} is not an object")
        item_id = field_value(record, selection["item_id_path"])
        if not isinstance(item_id, str) or not item_id:
            raise ClaimValidationError(
                f"target inventory record {index} has no non-empty string item ID"
            )
        if item_id in seen_ids:
            raise ClaimValidationError(f"duplicate target inventory item ID {item_id!r}")
        seen_ids.add(item_id)
        included = all(
            predicate_matches(record, predicate)
            for predicate in selection["include_all"]
        )
        excluded = any(
            predicate_matches(record, predicate)
            for predicate in selection["exclude_any"]
        )
        if included and not excluded:
            selected.append(item_id)
    return selected


def claims_from_bytes(data: bytes, source: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(data)
        return list(iter_claims(payload))
    except (UnicodeDecodeError, json.JSONDecodeError, ClaimValidationError) as exc:
        raise ClaimValidationError(f"{source} is not a valid claim JSON file: {exc}") from exc


def committed_proposed_claim_checks(
    claim: dict[str, Any], payload_path: Path | None = None
) -> list[str]:
    """Allow legacy timing only for an unchanged, history-anchored proposal.

    This does not upgrade a proposal to prospective/frozen status. It prevents
    an edited payload from borrowing the self-attested timing and source path of
    a committed proposal, which is the adversarial fixture's exact move.
    """
    claim_id = claim.get("claim_id", "<unknown>")
    expected_digest = anchored_claim_digest(claim)
    provenance = claim.get("provenance", {})
    candidate_paths = list(provenance.get("source_files", []))
    if payload_path is not None:
        candidate_paths.append(str(payload_path))
    for raw_path in candidate_paths:
        path, path_error = repository_path(str(raw_path))
        if path_error or path is None:
            continue
        relative = path.relative_to(ROOT.resolve()).as_posix()
        try:
            history = str(git_output("log", "--format=%H", "--", relative)).splitlines()
            for commit in history:
                candidates = claims_from_bytes(git_blob(commit, relative), relative)
                if any(
                    candidate.get("claim_id") == claim.get("claim_id")
                    and candidate.get("claim_version") == claim.get("claim_version")
                    and anchored_claim_digest(candidate) == expected_digest
                    for candidate in candidates
                ):
                    return []
        except ClaimValidationError:
            continue
    return [
        f"{claim_id}: legacy self-attested timing is valid only for an unchanged "
        "proposed claim anchored in the Git history of a declared source file; "
        "it does not establish prospectivity"
    ]


def external_anchor_checks(claim: dict[str, Any]) -> list[str]:
    claim_id = claim.get("claim_id", "<unknown>")
    declaration = claim.get("declaration", {})
    provenance = claim.get("provenance", {})
    selection = declaration.get("target_selection")
    anchor = provenance.get("repository_anchor")
    if not isinstance(selection, dict) or not isinstance(anchor, dict):
        return []  # The schema gives the more precise missing-field errors.

    errors: list[str] = []
    inventory_path, path_error = repository_path(str(selection["inventory_path"]))
    if path_error:
        errors.append(f"{claim_id}: target inventory {path_error}")
        return errors
    assert inventory_path is not None
    if not inventory_path.is_file():
        errors.append(f"{claim_id}: target inventory does not exist")
        return errors
    inventory_bytes = inventory_path.read_bytes()
    if sha256_bytes(inventory_bytes) != selection["inventory_sha256"]:
        errors.append(f"{claim_id}: target inventory does not match its declared digest")

    try:
        if not git_is_ancestor(anchor["commit"], "HEAD"):
            errors.append(f"{claim_id}: claim anchor is not in the current Git history")
        anchored_inventory = git_blob(anchor["commit"], selection["inventory_path"])
        if sha256_bytes(anchored_inventory) != selection["inventory_sha256"]:
            errors.append(
                f"{claim_id}: target inventory digest was not present at the anchor commit"
            )

        claim_blob = git_blob(anchor["commit"], anchor["claim_path"])
        matches = [
            candidate
            for candidate in claims_from_bytes(claim_blob, anchor["claim_path"])
            if candidate.get("claim_id") == claim.get("claim_id")
            and candidate.get("claim_version") == claim.get("claim_version")
        ]
        if len(matches) != 1:
            errors.append(
                f"{claim_id}: anchor commit must contain exactly one matching claim ID/version"
            )
        else:
            anchored_digest = anchored_claim_digest(matches[0])
            current_digest = anchored_claim_digest(claim)
            if anchor["claim_sha256"] != current_digest:
                errors.append(f"{claim_id}: current claim does not match its declared digest")
            if anchor["claim_sha256"] != anchored_digest:
                errors.append(f"{claim_id}: claim digest was not present at the anchor commit")

        selected = evaluate_selection(selection, inventory_bytes)
        if selected != selection["selected_item_ids"]:
            errors.append(
                f"{claim_id}: selected_item_ids do not equal the executable selection result"
            )

        outcome = anchor.get("first_target_outcome")
        timing = provenance.get("declaration_timing")
        if timing == "repository_anchored_before_target_outcomes":
            if not isinstance(outcome, dict):
                errors.append(
                    f"{claim_id}: before-outcome status requires a first-target-outcome binding"
                )
            else:
                outcome_blob = git_blob(outcome["commit"], outcome["path"])
                if sha256_bytes(outcome_blob) != outcome["sha256"]:
                    errors.append(
                        f"{claim_id}: first target outcome does not match its committed digest"
                    )
                if (
                    not git_is_ancestor(anchor["commit"], outcome["commit"])
                    or anchor["commit"] == outcome["commit"]
                ):
                    errors.append(
                        f"{claim_id}: claim anchor is not a proper ancestor of the first target outcome"
                    )
                if not git_is_ancestor(outcome["commit"], "HEAD"):
                    errors.append(
                        f"{claim_id}: first target outcome is not in the current Git history"
                    )
                try:
                    git_blob(anchor["commit"], outcome["path"])
                except ClaimValidationError:
                    pass
                else:
                    errors.append(
                        f"{claim_id}: target outcome path already existed at the claim anchor"
                    )
                changes = str(
                    git_output(
                        "rev-list",
                        "--reverse",
                        f"{anchor['commit']}..{outcome['commit']}",
                        "--",
                        outcome["path"],
                    )
                ).splitlines()
                if not changes or changes[0] != outcome["commit"]:
                    errors.append(
                        f"{claim_id}: outcome binding is not the first committed change "
                        "to the target-outcome path after the claim anchor"
                    )
    except ClaimValidationError as exc:
        errors.append(f"{claim_id}: repository anchor cannot be verified: {exc}")
    return errors


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


def semantic_checks(
    claim: dict[str, Any], payload_path: Path | None = None
) -> list[str]:
    errors: list[str] = []
    claim_id = claim.get("claim_id", "<unknown>")
    declaration = claim.get("declaration", {})
    inquiry = claim.get("inquiry_use", {})
    warrant = claim.get("warrant_plan", {})
    revision = claim.get("revision_rule", {})
    provenance = claim.get("provenance", {})

    timing = provenance.get("declaration_timing")
    if claim.get("status") == "proposed":
        if timing not in {
            "before_target_outcomes",
            "repository_anchored_target_chronology_not_established",
            "repository_anchored_before_target_outcomes",
        }:
            errors.append(f"{claim_id}: proposed declaration is already post-outcome")
        if timing == "before_target_outcomes":
            errors.extend(committed_proposed_claim_checks(claim, payload_path))
    elif timing not in {
        "repository_anchored_target_chronology_not_established",
        "repository_anchored_before_target_outcomes",
    }:
        errors.append(
            f"{claim_id}: {claim.get('status')} status requires externally anchored chronology"
        )

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

    errors.extend(external_anchor_checks(claim))
    return errors


def validate_payload(
    payload: Any, schema: dict[str, Any], payload_path: Path | None = None
) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    claims = list(iter_claims(payload))
    seen: set[tuple[str, str]] = set()
    for claim in claims:
        identity = (str(claim.get("claim_id")), str(claim.get("claim_version")))
        if identity in seen:
            errors.append(f"{identity[0]}: duplicate claim ID/version {identity[1]}")
        seen.add(identity)
        schema_errors: list[str] = []
        for issue in sorted(validator.iter_errors(claim), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in issue.path) or "<root>"
            schema_errors.append(
                f"{claim.get('claim_id', '<unknown>')}:{location}: {issue.message}"
            )
        errors.extend(schema_errors)
        if not schema_errors:
            errors.extend(semantic_checks(claim, payload_path))
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
        errors = validate_payload(load_json(path), schema, payload_path=path)
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
