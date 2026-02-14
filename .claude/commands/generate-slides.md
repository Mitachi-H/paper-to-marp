ワークスペース `$ARGUMENTS` からプレゼンテーション（pptx）を生成する。

1. `$ARGUMENTS/content.md` を読む（なければ `/generate-content $ARGUMENTS` を案内）
2. `$ARGUMENTS/paper_text.txt`、`$ARGUMENTS/figures/`、`$ARGUMENTS/meta/*.json` を確認する
3. plugin（document-skills）を使って `$ARGUMENTS/presentation.pptx` を生成する
4. plugin のレイアウト崩れチェック結果を確認し、問題があれば修正して再生成する
5. 生成物パス・チェック結果・残課題を報告する
