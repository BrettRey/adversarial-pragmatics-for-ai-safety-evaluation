#!/usr/bin/env python3
"""Validate Study A's private assignment registry at the identifier level.

The registry is deliberately private and contains only investigator-assigned
keys.  Real names and contact details belong in a separate identity-side file.
Independent-response ingestion imports the validation functions below and
requires an attestation whose digest matches the exact registry bytes. Registry
validation cannot establish that keys denote unique real people, that people
are role-eligible, or that the role pools are disjoint; those claims require a
separate investigator review of the identity-side roster.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


STUDY_ID = "AP-STUDY-A-INDEPENDENT-READJUDICATION"
ATTESTATION_SCHEMA_VERSION = 2
DEFAULT_ROLES = frozenset({"linguistic_task", "policy_safety"})
REGISTRY_FIELDS = ("person_key", "rater_id", "role", "package_id")
SAFE_LOCAL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
OPAQUE_PACKAGE_ID = re.compile(r"^PKG-[A-F0-9]{16}$")


@dataclass(frozen=True)
class Assignment:
    person_key: str
    rater_id: str
    role: str
    package_id: str


@dataclass(frozen=True)
class AssignmentRegistry:
    assignments: tuple[Assignment, ...]
    roles: frozenset[str]

    @property
    def by_rater_id(self) -> dict[str, Assignment]:
        return {assignment.rater_id: assignment for assignment in self.assignments}

    @property
    def counts_by_role(self) -> dict[str, int]:
        return {
            role: sum(assignment.role == role for assignment in self.assignments)
            for role in sorted(self.roles)
        }

    @property
    def package_ids_by_role(self) -> dict[str, list[str]]:
        return {
            role: sorted(
                {
                    assignment.package_id
                    for assignment in self.assignments
                    if assignment.role == role
                }
            )
            for role in sorted(self.roles)
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_assignment_registry(
    path: Path,
    allowed_roles: set[str] | frozenset[str] | None = None,
) -> AssignmentRegistry:
    """Load a strict, identity-minimized registry or raise ``ValueError``."""
    roles = frozenset(DEFAULT_ROLES if allowed_roles is None else allowed_roles)
    if not roles:
        raise ValueError("assignment registry must declare at least one allowed role")
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            header = tuple(reader.fieldnames or ())
            if header != REGISTRY_FIELDS:
                raise ValueError(
                    "assignment registry header must be exactly "
                    + ",".join(REGISTRY_FIELDS)
                )
            source_rows = list(reader)
    except OSError as exc:
        raise ValueError(f"cannot read assignment registry {path}: {exc}") from exc
    if not source_rows:
        raise ValueError("assignment registry has no assignments")

    assignments: list[Assignment] = []
    seen_person_keys: set[str] = set()
    seen_raters: set[str] = set()
    package_role: dict[str, str] = {}
    for row_number, row in enumerate(source_rows, start=2):
        if None in row:
            raise ValueError(
                f"row {row_number}: assignment registry has surplus CSV cells"
            )
        values = {field: str(row.get(field, "")).strip() for field in REGISTRY_FIELDS}
        person_key = values["person_key"]
        rater_id = values["rater_id"]
        role = values["role"]
        package_id = values["package_id"]
        if not SAFE_LOCAL_ID.fullmatch(person_key):
            raise ValueError(f"row {row_number}: invalid private person_key")
        if not SAFE_LOCAL_ID.fullmatch(rater_id):
            raise ValueError(f"row {row_number}: invalid pseudonymous rater_id")
        if role not in roles:
            raise ValueError(f"row {row_number}: unknown role {role!r}")
        if not OPAQUE_PACKAGE_ID.fullmatch(package_id):
            raise ValueError(f"row {row_number}: invalid opaque package_id")
        if person_key in seen_person_keys:
            raise ValueError(
                f"row {row_number}: person_key {person_key!r} has more than one "
                "identifier-level assignment"
            )
        if rater_id in seen_raters:
            raise ValueError(
                f"row {row_number}: rater_id {rater_id!r} is not globally unique"
            )
        prior_role = package_role.setdefault(package_id, role)
        if prior_role != role:
            raise ValueError(
                f"row {row_number}: package_id {package_id!r} is assigned across roles"
            )
        seen_person_keys.add(person_key)
        seen_raters.add(rater_id)
        assignments.append(Assignment(person_key, rater_id, role, package_id))

    present_roles = {assignment.role for assignment in assignments}
    missing_roles = roles - present_roles
    if missing_roles:
        raise ValueError(
            "assignment registry has no assignment for role(s): "
            + ", ".join(sorted(missing_roles))
        )
    registry = AssignmentRegistry(tuple(assignments), roles)
    for role, package_ids in registry.package_ids_by_role.items():
        if len(package_ids) != 1:
            raise ValueError(
                f"role {role!r} must use exactly one attested package_id; got {package_ids!r}"
            )
    return registry


def assignment_attestation(
    registry_path: Path,
    registry: AssignmentRegistry,
    *,
    study_id: str = STUDY_ID,
    validated_at: str | None = None,
) -> dict[str, object]:
    return {
        "attestation_schema_version": ATTESTATION_SCHEMA_VERSION,
        "study_id": study_id,
        "validated_at": validated_at or datetime.now(timezone.utc).isoformat(),
        "registry_sha256": sha256_file(registry_path),
        "assignment_count": len(registry.assignments),
        "counts_by_role": registry.counts_by_role,
        "package_ids_by_role": registry.package_ids_by_role,
        "invariants": {
            "one_assignment_per_person_key_identifier": True,
            "globally_unique_rater_ids": True,
            "person_keys_unique_across_roles": True,
            "one_package_id_per_role": True,
            "package_ids_not_shared_across_roles": True,
        },
    }


def write_assignment_attestation(
    registry_path: Path,
    attestation_path: Path,
    *,
    allowed_roles: set[str] | frozenset[str] | None = None,
    study_id: str = STUDY_ID,
) -> AssignmentRegistry:
    registry = load_assignment_registry(registry_path, allowed_roles)
    payload = assignment_attestation(registry_path, registry, study_id=study_id)
    attestation_path.parent.mkdir(parents=True, exist_ok=True)
    attestation_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return registry


def verify_assignment_attestation(
    registry_path: Path,
    attestation_path: Path,
    *,
    allowed_roles: set[str] | frozenset[str] | None = None,
    study_id: str = STUDY_ID,
) -> AssignmentRegistry:
    registry = load_assignment_registry(registry_path, allowed_roles)
    try:
        payload = json.loads(attestation_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read assignment attestation {attestation_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("assignment attestation must be a JSON object")
    validated_at = payload.get("validated_at")
    if not isinstance(validated_at, str) or not validated_at.strip():
        raise ValueError("assignment attestation is missing validated_at")
    try:
        parsed_timestamp = datetime.fromisoformat(validated_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("assignment attestation has an invalid validated_at") from exc
    if parsed_timestamp.tzinfo is None:
        raise ValueError("assignment attestation validated_at must include a timezone")
    expected = assignment_attestation(
        registry_path,
        registry,
        study_id=study_id,
        validated_at=validated_at,
    )
    for field in (
        "attestation_schema_version",
        "study_id",
        "registry_sha256",
        "assignment_count",
        "counts_by_role",
        "package_ids_by_role",
        "invariants",
    ):
        if payload.get(field) != expected[field]:
            raise ValueError(f"assignment attestation mismatch in {field}")
    return registry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--attestation", required=True, type=Path)
    parser.add_argument(
        "--write",
        action="store_true",
        help="write a new attestation; without this flag, verify the existing attestation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        if args.write:
            registry = write_assignment_attestation(args.registry, args.attestation)
            action = "wrote"
        else:
            registry = verify_assignment_attestation(args.registry, args.attestation)
            action = "verified"
    except ValueError as exc:
        raise SystemExit(f"assignment validation failed: {exc}") from exc
    print(
        f"{action} identifier-level assignment attestation for "
        f"{len(registry.assignments)} assignment(s): {args.attestation}"
    )


if __name__ == "__main__":
    main()
