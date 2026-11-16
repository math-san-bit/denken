#!/usr/bin/env python3
"""主要キーワードに合わせた頁ごとの直し（2026-11-17）。何度かけても同じ結果になる。

1. 題（title・h1・共有の題・構造化データ・ほかの頁からのリンクの文字）の頭に、検索で使われる言葉を置く
2. 説明（meta description）の頭に、検索の言葉と答えを置く
3. 解説の頁に「式のまとめ」（式・別の呼び方・数値の例）を足す。確かめの1問の前に入れる
3b. 構造化データの説明を、頁の説明にそろえる
4. 直した頁の「最終更新」を今日にする（構造化データと sitemap は seo_fix.py でそろえる）

使い方: python3 .github/scripts/kw_kaizen.py . && python3 .github/scripts/seo_fix.py .
"""
import html
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
TODAY = "2026年11月17日"

# ---- 数値の検算（まとめに書く数値は、ここで確かめた物だけ） ----
R3 = math.sqrt(3)
assert round(200 * R3) == 346
assert round(R3 * 200 * 10 * 0.8) == 2771
assert round(100000 / (R3 * 200)) == 289
assert math.isclose(math.hypot(80, 60), 100) and math.isclose(80 / 100, 0.8)
assert 6600 / 220 == 30 and math.isclose(0.01 * 30 ** 2, 9)
assert 500 * 100 / 5 == 10000
assert 5 * 100 / 10 == 50
assert round(10 * math.log10(2)) == 3 and round(20 * math.log10(2)) == 6
assert round(10 * math.log10(2000)) == 33 and 10 * math.log10(1000) == 30
assert round(10 ** (-3 / 20), 3) == 0.708 and round(1 / math.sqrt(2), 3) == 0.707
assert 6 * 3 / (6 + 3) == 2
assert 400 == 2 * 2 * 10 * 10 and 3 + 3 + 10 + 10 == 26
assert round(10 ** (54 / 10)) == 251189 and 10 ** 6 / 4 == 250000
assert 300 / 150 == 2 and math.isclose(0.3 / 3, 0.1) and 300000 / 1000 == 300
assert round(1 - 0.3, 2) == 0.7 and round(0.3 + 0.48, 2) == 0.78 and round(0.48 * 2, 2) == 0.96
assert math.hypot(3, 4) == 5 and math.hypot(5, 12) == 13
assert round(math.cos(math.radians(30)), 3) == 0.866 and round(math.sin(math.radians(45)), 3) == 0.707

