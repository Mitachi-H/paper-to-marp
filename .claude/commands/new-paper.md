.venvを起動し、`python scripts/paper_cli.py --pdf $ARGUMENTS` を実行する。

完了後:
1. ワークスペースのパス・抽出テキスト行数・図表数を報告する
2. `figures/` 内の画像を**すべて Read ツールで表示**し、抽出が正しいかユーザーに確認を求める
3. 問題があれば `--image-scale` の調整や再抽出を提案する
4. 確認 OK なら `/generate-slides papers/<slug>` を案内する
