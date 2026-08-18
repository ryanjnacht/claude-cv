#!/usr/bin/env python3
"""
render_pdf.py — Render a distribution-ready PDF CV from a Markdown CV.

Pipeline:
    Markdown ──> python-markdown ──> HTML ──> WeasyPrint ──> PDF

The Markdown CV is the canonical intermediate: this script consumes whatever
render_cv.py (or a tailored profile) produced, so no template logic is
duplicated here.

Usage:
    python scripts/render_pdf.py <input_md> <output_pdf> [--css <path>] [--html-only]

Example:
    python scripts/render_pdf.py output/cv.md output/cv.pdf
    python scripts/render_pdf.py output/cv.md output/cv.pdf --html-only
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# The Jinja template separates the name block from the links with a decorative
# rule of tildes ("~" * 50). In raw Markdown that is just a line of text that
# gets glued onto the contact paragraph, so before conversion we normalize the
# pair — a text line immediately followed by a line of 5+ tildes — into a
# real <p class="contact-line"> plus a styled <hr>.
_CONTACT_RULE = re.compile(
    r"(?m)^(?P<line>[^\n~].*?)\n~{5,}[ \t]*$",
)


def require_module(name: str, apt_pkg: str, pip_pkg: str):
    """Import a third-party module or exit with install instructions."""
    try:
        return __import__(name)
    except ImportError:
        print(f"❌ Missing dependency: {name!r} is not installed.")
        print("   Install with one of:")
        print(f"     sudo apt install {apt_pkg}   # Debian/Ubuntu (recommended)")
        print(f"     pip install {pip_pkg}        # or into a venv")
        if name == "weasyprint":
            print("   The apt package pulls in the required Pango/HarfBuzz")
            print("   system libraries automatically.")
        sys.exit(1)


def md_to_html(markdown_text: str) -> str:
    """Convert the Markdown CV to HTML body content."""
    markdown = require_module("markdown", "python3-markdown", "markdown")

    normalized = _CONTACT_RULE.sub(
        r'<p class="contact-line">\g<line></p>\n<hr class="contact-rule" />',
        markdown_text,
    )

    return markdown.markdown(normalized, extensions=["tables"])


def build_document(body_html: str, css_path: str) -> str:
    """Wrap the HTML body in a self-contained document (CSS inlined)."""
    css = Path(css_path)
    if not css.exists():
        print(f"❌ Error: stylesheet not found at {css_path}")
        sys.exit(1)

    css_text = css.read_text(encoding="utf-8")

    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8" />\n'
        "<style>\n" + css_text + "\n</style>\n"
        "</head>\n"
        "<body>\n" + body_html + "\n</body>\n"
        "</html>\n"
    )


def render_pdf(document_html: str, out_path: Path) -> None:
    """Render the styled HTML document to PDF via WeasyPrint."""
    weasyprint = require_module("weasyprint", "python3-weasyprint", "weasyprint")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    weasyprint.HTML(string=document_html).write_pdf(str(out_path))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a distribution-ready PDF CV from a Markdown CV."
    )
    parser.add_argument("input_md", help="Path to the Markdown CV (e.g. output/cv.md).")
    parser.add_argument("output_pdf", help="Path for the generated PDF (e.g. output/cv.pdf).")
    parser.add_argument(
        "--css",
        default="styles/cv.css",
        help="Path to the print stylesheet (default: styles/cv.css).",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Stop after HTML and write <output>.html — skips WeasyPrint.",
    )
    args = parser.parse_args()

    md_path = Path(args.input_md)
    if not md_path.exists():
        print(f"❌ Error: Markdown file not found at {args.input_md}")
        sys.exit(1)

    body_html = md_to_html(md_path.read_text(encoding="utf-8"))
    document = build_document(body_html, args.css)

    if args.html_only:
        out = Path(args.output_pdf).with_suffix(".html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(document, encoding="utf-8")
        print(f"✅ HTML written (PDF step skipped) → {out}")
        return

    out_pdf = Path(args.output_pdf)
    render_pdf(document, out_pdf)

    size_kb = out_pdf.stat().st_size / 1024
    print(f"✅ PDF rendered successfully → {out_pdf}")
    try:
        import fitz  # PyMuPDF — already a project dependency (PDF import)
        with fitz.open(str(out_pdf)) as doc:
            print(f"   ({size_kb:.1f} KB, {len(doc)} pages)")
    except ImportError:
        print(f"   ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
