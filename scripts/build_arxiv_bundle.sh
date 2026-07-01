#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT/submission/arxiv/build/source"
BUNDLE="$ROOT/submission/arxiv/adversarial-pragmatics-arxiv-source.tar.gz"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/sections" "$OUT_DIR/figures"

cp "$ROOT/main.tex" "$OUT_DIR/main.tex"
cp "$ROOT/supplement.tex" "$OUT_DIR/supplement.tex"
cp "$ROOT/.house-style/preamble.tex" "$OUT_DIR/preamble.tex"
cp "$ROOT/references.bib" "$OUT_DIR/references.bib"
cp "$ROOT/references-local.bib" "$OUT_DIR/references-local.bib"
cp "$ROOT"/sections/*.tex "$OUT_DIR/sections/"
cp "$ROOT"/figures/*.pdf "$OUT_DIR/figures/"

perl -0pi -e 's/\\input\{\.house-style\/preamble\.tex\}/\\input\{preamble.tex\}/g' \
  "$OUT_DIR/main.tex" "$OUT_DIR/supplement.tex"

tar -C "$OUT_DIR" -czf "$BUNDLE" .

echo "Wrote $BUNDLE"
