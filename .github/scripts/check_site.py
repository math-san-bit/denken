#!/usr/bin/env python3
"""公開の前の検査。サイトの中のリンクと、頁の一覧（sitemap）を確かめる。

確かめること
1. すべての HTML の href と src のうち、サイトの中を指すものが、実在するファイルに届くこと
2. sitemap.xml、sitemap-pages.xml、sitemap.txt に載っているアドレスが、実在するファイルに届くこと
3. すべての HTML が sitemap.xml に載っていること（検索の確かめ用のファイルを除く）

使い方: python3 .github/scripts/check_site.py [サイトの根のフォルダー]
誤りが1つでもあれば、終了コード 1 で終わる。
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

BASE_URL = "https://hissandou.pages.dev/"
OLD_URL = "https://math-san-bit.github.io/denken/"
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SKIP_DIRS = {".git", ".github", ".claude", "_site"}
ATTR = re.compile(r"""(?:href|src)\s*=\s*["']([^"']*)["']""", re.I)
LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")


def html_files():
    for p in sorted(ROOT.rglob("*.html")):
        if not SKIP_DIRS.intersection(p.relative_to(ROOT).parts):
            yield p


def to_file(path: Path):
    """フォルダーを指すアドレスは、その中の index.html に読み替える。"""
    if path.is_dir():
        path = path / "index.html"
    if not path.is_file() and path.suffix == "" and path.with_suffix(".html").is_file():
        path = path.with_suffix(".html")  # 公開先（Cloudflare Pages）は .html を外したアドレスで出す
    return path if path.is_file() else None


def local_target(src: Path, ref: str):
    """サイトの中を指すなら (届け先 or None) を、外を指すなら False を返す。"""
    ref = ref.strip()
    if not ref or ref.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
        return False
    if ref.startswith(BASE_URL):
        ref = "/" + ref[len(BASE_URL):]
    parts = urlsplit(ref)
    if parts.scheme or parts.netloc:
        return False
    path = unquote(parts.path)
    if not path:
        return False
    if path.startswith("/"):
        base = ROOT / path[1:]
    else:
        base = src.parent / path
    base = base.resolve()
    if ROOT != base and ROOT not in base.parents:
        return None
    return to_file(base)


def main():
    errors = []
    pages = list(html_files())

    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        for ref in ATTR.findall(text):
            target = local_target(page, ref)
            if target is None:
                errors.append(f"リンク切れ: {page.relative_to(ROOT)} → {ref}")

    # 公開のアドレスは .html を外した形で書く（Cloudflare Pages は .html 付きを 308 で外す）。古いアドレスも残さない
    abs_html = re.compile(re.escape(BASE_URL) + r"[^\s\"'<>)]*\.html")
    for f in sorted(ROOT.rglob("*")):
        if SKIP_DIRS.intersection(f.relative_to(ROOT).parts) or not f.is_file():
            continue
        if f.suffix not in {".html", ".xml", ".txt", ".js"}:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        for u in abs_html.findall(text):
            errors.append(f".html 付きの公開アドレス: {f.relative_to(ROOT)} → {u}")
        if OLD_URL in text:
            errors.append(f"古いアドレス（github.io）が残っている: {f.relative_to(ROOT)}")

    listed = set()
    for name in ("sitemap.xml", "sitemap-pages.xml", "sitemap.txt"):
        f = ROOT / name
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        urls = LOC.findall(text) if name.endswith(".xml") else text.split()
        for url in urls:
            if not url.startswith(BASE_URL):
                errors.append(f"{name}: このサイトの外のアドレス → {url}")
                continue
            target = to_file(ROOT / unquote(urlsplit(url).path)[1:])
            if target is None:
                errors.append(f"{name}: 実在しない頁 → {url}")
            elif name == "sitemap.xml":
                listed.add(target)

    if (ROOT / "sitemap.xml").is_file():
        for page in pages:
            if page.name.startswith("google") and page.parent == ROOT:
                continue  # 検索の確かめ用のファイル
            if page not in listed:
                errors.append(f"sitemap.xml に載っていない頁: {page.relative_to(ROOT)}")

    print(f"調べた頁: {len(pages)}")
    if errors:
        print(f"誤り: {len(errors)} 件")
        for e in errors:
            print("  " + e)
        return 1
    print("誤りは見つかりませんでした")
    return 0


if __name__ == "__main__":
    sys.exit(main())
