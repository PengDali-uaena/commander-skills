#!/usr/bin/env bash
# check_assets.sh — 切图闸门入口，逻辑在 check_assets.py（纯 python3，无第三方依赖）。
#   ./check_assets.sh --repo <仓库根> assets.review.tsv
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$here/check_assets.py" "$@"
