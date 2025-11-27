"""Docling などの図抽出結果を Figure/Table 番号ベースに整える."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


def detect_label(fig: Dict) -> Optional[Tuple[str, str]]:
    """Figure/Table と番号を推定して返す."""
    candidates: List[str] = []
    fig_type = fig.get("figType", "")
    caption = fig.get("caption", "")
    name = str(fig.get("name", "")).strip()

    if isinstance(fig_type, str):
        candidates = [fig_type]
    if isinstance(caption, str):
        candidates = list(candidates) + [caption]
    elif isinstance(caption, dict):
        candidates = list(candidates) + [caption.get("text", "")]

    for text in candidates:
        m = re.search(r"(Figure|Fig\.?|Table)\s*([0-9]+)", text, re.IGNORECASE)
        if m:
            kind = "Table" if m.group(1).lower().startswith("tab") else "Figure"
            return kind, m.group(2)

    if name.isdigit():
        kind = "Table" if "table" in str(fig_type).lower() else "Figure"
        return kind, name

    return None


def ensure_unique(base: str, used: Set[str]) -> str:
    """Figure1, Figure1-2 ... のように一意な名前にする."""
    name = base
    counter = 2
    while name in used:
        name = f"{base}-{counter}"
        counter += 1
    used.add(name)
    return name


def normalize(meta_dir: Path, fig_dir: Path) -> None:
    used: Set[str] = set()
    meta_files = sorted(meta_dir.glob("*.json"))
    if not meta_files:
        raise SystemExit(f"メタデータが見つかりません: {meta_dir}")

    for meta_file in meta_files:
        data = json.loads(meta_file.read_text())
        is_list = isinstance(data, list)
        if is_list:
            figures = data
        elif isinstance(data, dict):
            figures = data.get("figures", [])
        else:
            print(f"[warn] 未対応のメタデータ形式です: {meta_file}")
            continue
        changed = False

        for fig in figures:
            label = detect_label(fig)
            if not label:
                continue

            kind, num = label
            base_name = ensure_unique(f"{kind}{num}", used)

            render_url = str(fig.get("renderURL", ""))
            src_name = Path(render_url).name
            src = fig_dir / src_name
            if not src.exists():
                print(f"[warn] 画像が見つかりません: {src}")
                continue

            new_name = f"{base_name}{src.suffix or '.png'}"
            dst = fig_dir / new_name
            if src != dst:
                src.rename(dst)

            rel_path = Path(os.path.relpath(fig_dir, meta_dir)) / new_name
            fig["renderURL"] = str(rel_path)
            changed = True

        if changed:
            output_obj = figures if is_list else data
            if not is_list:
                data["figures"] = figures
            meta_file.write_text(
                json.dumps(output_obj, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    print(f"リネーム完了: {fig_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="抽出済みの図・表画像を Figure/Table 番号ベースでリネームする。",
    )
    parser.add_argument("meta_dir", type=Path, help="メタデータディレクトリ（Docling 出力など）")
    parser.add_argument("figure_dir", type=Path, help="抽出された図・表のディレクトリ")
    args = parser.parse_args()

    if not args.meta_dir.exists():
        raise SystemExit(f"meta ディレクトリが見つかりません: {args.meta_dir}")
    if not args.figure_dir.exists():
        raise SystemExit(f"figure ディレクトリが見つかりません: {args.figure_dir}")

    normalize(args.meta_dir, args.figure_dir)


if __name__ == "__main__":
    main()
