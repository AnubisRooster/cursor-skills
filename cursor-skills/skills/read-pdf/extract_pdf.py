#!/usr/bin/env python3
"""Extract text from PDF(s) into .extracted.md files readable by non-PDF models."""
import argparse
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    sys.exit("pypdf is not installed. Run: pip install pypdf")


def _reflow(text: str, width: int = 110) -> str:
    """Collapse word-per-line PDF exports into wrapped prose."""
    import re
    import textwrap
    flat = re.sub(r"\s+", " ", text).strip()
    if not flat:
        return ""
    return "\n".join(textwrap.wrap(flat, width=width, break_long_words=False))


def extract(pdf: Path, outdir: Path | None) -> Path:
    reader = PdfReader(str(pdf))
    out = (outdir or pdf.parent) / (pdf.stem + ".extracted.md")
    lines = [
        f"# Extracted from: {pdf.name}",
        f"Pages: {len(reader.pages)}",
        "",
    ]
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = (page.extract_text() or "").strip()
        except Exception as e:  # noqa: BLE001
            text = f"[extraction error: {e}]"
        lines.append(f"## Page {i}")
        lines.append(_reflow(text) if text else "[no extractable text]")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract PDF text to .extracted.md")
    ap.add_argument("pdfs", nargs="+", type=Path, help="PDF file(s) to extract")
    ap.add_argument("-o", "--outdir", type=Path, default=None, help="Output directory")
    args = ap.parse_args()

    if args.outdir is not None:
        args.outdir.mkdir(parents=True, exist_ok=True)

    for pdf in args.pdfs:
        if not pdf.is_file():
            print(f"ERROR: not found: {pdf}")
            continue
        out = extract(pdf, args.outdir)
        print(f"OK: {pdf.name} -> {out}")


if __name__ == "__main__":
    main()
