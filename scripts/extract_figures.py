#!/usr/bin/env python
"""Docling で PDF から図表の PNG とメタデータを抽出するスクリプト。"""

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
    meta_list: List[Dict[str, object]] = []

    for item in sorted_items:
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

    stats = [
        {
            "filename": str(pdf_path.resolve()),
            "numFigures": counters["Figure"],
            "numTables": counters["Table"],
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
    )


if __name__ == "__main__":
    main()
