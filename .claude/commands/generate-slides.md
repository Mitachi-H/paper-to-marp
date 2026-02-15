ワークスペース `$ARGUMENTS` からプレゼンテーション（pptx）を生成する。

## 前提環境

不足ツールがあれば以下のコマンドで自動インストールする。(Macで動作確認済み。OSがWindowsの場合は適宜変更すること。)

```bash
# pptx 生成エンジン
which node > /dev/null || brew install node
npm list -g pptxgenjs > /dev/null 2>&1 || npm install -g pptxgenjs

# Visual QA 用（pptx → PDF → JPG）
which soffice > /dev/null || brew install --cask libreoffice
which pdftoppm > /dev/null || brew install poppler

# 数式 PNG 化
which pdflatex > /dev/null || brew install --cask mactex-no-gui
.venv/bin/pip show pymupdf > /dev/null 2>&1 || .venv/bin/pip install pymupdf
```

**NODE_PATH の自動解決**: generate_pptx.js の先頭で `execSync("npm root -g")` を実行し、
グローバルモジュールのパスを `module.paths` に追加する。手動で `NODE_PATH` を設定する必要はない。

## 生成手順

1. `$ARGUMENTS/content.md` を読む（なければ `/generate-content $ARGUMENTS` を案内）
2. デザイン基準として `academic.css` を読み、
3. `academic.css` のスタイルを **PPTX 用語に翻訳**して適用する
   - テーマ配色: 背景 `#fff`、本文 `#333`、アクセント/ヘッダ `#800000`
   - テーマフォント: 本文/見出しは Noto Sans JP 系、コードは等幅（Source Code Pro 系）
   - スライドマスター: 余白（上広め）・ヘッダ帯（えんじ地+白文字）・フッタページ番号（`n/N`）
   - レイアウトテンプレート: タイトル、セクション、本文、2カラム（図+説明）
   - また、画像のアスペクト比を変更してはいけない。**見切れてしまう場合はアスペクト比を保ったまま小さくすること。**
4. 数式は**すべて** `scripts/render_equation.py` で PNG 化して画像として配置する。pptx にテキストとして数式を書いてはいけない。
   - 独立数式（$$...$$）だけでなく、文章中のインライン数式（$d_k$, $O(n^2)$ 等）も PNG 化する。
   - インライン数式は `--inline` フラグを付ける。`--inline` は小さめレンダリング＋**背景透過 PNG** を自動で有効にする。
   - Write ツールで `.tex` ファイルを作成し、それを引数に渡す。
   - 例:
     1. Write ツールで `$ARGUMENTS/assets/equations/eq_01.tex` を作成
     2. `.venv/bin/python scripts/render_equation.py $ARGUMENTS/assets/equations/eq_01.tex -o $ARGUMENTS/assets/equations/eq_01.png`
     3. インラインの場合: `.venv/bin/python scripts/render_equation.py --inline $ARGUMENTS/assets/equations/inline_dk.tex -o $ARGUMENTS/assets/equations/inline_dk.png`
5. `$ARGUMENTS/content.md` の内容に忠実に、plugin（document-skills）で `$ARGUMENTS/presentation.pptx` を生成する
   - フッタのページ番号（`n/N`）は**全スライド生成後に `pres.slides.length` で自動計算**する（ハードコード禁止）。
6. Visual QA を実施し（後述）、問題があれば修正して再生成する
7. 生成物パス・適用したテーマ/フォント/テンプレート・チェック結果・残課題を報告する

## Visual QA パイプライン

pptx 生成後、必ず以下の手順で目視チェックを行う。

### 1. pptx → PDF → JPG 変換

```bash
# QA 出力ディレクトリ作成
mkdir -p $ARGUMENTS/qa

# pptx → PDF（LibreOffice）
soffice --headless --convert-to pdf --outdir $ARGUMENTS/qa $ARGUMENTS/presentation.pptx

# PDF → JPG（全スライド）
pdftoppm -jpeg -r 150 $ARGUMENTS/qa/presentation.pdf $ARGUMENTS/qa/slide
# → slide-01.jpg, slide-02.jpg, ... が生成される
```

### 2. 目視チェック

Read ツールで各スライド画像を読み、以下を確認する。
サブエージェント（Task ツール）は使わず、Read ツールを使って自分で検査すること。
その際、

チェック項目:
- jsで定義したすべての文字が画像内に含まれているかどうか
- 画像と文字の間などに余白が多すぎないか
- 要素の重なり（テキスト同士、テキストと図、テキストと数式画像）
- テキストのはみ出し・切れ
- 余白不足（スライド端から 0.5 インチ未満）
- 要素間の隙間が不均一
- カラムやカードの整列ずれ
- 低コントラスト（淡色背景に淡色テキスト等）
- **インライン数式画像のサイズ・位置ずれ**
- 画像のアスペクト比崩れ
- プレースホルダテキストの残存

### 3. 修正 → 再検証

問題を修正したら、該当スライドのみ再レンダリングして確認:

```bash
# スライド N だけ再レンダリング
pdftoppm -jpeg -r 150 -f N -l N $ARGUMENTS/qa/presentation.pdf $ARGUMENTS/qa/slide-fixed
```

**問題のあるスライド全てについて最低1回の再検証サイクルを完了するまで完了宣言しない。**
