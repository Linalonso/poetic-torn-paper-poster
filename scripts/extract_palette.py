#!/usr/bin/env python3
"""Return dominant color candidates from an image using Pillow only.

Usage:
    python extract_palette.py /path/to/image.jpg
"""
from __future__ import annotations

import colorsys
import sys
from pathlib import Path

from PIL import Image


def rgb_to_hex(rgb):
    return "#%02X%02X%02X" % rgb


def saturation(rgb):
    r, g, b = (v / 255.0 for v in rgb)
    return colorsys.rgb_to_hsv(r, g, b)[1]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python extract_palette.py IMAGE", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    with Image.open(path) as im:
        im = im.convert("RGB")
        im.thumbnail((512, 512))
        # Quantize to a compact palette, then sort by frequency.
        pal = im.quantize(colors=12, method=Image.Quantize.MEDIANCUT).convert("RGB")
        counts = pal.getcolors(maxcolors=512 * 512) or []

    ranked = sorted(counts, reverse=True)
    seen = set()
    rows = []
    for count, rgb in ranked:
        if rgb in seen:
            continue
        seen.add(rgb)
        rows.append((count, rgb, saturation(rgb)))

    total = sum(c for c, _, _ in rows) or 1
    print("Dominant palette candidates:")
    for count, rgb, sat in rows[:10]:
        pct = count / total * 100
        print(f"{rgb_to_hex(rgb)}  rgb={rgb}  share={pct:5.1f}%  saturation={sat:.2f}")

    # Accent candidates: favor some saturation but reject tiny-frequency colors.
    accents = [r for r in rows if r[0] / total >= 0.015 and r[2] >= 0.18]
    accents.sort(key=lambda r: (r[2] * 0.7 + min(r[0] / total, 0.2) * 1.5), reverse=True)
    if accents:
        print("\nSuggested accent candidates:")
        for count, rgb, sat in accents[:5]:
            print(f"{rgb_to_hex(rgb)}  share={count/total*100:5.1f}%  saturation={sat:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
