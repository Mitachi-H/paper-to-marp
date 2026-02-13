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
    for name in ("academic.css", "prompt.md", "format.md"):
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


def render_agent_content(pdf_name: str) -> str:
    return dedent(
        f"""
        # Paper Slide Agent

        このディレクトリの論文 PDF から Marp (theme: academic) 用の `slide.md` を生成する。
        プロジェクト全体の規約は `../../CLAUDE.md` を参照。

        ## ワークスペース構成

        | ファイル | 説明 |
        |---|---|
        | `{pdf_name}` | 入力 PDF |
        | `paper_text.txt` | 抽出テキスト（ページ区切り付き） |
        | `figures/` | 抽出された図表 (Figure*.png, Table*.png) |
        | `meta/` | 図表メタデータ JSON |
        | `prompt.md` | スライド生成プロンプト（内容面の指示） |
        | `format.md` | Marp 書式ルール（デザイン面の指示） |
        | `academic.css` | Marp テーマ |
        | `slide.md` | 生成するスライド |

        ## スライド生成

        ユーザーが「この論文をスライド化して」などと言ったら:

        1. `paper_text.txt` を読み、論文の全体構成・主要貢献・手法・実験結果を把握する。
        2. `figures/` と `meta/` から利用可能な図表を確認する。
        3. 最初に必ずユーザーへ質問する:
            - 背景の深さ（どこから説明するか）
            - 特に強調したいセクション
            - 発表者名・セミナー名
            - （論文内容に応じた具体的な質問）
        4. `prompt.md`（内容）と `format.md`（書式）の指示を厳守して `slide.md` を生成する。
           - 図は `./figures/<ファイル名>` で参照（実在ファイルのみ使用）。

        Claude Code を使う場合、以下のスラッシュコマンドも利用可能:
        - `/generate-slides` — スライド生成（このタスクと同等）
        - `/check-slides` — 生成後のフォーマット検証

        ## 重要なルール

        - `prompt.md`、`format.md`、`academic.css` の内容に従う。変更が必要ならユーザーに確認する。
        - `<div>` タグ後の空行を忘れない（Marp が markdown を認識するために必須）。
        """
    ).strip() + "\n"


def write_agent_docs(dst_dir: Path, pdf_name: str) -> None:
    content = render_agent_content(pdf_name)
    for name in ("AGENTS.md", "CLAUDE.md"):
        path = dst_dir / name
        if path.exists():
            continue
        path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="論文ワークスペースを初期化します。")
    parser.add_argument("--pdf", type=Path, help="対象の PDF パス（省略時はカレントの単一 PDF）")
    args = parser.parse_args()

    cwd = Path.cwd()
    pdf_path = find_pdf(cwd, args.pdf)

    (cwd / "figures").mkdir(exist_ok=True)
    (cwd / "meta").mkdir(exist_ok=True)

    copy_templates(cwd)
    write_agent_docs(cwd, pdf_path.name)

    print("初期化完了: AGENTS.md, CLAUDE.md, figures/, meta/, academic.css, prompt.md を用意しました。")


if __name__ == "__main__":
    main()
