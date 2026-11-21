#!/usr/bin/env python3
"""2026-11-17 の改善（週1回の順位を上げる作業）。何度かけても同じ結果になる。

1. 新しい頁を2つ書く：henatsu-kouritsu.html（変圧器の効率）、denatsu-hendouritsu.html（電圧変動率）
2. 一覧の頁（ichiran.html）を直す：頁の数、束ごとの並び、資格を取ったあとの仕事へのリンクの誤り
3. sitemap.xml・sitemap-pages.xml・sitemap.txt に新しい頁を足す
4. 全体像の章（chizu_sansou.py の CHAPS）に新しい頁を足す

この後に chizu_sansou.py と seo_fix.py をかける。
使い方: python3 .github/scripts/kaizen_1117.py [サイトの根のフォルダー]
"""
import json, math, re, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
BASE = "https://hissandou.pages.dev/"
TODAY = "2026-11-17"
TODAY_JA = "2026年11月17日"

# ---- 数値の検算 ----
# 変圧器の効率：100 kV·A、鉄損 0.5 kW、全負荷銅損 1.5 kW、力率 0.8
S, PI, PC, PF = 100, 0.5, 1.5, 0.8
def eta(a, pf=PF, s=S, pi=PI, pc=PC):
    out = a * s * pf
    return out, pc * a * a, out / (out + pi + pc * a * a) * 100
o1, c1, e1 = eta(1)
assert (o1, c1) == (80, 1.5) and round(e1, 1) == 97.6          # 全負荷：80 ÷ 82
o2, c2, e2 = eta(0.5)
assert (o2, c2) == (40, 0.375) and round(e2, 1) == 97.9        # 半分の負荷：40 ÷ 40.875
assert 0.5 + 0.375 == 0.875 and 40 + 0.875 == 40.875
wrong = 40 / (40 + 0.5 + 1.5 * 0.5) * 100
assert 1.5 * 0.5 == 0.75 and round(wrong, 1) == 97.0          # 銅損を半分にした誤り
# 確かめの1問：50 kV·A、鉄損 200 W、全負荷銅損 800 W、負荷 1/2、力率 1
out_q = 50000 * 0.5 * 1.0
cu_q = 800 * 0.25
assert out_q == 25000 and cu_q == 200 and round(out_q / (out_q + 200 + cu_q) * 100, 2) == 98.43

# 電圧変動率：p 3%、q 4%（%Z 5%）、遅れ力率 0.8
p, q, cos, sin = 3, 4, 0.8, 0.6
assert abs(cos ** 2 + sin ** 2 - 1) < 1e-12
assert 3 / 100 * 100 == 3                                       # p ＝ 3 kW ÷ 100 kV·A × 100
assert math.sqrt(5 ** 2 - 3 ** 2) == 4
eps = p * cos + q * sin
assert abs(eps - 4.8) < 1e-9 and abs(p * cos - 2.4) < 1e-9 and abs(q * sin - 2.4) < 1e-9
assert abs(p * sin + q * cos - 5.0) < 1e-9                      # cos と sin を入れ替えた誤り
assert abs(200 * (1 + eps / 100) - 209.6) < 1e-9                # 二次の定格 200 V → 無負荷で 209.6 V
assert abs(3 * 1 + 4 * 0 - 3) < 1e-9                            # 力率 1 なら ε ≒ p
assert abs(1 * 0.8 + 5 * 0.6 - 3.8) < 1e-9                      # 確かめの1問

