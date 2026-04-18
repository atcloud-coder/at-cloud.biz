#!/usr/bin/env python3
"""Build a sitemap for the GitHub Pages site and optionally verify local links.

By default scans only ``docs/`` (the Pages publish root), writes ``docs/sitemap.txt``
with one URL path per line relative to the site root (e.g. ``index.html``,
``programs/nextgen-coaching.html``). That file is handy for humans and scripts;
**search engines expect absolute URLs**, usually as XML.

Pass ``--base-url https://example.com`` to also write ``docs/sitemap.xml`` in the
`sitemaps.org <https://www.sitemaps.org/protocol.html>`_ format (submit that URL in
Google Search Console or Bing Webmaster Tools).

Pass ``--roots`` to include other folders. External http(s) URLs are skipped unless
``--check-external`` is set.
"""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE_ROOT = "docs"
DEFAULT_SITEMAP = "docs/sitemap.txt"
DEFAULT_SITEMAP_XML = "docs/sitemap.xml"
# WordPress mirror paths only matter if you add design/at-cloud.biz to --roots.
DEFAULT_IGNORE_PREFIXES = (
    "/wp-json/",
    "/xmlrpc.php",
    "/wp-content/",
    "/wp-includes/",
    "/wp-admin/",
)
SKIP_SCHEMES = frozenset(
    ("mailto:", "tel:", "javascript:", "about:", "blob:", "data:")
)


