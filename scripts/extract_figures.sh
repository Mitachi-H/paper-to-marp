#!/usr/bin/env bash
set -euo pipefail

# PDF を指定して pdffigures2 で図表を抽出するラッパー。
# 使い方:
#   ./scripts/extract_figures.sh paper.pdf [figures_dir] [meta_dir] [stats.json]
# 例:
#   ./scripts/extract_figures.sh paper.pdf figures meta stats.json

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/file.pdf [figures_dir] [meta_dir] [stats.json]" >&2
  exit 1
fi

PDF_PATH="$1"
FIG_DIR="${2:-figures}"
META_DIR="${3:-meta}"
STATS_FILE="${4:-stats.json}"

if [[ ! -f "$PDF_PATH" ]]; then
  echo "PDF not found: $PDF_PATH" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

JAVA_HOME_DEFAULT="/Library/Java/JavaVirtualMachines/amazon-corretto-11.jdk/Contents/Home"
if [[ -z "${JAVA_HOME:-}" && -d "$JAVA_HOME_DEFAULT" ]]; then
  export JAVA_HOME="$JAVA_HOME_DEFAULT"
fi
if [[ -n "${JAVA_HOME:-}" ]]; then
  export PATH="$JAVA_HOME/bin:$PATH"
fi

# sbt assembly で作る fat jar を優先的に使う
ASSEMBLY_JAR="$ROOT_DIR/pdffigures2/pdffigures2.jar"
LEGACY_ASSEMBLY_JAR="$ROOT_DIR/pdffigures2/target/scala-2.12/pdffigures2-assembly-0.1.0.jar"
PACKAGE_JAR="$ROOT_DIR/pdffigures2/target/scala-2.12/pdffigures2_2.12-0.1.0.jar"

if [[ -f "$ASSEMBLY_JAR" ]]; then
  JAR="$ASSEMBLY_JAR"
elif [[ -f "$LEGACY_ASSEMBLY_JAR" ]]; then
  JAR="$LEGACY_ASSEMBLY_JAR"
else
  if [[ -f "$PACKAGE_JAR" ]]; then
    echo "pdffigures2 の fat jar が見つかりません。" >&2
    echo "pdffigures2_2.12-0.1.0.jar は main と依存を含まないため実行できません。" >&2
  else
    echo "pdffigures2 の jar が見つかりません。" >&2
  fi
  echo "以下のコマンドで fat jar を作成してください:" >&2
  echo "  cd \"$ROOT_DIR/pdffigures2\" && JAVA_HOME=\"$JAVA_HOME_DEFAULT\" PATH=\"\$JAVA_HOME/bin:\$PATH\" sbt -Dsbt.supershell=false \"set Test / skip := true\" assembly" >&2
  exit 1
fi

mkdir -p "$FIG_DIR" "$META_DIR"

FIG_PREFIX="${FIG_DIR%/}/"
META_PREFIX="${META_DIR%/}/"
BASENAME="$(basename "$PDF_PATH")"
BASE_NO_EXT="${BASENAME%.*}"

java -jar "$JAR" \
  "$PDF_PATH" \
  --save-stats "$STATS_FILE" \
  --figure-data-prefix "$META_PREFIX" \
  --figure-prefix "$FIG_PREFIX"

echo "Figures: $FIG_DIR"
echo "Meta:    ${META_PREFIX}${BASE_NO_EXT}.json"
echo "Stats:   $STATS_FILE"
