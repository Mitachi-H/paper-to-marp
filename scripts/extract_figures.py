#!/usr/bin/env python
"""Docling で PDF から図表の PNG とメタデータを抽出するスクリプト。"""

# 本ファイルは Docling 公式の Figure export 例をベースに改変しています。
# - 参照: https://docling-project.github.io/docling/examples/export_figures/
# - 元実装: https://github.com/docling-project/docling/tree/main/docs/examples
# - 元ライセンス: MIT (c) 2024 International Business Machines
# 詳細な帰属・ライセンス情報は THIRD_PARTY_NOTICES.md を参照してください。

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import ConversionResult, ConversionStatus
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DoclingDocument, PictureItem, TableItem
from docling_core.types.doc.document import BoundingBox, DocItem

DEFAULT_IMAGE_SCALE = 2.0
DEFAULT_MIN_AREA = 5000.0   # pt² — これ未満は無条件除外（ロゴ・アイコン）
DEFAULT_SOFT_AREA = 20000.0  # pt² — キャプションなし且つこれ未満なら除外


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Docling を使って PDF から図表画像とメタデータを抽出する。",
    )
    parser.add_argument("pdf", type=Path, help="入力 PDF パス")
    parser.add_argument(
        "figure_dir",
        nargs="?",
        default=Path("figures"),
        type=Path,
        help="PNG を保存するディレクトリ（既定: figures）",
    )
    parser.add_argument(
        "meta_dir",
        nargs="?",
        default=Path("meta"),
        type=Path,
        help="メタデータを保存するディレクトリ（既定: meta）",
    )
    parser.add_argument(
        "stats_file",
        nargs="?",
        default=Path("stats.json"),
        type=Path,
        help="実行統計を保存するファイル（既定: stats.json）",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=DEFAULT_IMAGE_SCALE,
        dest="image_scale",
        help="画像解像度スケール（72dpi を 1.0 とする倍率）",
    )
    parser.add_argument(
        "--min-area",
        type=float,
        default=DEFAULT_MIN_AREA,
        help=f"この面積(pt²)未満を無条件除外（既定: {DEFAULT_MIN_AREA}）",
    )
    parser.add_argument(
        "--soft-area",
        type=float,
        default=DEFAULT_SOFT_AREA,
        help=f"キャプションなし且つこの面積(pt²)未満を除外（既定: {DEFAULT_SOFT_AREA}）",
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="面積フィルタを無効化し全アイテムを保持する",
    )
    return parser.parse_args()


def build_converter(image_scale: float) -> DocumentConverter:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = image_scale
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )


def to_boundary(bbox: BoundingBox, page_height: float) -> Dict[str, float]:
    top_left_bbox = bbox.to_top_left_origin(page_height=page_height)
    return {
        "x1": top_left_bbox.l,
        "x2": top_left_bbox.r,
        "y1": top_left_bbox.t,
        "y2": top_left_bbox.b,
    }


def sort_items(items: Sequence[DocItem]) -> List[DocItem]:
    def _key(it: DocItem) -> Tuple[int, float, int]:
        prov = it.prov[0] if it.prov else None
        page_no = prov.page_no if prov else 10**9
        top = prov.bbox.t if prov else float("inf")
        # Picture を先に処理し、その後 Table
        kind_order = 1 if isinstance(it, TableItem) else 0
        return (page_no, top, kind_order)

    return sorted(items, key=_key)


def bbox_area(item: DocItem) -> float:
    """バウンディングボックスの面積 (pt²) を返す。"""
    if not item.prov:
        return 0.0
    bbox = item.prov[0].bbox
    return abs((bbox.r - bbox.l) * (bbox.b - bbox.t))


def should_keep(
    item: DocItem,
    doc: DoclingDocument,
    min_area: float,
    soft_area: float,
) -> tuple[bool, str]:
    """アイテムを保持するか判定する。(keep, reason) を返す。"""
    area = bbox_area(item)
    if area < min_area:
        return False, f"area={area:.0f} < min_area={min_area:.0f}"
    caption = item.caption_text(doc) if hasattr(item, "caption_text") else ""
    if not caption and area < soft_area:
        return False, f"no caption, area={area:.0f} < soft_area={soft_area:.0f}"
    return True, ""


