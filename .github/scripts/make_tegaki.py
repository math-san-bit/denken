#!/usr/bin/env python3
"""手書き風の筆算の図を作る（img/tegaki-*.png）。

使い方: python3 .github/scripts/make_tegaki.py <フォントのフォルダー> <出力のフォルダー>
フォント: Zen Kurenaido（SIL Open Font License 1.1）。@fontsource/zen-kurenaido の files フォルダーを渡す。
フォントそのものは、サイトに置かない。図の中の数値は、下の assert で確かめる。
"""
import glob, random, sys
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

FD, OUT = sys.argv[1], sys.argv[2]
S = 2                      # 2倍の大きさで描く
INK, RED, GRID, PAPER, MARK = "#1c1c1e", "#ba2424", "#e4e1d8", "#faf8f3", "#f4dcdc"   # 筆算堂の色。赤は書き足した所だけ。下地の線は、赤をうすめた色
_files = sorted(glob.glob(FD + "/zen-kurenaido-*-400-normal.woff"))
_cmap = {}
for f in _files:
    for cp in TTFont(f, lazy=True).getBestCmap():
        _cmap.setdefault(cp, f)
_fonts = {}
def font(ch, size):
    f = _cmap.get(ord(ch))
    if f is None:
        raise SystemExit("字が無い: " + repr(ch))
    k = (f, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(f, size * S)
    return _fonts[k]

class Note:
    def __init__(self, w, h, seed=1):
        self.w, self.h = w, h
        self.im = Image.new("RGB", (w * S, h * S), PAPER)
        self.d = ImageDraw.Draw(self.im)
        self.r = random.Random(seed)
        for x in range(0, w, 24):
            self.d.line([(x * S, 0), (x * S, h * S)], fill=GRID, width=1)
        for y in range(0, h, 24):
            self.d.line([(0, y * S), (w * S, y * S)], fill=GRID, width=1)
    def text(self, x, y, s, size=26, color=INK, cell=None, bold=False):
        """cell を渡すと、1字ずつ同じ幅に置く（筆算の桁をそろえる）。右端の x を返す。
        「≒」は、等号の左上と右下に点を打って描く。「√」の後ろの数には、上に横線を引く。"""
        bar = None
        for ch in s:
            if bar is not None and not (ch.isdigit() or ch == "."):
                self.line(bar - size * 0.2, y + size * 0.21, x + 2, y + size * 0.21, color, 1 if size < 22 else 2); bar = None
            if ch == " " and cell is None:
                x += size * 0.35; continue
            g = "＝" if ch == "≒" else ch
            f = font(g, size) if ch != " " else None
            jy = self.r.uniform(-1.2, 1.2)
            if f:
                adv = f.getlength(g) / S
                dx = (cell - adv) / 2 if cell else 0
                self.d.text(((x + dx) * S, (y + jy) * S), g, font=f, fill=color,
                            stroke_width=2 if bold else 1, stroke_fill=color)
                if ch == "≒":
                    l, t, rgt, btm = f.getbbox(g)
                    r = size * (0.085 if bold else 0.07); gap = size * 0.14
                    ox, oy = x + dx, y + jy
                    for px, py in ((ox + l / S + (rgt - l) / S * 0.2, oy + t / S - gap), (ox + l / S + (rgt - l) / S * 0.8, oy + btm / S + gap)):
                        self.d.ellipse([(px - r) * S, (py - r) * S, (px + r) * S, (py + r) * S], fill=color)
                if ch == "√":
                    bar = x + dx + adv
            x += cell if cell else adv
        if bar is not None:
            self.line(bar - size * 0.2, y + size * 0.21, x + 2, y + size * 0.21, color, 1 if size < 22 else 2)
        return x
    def frac(self, x, y, top, bottom, size=25, color=INK):
        """分数を描く。右端の x を返す。"""
        wt, wb = self.width(top, size), self.width(bottom, size); w = max(wt, wb) + 12
        self.text(x + (w - wt) / 2, y, top, size, color)
        self.line(x, y + size * 1.42, x + w, y + size * 1.42, color)
        self.text(x + (w - wb) / 2, y + size * 1.5, bottom, size, color)
        return x + w
    def width(self, s, size=26):
        return sum(font("＝" if c == "≒" else c, size).getlength("＝" if c == "≒" else c) / S if c != " " else size * 0.35 for c in s)
    def line(self, x1, y1, x2, y2, color=INK, w=2):
        n = max(2, int(abs(x2 - x1) + abs(y2 - y1)) // 18)
        pts = [((x1 + (x2 - x1) * i / n + self.r.uniform(-.8, .8)) * S,
                (y1 + (y2 - y1) * i / n + self.r.uniform(-.8, .8)) * S) for i in range(n + 1)]
        self.d.line(pts, fill=color, width=w * S, joint="curve")
    def marker(self, x1, y, x2, h=16):
        self.d.rectangle([x1 * S, y * S, x2 * S, (y + h) * S], fill=MARK)
    def arrow(self, x1, y1, x2, y2, color=RED):
        self.line(x1, y1, x2, y2, color)
        import math
        a = math.atan2(y2 - y1, x2 - x1)
        for da in (2.6, -2.6):
            self.line(x2, y2, x2 + 10 * math.cos(a + da), y2 + 10 * math.sin(a + da), color)
    def save(self, name):
        self.im.save(f"{OUT}/{name}", optimize=True)
        print(name, self.im.size)

W = 456   # 電話の幅で字が小さくならないよう、細長い紙にする

def fit(n, x, s, size):
    assert x + n.width(s, size) <= W - 12, (s, x + n.width(s, size))

def T(n, x, y, s, size=25, color=INK, bold=False):
    fit(n, x, s, size); return n.text(x, y, s, size, color, bold=bold)

# ---- 1. トップ：飛ばされる1行（定格電流 100 A、%Z 5%） ----
assert 100 / 5 == 20 and 100 * 20 == 2000
n = Note(W, 372, 3)
T(n, 24, 18, "定格電流 100 A、%Z ＝ 5%", 26)
n.marker(20, 92, 372, 18); n.marker(20, 132, 330, 18); n.marker(20, 180, 290, 18); n.marker(20, 220, 250, 18)
T(n, 24, 68, "%Z が 5% → 定格電流を流すのに", 24, RED)
T(n, 24, 108, "必要な電圧は、定格の 5%", 24, RED)
T(n, 24, 156, "短絡すると、電圧は 100%", 24, RED)
T(n, 24, 196, "100 ÷ 5 ＝ 20倍", 24, RED)
n.arrow(330, 236, 268, 216); T(n, 262, 240, "ここが、省かれた1行", 17, RED)
T(n, 24, 280, "短絡電流 ＝ 100 A × 20", 27, bold=True)
T(n, 150, 320, "＝ 2000 A", 27, bold=True)
n.line(150, 358, 290, 358); n.line(150, 364, 290, 364)
n.save("tegaki-top.png")

# ---- 2. 短絡電流：500 kV·A、6.6 kV、%Z 5% ----
assert 1732 * 6 == 10392 and 10392 + 103920 == 114312
assert round(500 / 11.43, 2) == 43.74 and round(43.74 * 20) == 875
n = Note(W, 700, 5)
T(n, 24, 30, "① 定格電流 ＝", 25)
n.frac(196, 10, "500", "√3 × 6.6", 25)
c, x0, y = 27, 86, 122
n.text(x0, y, " 1.732", 27, cell=c); n.text(x0 - c, y + 40, "×   6.6", 27, cell=c)
n.line(x0 - c, y + 84, x0 + c * 6 + 6, y + 84)
n.text(x0, y + 90, " 10392", 27, cell=c); n.text(x0 - c, y + 130, " 10392", 27, cell=c)
n.line(x0 - c, y + 174, x0 + c * 6 + 6, y + 174)
n.text(x0 - c, y + 180, "11.4312", 27, cell=c)
T(n, 286, y + 4, "√3 ≒ 1.732", 20, RED)
T(n, 56, 356, "500 ÷ 11.43 ≒ 43.74 A", 25)
T(n, 24, 414, "② 短絡すると、電圧は", 25)
T(n, 56, 452, "5% から 100% になる", 25)
n.marker(52, 514, 396, 18)
T(n, 56, 490, "100 ÷ 5 ＝ 20倍。電流も 20倍", 24, RED)
T(n, 24, 550, "③ 短絡電流 ＝ 43.74 × 20", 27, bold=True)
T(n, 176, 592, "≒ 875 A", 27, bold=True)
n.line(176, 640, 310, 640); n.line(176, 646, 310, 646)
T(n, 24, 656, "定格電流より大きければ、向きは合っている", 19, RED)
n.save("tegaki-tanraku-100.png")

# ---- 3. √3 で割る：200 V ÷ 1.732 ----
assert 2000 - 1732 == 268 and 2680 - 1732 == 948 and 1732 * 5 == 8660 and 9480 - 8660 == 820
assert 1732 * 4 == 6928 and 8200 - 6928 == 1272 and 1732 * 7 == 12124 and 12720 - 12124 == 596
assert round(200 / 1.732, 1) == 115.5
n = Note(W, 800, 7)
T(n, 24, 30, "相電圧 ＝", 25)
xr = n.frac(138, 10, "200", "√3", 25)
T(n, xr + 10, 30, "≒ 200 ÷ 1.732", 25)
T(n, 24, 104, "小数点を3けたずらす", 21, RED)
c, x0, y = 27, 150, 156
def put(num, end, row, bold=False):
    for k, ch in enumerate(num):
        n.text(x0 + c * (end - len(num) + 1 + k), y + row, ch, 27, cell=c, bold=bold)
    return x0 + c * (end - len(num) + 1), x0 + c * (end + 1)
def dot(row, bold=False):   # 小数点は、6けた目と7けた目の間に打つ
    rr = 3.2 if bold else 2.6
    px, py = x0 + c * 6, y + row + 31
    n.d.ellipse([(px - rr) * S, (py - rr) * S, (px + rr) * S, (py + rr) * S], fill=INK)
put("20000000", 7, 46); dot(46)
for i, ch in zip((3, 4, 5, 6, 7), "11547"):
    n.text(x0 + c * i, y, ch, 27, cell=c, bold=True)
dot(0, True)
n.line(x0 - 6, y + 40, x0 + c * 8 + 6, y + 40); n.line(x0 - 6, y + 40, x0 - 14, y + 84)
n.text(x0 - 122, y + 46, "1732", 27, cell=c)
rows = [("1732", 3, "× 1"), ("2680", 4, None), ("1732", 4, "× 1"), ("9480", 5, None), ("8660", 5, "× 5"),
        ("8200", 6, None), ("6928", 6, "× 4"), ("12720", 7, None), ("12124", 7, "× 7"), ("596", 7, None)]
r = 86
for num, end, note in rows:
    a, b = put(num, end, r)
    if note:
        n.text(x0 + c * 8 + 18, y + r + 4, note, 19, RED); n.line(a - 4, y + r + 40, b + 4, y + r + 40); r += 46
    else:
        r += 38
T(n, 24, 688, "相電圧 ≒ 115.5 V", 27, bold=True); n.line(24, 734, 250, 734); n.line(24, 740, 250, 740)
T(n, 24, 758, "線間電圧より小さくなる。だから、割る", 21, RED)
n.save("tegaki-root3.png")
