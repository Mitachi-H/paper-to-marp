"""1 コマンドで論文ワークスペースを準備・抽出する CLI。"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
PAPERS = ROOT / "papers"
ASSEMBLY_JARS = [
    ROOT / "pdffigures2" / "pdffigures2.jar",
    ROOT / "pdffigures2" / "target" / "scala-2.12" / "pdffigures2-assembly-0.1.0.jar",
]
PACKAGE_JAR = ROOT / "pdffigures2" / "target" / "scala-2.12" / "pdffigures2_2.12-0.1.0.jar"
ASSEMBLY_CMD = (
    f'cd "{ROOT / "pdffigures2"}" && '
    'JAVA_HOME="/Library/Java/JavaVirtualMachines/amazon-corretto-11.jdk/Contents/Home" '
    'PATH="$JAVA_HOME/bin:$PATH" sbt -Dsbt.supershell=false "set Test / skip := true" assembly'
)


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def slugify(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", name).strip("-")
    return slug or "paper"


def main() -> None:
    parser = argparse.ArgumentParser(description="論文ワークスペースを1コマンドで準備する。")
    parser.add_argument("--pdf", required=True, type=Path, help="入力 PDF パス")
    parser.add_argument("--skip-text", action="store_true", help="テキスト抽出をスキップ")
    parser.add_argument("--skip-figures", action="store_true", help="図抽出をスキップ")
    parser.add_argument("--skip-normalize", action="store_true", help="図ファイル名リネームをスキップ")
    parser.add_argument("--force-copy", action="store_true", help="既存の paper.pdf を上書きする")
    args = parser.parse_args()

    pdf_src = args.pdf.expanduser().resolve()
    if not pdf_src.exists():
        raise SystemExit(f"PDF が見つかりません: {pdf_src}")

    base_id = slugify(pdf_src.stem)
    dest = PAPERS / base_id
    counter = 2
    while dest.exists() and not args.force_copy and (dest / "paper.pdf").exists():
        dest = PAPERS / f"{base_id}-{counter}"
        counter += 1
    dest.mkdir(parents=True, exist_ok=True)

    pdf_dst = dest / "paper.pdf"
    if pdf_dst.exists() and not args.force_copy:
        print(f"[skip] paper.pdf は既に存在します: {pdf_dst}")
    else:
        shutil.copy(pdf_src, pdf_dst)
        print(f"[copy] {pdf_src} -> {pdf_dst}")

    if not args.skip_figures:
        if not any(jar.exists() for jar in ASSEMBLY_JARS):
            if PACKAGE_JAR.exists():
                raise SystemExit(
                    "pdffigures2 の fat jar がありません。"
                    " sbt assembly で依存込みの jar を作ってください:\n"
                    f"  {ASSEMBLY_CMD}"
                )
            raise SystemExit(
                "pdffigures2 の jar が見つかりません。"
                " sbt assembly でビルドしてください:\n"
                f"  {ASSEMBLY_CMD}"
            )

    # init: AGENT.md, prompt.css, figures/meta など
    run([sys.executable, str(SCRIPTS / "init_paper.py"), "--pdf", str(pdf_dst)], cwd=dest)

    if not args.skip_text:
        run([sys.executable, str(SCRIPTS / "pdf_to_text.py"), "paper.pdf", "paper_text.txt"], cwd=dest)

    if not args.skip_figures:
        env = os.environ.copy()
        if "JAVA_HOME" not in env:
            default_java = "/Library/Java/JavaVirtualMachines/amazon-corretto-11.jdk/Contents/Home"
            if Path(default_java).exists():
                env["JAVA_HOME"] = default_java
                env["PATH"] = f"{default_java}/bin:{env['PATH']}"
        run([str(SCRIPTS / "extract_figures.sh"), "paper.pdf", "figures", "meta", "stats.json"], cwd=dest)

    if not args.skip_normalize and not args.skip_figures:
        run([sys.executable, str(SCRIPTS / "normalize_figures.py"), "meta", "figures"], cwd=dest)

    print(f"完了: {dest}")
    print("次のステップ例: Cursor/Codex で AGENT.md を開き、prompt に従って slide.md を生成してください。")


if __name__ == "__main__":
    main()
