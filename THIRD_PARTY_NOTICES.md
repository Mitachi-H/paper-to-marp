# THIRD-PARTY NOTICES

このリポジトリには、第三者コードを改変して利用している箇所があります。

## Docling Figure Export Example (MIT)

- 対象ファイル: `scripts/extract_figures.py`
- 出典:
  - Documentation: https://docling-project.github.io/docling/examples/export_figures/
  - Source repository: https://github.com/docling-project/docling/tree/main/docs/examples
- 著作権表示: Copyright (c) 2024 International Business Machines
- ライセンス: MIT
  - License text source: https://github.com/docling-project/docling/blob/main/LICENSE
- このリポジトリでの主な改変:
  - CLI 引数と実行統計 (`stats.json`) 出力の追加
  - 図表面積フィルタ（`--min-area`, `--soft-area`, `--no-filter`）の追加
  - ファイル命名規則・メタデータ構造の調整
  - エラーハンドリングと警告出力の追加

### MIT License (upstream: docling)

```text
MIT License

Copyright (c) 2024 International Business Machines

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## marp-theme-academic (MIT)

- 対象ファイル: `template/academic.css`
- 出典: https://github.com/kaisugi/marp-theme-academic
- 著作権表示: Copyright (c) 2022 Kaito Sugimoto
- ライセンス: MIT
  - License text source: https://github.com/kaisugi/marp-theme-academic/blob/master/LICENSE
- このリポジトリでの主な改変:
  - フォントサイズ・カラーの調整
  - header スタイルの変更
  - blockquote を脚注として利用するスタイルの追加

### MIT License (upstream: marp-theme-academic)

```text
MIT License

Copyright (c) 2022 Kaito Sugimoto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
