#!/usr/bin/env python3
"""Recompute the content bindings that tie the evidentiary-assurance artifact together.

The matched-case substrate is deliberately hash-bound: bundles commit to the
applicability map, classifier, regime, and record set; the frozen manifest and
reviewer package commit to each bundle and to the hidden reference key. Those
commitments exist so that a key or map cannot be edited after reviewers have
seen the material.

Re-stamping is therefore legitimate only while the set is still pre-review. This
script refuses to run once any genuine reviewer response exists or once the
declared unblinding boundary has passed, so maintaining the fixtures cannot
become a route around the freeze. Version fields are the author's
responsibility; this script only recomputes digests and propagates them.

Usage:
    python3 scripts/stamp_evidentiary_artifacts.py [--check]

With --check the script writes nothing and exits non-zero if any binding is
stale, which makes it usable as a CI guard.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EA = ROOT / "assurance" / "evidentiary"
MATCHED = EA / "matched-cases"
RESPONSES = MATCHED / "responses"


class StampError(RuntimeError):
    pass


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    """The one on-disk form for every artifact file in this tree."""
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_object(value: Any) -> str:
    """Content hash of a JSON value, matching the validator's convention."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class Tree:
    """Holds every artifact file in memory so digests are computed once, in order."""

    def __init__(self) -> None:
        self.files: dict[Path, Any] = {}
        self.changed: list[str] = []

    def load(self, path: Path) -> Any:
        if path not in self.files:
            self.files[path] = read_json(path)
        return self.files[path]

    def digest(self, path: Path) -> str:
        return sha256_bytes(canonical_bytes(self.load(path)))

    def flush(self, check_only: bool) -> list[str]:
        rewritten: list[str] = []
        for path, value in sorted(self.files.items()):
            new = canonical_bytes(value)
            if path.read_bytes() != new:
                rewritten.append(str(path.relative_to(ROOT)))
                if not check_only:
                    path.write_text(new.decode("utf-8"), encoding="utf-8")
        return rewritten


def guard_pre_review(tree: Tree) -> None:
    """Refuse to re-stamp a set that reviewers may already have acted on."""
    if RESPONSES.exists():
        genuine = [
            path
            for path in RESPONSES.glob("*.json")
            if read_json(path).get("response_source") == "genuine_reviewer"
        ]
        if genuine:
            raise StampError(
                f"{len(genuine)} genuine reviewer response(s) exist; re-stamping is "
                "blocked. Publish a new set version instead of mutating this one."
            )
    if (MATCHED / "hidden" / "unblinding-record.json").exists():
        raise StampError("an unblinding record exists; this set is closed to re-stamping")
    package = tree.load(MATCHED / "reviewer-package.json")
    boundary = datetime.fromisoformat(
        package["reference_key_unblinding_not_before"].replace("Z", "+00:00")
    )
    if datetime.now(timezone.utc) >= boundary:
        raise StampError(
            f"the unblinding boundary {package['reference_key_unblinding_not_before']} "
            "has passed; re-stamping is blocked"
        )


def stamp(check_only: bool) -> int:
    tree = Tree()
    guard_pre_review(tree)

    map_path = EA / "applicability-map.json"
    classifier_path = EA / "action-classifier.json"
    regime_path = EA / "authorization-regime.json"
    manifest_path = MATCHED / "case-manifest.json"
    package_path = MATCHED / "reviewer-package.json"
    keys_path = MATCHED / "hidden" / "reference-keys.json"

    applicability = tree.load(map_path)

    # 1. Leaf inputs the map commits to.
    applicability["action_classifier"]["sha256"] = tree.digest(classifier_path)
    applicability["authorization_regime_R"]["sha256"] = tree.digest(regime_path)

    # 2. The map is now final, so every downstream commitment can quote it.
    map_hash = tree.digest(map_path)
    classifier_binding = dict(applicability["action_classifier"])
    regime_binding = dict(applicability["authorization_regime_R"])
    map_binding = {
        "id": applicability["map_id"],
        "version": applicability["map_version"],
        "path": "applicability-map.json",
        "sha256": map_hash,
    }

    # 3. Bundles commit to the map, classifier, regime, and their record set.
    #    Negative fixtures are stamped the same way so that each one still fails
    #    at its designated defect rather than tripping an earlier hash check.
    #    Only digests are propagated, so a deliberately wrong asserted action
    #    class or an over-capturing record set survives untouched.
    manifest = tree.load(manifest_path)
    bundle_hashes: dict[str, str] = {}

    def stamp_bundle(bundle_path: Path) -> str:
        bundle = tree.load(bundle_path)
        bundle["map_binding"] = dict(map_binding)
        bundle["classifier_binding"] = dict(classifier_binding)
        bundle["regime_binding"] = dict(regime_binding)
        record_path = MATCHED / bundle["target_binding"]["path"]
        record_set = tree.load(record_path)
        bundle["target_binding"]["sha256"] = tree.digest(record_path)
        bundle["target_binding"]["action_sha256"] = sha256_object(record_set.get("action"))
        return tree.digest(bundle_path)

    for case in manifest["cases"]:
        bundle_hashes[case["case_id"]] = stamp_bundle(MATCHED / case["bundle"])
    for negative in manifest.get("negative_fixtures", []):
        stamp_bundle(MATCHED / negative["bundle"])

    # 4. Manifest and reviewer package commit to bundles and the hidden key.
    for case in manifest["cases"]:
        case["bundle_sha256"] = bundle_hashes[case["case_id"]]
    manifest["applicability_map_version"] = applicability["map_version"]
    manifest["claim_graph_version"] = applicability["claim_graph_version"]
    manifest["reference_key_binding"]["sha256"] = tree.digest(keys_path)

    package = tree.load(package_path)
    package["map_sha256"] = map_hash
    package["reference_key_commitment"] = dict(manifest["reference_key_binding"])
    package["cases"] = [
        {key: case[key] for key in ("case_id", "bundle", "bundle_sha256")}
        for case in manifest["cases"]
    ]

    # 5. The projective-claim register quotes the map exactly, so the declared
    #    tolerances and reach thresholds travel with the map rather than drifting.
    register = tree.load(EA / "projective-claim-register.json")
    register["applicability_map_binding"] = {
        "path": "applicability-map.json",
        "sha256": map_hash,
    }
    declared = {use["use_id"]: use for use in applicability["declared_uses"]}
    for link in register.get("use_claim_links", []):
        use = declared.get(link["use_id"])
        if use is None:
            raise StampError(
                f"projective-claim register links unknown use {link['use_id']!r}; "
                "add it to the map's declared uses or drop the link"
            )
        for field in (
            "tolerances",
            "minimum_reach_thresholds",
            "required_coverage_tags",
            "required_controlled_pair_ids",
        ):
            link[field] = json.loads(json.dumps(use[field]))

    # 6. Canonicalize every remaining artifact file so the tree has one on-disk form.
    for path in sorted(EA.rglob("*.json")):
        tree.load(path)

    rewritten = tree.flush(check_only)
    if check_only:
        if rewritten:
            print("stale evidentiary bindings or formatting:", file=sys.stderr)
            for name in rewritten:
                print(f"  {name}", file=sys.stderr)
            return 1
        print("evidentiary artifact bindings are current")
        return 0
    if rewritten:
        print(f"restamped {len(rewritten)} file(s):")
        for name in rewritten:
            print(f"  {name}")
    else:
        print("evidentiary artifact bindings were already current")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify bindings without writing; exit non-zero when stale",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return stamp(args.check)
    except StampError as exc:
        print(f"stamp refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
