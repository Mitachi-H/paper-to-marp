# 論文スライド化 仕様書

## 目的と範囲
- 1 論文 = 1 ディレクトリのワークスペースで、PDF からテキストと図表を抽出し、Marp (academic テーマ) 用の `slide.md` を生成する手順を標準化する。
- 本仕様はルート `論文スライド化/` の構成、依存関係、各スクリプトの責務、運用フローを定義する。

## ディレクトリ構成（テンプレート）
- `scripts/` : 共通ツール群
  - `pdf_to_text.py` : PDF→テキスト抽出
  - `extract_figures.py` : Docling で図表を抽出
- `extract_figures.sh` : 上記 Python の薄いラッパー
  - `normalize_figures.py` : 図表ファイル名と meta の整理
  - `init_paper.py` : 論文ワークスペース初期化 & `AGENT.md` 生成
  - `paper_cli.py` : PDF を指定するだけで一連の作業を実行するワンコマンド CLI
- `template/` : `prompt.md`, `academic.css` のテンプレート
- `papers/` : 論文ごとのワークスペースを置く場所
- `ex/` : 動作例（サンプル PDF・抽出結果・スライド例）

## 前提ソフトウェア
- Python 3.10+ / `pip install -r requirements.txt`（Docling, PyMuPDF を含む）
- Docling 初回実行時にレイアウトモデル等をダウンロードするためネット接続が必要
- Marp CLI（必要に応じてスライド PDF を生成する場合）

### 推奨セットアップ手順
- 例:
  0) 通常の `git clone`
  1) `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
  2) Docling モデルの初回ダウンロードのためネット接続を用意
  3) 任意: `npm install -g @marp-team/marp-cli`

## 新規論文ワークスペースの手順
### 最短ワンコマンド
```
python scripts/paper_cli.py --pdf ~/Downloads/<paper>.pdf
```
- `papers/<PDF名から生成した slug>/` を自動で作成し、`paper.pdf` コピー → init → テキスト抽出 → 図抽出（Docling） → リネームまで実行。
- `--image-scale` で Docling が出力する PNG の解像度倍率を変更できる（既定 2.0 ≒ 144dpi）。

### 手動ステップ（必要なら）
1) 箱を作る: `mkdir -p papers/<paper_id> && cp ~/Downloads/<paper>.pdf papers/<paper_id>/paper.pdf`
2) `cd papers/<paper_id> && python ../../scripts/init_paper.py`
3) テキスト・図抽出:  
   - `python ../../scripts/pdf_to_text.py paper.pdf paper_text.txt`  
   - `python ../../scripts/extract_figures.py paper.pdf figures meta stats.json`  
   - （必要なら）`python ../../scripts/normalize_figures.py meta figures`
4) スライド生成: Cursor/Codex で `AGENT.md` を参照し、`prompt.md` に従って `slide.md` を作成。必要なら `marp slide.md -o slide.pdf --theme academic.css`。

## スクリプト仕様
- `scripts/init_paper.py`
  - カレントディレクトリにある単一の PDF（または `--pdf` 指定）を対象。
  - `figures/`, `meta/`, `prompt.md`, `academic.css`, `AGENT.md` を生成。既存ファイルは上書きしない。
- `scripts/pdf_to_text.py`
  - PyMuPDF でページ順にテキストを抽出し、ページ区切りを `-----` と `[PAGE n]` で明示して保存。
- `scripts/extract_figures.py`
  - 引数: `pdf [figures_dir] [meta_dir] [stats_file]`（既定: `figures meta stats.json`）
  - Docling を用いて図表 PNG とメタデータを出力する。`--scale` で解像度倍率を調整。
- `scripts/normalize_figures.py`
  - meta JSON を読み、Figure/Table の番号から `Figure1.png`, `Table2.png` のようにリネーム。重複は `-2` などで解消。
  - meta 内の `renderURL` も新しい相対パスに更新。
- `scripts/paper_cli.py`
  - `--pdf` を指定するだけで init → テキスト抽出 → 図抽出 → リネームまで自動実行。Docling が import できない場合はエラーで案内。

## AGENT.md（各論文ディレクトリに生成）
- 目的: 「初期処理（テキスト化・図抽出・リネーム）」と「スライド生成」の手順をエージェントに指示する。
- 重要ルール:
  - ワークスペース外を触らない。
  - `prompt.md` と `academic.css` を厳守し、`slide.md` は Marp で通る完全な形で更新。
  - 必ずユーザーへのヒアリング（背景の深さなど）を行ってからスライド生成に入る。

## 出力物の期待仕様
- `paper_text.txt` : PDF 全文（ページ区切り付き UTF-8）
- `figures/` : `Figure*.png`, `Table*.png`（Docling 抽出）
- `meta/` : 抽出メタ JSON（`renderURL` はファイル名に合わせた相対パス）
- `stats.json` : Docling 実行統計（所要時間、出力数）
- `slide.md` : Marp 用スライド（生成後にユーザーが確認）
- 任意: `slide.pdf`（Marp CLI で出力）

## 運用上のメモ
- Docling 初回実行時はモデルダウンロードが走るため、ネット接続と多少の時間を確保する。
- `--image-scale` で図の解像度を上げられる。デフォルト 2.0 で十分だが、細部が潰れる場合は 3.0 などに上げる。
- `normalize_figures.py` は Docling 出力でも idempotent。キャプションの番号に揃えたい場合のみ実行すればよい。