# ---- 頁ごとの表 ----
# kw: 主要キーワード（記録用）　title: 新しい題（None は今のまま）　desc: 新しい説明（None は今のまま）
# h2: まとめの見出し　calc: 式（1行ずつ）　p: 言葉の行
PAGES = {
    "root3.html": dict(
        kw="線間電圧 相電圧 √3",
        title="線間電圧と相電圧の関係：√3 は、掛けるのか割るのか",
        desc="線間電圧と相電圧の関係で、√3 を掛けるのか割るのかで止まる所を、Y結線とΔ結線に分けて解きます。Y結線は 線間電圧 ＝ √3 × 相電圧、Δ結線は 線電流 ＝ √3 × 相電流 です。",
        h2="線間電圧と相電圧の式のまとめ",
        calc=["Y結線：線間電圧 ＝ √3 × 相電圧、線電流 ＝ 相電流", "Δ結線：線間電圧 ＝ 相電圧、線電流 ＝ √3 × 相電流"],
        p=["√3 ≒ 1.732 です。相電圧 200 V の Y結線なら、線間電圧は 200 × 1.732 ≒ 346 V になります。",
           "別の呼び方：Y結線は星形結線・スター結線、Δ結線は三角結線・デルタ結線とも書かれます。線間電圧は「線と線の間の電圧」、相電圧は「1相ぶんの巻線や負荷にかかる電圧」です。"]),
    "root3-to-3.html": dict(
        kw="三相電力 公式 √3 なぜ",
        title="三相電力の公式：√3 を掛けたうえで、なぜ3倍しないのか",
        desc=None,
        h2="三相電力の公式のまとめ",
        calc=["三相電力 ＝ √3 × 線間電圧 × 線電流 × 力率", "三相電力 ＝ 3 × 相電圧 × 相電流 × 力率"],
        p=["2つの式は同じ値になります。線間電圧 200 V、線電流 10 A、力率 0.8 なら、√3 × 200 × 10 × 0.8 ≒ 2771 W です。",
           "別の呼び方：三相電力は三相交流の有効電力のことで、単位は W や kW です。力率を掛けない √3 × 線間電圧 × 線電流 は皮相電力（V·A）です。"]),
    "youryou-denryuu.html": dict(
        kw="変圧器 容量 電流 求め方",
        title=None,
        desc="三相の変圧器や負荷の容量（kV·A）から電流を求めるとき、容量を電圧で割るだけでは合いません。電流 ＝ 容量 ÷（√3 × 線間電圧）になる理由と、単相との違いを説明します。",
        h2="容量から電流を求める式のまとめ",
        calc=["三相：電流 ＝ 容量 ÷（√3 × 線間電圧）", "単相：電流 ＝ 容量 ÷ 電圧"],
        p=["三相 100 kV·A、線間電圧 200 V なら、100000 ÷（1.732 × 200）≒ 289 A です。単位は、容量を V·A、電圧を V にそろえてから割ります。",
           "別の呼び方：この電流は定格電流と呼ばれます。「kVA から A（アンペア）を出す」「変圧器の一次電流・二次電流を出す」と書かれる計算も、同じ式です。"]),
    "rikiritsu.html": dict(
        kw="力率 無効電力 求め方",
        title="力率と無効電力の求め方：kW と kV·A と kvar は、どうつながるのか",
        desc=None,
        h2="力率と無効電力の式のまとめ",
        calc=["皮相電力² ＝ 有効電力² ＋ 無効電力²", "力率 cos θ ＝ 有効電力 ÷ 皮相電力", "無効電力 ＝ 皮相電力 × sin θ ＝ 有効電力 × tan θ"],
        p=["有効電力 80 kW、力率 0.8 なら、皮相電力は 80 ÷ 0.8 ＝ 100 kV·A、無効電力は 60 kvar です（80、60、100 の直角三角形）。",
           "別の呼び方：有効電力は消費電力、皮相電力は容量とも書かれます。単位は、有効電力が kW、皮相電力が kV·A（kVA）、無効電力が kvar です。"]),
    "henatsu-makisuu.html": dict(
        kw="変圧器 巻数比 計算",
        title="変圧器の巻数比の計算：電圧・電流・インピーダンスで、掛けるのか割るのか",
        desc=None,
        h2="巻数比の式のまとめ",
        calc=["巻数比 a ＝ 一次の巻数 ÷ 二次の巻数 ＝ 一次電圧 ÷ 二次電圧 ＝ 二次電流 ÷ 一次電流",
              "二次の値を一次に直す：電圧は a 倍、電流は a 分の1、インピーダンスは a² 倍"],
        p=["6600 V / 220 V の変圧器なら、巻数比は 30 です。二次側の 0.01 Ω を一次側に直すと、0.01 × 30² ＝ 9 Ω になります。",
           "別の呼び方：巻数比は変圧比とも書かれます。「一次に直す」は、一次換算・一次側換算と同じ意味です。"]),
    "tanraku-100.html": dict(
        kw="短絡電流 求め方 %Z",
        title=None,
        desc=None,
        h2="短絡電流と %Z の式のまとめ",
        calc=["短絡電流 ＝ 定格電流 × 100 ÷ %Z", "定格電流（三相）＝ 定格容量 ÷（√3 × 定格電圧）", "短絡容量 ＝ 定格容量 × 100 ÷ %Z"],
        p=["定格容量 500 kV·A、%Z ＝ 5% なら、短絡容量は 500 × 100 ÷ 5 ＝ 10000 kV·A（10 MV·A）です。",
           "別の呼び方：%Z は、パーセントインピーダンス、百分率インピーダンス、%インピーダンスとも書かれます。ここで求めた値は、三相短絡電流と呼ばれます。"]),
    "kijun-youryou.html": dict(
        kw="%Z 基準容量 換算",
        title=None,
        desc="%Z（パーセントインピーダンス）を別の基準容量に換算するとき、容量の比を掛けるのか割るのかで止まる所を解きます。新しい %Z ＝ 元の %Z × 新しい基準容量 ÷ 元の基準容量 です。",
        h2="%Z の基準容量の換算の式のまとめ",
        calc=["新しい %Z ＝ 元の %Z × 新しい基準容量 ÷ 元の基準容量"],
        p=["基準容量 10 MV·A で 5% の %Z は、基準容量 100 MV·A に直すと 5 × 100 ÷ 10 ＝ 50% です。基準容量を大きくすると、%Z も同じ割合で大きくなります。",
           "別の呼び方：この計算は「基準容量をそろえる」「基準容量の統一」「百分率インピーダンスの換算」とも書かれます。%Z を足し合わせる前に、必ず同じ基準容量に直します。"]),
    "juyouritsu.html": dict(
        kw="需要率 負荷率 違い",
        title="需要率と負荷率の違い：どちらを、何で割るのか",
        desc=None,
        h2="需要率・負荷率・不等率の式のまとめ",
        calc=["需要率 ＝ 最大需要電力 ÷ 設備容量 × 100 [%]", "負荷率 ＝ 平均需要電力 ÷ 最大需要電力 × 100 [%]",
              "不等率 ＝ 各負荷の最大需要電力の和 ÷ 合成最大需要電力"],
        p=["需要率と負荷率は 100% 以下、不等率は 1 以上になります。答えがこの範囲から外れたら、分子と分母が逆です。",
           "別の呼び方：平均需要電力は平均電力、設備容量は設備の定格容量の合計とも書かれます。負荷率は、期間によって日負荷率・月負荷率・年負荷率と呼び分けます。"]),
    "kyosuu-naze.html": dict(
        kw="交流回路 複素数 なぜ",
        title="交流回路の複素数：なぜ j（虚数）を使うのか",
        desc=None,
        h2="交流回路の複素数の式のまとめ",
        calc=["インピーダンス Z ＝ R ＋ jX、大きさ ＝ √(R² ＋ X²)", "コイル：jωL　コンデンサ：1 ÷ (jωC) ＝ −j ÷ (ωC)", "j × j ＝ −1"],
        p=["j を掛けると位相が 90° 進み、j で割ると 90° 遅れます。コイルでは電流が電圧より 90° 遅れ、コンデンサでは 90° 進みます。",
           "別の呼び方：j は虚数単位で、数学の i と同じ物です。電気では i を電流に使うので、j と書きます。この計算の方法は、記号法・複素数表示・フェーザ表示とも呼ばれます。"]),
    "suugaku-dokomade.html": dict(
        kw="電験三種 数学 どこまで",
        title="電験三種の数学は、どこまで要るか：単元ごとの範囲",
        desc="電験三種の計算に数学がどこまで要るかを、単元ごとに並べます。分数、平方根、三角関数、ベクトル、複素数、指数が土台です。やらなくてよい単元も書きます。",
    ),
    "denken3.html": dict(
        kw="電験三種 計算 わからない",
        title=None,
        desc="電験三種の計算問題で、解説を読んでもわからない所・手が止まる所を、1ページに1つずつ、図と3行の式で解きます。三相交流、変圧器、%Z、力率、需要率。",
    ),
    "musen/10log-20log.html": dict(
        kw="10log 20log 違い",
        title="10 log と 20 log の違い：どちらを使うか",
        desc=None,
        h2="10 log と 20 log の式のまとめ",
        calc=["電力の比：dB ＝ 10 log（出力の電力 ÷ 入力の電力）", "電圧・電流の比：dB ＝ 20 log（出力の電圧 ÷ 入力の電圧）"],
        p=["電力が2倍なら 3 dB、10倍なら 10 dB。電圧が2倍なら 6 dB、10倍なら 20 dB です。20 log は、入力と出力の抵抗（インピーダンス）が同じときに使えます。",
           "別の呼び方：電力の比は電力利得・電力増幅度、電圧の比は電圧利得・電圧増幅度と書かれます。log は、10 を底とする常用対数です。"]),
    "musen/1w-30dbm.html": dict(
        kw="1W 30dBm なぜ",
        title="1 W は、なぜ 30 dBm なのか：W と dBm の換算",
        desc=None,
        h2="W と dBm の換算のまとめ",
        calc=["dBm ＝ 10 log（電力 ÷ 1 mW）", "0 dBm ＝ 1 mW　10 dBm ＝ 10 mW　20 dBm ＝ 100 mW　30 dBm ＝ 1 W　40 dBm ＝ 10 W"],
        p=["10倍ごとに 10 を足し、2倍ごとに 3 を足します。2 W は 30 ＋ 3 ＝ 33 dBm、0.5 W は 30 − 3 ＝ 27 dBm です。",
           "別の呼び方：dBm は「デービーエム」と読み、1 mW を基準にした電力の表し方です。1 W を基準にした dBW では、1 W ＝ 0 dBW ＝ 30 dBm になります。"]),
    "musen/3db-hanbun.html": dict(
        kw="3dB 半分 電力 電圧",
        title=None,
        desc=None,
        h2="3 dB・6 dB と倍率のまとめ",
        calc=["−3 dB：電力は 2分の1、電圧は √2 分の1（約0.707倍）", "−6 dB：電力は 4分の1、電圧は 2分の1",
              "−10 dB：電力は 10分の1　−20 dB：電力は 100分の1、電圧は 10分の1"],
        p=["増える向き（＋3 dB、＋6 dB）は、逆数になります。＋3 dB で電力は2倍、＋6 dB で電圧は2倍です。",
           "別の呼び方：減衰器はアッテネータ（ATT）とも書かれます。「3 dB 下がる」「半値」「電力半値」は、電力が2分の1になることを指します。"]),
    "musen/bunsuu-heiretsu.html": dict(
        kw="並列 合成抵抗 求め方",
        title="並列の合成抵抗の求め方：分数の中の分数をほどく",
        desc=None,
        h2="並列の合成抵抗の式のまとめ",
        calc=["2本：合成抵抗 ＝（R1 × R2）÷（R1 ＋ R2）", "3本以上：1 ÷ 合成抵抗 ＝ 1 ÷ R1 ＋ 1 ÷ R2 ＋ 1 ÷ R3", "同じ値が n 本：合成抵抗 ＝ R ÷ n"],
        p=["6 Ω と 3 Ω の並列は、（6 × 3）÷（6 ＋ 3）＝ 2 Ω です。並列の合成抵抗は、いちばん小さい抵抗より必ず小さくなります。",
           "別の呼び方：2本の式は「和分の積」と呼ばれます。コイルの並列と、コンデンサの直列も、同じ形の式になります。"]),
    "musen/db-3-10.html": dict(
        kw="デシベル 計算 電卓なし",
        title="デシベルの計算：電卓なしで、3 と 10 だけで出す",
        desc=None,
        h2="デシベルの計算のまとめ（電力の比）",
        calc=["2倍 ＝ 3 dB　10倍 ＝ 10 dB", "掛け算は足し算に、割り算は引き算に直す",
              "4倍 ＝ 6 dB　5倍 ＝ 7 dB　8倍 ＝ 9 dB　20倍 ＝ 13 dB　100倍 ＝ 20 dB"],
        p=["400倍は 2 × 2 × 10 × 10 なので、3 ＋ 3 ＋ 10 ＋ 10 ＝ 26 dB です。5倍は 10 ÷ 2 なので、10 − 3 ＝ 7 dB です。",
           "別の呼び方：デシベルは dB と書きます。ここでの値は電力の比（10 log）です。電圧の比（20 log）では、2倍が 6 dB、10倍が 20 dB になります。"]),
    "musen/db-bairitsu.html": dict(
        kw="dB 倍率 変換",
        title="dB から倍率に戻す計算：54 dB は何倍か",
        desc=None,
        h2="dB から倍率への換算のまとめ",
        calc=["電力：10 dB ＝ 10倍　20 dB ＝ 100倍　30 dB ＝ 1000倍　3 dB ＝ 2倍　6 dB ＝ 4倍",
              "電圧：20 dB ＝ 10倍　40 dB ＝ 100倍　6 dB ＝ 2倍　12 dB ＝ 4倍"],
        p=["dB の足し算は倍率の掛け算に、引き算は割り算に戻します。式で書くと、電力の倍率は 10 の（dB ÷ 10）乗、電圧の倍率は 10 の（dB ÷ 20）乗です。",
           "別の呼び方：倍率は、真数・利得の真数・増幅度とも書かれます。「dB を真数に直す」は、この頁の計算と同じです。"]),
    "musen/db-keisan.html": dict(
        kw="デシベル 計算 ツール",
        title=None,  # 見出しが短く、ほかの頁のリンクの文字と同じなので変えない
        desc="倍率を入れると dB を、dB を入れると倍率を出す、デシベルの計算の道具（計算ツール）です。2 と 10 に分けられる数は、3 と 10 の足し算での出し方も見せます。",
    ),
    "musen/dbm-tasenai.html": dict(
        kw="dBm 足し算",
        title=None,
        desc="dBm の足し算で、30 dBm ＋ 30 dBm が 60 dBm にならない理由を解きます。dB は足せるのに、dBm どうしは足せません。足してよい組み合わせと、W に戻して足す組み合わせを分けます。",
        h2="dBm の足し算・引き算のまとめ",
        calc=["dBm ＋ dB ＝ dBm（足してよい）", "dBm − dBm ＝ dB（引いてよい。2つの電力の比になる）", "dBm ＋ dBm：W や mW に戻してから足す"],
        p=["同じ電力を2つ合わせると、電力は2倍なので 3 dB 増えます。30 dBm と 30 dBm を合わせると、33 dBm です。",
           "別の呼び方：dBm は 1 mW を基準にした電力（絶対値）、dB は2つの量の比（相対値）です。利得や損失は dB、送信電力や受信電力は dBm で書かれます。"]),
    "musen/ichirikugi-suugaku.html": dict(
        kw="一陸技 数学",
        title="一陸技の数学は、どこまで要るか：単元ごとの範囲",
        desc="一陸技（第一級陸上無線技術士）の計算に数学がどこまで要るかを、単元ごとに並べます。対数、三角関数、複素数が土台です。文系や、数学から離れた人が、受ける前に確かめる所をまとめました。",
    ),
    "musen/keta-hachou.html": dict(
        kw="波長 周波数 計算",
        title="波長の計算：300 を周波数で割るとき、桁がずれる",
        desc=None,
        h2="波長と周波数の式のまとめ",
        calc=["波長 [m] ＝ 300 ÷ 周波数 [MHz]", "波長 [m] ＝ 0.3 ÷ 周波数 [GHz]", "波長 [m] ＝ 300000 ÷ 周波数 [kHz]"],
        p=["150 MHz なら 2 m、3 GHz なら 0.1 m（10 cm）、1000 kHz なら 300 m です。元の式は、波長 ＝ 電波の速さ（3 × 10⁸ m/s）÷ 周波数 [Hz] です。",
           "別の呼び方：波長は λ（ラムダ）、周波数は f、電波の速さ（光速）は c と書かれ、λ ＝ c ÷ f の形で出てきます。アンテナの長さの「2分の1波長」「4分の1波長」は、この波長を2や4で割った長さです。"]),
    "musen/log-2-3.html": dict(
        kw="log 計算 log2 log3",
        title="対数の計算：log 2 と log 3 だけで、ほかの数の log を出す",
        desc=None,
        h2="対数（log）の計算のまとめ",
        calc=["log（a × b）＝ log a ＋ log b", "log（a ÷ b）＝ log a − log b", "log（a の n 乗）＝ n × log a　log 10 ＝ 1　log 1 ＝ 0"],
        p=["log 2 ≒ 0.3、log 3 ≒ 0.48 とすると、log 4 ≒ 0.6、log 5 ≒ 0.7（1 − 0.3）、log 6 ≒ 0.78、log 8 ≒ 0.9、log 9 ≒ 0.96 です。",
           "別の呼び方：ここでの log は、10 を底とする常用対数（log₁₀）です。対数は、ロガリズム・ログとも読まれます。"]),
    "musen/root-j.html": dict(
        kw="複素数 大きさ 絶対値",
        title="複素数の大きさ（絶対値）の出し方：3 ＋ j4 から、5 を出す",
        desc=None,
        h2="j の付いた数の大きさの式のまとめ",
        calc=["a ＋ jb の大きさ ＝ √(a² ＋ b²)", "インピーダンスの大きさ ＝ √(抵抗² ＋ リアクタンス²)"],
        p=["よく出る組は、3・4・5 と、5・12・13 です。6・8・10 のように、同じ数を掛けた組も平方根が開けます。",
           "別の呼び方：大きさは絶対値とも呼ばれ、|Z| と書かれます。この関係は、三平方の定理（ピタゴラスの定理）と同じです。"]),
    "musen/sankaku.html": dict(
        kw="cos60 0.5 なぜ 三角関数",
        title=None,
        desc=None,
        h2="sin・cos の値のまとめ",
        calc=["30°：sin ＝ 0.5　cos ≒ 0.866", "45°：sin ＝ cos ≒ 0.707", "60°：sin ≒ 0.866　cos ＝ 0.5", "tan ＝ sin ÷ cos"],
        p=["0.866 は 2分の√3、0.707 は √2 分の1です。sin と cos は、30° と 60° で値が入れ替わります。",
           "別の呼び方：sin は正弦（サイン）、cos は余弦（コサイン）、tan は正接（タンジェント）です。力率 cos θ の cos も、同じ物です。"]),
}


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;")


