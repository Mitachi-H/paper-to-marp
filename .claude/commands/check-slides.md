`$ARGUMENTS/slide.md` の Marp フォーマットと見切れを検証する。

## Phase 1: 静的チェック

`$ARGUMENTS/slide.md` を読み、以下を検証する:

1. front matter (`marp: true`, `theme: academic`, `paginate: true`, `math: katex`)
2. `<div>` タグ直後の空行の有無
3. 通常スライドの `<div style="font-size:0.8em">` ラッパー
4. `![...](./figures/...)` の参照先が `$ARGUMENTS/figures/` に実在するか
5. `<!-- _header: ... -->` の有無とフォーマット
6. スライド数（`---` を数えて 20-40 枚の範囲か）
7. 見出しが `#### **テキスト**` 形式か
8. **ヘッダー文字数チェック**: `<!-- _header: ... -->` の内容が長すぎないか
   - 全角文字 = 1、半角英数・スペース = 0.5 として換算幅を計算
   - **換算幅 30 を超えたら WARNING** — 見切れる可能性が高い
   - 例（見切れた実例）:
     - "本発表では Kilosort4 のアルゴリズム・シミュレーション・ベンチマーク"
     - "スパイクソーティングは細胞外記録から単一ニューロンの発火時刻を推定す"
     - "Kilosort4 のクラスタリングはモジュラリティ最適化に基づく反復的近傍再"

Phase 1 の結果を OK / WARNING / ERROR で報告する。

## Phase 2: レンダリング目視チェック

Phase 1 完了後、以下の手順で見切れを視覚的に検証する:

1. marp-cli でスライドを PNG に変換する:
   ```
   npx @marp-team/marp-cli $ARGUMENTS/slide.md --images png --theme $ARGUMENTS/academic.css --allow-local-files -o $ARGUMENTS/slide.png
   ```
2. 生成された `$ARGUMENTS/slide.001.png` 〜 を **すべて Read ツールで表示**し、各スライドを目視確認する
3. 以下の観点でチェックする:
   - ヘッダーバーの文字が右端で途切れていないか
   - スライド下端でテキスト・箇条書き・数式・画像が見切れていないか
   - テキストが多すぎてスライドが窮屈になっていないか
4. 問題のあるスライドを番号・原因とともに報告する

## Phase 3: 修正提案

問題があれば、スライドごとに修正案を提示する:
- ヘッダーが長い → 短縮案を提示
- コンテンツ見切れ → スライド分割 or テキスト削減案を提示
ユーザーの確認を得てから `$ARGUMENTS/slide.md` を編集する。
