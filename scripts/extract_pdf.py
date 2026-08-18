#!/usr/bin/env python3
"""
extract_pdf.py — Extract raw text from a PDF resume/CV for profile import.

Usage:
    python scripts/extract_pdf.py <input.pdf> [-o output.txt]

Prints a one-line stats summary to stderr and the extracted text to stdout,
or to the file given by -o (parent directories are created).

Exit codes:
    0  success
    1  file not found / unreadable / not a valid PDF
    2  no extractable text (likely a scanned image PDF)
    3  missing PyMuPDF dependency
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# PyMuPDF >= 1.25 renamed the module; fall back to the legacy name for
# older installs.
try:
    import pymupdf as mupdf
except ImportError:
    try:
        import fitz as mupdf  # type: ignore[no-redef]
    except ImportError:
        print(
            "❌ Error: PyMuPDF is not installed.\n"
            "   Debian: sudo apt install python3-pymupdf\n"
            "   pip:    python3 -m pip install PyMuPDF",
            file=sys.stderr,
        )
        sys.exit(3)

# Fewer non-whitespace characters than this across the whole document
# means the PDF has no usable text layer (scanned images, or vector-only art).
MIN_MEANINGFUL_CHARS = 40


def extract(pdf_path: Path) -> tuple[int, str]:
    """Return (page_count, full_text) for the given PDF."""
    doc = mupdf.open(str(pdf_path))
    try:
        pages = [doc[i].get_text("text") for i in range(len(doc))]
    finally:
        doc.close()
    return len(pages), "\n".join(pages)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract raw text from a PDF resume/CV."
    )
    parser.add_argument("input_pdf", help="Path to the PDF file.")
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Write extracted text to this file instead of stdout.",
    )
    args = parser.parse_args()

    src = Path(args.input_pdf)
    if not src.is_file():
        print(f"❌ Error: PDF not found at {src}", file=sys.stderr)
        sys.exit(1)

    try:
        pages, text = extract(src)
    except Exception as exc:
        print(f"❌ Error: could not read PDF: {exc}", file=sys.stderr)
        sys.exit(1)

    meaningful = len("".join(text.split()))
    print(f"Pages: {pages} | Extracted chars: {len(text)} | Meaningful: {meaningful}", file=sys.stderr)

    if meaningful < MIN_MEANINGFUL_CHARS:
        print(
            "⚠️  No usable text layer found — this looks like a scanned image PDF.\n"
            "    Try a text-based export, a web version of the document, or paste the text instead.",
            file=sys.stderr,
        )
        sys.exit(2)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"✅ Text extracted → {out}")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
