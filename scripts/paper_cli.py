"""1 コマンドで論文ワークスペースを準備・抽出する CLI。"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
PAPERS = ROOT / "papers"
DEFAULT_IMAGE_SCALE = 2.0


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def slugify(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", name).strip("-")
    return slug or "paper"


def ensure_docling_available() -> None:
    try:
        import docling  # noqa: F401
    except ImportError:
        raise SystemExit(
            "Docling が見つかりません。`pip install -r requirements.txt` を実行してください。"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="論文ワークスペースを1コマンドで準備する。")
    parser.add_argument("--pdf", required=True, type=Path, help="入力 PDF パス")
    parser.add_argument("--skip-text", action="store_true", help="テキスト抽出をスキップ")
    parser.add_argument("--skip-figures", action="store_true", help="図抽出をスキップ")
    parser.add_argument("--skip-normalize", action="store_true", help="図ファイル名リネームをスキップ")
    parser.add_argument(
        "--image-scale",
        type=float,
        default=DEFAULT_IMAGE_SCALE,
        help="Docling で生成する画像解像度スケール（72dpi 基準）",
    )
    parser.add_argument("--no-filter", action="store_true", help="図抽出の面積フィルタを無効化する")
    parser.add_argument("--force-copy", action="store_true", help="既存の paper.pdf を上書きする")
    args = parser.parse_args()

    pdf_src = args.pdf.expanduser().resolve()
    if not pdf_src.exists():
        raise SystemExit(f"PDF が見つかりません: {pdf_src}")

    base_id = slugify(pdf_src.stem)
    dest = PAPERS / base_id
    counter = 2
    while dest.exists() and not args.force_copy and (dest / "paper.pdf").exists():
        dest = PAPERS / f"{base_id}-{counter}"
        counter += 1
    dest.mkdir(parents=True, exist_ok=True)

    pdf_dst = dest / "paper.pdf"
    if pdf_dst.exists() and not args.force_copy:
        print(f"[skip] paper.pdf は既に存在します: {pdf_dst}")
    else:
        shutil.copy(pdf_src, pdf_dst)
        print(f"[copy] {pdf_src} -> {pdf_dst}")

    if not args.skip_figures:
        ensure_docling_available()

    # init: AGENTS.md, prompt/format, figures/meta など
    run([sys.executable, str(SCRIPTS / "init_paper.py"), "--pdf", str(pdf_dst)], cwd=dest)

    if not args.skip_text:
        run([sys.executable, str(SCRIPTS / "pdf_to_text.py"), "paper.pdf", "paper_text.txt"], cwd=dest)

    if not args.skip_figures:
        extract_cmd = [
            sys.executable,
            str(SCRIPTS / "extract_figures.py"),
            "--scale",
            str(args.image_scale),
        ]
        if args.no_filter:
            extract_cmd.append("--no-filter")
        extract_cmd += ["paper.pdf", "figures", "meta", "stats.json"]
        run(extract_cmd, cwd=dest)

    if not args.skip_normalize and not args.skip_figures:
        run([sys.executable, str(SCRIPTS / "normalize_figures.py"), "meta", "figures"], cwd=dest)

    print(f"完了: {dest}")
    print(
        "次のステップ例: /generate-content で content.md を生成し、"
        "人手レビュー後に /generate-slides を実行してください。"
    )


if __name__ == "__main__":
    main()
