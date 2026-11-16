#!/usr/bin/env python3
"""三相と変圧器のまとまりに「地図の層」を足す（幅を先に見せる試し。2026-11-16 から）。

1. 地図の頁 sansou-chizu.html を作る（止まる順に7つ）
2. 7つの解説の頁に、現在地（7つのうち何番目か）と全体の1行を足す
3. 7つの解説の頁の「次に読む」を、止まる順の次の3つにする
4. 電験三種の入口・ページの一覧・頁の一覧（3種）に地図を足す
何度かけても同じ結果になる。地図のリンクには data-chizu を付け、m.js が chizu の行動として数える。

使い方: python3 .github/scripts/chizu_sansou.py [サイトの根のフォルダー]
"""
import html, re, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
BASE = "https://math-san-bit.github.io/denken/"
MAP = "sansou-chizu.html"
TITLE = "三相と変圧器の計算で、止まる所の地図"
# 止まる順：前の所が分かっていると、次が楽になる並び
ORDER = [
    ("root3.html", "線間電圧と相電圧", "√3 を掛けるか、割るか"),
    ("root3-to-3.html", "三相の電力", "√3 を掛けたうえで、3倍するか"),
    ("youryou-denryuu.html", "容量から電流", "√3 で割るのを忘れる"),
    ("rikiritsu.html", "力率と無効電力", "kW・kV·A・kvar のつながり"),
    ("henatsu-makisuu.html", "変圧器の巻数比", "a を掛けるか、割るか、2乗か"),
    ("tanraku-100.html", "短絡電流と %Z", "100 を掛けるか、割るか"),
    ("kijun-youryou.html", "%Z の基準容量", "容量の比を掛けるか、割るか"),
]
N = len(ORDER)
NUM = "①②③④⑤⑥⑦⑧⑨"


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def info(name):
    t = read(name)
    h1 = re.search(r"<h1>(.*?)</h1>", t).group(1)
    g = re.search(r'<div class="gennin">.*?<span class="shurui">(.*?)</span>(.*?)</div>', t, re.S)
    a = re.search(r'<div class="answer"><strong>先に答え</strong>(.*?)</div>', t, re.S)
    first = re.split(r"(?<=。)", re.sub("<[^>]+>", "", a.group(1)))[0] if a else ""
    return h1, (g.group(1) if g else ""), first


def map_page():
    src = read("root3.html")
    head_end = src.index("<main>")
    head = src[:head_end]
    desc = "電験三種の三相交流と変圧器の計算で、手が止まる所は大きく7つ。止まる順に並べた地図です。1つずつ、答えと理由と確かめの1問のページにつながります。"
    head = re.sub(r"<title>.*?</title>", f"<title>{TITLE}｜筆算堂</title>", head)
    head = re.sub(r'(<meta name="description" content=")[^"]*', r"\g<1>" + desc, head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', r"\g<1>" + desc, head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', r"\g<1>" + TITLE + "｜筆算堂", head)
    head = head.replace("root3.html", MAP)
    head = head.replace('"og:type" content="article"', '"og:type" content="website"')
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\n', "", head)
    ld = ('<script type="application/ld+json">{"@context": "https://schema.org", "@type": "ItemList", "name": "' + TITLE + '", "itemListOrder": "https://schema.org/ItemListOrderAscending", "itemListElement": ['
          + ", ".join(f'{{"@type": "ListItem", "position": {i+1}, "url": "{BASE}{f}"}}' for i, (f, _, _) in enumerate(ORDER)) + "]}</script>\n")
    head = head.replace('<link rel="stylesheet"', ld + '<link rel="stylesheet"', 1)
    cards = []
    for i, (f, short, stop) in enumerate(ORDER):
        h1, shurui, first = info(f)
        cards.append(
            f'<li class="chizu-card"><span class="chizu-no">{NUM[i]}</span><div>'
            f'<a href="{f}" data-chizu="map">{html.escape(short)}：{html.escape(stop)}</a>'
            f'<p class="chizu-gennin"><span class="shurui">{shurui}</span></p>'
            f'<p class="chizu-ans">{first}</p></div></li>')
    foot = src[src.index("</main>"):]
    body = f"""<main>
<p class="crumb"><a href="./">トップ</a> › <a href="denken3.html">電験三種</a> › 三相と変圧器の地図</p>
<h1>{TITLE}</h1>
<p class="lead">電験三種で、三相交流と変圧器の計算に入ると、手が止まる所は大きく{N}つあります。上から順に、前の所が分かっていると次が楽になる並びです。読んだページには「読んだ」の印が付きます。</p>
<div class="answer"><strong>使い方</strong>上から順に読んでも、止まっている所だけ開いてもかまいません。どこで止まるか分からないときは、先に<a href="tenken.html" data-chizu="tenken">10問の点検</a>で、やり直す所を見つけてください。</div>
<ul class="list chizu">
{chr(10).join(cards)}
</ul>
<div class="cta cta-light"><p class="cta-need">{N}つのうち、どこで止まっているかを確かめたい</p><p>計算の10問を解くと、やり直す所と、読むページが分かります。約5分です。</p><a class="btn btn-sub" href="tenken.html" data-chizu="tenken" data-micro="約5分・採点は画面の中だけ">10問の点検を始める</a></div>
<p>この{N}つを、順を追って解く本：<a href="hon.html">本の案内</a></p>
<p class="updated">最終更新：2026年11月16日</p>
<p><a href="denken3.html">電験三種の入口へ戻る</a>　／　<a href="./">辞典のトップ</a></p>
"""
    (ROOT / MAP).write_text(head + body + foot, encoding="utf-8")