HEAD_FMT = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}｜筆算堂</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="筆算堂">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}｜筆算堂">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://hissandou.pages.dev/img/og-denken.png">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{ld}</script>
<link rel="stylesheet" href="style.css?v=20261116a">
<script src="m.js?v=20261116a"></script>
<script>function loadScript(a){{var b=document.getElementsByTagName("head")[0],c=document.createElement("script");c.type="text/javascript",c.src="https://tracker.metricool.com/resources/be.js",c.onreadystatechange=a,c.onload=a,b.appendChild(c)}}if(window.jitenLive){{loadScript(function(){{beTracker.t({{hash:"2b75e6ae5b3bd38f11244c20df0cb5ad"}})}})}}</script>
</head>
<body>
<header class="site"><a class="yagou" href="./">筆算堂</a><a href="denken3.html">電験三種　計算で止まる所の辞典</a><nav class="gnav" aria-label="サイトの案内"><a href="denken3.html">電験三種</a><a href="musen/">一陸特・一陸技</a><a href="tenken.html">10問の点検</a><a href="hon.html">本の案内</a></nav></header>
<main>
<p class="crumb"><a href="./">トップ</a> › <a href="denken3.html">電験三種</a> › 変圧器</p>
<h1>{title}</h1>
"""

FOOT = """<div class="cta cta-light"><p class="cta-need">ほかにも、止まっている所があるかもしれない</p><p>計算の10問を解くと、やり直す所と、読むページが分かります。約5分です。</p><a class="btn btn-sub" href="tenken.html" data-micro="約5分・採点は画面の中だけ">10問の点検を始める</a></div>
<p>この計算を順を追って解く本：<a href="hon.html#v5">第5巻の案内</a></p>
<nav class="next"><strong>同じまとまりで、ほかに止まりやすい所</strong><ul class="list"><li><a href="henatsu-makisuu.html" data-chizu="next">変圧器の巻数比の計算</a></li></ul><p><a href="sansou-zentai.html" data-chizu="all">全体を俯瞰して、自分のツボを見つける（9問）</a></p></nav>
<p class="updated">最終更新：{day}</p>
<p><a href="sansou-zentai.html">三相と変圧器の全体像へ</a>　／　<a href="denken3.html">電験三種の入口へ戻る</a>　／　<a href="./">辞典のトップ</a></p>
</main>
<footer>
<p class="yagou-foot"><strong>筆算堂</strong>止まる原因を、書いて見せます。</p>
<p>筆算堂で書いている人：電験数学ノート編集室。電験三種の計算で止まる所を1つずつ解く本を作っています。</p>
<p>この辞典の数値と例題は編集室が作ったもので、過去問題そのものではありません。誤りに気付いたときは、本の商品ページのカスタマーレビューで知らせていただけると助かります。</p>
<p><a href="privacy.html">このサイトが数えている物</a>　／　<a href="ichiran.html">ページの一覧</a></p>
</footer>
</body>
</html>
"""


def head(name, title, desc):
    url = BASE + name
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
          "inLanguage": "ja", "datePublished": TODAY, "dateModified": TODAY, "mainEntityOfPage": url,
          "author": {"@type": "Organization", "name": "電験数学ノート編集室"},
          "publisher": {"@type": "Organization", "name": "筆算堂", "url": BASE}}
    return HEAD_FMT.format(title=title, desc=desc, url=url, ld=json.dumps(ld, ensure_ascii=False))


def write_page(name, title, desc, body):
    p = ROOT / name
    if p.exists():
        old = p.read_text(encoding="utf-8")
        # 2回目以降は、chizu_sansou.py と seo_fix.py が入れた所を残すため、書き直さない
        if 'class="chizu-ima"' in old:
            return
    p.write_text(head(name, title, desc) + body + FOOT.format(day=TODAY_JA), encoding="utf-8")


# ---- 1-a. 変圧器の効率 ----
K_TITLE = "変圧器の効率の求め方：鉄損と銅損は、負荷でどう変わるのか"
K_DESC = ("変圧器の効率の求め方。効率 ＝ 出力 ÷（出力 ＋ 鉄損 ＋ 負荷率の2乗 × 全負荷銅損）。"
          "銅損は負荷率の2乗で変わり、鉄損は負荷によらず一定です。電験三種の機械の計算で、半分の負荷のときの損失を数値で確かめます。")
K_BODY = """<p class="lead">損失を足して、出力で割る。変圧器の効率の式は短いのに、負荷が全負荷でないときに、銅損をいくつにするかで手が止まります。</p>
<div class="answer"><strong>先に答え</strong>効率 ＝ 出力 ÷（出力 ＋ 鉄損 ＋ 銅損）。負荷率を α とすると、出力は α × 容量 × 力率、鉄損は負荷によらず同じ、銅損は α の2乗 × 全負荷の銅損です。負荷が半分なら、銅損は4分の1になります。</div>

