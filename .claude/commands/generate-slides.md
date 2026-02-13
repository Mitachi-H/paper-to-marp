ワークスペース `$ARGUMENTS` からスライドを生成する。

1. `$ARGUMENTS/paper_text.txt` を読み論文を理解する（なければ `/new-paper` を案内）
2. `$ARGUMENTS/prompt.md`（内容指示）と `$ARGUMENTS/format.md`（書式ルール）を読む
3. `$ARGUMENTS/figures/` と `$ARGUMENTS/meta/*.json` から利用可能な図表を把握する
4. ユーザーに質問する（背景の深さ、強調セクション、発表者名、セミナー名など）
5. `prompt.md` と `format.md` に**完全準拠**して `$ARGUMENTS/slide.md` を生成する
6. スライド枚数と使用図表を報告し、`/check-slides $ARGUMENTS` を案内する
