#!/usr/bin/env python3
"""手書き風の筆算の図の2組め（解説の頁ごとに1枚）。

使い方: python3 .github/scripts/make_tegaki2.py <フォントのフォルダー> <出力のフォルダー>
道具（Note、T など）は make_tegaki.py の前半をそのまま使う。図の中の数値は assert で確かめる。
"""
import math, pathlib, sys

src = pathlib.Path(__file__).with_name("make_tegaki.py").read_text(encoding="utf-8")
exec(src.split("# ---- 1.")[0])   # Note, T, W, INK, RED などを読み込む


def page(name, rows, seed, h=None):
    """rows: (左, 文, 大きさ, 色, 太字, 二重線) を上から並べる。y は自動。"""
    y, plan = 22, []
    for r in rows:
        if r is None:
            y += 14; continue
        x, s, size = r[0], r[1], r[2]
        color = r[3] if len(r) > 3 else INK
        bold = r[4] if len(r) > 4 else False
        under = r[5] if len(r) > 5 else False
        plan.append((x, y, s, size, color, bold, under))
        y += size + 22 + (10 if under else 0)
    n = Note(W, h or y + 16, seed)
    for x, yy, s, size, color, bold, under in plan:
        if color == RED and not bold:
            n.marker(x - 4, yy + size * 0.55, x + n.width(s, size) + 4, size * 0.55)
        xr = T(n, x, yy, s, size, color, bold)
        if under:
            n.line(x, yy + size + 10, xr, yy + size + 10); n.line(x, yy + size + 16, xr, yy + size + 16)
    n.save(name)
    n.plan = plan
    return n


def strike(n, x1, y1, x2, y2):
    n.line(x1, y1, x2, y2, RED, 2)


# ---- 容量から電流：三相 300 kV·A、6.6 kV ----
assert round(1.732 * 6.6, 2) == 11.43 and round(300 / 11.43, 1) == 26.2 and round(300 / 6.6, 1) == 45.5
page("tegaki-youryou-denryuu.png", [
    (24, "三相 300 kV·A、6.6 kV の線電流", 23),
    (24, "容量 ＝ √3 × V × I なので", 24),
    (24, "I ＝ 300 ÷（√3 × 6.6）", 25),
    (56, "√3 × 6.6 ≒ 1.732 × 6.6 ≒ 11.43", 21, RED),
    (24, "I ≒ 300 ÷ 11.43 ≒ 26.2 A", 27, INK, True, True),
    None,
    (24, "300 ÷ 6.6 ≒ 45.5 A は、√3 を忘れた値", 19, RED),
], 11)

# ---- 三相の電力：3 ÷ √3 ＝ √3 ----
assert abs(3 / math.sqrt(3) - math.sqrt(3)) < 1e-12 and round(math.sqrt(3) * 200 * 10) == 3464
page("tegaki-root3-to-3.png", [
    (24, "3相の合計 ＝ 3 × E × I × cosθ", 24),
    (24, "E ＝ V ÷ √3 を入れる", 24),
    (24, "3 × (V ÷ √3) × I × cosθ", 24),
    (56, "3 ＝ √3 × √3 だから", 22, RED),
    (56, "3 ÷ √3 ＝ √3", 22, RED),
    (24, "＝ √3 × V × I × cosθ", 25, INK, True),
    None,
    (24, "√3 × 200 × 10 ≒ 3464 W", 26, INK, True, True),
    (24, "これで3相の合計。もう3倍しない", 20, RED),
], 12)

# ---- 基準容量：10 MV·A 基準 7.5% → 30 MV·A 基準 ----
assert 7.5 * (30 / 10) == 22.5
page("tegaki-kijun-youryou.png", [
    (24, "10 MV·A 基準で %Z ＝ 7.5%", 24),
    (24, "30 MV·A 基準に直す", 24),
    (56, "基準が 3倍 → 基準の電流も 3倍", 21, RED),
    (56, "かかる電圧も 3倍 → %Z も 3倍", 21, RED),
    (24, "7.5 × (30 ÷ 10)", 26),
    (24, "＝ 7.5 × 3 ＝ 22.5%", 27, INK, True, True),
    None,
    (24, "基準を大きくしたら、%Z も大きくなる", 19, RED),
], 13)

# ---- 巻数比：6600 V / 200 V ----
assert 6600 / 200 == 33 and 330 / 33 == 10 and 33 * 33 == 1089 and round(0.1 * 1089, 1) == 108.9
page("tegaki-henatsu-makisuu.png", [
    (24, "a ＝ 6600 ÷ 200 ＝ 33", 26, INK, True),
    None,
    (24, "電圧：二次 × a", 23),
    (24, "電流：二次 ÷ a", 23),
    (56, "330 A ÷ 33 ＝ 10 A", 24),
    (24, "インピーダンス：二次 × a × a", 23),
    (56, "33 × 33 ＝ 1089", 24, RED),
    (56, "0.1 Ω × 1089 ＝ 108.9 Ω", 26, INK, True, True),
    None,
    (24, "電圧も電流も a 倍ずつ効くので、2乗", 19, RED),
], 14)

