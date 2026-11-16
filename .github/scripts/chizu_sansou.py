#!/usr/bin/env python3
"""三相と変圧器のまとまりに「全体像の層」を足す（幅を先に見せる試し。2026-11-16 から）。

全体像の軸（漏れなく、重なりなく）
  範囲：電験三種の、三相交流（理論）と変圧器（機械）の計算問題。平衡の三相回路に限る。
  分け方：式を1つの換算ずつに分けると、どの1行も次の7種類のどれか1つに入る。
    ① 回路の計算（1相分の電圧 ↔ 電流）
    ② 相 ↔ 線
    ③ 1相分 ↔ 3相の合計
    ④ 有効 ↔ 無効 ↔ 皮相
    ⑤ 一次 ↔ 二次
    ⑥ 実の値 ↔ 百分率
    ⑦ 出力 ↔ 損失 ↔ 効率
  範囲の外（別のまとまり）：不平衡の三相回路、回転機（誘導機・同期機）、送配電線の電圧降下。

作る物
1. 全体像の頁 sansou-zentai.html：段の図、7種類 × 出る科目 の表、問題の型の分け方、7問のツボ探し
2. 7つの解説の頁に、小さな段の図（その頁の種類に印）。末尾は止まる順の次の3つ
3. 電験三種の入口・ページの一覧・頁の一覧（3種）に全体像を足す
何度かけても同じ結果になる。リンクには data-chizu を付け、m.js が chizu の行動として数える。
ツボ探しの結果は chizu_check（right、miss）として数える。

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
DAN = ["土台", "2段目", "3段目", "4段目", "てっぺん"]

# 7種類：(短い名前, 何と何の行き来か, 段, 理論の三相回路で出る形, 機械の変圧器で出る形, 解説の頁)
CATS = [
    ("回路の計算", "1相分の電圧 ↔ 電流", 0,
     "1相分の V ＝ Z × I", "等価回路", []),
    ("相 ↔ 線", "相電圧・相電流 ↔ 線間電圧・線電流", 1,
     "Y・Δ、Y-Δの置き換え", "Δ-Y の結線、V結線", ["root3.html"]),
    ("1相 ↔ 3相", "1相分の電力・容量 ↔ 3相の合計", 1,
     "三相の電力", "容量と定格電流", ["root3-to-3.html", "youryou-denryuu.html"]),
    ("有効 ↔ 無効 ↔ 皮相", "kW ↔ kvar ↔ kV·A", 2,
     "力率、力率の改善", "負荷の力率", ["rikiritsu.html"]),
    ("一次 ↔ 二次", "巻線の片側の値 ↔ 反対側の値", 3,
     "（出ない）", "巻数比、2乗の換算", ["henatsu-makisuu.html"]),
    ("実の値 ↔ 百分率", "Ω・V・A ↔ %", 4,
     "（出ない）", "%Z、短絡電流、電圧変動率、並行運転", ["tanraku-100.html", "kijun-youryou.html"]),
    ("出力 ↔ 損失 ↔ 効率", "出力・鉄損・銅損 ↔ 効率", 4,
     "（出ない）", "鉄損と銅損、効率、全日効率", []),
]
N = len(CATS)

# 問題の型を、7種類の組み合わせで書く（科目, 型, 種類の番号の並び）
TYPES = [
    ("理論", "Δ結線の負荷の消費電力", [0, 1, 2]),
    ("理論", "力率を改善するコンデンサの容量", [3, 1, 0]),
    ("機械", "三相変圧器の定格電流", [2]),
    ("機械", "変圧器の短絡電流", [2, 5]),
    ("機械", "電圧変動率", [5, 3]),
    ("機械", "二次側の抵抗を一次側から見た値", [4]),
    ("機械", "並行運転の負荷の分担", [5]),
    ("機械", "最大効率・全日効率", [6, 3]),
    ("機械", "V結線の出力", [1, 2]),
]

# ツボ探しの7問（種類ごとに1問。ans は正しい選択肢の番号）
Q = [
    ("相電圧 100 V、1相のインピーダンス 6 ＋ j8 Ω。相電流は？", ["10 A", "約 7.1 A", "約 16.7 A"], 0),
    ("線間電圧 200 V の Y結線。相電圧は？", ["約 346 V", "約 115 V", "200 V"], 1),
    ("三相 100 kV·A、200 V の変圧器の定格電流は？", ["500 A", "約 289 A", "約 866 A"], 1),
    ("有効電力 60 kW、力率 0.6。皮相電力は？", ["36 kV·A", "40 kV·A", "100 kV·A"], 2),
    ("巻数比 33。二次側の 0.1 Ω を一次側に直すと？", ["3.3 Ω", "108.9 Ω", "約 0.003 Ω"], 1),
    ("定格電流 100 A、%Z ＝ 4%。短絡電流は？", ["2500 A", "4 A", "400 A"], 0),
    ("鉄損 100 W、全負荷の銅損 400 W。負荷が半分のときの銅損は？", ["200 W", "100 W", "400 W"], 1),
]
r3 = math.sqrt(3)
assert abs(complex(6, 8)) == 10 and round(100 / 14, 1) == 7.1 and round(100 / 6, 1) == 16.7
assert round(200 / r3) == 115 and round(200 * r3) == 346
assert round(100000 / (r3 * 200)) == 289 and round(r3 * 500) == 866
assert round(60 / 0.6) == 100 and round(60 * 0.6) == 36
assert round(0.1 * 33 * 33, 1) == 108.9 and round(0.1 * 33, 1) == 3.3 and round(0.1 / 33, 3) == 0.003
assert 100 * 100 / 4 == 2500 and 100 * 4 / 100 == 4
assert 400 * 0.5 ** 2 == 100 and 400 * 0.5 == 200
assert len(Q) == N

ORDER = [f for c in CATS for f in c[5]]          # 止まる順（解説の頁）
CAT_OF = {f: i for i, c in enumerate(CATS) for f in c[5]}


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def h1_of(name):
    return re.search(r"<h1>(.*?)</h1>", read(name)).group(1)


def cat_href(i):
    return CATS[i][5][0] if CATS[i][5] else f"{PAGE}#k{i+1}"


def pyramid(cur=None, small=False):
    rows = []
    for d in range(len(DAN) - 1, -1, -1):
        cells = []
        for i, c in enumerate(CATS):
            if c[2] != d:
                continue
            cls = "pz-box" + (" ima" if i == cur else "") + ("" if c[5] else " mada")
            cells.append(f'<a class="{cls}" data-i="{i}" href="{cat_href(i)}" data-chizu="{"pz" if small else "zentai"}">'
                         f'<span class="pz-no">{NUM[i]}</span><span class="pz-name">{html.escape(c[0])}</span></a>')
        rows.append(f'<div class="pz-row pz-d{d}"><span class="pz-dan">{DAN[d]}</span><div class="pz-cells">{"".join(cells)}</div></div>')
    return f'<div class="pz{" pz-small" if small else ""}">{"".join(rows)}</div>'


def matrix():
    body = []
    for i, c in enumerate(CATS):
        pages = "".join(f'<a href="{f}" data-chizu="matrix">{h1_of(f).split("：")[0]}</a>' for f in c[5]) or '<span class="mada-txt">解説は準備中</span>'
        cell = lambda s: '<span class="nashi">―</span>' if s.startswith("（") else f'<span class="maru">●</span>{html.escape(s)}'
        body.append(f'<tr id="k{i+1}"><th scope="row"><span class="mx-dot" data-i="{i}">{NUM[i]}</span>{html.escape(c[0])}<span class="mx-pages">{pages}</span></th>'
                    f'<td>{cell(c[3])}</td><td>{cell(c[4])}</td></tr>')
    return ('<table class="mx"><thead><tr><th>種類（と解説）</th><th>理論：三相回路</th><th>機械：変圧器</th></tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table>')


def types_block():
    rows = []
    for subj, name, seq in TYPES:
        chips = '<span class="ty-arrow">→</span>'.join(f'<span class="ty-chip" data-i="{k}">{NUM[k]} {html.escape(CATS[k][0])}</span>' for k in seq)
        rows.append(f'<li><span class="ty-subj">{subj}</span><span class="ty-name">{html.escape(name)}</span><span class="ty-seq">{chips}</span></li>')
    return '<ul class="ty">' + "".join(rows) + "</ul>"


def check_block():
    qs = []
    for i, (q, opts, ans) in enumerate(Q):
        bs = "".join(f'<button type="button" class="btn-q" data-k="{k}">{html.escape(o)}</button>' for k, o in enumerate(opts))
        qs.append(f'<li class="zq" data-q="{i}" data-ans="{ans}"><p><span class="pz-no">{NUM[i]}</span><span class="zq-kind">{html.escape(CATS[i][0])}</span>{html.escape(q)}</p>'
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
      box.innerHTML = '<p class="zq-big">' + N + '種類とも、止まらずに進めました。</p><p>このまとまりは土台ができています。ほかの分野は <a href="tenken.html" data-chizu="tenken">10問の点検</a>で確かめられます。</p>';
    } else {
      var ls = miss.map(function(i){ return '<li><a href="' + links[i] + '" data-chizu="tsubo">' + NUMS[i] + ' ' + names[i] + '</a></li>'; }).join('');
      box.innerHTML = '<p class="zq-big">' + N + '種類のうち、止まるのは ' + miss.length + '種類だけです。</p><p>赤くなった所が、つまずきのツボです。上の「問題の型」で赤い札が付いた型は、その種類を直せば解けるようになります。</p><ul class="list">' + ls + '</ul>';
    }
    try { if (window.jitenEvent) { window.jitenEvent('chizu_check', { right: N - miss.length, miss: miss.map(function(i){ return i + 1; }).join('-') || 'none' }); } } catch (e) {}
  }
  document.querySelectorAll('.zq').forEach(function(li){
    li.addEventListener('click', function(e){
      var b = e.target.closest ? e.target.closest('button') : null; if (!b) return;
      var i = +li.getAttribute('data-q'), ans = +li.getAttribute('data-ans'); if (done[i] !== undefined) return;
      var ok = +b.getAttribute('data-k') === ans;
      done[i] = ok; if (!ok) { miss.push(i); miss.sort(function(a, c){ return a - c; }); }
      li.querySelectorAll('button').forEach(function(x){ x.disabled = true; if (+x.getAttribute('data-k') === ans) { x.classList.add("zq-right"); } });
      if (!ok) { b.classList.add("zq-wrong"); }
      var rs = li.querySelector('.zq-res'); if (!ok) { rs.classList.add('ng'); }
      rs.innerHTML = ok ? '進めます' : 'ここで止まりやすい → <a href="' + links[i] + '" data-chizu="tsubo">' + (links[i].indexOf('#') >= 0 ? '解説は準備中（表の行へ）' : '解説を読む') + '</a>';
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
    desc = "電験三種の三相交流と変圧器の計算は、式を分けると7種類の換算のどれかに入ります。段の図と表で全体を俯瞰し、7問で自分のつまずきのツボを見つけます。"
    head = re.sub(r"<title>.*?</title>", f"<title>{TITLE}｜筆算堂</title>", head)
    head = re.sub(r'(<meta name="description" content=")[^"]*', r"\g<1>" + desc, head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', r"\g<1>" + desc, head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', r"\g<1>" + TITLE + "｜筆算堂", head)
    head = head.replace("root3.html", PAGE).replace('"og:type" content="article"', '"og:type" content="website"')
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\n', "", head)
    ld = ('<script type="application/ld+json">{"@context": "https://schema.org", "@type": "ItemList", "name": "' + TITLE + '", "itemListOrder": "https://schema.org/ItemListOrderAscending", "itemListElement": ['
          + ", ".join(f'{{"@type": "ListItem", "position": {k+1}, "url": "{BASE}{f}"}}' for k, f in enumerate(ORDER)) + "]}</script>\n")
    head = head.replace('<link rel="stylesheet"', ld + '<link rel="stylesheet"', 1)
    foot = src[src.index("</main>"):]
    script = SCRIPT.replace("__NAMES__", json.dumps([c[0] for c in CATS], ensure_ascii=False)).replace("__LINKS__", json.dumps([cat_href(i) for i in range(N)]))
    body = f"""<main>
