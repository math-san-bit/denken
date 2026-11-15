#!/usr/bin/env python3
"""共有のときの画像を作る（img/og-*.png、1200×630）。筆算堂の画像の決まりに合わせる。

使い方: python3 .github/scripts/make_og.py <明朝の太字のフォント> <ゴシックの太字のフォント> <出力のフォルダー>
例: Noto Serif CJK JP Bold と Noto Sans CJK JP Bold。フォントそのものは、サイトに置かない。
決まり: 生成りの方眼紙、黒の字、赤は「書き足した所」だけ。
"""
import sys
from PIL import Image, ImageDraw, ImageFont
SERIF, SANS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
PAPER, GRID, INK, RED, SUB = "#FAF8F3", "#E4E1D8", "#1C1C1E", "#BA2424", "#5A5A5F"
W, H, CELL = 1200, 630, 30
def font(p, s): return ImageFont.truetype(p, s, index=0)

def mark(d, x, y, s):
    u = s / 32
    d.rounded_rectangle([x + 1.5 * u, y + 1.5 * u, x + 30.5 * u, y + 30.5 * u], radius=3 * u, fill="#FFFEFB", outline=INK, width=max(2, round(2 * u)))
    for x0, yy, x1, col in ((9, 8.5, 23, INK), (11, 14.5, 23, RED), (9, 26, 18, INK)):
        d.line([(x + x0 * u, y + yy * u), (x + x1 * u, y + yy * u)], fill=col, width=max(2, round(2.6 * u)))
    d.line([(x + 6 * u, y + 20.5 * u), (x + 26 * u, y + 20.5 * u)], fill=INK, width=max(1, round(1.4 * u)))

def og(name, lines, shita, migi):
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    for x in range(0, W, CELL): d.line([(x, 0), (x, H)], fill=GRID)
    for y in range(0, H, CELL): d.line([(0, y), (W, y)], fill=GRID)
    mark(d, 60, 44, 64); f = font(SERIF, 40); x = 140
    for ch in "筆算堂": d.text((x, 50), ch, font=f, fill=INK); x += d.textlength(ch, font=f) + 6
    fq = font(SANS, 28); w = d.textlength(migi, font=fq); assert w < 700, migi
    d.text((W - 60 - w, 62), migi, font=fq, fill=SUB)
    ft = font(SERIF, 68); y = 180
    for s in lines:
        assert d.textlength(s, font=ft) <= W - 120, s
        d.text((60, y), s, font=ft, fill=INK); y += 100
    fs = font(SANS, 38); assert d.textlength(shita, font=fs) <= W - 150, shita
    d.line([(60, 478), (60, 566)], fill=RED, width=8)
    d.text((88, 496), shita, font=fs, fill=INK)
    im.quantize(colors=32, dither=Image.Dither.NONE).save(f"{OUT}/{name}", optimize=True)

og("og-top.png", ["計算で止まるのは、", "頭のせいではありません。"], "参考書で省かれた途中の式を、書き足します。", "電験三種・一陸特・一陸技")
og("og-denken.png", ["電験三種", "計算で止まる所の辞典"], "止まる原因を、書いて見せます。", "√3・%Z・j・力率")
og("og-musen.png", ["一陸特・一陸技", "計算で止まる所の辞典"], "止まる原因を、書いて見せます。", "dB・dBm・対数")
print("ok")