<h2>どこで止まるか</h2>
<div class="gennin"><strong>止まる段</strong><span class="shurui">立式</span>銅損は「電流の2乗 × 巻線の抵抗」なので、電流が α 倍なら α の2乗倍になります。この途中が省かれ、効率の式だけが示されがちです。</div>
<div class="wrong">負荷が半分なので、銅損も半分にして 1.5 × 0.5 ＝ 0.75 kW としてしまう。正しくは、1.5 × 0.5 × 0.5 ＝ 0.375 kW です。</div>

<h2>鉄損と銅損は、何で決まるか</h2>
<p>鉄損は、鉄心の中で磁気の向きが変わるたびに出る損失です。鉄心の磁気の強さは、かかる電圧で決まります。電圧は負荷によらずほぼ同じなので、鉄損は負荷が軽くても重くても同じです。このため、無負荷損とも呼ばれます。</p>
<p>銅損は、巻線の抵抗に電流が流れて出る熱です。</p>
<div class="calc">銅損 ＝ 電流 × 電流 × 巻線の抵抗<br>負荷率 α のとき、電流 ＝ α × 全負荷の電流<br>銅損 ＝ α × α × 全負荷の電流 × 全負荷の電流 × 巻線の抵抗<br>銅損 ＝ α² × 全負荷の銅損</div>
<p>このため、銅損は負荷損とも呼ばれます。負荷が半分なら4分の1、4分の3なら16分の9になります。</p>

<h2>数値で確かめる</h2>
<p>容量 100 kV·A、鉄損 0.5 kW、全負荷の銅損 1.5 kW、力率 0.8 の変圧器で、負荷が半分のときの効率を出します。</p>
<div class="calc">出力 ＝ 1/2 × 100 kV·A × 0.8 ＝ 40 kW<br>鉄損 ＝ 0.5 kW<br>銅損 ＝ (1/2)² × 1.5 ＝ 0.25 × 1.5 ＝ 0.375 kW<br>損失の合計 ＝ 0.5 ＋ 0.375 ＝ 0.875 kW<br>効率 ＝ 40 ÷ (40 ＋ 0.875) ＝ 40 ÷ 40.875 ≒ 0.979 → 97.9%</div>
<p>同じ変圧器の全負荷の効率は、80 ÷ (80 ＋ 0.5 ＋ 1.5) ＝ 80 ÷ 82 ≒ 97.6% です。銅損を半分の 0.75 kW にした誤りの答えは、40 ÷ 41.25 ≒ 97.0% になり、全負荷より低く出ます。</p>
<p>確かめ：損失の合計（0.875 kW）は、鉄損（0.5 kW）より大きく、全負荷の損失（2.0 kW）より小さい。出力より大きな損失や、鉄損より小さな損失の合計が出たら、式を見直します。</p>

<figure class="tegaki"><img src="img/tegaki-henatsu-kouritsu.png" alt="手書きの計算。出力 ＝ 100 × 1/2 × 0.8 ＝ 40 kW。鉄損は 0.5 kW のまま。銅損 ＝ 1.5 × (1/2)² ＝ 0.375 kW。効率 ＝ 40 ÷ 40.875 ≒ 97.9 %。" width="456" height="380" loading="lazy"><figcaption>負荷で変わるのは銅損だけ。それも2乗で変わります。</figcaption></figure>