<p class="crumb"><a href="./">トップ</a> › <a href="denken3.html">電験三種</a> › 三相と変圧器の全体像</p>
<h1>{TITLE}</h1>
<p class="lead">電験三種の、三相交流（理論）と変圧器（機械）の計算問題は、式を1行ずつに分けると、どの行も下の {N}種類のどれか1つに入ります。まず全体を俯瞰して、そのあと {N}問で、自分がどの種類で止まるかを確かめます。</p>
<div class="answer"><strong>分け方</strong>1行の式が「何を何に換えているか」で分けます。たとえば √3 × V × I × cosθ は、③ 1相 ↔ 3相 と ④ 有効 ↔ 無効 ↔ 皮相 の2行をまとめて書いた物です。ここで扱うのは平衡の三相回路です。不平衡の三相回路、回転機（誘導機・同期機）、送配電線の電圧降下は、別のまとまりとして扱います。</div>

<h2>全体像：段の図</h2>
<p>下の段が土台です。上の段の計算は、下の段の計算を使います。たとえば ⑥ の短絡電流は、③ で定格電流が出せないと解けません。点線の箱は、解説を準備中の種類です。</p>
{pyramid()}

<h2>全体像：{N}種類と、出る科目の表</h2>
<p>横に見ると、その種類が理論と機械のどこで出るかが分かります。⑤〜⑦ は機械（変圧器）だけで出ます。</p>
{matrix()}

