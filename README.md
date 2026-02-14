# 論文スライド化

学術論文の PDF を、段階的にプレゼン資料（pptx）へ変換するワークフローツールです。
新フローでは、先にレビュー用の通常 Markdown（`content.md`）を確定してから `pptx` を生成します。

## セットアップ

```bash
# Python 依存
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

- Docling 初回実行時にレイアウトモデルをダウンロードするため、ネット接続が必要

## ワークフロー

### 1. 初回セットアップ — `/init-prompt`

`template/prompt.md`（`content.md` 生成用の内容指示テンプレート）を、対象読者・専門分野・発表形式に合わせてカスタマイズする。一度設定すれば以降の全論文に反映される。

### 2. 論文の取り込み — `/new-paper <PDF パス>`

PDF からテキスト・図表を自動抽出し、ワークスペース (`papers/<slug>/`) を作成する。
抽出された図表は自動表示されるので、品質を確認できる。

| ファイル | 内容 |
|---|---|
| `paper.pdf` | 元の PDF（コピー） |
| `paper_text.txt` | 全文テキスト（ページ区切り付き UTF-8） |
| `figures/` | `Figure1.png`, `Table1.png`, ...（Docling 抽出） |
| `meta/` | 図表メタデータ JSON |
| `stats.json` | 抽出の実行統計 |
| `prompt.md` | `content.md` 生成プロンプト（テンプレートからコピー、カスタマイズ可） |
| `content.md` | レビュー用の通常 Markdown（`/generate-content` で生成） |
| `presentation.pptx` | 最終プレゼン資料（`/generate-slides` で生成） |
| `AGENTS.md` | Codex 向け指示 |
| `CLAUDE.md` | Claude Code 向け指示（`AGENTS.md` と同内容を生成） |

### 3. 内容生成 — `/generate-content papers/<slug>`

論文テキストと図表を読み込み、`prompt.md` に従って通常 Markdown の `content.md` を生成する。
この段階では **スライド専用記法（front matter / `<div>` / `<!-- _header -->`）を使わない**。

### 4. 人手レビュー

`content.md` を人間がレビューして、主張・構成・数式説明・実務観点を確定する。

### 5. スライド生成 — `/generate-slides papers/<slug>`

レビュー済み `content.md` をもとに、plugin（document-skills）で `pptx` を生成する。
レイアウト崩れチェックは同時に実行される。

## ディレクトリ構成

```
scripts/           共通スクリプト（paper_cli.py 等）
template/          prompt.md などのテンプレート
papers/            論文ワークスペース（.gitignore で除外）
.claude/commands/  スラッシュコマンド定義
```

| スクリプト | 説明 |
|---|---|
| `paper_cli.py` | ワンコマンドで init → テキスト抽出 → 図抽出 → リネーム |
| `init_paper.py` | ワークスペース初期化 & `AGENTS.md` / `CLAUDE.md` 生成 |
| `pdf_to_text.py` | PyMuPDF でページ区切り付きテキスト抽出 |
| `extract_figures.py` | Docling で図表 PNG + メタデータ JSON 出力 |
| `normalize_figures.py` | メタデータからキャプション番号に沿ってリネーム（idempotent） |

## 依存関係

- **Python 3.10+**: docling, pymupdf
- **Claude Code**: スラッシュコマンドの実行に必要

## ライセンス

このプロジェクトは [GNU Affero General Public License v3.0](./LICENSE) の下で公開されています。
PyMuPDF (AGPL-3.0) に依存するため、プロジェクト全体を AGPL-3.0 としています。

第三者コードの帰属情報は [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md) を参照してください。
