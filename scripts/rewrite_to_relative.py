#!/usr/bin/env python3
"""
Rewrite absolute href paths in dist/ HTML into artifact-relative paths
so the site is clickable inside Claude's artifact sandbox. Production
deploy doesn't need this (absolute paths work at the site root).
"""

import re
import sys
from pathlib import Path

DIST = Path(__file__).resolve().parent.parent / "dist"


def rewrite_file(html_path: Path):
    # Depth = how many directory levels this file is below dist/
    rel = html_path.relative_to(DIST)
    depth = len(rel.parts) - 1  # subtract filename
    prefix = "../" * depth if depth > 0 else ""

    text = html_path.read_text()
    # href="/..."  -> href="<prefix>..."
    # Skip protocol-relative hrefs (href="//...")
    def repl(m):
        href = m.group(1)
        if href.startswith("/") or href == "":
            return f'href="{prefix}{href[1:]}"' if href else m.group(0)
        return m.group(0)

    # Match both href= and src= with absolute single-slash paths
    new_text = re.sub(r'href="/(?!/)([^"]*)"', lambda m: f'href="{prefix}{m.group(1)}"', text)
    new_text = re.sub(r'src="/(?!/)([^"]*)"', lambda m: f'src="{prefix}{m.group(1)}"', new_text)

    if new_text != text:
        html_path.write_text(new_text)


def main():
    count = 0
    for html in DIST.rglob("*.html"):
        rewrite_file(html)
        count += 1
    print(f"Rewrote {count} HTML files")


if __name__ == "__main__":
    main()
