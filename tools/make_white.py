#!/usr/bin/env python3
"""Her logo için koyu zemin sürümü üretir: <slug>-white.png

Beyaz silüet, alfa kanalı korunarak üretilir. Logo yeniden çizilmez, rengi
değiştirilmez; yalnız aynı vektörün tek renk beyaz sürümü çıkarılır.

Okunmayacak sürümler otomatik atlanır:
  - solid > 0.90  : içi dolu kare app ikonu (silüet beyaz kareye dönüşür)
  - soft  > 0.22  : yumuşak gradyan (silüet bulanık lekeye dönüşür)
Bu logolar koyu zeminde renkli haliyle veya açık karo içinde kullanılır.
"""
import glob, os, sys
from pathlib import Path

import numpy as np
from PIL import Image

LOGOS = Path(__file__).resolve().parent.parent / "logos"
SKIP_FILE = Path(__file__).resolve().parent / "white_skip.txt"


def white(im: Image.Image) -> Image.Image:
    out = Image.new("RGBA", im.size, (255, 255, 255, 255))
    out.putalpha(im.getchannel("A"))
    return out


def legible(im: Image.Image) -> bool:
    a = np.array(im.getchannel("A"))
    solid = float((a == 255).mean())
    soft = float(((a > 8) & (a < 248)).mean())
    return solid <= 0.90 and soft <= 0.22


def main():
    manual = set()
    if SKIP_FILE.exists():
        manual = {l.strip() for l in SKIP_FILE.read_text().splitlines() if l.strip() and not l.startswith("#")}
    n, skipped = 0, []
    for f in sorted(glob.glob(str(LOGOS / "*.png"))):
        if f.endswith("-white.png"):
            continue
        slug = os.path.basename(f)[:-4]
        im = Image.open(f).convert("RGBA")
        if slug in manual or not legible(im):
            p = LOGOS / f"{slug}-white.png"
            if p.exists():
                p.unlink()
            skipped.append(slug)
            continue
        white(im).save(LOGOS / f"{slug}-white.png", optimize=True)
        n += 1
    if skipped:
        SKIP_FILE.write_text("# Beyaz sürümü üretilmeyen logolar (otomatik + elle)\n" + "\n".join(sorted(skipped)) + "\n")
    print(f"{n} beyaz sürüm üretildi, {len(skipped)} atlandı")


if __name__ == "__main__":
    main()
