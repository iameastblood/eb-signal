#!/usr/bin/env python3
"""Her logo için koyu zemin sürümü üretir: <slug>-white.png

Beyaz silüet, alfa kanalı korunarak üretilir. Logo yeniden çizilmez, rengi
değiştirilmez; yalnız aynı vektörün tek renk beyaz sürümü çıkarılır.
Koyu EB SIGNAL zeminlerinde ve video karelerinde kullanılır.
"""
import glob, os, sys
from pathlib import Path
from PIL import Image

LOGOS = Path(__file__).resolve().parent.parent / "logos"


def white(im: Image.Image) -> Image.Image:
    a = im.getchannel("A")
    out = Image.new("RGBA", im.size, (255, 255, 255, 255))
    out.putalpha(a)
    return out


def main():
    n = 0
    for f in sorted(glob.glob(str(LOGOS / "*.png"))):
        if f.endswith("-white.png"):
            continue
        slug = os.path.basename(f)[:-4]
        im = Image.open(f).convert("RGBA")
        white(im).save(LOGOS / f"{slug}-white.png", optimize=True)
        n += 1
    print(f"{n} beyaz sürüm üretildi")


if __name__ == "__main__":
    main()
