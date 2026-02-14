# 論文スライド化プロジェクト

学術論文 (PDF) をプレゼン資料 (`pptx`) に変換するワークフローツール。
新フローでは、先にレビュー用の通常 Markdown（`content.md`）を確定してから `pptx` を生成する。

## 3 フェーズ構成

- **Phase 1 (自動処理)**: `paper_cli.py` で PDF → テキスト抽出 → 図表抽出 → リネームまで一括実行
- **Phase 2 (AI 支援)**: `prompt.md` に従いレビュー用の通常 Markdown (`content.md`) を生成
- **Phase 3 (AI 支援)**: レビュー済み `content.md` から plugin（document-skills）で `pptx` を生成（レイアウトチェック込み）

## ディレクトリ構成

```
scripts/           # 共通スクリプト
  paper_cli.py       Phase 1 ワンコマンド CLI
  init_paper.py      ワークスペース初期化 & AGENTS.md 生成
  pdf_to_text.py     PyMuPDF でテキスト抽出
  extract_figures.py Docling で図表抽出
  normalize_figures.py Figure1.png 等にリネーム
template/          # prompt.md のテンプレート
papers/            # 論文ワークスペース（.gitignore で除外）
```

## ペーパーワークスペース (`papers/<slug>/`)

```
paper.pdf       paper_text.txt    figures/    meta/
stats.json      prompt.md         content.md
presentation.pptx    AGENTS.md    CLAUDE.md
```

## セットアップ

```bash
# venv 作成 & 有効化（初回のみ）
python -m venv .venv
source .venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
```

> **注意**: スクリプト実行前に必ず venv が有効化されていること。
> Claude Code からスクリプトを実行する際も `.venv/bin/python` を使う。

## よく使うコマンド

```bash
# 新規論文（Phase 1 一括）
.venv/bin/python scripts/paper_cli.py --pdf ~/Downloads/foo.pdf

# 最終資料は /generate-slides で pptx 生成
```

## スラッシュコマンド

| コマンド | 説明 |
|---|---|
| `/init-prompt` | `template/prompt.md` を用途に合わせてカスタマイズ（初回セットアップ） |
| `/new-paper` | PDF → ワークスペース作成 |
| `/generate-content` | 論文を読みレビュー用 `content.md` を生成 |
| `/generate-slides` | plugin（document-skills）で `pptx` を生成（レイアウトチェック込み） |

## コーディング規約

- `pathlib.Path`、`encoding="utf-8"`、`argparse`、`main()` パターン、型ヒント

## 依存関係

- **Python**: docling (>=2.63.0,<3.0.0), pymupdf