<h2 id="matome">変圧器の効率の式のまとめ</h2>
<div class="calc">出力 ＝ 負荷率 α × 容量 × 力率<br>鉄損（無負荷損）：負荷によらず同じ<br>銅損（負荷損）＝ α² × 全負荷の銅損<br>効率 ＝ 出力 ÷（出力 ＋ 鉄損 ＋ α² × 全負荷の銅損）× 100〔%〕</div>
<p>別の呼び方：損失から計算で出した効率を、規約効率と呼びます。負荷率は、利用率や負荷の割合と書かれることもあります。</p>
<p>容量 100 kV·A、鉄損 0.5 kW、全負荷の銅損 1.5 kW、力率 0.8 なら、全負荷で 97.6%、半分の負荷で 97.9% です。</p>
<div class="check"><strong>確かめの1問</strong><br>容量 50 kV·A、鉄損 200 W、全負荷の銅損 800 W の変圧器を、力率 1.0、負荷率 1/2 で使います。効率は何 % ですか（小数第2位まで）。
<details><summary>答え</summary>出力 ＝ 1/2 × 50 kV·A × 1.0 ＝ 25 kW ＝ 25000 W。銅損 ＝ (1/2)² × 800 ＝ 200 W。損失の合計 ＝ 200 ＋ 200 ＝ 400 W。効率 ＝ 25000 ÷ 25400 ≒ 98.43%。</details></div>

"""

# ---- 1-b. 電圧変動率 ----
D_TITLE = "電圧変動率の求め方：p cos θ ＋ q sin θ の p と q は何か"
D_DESC = ("電圧変動率の求め方。遅れ力率のとき ε ≒ p cos θ ＋ q sin θ。p は百分率抵抗降下、q は百分率リアクタンス降下です。"
          "p ＝ 3%、q ＝ 4%、力率 0.8 なら 4.8%。電験三種の機械の計算で、p と q の出し方から確かめます。")
D_BODY = """<p class="lead">電圧変動率の式は、ε ≒ p cos θ ＋ q sin θ と1行で示されます。ところが、問題文に p と q がそのまま書かれていないと、何を入れればよいかで手が止まります。</p>
<div class="answer"><strong>先に答え</strong>遅れ力率のとき、電圧変動率 ε ≒ p cos θ ＋ q sin θ〔%〕。p は百分率抵抗降下（全負荷の銅損 ÷ 容量 × 100）、q は百分率リアクタンス降下です。p ＝ 3%、q ＝ 4%、力率 0.8 なら、3 × 0.8 ＋ 4 × 0.6 ＝ 4.8% です。</div>

<h2>どこで止まるか</h2>
<div class="gennin"><strong>止まる段</strong><span class="shurui">立式</span>p と q は、%Z（百分率インピーダンス）を、抵抗の分とリアクタンスの分に分けた物です。この説明が省かれ、式だけが示されがちです。</div>
<div class="wrong">p に sin θ、q に cos θ を掛けて、3 × 0.6 ＋ 4 × 0.8 ＝ 5.0% としてしまう。抵抗の p には cos θ、リアクタンスの q には sin θ を掛けます。</div>

<h2>電圧変動率とは</h2>
<p>電圧変動率は、全負荷から無負荷にしたとき、二次の電圧がどれだけ上がるかの割合です。</p>
<div class="calc">ε ＝（無負荷の二次電圧 − 定格の二次電圧）÷ 定格の二次電圧 × 100〔%〕</div>
<p>電圧が変わるのは、巻線の抵抗とリアクタンスで、電圧が下がるからです。その下がり方を、定格の電圧に対する割合で表した物が p と q です。</p>

<h2>p と q の出し方</h2>
<p>p は、抵抗による電圧の降下の割合です。抵抗の電圧と電流を掛けると銅損になるので、全負荷の銅損から出せます。</p>
<div class="calc">p ＝ 全負荷の電流 × 抵抗 ÷ 定格の電圧 × 100<br>p ＝ 全負荷の電流 × 全負荷の電流 × 抵抗 ÷（定格の電圧 × 全負荷の電流）× 100<br>p ＝ 全負荷の銅損 ÷ 容量 × 100〔%〕</div>
<p>q は、リアクタンスによる電圧の降下の割合です。%Z は、p と q を直角に合わせた大きさなので、%Z と p が分かれば q が出ます。</p>
<div class="calc">%Z ＝ √(p² ＋ q²)<br>q ＝ √(%Z² − p²)</div>

