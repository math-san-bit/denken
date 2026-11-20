#!/usr/bin/env python3
"""手書き風の筆算の図の3組め（2026-11-20：cos60°、log の割り算、dBm の引き算、波長の対応表）。

使い方: python3 .github/scripts/make_tegaki3.py <フォントのフォルダー> <出力のフォルダー>
道具（Note、T、page など）は make_tegaki2.py と同じく make_tegaki.py の前半を使う。図の中の数値は assert で確かめる。
"""
import math, pathlib, sys

src = pathlib.Path(__file__).with_name("make_tegaki.py").read_text(encoding="utf-8")
exec(src.split("# ---- 1.")[0])   # Note, T, W, INK, RED などを読み込む
src2 = pathlib.Path(__file__).with_name("make_tegaki2.py").read_text(encoding="utf-8")
exec(src2.split("def strike")[0].split("exec(src.split")[1].split("\n", 1)[1])   # page を読み込む


# ---- cos60°：正三角形を半分に切る ----
assert abs(math.cos(math.radians(60)) - 0.5) < 1e-12
assert abs(math.sqrt(2 ** 2 - 1 ** 2) - math.sqrt(3)) < 1e-12 and round(math.sqrt(3) / 2, 3) == 0.866
n = Note(W, 430, 41)
# 正三角形（1辺 2）を、高さの線で半分に切る。左下の角が 60°
ax, ay, bx, by, cx, cy = 60, 230, 260, 230, 160, 230 - 173   # 1辺 200、高さ 173（200 × √3 ÷ 2）
n.line(ax, ay, bx, by); n.line(ax, ay, cx, cy); n.line(bx, by, cx, cy, "#9a9a9a")
n.line(cx, cy, cx, ay, RED)                       # 高さの線（ここで半分に切る）
n.line(cx - 12, ay, cx - 12, ay - 12, RED, 1); n.line(cx - 12, ay - 12, cx, ay - 12, RED, 1)   # 直角の印
T(n, ax + 18, ay - 34, "60°", 20)
T(n, 64, 128, "2", 24)                             # 斜めの辺
T(n, 98, ay + 8, "1", 24, RED, True)               # 横の辺（半分）
T(n, cx + 8, ay + 8, "1", 22, "#9a9a9a")
T(n, cx + 10, 132, "√3", 22)
T(n, 236, 128, "2", 22, "#9a9a9a")
T(n, 290, 92, "正三角形を", 20); T(n, 290, 120, "半分に切る", 20)
T(n, 24, 274, "cos60° ＝ 横 ÷ 斜め", 24)
T(n, 56, 314, "＝ 1 ÷ 2 ＝ 1/2 ＝ 0.5", 26, INK, True)
n.line(56, 350, 330, 350); n.line(56, 356, 330, 356)
T(n, 24, 378, "横は、斜めのちょうど半分", 20, RED)
n.save("tegaki-sankaku.png")

# ---- log の割り算：log 8 ÷ log 2 ----
assert round(3 * 0.3010, 3) == 0.903 and round(0.903 / 0.301, 6) == 3 and round(2 * 0.3010, 3) == 0.602
assert round(3 / 0.3010, 2) == 9.97
page("tegaki-log-warizan.png", [
    (24, "log 8 ÷ log 2 を求める", 24),
    (24, "log 8 ＝ 3 × log 2 ＝ 0.903", 24),
    (24, "0.903 ÷ 0.301 ＝ 3", 27, INK, True, True),
    (56, "2 を 3回掛けると 8", 21, RED),
    None,
    (24, "log 4 ＝ 0.602 は、log(8 ÷ 2)", 22),
    (56, "log の中の割り算は、引き算", 20, RED),
    (56, "log 8 − log 2 ＝ 0.903 − 0.301", 21),
], 42)

# ---- dBm の引き算：−50 dBm と −70 dBm ----
assert -50 - (-70) == 20 and 10 ** (20 / 10) == 100
assert abs(10 ** (-50 / 10) / 10 ** (-70 / 10) - 100) < 1e-9
page("tegaki-dbm-hikizan.png", [
    (24, "信号 −50 dBm、雑音 −70 dBm", 24),
    (24, "S/N ＝ −50 − (−70)", 25),
    (56, "引く数がマイナス → 足し算になる", 20, RED),
    (24, "＝ −50 ＋ 70 ＝ 20 dB", 27, INK, True, True),
    (56, "答えは dB（比）。dBm ではない", 21, RED),
    None,
    (24, "20 dB ＝ 100倍", 24),
    (56, "10 nW ÷ 0.1 nW ＝ 100 で確かめ", 20),
], 43)

# ---- 波長の見当：周波数 × 波長 ＝ 300 ----
assert 300 / 150 == 2 and 300 / 1500 == 0.2 and 150 * 2 == 300 and round(300 / 430, 2) == 0.70
page("tegaki-hachou-hyou.png", [
    (24, "周波数〔MHz〕× 波長〔m〕＝ 300", 23),
    None,
    (24, "150 MHz → 300 ÷ 150 ＝ 2 m", 24),
    (24, "1.5 GHz ＝ 1500 MHz", 24),
    (56, "周波数が 10倍 → 波長は 10分の1", 20, RED),
    (56, "→ 0.2 m ＝ 20 cm", 26, INK, True, True),
    None,
    (24, "表の近い行と、桁が合うかを見る", 20, RED),
], 44)
