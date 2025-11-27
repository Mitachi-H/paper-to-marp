#!/usr/bin/env bash
set -euo pipefail

# Docling ベースの Python スクリプトの薄いラッパー。
# 使い方:
#   ./scripts/extract_figures.sh paper.pdf [figures_dir] [meta_dir] [stats.json]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$SCRIPT_DIR/extract_figures.py" "$@"