# ---- 力率：80 kW、0.8 → 直角三角形 ----
assert 80 / 0.8 == 100 and round(100 * 0.6) == 60 and 80 ** 2 + 60 ** 2 == 100 ** 2
n = page("tegaki-rikiritsu.png", [
    (24, "皮相電力 ＝ 80 ÷ 0.8 ＝ 100 kV·A", 24, INK, True),
    (24, "無効電力 ＝ 100 × 0.6 ＝ 60 kvar", 24, INK, True),
    (56, "cosθ ＝ 0.8 なら sinθ ＝ 0.6", 21, RED),
    (24, "確かめ：80 × 80 ＋ 60 × 60", 23),
    (56, "＝ 6400 ＋ 3600 ＝ 10000 ＝ 100 × 100", 20),
], 15, h=560)
x0, y0 = 70, 520
n.line(x0, y0, x0 + 280, y0); n.line(x0 + 280, y0, x0 + 280, y0 - 210); n.line(x0, y0, x0 + 280, y0 - 210, RED)
n.text(x0 + 110, y0 + 6, "80 kW", 21); n.text(x0 + 292, y0 - 120, "60 kvar", 21)
n.text(x0 + 60, y0 - 150, "100 kV·A", 21, RED)
n.save("tegaki-rikiritsu.png")

# ---- 需要率と負荷率 ----
assert 100 * 0.6 == 60 and 30 / 60 == 0.5
page("tegaki-juyouritsu.png", [
    (24, "大きい順：設備容量 ≧ 最大需要 ≧ 平均", 20, RED),
    None,
    (24, "最大需要電力 ＝ 100 × 0.6 ＝ 60 kW", 23),
    (24, "負荷率 ＝ 平均 ÷ 最大需要", 24),
    (56, "＝ 30 ÷ 60 ＝ 0.5 ＝ 50%", 27, INK, True, True),
    None,
    (24, "どちらの率も、小さいほう ÷ 大きいほう", 19, RED),
], 16)

# ---- 1 W は 30 dBm ----
page("tegaki-1w-30dbm.png", [
    (24, "1 mW    → 0 dBm", 25),
    (24, "10 mW   → 10 dBm", 25),
    (24, "100 mW  → 20 dBm", 25),
    (24, "1000 mW → 30 dBm", 25, INK, True),
    (56, "10倍ごとに、10 を足す", 21, RED),
    (24, "1 W ＝ 1000 mW ＝ 30 dBm", 27, INK, True, True),
    (24, "2 W は2倍なので 30 ＋ 3 ＝ 33 dBm", 21),
], 17)

# ---- dBm の足し算 ----
assert 1 + 1 == 2
n = page("tegaki-dbm-tasenai.png", [
    (24, "30 dBm ＋ 30 dBm ＝ 60 dBm", 25),
    (56, "60 dBm は 1000 W。合わない", 20, RED),
    None,
    (24, "W に戻す：1 W ＋ 1 W ＝ 2 W", 25),
    (56, "2倍は ＋3 dB", 21, RED),
    (24, "2 W ＝ 30 ＋ 3 ＝ 33 dBm", 27, INK, True, True),
], 18)
x, yy, s, size = n.plan[0][:4]
strike(n, x - 4, yy + size * 0.7, x + n.width(s, size) + 4, yy + size * 0.4)
n.save("tegaki-dbm-tasenai.png")

# ---- 54 dB は何倍（電圧） ----
assert 10 ** 3 / 2 == 500 and 20 * 3 - 6 == 54
page("tegaki-db-bairitsu.png", [
    (24, "電圧の 54 dB", 25),
    (24, "54 ＝ 20 ＋ 20 ＋ 20 − 6", 25),
    (56, "電圧は 20 dB で10倍、6 dB で2倍", 20, RED),
    (24, "10 × 10 × 10 ÷ 2", 26),
    (24, "＝ 500倍", 28, INK, True, True),
    (56, "足し算は掛け算、引き算は割り算", 20, RED),
], 19)

# ---- 3 dB で半分になるのは電力 ----
assert round(1 / math.sqrt(2), 2) == 0.71 and round(0.71 * 0.71, 1) == 0.5
page("tegaki-3db-hanbun.png", [
    (24, "3 dB の減衰", 25, INK, True),
    (24, "電力：1 → 0.5（半分）", 25),
    (24, "電圧：1 → 1 ÷ √2 ≒ 0.71", 25),
    (56, "電力は電圧の2乗に比例する", 21, RED),
    (56, "0.71 × 0.71 ≒ 0.5", 25),
    None,
    (24, "電圧が半分になるのは 6 dB", 24, INK, True, True),
], 20)

