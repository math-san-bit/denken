#!/usr/bin/env python3
"""三相と変圧器のまとまりに「全体像の層」を足す（幅を先に見せる試し。2026-11-16 から）。

全体像の軸（漏れなく、重なりなく）
  範囲：電験三種の、三相交流（理論）と変圧器（機械）の計算問題。平衡の三相回路に限る。
  縦の軸：参考書の章（9章）。どの問題も、どれか1つの章に入る。
  横の軸：解く途中の段（4段）。Newman の誤り分析（1977）の段を、電験の計算に合わせてまとめた。
    読み取り → 立式 → 計算 → 確かめ
  ツボ探し：9章に1問ずつ。まちがいの選択肢は、どの段で止まったかに1つずつ結び付けてある。
  確かめの段は、選んだ答えが「確かめの決まり」（例：Y結線の相電圧は線間電圧より小さい）に反するときに印を付ける。

作る物
1. 全体像の頁 sansou-zentai.html：体系図、9章 × 4段の表、4段の説明、9問のツボ探し
2. 解説の頁に、小さな体系図（その頁の章に印）。末尾は止まる順の次の3つ
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

STAGES = [
    ("読み取り", "与えられた量と条件をつかむ", "線間か相か、Y か Δ か、単相か三相か、どちら側の値か"),
    ("立式", "使う決まりと式を選ぶ", "√3 を入れるか、巻数比を2乗するか、掛けるか割るか"),
    ("計算", "数を処理する", "分数、√、累乗、単位と桁"),
    ("確かめ", "答えの大きさと単位を見る", "短絡電流が定格電流より小さければ、どこかが逆"),
]
S = len(STAGES)

# 9章：(章の名前, 分野, 解説の頁)
CHAPS = [
    ("Y結線とΔ結線", "理論", ["root3.html"]),
    ("三相の電力と容量", "理論", ["root3-to-3.html", "youryou-denryuu.html"]),
    ("力率と力率の改善", "理論", ["rikiritsu.html"]),
    ("巻数比と等価回路", "機械", ["henatsu-makisuu.html"]),
    ("損失と効率", "機械", []),
    ("電圧変動率", "機械", []),
    ("%Z と短絡電流", "機械", ["tanraku-100.html", "kijun-youryou.html"]),
    ("並行運転", "機械", []),
    ("三相の結線とV結線", "機械", []),
]
N = len(CHAPS)
FIELD_NOTE = {
    "理論": "三相交流（Y-Δ の置き換え、二電力計法を含む）",
    "機械": "変圧器（無負荷試験・短絡試験、単巻変圧器を含む）",
}

# ツボ探しの9問：(問い, [(選択肢, 段 or None(正解), 確かめに反するか)], 確かめの決まり)
R, T, K = 0, 1, 2  # 読み取り・立式・計算
Q = [
    ("線間電圧 200 V の Y結線。相電圧は？",
     [("約 115 V", None, False), ("200 V", R, False), ("約 346 V", T, True), ("約 1155 V", K, True)],
     "Y結線の相電圧は、線間電圧より小さい"),
    ("線間電圧 400 V、線電流 5 A、力率 0.8 の三相負荷の消費電力は？",
     [("約 2771 W", None, False), ("1600 W", R, False), ("約 8314 W", T, False), ("約 277 W", K, True)],
     "三相の電力は、同じ電圧と電流の単相の電力（1600 W）より大きい"),
    ("有効電力 60 kW、力率 0.6。皮相電力は？",
     [("100 kV·A", None, False), ("60 kV·A", R, True), ("36 kV·A", T, True), ("10 kV·A", K, True)],
     "皮相電力は、有効電力より大きい"),
    ("巻数比 33。二次側（低圧側）の 0.1 Ω を一次側（高圧側）に直すと？",
     [("108.9 Ω", None, False), ("約 0.000092 Ω", R, True), ("3.3 Ω", T, False), ("10.89 Ω", K, False)],
     "高圧側に直したインピーダンスは、元より大きくなる"),
    ("鉄損 100 W、全負荷の銅損 400 W。負荷が半分のときの損失の合計は？",
     [("200 W", None, False), ("100 W", R, True), ("300 W", T, False), ("110 W", K, False)],
     "損失の合計は、鉄損（100 W）より大きい"),
    ("百分率抵抗降下 2%、百分率リアクタンス降下 3%、遅れ力率 0.8。電圧変動率はおよそ？",
     [("3.4%", None, False), ("5%", R, False), ("3.6%", T, False), ("34%", K, True)],
     "電圧変動率は、2% ＋ 3% ＝ 5% を超えない"),
    ("定格電流 100 A、%Z ＝ 4%。短絡電流は？",
     [("2500 A", None, False), ("25 A", R, True), ("4 A", T, True), ("250 A", K, False)],
     "短絡電流は、定格電流より大きい"),
    ("容量の等しい変圧器 A（%Z 4%）と B（%Z 6%）を並行運転し、合計 100 kV·A の負荷をかける。A の分担は？",
     [("60 kV·A", None, False), ("50 kV·A", R, True), ("40 kV·A", T, True), ("6 kV·A", K, True)],
     "%Z の小さいほうが、多く分担する"),
    ("10 kV·A の単相変圧器 2台を V結線にしたときの、三相の出力は？",
     [("約 17.3 kV·A", None, False), ("30 kV·A", R, False), ("20 kV·A", T, False), ("約 1.73 kV·A", K, True)],
     "2台の出力は、1台分（10 kV·A）より大きい"),
]
r3 = math.sqrt(3)
assert round(200 / r3) == 115 and round(200 * r3) == 346 and round(2000 / r3) == 1155
assert round(r3 * 400 * 5 * .8) == 2771 and round(3 * r3 * 400 * 5 * .8) == 8314 and 400 * 5 * .8 == 1600
assert round(60 / .6) == 100 and round(60 * .6) == 36
assert round(.1 * 33 ** 2, 1) == 108.9 and round(.1 / 33 ** 2, 6) == 0.000092 and round(.1 * 33, 1) == 3.3
assert 400 * .5 ** 2 + 100 == 200 and 400 * .5 + 100 == 300 and round(400 * .025 + 100) == 110
assert round(2 * .8 + 3 * .6, 2) == 3.4 and round(2 * .6 + 3 * .8, 2) == 3.6
assert 100 * 100 / 4 == 2500 and 100 / 4 == 25 and 100 * 4 / 100 == 4
assert 100 * 6 / (4 + 6) == 60 and 100 * 4 / (4 + 6) == 40
assert round(r3 * 10, 1) == 17.3
assert len(Q) == N and all(sum(1 for o in q[1] if o[1] is None) == 1 for q in Q)

ORDER = [f for c in CHAPS for f in c[2]]
CHAP_OF = {f: i for i, c in enumerate(CHAPS) for f in c[2]}


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def h1_of(name):
    return re.search(r"<h1>(.*?)</h1>", read(name)).group(1)


def chap_href(i):
    return CHAPS[i][2][0] if CHAPS[i][2] else f"{PAGE}#k{i+1}"


def tree(cur=None, small=False):
    cols = []
    for fld, label in (("理論", "理論：三相交流"), ("機械", "機械：変圧器")):
        boxes = "".join(
            f'<a class="tr-box{" ima" if i == cur else ""}{"" if c[2] else " mada"}" data-i="{i}" href="{chap_href(i)}" data-chizu="{"tr" if small else "zentai"}">'
            f'<span class="pz-no">{NUM[i]}</span>{html.escape(c[0])}</a>'
            for i, c in enumerate(CHAPS) if c[1] == fld)
        cols.append(f'<div class="tr-col"><p class="tr-head">{label}</p>{boxes}</div>')
    root = '' if small else '<p class="tr-root">三相と変圧器の計算（9章）</p>'
    return f'<div class="tr{" tr-small" if small else ""}">{root}<div class="tr-cols">{"".join(cols)}</div></div>'


def matrix():
    head = "".join(f'<th>{s[0]}</th>' for s in STAGES)
    body = []
    for i, c in enumerate(CHAPS):
        pages = "".join(f'<a href="{f}" data-chizu="matrix">{h1_of(f).split("：")[0]}</a>' for f in c[2]) or '<span class="mada-txt">解説は準備中</span>'
        tds = "".join(f'<td class="mx-c" data-cell="{i}-{s}"></td>' for s in range(S))
        body.append(f'<tr id="k{i+1}"><th scope="row"><span class="mx-dot" data-i="{i}">{NUM[i]}</span>{html.escape(c[0])}<span class="mx-pages">{pages}</span></th>{tds}</tr>')
    return (f'<table class="mx"><thead><tr><th>章＼止まった段</th>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>')


def stages_block():
    rows = "".join(f'<li><span class="st-no">{k+1}</span><div><strong>{s[0]}</strong>：{s[1]}<br><span class="st-ex">例：{s[2]}</span></div></li>'
                   for k, s in enumerate(STAGES))
    return f'<ol class="st">{rows}</ol>'


def check_block():
    qs = []
    for i, (q, opts, rule) in enumerate(Q):
        shift = (i * 3 + 1) % len(opts)            # 正解の位置を問いごとにずらす（決まった並び）
        order = opts[shift:] + opts[:shift]
        bs = "".join(f'<button type="button" class="btn-q" data-s="{"ok" if s is None else s}" data-k="{1 if k else 0}">{html.escape(o)}</button>'
                     for o, s, k in order)
        qs.append(f'<li class="zq" data-q="{i}" data-rule="{html.escape(rule)}"><p><span class="pz-no">{NUM[i]}</span><span class="zq-kind">{html.escape(CHAPS[i][0])}</span>{html.escape(q)}</p>'
                  f'<p class="zq-opts">{bs}</p><p class="zq-res"></p></li>')
    return '<ol class="zq-list">' + "".join(qs) + "</ol>"


SCRIPT = r"""<script>
(function(){
  var names = __NAMES__, links = __LINKS__, stages = __STAGES__, N = names.length, done = {}, miss = [], NUMS = '①②③④⑤⑥⑦⑧⑨';
  function cell(i, s){ var c = document.querySelector('[data-cell="' + i + '-' + s + '"]'); if (c) { c.classList.add('ng'); c.textContent = '●'; } }
  function rowok(i){ document.querySelectorAll('[data-i="' + i + '"]').forEach(function(e){ e.classList.add('ok'); }); document.querySelectorAll('[data-cell^="' + i + '-"]').forEach(function(c){ c.classList.add('okrow'); }); }
  function rowng(i){ document.querySelectorAll('[data-i="' + i + '"]').forEach(function(e){ e.classList.add('ng'); }); }
  function summary(){
    var n = Object.keys(done).length, box = document.getElementById('zq-sum');
    if (n < N) { box.innerHTML = '<p>' + n + ' / ' + N + ' 問　答えた所から、上の図と表に印が付きます。</p>'; return; }
    if (!miss.length) {
      box.innerHTML = '<p class="zq-big">' + N + '章とも、止まらずに進めました。</p><p>このまとまりは土台ができています。ほかの分野は <a href="tenken.html" data-chizu="tenken">10問の点検</a>で確かめられます。</p>';
    } else {
      var cnt = [0, 0, 0, 0];
      miss.forEach(function(m){ cnt[m.s]++; if (m.k) cnt[3]++; });
      var top = 0; for (var s = 1; s < 3; s++) { if (cnt[s] > cnt[top]) top = s; }
      var ls = miss.map(function(m){ return '<li><a href="' + links[m.i] + '" data-chizu="tsubo">' + NUMS[m.i] + ' ' + names[m.i] + '</a>　<span class="zq-st">' + stages[m.s] + 'の段</span></li>'; }).join('');
      box.innerHTML = '<p class="zq-big">' + N + '章のうち、止まるのは ' + miss.length + '章だけです。</p>'
        + '<p>止まった段で見ると、いちばん多いのは「' + stages[top] + '」です（読み取り ' + cnt[0] + '、立式 ' + cnt[1] + '、計算 ' + cnt[2] + '）。' + (cnt[3] ? 'そのうち ' + cnt[3] + 'つは、最後に「確かめ」をすれば気付けた答えです。' : '') + '表の●が、つまずきのツボです。</p><ul class="list">' + ls + '</ul>';
    }
    try { if (window.jitenEvent) { window.jitenEvent('chizu_check', { right: N - miss.length, miss: miss.map(function(m){ return (m.i + 1) + ':' + 'RTK'[m.s] + (m.k ? 'C' : ''); }).join('-') || 'none' }); } } catch (e) {}
  }
  document.querySelectorAll('.zq').forEach(function(li){
    li.addEventListener('click', function(e){
      var b = e.target.closest ? e.target.closest('button') : null; if (!b) return;
      var i = +li.getAttribute('data-q'); if (done[i] !== undefined) return;
      var s = b.getAttribute('data-s'), ok = s === 'ok';
      done[i] = ok;
      li.querySelectorAll('button').forEach(function(x){ x.disabled = true; if (x.getAttribute('data-s') === 'ok') { x.classList.add("zq-right"); } });
      var rs = li.querySelector('.zq-res');
      if (ok) { rs.innerHTML = '進めます'; rowok(i); }
      else {
        s = +s; var k = b.getAttribute('data-k') === '1';
        miss.push({ i: i, s: s, k: k }); miss.sort(function(a, c){ return a.i - c.i; });
        b.classList.add("zq-wrong"); rs.classList.add('ng'); rowng(i); cell(i, s); if (k) { cell(i, 3); }
        rs.innerHTML = '「' + stages[s] + '」の段で止まっています。' + (k ? '確かめの決まり「' + li.getAttribute('data-rule') + '」でも気付けます。' : '')
          + ' → <a href="' + links[i] + '" data-chizu="tsubo">' + (links[i].indexOf('#') >= 0 ? '解説は準備中（表の行へ）' : '解説を読む') + '</a>';
      }
      summary();
    });
  });
  summary();
})();
</script>
"""


def zentai_page():
    src = read("root3.html")
    head = src[: src.index("<main>")]
    desc = "電験三種の三相交流と変圧器の計算を、参考書の9章と、解く途中の4段（読み取り・立式・計算・確かめ）の表で俯瞰します。9問で、どの章のどの段で止まるかが分かります。"
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
    script = (SCRIPT.replace("__NAMES__", json.dumps([c[0] for c in CHAPS], ensure_ascii=False))
              .replace("__LINKS__", json.dumps([chap_href(i) for i in range(N)]))
              .replace("__STAGES__", json.dumps([s[0] for s in STAGES], ensure_ascii=False)))
    body = f"""<main>
