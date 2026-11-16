#!/usr/bin/env python3
"""三相と変圧器のまとまりに「全体像の層」を足す（幅を先に見せる試し。2026-11-16 から）。

1. 全体像の頁 sansou-zentai.html を作る
   - 段の図（下の段が土台。上の段は下の段を使う）
   - 分野 × 止まる原因 の表（どの頁が、どの分野の、どの原因か）
   - 7問の点検。外した所が図と表の上で赤くなり、「苦手は少なく、ここだけ」と分かる
2. 7つの解説の頁に、小さな段の図（今の頁に印）を足す
3. 7つの解説の頁の「次に読む」を、止まる順の次の3つにする
4. 電験三種の入口・ページの一覧・頁の一覧（3種）に全体像を足す
何度かけても同じ結果になる。リンクには data-chizu を付け、m.js が chizu の行動として数える。
点検の結果は chizu_check（right、miss）として数える。

使い方: python3 .github/scripts/chizu_sansou.py [サイトの根のフォルダー]
"""
import html, json, math, re, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
BASE = "https://math-san-bit.github.io/denken/"
PAGE = "sansou-zentai.html"
OLD = "sansou-chizu.html"
TITLE = "三相と変圧器の計算を、俯瞰する"
NUM = "①②③④⑤⑥⑦⑧⑨"

# (頁, 短い名前, 分野, 段) 段は 0 が土台
ITEMS = [
    ("root3.html", "√3 を掛けるか割るか", "三相交流", 0),
    ("root3-to-3.html", "三相の電力", "三相交流", 1),
    ("youryou-denryuu.html", "容量から電流", "三相交流", 1),
    ("rikiritsu.html", "力率と無効電力", "力率", 2),
    ("henatsu-makisuu.html", "変圧器の巻数比", "変圧器", 2),
    ("tanraku-100.html", "短絡電流と %Z", "%Z", 3),
    ("kijun-youryou.html", "%Z の基準容量", "%Z", 3),
]
N = len(ITEMS)
FIELDS = ["三相交流", "力率", "変圧器", "%Z"]
DAN = ["土台", "2段目", "3段目", "てっぺん"]

# 点検の7問（頁の「確かめの1問」と同じ数値。ans は正しい選択肢の番号）
Q = [
    ("線間電圧 200 V の Y結線。相電圧は？", ["約 346 V", "約 115 V", "200 V"], 1),
    ("線間電圧 400 V、線電流 5 A、力率 0.8 の三相負荷の消費電力は？", ["約 2771 W", "約 8314 W", "1600 W"], 0),
    ("三相 100 kV·A、200 V の変圧器の定格電流は？", ["500 A", "約 289 A", "約 866 A"], 1),
    ("有効電力 60 kW、力率 0.6。皮相電力は？", ["36 kV·A", "40 kV·A", "100 kV·A"], 2),
    ("巻数比 33。二次側の 0.1 Ω を一次側に直すと？", ["3.3 Ω", "108.9 Ω", "約 0.003 Ω"], 1),
    ("定格電流 100 A、%Z ＝ 4%。短絡電流は？", ["2500 A", "4 A", "400 A"], 0),
    ("20 MV·A 基準で 6% の %Z を、10 MV·A 基準に直すと？", ["12%", "6%", "3%"], 2),
]
r3 = math.sqrt(3)
assert round(200 / r3) == 115 and round(200 * r3) == 346
assert round(r3 * 400 * 5 * 0.8) == 2771 and round(3 * r3 * 400 * 5 * 0.8) == 8314 and 400 * 5 * 0.8 == 1600
assert round(100000 / (r3 * 200)) == 289 and round(r3 * 500) == 866
assert round(60 / 0.6) == 100 and round(60 * 0.6) == 36
assert round(0.1 * 33 * 33, 1) == 108.9 and round(0.1 * 33, 1) == 3.3 and round(0.1 / 33, 3) == 0.003
assert 100 * 100 / 4 == 2500 and 100 * 4 / 100 == 4
assert 6 * 10 / 20 == 3 and 6 * 20 / 10 == 12
assert len(Q) == N


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def info(name):
    t = read(name)
    h1 = re.search(r"<h1>(.*?)</h1>", t).group(1)
    g = re.search(r'<div class="gennin">.*?<span class="shurui">(.*?)</span>', t, re.S)
    return h1, (g.group(1) if g else "")


