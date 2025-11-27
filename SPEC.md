# 論文スライド化 仕様書

## 目的と範囲
- 1 論文 = 1 ディレクトリのワークスペースで、PDF からテキストと図表を抽出し、Marp (academic テーマ) 用の `slide.md` を生成する手順を標準化する。
- 本仕様はルート `論文スライド化/` の構成、依存関係、各スクリプトの責務、運用フローを定義する。

## ディレクトリ構成（テンプレート）
- `scripts/` : 共通ツール群
  - `pdf_to_text.py` : PDF→テキスト抽出
  - `extract_figures.sh` : pdffigures2 ラッパー
  - `normalize_figures.py` : 図表ファイル名と meta の整理
  - `init_paper.py` : 論文ワークスペース初期化 & `AGENT.md` 生成
  - `paper_cli.py` : PDF を指定するだけで一連の作業を実行するワンコマンド CLI
- `template/` : `prompt.md`, `academic.css` のテンプレート
- `pdffigures2/` : 図抽出エンジン（sbt で jar をビルド、git submodule）
- `papers/` : 論文ごとのワークスペースを置く場所
- `ex/` : 動作例（サンプル PDF・抽出結果・スライド例）

## 前提ソフトウェア
- Java 11 (Amazon Corretto 11 推奨)  
  例: `export JAVA_HOME=/Library/Java/JavaVirtualMachines/amazon-corretto-11.jdk/Contents/Home`
- sbt (Scala 2.12 系を扱えるもの)
- Python 3.10+ / `pip install pymupdf`（`paper_cli` でも必須）
- Marp CLI（必要に応じてスライド PDF を生成する場合）

### 推奨セットアップ手順
- macOS 例:
  0) `git submodule update --init --recursive`（または `git clone --recursive ...`）
  1) `brew install --cask corretto11` → `export JAVA_HOME=.../corretto-11.jdk/Contents/Home`
  2) `brew install sbt`
  3) `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
  4) `cd pdffigures2 && JAVA_HOME=... sbt -Dsbt.supershell=false "set Test / skip := true" package`
  5) 任意: `npm install -g @marp-team/marp-cli`

## ビルド済み jar の用意
```
cd pdffigures2
JAVA_HOME=/Library/Java/JavaVirtualMachines/amazon-corretto-11.jdk/Contents/Home \
PATH="$JAVA_HOME/bin:$PATH" \
sbt -Dsbt.supershell=false "set Test / skip := true" package
# 生成物: pdffigures2/target/scala-2.12/pdffigures2_2.12-0.1.0.jar
```

## 新規論文ワークスペースの手順
### 最短ワンコマンド
```
python scripts/paper_cli.py --pdf ~/Downloads/<paper>.pdf
```
- `papers/<PDF名から生成した slug>/` を自動で作成し、`paper.pdf` コピー → init → テキスト抽出 → 図抽出 → リネームまで実行。

### 手動ステップ（必要なら）
1) 箱を作る: `mkdir -p papers/<paper_id> && cp ~/Downloads/<paper>.pdf papers/<paper_id>/paper.pdf`
2) `cd papers/<paper_id> && python ../../scripts/init_paper.py`
3) テキスト・図抽出:  
   - `python ../../scripts/pdf_to_text.py paper.pdf paper_text.txt`  
   - `../../scripts/extract_figures.sh paper.pdf figures meta stats.json`  
   - `python ../../scripts/normalize_figures.py meta figures`
4) スライド生成: Cursor/Codex で `AGENT.md` を参照し、`prompt.md` に従って `slide.md` を作成。必要なら `marp slide.md -o slide.pdf --theme academic.css`。

## スクリプト仕様
- `scripts/init_paper.py`
  - カレントディレクトリにある単一の PDF（または `--pdf` 指定）を対象。
  - `figures/`, `meta/`, `prompt.md`, `academic.css`, `AGENT.md` を生成。既存ファイルは上書きしない。
- `scripts/pdf_to_text.py`
  - PyMuPDF でページ順にテキストを抽出し、ページ区切りを `-----` と `[PAGE n]` で明示して保存。
- `scripts/extract_figures.sh`
  - 引数: `pdf [figures_dir] [meta_dir] [stats_file]`（既定: `figures meta stats.json`）
  - `pdffigures2_2.12-0.1.0.jar` を用いて画像と meta JSON を出力。
- `scripts/normalize_figures.py`
  - meta JSON を読み、Figure/Table の番号から `Figure1.png`, `Table2.png` のようにリネーム。重複は `-2` などで解消。
  - meta 内の `renderURL` も新しい相対パスに更新。

## AGENT.md（各論文ディレクトリに生成）
- 目的: 「初期処理（テキスト化・図抽出・リネーム）」と「スライド生成」の手順をエージェントに指示する。
- 重要ルール:
  - ワークスペース外を触らない。
  - `prompt.md` と `academic.css` を厳守し、`slide.md` は Marp で通る完全な形で更新。
  - 必ずユーザーへのヒアリング（背景の深さなど）を行ってからスライド生成に入る。

## 出力物の期待仕様
- `paper_text.txt` : PDF 全文（ページ区切り付き UTF-8）
- `figures/` : `Figure*.png`, `Table*.png`（pdffigures2 抽出）
- `meta/` : 抽出メタ JSON（`renderURL` はリネーム後パス）
- `stats.json` : pdffigures2 実行統計
- `slide.md` : Marp 用スライド（生成後にユーザーが確認）
- 任意: `slide.pdf`（Marp CLI で出力）

## 運用上のメモ
- Java バージョンを切り替えずに sbt を実行するとコンパイルエラーになる場合があるため、上記の Corretto 11 を明示する。
- `prompt.md` は論文ごとに微調整してもよいが、構成・禁止事項（コードブロックで囲まない等）は維持する。
- 既存 `ex/` はサンプルとして残し、新規作業は必ず `papers/` 配下で行う。***
