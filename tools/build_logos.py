#!/usr/bin/env python3
"""
EB SIGNAL logo builder.

Katalogdan (tools/logo_catalog.json) logo üretir:
  - SVG -> 2048 px render -> alfa kutusuna kırp -> en uzun kenar 512 px
  - PNG kaynak -> alfa kırp -> 512 px
  - Her logo için `<slug>-white.png` (beyaz silüet, koyu zemin için)

Kurallar:
  - Logo ASLA yapay zekâ ile çizilmez, elle yeniden boyanmaz.
  - Yalnız resmi/vektör kaynak kullanılır; kaynak ve lisans logos.csv'ye yazılır.
  - Şeffaflık zorunlu: opak zemin varsa kaynak reddedilir.
"""
import json, os, re, sys, io, subprocess, urllib.request, hashlib
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
LOGOS = ROOT / "logos"
CACHE = Path("/home/ubuntu/src/cache")
LOBE = Path("/home/ubuntu/src/lobe/package/icons")
TARGET = 512
RENDER = 2048

# Beyaz sürüm kararı tek yerde verilsin: make_white.py ile aynı kurallar.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from make_white import legible, read_list, read_manual_skips
except Exception:  # make_white yoksa eski davranış
    legible = lambda im: True
    read_list = lambda p: set()
    read_manual_skips = lambda p: set()

_TOOLS = Path(__file__).resolve().parent


def white_allowed(slug: str, im: Image.Image) -> bool:
    """Elle atlananlar ve okunmaz silüetler için beyaz sürüm üretilmez."""
    if slug in read_manual_skips(_TOOLS / "white_skip.txt"):
        return False
    if slug in read_list(_TOOLS / "white_force.txt"):
        return True
    return legible(im)


def lobe_path(name: str):
    """Renkli sürümü tercih et, yoksa mono."""
    for cand in (f"{name}-color.svg", f"{name}.svg"):
        p = LOBE / cand
        if p.exists():
            return p
    return None


def lobe_text_path(name: str):
    p = LOBE / f"{name}-text.svg"
    return p if p.exists() else None


def fetch(url: str) -> bytes:
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(url.encode()).hexdigest()[:16] + Path(url.split("?")[0]).suffix[:5]
    p = CACHE / key
    if p.exists():
        return p.read_bytes()
    req = urllib.request.Request(url, headers={"User-Agent": "eb-signal-logo-bot/1.0 (editorial use)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    p.write_bytes(data)
    return data


def svg_to_rgba(data: bytes, is_svg=True) -> Image.Image:
    if is_svg:
        png = cairosvg.svg2png(bytestring=data, output_width=RENDER)
        return Image.open(io.BytesIO(png)).convert("RGBA")
    return Image.open(io.BytesIO(data)).convert("RGBA")


def trim(im: Image.Image) -> Image.Image:
    bbox = im.getchannel("A").getbbox()
    if not bbox:
        raise ValueError("boş görsel (tamamen şeffaf)")
    return im.crop(bbox)


def fit(im: Image.Image, target=TARGET) -> Image.Image:
    w, h = im.size
    scale = target / max(w, h)
    if scale != 1:
        im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    return im


def white_silhouette(im: Image.Image) -> Image.Image:
    alpha = im.getchannel("A")
    out = Image.new("RGBA", im.size, (255, 255, 255, 0))
    out.putalpha(alpha)
    solid = Image.new("RGBA", im.size, (255, 255, 255, 255))
    solid.putalpha(alpha)
    return solid

def round_corners(im: Image.Image, ratio=0.225) -> Image.Image:
    """App ikonu karelerini yuvarlat: köşe dışı tam şeffaf olur."""
    w, h = im.size
    r = int(min(w, h) * ratio)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    out = im.copy()
    out.putalpha(Image.composite(im.getchannel("A"), Image.new("L", (w, h), 0), mask))
    return out

def check(im: Image.Image, slug: str) -> list:
    errs = []
    if im.mode != "RGBA":
        errs.append("RGBA değil")
    a = im.getchannel("A")
    if a.getextrema() != (0, 255):
        errs.append(f"alfa aralığı {a.getextrema()}")
    w, h = im.size
    if max(w, h) < 512:
        errs.append(f"küçük {w}x{h}")
    if min(w, h) < 12:
        errs.append(f"aşırı ince {w}x{h}")
    if w / h > 25 or h / w > 25:
        errs.append(f"oran aşırı {w}x{h}")
    return errs


def resolve(src: str):
    """(bytes, is_svg, kaynak_url, kaynak_adı)"""
    kind, _, val = src.partition(":")
    if kind == "lobe":
        p = lobe_path(val)
        if not p:
            raise FileNotFoundError(f"lobe ikonu yok: {val}")
        return p.read_bytes(), True, f"https://github.com/lobehub/lobe-icons ({p.name})", "lobe-icons"
    if kind == "lobe-text":
        p = lobe_text_path(val)
        if not p:
            raise FileNotFoundError(f"lobe wordmark yok: {val}")
        return p.read_bytes(), True, f"https://github.com/lobehub/lobe-icons ({p.name})", "lobe-icons"
    if kind == "url":
        data = fetch(val)
        is_svg = data[:200].lstrip().lower().startswith(b"<svg") or b"<svg" in data[:400].lower()
        return data, is_svg, val, "web"
    if kind == "file":
        p = Path(val)
        return p.read_bytes(), p.suffix.lower() == ".svg", str(p), "local"
    raise ValueError(f"bilinmeyen kaynak: {src}")


def build_one(entry, outdir: Path, write_white=True):
    slug = entry["slug"]
    data, is_svg, url, srcname = resolve(entry["src"])
    im = svg_to_rgba(data, is_svg)
    opaque = entry.get("opaque", False)
    if not opaque and im.getchannel("A").getextrema() == (255, 255):
        raise ValueError("kaynak opak (şeffaflık yok)")
    im = fit(trim(im))
    if entry.get("round"):
        im = round_corners(im)
    errs = check(im, slug)
    im.save(outdir / f"{slug}.png", optimize=True)
    if write_white and not opaque and white_allowed(slug, im):
        white_silhouette(im).save(outdir / f"{slug}-white.png", optimize=True)
    return {"slug": slug, "size": im.size, "errors": errs, "source": url, "srcname": srcname}


def main():
    catalog = json.loads((ROOT / "tools" / "logo_catalog.json").read_text())
    outdir = Path(sys.argv[1]) if len(sys.argv) > 1 else LOGOS
    outdir.mkdir(parents=True, exist_ok=True)
    only = sys.argv[2] if len(sys.argv) > 2 else None
    ok, fail = [], []
    for e in catalog:
        if only and only not in e["slug"]:
            continue
        try:
            r = build_one(e, outdir)
            ok.append(r)
            flag = " !" + ",".join(r["errors"]) if r["errors"] else ""
            print(f"  ok  {r['slug']:28s} {r['size'][0]:4d}x{r['size'][1]:<4d}{flag}")
        except Exception as ex:
            fail.append((e["slug"], str(ex)))
            print(f"  FAIL {e['slug']:28s} {ex}")
    print(f"\n{len(ok)} üretildi, {len(fail)} hata")
    if fail:
        print("HATALAR:", fail)


if __name__ == "__main__":
    main()
