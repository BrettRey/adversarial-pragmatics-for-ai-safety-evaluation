#!/usr/bin/env python3
"""Verify the frozen 54-row pilot without altering its source labels."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from freeze_pilot_artifact import (
    LABEL_COLUMNS,
    LOCAL_FILES,
    MANIFEST_PATH,
    PUBLIC_FILES,
    ROOT,
    RUN_DIR,
    RUN_ID,
    SNAPSHOT_PATH,
    sha256,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_manifest(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def verify_fingerprints(manifest: dict, *, local: bool) -> list[str]:
    errors: list[str] = []
    groups = [("public_files", True), ("local_source_fingerprints", local)]
    for key, required in groups:
        for entry in manifest.get(key, []):
            path = ROOT / entry["path"]
            if not path.exists():
                if required:
                    errors.append(f"missing frozen file: {entry['path']}")
                continue
            actual = sha256(path)
            if actual != entry["sha256"]:
                errors.append(f"digest changed: {entry['path']}")
    return errors


def source_integrity() -> list[str]:
    errors: list[str] = []
    seed_path = ROOT / "benchmark" / "items" / "seed-items.csv"
    outputs_path = RUN_DIR / "outputs.csv"
    author_path = RUN_DIR / "adjudication_responses.csv"
    evidence_path = RUN_DIR / "adjudication_row_evidence.csv"
    for path in [seed_path, outputs_path, author_path, evidence_path, SNAPSHOT_PATH]:
        if not path.exists():
            errors.append(f"missing required local source: {path.relative_to(ROOT)}")
    if errors:
        return errors

    seed_rows = read_csv(seed_path)
    output_rows = read_csv(outputs_path)
    author_rows = read_csv(author_path)
    evidence_rows = read_csv(evidence_path)
    snapshot_rows = read_csv(SNAPSHOT_PATH)
    if len(seed_rows) != 18:
        errors.append(f"seed item count is {len(seed_rows)}, expected 18")
    if len(output_rows) != 54:
        errors.append(f"pilot output count is {len(output_rows)}, expected 54")
    if len(author_rows) != 54:
        errors.append(f"author-label count is {len(author_rows)}, expected 54")
    if len(snapshot_rows) != 54:
        errors.append(f"frozen snapshot count is {len(snapshot_rows)}, expected 54")
    if len(evidence_rows) != 54:
        errors.append(f"row-evidence count is {len(evidence_rows)}, expected 54")

    expected_keys = {(row["item_id"], row["model"]) for row in output_rows}
    author_keys = {(row["item_id"], row["model"]) for row in author_rows}
    snapshot_keys = {(row["item_id"], row["model"]) for row in snapshot_rows}
    evidence_keys = {(row["item_id"], row["model"]) for row in evidence_rows}
    if len(expected_keys) != 54:
        errors.append("pilot outputs do not have 54 unique item/model keys")
    for name, keys in [
        ("author labels", author_keys),
        ("frozen snapshot", snapshot_keys),
        ("row evidence", evidence_keys),
    ]:
        if keys != expected_keys:
            errors.append(f"{name} do not cover the same item/model matrix as outputs")
    for index, row in enumerate(author_rows, start=2):
        missing = [field for field in LABEL_COLUMNS if not row.get(field, "").strip()]
        if missing:
            errors.append(
                f"author row {index} {row.get('review_id', '?')} missing labels: {', '.join(missing)}"
            )
        if not row.get("rationale", "").strip():
            errors.append(f"author row {index} {row.get('review_id', '?')} missing rationale")
    return errors


def reproduce_summaries() -> list[str]:
    """Regenerate summaries in a temp copy so the historical run stays untouched."""
    errors: list[str] = []
    script = ROOT / "scripts" / "summarize_adjudication_pilot.py"
    canonical_dir = ROOT / "benchmark" / "results" / "summaries"
    names = [
        f"{RUN_ID}-model-summary.csv",
        f"{RUN_ID}-pair-summary.csv",
        f"{RUN_ID}-priority-summary.csv",
        f"{RUN_ID}-row-evidence.csv",
        f"{RUN_ID}-adjudication-readout.md",
    ]
    with tempfile.TemporaryDirectory(prefix="ap-pilot-repro-") as temp:
        temp_root = Path(temp)
        copy_dir = temp_root / RUN_ID
        shutil.copytree(RUN_DIR, copy_dir)
        summary_dir = temp_root / "summaries"
        completed = subprocess.run(
            [
                sys.executable,
                str(script),
                "--run-dir",
                str(copy_dir),
                "--summary-dir",
                str(summary_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            return ["summary reproduction failed: " + completed.stderr.strip()]
        for name in names:
            generated = summary_dir / name
            canonical = canonical_dir / name
            if not generated.exists() or not canonical.exists():
                errors.append(f"missing generated or canonical summary: {name}")
            elif sha256(generated) != sha256(canonical):
                errors.append(f"reproduced summary differs from canonical: {name}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-reproduction", action="store_true")
    parser.add_argument(
        "--public-only",
        action="store_true",
        help="verify the tracked snapshot only; permits absence of ignored local sources",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"missing freeze manifest: {MANIFEST_PATH}")
    manifest = load_manifest(MANIFEST_PATH)
    errors = verify_fingerprints(manifest, local=not args.public_only)
    if not args.public_only:
        errors.extend(source_integrity())
        if not args.skip_reproduction:
            errors.extend(reproduce_summaries())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    mode = "public snapshot" if args.public_only else "local pilot and public snapshot"
    print(f"ok: frozen {mode} verified for {RUN_ID}")


if __name__ == "__main__":
    main()
