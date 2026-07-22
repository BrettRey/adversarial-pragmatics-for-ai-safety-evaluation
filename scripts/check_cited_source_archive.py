#!/usr/bin/env python3
"""Verify that every source cited by the three papers has an intact local copy."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "notes/cited-source-local-archive.md"
TEX_GLOBS = (
    "adversarial-pragmatics-for-ai-safety-evaluation.tex",
    "sections/*.tex",
    "delegation-assurance.tex",
    "sections-delegation/*.tex",
    "evidentiary-assurance.tex",
    "sections-evidentiary/*.tex",
)
CITE_RE = re.compile(
    r"\\(?:cite|citep|textcite|parencite|citealt|citeauthor|citeyear|autocite)"
    r"(?:\[[^\]]*\]){0,2}\{([^}]+)\}"
)
ROW_RE = re.compile(r"^\| `([^`]+)` \|", re.MULTILINE)
LINK_RE = re.compile(r"\]\((?:<([^>]+)>|([^)]+))\)")
HASH_RE = re.compile(r"`([0-9a-f]{64})`")
COVERAGE_RE = re.compile(r"Coverage: \*\*(\d+)/(\d+) cited sources")


def tex_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in TEX_GLOBS:
        files.update(ROOT.glob(pattern))
    return sorted(files)


def cited_keys() -> set[str]:
    keys: set[str] = set()
    for path in tex_files():
        text = path.read_text(encoding="utf-8")
        for match in CITE_RE.finditer(text):
            keys.update(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def manifest_rows() -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\| `([^`]+)` \|", line)
        if match:
            rows[match.group(1)] = line
    return rows


def local_targets(row: str) -> list[Path]:
    targets: list[Path] = []
    for match in LINK_RE.finditer(row):
        target = match.group(1) or match.group(2)
        if target.startswith("/"):
            targets.append(Path(target))
    return targets


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    manifest_text = MANIFEST.read_text(encoding="utf-8")
    rows = manifest_rows()
    cited = cited_keys()
    problems: list[str] = []

    coverage = COVERAGE_RE.search(manifest_text)
    if not coverage:
        problems.append("manifest coverage declaration is missing")
    else:
        numerator, denominator = (int(value) for value in coverage.groups())
        if numerator != denominator or denominator != len(rows):
            problems.append(
                f"coverage says {numerator}/{denominator}, but inventory has {len(rows)} rows"
            )

    missing_rows = sorted(cited - rows.keys())
    if missing_rows:
        problems.append("cited keys missing from archive: " + ", ".join(missing_rows))

    for key, row in sorted(rows.items()):
        targets = local_targets(row)
        if not targets:
            problems.append(f"{key}: no absolute local-source link")
            continue
        expected_hashes = HASH_RE.findall(row)
        if len(expected_hashes) != len(targets):
            problems.append(
                f"{key}: {len(targets)} local source(s) but "
                f"{len(expected_hashes)} SHA-256 value(s)"
            )
            continue
        for target, expected in zip(targets, expected_hashes, strict=True):
            if "Downloads" in target.parts:
                problems.append(f"{key}: source remains in Downloads: {target}")
            if not target.is_file():
                problems.append(f"{key}: local source is missing or not a file: {target}")
                continue
            actual = sha256(target)
            if actual != expected:
                problems.append(
                    f"{key}: SHA-256 mismatch for {target.name} "
                    f"(manifest {expected}, actual {actual})"
                )

    if problems:
        print("CITED SOURCE ARCHIVE: FAIL")
        for problem in problems:
            print(f"- {problem}")
        return 1

    unused = sorted(rows.keys() - cited)
    print(
        f"CITED SOURCE ARCHIVE: PASS ({len(cited)} cited keys; "
        f"{len(rows)} locally verified inventory rows)"
    )
    if unused:
        print(
            "Inventory rows not currently cited (retained for the three-paper source set): "
            + ", ".join(unused)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
