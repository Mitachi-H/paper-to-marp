# Marp スライド書式ルール

このファイルは Marp (academic テーマ) のデザイン・フォーマットルールを定義する。
`/generate-slides` では、**レビュー済み `content.md` を入力**としてこのルールに従うこと。
内容面の指示は `prompt.md`（= `content.md` 生成ルール）を参照。

## 0. 前提

- `content.md` が人手レビュー済みであることを前提にする。
- `slide.md` は `content.md` の主張・構成を優先して作る。
- 図参照は `./figures/` の実在ファイルのみ使う。

## 1. 出力形式

- 出力は **Marp 用 markdown ファイル**。そのまま `slide.md` として保存して使える形にする。
- コードブロックやシェル記法では包まない（` ``` ` は使わない）。
- front matter:

```
---
marp: true
theme: academic
paginate: true
math: katex
---
```

## 2. スライドの書式

### タイトルスライド

```markdown
<!-- _class: lead -->

# {{SeminarName}} 深堀り資料

{{PaperTitle}}

<br>

**{{PresenterName}}**
{{Affiliation}}
{{Date}}
```

### 通常スライド

- **全てのスライド内容を `<div style="font-size:0.8em">...</div>` で囲む**
- 先頭行に `<!-- _header: ... -->` でスライドの主張を書く（名詞止め不可、文として成立させる）
  - **文字数制限**: 全角 1・半角 0.5 換算で **30 以内**に収める。超えるとヘッダーバーで見切れる
  - 例: `<!-- _header: 目的：離散トークン制約を排除し思考の探索空間を拡張する -->`
- 見出しは `#### **テキスト**`（h4 + bold）。ヘッダの主張をサポートする内容にする。
- 箇条書きを基本にし、1 スライドのテキスト量を詰め込みすぎない。

```markdown
<!-- _header: 背景：〜〜〜 -->

<div style="font-size:0.8em">

#### **前提：...**

内容...

</div>
```

### セクション区切りスライド

```markdown
<!-- _class: lead -->

## {{セクション名}}

<small>{{必要なら英語サブタイトル}}</small>
```

## 3. 図・表の使い方

- 論文の重要な図・表は、なるべくスライドに取り入れる。
- 図の上または下に、**2–4 行の箇条書きで日本語で説明**する。
- 元論文の Figure / Table 番号を明記する（例: 「_Figure 3 より_」）

### 中央配置

```markdown
![w:1100 center](./figures/Figure1.png)
```

### 左右配置（図 + 説明文）

**重要**: `<div>` タグの後には必ず空行を入れること。空行がないと Marp が markdown として認識しない。

```markdown
<div style="font-size:0.8em">
<div style="display: flex; gap:1em">
<div>

![w:600](./figures/Figure1.png)

</div>
<div>

#### 図の説明

- 要点 1
- 要点 2
- 要点 3

</div>
</div>
</div>
```

## 4. 数式・記号の扱い

- 数式は KaTeX 形式で書く。
  - インライン: `$H_t \in \mathbb{R}^{t \times d}$`
  - ブロック: `$$...$$`
- 各ブロック数式の直後には、**必ず記号と次元を説明する箇条書き**を入れる:

```markdown
$$
H_t = \mathrm{Transformer}(E_t), \qquad
M(x_{t+1} \mid x_{\le t}) = \mathrm{softmax}(W h_t)
$$

- $E_t = [e(x_1), \dots, e(x_t)] \in \mathbb{R}^{t \times d}$：位置 $t$ までのトークン埋め込み
- $H_t \in \mathbb{R}^{t \times d}$：最終層の隠れ状態の列
- $h_t = H_t[t, :] \in \mathbb{R}^{d}$：時刻 $t$ の隠れ状態
- $W \in \mathbb{R}^{V \times d}$：語彙サイズ $V$ の出力線形層
```

- 論文に特有の記号があれば、専用スライドを 1 枚用意して**すべて列挙して定義**する。
- 変分推論・RL などで勾配が複雑な場合、「何に対して勾配を取り、どの項が微分可能/非微分か」を文章＋式で丁寧に説明する。

## 5. ポイント枠（任意）

重要スライドで使えるまとめ枠:

```markdown
<div style="
  border: 2px solid #4A90E2;
  border-radius: 12px;
  padding: 10px;
  margin: 10px 0;
  background-color: #f5faff;
  font-size: 0.9em;
">
<strong>ポイント：</strong><br>
- 要点 1<br>
- 要点 2
</div>
```

## 6. 最重要チェックリスト

1. **`<div>` タグ後の空行** — Marp が markdown を認識するために必須
2. **通常スライドの `<div style="font-size:0.8em">` ラッパー** — タイトル・セクション区切り以外すべて
3. **`<!-- _header: ... -->` は文として** — 名詞止め不可
4. **見出しは `#### **テキスト**`** — h4 + bold
5. **画像参照は実在ファイルのみ** — `./figures/` 内のファイルを確認してから使う
