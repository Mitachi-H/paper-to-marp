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


def ensure_content_stub(dst_dir: Path) -> None:
    content_path = dst_dir / "content.md"
    if content_path.exists():
        return
    content_path.write_text(
        dedent(
            """
            # Content Draft

            `/generate-content` 実行後、このファイルにレビュー用の通常 Markdown が出力されます。
            内容レビュー完了後に `/generate-slides` を実行してください。
            """
        ).lstrip(),
        encoding="utf-8",
    )


def render_agent_content(pdf_name: str) -> str:
    return dedent(
        f"""
        # Paper Slide Agent

        このディレクトリの論文 PDF を段階的に整理し、最終的にプレゼン資料 (`pptx`) を生成する。
        プロジェクト全体の規約は `../../CLAUDE.md` を参照。

        ## ワークスペース構成

        | ファイル | 説明 |
        |---|---|
        | `{pdf_name}` | 入力 PDF |
        | `paper_text.txt` | 抽出テキスト（ページ区切り付き） |
        | `figures/` | 抽出された図表 (Figure*.png, Table*.png) |
        | `meta/` | 図表メタデータ JSON |
        | `prompt.md` | `content.md` 生成プロンプト（内容面の指示） |
        | `content.md` | レビュー用の通常 Markdown |
        | `format.md` | （必要に応じた）Marp 書式ルール |
        | `academic.css` | Marp テーマ |
        | `presentation.pptx` | 最終プレゼン資料 |

        ## コンテンツ生成 (Phase 2)

        ユーザーが「この論文の内容を整理して」などと言ったら:

        1. `paper_text.txt` を読み、論文の全体構成・主要貢献・手法・実験結果を把握する。
        2. `figures/` と `meta/` から利用可能な図表を確認する。
        3. 最初に必ずユーザーへ質問する:
            - 背景の深さ（どこから説明するか）
            - 特に強調したいセクション
            - 発表者名・セミナー名
            - （論文内容に応じた具体的な質問）
        4. `prompt.md` の指示に従って `content.md` を生成する。
           - **この段階では Marp 形式を使わない**（front matter, `<div>`, `<!-- _header -->`, `---` 区切りは禁止）。
           - 図は `./figures/<ファイル名>` で参照（実在ファイルのみ使用）。

        ## スライド生成 (Phase 3)

        ユーザーが「レビュー済み内容からスライド化して」と言ったら:

        1. `content.md` を読み、レビュー済みの主張・構成を優先する。
        2. plugin（document-skills）を使って `pptx` を生成する。
        3. レイアウト崩れチェックも同時に行い、結果を報告する。

        Claude Code を使う場合、以下のスラッシュコマンドも利用可能:
        - `/generate-content` — レビュー用 `content.md` を生成
        - `/generate-slides` — plugin（document-skills）で `pptx` を生成

        ## 重要なルール

        - `prompt.md` の内容に従う。変更が必要ならユーザーに確認する。
        - `content.md` は通常 Markdown で作る（Marp 記法を混ぜない）。
        - `/generate-slides` では plugin のチェック結果を必ず共有する。
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
    ensure_content_stub(cwd)
    write_agent_docs(cwd, pdf_path.name)

    print(
        "初期化完了: AGENTS.md, CLAUDE.md, figures/, meta/, academic.css, "
        "prompt.md, format.md, content.md を用意しました。"
    )


if __name__ == "__main__":
    main()