# ---- log 12 ----
assert round(0.3010 + 0.3010 + 0.4771, 4) == 1.0791
n = page("tegaki-log-2-3.png", [
    (24, "12 ＝ 2 × 2 × 3", 26),
    (24, "log 12 ＝ log 2 ＋ log 2 ＋ log 3", 23),
    (56, "掛け算は、log では足し算", 21, RED),
], 21, h=470)
xr, y = 300, 200
for k, s in enumerate(["0.3010", "0.3010", "0.4771"]):
    n.text(xr - n.width(s, 27), y + 40 * k, s, 27)
n.text(xr - n.width("0.4771", 27) - 34, y + 80, "＋", 27)
n.line(xr - 150, y + 122, xr + 6, y + 122)
n.text(xr - n.width("1.0791", 27), y + 128, "1.0791", 27, bold=True)
T(n, 24, 380, "× 10 ＝ 10.79 dB", 27, INK, True)
n.line(24, 424, 250, 424); n.line(24, 430, 250, 430)
n.save("tegaki-log-2-3.png")

# ---- 波長 2.4 GHz ----
assert 300 / 2400 == 0.125 and 300 / 2.4 == 125
n = page("tegaki-keta-hachou.png", [
    (24, "波長〔m〕＝ 300 ÷ 周波数〔MHz〕", 22),
    (24, "2.4 GHz ＝ 2400 MHz", 25),
    (56, "先に MHz にそろえる", 21, RED),
    (24, "300 ÷ 2400 ＝ 0.125 m", 27, INK, True, True),
    (24, "＝ 12.5 cm", 26),
    None,
    (24, "300 ÷ 2.4 ＝ 125 m", 24),
    (56, "電波の長さが 125 m は、大きすぎる", 19, RED),
], 22)
x, yy, s, size = n.plan[5][:4]
strike(n, x - 4, yy + size * 0.7, x + n.width(s, size) + 4, yy + size * 0.4)
n.save("tegaki-keta-hachou.png")

# ---- 10 log と 20 log ----
assert 200 / 2 == 100 and 20 * math.log10(100) == 40
page("tegaki-10log-20log.png", [
    (24, "入力 2 mV、出力 200 mV", 25),
    (24, "電圧の比 ＝ 200 ÷ 2 ＝ 100倍", 25),
    (56, "電圧なので 20 log", 21, RED),
    (24, "20 × log 100 ＝ 20 × 2", 25),
    (24, "＝ 40 dB", 28, INK, True, True),
    (56, "電力なら 10000倍。10 × 4 ＝ 40 dB", 20, RED),
], 23)

# ---- 変圧器の効率：100 kV·A、鉄損 0.5 kW、全負荷銅損 1.5 kW、負荷 1/2、力率 0.8 ----
assert 100 * 0.5 * 0.8 == 40 and 1.5 * 0.5 ** 2 == 0.375 and 0.5 + 0.375 == 0.875
assert round(40 / 40.875 * 100, 1) == 97.9
page("tegaki-henatsu-kouritsu.png", [
    (24, "出力 ＝ 100 × 1/2 × 0.8 ＝ 40 kW", 24),
    (24, "鉄損 ＝ 0.5 kW（負荷によらない）", 22),
    (24, "銅損 ＝ 1.5 × (1/2)² ", 24),
    (56, "電流が半分 → 銅損は 1/4", 21, RED),
    (56, "＝ 1.5 × 0.25 ＝ 0.375 kW", 24),
    None,
    (24, "効率 ＝ 40 ÷ (40 ＋ 0.5 ＋ 0.375)", 23),
    (56, "＝ 40 ÷ 40.875 ≒ 97.9 %", 26, INK, True, True),
], 31)

# ---- 電圧変動率：p 3%、q 4%、遅れ力率 0.8 ----
assert abs(3 * 0.8 + 4 * 0.6 - 4.8) < 1e-9 and 3 ** 2 + 4 ** 2 == 5 ** 2
page("tegaki-denatsu-hendouritsu.png", [
    (24, "p ＝ 3 kW ÷ 100 kV·A × 100 ＝ 3 %", 22),
    (24, "q ＝ √(5² − 3²) ＝ √16 ＝ 4 %", 22),
    (56, "%Z の 5 % から、p を引いて出す", 20, RED),
    None,
    (24, "cos θ ＝ 0.8、sin θ ＝ 0.6", 23),
    (24, "ε ≒ 3 × 0.8 ＋ 4 × 0.6", 25),
    (56, "＝ 2.4 ＋ 2.4 ＝ 4.8 %", 26, INK, True, True),
    (56, "p に cos、q に sin", 21, RED),
], 32)
