"""論文ワークスペースを初期化するスクリプト。"""

from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import dedent
import shutil


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "template"


def find_pdf(cwd: Path, explicit: Path | None) -> Path:
    if explicit:
        pdf = explicit
        if not pdf.exists():
            raise SystemExit(f"PDF が見つかりません: {pdf}")
        return pdf

    pdfs = sorted(cwd.glob("*.pdf"))
    if len(pdfs) == 0:
        raise SystemExit("このディレクトリに PDF がありません。paper.pdf を置いてから実行してください。")
    if len(pdfs) > 1:
        names = "\n  - ".join(p.name for p in pdfs)
        raise SystemExit(f"PDF が複数あります。--pdf で指定してください:\n  - {names}")
    return pdfs[0]


def copy_templates(dst_dir: Path) -> None:
    for name in ("academic.css", "prompt.md"):
        src = TEMPLATE_DIR / name
        dst = dst_dir / name
        if dst.exists():
            continue
        if not src.exists():
            raise SystemExit(f"テンプレートが見つかりません: {src}")
        shutil.copy(src, dst)

    vscode_src = TEMPLATE_DIR / ".vscode"
    vscode_dst = dst_dir / ".vscode"
    if vscode_src.exists() and not vscode_dst.exists():
        shutil.copytree(vscode_src, vscode_dst)


def write_agent(dst_dir: Path, pdf_name: str) -> None:
    agent_path = dst_dir / "AGENT.md"
    if agent_path.exists():
        return

    content = dedent(
        f"""
        # Paper Slide Agent

        このエージェントは、このディレクトリの論文 PDF から Marp (theme: academic) 用の `slide.md` を生成する。

        ## プロジェクト構成

        - 入力 PDF: `{pdf_name}`
        - テキスト: `paper_text.txt`
        - 図: `figures/`
        - メタデータ: `meta/`
        - スライド: `slide.md`
        - プロンプト仕様: `prompt.md`
        - スタイル: `academic.css`
        - 実行統計: `stats.json`

        ## セットアップ

        - Python 仮想環境を用意し、`pip install pymupdf` を実行して `fitz` を利用可能にする。
        - Java 11 (例: Amazon Corretto 11) を利用する。
        - pdffigures2 の jar は `../../pdffigures2/target/scala-2.12/pdffigures2_2.12-0.1.0.jar` を想定。

        ## タスク: 初期処理

        ユーザーが「初期化して」「図を抽出して」と指示したら、次を順に実行する:

        1. `python ../../scripts/pdf_to_text.py "{pdf_name}" paper_text.txt`
        2. `../../scripts/extract_figures.sh "{pdf_name}" figures meta stats.json`
        3. `python ../../scripts/normalize_figures.py meta figures`

        ## タスク: スライド生成

        ユーザーが「この論文をスライド化して」などと言ったら:

        1. `paper_text.txt` を開き、章構成やページ範囲を把握する。
        2. 最初に必ずユーザーへ質問する:
            - 例: 「背景知識はどのあたりから説明しますか？」（`paper_text.txt` 全体をよく読んで、具体的な質問を考えること。）
        3. `prompt.md` の指示を厳守して `slide.md` を生成する。
           - 図は `./figures/<ファイル名>` で埋め込む。

        ## 重要なルール

        - このディレクトリ外のファイルは読み書きしない。
        - `prompt.md` と `academic.css` の内容には従う。変更が必要ならユーザーに確認する。
        """
    ).strip() + "\n"

    agent_path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="論文ワークスペースを初期化します。")
    parser.add_argument("--pdf", type=Path, help="対象の PDF パス（省略時はカレントの単一 PDF）")
    args = parser.parse_args()

    cwd = Path.cwd()
    pdf_path = find_pdf(cwd, args.pdf)

    (cwd / "figures").mkdir(exist_ok=True)
    (cwd / "meta").mkdir(exist_ok=True)

    copy_templates(cwd)
    write_agent(cwd, pdf_path.name)

    print("初期化完了: AGENT.md, figures/, meta/, academic.css, prompt.md を用意しました。")


if __name__ == "__main__":
    main()