<h2>なぜ p に cos θ、q に sin θ か</h2>
<p>抵抗による降下は、電流と同じ向きです。リアクタンスによる降下は、電流から 90° 進んだ向きです。遅れ力率では、電流が電圧から θ だけ遅れています。</p>
<p>電圧の向きに数えると、抵抗の分は cos θ 倍、リアクタンスの分は sin θ 倍だけ効きます。足すと p cos θ ＋ q sin θ になります。電圧の向きと直角な分は小さいので省きます。このため「≒」で書きます。</p>
<p>力率が 1 なら sin θ ＝ 0 なので、ε ≒ p です。</p>

<h2>数値で確かめる</h2>
<p>容量 100 kV·A、全負荷の銅損 3 kW、%Z ＝ 5%、二次の定格電圧 200 V の変圧器を、遅れ力率 0.8 で使います。</p>
<div class="calc">p ＝ 3 ÷ 100 × 100 ＝ 3%<br>q ＝ √(5² − 3²) ＝ √(25 − 9) ＝ √16 ＝ 4%<br>cos θ ＝ 0.8、sin θ ＝ √(1 − 0.8²) ＝ 0.6<br>ε ≒ 3 × 0.8 ＋ 4 × 0.6 ＝ 2.4 ＋ 2.4 ＝ 4.8%</div>
<p>無負荷にしたときの二次電圧は、200 × (1 ＋ 0.048) ＝ 209.6 V です。</p>
<p>確かめ：遅れ力率の電圧変動率は、%Z（5%）を超えません。5% より大きな答えが出たら、cos θ と sin θ を入れ替えていないか見直します。</p>

<figure class="tegaki"><img src="img/tegaki-denatsu-hendouritsu.png" alt="手書きの計算。p ＝ 3 kW ÷ 100 kV·A × 100 ＝ 3 %。q ＝ √(5² − 3²) ＝ 4 %。ε ≒ 3 × 0.8 ＋ 4 × 0.6 ＝ 2.4 ＋ 2.4 ＝ 4.8 %。" width="456" height="375" loading="lazy"><figcaption>p は銅損から、q は %Z から出します。</figcaption></figure>

<h2 id="matome">電圧変動率の式のまとめ</h2>
<div class="calc">ε ＝（無負荷の二次電圧 − 定格の二次電圧）÷ 定格の二次電圧 × 100<br>遅れ力率：ε ≒ p cos θ ＋ q sin θ〔%〕<br>p ＝ 全負荷の銅損 ÷ 容量 × 100、q ＝ √(%Z² − p²)</div>
<p>別の呼び方：p は百分率抵抗降下・%r、q は百分率リアクタンス降下・%x と書かれます。ε ≒ p cos θ ＋ q sin θ は、電圧変動率の近似式・簡易式とも呼ばれます。</p>
<p>p ＝ 3%、q ＝ 4%、遅れ力率 0.8 なら 4.8%、力率 1 なら 3% です。</p>
<div class="check"><strong>確かめの1問</strong><br>百分率抵抗降下 1%、百分率リアクタンス降下 5% の変圧器を、遅れ力率 0.8 で使います。電圧変動率はおよそ何 % ですか。
<details><summary>答え</summary>sin θ ＝ 0.6。ε ≒ 1 × 0.8 ＋ 5 × 0.6 ＝ 0.8 ＋ 3.0 ＝ 3.8%。</details></div>

