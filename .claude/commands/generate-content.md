ワークスペース `$ARGUMENTS` からレビュー用の通常 Markdown（`content.md`）を生成する。

1. `$ARGUMENTS/paper_text.txt` を読み論文を理解する（なければ `/new-paper` を案内）
2. `$ARGUMENTS/prompt.md`（内容指示）を読む
3. `$ARGUMENTS/figures/` と `$ARGUMENTS/meta/*.json` から利用可能な図表を把握する
4. ユーザーに質問する（背景の深さ、強調セクション、発表者名、セミナー名など）
5. `prompt.md` に従って `$ARGUMENTS/content.md` を生成する
   - **通常 Markdown で出力する（Marp 記法は使わない）**
   - 図は実在ファイルのみ参照する
6. 要約・使用図表・未確定論点を報告し、人間レビューを依頼する
7. レビュー完了後に `/generate-slides $ARGUMENTS` を案内する