def matome(d):
    lines = "<br>".join(d["calc"])
    ps = "".join(f"<p>{x}</p>" for x in d["p"])
    return f'<h2 id="matome">{d["h2"]}</h2>\n<div class="calc">{lines}</div>\n{ps}\n'


def main():
    files = sorted(list(ROOT.glob("*.html")) + list(ROOT.glob("musen/*.html")))
    texts = {f: f.read_text(encoding="utf8") for f in files}
    changed = set()

    # 1. 題：古い題の文字を、すべての頁で新しい題に置き換える（リンクの文字も含む）
    for name, d in PAGES.items():
        new = d.get("title")
        if not new:
            continue
        m = re.search(r"<h1[^>]*>(.*?)</h1>", texts[ROOT / name], re.S)
        old = m.group(1).strip()
        if old == new:
            continue
        for f in files:
            t = texts[f]
            for a, b in ((old, new), (esc(old), esc(new))):
                if a in t:
                    t = t.replace(a, b)
            if t != texts[f]:
                texts[f] = t
                changed.add(f)

    for name, d in PAGES.items():
        f = ROOT / name
        t = texts[f]
        before = t
        # 2. 説明
        if d.get("desc"):
            for pat in (r'(<meta name="description" content=")[^"]*(")',
                        r'(<meta property="og:description" content=")[^"]*(")',
                        r'("description": *")[^"]*(")'):
                t = re.sub(pat, lambda m: m.group(1) + esc(d["desc"]) + m.group(2), t, count=1)
        # 3. 式のまとめ
        if d.get("h2") and 'id="matome"' not in t:
            assert '<div class="check">' in t, name
            t = t.replace('<div class="check">', matome(d) + '<div class="check">', 1)
        if t != before:
            texts[f] = t
            changed.add(f)

    # 3b. 構造化データ（Article）の説明を、頁の説明にそろえる（別の頁の説明が入っていた頁があった）
    for f in files:
        t = texts[f]
        m = re.search(r'<meta name="description" content="([^"]*)"', t)
        if not m or '"@type": "Article"' not in t:
            continue
        desc = json.dumps(html.unescape(m.group(1)), ensure_ascii=False)
        t2 = re.sub(r'("@type": "Article".*?"description": )"(?:[^"\\]|\\.)*"', lambda k: k.group(1) + desc, t, count=1, flags=re.S)
        if t2 != t:
            texts[f] = t2
            changed.add(f)

    # 4. 最終更新（解説の表に載せた頁だけ）
    for name in PAGES:
        f = ROOT / name
        if f in changed:
            texts[f] = re.sub(r'(class="updated">最終更新：)[^<]*', r"\g<1>" + TODAY, texts[f])

    for f in changed:
        f.write_text(texts[f], encoding="utf8")
    print(f"直した頁: {len(changed)}")
    for name, d in PAGES.items():
        t = texts[ROOT / name]
        title = re.search(r"<title>(.*?)</title>", t, re.S).group(1)
        print(f"{name}\t{d['kw']}\t{title}")


if __name__ == "__main__":
    main()
