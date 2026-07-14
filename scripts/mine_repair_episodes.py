#!/usr/bin/env python3
"""Mine likely repair episodes from a local normalized conversation JSONL file.

The output is a private discovery queue, not a labeled corpus. Correction-like
turns are retrieval signals only. This script never uploads text or calls an
external API.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "data" / "fixtures"
PRIVATE_DIR = ROOT / "private"

SIGNALS: list[tuple[str, re.Pattern[str]]] = [
    ("i_mean", re.compile(r"\bi\s+mean\b", re.I)),
    ("not_x_y", re.compile(r"\bnot\s+[^,.]{1,70},\s*(?:but\s+)?[^,.]{1,90}", re.I)),
    ("not_what_asked", re.compile(r"\b(?:that|this)\s+(?:is|was)\s+not\s+what\s+i\s+asked\b", re.I)),
    ("misunderstood", re.compile(r"\b(?:you\s+)?misunderstood\b", re.I)),
    ("other_reference", re.compile(r"\b(?:no,?\s+)?the\s+other\b", re.I)),
    ("continue_or_resume", re.compile(r"\b(?:continue|resume)\b", re.I)),
    ("you_missed", re.compile(r"\byou\s+missed\b", re.I)),
    ("this_is_about", re.compile(r"\bthis\s+is\s+about\b", re.I)),
    ("relative_reference", re.compile(r"\b(?:the\s+previous|the\s+one\s+above|the\s+last\s+one)\b", re.I)),
    ("wrong_file_or_scope", re.compile(r"\b(?:wrong\s+file|didn'?t\s+ask|do\s+not\s+edit|instead\s+of\s+explaining|changed\s+the)\b", re.I)),
    ("factual_correction", re.compile(r"\b(?:factually\s+(?:incorrect|wrong)|that(?:'s|\s+is)\s+incorrect)\b", re.I)),
]
PRIVACY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("email_like", re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")),
    ("phone_like", re.compile(r"\b(?:\+?\d{1,2}[ .-]?)?(?:\(?\d{3}\)?[ .-]?)\d{3}[ .-]\d{4}\b")),
    ("url", re.compile(r"https?://\S+", re.I)),
    ("credential_word", re.compile(r"\b(?:password|api[_ -]?key|access[_ -]?token|secret)\b", re.I)),
    ("local_path", re.compile(r"(?:/Users/|[A-Z]:\\\\|~/(?:Documents|Downloads)/)")),
]
THIRD_PARTY_PATTERN = re.compile(r"\b(?:from:|to:|subject:|client|student|colleague|employee|customer)\b", re.I)


def truncate(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            required = ["conversation_id", "turn_index", "role", "content"]
            missing = [field for field in required if field not in row]
            if missing:
                raise SystemExit(f"{path}:{line_number}: missing fields: {', '.join(missing)}")
            if not isinstance(row["content"], str):
                raise SystemExit(f"{path}:{line_number}: content must be a string")
            rows.append(row)
    return rows


def repair_signals(text: str, preceding_response: str) -> list[str]:
    found = [name for name, pattern in SIGNALS if pattern.search(text)]
    if len(text.split()) <= 28 and len(preceding_response.split()) >= 60:
        found.append("short_turn_after_long_response")
    return sorted(set(found))


def risk_flags(text: str) -> list[str]:
    flags = [name for name, pattern in PRIVACY_PATTERNS if pattern.search(text)]
    if THIRD_PARTY_PATTERN.search(text):
        flags.append("possible_third_party_content")
    if len(text) > 5000:
        flags.append("long_context")
    return sorted(set(flags))


def prior_index(turns: list[dict[str, Any]], start: int, role: str) -> int | None:
    for index in range(start - 1, -1, -1):
        if turns[index].get("role") == role:
            return index
    return None


def opaque(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length].upper()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_provenance(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        fields = ["episode_id", "source_ref", "source", "conversation_id", "turn_index", "input_path"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--source", required=True, help="local source label, e.g. chatgpt-export")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--context-turns", type=int, default=2)
    parser.add_argument("--max-chars", type=int, default=1400)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input.resolve()
    out_dir = args.out_dir.resolve()
    if args.context_turns < 0 or args.max_chars < 100:
        raise SystemExit("--context-turns must be nonnegative and --max-chars must be at least 100")
    if out_dir.exists() and any(out_dir.iterdir()):
        if not args.overwrite:
            raise SystemExit(f"output directory exists: {out_dir}; pass --overwrite")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    records = read_jsonl(input_path)
    conversations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        conversations[str(row["conversation_id"])].append(row)
    candidates: list[dict[str, Any]] = []
    provenance: list[dict[str, str]] = []
    for conversation_id, turns in sorted(conversations.items()):
        turns.sort(key=lambda row: int(row["turn_index"]))
        for index, repair in enumerate(turns):
            if repair.get("role") != "user":
                continue
            response_index = prior_index(turns, index, "assistant")
            if response_index is None:
                continue
            target_index = prior_index(turns, response_index, "user")
            if target_index is None:
                continue
            response = str(turns[response_index]["content"])
            repair_text = str(repair["content"])
            signals = repair_signals(repair_text, response)
            if not signals:
                continue
            context_start = max(0, target_index - args.context_turns)
            context = [
                {
                    "role": str(turn["role"]),
                    "content": truncate(str(turn["content"]), args.max_chars),
                }
                for turn in turns[context_start:target_index]
                if turn.get("role") != "system"
            ]
            source_ref = "SRC-" + opaque(f"{args.source}|{conversation_id}")
            episode_id = "DISC-" + opaque(
                f"{args.source}|{conversation_id}|{repair.get('turn_index')}"
            )
            combined = "\n".join(
                [entry["content"] for entry in context]
                + [str(turns[target_index]["content"]), response, repair_text]
            )
            candidates.append(
                {
                    "episode_id": episode_id,
                    "source_ref": source_ref,
                    "retrieval_signals": signals,
                    "privacy_flags": risk_flags(combined),
                    "preceding_context": context,
                    "target_prompt": truncate(str(turns[target_index]["content"]), args.max_chars),
                    "model_interpretation_or_action": truncate(response, args.max_chars),
                    "repair_turn": truncate(repair_text, args.max_chars),
                    "discovery_note": (
                        "Candidate retrieved from a correction-like turn. It is not a label, "
                        "a representative observation, or evidence of a uniquely required interpretation."
                    ),
                }
            )
            provenance.append(
                {
                    "episode_id": episode_id,
                    "source_ref": source_ref,
                    "source": args.source,
                    "conversation_id": conversation_id,
                    "turn_index": str(repair.get("turn_index", "")),
                    "input_path": str(input_path),
                }
            )
    write_jsonl(out_dir / "candidates.jsonl", candidates)
    write_provenance(out_dir / "provenance-index.csv", provenance)
    summary = {
        "source": args.source,
        "input_records": len(records),
        "candidate_episodes": len(candidates),
        "retrieval_signal_counts": dict(
            Counter(signal for candidate in candidates for signal in candidate["retrieval_signals"])
        ),
        "privacy_flag_counts": dict(
            Counter(flag for candidate in candidates for flag in candidate["privacy_flags"])
        ),
        "local_only": True,
        "external_api_calls": False,
        "interpretation": "retrieval queue only; manual review required",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# Private Repair-Episode Discovery Run\n\n"
        "This run contains raw bounded context from a local input source and must remain "
        "private. `candidates.jsonl` is a retrieval queue, not a labeled corpus. Open the "
        "offline review page generated by `build_repair_episode_review.py` before retaining "
        "or deriving any case.\n",
        encoding="utf-8",
    )
    if not (input_path.is_relative_to(PRIVATE_DIR) or input_path.is_relative_to(FIXTURES_DIR)):
        print("WARNING: input is outside private/ and data/fixtures/; confirm it is safe for local handling.")
    print(f"Mined {len(candidates)} candidate repair episodes into {out_dir}")


if __name__ == "__main__":
    main()
