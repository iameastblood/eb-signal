#!/usr/bin/env python3
"""Her logo için koyu zemin sürümü üretir: <slug>-white.png

Beyaz silüet, alfa kanalı korunarak üretilir. Logo yeniden çizilmez, rengi
değiştirilmez; yalnız aynı vektörün tek renk beyaz sürümü çıkarılır.

Okunmayacak sürümler otomatik atlanır:
  - solid > 0.90  : içi dolu kare app ikonu (silüet beyaz kareye dönüşür)
  - soft  > 0.22  : yumuşak gradyan (silüet bulanık lekeye dönüşür)
Bu logolar koyu zeminde renkli haliyle veya açık karo içinde kullanılır.

Elle karar verilenler:
  - white_skip.txt  : hiç beyaz sürüm üretilmeyecek slug'lar (elle, üst bölüm)
  - white_force.txt : otomatik kurala rağmen beyaz sürüm üretilecek slug'lar
"""
import glob, os, sys
from pathlib import Path

import numpy as np
from PIL import Image

LOGOS = Path(__file__).resolve().parent.parent / "logos"
SKIP_FILE = Path(__file__).resolve().parent / "white_skip.txt"
FORCE_FILE = Path(__file__).resolve().parent / "white_force.txt"


def read_list(p: Path) -> set:
    if not p.exists():
        return set()
    return {l.strip() for l in p.read_text().splitlines() if l.strip() and not l.startswith("#")}


def read_manual_skips(p: Path) -> set:
    """white_skip.txt içindeki yalnız ELLE bölümünü okur (OTOMATİK bölüm yok sayılır)."""
    if not p.exists():
        return set()
    out, auto = set(), False
    for line in p.read_text().splitlines():
        s = line.strip()
        if s.startswith("#") and "OTOMAT" in s.upper():
            auto = True
            continue
        if not s or s.startswith("#") or auto:
            continue
        out.add(s)
    return out


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
    manual = read_manual_skips(SKIP_FILE)
    force = read_list(FORCE_FILE)
    n, skipped = 0, []
    for f in sorted(glob.glob(str(LOGOS / "*.png"))):
        if f.endswith("-white.png"):
            continue
        slug = os.path.basename(f)[:-4]
        im = Image.open(f).convert("RGBA")
        if slug in manual or (slug not in force and not legible(im)):
            p = LOGOS / f"{slug}-white.png"
            if p.exists():
                p.unlink()
            skipped.append(slug)
            continue
        white(im).save(LOGOS / f"{slug}-white.png", optimize=True)
        n += 1
    auto = sorted(s for s in skipped if s not in manual)
    lines = ["# ELLE atlananlar (bu bölüm korunur). Dolu app ikonu/maskot: beyaz silueti okunmaz, koyu zeminde renkli haliyle veya açık karoda kullanılır."]
    lines += sorted(manual) or ["# (yok)"]
    lines += ["", "# OTOMATİK atlananlar (her koşuda yeniden yazılır; beyaz sürüm istiyorsan slug'ı white_force.txt'ye ekle)"]
    lines += auto or ["# (yok)"]
    SKIP_FILE.write_text("\n".join(lines) + "\n")
    print(f"{n} beyaz sürüm üretildi, {len(skipped)} atlandı")


if __name__ == "__main__":
    main()