"""

write_page("henatsu-kouritsu.html", K_TITLE, K_DESC, K_BODY)
write_page("denatsu-hendouritsu.html", D_TITLE, D_DESC, D_BODY)
assert K_TITLE.startswith("変圧器の効率の求め方") and D_TITLE.startswith("電圧変動率の求め方")

# ---- 2. 一覧の頁 ----
p = ROOT / "ichiran.html"
t = p.read_text(encoding="utf-8")
t = t.replace('<li><a href="ichiran.html">資格を取ったあとの仕事', '<li><a href="shigoto.html">資格を取ったあとの仕事')
for name, title in (("henatsu-kouritsu.html", K_TITLE), ("denatsu-hendouritsu.html", D_TITLE)):
    if f'href="{name}"' not in t:
        t = t.replace('<li><a href="henatsu-makisuu.html">',
                      f'<li><a href="{name}">{title}</a></li>\n<li><a href="henatsu-makisuu.html">', 1) if name == "henatsu-kouritsu.html" else \
            t.replace('<li><a href="tanraku-100.html">', f'<li><a href="{name}">{title}</a></li>\n<li><a href="tanraku-100.html">', 1)
# 頁の数を、一覧に並ぶリンクの数にそろえる
n = len(re.findall(r'<li><a href="[^"]+">', t))
t = re.sub(r"全部で \d+ ページあります。", f"全部で {n} ページあります。", t)
# 題と説明：屋号と「一覧」を前に
t = t.replace("<title>ページの一覧｜筆算堂</title>", "<title>筆算堂のページの一覧：電験三種・一陸特・一陸技の解説｜筆算堂</title>")
t = t.replace('content="計算で止まる所の辞典の、すべてのページの一覧です。電験三種、一陸特・一陸技の解説、点検、案内。"',
              f'content="筆算堂のページの一覧です。計算で止まる所の辞典の全 {n} ページを、電験三種の解説（三相と変圧器・数学・法規）、一陸特・一陸技の解説（デシベル・数学）、点検、案内に分けて並べます。"')
t = t.replace('<h1>ページの一覧</h1>', '<h1>筆算堂のページの一覧</h1>')
t = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="筆算堂のページの一覧：電験三種・一陸特・一陸技の解説｜筆算堂">', t)
t = re.sub(r'(<meta property="og:description" content=")[^"]*(">)',
           lambda m: m.group(1) + f"筆算堂のページの一覧です。計算で止まる所の辞典の全 {n} ページを、電験三種の解説（三相と変圧器・数学・法規）、一陸特・一陸技の解説（デシベル・数学）、点検、案内に分けて並べます。" + m.group(2), t)
t = re.sub(r"最終更新：\d+年\d+月\d+日", "最終更新：" + TODAY_JA, t)
p.write_text(t, encoding="utf-8")

# ---- 3. サイトマップ ----
for name in ("henatsu-kouritsu.html", "denatsu-hendouritsu.html"):
    url = BASE + name
    for fn, add in (("sitemap.xml", f"<url><loc>{url}</loc><lastmod>{TODAY}</lastmod></url>\n</urlset>"),
                    ("sitemap-pages.xml", f"  <url>\n    <loc>{url}</loc>\n  </url>\n</urlset>")):
        f = ROOT / fn
        s = f.read_text(encoding="utf-8")
        if f"<loc>{url}</loc>" not in s:
            s = s.replace("</urlset>", add, 1)
            f.write_text(s, encoding="utf-8")
    f = ROOT / "sitemap.txt"
    s = f.read_text(encoding="utf-8")
    if url not in s.split():
        s = s.rstrip("\n") + "\n" + url + "\n"
        f.write_text(s, encoding="utf-8")

# ---- 4. 全体像の章 ----
f = ROOT / ".github/scripts/chizu_sansou.py"
s = f.read_text(encoding="utf-8")
s = s.replace('("損失と効率", "機械", []),', '("損失と効率", "機械", ["henatsu-kouritsu.html"]),')
s = s.replace('("電圧変動率", "機械", []),', '("電圧変動率", "機械", ["denatsu-hendouritsu.html"]),')
f.write_text(s, encoding="utf-8")
print("kaizen_1117: 済み", n, "ページ")
