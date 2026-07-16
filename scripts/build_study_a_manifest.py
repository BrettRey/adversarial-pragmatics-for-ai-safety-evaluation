#!/usr/bin/env python3
"""Build (or verify) the Study A pre-registration freeze manifest.

Freezing the Study A analysis path means more than a git tag: the tag pins
tracked files, but the point is a tamper-evident record of the exact artifacts
the analysis was pre-committed to *before any external evaluator return is
opened*. This script hashes those artifacts into `benchmark/study-a/FREEZE-
MANIFEST.json`. Re-run with `--verify` to confirm nothing drifted; any change to
a frozen artifact after the freeze is a deviation that belongs in
`benchmark/study-a/revision-ledger.md`, not a silent edit.

Two freeze stamps:
  * Stamp 1 (now): the analysis path — plan, schema, scripts, and the two frozen
    judge comparators. Locks how the data will be analyzed before it exists.
  * Stamp 2 (when real blind packages are built): add the row map, blind-package
    presentation order, and the frozen author snapshot by extending FROZEN_*.

Usage:
  python3 scripts/build_study_a_manifest.py           # write the manifest
  python3 scripts/build_study_a_manifest.py --verify   # check for drift (exit 1 on drift)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "benchmark" / "study-a" / "FREEZE-MANIFEST.json"

# Frozen artifacts, project-root-relative. Stamp 1 (analysis path).
FROZEN_ARTIFACTS = [
    "benchmark/study-a/analysis-plan.md",
    "benchmark/study-a/schema.json",
    "benchmark/study-a/judge-comparators/judge-labels-mistral-7b.csv",
    "benchmark/study-a/judge-comparators/judge-labels-mistral-24b.csv",
    "scripts/run_study_a_judge.py",
    "scripts/analyze_independent_reassessment.py",
    "scripts/ingest_independent_reassessment.py",
    "scripts/build_independent_reassessment.py",
]

# External (non-file) frozen inputs: the two Ollama judge model digests. These
# come from `ollama list`; recorded so the frozen comparators can be regenerated.
FROZEN_MODEL_DIGESTS = {
    "mistral:7b-instruct-v0.3-q4_K_M": "6577803aa9a0",
    "mistral-small:24b-instruct-2501-q4_K_M": "8039dd90c113",
}

JUDGE_RUN_COMMAND = (
    "python3 scripts/run_study_a_judge.py --judge-model <model> "
    "--out benchmark/study-a/judge-comparators/judge-labels-<tag>.csv  "
    "# deterministic: temperature 0, seed 1"
)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_artifacts() -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for rel in FROZEN_ARTIFACTS:
        path = PROJECT_ROOT / rel
        if not path.exists():
            raise SystemExit(f"frozen artifact missing: {rel}")
        out[rel] = {"sha256": sha256_of(path), "bytes": path.stat().st_size}
    return out


def git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def build_manifest() -> dict[str, object]:
    return {
        "study": "A",
        "purpose": "pre-registration freeze of the analysis path before any external return is opened",
        "schema_version": 7,
        "freeze_stamp": 1,
        "git_commit": git_commit(),
        "model_digests": FROZEN_MODEL_DIGESTS,
        "judge_run_command": JUDGE_RUN_COMMAND,
        "artifacts": compute_artifacts(),
        "not_yet_frozen": [
            "row_map (built with real blind packages)",
            "blind-package presentation order (real run)",
            "frozen author snapshot (real run)",
        ],
        "deviations_recorded_in": "benchmark/study-a/revision-ledger.md",
    }


def verify() -> int:
    if not MANIFEST_PATH.exists():
        print(f"no manifest at {MANIFEST_PATH}; run without --verify first")
        return 1
    recorded = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    current = compute_artifacts()
    drift = []
    for rel, meta in recorded.get("artifacts", {}).items():
        cur = current.get(rel)
        if cur is None:
            drift.append(f"  MISSING now: {rel}")
        elif cur["sha256"] != meta["sha256"]:
            drift.append(f"  CHANGED: {rel}\n    frozen {meta['sha256'][:16]} -> now {cur['sha256'][:16]}")
    for rel in current:
        if rel not in recorded.get("artifacts", {}):
            drift.append(f"  NEW (not in frozen manifest): {rel}")
    if drift:
        print("FREEZE DRIFT DETECTED (record deviations in revision-ledger.md):")
        print("\n".join(drift))
        return 1
    print(f"OK: all {len(current)} frozen artifacts match the manifest.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="check for drift instead of writing")
    args = parser.parse_args()
    if args.verify:
        raise SystemExit(verify())
    manifest = build_manifest()
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH.relative_to(PROJECT_ROOT)} "
          f"({len(manifest['artifacts'])} artifacts, commit {manifest['git_commit'][:12]}).")


if __name__ == "__main__":
    main()
