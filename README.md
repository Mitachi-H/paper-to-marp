# 論文スライド化

学術論文の PDF を、Claude Code のスラッシュコマンドだけで Marp スライドに変換するツールです。

## セットアップ

```bash
# Python 依存
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# PDF 出力用（任意）
npm install -g @marp-team/marp-cli
```

- Docling 初回実行時にレイアウトモデルをダウンロードするため、ネット接続が必要
- VSCode に [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) をインストールすること（プレビュー・PDF 出力に使用）

## ワークフロー

### 1. 初回セットアップ — `/init-prompt`

`template/prompt.md`（スライド生成の内容指示テンプレート）を、対象読者・専門分野・発表形式に合わせてカスタマイズする。一度設定すれば以降の全論文に反映される。

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
| `prompt.md` | スライド生成プロンプト（テンプレートからコピー、カスタマイズ可） |
| `academic.css` | Marp テーマ |
| `AGENTS.md` | Codex 向け指示 |
| `CLAUDE.md` | Claude Code 向け指示（`AGENTS.md` と同内容を生成） |

### 3. スライド生成 — `/generate-slides papers/<slug>`

論文テキストと図表を読み込み、`prompt.md` + `format.md` に従って `slide.md` を生成する。
背景の深さ・強調セクション・発表者名などを対話的に決められる。

### 4. フォーマット検証 — `/check-slides papers/<slug>`

生成された `slide.md` の書式チェックと見切れ検出を行う。

- **静的チェック**: front matter、`<div>` 空行、ヘッダー文字数制限など
- **レンダリング目視**: marp-cli で PNG 出力 → 全スライドを視覚的に確認
- **修正提案**: 見切れ箇所の短縮・分割案を提示し、確認後に自動修正

### 5. PDF 出力（任意）

```bash
cd papers/<slug>
npx @marp-team/marp-cli slide.md -o slide.pdf --theme academic.css --allow-local-files
```

## ディレクトリ構成

```
scripts/           共通スクリプト（paper_cli.py 等）
template/          prompt.md, format.md, academic.css のテンプレート
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
- **Node.js**（任意）: @marp-team/marp-cli
- **Claude Code**: スラッシュコマンドの実行に必要