<p class="crumb"><a href="./">トップ</a> › <a href="denken3.html">電験三種</a> › 三相と変圧器の全体像</p>
<h1>{TITLE}</h1>
<p class="lead">電験三種の、三相交流（理論）と変圧器（機械）の計算問題を、参考書の {N}章と、解く途中の {S}段で並べました。どの問題も、どれか1つの章に入ります。まず全体を俯瞰して、そのあと {N}問で、どの章のどの段で止まるかを確かめます。</p>
<div class="answer"><strong>範囲</strong>{FIELD_NOTE["理論"]}と、{FIELD_NOTE["機械"]}。平衡の三相回路を扱います。不平衡の三相回路、回転機（誘導機・同期機）、送配電線の電圧降下は、別のまとまりとして扱います。</div>

<h2>全体像：体系図</h2>
<p>理論の3章と、機械の6章です。点線の箱は、解説を準備中の章です。</p>
{tree()}

<h2>止まるのは、解く途中の {S}つの段のどこか</h2>
<p>どの章の問題も、解く人は同じ {S}つの段を順に通ります。止まるのは、このどこか1つです。</p>
{stages_block()}

<h2>全体像：{N}章 × {S}段の表</h2>
<p>下の {N}問を解くと、止まった章と段のマス目に ● が付きます。</p>
{matrix()}