<h2>問題の型は、{N}種類の組み合わせ</h2>
<p>よく出る問題の型を、使う種類の順に並べました。どの型も、上の {N}種類の札だけで書けます。</p>
{types_block()}

<h2>自分のつまずきのツボを見つける（{N}問）</h2>
<p>1種類に1問です。選ぶと、その場で答えが出て、上の図・表・問題の型に色が付きます。採点は画面の中だけで、答えはどこにも送りません。</p>
{check_block()}
<div id="zq-sum" class="zq-sum"></div>

<div class="cta cta-light"><p class="cta-need">ほかの分野も含めて、止まる所を確かめたい</p><p>電験三種の計算の10問を解くと、やり直す所と、読むページが分かります。約5分です。</p><a class="btn btn-sub" href="tenken.html" data-chizu="tenken" data-micro="約5分・採点は画面の中だけ">10問の点検を始める</a></div>
<p>この計算を、順を追って解く本：<a href="hon.html">本の案内</a></p>
<p class="updated">最終更新：2026年11月16日</p>
<p><a href="denken3.html">電験三種の入口へ戻る</a>　／　<a href="./">辞典のトップ</a></p>
{script}"""
    (ROOT / PAGE).write_text(head + body + foot, encoding="utf-8")
    old = ROOT / OLD
    if old.exists():
        old.unlink()


def pages():
    for k, f in enumerate(ORDER):
        i = CAT_OF[f]
        t = read(f)
        t = re.sub(r'<div class="chizu-ima">[^\n]*\n', "", t)
        ima = (f'<div class="chizu-ima"><p><a href="{PAGE}" data-chizu="ima">三相と変圧器の全体像</a>　'
               f'計算は {N}種類。このページは {DAN[CATS[i][2]]}の <strong>{NUM[i]} {html.escape(CATS[i][0])}</strong></p>'
               f'{pyramid(cur=i, small=True)}</div>\n')
        t = re.sub(r"(</h1>\n)", lambda m: m.group(1) + ima, t, count=1)
        M = len(ORDER)
        nxt = [ORDER[(k + j) % M] for j in (1, 2, 3)]
        items = "".join(f'<li><a href="{g}" data-chizu="next">{h1_of(g)}</a></li>' for g in nxt)
        label = "次に止まりやすい所" if k + 3 < M else "同じまとまりで、ほかに止まりやすい所"
        new_nav = (f'<nav class="next"><strong>{label}</strong><ul class="list">{items}</ul>'
                   f'<p><a href="{PAGE}" data-chizu="all">全体を俯瞰して、自分のツボを見つける（{N}問）</a></p></nav>')
        t = re.sub(r'<nav class="next">.*?</nav>', new_nav, t, count=1, flags=re.S)
        t = t.replace(OLD, PAGE)
        (ROOT / f).write_text(t, encoding="utf-8")


def entries():
    url_old, url = BASE + OLD, BASE + PAGE
    p = ROOT / "denken3.html"
    t = p.read_text(encoding="utf-8")
    t = re.sub(r'<div class="chizu-iriguchi">[^\n]*\n', "", t)
    box = (f'<div class="chizu-iriguchi"><a class="btn" href="{PAGE}" data-chizu="iriguchi">三相と変圧器を俯瞰する</a>'
           f'<p>三相交流と変圧器の計算は、{N}種類の換算に分けられます。段の図と表で全体を見て、{N}問で自分のつまずきのツボを見つけます。</p></div>\n')
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
.pz-dan{flex:0 0 4.4em;font-size:.75rem;color:var(--sub);display:flex;align-items:center;white-space:nowrap}
.pz-cells{flex:1;display:flex;justify-content:center;gap:6px}
.pz-d4 .pz-cells{padding:0 8%}.pz-d3 .pz-cells{padding:0 22%}.pz-d2 .pz-cells{padding:0 14%}.pz-d1 .pz-cells{padding:0 3%}
.pz-box{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;border:1.5px solid var(--ink);border-radius:4px;background:var(--paper);color:var(--ink);text-decoration:none;padding:.35em .3em;line-height:1.35;font-size:.85rem}
.pz-box.mada{border-style:dashed}
.pz-d0 .pz-box{border-width:2.5px}
.pz-no{font-weight:700;margin-right:.2em}
.pz-small{margin:.2em 0}
.pz-small .pz-box{font-size:.72rem;padding:.2em .2em}
.pz-small .pz-dan{flex-basis:4.4em;font-size:.68rem}
.pz-box.ima{background:var(--mark);border-color:var(--mark);color:#fff}
.pz-box.ok,.mx-dot.ok,.ty-chip.ok{opacity:.4}
.pz-box.ng,.mx-dot.ng,.ty-chip.ng{background:var(--mark);border-color:var(--mark);color:#fff}
table.mx{width:100%;border-collapse:collapse;font-size:.8rem;margin:1em 0;table-layout:fixed}
table.mx thead th:first-child{width:42%}
table.mx th,table.mx td{border:1px solid var(--line);padding:.45em .5em;text-align:left;vertical-align:top}
table.mx thead th{font-size:.76rem;color:var(--sub);font-weight:400}
table.mx tbody th{font-weight:700}
.mx-pages{display:block;font-weight:400;font-size:.72rem;margin-top:.2em}
.mx-pages a{display:block}
.maru{color:var(--ink);margin-right:.2em;font-size:.7rem}
.nashi,.mada-txt{color:var(--sub)}
.mx-dot{display:inline-block;width:1.8em;height:1.8em;line-height:1.8em;text-align:center;border:1.5px solid var(--ink);border-radius:999px;margin-right:.3em;color:var(--ink);font-weight:700;background:var(--paper)}
ul.ty{list-style:none;padding:0;margin:1em 0}
ul.ty li{display:flex;flex-wrap:wrap;align-items:center;gap:.3em .5em;border-bottom:1px solid var(--line);padding:.5em 0}
.ty-subj{font-size:.72rem;border:1px solid var(--sub);color:var(--sub);border-radius:3px;padding:0 .4em}
.ty-name{font-weight:700;font-size:.92rem}
.ty-seq{flex-basis:100%;display:flex;flex-wrap:wrap;align-items:center;gap:.3em}
.ty-chip{font-size:.78rem;border:1.5px solid var(--ink);border-radius:999px;padding:0 .6em;background:var(--paper)}
.ty-arrow{color:var(--sub);font-size:.8rem}
ol.zq-list{list-style:none;padding:0}
.zq{border-bottom:1px solid var(--line);padding:.6em 0}
.zq p{margin:.3em 0}
.zq-kind{display:inline-block;font-size:.75rem;border:1px solid var(--sub);color:var(--sub);border-radius:3px;padding:0 .4em;margin-right:.4em}
.zq-opts{display:flex;flex-wrap:wrap;gap:6px}
.btn-q{font:inherit;font-size:.9rem;padding:.35em .9em;border:1.5px solid var(--ink);border-radius:999px;background:var(--paper);color:var(--ink);cursor:pointer}
.btn-q.zq-right{font-weight:700;border-width:2.5px}
.btn-q.zq-wrong{border-color:var(--mark);color:var(--mark);text-decoration:line-through}
.zq-res{font-size:.88rem;color:var(--sub)}
.zq-res.ng{color:var(--mark)}
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
    print("全体像の層を足した:", PAGE, "と", len(ORDER), "ページ")
