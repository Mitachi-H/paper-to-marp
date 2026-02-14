"""TeX 数式を画像 (PNG) に変換するスクリプト。"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

try:
    import fitz  # PyMuPDF
except ImportError as exc:
    raise SystemExit("PyMuPDF が必要です。`pip install pymupdf` を実行してください。") from exc


def is_full_tex_document(text: str) -> bool:
    return "\\documentclass" in text and "\\begin{document}" in text and "\\end{document}" in text


def wrap_tex(text: str, inline: bool) -> str:
    body = text.strip()
    if is_full_tex_document(body):
        return body

    if "$" not in body and "\\[" not in body and "\\begin{" not in body:
        body = f"${body}$" if inline else f"\\[\n{body}\n\\]"

    return (
        "\\documentclass[preview,border=2pt]{standalone}\n"
        "\\usepackage{amsmath,amssymb,bm}\n"
        "\\begin{document}\n"
        f"{body}\n"
        "\\end{document}\n"
    )


def compile_pdf(tex_source: str, temp_dir: Path, engine: str) -> Path:
    tex_file = temp_dir / "equation.tex"
    tex_file.write_text(tex_source, encoding="utf-8")

    cmd = [
        engine,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-output-directory",
        str(temp_dir),
        str(tex_file),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise SystemExit(
            f"LaTeX エンジン `{engine}` が見つかりません。TeX をインストールして再実行してください。"
        ) from exc
    except subprocess.CalledProcessError as exc:
        log_path = temp_dir / "equation.log"
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        detail = "\n".join(part for part in (stdout, stderr) if part)
        if detail:
            detail = f"\n\n--- compiler output ---\n{detail[:2000]}"
        raise SystemExit(f"LaTeX のコンパイルに失敗しました: {log_path}{detail}") from exc

    pdf_path = temp_dir / "equation.pdf"
    if not pdf_path.exists():
        raise SystemExit("PDF の生成に失敗しました。")
    return pdf_path


def render_pdf_to_png(pdf_path: Path, output_path: Path, dpi: int) -> None:
    if dpi <= 0:
        raise SystemExit("--dpi は 1 以上を指定してください。")

    scale = dpi / 72.0
    matrix = fitz.Matrix(scale, scale)

    with fitz.open(pdf_path) as doc:
        if len(doc) == 0:
            raise SystemExit("生成 PDF にページがありません。")
        page = doc[0]
        pix = page.get_pixmap(matrix=matrix, alpha=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(output_path)


def load_input_text(tex_file: Path) -> str:
    if not tex_file.exists():
        raise SystemExit(f"入力ファイルが見つかりません: {tex_file}")
    return tex_file.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="TeX 数式を PNG 画像に変換します。")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="出力 PNG パス（例: papers/foo/assets/equations/eq_01.png）",
    )
    parser.add_argument(
        "tex_file",
        type=Path,
        help="入力 .tex ファイルパス（完全な LaTeX 文書でも数式のみでも可）",
    )
    parser.add_argument("--dpi", type=int, default=300, help="出力解像度 (DPI)")
    parser.add_argument(
        "--engine",
        default="pdflatex",
        help="使用する TeX エンジン（例: pdflatex, lualatex, xelatex）",
    )
    parser.add_argument(
        "--inline",
        action="store_true",
        help="数式文字列をインライン数式 ($...$) として扱う",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="一時生成物を ./tmp_tex_render に保存して残す",
    )
    args = parser.parse_args()

    input_text = load_input_text(args.tex_file)
    tex_source = wrap_tex(input_text, inline=args.inline)

    if args.keep_temp:
        temp_dir = Path("tmp_tex_render").resolve()
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = compile_pdf(tex_source, temp_dir, args.engine)
        render_pdf_to_png(pdf_path, args.output, args.dpi)
        print(f"数式画像を出力しました: {args.output}")
        print(f"中間ファイルを保持しました: {temp_dir}")
        return

    with tempfile.TemporaryDirectory(prefix="tex_render_") as temp_str:
        temp_dir = Path(temp_str)
        pdf_path = compile_pdf(tex_source, temp_dir, args.engine)
        render_pdf_to_png(pdf_path, args.output, args.dpi)

    print(f"数式画像を出力しました: {args.output}")


if __name__ == "__main__":
    main()