def pyramid(cur=None, small=False):
    rows = []
    for d in range(len(DAN) - 1, -1, -1):
        cells = []
        for i, (f, short, field, dan) in enumerate(ITEMS):
            if dan != d:
                continue
            cls = "pz-box" + (" ima" if i == cur else "")
            cells.append(f'<a class="{cls}" data-i="{i}" href="{f}" data-chizu="{"pz" if small else "zentai"}">'
                         f'<span class="pz-no">{NUM[i]}</span><span class="pz-name">{html.escape(short)}</span></a>')
        rows.append(f'<div class="pz-row pz-d{d}"><span class="pz-dan">{DAN[d]}</span><div class="pz-cells">{"".join(cells)}</div></div>')
    return f'<div class="pz{" pz-small" if small else ""}">{"".join(rows)}</div>'


def matrix():
    causes = []
    for f, *_ in ITEMS:
        c = info(f)[1]
        if c and c not in causes:
            causes.append(c)
    head = "".join(f"<th>{html.escape(c)}</th>" for c in causes)
    body = []
    for fld in FIELDS:
        tds = []
        for c in causes:
            cell = "".join(f'<a class="mx-dot" data-i="{i}" href="{f}" data-chizu="matrix" title="{html.escape(s)}">{NUM[i]}</a>'
                           for i, (f, s, ff, _) in enumerate(ITEMS) if ff == fld and info(f)[1] == c)
            tds.append(f"<td>{cell}</td>")
        body.append(f'<tr><th scope="row">{fld}</th>{"".join(tds)}</tr>')
    return (f'<table class="mx"><thead><tr><th>分野＼止まる原因</th>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table>')


def check_block():
    qs = []
    for i, (q, opts, ans) in enumerate(Q):
        bs = "".join(f'<button type="button" class="btn-q" data-k="{k}">{html.escape(o)}</button>' for k, o in enumerate(opts))
        qs.append(f'<li class="zq" data-q="{i}" data-ans="{ans}"><p><span class="pz-no">{NUM[i]}</span>{html.escape(q)}</p>'
                  f'<p class="zq-opts">{bs}</p><p class="zq-res"></p></li>')
    return '<ol class="zq-list">' + "".join(qs) + "</ol>"


SCRIPT = r"""<script>
(function(){
  var names = __NAMES__, links = __LINKS__, N = names.length, done = {}, miss = [], NUMS = '①②③④⑤⑥⑦⑧⑨';
  function mark(i, ok){
    document.querySelectorAll('[data-i="' + i + '"]').forEach(function(e){ e.classList.remove('ok','ng'); e.classList.add(ok ? 'ok' : 'ng'); });
  }
  function summary(){
    var n = Object.keys(done).length, box = document.getElementById('zq-sum');
    if (n < N) { box.innerHTML = '<p>' + n + ' / ' + N + ' 問　答えた所から、上の図と表に色が付きます。</p>'; return; }
    if (!miss.length) {
      box.innerHTML = '<p class="zq-big">' + N + 'つ全部、止まらずに進めました。</p><p>このまとまりは土台ができています。ほかの分野は <a href="tenken.html" data-chizu="tenken">10問の点検</a>で確かめられます。</p>';
    } else {
      var ls = miss.map(function(i){ return '<li><a href="' + links[i] + '" data-chizu="tsubo">' + NUMS[i] + ' ' + names[i] + '</a></li>'; }).join('');
      box.innerHTML = '<p class="zq-big">' + N + 'つのうち、止まるのは ' + miss.length + 'つだけです。</p><p>赤くなった所が、つまずきのツボです。読むのは次のページだけで足ります。</p><ul class="list">' + ls + '</ul>';
    }
    try { if (window.jitenEvent) { window.jitenEvent('chizu_check', { right: N - miss.length, miss: miss.map(function(i){ return i + 1; }).join('-') || 'none' }); } } catch (e) {}
  }
  document.querySelectorAll('.zq').forEach(function(li){
    li.addEventListener('click', function(e){
      var b = e.target.closest ? e.target.closest('button') : null; if (!b) return;
      var i = +li.getAttribute('data-q'), ans = +li.getAttribute('data-ans'); if (done[i] !== undefined) return;
      var ok = +b.getAttribute('data-k') === ans;
      done[i] = ok; if (!ok) { miss.push(i); miss.sort(function(a, c){ return a - c; }); }
      li.querySelectorAll('button').forEach(function(x){ x.disabled = true; if (+x.getAttribute('data-k') === ans) { x.classList.add('right'); } });
      if (!ok) { b.classList.add('wrong'); }
      li.querySelector('.zq-res').innerHTML = ok ? '進めます' : 'ここで止まりやすい → <a href="' + links[i] + '" data-chizu="tsubo">解説を読む</a>';
      mark(i, ok); summary();
    });
  });
  summary();
})();
</script>
"""


