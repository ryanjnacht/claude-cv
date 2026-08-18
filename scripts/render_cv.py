#!/usr/bin/env python3
"""
render_cv.py — Render a Markdown CV from a YAML master profile and a Jinja2 template.

Usage:
    python scripts/render_cv.py <input_yaml> <output_markdown> [--template <path>]

Example:
    python scripts/render_cv.py data/master_profile.yaml output/cv.md
    python scripts/render_cv.py data/master_profile.yaml output/cv.md \
        --template templates/modern_cv.md.jinja
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader


def load_profile(yaml_path: str) -> dict:
    """Load and parse the YAML master profile."""
    path = Path(yaml_path)
    if not path.exists():
        print(f"❌ Error: YAML file not found at {yaml_path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    if not data:
        print(f"❌ Error: {yaml_path} is empty or contains no valid YAML.")
        sys.exit(1)

    return data


def render(template_path: str, context: dict) -> str:
    """Render the Jinja2 template with the given context."""
    template_dir = str(Path(template_path).parent)
    template_name = Path(template_path).name

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,  # output is Markdown, not HTML — no entity escaping
        trim_blocks=True,
        lstrip_blocks=True,
    )

    try:
        template = env.get_template(template_name)
    except Exception as exc:
        print(f"❌ Error loading template: {exc}")
        sys.exit(1)

    return template.render(**context)


def save(output_path: str, content: str) -> None:
    """Write the rendered Markdown to disk."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a Markdown CV from a YAML profile and Jinja2 template."
    )
    parser.add_argument("input_yaml", help="Path to the master profile YAML file.")
    parser.add_argument("output_markdown", help="Path for the generated Markdown CV.")
    parser.add_argument(
        "--template",
        default=None,
        help="Path to the Jinja2 template (default: templates/modern_cv.md.jinja).",
    )
    args = parser.parse_args()

    # Resolve template path
    template_path = args.template or "templates/modern_cv.md.jinja"

    # Load, render, save
    profile = load_profile(args.input_yaml)
    markdown = render(template_path, profile)
    save(args.output_markdown, markdown)

    print(f"✅ CV rendered successfully → {args.output_markdown}")
    print(f"   ({len(markdown.splitlines())} lines, {len(markdown)} bytes)")


if __name__ == "__main__":
    main()
