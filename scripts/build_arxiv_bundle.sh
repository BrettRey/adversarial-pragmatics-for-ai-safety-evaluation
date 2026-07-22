#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT/submission/arxiv/build/source"
BUNDLE="$ROOT/submission/arxiv/adversarial-pragmatics-arxiv-source.tar.gz"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/sections" "$OUT_DIR/figures"

cp "$ROOT/adversarial-pragmatics-for-ai-safety-evaluation.tex" \
  "$OUT_DIR/adversarial-pragmatics-for-ai-safety-evaluation.tex"
cp "$ROOT/supplement.tex" "$OUT_DIR/supplement.tex"
cp "$ROOT/.house-style/preamble.tex" "$OUT_DIR/preamble.tex"
cp "$ROOT/references.bib" "$OUT_DIR/references.bib"
cp "$ROOT/references-local.bib" "$OUT_DIR/references-local.bib"
cp "$ROOT"/sections/*.tex "$OUT_DIR/sections/"
cp "$ROOT"/figures/*.pdf "$OUT_DIR/figures/"

# Bundle the fonts at the package top level (NOT a fonts/ subdir) and reference
# them by bare filename with no Path= in the preamble. Top-level + bare filename
# means kpathsea finds the bundled copy in the build CWD; and if arXiv strips the
# uploaded font binaries, the same bare filenames still resolve against TeX Live's
# ebgaramond / inconsolata / charissil. Do not reintroduce Path=fonts/: a bundled
# fonts/ subdir plus Path=fonts/ is what failed on arXiv.
for font in \
  EBGaramond-Regular.otf \
  EBGaramond-Italic.otf \
  EBGaramond-Bold.otf \
  EBGaramond-BoldItalic.otf \
  InconsolataN-Regular.otf \
  InconsolataN-Bold.otf \
  CharisSIL-Regular.ttf \
  CharisSIL-Italic.ttf \
  CharisSIL-Bold.ttf \
  CharisSIL-BoldItalic.ttf
do
  font_path="$(kpsewhich "$font" || true)"
  if [[ -z "$font_path" ]]; then
    echo "Missing font $font; cannot build self-contained bundle." >&2
    exit 1
  fi
  cp "$font_path" "$OUT_DIR/$font"
done

perl -0pi -e 's/\\input\{\.house-style\/preamble\.tex\}/\\input\{preamble.tex\}/g' \
  "$OUT_DIR/adversarial-pragmatics-for-ai-safety-evaluation.tex" "$OUT_DIR/supplement.tex"
perl -0pi -e 's/\\setmainfont\{EB Garamond\}\[\n  Numbers=OldStyle,\n  Ligatures=TeX,\n  BoldFont=\{EB Garamond\},\n\]/\\setmainfont{EBGaramond-Regular.otf}[\n  Numbers=OldStyle,\n  Ligatures=TeX,\n  ItalicFont=EBGaramond-Italic.otf,\n  BoldFont=EBGaramond-Bold.otf,\n  BoldItalicFont=EBGaramond-BoldItalic.otf,\n]/g' \
  "$OUT_DIR/preamble.tex"
perl -0pi -e 's/\\newfontfamily\\ipafont\{Charis SIL\}/\\newfontfamily\\ipafont{CharisSIL-Regular.ttf}[\n  ItalicFont=CharisSIL-Italic.ttf,\n  BoldFont=CharisSIL-Bold.ttf,\n  BoldItalicFont=CharisSIL-BoldItalic.ttf,\n]/g' \
  "$OUT_DIR/preamble.tex"
perl -0pi -e 's/% CJK fallback font \(Japanese \/ Chinese \/ Korean\)\n\\newfontfamily\\cjkfont\{Hiragino Mincho ProN\}\n\\newcommand\{\\cjk\}\[1\]\{\{\\cjkfont #1\}\}/% CJK fallback disabled for the arXiv package; this submission contains no CJK text.\n\\newcommand{\\cjk}[1]{#1}/g' \
  "$OUT_DIR/preamble.tex"
perl -0pi -e 's/\\setmonofont\{Inconsolata\}\[Scale=MatchLowercase\]/\\setmonofont{InconsolataN-Regular.otf}[\n  Scale=MatchLowercase,\n  BoldFont=InconsolataN-Bold.otf,\n]/g' \
  "$OUT_DIR/preamble.tex"
perl -0pi -e 's/\\IfFileExists\{references-standalone\.bib\}\s*\n\s*\{\\addbibresource\{references-standalone\.bib\}\}\s*\n\s*\{\\addbibresource\{references\.bib\}\\IfFileExists\{references-local\.bib\}\{\\addbibresource\{references-local\.bib\}\}\{\}\}/% Bibliography resources are declared explicitly in each arXiv top-level TeX file./g' \
  "$OUT_DIR/preamble.tex"
perl -0pi -e 's/(\\input\{preamble\.tex\}\n)/$1\\addbibresource{references.bib}\n\\addbibresource{references-local.bib}\n/' \
  "$OUT_DIR/adversarial-pragmatics-for-ai-safety-evaluation.tex" "$OUT_DIR/supplement.tex"

cat > "$OUT_DIR/00README.json" <<'JSON'
{
  "spec_version": 1,
  "process": {
    "compiler": "xelatex"
  },
  "texlive_version": 2025,
  "sources": [
    {
      "filename": "adversarial-pragmatics-for-ai-safety-evaluation.tex",
      "usage": "toplevel"
    },
    {
      "filename": "supplement.tex",
      "usage": "toplevel"
    }
  ]
}
JSON

if command -v xattr >/dev/null 2>&1; then
  xattr -cr "$OUT_DIR" 2>/dev/null || true
fi

COPYFILE_DISABLE=1 tar --no-xattrs -C "$OUT_DIR" -czf "$BUNDLE" .

echo "Wrote $BUNDLE"
