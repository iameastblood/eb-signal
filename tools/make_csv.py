#!/usr/bin/env python3
"""logos.csv üretir: eski kayıtları korur, katalogdan yenileri ekler.

Kolonlar (eski düzen korunur, sona iki kolon eklenir):
slug,name,kind,svg_url,png_url,source_page,license,brand,white_png_url
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/iameastblood/eb-signal/main/logos"
LEGACY_LICENSE = ("marka hakkı sahibinde; telif serbest, sadece haber/yorum bağlamı, "
                  "onay/ortaklık ima etme")
LOBE_LICENSE = ("MIT (lobe-icons ikon seti) · marka hakkı sahibinde; sadece haber/yorum "
                "bağlamı, onay/ortaklık ima etme")
WM_LICENSE = ("Wikimedia Commons (özgür lisans) · marka hakkı sahibinde; sadece haber/yorum "
              "bağlamı, onay/ortaklık ima etme")


def main():
    old = list(csv.DictReader(open(ROOT / "logos.csv")))
    by_slug = {r["slug"]: r for r in old}
    cat = json.loads((ROOT / "tools" / "logo_catalog.json").read_text())
    for e in cat:
        slug = e["slug"]
        src = e["src"]
        if src.startswith("lobe"):
            page = f"https://github.com/lobehub/lobe-icons ({src.split(':')[1]})"
            lic = LOBE_LICENSE
        elif src.startswith("url:"):
            page = src[4:]
            lic = WM_LICENSE
        else:
            page, lic = src, LEGACY_LICENSE
        white = ROOT / "logos" / f"{slug}-white.png"
        by_slug[slug] = {
            "slug": slug,
            "name": e["name"],
            "kind": e["kind"],
            "svg_url": by_slug.get(slug, {}).get("svg_url", ""),
            "png_url": f"{RAW}/{slug}.png",
            "source_page": page,
            "license": lic,
            "brand": e["brand"],
            "white_png_url": f"{RAW}/{slug}-white.png" if white.exists() else "",
        }
    # eski kayıtlara brand/white kolonlarını tamamla
    for slug, r in by_slug.items():
        r.setdefault("brand", "")
        r.setdefault("white_png_url", f"{RAW}/{slug}-white.png" if (ROOT / "logos" / f"{slug}-white.png").exists() else "")
        r.setdefault("license", LEGACY_LICENSE)
    rows = sorted(by_slug.values(), key=lambda r: (r.get("brand") or "zzz", r["slug"]))
    cols = ["slug", "name", "kind", "svg_url", "png_url", "source_page", "license", "brand", "white_png_url"]
    with open(ROOT / "logos.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} satır yazıldı")


if __name__ == "__main__":
    main()
