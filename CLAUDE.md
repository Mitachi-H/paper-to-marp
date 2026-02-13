# 論文スライド化プロジェクト

学術論文 (PDF) を Marp スライド (academic テーマ) に変換するワークフローツール。
スライド生成時は各ワークスペースの `prompt.md`（内容指示）と `format.md`（書式ルール）に従う。

## 2 フェーズ構成

- **Phase 1 (自動処理)**: `paper_cli.py` で PDF → テキスト抽出 → 図表抽出 → リネームまで一括実行
- **Phase 2 (AI 支援)**: `prompt.md` + `format.md` に従い `slide.md` を生成

## ディレクトリ構成

```
scripts/           # 共通スクリプト
  paper_cli.py       Phase 1 ワンコマンド CLI
  init_paper.py      ワークスペース初期化 & AGENT.md 生成
  pdf_to_text.py     PyMuPDF でテキスト抽出
  extract_figures.py Docling で図表抽出
  normalize_figures.py Figure1.png 等にリネーム
template/          # prompt.md, format.md, academic.css のテンプレート
papers/            # 論文ワークスペース（.gitignore で除外）
```

## ペーパーワークスペース (`papers/<slug>/`)

```
paper.pdf       paper_text.txt    figures/    meta/
stats.json      prompt.md         format.md
academic.css    AGENT.md          slide.md       slide.pdf (任意)
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

# PDF 出力（marp-cli）
npx @marp-team/marp-cli slide.md -o slide.pdf --theme academic.css --allow-local-files
```

## スラッシュコマンド

| コマンド | 説明 |
|---|---|
| `/init-prompt` | `template/prompt.md` を用途に合わせてカスタマイズ（初回セットアップ） |
| `/new-paper` | PDF → ワークスペース作成 |
| `/generate-slides` | 論文を読み `slide.md` を生成 |
| `/check-slides` | `slide.md` のフォーマット検証 |

## コーディング規約

- `pathlib.Path`、`encoding="utf-8"`、`argparse`、`main()` パターン、型ヒント

## Marp フォーマットルール

完全な仕様は各ワークスペースの `format.md` を参照。以下は頻出ルール:

1. **`<div>` タグ後の空行は必須** — Marp が内部の markdown を認識するために必要
2. **通常スライドは `<div style="font-size:0.8em">` で囲む**
3. **ヘッダ `<!-- _header: ... -->`** — スライドの主張を文として書く（全角1・半角0.5換算で30以内）
4. **見出し `#### **テキスト**`** — h4 + bold
5. **画像 `![w:600](./figures/Figure1.png)`** — 中央は `![w:1100 center](...)`
6. **左右配置** — `<div style="display: flex; gap:1em">`（内部 div 後にも空行）
7. **数式** — KaTeX。ブロック数式直後に記号・次元の箇条書き
8. **front matter** — `marp: true`, `theme: academic`, `paginate: true`, `math: katex`
9. **セクション区切り** — `<!-- _class: lead -->` + `## タイトル`

## 依存関係

- **Python**: docling (>=2.63.0,<3.0.0), pymupdf
- **Node.js** (任意): @marp-team/marp-cli
