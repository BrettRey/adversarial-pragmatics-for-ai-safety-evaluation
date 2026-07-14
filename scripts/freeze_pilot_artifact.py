#!/usr/bin/env python3
"""Freeze the original pilot labels without treating them as gold labels.

The source pilot bundle is deliberately ignored because it contains raw model
outputs and browser-exported author adjudications. This script creates a
public-safe, label-only snapshot and a manifest that makes later changes
visible. It never changes the source bundle.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "local-pilot-20260630-185417"
RUN_DIR = ROOT / "benchmark" / "results" / RUN_ID
SUMMARY_DIR = ROOT / "benchmark" / "results" / "summaries"
PROVISIONAL_DIR = ROOT / "data" / "provisional"
SNAPSHOT_PATH = PROVISIONAL_DIR / f"{RUN_ID}-provisional-author-labels.csv"
MANIFEST_PATH = PROVISIONAL_DIR / f"{RUN_ID}-freeze-manifest.json"

LABEL_COLUMNS = [
    "task_success",
    "policy_compliance",
    "safety_risk",
    "risk_type",
    "refusal_outcome",
    "failure_attribution",
    "confidence",
]
SNAPSHOT_COLUMNS = [
    "artifact_id",
    "label_provenance",
    "run_id",
    "review_id",
    "item_id",
    "model",
    "pair_id",
    "phenomenon",
    "variant",
    *LABEL_COLUMNS,
    "annotation_round",
]
PUBLIC_FILES = [
    ROOT / "benchmark" / "items" / "seed-items.csv",
    SNAPSHOT_PATH,
    SUMMARY_DIR / f"{RUN_ID}-model-summary.csv",
    SUMMARY_DIR / f"{RUN_ID}-pair-summary.csv",
    SUMMARY_DIR / f"{RUN_ID}-priority-summary.csv",
    SUMMARY_DIR / f"{RUN_ID}-row-evidence.csv",
    SUMMARY_DIR / f"{RUN_ID}-adjudication-readout.md",
]
LOCAL_FILES = [
    RUN_DIR / "outputs.csv",
    RUN_DIR / "adjudication_responses.csv",
    RUN_DIR / "run_metadata.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_count(path: Path) -> int | None:
    if path.suffix != ".csv":
        return None
    with path.open(encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def fingerprint(path: Path, *, relative_to: Path = ROOT) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(relative_to)),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "records": record_count(path),
    }


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_snapshot(path: Path) -> int:
    source = RUN_DIR / "adjudication_responses.csv"
    if not source.exists():
        raise SystemExit(f"missing local author-label source: {source}")
    rows = read_rows(source)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SNAPSHOT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "artifact_id": RUN_ID,
                    "label_provenance": "author_provisional_pre_independent_readjudication",
                    "run_id": row.get("run_id", RUN_ID),
                    "review_id": row.get("review_id", ""),
                    "item_id": row.get("item_id", ""),
                    "model": row.get("model", ""),
                    "pair_id": row.get("pair_id", ""),
                    "phenomenon": row.get("phenomenon", ""),
                    "variant": row.get("variant", ""),
                    **{column: row.get(column, "") for column in LABEL_COLUMNS},
                    "annotation_round": row.get("annotation_round", "author_pilot"),
                }
            )
    return len(rows)


def build_manifest(reason: str) -> dict[str, Any]:
    missing_public = [str(path) for path in PUBLIC_FILES if not path.exists()]
    if missing_public:
        raise SystemExit("missing public freeze inputs: " + ", ".join(missing_public))
    local = [fingerprint(path) for path in LOCAL_FILES if path.exists()]
    return {
        "manifest_version": 1,
        "artifact_id": RUN_ID,
        "status": "frozen_provisional_author_labels",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "label_interpretation": (
            "Historical author adjudications preserved for comparison; not an "
            "independent reference standard or gold labels."
        ),
        "expected": {
            "seed_items": 18,
            "pilot_output_rows": 54,
            "provisional_author_label_rows": 54,
            "models": 3,
        },
        "public_files": [fingerprint(path) for path in PUBLIC_FILES],
        "local_source_fingerprints": local,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="create or intentionally refresh the snapshot and manifest",
    )
    parser.add_argument(
        "--reason",
        default="",
        help="required with --write; records why the historical freeze changed",
    )
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.write:
        if not args.manifest.exists():
            raise SystemExit(
                f"freeze manifest not found: {args.manifest}; run with --write --reason first"
            )
        print(f"Frozen manifest exists: {args.manifest}")
        return
    if not args.reason.strip():
        raise SystemExit("--reason is required with --write")
    rows = write_snapshot(SNAPSHOT_PATH)
    manifest = build_manifest(args.reason.strip())
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {SNAPSHOT_PATH} ({rows} provisional label rows)")
    print(f"Wrote {args.manifest}")


if __name__ == "__main__":
    main()
