#!/usr/bin/env python3
"""検索向けの小直し（何度かけても同じ結果になる）。

1. 題（title と og:title）の後ろを「｜筆算堂」に短くする
2. 構造化データの Article に、発行元（筆算堂）を足し、dateModified を頁の「最終更新」にそろえる
3. 頁のパンくず（p.crumb）から BreadcrumbList の構造化データを作る
4. 無線の入口へのリンクを、正規のアドレス（musen/）にそろえる
5. 頁の一覧（sitemap.xml）の lastmod を、各頁の最終更新にそろえる

使い方: python3 .github/scripts/seo_fix.py [サイトの根のフォルダー]
"""
import json, re, sys
from pathlib import Path

BASE = "https://math-san-bit.github.io/denken/"
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
PUBLISHER = {"@type": "Organization", "name": "筆算堂", "url": BASE}

SUFFIXES = ["｜電験三種　計算で止まる所の辞典", "｜一陸特・一陸技　計算で止まる所の辞典", "｜計算で止まる所の辞典"]
TITLE_FIX = {  # 入口の頁は、題そのものを直す
    "電験三種　計算で止まる所の辞典": "電験三種の計算で止まる所の辞典｜筆算堂",
    "一陸特・一陸技　計算で止まる所の辞典": "一陸特・一陸技の計算で止まる所の辞典｜筆算堂",
}


def fix_title(t):
    if t in TITLE_FIX:
        return TITLE_FIX[t]
    for s in SUFFIXES:
        if t.endswith(s):
            return t[: -len(s)] + "｜筆算堂"
    return t


def url_of(p):
    rel = p.relative_to(ROOT).as_posix()
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return BASE + rel


def updated(text):
    m = re.search(r'class="updated">最終更新：(\d{4})年(\d{1,2})月(\d{1,2})日', text)
    return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else None


def breadcrumb(text, page):
    m = re.search(r'<p class="crumb">(.*?)</p>', text)
    if not m:
        return None
    parts = [x.strip() for x in m.group(1).split("›")]
    items = []
    for i, part in enumerate(parts, 1):
        a = re.match(r'<a href="([^"]*)">(.*?)</a>', part)
        if a:
            href, name = a.groups()
            target = (page.parent / href).resolve()
            if target.is_dir():
                target = target / "index.html"
            items.append({"@type": "ListItem", "position": i, "name": name, "item": url_of(target)})
        else:
            items.append({"@type": "ListItem", "position": i, "name": re.sub("<[^>]+>", "", part), "item": url_of(page)})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def main():
    lastmods = {}
    for page in sorted(ROOT.rglob("*.html")):
        if ".github" in page.parts or page.name.startswith("google"):
            continue
        text = page.read_text(encoding="utf-8")
        orig = text

        # 1. 題
        text = re.sub(r"<title>(.*?)</title>", lambda m: f"<title>{fix_title(m.group(1))}</title>", text)
        text = re.sub(r'(<meta property="og:title" content=")([^"]*)(")', lambda m: m.group(1) + fix_title(m.group(2)) + m.group(3), text)

        # 2. Article
        day = updated(text)
        if day:
            lastmods[url_of(page)] = day

        def fix_ld(m):
            data = json.loads(m.group(1))
            if data.get("@type") == "Article":
                data["publisher"] = PUBLISHER
                if day:
                    data["dateModified"] = day
                data["headline"] = fix_title(data["headline"]).removesuffix("｜筆算堂")
            return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"
        text = re.sub(r'<script type="application/ld\+json">(\{.*?\})</script>', fix_ld, text)

        # 3. パンくず
        text = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "BreadcrumbList".*?</script>\n', "", text)
        bc = breadcrumb(text, page)
        if bc and len(bc["itemListElement"]) > 1:
            tag = '<script type="application/ld+json">' + json.dumps(bc, ensure_ascii=False) + "</script>\n"
            text = text.replace('<link rel="stylesheet"', tag + '<link rel="stylesheet"', 1)

        # 4. 無線の入口
        text = text.replace('href="musen/index.html"', 'href="musen/"').replace('href="../musen/index.html"', 'href="../musen/"')
        if page.parent.name == "musen":
            text = text.replace('href="index.html"', 'href="./"')

        if text != orig:
            page.write_text(text, encoding="utf-8")
            print("直した:", page.relative_to(ROOT))

    # 5. lastmod
    sm = ROOT / "sitemap.xml"
    s = sm.read_text(encoding="utf-8")
    def fix_url(m):
        block = m.group(0)
        loc = re.search(r"<loc>([^<]+)</loc>", block).group(1).strip()
        day = lastmods.get(loc)
        if day and "<lastmod>" in block:
            block = re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{day}</lastmod>", block)
        return block
    s2 = re.sub(r"<url>.*?</url>", fix_url, s, flags=re.S)
    if s2 != s:
        sm.write_text(s2, encoding="utf-8")
        print("直した: sitemap.xml")


if __name__ == "__main__":
    main()
