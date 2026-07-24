#!/usr/bin/env python3
"""Verify that every source cited by the three papers has an intact local copy.

By default this checks the pooled manifest against all three papers' sources,
exactly as before. Pass --paper {ap,delegation,evidentiary} to instead check
one paper's own sources against the manifest rows attributed to that paper
(via the manifest's "Cited by" column) -- the scope a future single-paper repo
would run after a split. Default (no flag) behaviour is unchanged.
"""

from __future__ import annotations

import argparse
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
# Per-paper scopes for --paper. Slugs match the eventual repo split (AP alone;
# DA+EA together) and the load-bearing-claim-audit.csv per-paper file slugs.
PAPER_TEX_GLOBS: dict[str, tuple[str, ...]] = {
    "ap": ("adversarial-pragmatics-for-ai-safety-evaluation.tex", "sections/*.tex"),
    "delegation": ("delegation-assurance.tex", "sections-delegation/*.tex"),
    "evidentiary": ("evidentiary-assurance.tex", "sections-evidentiary/*.tex"),
}
# Labels as they appear in the manifest's "Cited by" column.
PAPER_LABELS: dict[str, str] = {
    "ap": "Adversarial Pragmatics",
    "delegation": "Delegation Assurance",
    "evidentiary": "Evidentiary Assurance",
}
# biblatex provides sentence-initial capitalized forms (\Textcite, \Parencite,
# \Autocite, ...). The command name must therefore accept an optional capital on
# its first letter, or cited sources go undetected and the coverage figure
# silently overstates completeness.
CITE_RE = re.compile(
    r"\\(?:[Cc]ite|[Cc]itep|[Tt]extcite|[Pp]arencite|[Cc]itealt"
    r"|[Cc]iteauthor|[Cc]iteyear|[Aa]utocite)"
    r"(?:\[[^\]]*\]){0,2}\{([^}]+)\}"
)
ROW_RE = re.compile(r"^\| `([^`]+)` \|", re.MULTILINE)
LINK_RE = re.compile(r"\]\((?:<([^>]+)>|([^)]+))\)")
HASH_RE = re.compile(r"`([0-9a-f]{64})`")
COVERAGE_RE = re.compile(r"Coverage: \*\*(\d+)/(\d+) cited sources")


def tex_files(globs: tuple[str, ...] = TEX_GLOBS) -> list[Path]:
    files: set[Path] = set()
    for pattern in globs:
        files.update(ROOT.glob(pattern))
    return sorted(files)


def cited_keys(globs: tuple[str, ...] = TEX_GLOBS) -> set[str]:
    keys: set[str] = set()
    for path in tex_files(globs):
        text = path.read_text(encoding="utf-8")
        for match in CITE_RE.finditer(text):
            keys.update(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def row_cited_by(row: str) -> str:
    """Return the raw "Cited by" cell text for a manifest inventory row."""
    cells = row.split("|")
    return cells[3].strip() if len(cells) > 3 else ""


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


def main(paper: str | None = None) -> int:
    manifest_text = MANIFEST.read_text(encoding="utf-8")
    all_rows = manifest_rows()
    problems: list[str] = []
    label = PAPER_LABELS[paper] if paper else None
    scope_note = f" (paper={paper})" if paper else ""

    if paper:
        # Scoped mode: this paper's own sources against the manifest rows
        # attributed to it. The pooled Coverage: N/N declaration describes the
        # whole 3-paper inventory and isn't decomposed per paper, so it's
        # skipped here rather than compared against a subset count.
        cited = cited_keys(PAPER_TEX_GLOBS[paper])
        rows = {key: row for key, row in all_rows.items() if label in row_cited_by(row)}
    else:
        cited = cited_keys()
        rows = all_rows

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
        print(f"CITED SOURCE ARCHIVE{scope_note}: FAIL")
        for problem in problems:
            print(f"- {problem}")
        return 1

    unused = sorted(rows.keys() - cited)
    print(
        f"CITED SOURCE ARCHIVE{scope_note}: PASS ({len(cited)} cited keys; "
        f"{len(rows)} locally verified inventory rows)"
    )
    if unused:
        print(
            "Inventory rows not currently cited (retained for the three-paper source set): "
            + ", ".join(unused)
        )
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--paper",
        choices=sorted(PAPER_LABELS),
        default=None,
        help=(
            "Restrict the check to one paper's own sources (sections/section "
            "directory) and the manifest rows attributed to it. Omit for "
            "today's default: all three papers against the full manifest."
        ),
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main(parse_args().paper))
