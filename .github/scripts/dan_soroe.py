#!/usr/bin/env python3
"""解説の「止まる原因」の枠を、解く途中の4段（読み取り・立式・計算・確かめ）にそろえる（2026-11-16）。

元の3種類（途中の式が省かれている／前に習った決まりを忘れている／言葉や記号の意味が書かれていない）は、
見る側が混ざり、答えから見分けられないため、全体像の頁と同じ4段に替える。
枠の見出しは「止まる段」、札は段の名前、本文はその段で止まる理由（元の文をそのまま使う）。
何度かけても同じ結果になる。

使い方: python3 .github/scripts/dan_soroe.py [サイトの根のフォルダー]
"""
import re, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
DAN = {
    "root3.html": "立式", "root3-to-3.html": "立式", "youryou-denryuu.html": "立式",
    "rikiritsu.html": "立式", "henatsu-makisuu.html": "立式", "tanraku-100.html": "立式",
    "kijun-youryou.html": "立式", "juyouritsu.html": "立式", "kyosuu-naze.html": "読み取り",
    "musen/1w-30dbm.html": "読み取り", "musen/3db-hanbun.html": "読み取り", "musen/dbm-tasenai.html": "立式",
    "musen/10log-20log.html": "立式", "musen/db-bairitsu.html": "計算", "musen/db-3-10.html": "計算",
    "musen/log-2-3.html": "計算", "musen/keta-hachou.html": "計算", "musen/bunsuu-heiretsu.html": "計算",
    "musen/root-j.html": "計算", "musen/sankaku.html": "計算",
}
STAGES = ("読み取り", "立式", "計算", "確かめ")
TOP_OLD = re.compile(r"<p>止まる原因は、大きく3つに分かれます。.*?</p>")
TOP_NEW = ("<p>問題を解く人は、読み取り（与えられた量と条件をつかむ）、立式（使う決まりと式を選ぶ）、"
           "計算（分数・√・累乗・単位と桁を処理する）、確かめ（答えの大きさと単位を見る）の4つの段を順に通ります。"
           "止まるのは、このどこか1つです。この辞典は、解説のはじめに、どの段で止まるのかと、その理由を名指しします。</p>")


def main():
    for rel, dan in DAN.items():
        assert dan in STAGES
        p = ROOT / rel
        t = p.read_text(encoding="utf-8")
        new = re.sub(r'<div class="gennin"><strong>[^<]*</strong><span class="shurui">[^<]*</span>',
                     f'<div class="gennin"><strong>止まる段</strong><span class="shurui">{dan}</span>', t, count=1)
        if new == t and f'<span class="shurui">{dan}</span>' not in t:
            raise SystemExit("枠が見つからない: " + rel)
        p.write_text(new, encoding="utf-8")
    p = ROOT / "index.html"
    t = p.read_text(encoding="utf-8")
    t = TOP_OLD.sub(TOP_NEW, t)
    t = t.replace("先に答え、止まる原因、", "先に答え、止まる段とその理由、")
    t = t.replace("解説のはじめに、止まる原因を名指しします。", "解説のはじめに、どの段で止まるのかを名指しします。")
    p.write_text(t, encoding="utf-8")
    left = [str(f.relative_to(ROOT)) for f in ROOT.rglob("*.html")
            if re.search("途中の式が省かれている|前に習った決まりを忘れている|言葉や記号の意味が書かれていない|大きく3つに分かれます", f.read_text(encoding="utf-8"))]
    if left:
        raise SystemExit("古い3種類が残っている: " + ", ".join(left))
    print("4段にそろえた:", len(DAN), "ページとトップ")


if __name__ == "__main__":
    main()