def pages():
    for i, (f, short, stop) in enumerate(ORDER):
        t = read(f)
        t = re.sub(r'<div class="chizu-ima">.*?</div>\n', "", t, flags=re.S)
        dots = "".join(
            f'<a href="{g}" data-chizu="dot" title="{html.escape(s)}" class="{"ima" if j == i else ""}">{NUM[j]}</a>'
            for j, (g, s, _) in enumerate(ORDER))
        ima = (f'<div class="chizu-ima"><p><a href="{MAP}" data-chizu="ima">三相と変圧器の地図</a>　'
               f'{N}つのうち <strong>{i+1}つ目</strong>：{html.escape(short)}</p>'
               f'<p class="chizu-dots">{dots}</p>'
               f'<p class="chizu-zentai">三相と変圧器の計算で止まる所は、大きく{N}つあります。このページは、その{i+1}つ目です。</p></div>\n')
        t = re.sub(r"(</h1>\n)", r"\1" + ima.replace("\\", "\\\\"), t, count=1)
        nxt = [ORDER[(i + k) % N] for k in (1, 2, 3)]
        items = "".join(f'<li><a href="{g}" data-chizu="next">{info(g)[0]}</a></li>' for g, _, _ in nxt)
        label = "次に止まりやすい所" if i + 3 < N else "同じ地図で、ほかに止まりやすい所"
        new_nav = (f'<nav class="next"><strong>{label}（{N}つのうち）</strong><ul class="list">{items}</ul>'
                   f'<p><a href="{MAP}" data-chizu="all">{N}つ全部を地図で見る</a></p></nav>')
        t = re.sub(r'<nav class="next">.*?</nav>', new_nav, t, count=1, flags=re.S)
        (ROOT / f).write_text(t, encoding="utf-8")


def entries():
    p = ROOT / "denken3.html"
    t = p.read_text(encoding="utf-8")
    box = (f'<div class="chizu-iriguchi"><a class="btn" href="{MAP}" data-chizu="iriguchi">三相と変圧器で止まる所の地図（{N}つ）</a>'
           f'<p>√3、三相の電力、力率、巻数比、%Z。止まる順に並べました。</p></div>\n')
    if MAP not in t:
        t = t.replace("<h2>止まる所から探す</h2>\n", "<h2>止まる所から探す</h2>\n" + box, 1)
        p.write_text(t, encoding="utf-8")
    p = ROOT / "ichiran.html"
    t = p.read_text(encoding="utf-8")
    if MAP not in t:
        t = t.replace("<h2>電験三種の解説</h2>\n<ul class=\"list\">\n", f'<h2>電験三種の解説</h2>\n<ul class="list">\n<li><a href="{MAP}">{TITLE}</a></li>\n', 1)
        t = re.sub(r"全部で (\d+) ページ", lambda m: f"全部で {int(m.group(1)) + 1} ページ", t)
        p.write_text(t, encoding="utf-8")
    url = BASE + MAP
    for name, add in (("sitemap.xml", f"<url><loc>{url}</loc><lastmod>2026-11-16</lastmod></url>\n</urlset>"),
                      ("sitemap-pages.xml", f"  <url>\n    <loc>{url}</loc>\n  </url>\n</urlset>")):
        p = ROOT / name
        t = p.read_text(encoding="utf-8")
        if url not in t:
            p.write_text(t.replace("</urlset>", add, 1), encoding="utf-8")
    p = ROOT / "sitemap.txt"
    t = p.read_text(encoding="utf-8")
    if url not in t:
        p.write_text(t.rstrip("\n") + "\n" + url + "\n", encoding="utf-8")


CSS = """
/* 地図の層（2026-11-16） */
.chizu-ima{border:1px solid var(--line);border-radius:6px;background:var(--paper);padding:.6em 1em;margin:.6em 0 1.2em;font-size:.9rem}
.chizu-ima p{margin:.2em 0}
.chizu-dots a{display:inline-block;min-width:1.9em;text-align:center;text-decoration:none;color:var(--sub);font-size:1.05rem}
.chizu-dots a.ima{color:var(--mark);font-weight:700}
.chizu-zentai{color:var(--sub)}
ul.chizu{list-style:none;padding:0}
.chizu-card{display:flex;gap:.8em;align-items:flex-start;border-bottom:1px solid var(--line);padding:.8em 0}
.chizu-no{font-size:1.5rem;line-height:1.2;color:var(--mark);font-weight:700}
.chizu-card a{font-weight:700;font-size:1.05rem}
.chizu-gennin,.chizu-ans{margin:.3em 0;font-size:.9rem}
.chizu-ans{color:var(--sub)}
.chizu-iriguchi{margin:.6em 0 1.4em}
.chizu-iriguchi p{margin:.4em 0;font-size:.9rem;color:var(--sub)}
"""


def css():
    p = ROOT / "style.css"
    t = p.read_text(encoding="utf-8")
    if "地図の層" not in t:
        p.write_text(t.rstrip("\n") + "\n" + CSS, encoding="utf-8")


if __name__ == "__main__":
    css()
    pages()
    map_page()
    entries()
    print("地図の層を足した:", MAP, "と", N, "ページ")