<h2>自分のつまずきのツボを見つける（{N}問）</h2>
<p>1章に1問です。まちがいの選択肢は、それぞれどの段で止まったときの答えかが決まっています。採点は画面の中だけで、答えはどこにも送りません。</p>
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
    M = len(ORDER)
    for k, f in enumerate(ORDER):
        i = CHAP_OF[f]
        t = read(f)
        t = re.sub(r'<div class="chizu-ima">[^\n]*\n', "", t)
        ima = (f'<div class="chizu-ima"><p><a href="{PAGE}" data-chizu="ima">三相と変圧器の全体像</a>　'
               f'{N}章のうち、このページは <strong>{NUM[i]} {html.escape(CHAPS[i][0])}</strong></p>'
               f'{tree(cur=i, small=True)}</div>\n')
        t = re.sub(r"(</h1>\n)", lambda m: m.group(1) + ima, t, count=1)
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
           f'<p>参考書の {N}章と、解く途中の {S}段の表で全体を見て、{N}問で、どの章のどの段で止まるかを見つけます。</p></div>\n')
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
.tr{margin:1em 0}
.tr-root{text-align:center;font-weight:700;border:2px solid var(--ink);border-radius:4px;padding:.3em;margin:0 auto .6em;max-width:20em;background:var(--paper)}
.tr-cols{display:flex;gap:10px;align-items:flex-start}
.tr-col{flex:1;display:flex;flex-direction:column;gap:6px;border-top:2px solid var(--ink);padding-top:.4em}
.tr-col:first-child{flex:.75}
.tr-head{margin:0 0 .2em;font-size:.8rem;font-weight:700;text-align:center}
.tr-box{display:block;border:1.5px solid var(--ink);border-radius:4px;background:var(--paper);color:var(--ink);text-decoration:none;padding:.35em .5em;font-size:.85rem;line-height:1.4}
.tr-box.mada{border-style:dashed;color:var(--sub)}
.tr-small .tr-box{font-size:.72rem;padding:.2em .4em}
.tr-small .tr-head{font-size:.7rem}
.tr-small .tr-col{gap:4px}
.pz-no{font-weight:700;margin-right:.2em}
.tr-box.ima{background:var(--mark);border-color:var(--mark);color:#fff}
.tr-box.ok,.mx-dot.ok{opacity:.4}
.tr-box.ng,.mx-dot.ng{background:var(--mark);border-color:var(--mark);color:#fff;border-style:solid}
ol.st{list-style:none;padding:0;display:flex;flex-direction:column;gap:6px;margin:1em 0}
ol.st li{display:flex;gap:.6em;align-items:flex-start;border:1px solid var(--line);border-radius:4px;padding:.4em .6em;background:var(--paper);font-size:.9rem}
.st-no{flex:0 0 1.7em;height:1.7em;line-height:1.7em;text-align:center;border-radius:999px;background:var(--ink);color:#fff;font-weight:700;font-size:.85rem}
.st-ex{color:var(--sub);font-size:.8rem}
table.mx{width:100%;border-collapse:collapse;font-size:.8rem;margin:1em 0;table-layout:fixed}
table.mx thead th:first-child{width:44%}
table.mx th,table.mx td{border:1px solid var(--line);padding:.4em .4em;vertical-align:middle}
table.mx thead th{font-size:.72rem;color:var(--sub);font-weight:400;text-align:center}
table.mx tbody th{font-weight:700;text-align:left}
.mx-pages{display:block;font-weight:400;font-size:.7rem;margin-top:.2em}
.mx-pages a{display:block}
.mada-txt{color:var(--sub)}
td.mx-c{text-align:center;color:var(--mark);font-size:1.1rem}
td.mx-c.okrow{background:var(--paper)}
td.mx-c.ng{background:#f4dcdc}
.mx-dot{display:inline-block;width:1.7em;height:1.7em;line-height:1.7em;text-align:center;border:1.5px solid var(--ink);border-radius:999px;margin-right:.3em;color:var(--ink);font-weight:700;background:var(--paper)}
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
.zq-st{font-size:.8rem;color:var(--sub)}
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