def zentai_page():
    src = read("root3.html")
    head = src[: src.index("<main>")]
    desc = f"電験三種の三相交流と変圧器の計算で、手が止まる所は {N}つ。段の図と、分野と原因の表で全体を俯瞰し、{N}問で自分のつまずきのツボを見つけます。"
    head = re.sub(r"<title>.*?</title>", f"<title>{TITLE}｜筆算堂</title>", head)
    head = re.sub(r'(<meta name="description" content=")[^"]*', r"\g<1>" + desc, head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', r"\g<1>" + desc, head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', r"\g<1>" + TITLE + "｜筆算堂", head)
    head = head.replace("root3.html", PAGE).replace('"og:type" content="article"', '"og:type" content="website"')
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\n', "", head)
    ld = ('<script type="application/ld+json">{"@context": "https://schema.org", "@type": "ItemList", "name": "' + TITLE + '", "itemListOrder": "https://schema.org/ItemListOrderAscending", "itemListElement": ['
          + ", ".join(f'{{"@type": "ListItem", "position": {i+1}, "url": "{BASE}{f}"}}' for i, (f, *_r) in enumerate(ITEMS)) + "]}</script>\n")
    head = head.replace('<link rel="stylesheet"', ld + '<link rel="stylesheet"', 1)
    foot = src[src.index("</main>"):]
    script = SCRIPT.replace("__NAMES__", json.dumps([s for _, s, _, _ in ITEMS], ensure_ascii=False)).replace("__LINKS__", json.dumps([f for f, *_ in ITEMS]))
    body = f"""<main>
<p class="crumb"><a href="./">トップ</a> › <a href="denken3.html">電験三種</a> › 三相と変圧器の全体像</p>
<h1>{TITLE}</h1>
<p class="lead">三相交流と変圧器の計算で、手が止まる所は {N}つです。まず全体を俯瞰して、そのあと {N}問で、自分がどこで止まるかを確かめます。{N}つ全部が苦手という人は少なく、たいていは1つか2つで止まっています。</p>

<h2>全体像：段の図</h2>
<p>下の段が土台です。上の段の計算は、下の段の計算を使います。たとえば ⑥ の短絡電流は、③ の定格電流が出せないと解けません。</p>
{pyramid()}

<h2>全体像：分野と止まる原因の表</h2>
<p>同じ分野でも、止まる原因は違います。原因が同じ所は、同じ直し方で進めます。</p>
{matrix()}

<h2>自分のつまずきのツボを見つける（{N}問）</h2>
<p>選ぶと、その場で答えが出て、上の図と表に色が付きます。採点は画面の中だけで、答えはどこにも送りません。</p>
{check_block()}
<div id="zq-sum" class="zq-sum"></div>

<div class="cta cta-light"><p class="cta-need">ほかの分野も含めて、止まる所を確かめたい</p><p>電験三種の計算の10問を解くと、やり直す所と、読むページが分かります。約5分です。</p><a class="btn btn-sub" href="tenken.html" data-chizu="tenken" data-micro="約5分・採点は画面の中だけ">10問の点検を始める</a></div>
<p>この{N}つを、順を追って解く本：<a href="hon.html">本の案内</a></p>
<p class="updated">最終更新：2026年11月16日</p>
<p><a href="denken3.html">電験三種の入口へ戻る</a>　／　<a href="./">辞典のトップ</a></p>
{script}"""
    (ROOT / PAGE).write_text(head + body + foot, encoding="utf-8")
    old = ROOT / OLD
    if old.exists():
        old.unlink()


