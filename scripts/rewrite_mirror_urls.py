#!/usr/bin/env python3
"""Rewrite mirrored at-cloud.biz absolute URLs to root-relative paths for local static serving."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "design" / "at-cloud.biz"
REPLACEMENTS = (
    ("https://at-cloud.biz/", "/"),
    ("http://at-cloud.biz/", "/"),
    ("//at-cloud.biz/", "/"),
    # Homepage URL without trailing slash (feeds, JSON, etc.)
    ('https://at-cloud.biz"', '/"'),
    ("https://at-cloud.biz'", "/'"),
    ("https://at-cloud.biz<", "/<"),
    ("https://at-cloud.biz)", "/)"),
    ("https://at-cloud.biz\\", "/\\"),
    ("http://at-cloud.biz\"", '/"'),
    ("http://at-cloud.biz'", "/'"),
    ("http://at-cloud.biz<", "/<"),
    ("http://at-cloud.biz)", "/)"),
)


def looks_text(data: bytes) -> bool:
    return b"\x00" not in data[:8192]


def should_try(path: Path) -> bool:
    n = path.name.lower()
    for suf in (".html", ".htm", ".css", ".js", ".svg", ".xml", ".json", ".txt", ".map"):
        if n.endswith(suf):
            return True
    return False


def main() -> None:
    if not ROOT.is_dir():
        raise SystemExit(f"Missing mirror directory: {ROOT}")
    changed = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or not should_try(path):
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if not looks_text(data):
            continue
        text = data.decode("utf-8", errors="surrogateescape")
        orig = text
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
        if text != orig:
            path.write_bytes(text.encode("utf-8", errors="surrogateescape"))
            changed += 1
    print(f"Updated {changed} files under {ROOT}")


if __name__ == "__main__":
    main()
