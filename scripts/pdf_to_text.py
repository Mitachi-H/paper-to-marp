"""PDF からテキストを抽出して 1 ファイルにまとめるスクリプト。"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # 提示をわかりやすく
    raise SystemExit("PyMuPDF が必要です。`pip install pymupdf` を実行してください。") from exc


def extract_text(pdf_path: Path) -> str:
    """PDF 全ページを順に抽出し、ページ区切りを明示した文字列を返す。"""
    doc = fitz.open(pdf_path)
    chunks = []
    for idx, page in enumerate(doc, start=1):
        chunks.append(page.get_text())
        chunks.append("\n\n" + "-" * 80 + f"\n[PAGE {idx}]\n\n")
    return "".join(chunks)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PDF からテキストを抽出して UTF-8 で保存します。",
    )
    parser.add_argument("pdf", type=Path, help="入力 PDF パス")
    parser.add_argument(
        "output",
        type=Path,
        help="出力先テキストファイル（例: paper_text.txt）",
    )
    args = parser.parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"PDF が見つかりません: {args.pdf}")

    text = extract_text(args.pdf)
    args.output.write_text(text, encoding="utf-8")
    print(f"テキストを書き出しました: {args.output}")


if __name__ == "__main__":
    main()
