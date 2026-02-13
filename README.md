# 論文スライド化

1 論文 = 1 ディレクトリで、PDF からテキスト・図表を抽出し、Marp スライド (`slide.md`) を作るテンプレートです。

## ディレクトリ構成

- `scripts/` : 共通スクリプト（PDF→TXT、Docling 図抽出、リネーム、初期化）
- `template/` : `prompt.md`（スライド生成プロンプト）と `academic.css`（Marp テーマ）
- `papers/` : 論文ごとのワークスペース

## セットアップ

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

- Docling 初回実行時にレイアウトモデルをダウンロードするため、ネット接続が必要
- （任意）VSCode に [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) をインストール
- （任意）PDF 出力: `npm install -g @marp-team/marp-cli`

## 使い方

### 1. ワークスペース作成（ワンコマンド）

```bash
python scripts/paper_cli.py --pdf ~/Downloads/foo.pdf
```

`papers/<slug>/` に以下を自動生成:

| ファイル | 内容 |
|---|---|
| `paper.pdf` | 元の PDF（コピー） |
| `paper_text.txt` | 全文テキスト（ページ区切り付き UTF-8） |
| `figures/` | `Figure1.png`, `Table1.png`, ...（Docling 抽出） |
| `meta/` | 図表メタデータ JSON |
| `stats.json` | 抽出の実行統計 |
| `prompt.md` | スライド生成プロンプト（テンプレートからコピー、カスタマイズ可） |
| `academic.css` | Marp テーマ |
| `AGENTS.md` | Codex 向け指示(CLAUDE.mdを変えるとsymlinkで勝手に変わる) |
| `CLAUDE.md` | Claude Code 向け指示（`AGENTS.md` と同内容） |

`--image-scale` で図の解像度倍率を変更できる（既定 2.0 ≒ 144 dpi）。

### 2. スライド生成

ワークスペースの `prompt.md` を必要に応じてカスタマイズし、AI エージェントに `slide.md` を生成させる。

### 3. PDF 出力（任意）

```bash
cd papers/<slug>
npx @marp-team/marp-cli slide.md -o slide.pdf --theme academic.css --allow-local-files
```

## スクリプト

| スクリプト | 説明 |
|---|---|
| `paper_cli.py` | ワンコマンドで init → テキスト抽出 → 図抽出 → リネーム |
| `init_paper.py` | ワークスペース初期化 & AGENTS.md とCLAUDE.md 両方を生成 |
| `pdf_to_text.py` | PyMuPDF でページ区切り付きテキスト抽出 |
| `extract_figures.py` | Docling で図表 PNG + メタデータ JSON 出力 |
| `normalize_figures.py` | メタデータからキャプション番号に沿ってリネーム（idempotent） |

## Claude Code

`CLAUDE.md` にプロジェクトコンテキスト、`.claude/commands/` にスラッシュコマンドを定義:

| コマンド | 説明 |
|---|---|
| `/new-paper <PDF>` | ワークスペース作成 |
| `/generate-slides <workspace>` | スライド生成 |
| `/check-slides <workspace>` | フォーマット検証 |