def save_item_image(
    item: Union[PictureItem, TableItem],
    doc: DoclingDocument,
    dst: Path,
) -> Optional[int]:
    image = item.get_image(doc)
    if image is None:
        return None
    image.save(dst, format="PNG")
    page_no = item.prov[0].page_no if item.prov else None
    return page_no


def convert(
    pdf_path: Path,
    fig_dir: Path,
    meta_dir: Path,
    stats_file: Path,
    image_scale: float,
    min_area: float = DEFAULT_MIN_AREA,
    soft_area: float = DEFAULT_SOFT_AREA,
    no_filter: bool = False,
) -> None:
    if not pdf_path.exists():
        raise SystemExit(f"PDF が見つかりません: {pdf_path}")

    fig_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)
    stats_file.parent.mkdir(parents=True, exist_ok=True)

    converter = build_converter(image_scale=image_scale)

    start = time.perf_counter()
    conv_res: ConversionResult = converter.convert(pdf_path)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    if conv_res.status in {ConversionStatus.FAILURE, ConversionStatus.SKIPPED}:
        error_msg = (
            "\n".join(err.error_message for err in conv_res.errors)
            or "Docling conversion failed."
        )
        raise SystemExit(error_msg)
    if conv_res.document is None:
        raise SystemExit("Docling がドキュメントを返しませんでした。")

    doc = conv_res.document
    if conv_res.errors:
        print(
            "[warn] Docling 実行中に警告/エラーがありました。内容を確認してください。",
            file=sys.stderr,
        )
        for err in conv_res.errors:
            print(f" - {err.component_type}: {err.error_message}", file=sys.stderr)

    pdf_stem = pdf_path.stem
    meta_path = meta_dir / f"{pdf_stem}.json"

    items: List[Union[PictureItem, TableItem]] = [*doc.pictures, *doc.tables]
    sorted_items = sort_items(items)

    counters: Dict[str, int] = {"Figure": 0, "Table": 0}
    skipped = 0
    meta_list: List[Dict[str, object]] = []

    for item in sorted_items:
        if not no_filter:
            keep, reason = should_keep(item, doc, min_area, soft_area)
            if not keep:
                skipped += 1
                print(f"[filter] 除外: {reason}", file=sys.stderr)
                continue

        kind = "Table" if isinstance(item, TableItem) else "Figure"
        next_index = counters[kind] + 1
        filename = f"{kind}{next_index}.png"
        dst = fig_dir / filename

        page_no = save_item_image(item, doc, dst)
        if page_no is None:
            print(f"[warn] 画像を取得できませんでした: {filename}", file=sys.stderr)
            continue

        counters[kind] = next_index

        page = doc.pages.get(page_no)
        boundary = None
        if page and page.size:
            boundary = to_boundary(item.prov[0].bbox, page.size.height) if item.prov else None

        dpi = None
        if item.image and item.image.dpi:
            dpi = item.image.dpi
        elif page and page.image and page.image.dpi:
            dpi = page.image.dpi
        elif image_scale:
            dpi = int(72 * image_scale)

        render_url = os.path.relpath(dst, meta_dir)
        caption = item.caption_text(doc)

        entry: Dict[str, object] = {
            "figType": kind,
            "name": str(next_index),
            "page": page_no,
            "caption": caption,
            "renderURL": render_url,
            "renderDpi": dpi,
        }
        if boundary:
            entry["regionBoundary"] = boundary

        meta_list.append(entry)

    meta_path.write_text(
        json.dumps(meta_list, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if skipped:
        print(f"[filter] {skipped} 件のアイテムを除外しました", file=sys.stderr)

    stats = [
        {
            "filename": str(pdf_path.resolve()),
            "numFigures": counters["Figure"],
            "numTables": counters["Table"],
            "numSkipped": skipped,
            "numPages": len(doc.pages),
            "timeInMillis": elapsed_ms,
            "imageScale": image_scale,
        }
    ]
    stats_file.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Figures: {fig_dir}")
    print(f"Meta:    {meta_path}")
    print(f"Stats:   {stats_file}")


def main() -> None:
    args = parse_args()
    convert(
        pdf_path=args.pdf,
        fig_dir=args.figure_dir,
        meta_dir=args.meta_dir,
        stats_file=args.stats_file,
        image_scale=args.image_scale,
        min_area=args.min_area,
        soft_area=args.soft_area,
        no_filter=args.no_filter,
    )


if __name__ == "__main__":
    main()