def pages():
    for i, (f, short, field, dan) in enumerate(ITEMS):
        t = read(f)
        t = re.sub(r'<div class="chizu-ima">[^\n]*\n', "", t)
        ima = (f'<div class="chizu-ima"><p><a href="{PAGE}" data-chizu="ima">三相と変圧器の全体像</a>　'
               f'止まる所は {N}つ。このページは {DAN[dan]}の <strong>{NUM[i]} {html.escape(short)}</strong></p>'
               f'{pyramid(cur=i, small=True)}</div>\n')
        t = re.sub(r"(</h1>\n)", lambda m: m.group(1) + ima, t, count=1)
        nxt = [ITEMS[(i + k) % N] for k in (1, 2, 3)]
        items = "".join(f'<li><a href="{g}" data-chizu="next">{info(g)[0]}</a></li>' for g, *_r in nxt)
        label = "次に止まりやすい所" if i + 3 < N else "同じまとまりで、ほかに止まりやすい所"
        new_nav = (f'<nav class="next"><strong>{label}（{N}つのうち）</strong><ul class="list">{items}</ul>'
                   f'<p><a href="{PAGE}" data-chizu="all">{N}つ全部を俯瞰して、自分のツボを見つける</a></p></nav>')
        t = re.sub(r'<nav class="next">.*?</nav>', new_nav, t, count=1, flags=re.S)
        t = t.replace(OLD, PAGE)
        (ROOT / f).write_text(t, encoding="utf-8")


def entries():
    url_old, url = BASE + OLD, BASE + PAGE
    p = ROOT / "denken3.html"
    t = p.read_text(encoding="utf-8")
    t = re.sub(r'<div class="chizu-iriguchi">[^\n]*\n', "", t)
    box = (f'<div class="chizu-iriguchi"><a class="btn" href="{PAGE}" data-chizu="iriguchi">三相と変圧器を俯瞰する（{N}つ）</a>'
           f'<p>√3、三相の電力、力率、巻数比、%Z。段の図と表で全体を見て、{N}問で自分のつまずきのツボを見つけます。</p></div>\n')
    t = t.replace("<h2>止まる所から探す</h2>\n", "<h2>止まる所から探す</h2>\n" + box, 1)
    p.write_text(t, encoding="utf-8")
    p = ROOT / "ichiran.html"
    t = p.read_text(encoding="utf-8")
    t = re.sub(r'<li><a href="sansou-(chizu|zentai)\.html">[^<]*</a></li>\n', "", t)
    t = t.replace("<h2>電験三種の解説</h2>\n<ul class=\"list\">\n", f'<h2>電験三種の解説</h2>\n<ul class="list">\n<li><a href="{PAGE}">{TITLE}</a></li>\n', 1)
    p.write_text(t, encoding="utf-8")
    for name, add in (("sitemap.xml", f"<url><loc>{url}</loc><lastmod>2026-11-16</lastmod></url>\n</urlset>"),
                      ("sitemap-pages.xml", f"  <url>\n    <loc>{url}</loc>\n  </url>\n</urlset>")):
        p = ROOT / name
        t = p.read_text(encoding="utf-8")
        t = t.replace(f"<url><loc>{url_old}</loc><lastmod>2026-11-16</lastmod></url>\n", "")
        t = t.replace(f"  <url>\n    <loc>{url_old}</loc>\n  </url>\n", "")
        if url not in t:
            t = t.replace("</urlset>", add, 1)
        p.write_text(t, encoding="utf-8")
    p = ROOT / "sitemap.txt"
    lines = [l for l in p.read_text(encoding="utf-8").split() if l != url_old]
    if url not in lines:
        lines.append(url)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


