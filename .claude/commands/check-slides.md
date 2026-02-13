`$ARGUMENTS/slide.md` の Marp フォーマットを検証する。

チェック項目:
1. front matter (`marp: true`, `theme: academic`, `paginate: true`, `math: katex`)
2. `<div>` タグ直後の空行の有無
3. 通常スライドの `<div style="font-size:0.8em">` ラッパー
4. `![...](./figures/...)` の参照先が `$ARGUMENTS/figures/` に実在するか
5. `<!-- _header: ... -->` の有無とフォーマット
6. スライド数（`---` を数えて 20-40 枚の範囲か）
7. 見出しが `#### **テキスト**` 形式か

結果を OK / WARNING / ERROR で報告し、問題があれば修正するか確認する。