class AssetLinkParser(HTMLParser):
    """Collect href and src (and link href) from HTML; best-effort srcset."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k.lower(): v for k, v in attrs if v is not None}
        if tag == "img":
            if "src" in ad:
                self.urls.append(ad["src"])
            if "srcset" in ad:
                self._parse_srcset(ad["srcset"])
        elif tag == "source":
            if "src" in ad:
                self.urls.append(ad["src"])
            if "srcset" in ad:
                self._parse_srcset(ad["srcset"])
        elif tag == "script" and "src" in ad:
            self.urls.append(ad["src"])
        elif tag == "a" and "href" in ad:
            self.urls.append(ad["href"])
        elif tag == "link" and "href" in ad:
            self.urls.append(ad["href"])
        elif tag == "area" and "href" in ad:
            self.urls.append(ad["href"])
        elif tag == "use" and "href" in ad:
            self.urls.append(ad["href"])
        elif tag == "base" and "href" in ad:
            self.urls.append(ad["href"])

    def _parse_srcset(self, srcset: str) -> None:
        for part in srcset.split(","):
            piece = part.strip().split()
            if piece:
                self.urls.append(piece[0])


def normalize_roots(repo: Path, roots: list[str]) -> list[Path]:
    out: list[Path] = []
    for r in roots:
        p = (repo / r).resolve()
        if not p.is_dir():
            raise SystemExit(f"Not a directory: {p}")
        out.append(p)
    out.sort(key=lambda x: len(x.parts), reverse=True)
    return out


def longest_root_containing(roots: list[Path], path: Path) -> Path | None:
    rp = path.resolve()
    best: Path | None = None
    for root in roots:
        try:
            rp.relative_to(root)
        except ValueError:
            continue
        if best is None or len(root.parts) > len(best.parts):
            best = root
    return best


def discover_html_files(roots: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    files: list[Path] = []
    for root in roots:
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in (".html", ".htm"):
                continue
            rp = p.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            files.append(p)
    files.sort()
    return files


def should_skip_href(raw: str) -> bool:
    s = raw.strip()
    if not s:
        return True
    low = s.lower()
    if low.startswith("#"):
        return True
    for sc in SKIP_SCHEMES:
        if low.startswith(sc):
            return True
    return False


def is_external(url: str) -> bool:
    low = url.strip().lower()
    return low.startswith("http://") or low.startswith("https://") or low.startswith("//")


def _wordpress_shortlink_file(web_root: Path, query: str) -> Path | None:
    """Mirror layout: index.html?p={id}.html at site root."""
    if not query.startswith("p="):
        return None
    pid = query[2:].split("&", 1)[0]
    if not pid.isdigit():
        return None
    cand = web_root / f"index.html?p={pid}.html"
    return cand if cand.is_file() else None


def _link_target_exists(path: Path) -> bool:
    if path.is_file():
        return True
    if path.is_dir() and (path / "index.html").is_file():
        return True
    return False


def resolve_local_target(
    html_path: Path,
    web_root: Path,
    href: str,
    ignore_prefixes: tuple[str, ...],
) -> Path | None:
    """Return filesystem path to verify, or None if not applicable (skipped)."""
    raw = href.strip()
    if not raw or raw.startswith("#"):
        return None
    low = raw.lower()
    for sc in SKIP_SCHEMES:
        if low.startswith(sc):
            return None
    if is_external(raw):
        return None

    no_frag = raw.split("#", 1)[0]
    no_frag = urllib.parse.unquote(no_frag)

    if no_frag.startswith("/"):
        parts = urllib.parse.urlsplit("https://local.invalid" + no_frag)
        path_part = parts.path or "/"
        query = parts.query
        for prefix in ignore_prefixes:
            if path_part.startswith(prefix):
                return None
        # WordPress-style shortlink: /?p=123
        if path_part in ("/", "") and query:
            wp = _wordpress_shortlink_file(web_root, query)
            if wp is not None:
                return wp

        rel = path_part.lstrip("/")
        candidate = (web_root / rel).resolve() if rel else web_root.resolve()
        if _link_target_exists(candidate):
            return candidate
        if not candidate.exists() and not candidate.suffix:
            alt = candidate / "index.html"
            if alt.is_file():
                return alt
        return candidate

    # Relative to the HTML file's directory (may include "?" in filename).
    base_dir = html_path.parent
    candidate = (base_dir / no_frag).resolve()
    if _link_target_exists(candidate):
        return candidate

    # Cache-buster style: foo.css?v=3
    if "?" in no_frag:
        stem = no_frag.split("?", 1)[0]
        if stem:
            alt = (base_dir / stem).resolve()
            if _link_target_exists(alt):
                return alt
    return candidate


def check_external(url: str, timeout: float) -> tuple[bool, str]:
    if url.startswith("//"):
        url = "https:" + url
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "sitemap_and_linkcheck/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            if 200 <= code < 400:
                return True, f"HTTP {code}"
            return False, f"HTTP {code}"
    except urllib.error.HTTPError as e:
        if e.code in (405, 501):
            return check_external_get(url, timeout)
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)


def check_external_get(url: str, timeout: float) -> tuple[bool, str]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "sitemap_and_linkcheck/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            if 200 <= code < 400:
                return True, f"HTTP {code} (GET)"
            return False, f"HTTP {code}"
    except Exception as e:
        return False, str(e)


def collect_links(html_path: Path) -> list[str]:
    data = html_path.read_text(encoding="utf-8", errors="replace")
    parser = AssetLinkParser()
    try:
        parser.feed(data)
    except Exception:
        pass
    parser.close()
    return parser.urls


def rel_to_repo(path: Path, repo: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def rel_to_site(path: Path, site_root: Path) -> str:
    """Path as served from the GitHub Pages root (under docs/)."""
    return path.resolve().relative_to(site_root.resolve()).as_posix()


def public_url(base: str, site_relative: str) -> str:
    """Join canonical site origin with a path like ``programs/foo.html``."""
    b = base.strip().rstrip("/")
    p = site_relative.strip().lstrip("/")
    if not p:
        return f"{b}/"
    return f"{b}/{p}"


def build_sitemap_xml(locations: list[str]) -> str:
    """Sitemaps.org XML format (UTF-8)."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc in locations:
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_escape(loc)}</loc>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--repo",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (default: parent of this script)",
    )
    ap.add_argument(
        "--roots",
        nargs="+",
        default=[DEFAULT_SITE_ROOT],
        help="Subdirectories under --repo to scan (default: docs)",
    )
    ap.add_argument(
        "--sitemap",
        type=Path,
        default=None,
        help="Plain list output (paths relative to site root). Default: docs/sitemap.txt",
    )
    ap.add_argument(
        "--base-url",
        default=None,
        metavar="URL",
        help="Canonical origin, e.g. https://at-cloud.biz — writes docs/sitemap.xml "
        "with absolute <loc> URLs for search engines (sitemap.txt stays path-only).",
    )
    ap.add_argument(
        "--sitemap-xml",
        type=Path,
        default=None,
        help="XML sitemap path when --base-url is set. Default: docs/sitemap.xml",
    )
    ap.add_argument(
        "--check-external",
        action="store_true",
        help="HEAD (or GET if HEAD fails) external http(s) URLs",
    )
    ap.add_argument(
        "--external-timeout",
        type=float,
        default=12.0,
        help="Timeout in seconds for external checks",
    )
    ap.add_argument(
        "--ignore-prefix",
        action="append",
        default=[],
        help="Additional site-root path prefixes to skip (repeatable). "
        "Merged with built-in WordPress mirror skips.",
    )
    args = ap.parse_args()
    repo = args.repo.resolve()
    docs_root = (repo / DEFAULT_SITE_ROOT).resolve()
    if not docs_root.is_dir():
        raise SystemExit(f"Missing GitHub Pages folder: {docs_root}")

    roots = normalize_roots(repo, args.roots)
    sitemap_path = (args.sitemap or (repo / DEFAULT_SITEMAP)).resolve()

    html_files = discover_html_files(roots)
    sitemap_pages = sorted(
        p
        for p in html_files
        if p.resolve() == docs_root or docs_root in p.resolve().parents
    )
    lines = [rel_to_site(p, docs_root) for p in sitemap_pages]
    sitemap_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    if args.base_url:
        xml_path = (args.sitemap_xml or (repo / DEFAULT_SITEMAP_XML)).resolve()
        locs = [public_url(args.base_url, rel) for rel in lines]
        xml_path.write_text(build_sitemap_xml(locs), encoding="utf-8")

    ignore_prefixes = tuple(DEFAULT_IGNORE_PREFIXES) + tuple(args.ignore_prefix)

    broken_local: list[tuple[str, str, str]] = []
    broken_external: list[tuple[str, str, str]] = []

    for html_path in html_files:
        web_root = longest_root_containing(roots, html_path)
        if web_root is None:
            web_root = html_path.parent

        page_key = rel_to_repo(html_path, repo)
        for raw in collect_links(html_path):
            if should_skip_href(raw):
                continue
            if is_external(raw):
                if args.check_external:
                    ok, detail = check_external(raw.strip(), args.external_timeout)
                    if not ok:
                        broken_external.append((page_key, raw.strip(), detail))
                continue

            target = resolve_local_target(html_path, web_root, raw, ignore_prefixes)
            if target is None:
                continue
            if not _link_target_exists(target):
                broken_local.append((page_key, raw.strip(), target.as_posix()))

    print(
        f"Sitemap: {len(sitemap_pages)} pages under {DEFAULT_SITE_ROOT}/ -> {sitemap_path.relative_to(repo)}"
    )
    if args.base_url:
        xml_path = (args.sitemap_xml or (repo / DEFAULT_SITEMAP_XML)).resolve()
        print(f"         XML for crawlers -> {xml_path.relative_to(repo)} ({args.base_url})")
    if broken_local:
        print("\nBroken local URLs (source page, href/src, resolved path):", file=sys.stderr)
        for src_page, href, resolved in broken_local:
            print(f"  {src_page}\n    {href}\n    -> {resolved}", file=sys.stderr)
    if broken_external:
        print("\nBroken external URLs:", file=sys.stderr)
        for src_page, href, detail in broken_external:
            print(f"  {src_page}\n    {href}\n    -> {detail}", file=sys.stderr)

    if broken_local or broken_external:
        print(
            f"\nSummary: {len(broken_local)} broken local, {len(broken_external)} broken external.",
            file=sys.stderr,
        )
        return 1

    print("Link check: no broken local URLs" + (" or external URLs checked." if args.check_external else "."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
