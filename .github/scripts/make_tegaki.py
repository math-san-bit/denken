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
INK, RED, GRID, PAPER, MARK = "#22303a", "#c0392b", "#d9e4ea", "#fdfdfb", "#ffe27a"
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
        """cell を渡すと、1字ずつ同じ幅に置く（筆算の桁をそろえる）。右端の x を返す。"""
        for ch in s:
            if ch == " " and cell is None:
                x += size * 0.35; continue
            f = font(ch, size) if ch != " " else None
            jy = self.r.uniform(-1.2, 1.2)
            if f:
                adv = f.getlength(ch) / S
                dx = (cell - adv) / 2 if cell else 0
                self.d.text(((x + dx) * S, (y + jy) * S), ch, font=f, fill=color,
                            stroke_width=2 if bold else 1, stroke_fill=color)
            x += cell if cell else adv
        return x
    def width(self, s, size=26):
        return sum(font(c, size).getlength(c) / S if c != " " else size * 0.35 for c in s)
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
n.marker(20, 92, 372, 18); n.marker(20, 132, 196, 18); n.marker(20, 180, 290, 18); n.marker(20, 220, 250, 18)
T(n, 24, 68, "%Z 5% → 定格電流を流す電圧は", 24, RED)
T(n, 24, 108, "5% で足りる", 24, RED)
T(n, 24, 156, "短絡すると電圧は 100%", 24, RED)
T(n, 24, 196, "100 ÷ 5 ＝ 20倍", 24, RED)
n.arrow(330, 236, 268, 216); T(n, 262, 240, "ここが、飛ばされる1行", 17, RED)
T(n, 24, 280, "短絡電流 ＝ 100 A × 20", 27, bold=True)
T(n, 150, 320, "＝ 2000 A", 27, bold=True)
n.line(150, 358, 290, 358); n.line(150, 364, 290, 364)
n.save("tegaki-top.png")

# ---- 2. 短絡電流：500 kV·A、6.6 kV、%Z 5% ----
assert 1732 * 6 == 10392 and 10392 + 103920 == 114312
i_rated = 500 / (3 ** 0.5 * 6.6); assert round(i_rated, 1) == 43.7 and round(i_rated * 20) == 875
n = Note(W, 676, 5)
T(n, 24, 16, "① 定格電流", 25)
T(n, 56, 54, "＝ 500 ÷（√3 × 6.6）", 25)
c, x0, y = 27, 86, 106
n.text(x0, y, " 1.732", 27, cell=c); n.text(x0 - c, y + 40, "×   6.6", 27, cell=c)
n.line(x0 - c, y + 84, x0 + c * 6 + 6, y + 84)
n.text(x0, y + 90, " 10392", 27, cell=c); n.text(x0 - c, y + 130, " 10392", 27, cell=c)
n.line(x0 - c, y + 174, x0 + c * 6 + 6, y + 174)
n.text(x0 - c, y + 180, "11.4312", 27, cell=c)
T(n, 290, y + 4, "√3 は 1.732", 19, RED); T(n, 290, y + 186, "→ 約 11.43", 22)
T(n, 56, 340, "500 ÷ 11.43 ＝ 約 43.7 A", 25)
T(n, 24, 396, "② 短絡すると、電圧は", 25)
T(n, 56, 434, "5% から 100% へ", 25)
n.marker(52, 496, 392, 18)
T(n, 56, 472, "100 ÷ 5 ＝ 20倍。電流も 20倍", 24, RED)
T(n, 24, 530, "③ 短絡電流 ＝ 43.7 × 20", 27, bold=True)
T(n, 176, 570, "＝ 約 875 A", 27, bold=True)
n.line(176, 608, 330, 608); n.line(176, 614, 330, 614)
T(n, 24, 632, "定格より大きければ、向きは合っている", 20, RED)
n.save("tegaki-tanraku-100.png")

# ---- 3. √3 で割る：200 V ÷ 1.73 ----
assert 173 * 115 == 19895 and 20000 - 19895 == 105 and 200 - 173 == 27 and 270 - 173 == 97 and 970 - 865 == 105
n = Note(W, 640, 7)
T(n, 24, 16, "相電圧 ＝ 200 ÷ √3", 25)
T(n, 96, 54, "＝ 200 ÷ 1.73", 25)
T(n, 24, 98, "小数点を2つずらして、20000 ÷ 173", 21, RED)
c, x0, y = 28, 150, 150
n.text(x0 + c * 2, y, "115", 27, cell=c, bold=True)
n.line(x0 - 6, y + 40, x0 + c * 5 + 8, y + 40); n.line(x0 - 6, y + 40, x0 - 14, y + 84)
n.text(x0 - 104, y + 46, "173", 27, cell=c); n.text(x0, y + 46, "20000", 27, cell=c)
n.text(x0, y + 86, "173", 27, cell=c); n.line(x0 - 4, y + 128, x0 + c * 3 + 6, y + 128)
n.text(x0 + c, y + 134, "270", 27, cell=c); n.text(x0 + c, y + 174, "173", 27, cell=c)
n.line(x0 + c - 4, y + 216, x0 + c * 4 + 6, y + 216)
n.text(x0 + c * 2, y + 222, "970", 27, cell=c); n.text(x0 + c * 2, y + 262, "865", 27, cell=c)
n.line(x0 + c * 2 - 4, y + 304, x0 + c * 5 + 6, y + 304)
n.text(x0 + c * 2, y + 310, "105", 27, cell=c)
T(n, 330, y + 90, "173 × 1", 19, RED); T(n, 330, y + 178, "173 × 1", 19, RED); T(n, 330, y + 266, "173 × 5", 19, RED)
T(n, 24, 524, "相電圧 ＝ 約 115 V", 27, bold=True); n.line(24, 562, 250, 562); n.line(24, 568, 250, 568)
T(n, 24, 592, "線間電圧より小さい。だから、割る", 21, RED)
n.save("tegaki-root3.png")