CSS = """
/* 全体像の層（2026-11-16） */
.chizu-ima{border:1px solid var(--line);border-radius:6px;background:var(--paper);padding:.6em .8em;margin:.6em 0 1.2em;font-size:.9rem}
.chizu-ima>p{margin:.1em 0 .5em}
.pz{display:flex;flex-direction:column;gap:6px;margin:1em 0}
.pz-row{display:flex;align-items:stretch;gap:8px}
.pz-dan{flex:0 0 4.2em;font-size:.75rem;color:var(--sub);display:flex;align-items:center}
.pz-cells{flex:1;display:flex;justify-content:center;gap:6px}
.pz-d3 .pz-cells{padding:0 10%}.pz-d2 .pz-cells{padding:0 5%}.pz-d1 .pz-cells{padding:0 2%}
.pz-box{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;border:1.5px solid var(--ink);border-radius:4px;background:var(--paper);color:var(--ink);text-decoration:none;padding:.35em .3em;line-height:1.35;font-size:.85rem}
.pz-d0 .pz-box{border-width:2.5px}
.pz-no{font-weight:700;margin-right:.2em}
.pz-small{margin:.2em 0}
.pz-small .pz-box{font-size:.72rem;padding:.2em .2em}
.pz-small .pz-dan{flex-basis:3.6em;font-size:.68rem}
.pz-box.ima{background:var(--mark);border-color:var(--mark);color:#fff}
.pz-box.ok,.mx-dot.ok{opacity:.4}
.pz-box.ng,.mx-dot.ng{background:var(--mark);border-color:var(--mark);color:#fff}
table.mx{width:100%;border-collapse:collapse;font-size:.85rem;margin:1em 0}
table.mx th,table.mx td{border:1px solid var(--line);padding:.4em .5em;text-align:center;vertical-align:middle}
table.mx thead th{font-size:.78rem;color:var(--sub);font-weight:400}
table.mx tbody th{white-space:nowrap}
.mx-dot{display:inline-block;width:2em;height:2em;line-height:2em;border:1.5px solid var(--ink);border-radius:999px;margin:.15em;text-decoration:none;color:var(--ink);font-weight:700;background:var(--paper)}
ol.zq-list{list-style:none;padding:0}
.zq{border-bottom:1px solid var(--line);padding:.6em 0}
.zq p{margin:.3em 0}
.zq-opts{display:flex;flex-wrap:wrap;gap:6px}
.btn-q{font:inherit;font-size:.9rem;padding:.35em .9em;border:1.5px solid var(--ink);border-radius:999px;background:var(--paper);color:var(--ink);cursor:pointer}
.btn-q.right{font-weight:700;border-width:2.5px}
.btn-q.wrong{border-color:var(--mark);color:var(--mark);text-decoration:line-through}
.zq-res{font-size:.88rem;color:var(--mark)}
.zq-sum{border:2px solid var(--ink);border-radius:6px;padding:.6em 1em;margin:1.2em 0;background:var(--paper)}
.zq-big{font-weight:700;font-size:1.1rem}
.chizu-iriguchi{margin:.6em 0 1.4em}
.chizu-iriguchi p{margin:.4em 0;font-size:.9rem;color:var(--sub)}
"""


def css():
    p = ROOT / "style.css"
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"\n/\* (地図|全体像)の層.*", "", t, flags=re.S)
    p.write_text(t.rstrip("\n") + "\n" + CSS, encoding="utf-8")


if __name__ == "__main__":
    css()
    pages()
    zentai_page()
    entries()
    print("全体像の層を足した:", PAGE, "と", N, "ページ")
