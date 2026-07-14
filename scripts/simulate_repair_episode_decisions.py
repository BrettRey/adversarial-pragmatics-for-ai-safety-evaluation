#!/usr/bin/env python3
"""Create deterministic synthetic review decisions for workflow testing only."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = read_jsonl(args.candidates.resolve())
    decisions: list[dict[str, str]] = []
    for index, candidate in enumerate(candidates):
        signals = set(candidate.get("retrieval_signals", []))
        if "factual_correction" in signals:
            assessment = "non_pragmatic_capability_or_factual_error"
            surface = "non_pragmatic"
            decision = "reject"
        elif "wrong_file_or_scope" in signals or "not_what_asked" in signals:
            assessment = "clear_model_misinterpretation"
            surface = "action_scope_failure"
            decision = "retain"
        else:
            assessment = "clarification_required"
            surface = "conversational_misunderstanding"
            decision = "needs_followup"
        decisions.append(
            {
                "episode_id": candidate["episode_id"],
                "decision": decision,
                "interpretation_assessment": assessment,
                "failure_surface": surface,
                "privacy_disposition": "needs_manual_review"
                if candidate.get("privacy_flags")
                else "synthetic_or_public_safe",
                "notes": "Synthetic decision for workflow testing only.",
            }
        )
    payload = {
        "schema_version": 1,
        "kind": "private_repair_episode_review",
        "synthetic": True,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "decisions": decisions,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(decisions)} synthetic repair-review decisions to {args.out}")


if __name__ == "__main__":
    main()
