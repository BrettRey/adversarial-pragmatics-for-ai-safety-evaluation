#!/usr/bin/env python3
"""Merge local private review decisions into a retained-candidate queue."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = {row["episode_id"]: row for row in read_jsonl(args.candidates.resolve())}
    payload = json.loads(args.decisions.read_text(encoding="utf-8"))
    if payload.get("kind") != "private_repair_episode_review":
        raise SystemExit("not a repair-episode review payload")
    decisions = {row.get("episode_id"): row for row in payload.get("decisions", [])}
    unknown = sorted(set(decisions) - set(candidates))
    if unknown:
        raise SystemExit("unknown episode IDs in decisions: " + ", ".join(unknown))
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    retained: list[dict[str, Any]] = []
    for episode_id, candidate in candidates.items():
        decision = decisions.get(episode_id, {"decision": "unreviewed"})
        row = {
            "episode_id": episode_id,
            "decision": decision.get("decision", "unreviewed"),
            "interpretation_assessment": decision.get("interpretation_assessment", ""),
            "failure_surface": decision.get("failure_surface", ""),
            "privacy_disposition": decision.get("privacy_disposition", ""),
            "notes": decision.get("notes", ""),
        }
        rows.append(row)
        if row["decision"] == "retain":
            retained.append({**candidate, "review_decision": row})
    with (out_dir / "candidate-decisions.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["episode_id", "decision"])
        writer.writeheader()
        writer.writerows(rows)
    write_jsonl(out_dir / "retained-candidates.jsonl", retained)
    print(f"Merged {len(rows)} decisions; retained {len(retained)} candidates in {out_dir}")


if __name__ == "__main__":
    main()
