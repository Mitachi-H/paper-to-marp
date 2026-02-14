ワークスペース `$ARGUMENTS` からプレゼンテーション（pptx）を生成する。

1. `$ARGUMENTS/content.md` を読む（なければ `/generate-content $ARGUMENTS` を案内）
2. デザイン基準として `academic.css` を読み、
3. `academic.css` のスタイルを **PPTX 用語に翻訳**して適用する
   - テーマ配色: 背景 `#fff`、本文 `#333`、アクセント/ヘッダ `#800000`
   - テーマフォント: 本文/見出しは Noto Sans JP 系、コードは等幅（Source Code Pro 系）
   - スライドマスター: 余白（上広め）・ヘッダ帯（えんじ地+白文字）・フッタページ番号（`n/N`）
   - レイアウトテンプレート: タイトル、セクション、本文、2カラム（図+説明）
   - また、画像のアスペクト比を変更してはいけない。**見切れてしまう場合はアスペクト比を保ったまま小さくすること。**
4. 数式を書く場合は、必ず `scripts/render_equation.py` で TeX 数式を PNG 化して利用する。
   - Write ツールで `.tex` ファイルを作成し、それを引数に渡す。
   - 例:
     1. Write ツールで `$ARGUMENTS/assets/equations/eq_01.tex` を作成
     2. `.venv/bin/python scripts/render_equation.py $ARGUMENTS/assets/equations/eq_01.tex -o $ARGUMENTS/assets/equations/eq_01.png`
5. `$ARGUMENTS/content.md` の内容に忠実に、plugin（document-skills）で `$ARGUMENTS/presentation.pptx` を生成する
6. plugin のレイアウト崩れチェック結果を確認し、問題があれば修正して再生成する
7. 生成物パス・適用したテーマ/フォント/テンプレート・チェック結果・残課題を報告する
