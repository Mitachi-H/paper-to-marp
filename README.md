# 論文スライド化ワークスペース

1 論文 = 1 ディレクトリで、PDF からテキスト・図表を抽出し、Marp スライド (`slide.md`) を作るためのテンプレートです。

## ディレクトリ構成

- `scripts/` : 共通スクリプト（PDF→TXT、Docling 図抽出、リネーム、初期化）
- `template/` : `prompt.md` と `academic.css` のテンプレート
- `papers/` : 論文ごとのワークスペースを置く場所（空の箱）
- `ex/` : サンプル出力（既存の動作例）

## 事前準備

### 環境セットアップ（初回のみ）

1. Python 仮想環境を作り依存を入れる（Docling + PyMuPDF）
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   - Docling 初回実行時にレイアウトモデル等をダウンロードするため、ネット接続が必要。
2. （任意）Marp CLI を入れて PDF 化もしたい場合
   - `npm install -g @marp-team/marp-cli`

## 新しい論文を追加する手順

### 最短ワンコマンド（推奨）

```
python scripts/paper_cli.py --pdf ~/Downloads/foo.pdf
```

- `papers/<PDF名ベースのslug>/` を自動で作成し、`paper.pdf` コピー → `AGENT.md` 生成 → テキスト抽出 → 図抽出（Docling） → リネームまで実行。
- `--image-scale` で出力 PNG の解像度倍率を調整できる（既定 2.0 ≒ 144dpi）。

### 手動でやる場合

1. 論文用ディレクトリを作る  
   `mkdir -p papers/your-paper && cp ~/Downloads/paper.pdf papers/your-paper/`
2. そのディレクトリで初期化  
   `cd papers/your-paper`  
   `python ../../scripts/init_paper.py`
3. PDF からテキストと図を抽出
   - `python ../../scripts/pdf_to_text.py paper.pdf paper_text.txt`
   - `python ../../scripts/extract_figures.py paper.pdf figures meta stats.json`
   - （必要なら）`python ../../scripts/normalize_figures.py meta figures`
4. Cursor/Codex などのエージェントに `AGENT.md` を読ませ、`prompt.md` に従って `slide.md` を生成させる  
   （必要に応じて `marp slide.md -o slide.pdf --theme academic.css`）

## スクリプトメモ

- `scripts/extract_figures.py`: `pdf`, `figures_dir`, `meta_dir`, `stats.json` を引数にとる Docling ベースの図抽出。`--scale` で解像度を指定。
- `scripts/extract_figures.sh`: 上記 Python スクリプトの簡易ラッパー。
- `scripts/normalize_figures.py`: メタデータを見て `Figure1.png`, `Table1.png` のようにリネームし、meta の `renderURL` も更新。
- `scripts/pdf_to_text.py`: PyMuPDF でページ区切り付きテキストを出力。
- `scripts/init_paper.py`: 現在のディレクトリにある単一の PDF を対象に、ワークスペース一式と `AGENT.md` を生成。

## サンプル

`ex/` 以下に NeurIPS 2020 "Can the brain do backpropagation..." の PDF、抽出結果、スライド例が残っています（旧構成）。
