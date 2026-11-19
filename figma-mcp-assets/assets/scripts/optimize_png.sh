#!/usr/bin/env bash
# 对 PNG 做 oxipng 无损压缩；若压缩后更大则保留原文件。
set -euo pipefail

if ! command -v oxipng >/dev/null 2>&1; then
  echo "error: oxipng not found. Install with: brew install oxipng" >&2
  exit 1
fi

optimize_one() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo "skip (missing): $file" >&2
    return 0
  fi
  local before after tmp
  before=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
  tmp="${file}.oxipng.tmp"
  cp "$file" "$tmp"
  oxipng -o 4 --strip safe -q "$tmp"
  after=$(stat -f%z "$tmp" 2>/dev/null || stat -c%s "$tmp")
  if [[ "$after" -le "$before" ]]; then
    mv "$tmp" "$file"
    echo "ok: $file ${before} -> ${after} bytes"
  else
    rm -f "$tmp"
    echo "keep: $file (oxipng would grow ${before} -> ${after})"
  fi
}

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <file.png|directory>" >&2
  exit 1
fi

for target in "$@"; do
  if [[ -d "$target" ]]; then
    while IFS= read -r -d '' f; do
      optimize_one "$f"
    done < <(find "$target" -maxdepth 1 -name '*.png' -print0)
  elif [[ -f "$target" ]]; then
    case "$target" in
      *.png) optimize_one "$target" ;;
      *) echo "skip (not png): $target" >&2 ;;
    esac
  else
    echo "skip: $target" >&2
  fi
done
