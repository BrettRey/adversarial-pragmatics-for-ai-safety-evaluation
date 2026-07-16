#!/usr/bin/env python3
"""Read-only Study A gate for a complete stamp-2 candidate.

Passing means the scoped artifacts are ready for an explicit commit and
annotated-tag decision.  This command does not write a manifest, make a commit,
create a tag, distribute a package, or authorize opening returns.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import audit_study_a_judge_condition as judge_audit
import build_study_a_manifest as freeze_manifest


def check_freeze_ready(manifest_path: Path, production_root: Path) -> list[str]:
    errors = freeze_manifest.verify_manifest(
        manifest_path.resolve(),
        production_root.absolute(),
        require_stamp=2,
        allow_legacy_v1=False,
    )
    if not manifest_path.is_file():
        return errors
    try:
        recorded = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return errors
    if recorded.get("manifest_version") != 2:
        errors.append("freeze-ready requires semantic manifest version 2")
        return errors
    if recorded.get("freeze_stamp") != 2:
        errors.append("freeze-ready requires freeze_stamp 2")
    if recorded.get("freeze_status") != "ready_for_tag":
        errors.append("stamp-2 freeze_status must be ready_for_tag")
    if recorded.get("freeze_accomplished") is not False:
        errors.append("stamp-2 candidate must state that no freeze is yet accomplished")
    if recorded.get("open_returns_authorized") is not False:
        errors.append("the manifest must keep open_returns_authorized false")
    if recorded.get("not_yet_frozen") != []:
        errors.append("stamp 2 still contains not_yet_frozen entries")

    expected_audit = judge_audit.canonical_json(judge_audit.build_audit())
    audit_path = judge_audit.AUDIT_PATH
    if not audit_path.is_file():
        errors.append(f"judge condition audit output is missing: {audit_path}")
    elif audit_path.read_text(encoding="utf-8") != expected_audit:
        errors.append("judge condition audit output is stale or changed")
    else:
        payload = json.loads(expected_audit)
        if payload.get("structural_audit", {}).get("status") != "pass":
            errors.append("judge condition structural audit does not pass")
        # Visible-rule mismatches are intentionally not appended: the audit
        # records them as post-output diagnostics, not comparator invalidation.

    errors.extend(freeze_manifest.response_boundary_errors(production_root))
    return list(dict.fromkeys(errors))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=freeze_manifest.DEFAULT_MANIFEST)
    parser.add_argument(
        "--production-root", type=Path, default=freeze_manifest.DEFAULT_PRODUCTION_ROOT
    )
    args = parser.parse_args()
    errors = check_freeze_ready(args.manifest.resolve(), args.production_root.absolute())
    if errors:
        print("Study A is not freeze-ready:")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)
    print(
        "OK: Study A stamp 2 is ready for explicit commit/tag authorization. "
        "No tag was created and returns are not authorized to open."
    )


if __name__ == "__main__":
    main()
