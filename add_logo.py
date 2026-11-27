#!/usr/bin/env python3
"""EB SIGNAL logo ekleme aracı: URL/dosya -> şeffaf, kırpılmış PNG -> koyu zemin kontrolü -> logos.csv.

  python add_logo.py --src https://.../logo.png --slug claude-code --name "Claude Code" \
      --tags coding,agent --source https://anthropic.com/press --brand anthropic

Ne yapar:
  1. Kaynağı indirir/okur (PNG, JPG, WebP; SVG ise cairosvg kuruluysa).
  2. Düz beyaz/neredeyse tek renkli zemini şeffaf yapar (köşelerden taşma doldurma), kenar boşluğunu kırpar,
     en uzun kenarı 512 px'e getirir -> logos/<slug>.png
  3. #0A0C10 üzerinde kontrast ölçer. Logo koyu zeminde kaybolacak kadar koyuysa otomatik açık (beyaz silüet)
     sürüm üretir -> logos/<slug>-white.png. Logo açık zeminli karoda (#F5F6F8) kaybolacak kadar açıksa
     slug.png koyu silüete çevrilir, orijinal -white olur.
  4. logos.csv'ye satır ekler (etiketler 'tags' kolonunda). Var olan bir slug'ı EZMEZ (--replace-own ile bile
     sadece açıkça istenirse). Başkasının logosunu silme/yeniden adlandırma.
  5. --push ile: git pull --rebase, add, commit "logo: <slug> eklendi", push.
Yapay zekâ ile logo ÇİZİLMEZ; yalnızca resmi kaynak dosya işlenir.
"""
import argparse, csv, io, os, re, subprocess, sys, urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = "https://raw.githubusercontent.com/iameastblood/eb-signal/main/logos"
COLS = ["slug", "name", "kind", "svg_url", "png_url", "source_page", "license", "brand", "white_png_url", "tags"]
DEFAULT_LICENSE = "Resmi kaynaktan; marka hakkı sahibinde; sadece haber/yorum bağlamı, onay/ortaklık ima etme"
TAGS = {"ai-lab", "coding", "agent", "tool", "chip", "cloud", "model", "app", "framework", "other"}
BG, LIGHT_TILE = (10, 12, 16), (245, 246, 248)


def lum(rgb):
    c = np.asarray(rgb, dtype=np.float64) / 255
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def contrast(l1, l2):
    hi, lo = np.maximum(l1, l2), np.minimum(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def load(src):
    if re.match(r"https?://", src):
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0 (EB-SIGNAL add_logo)"})
        data = urllib.request.urlopen(req, timeout=60).read()
    else:
        data = open(src, "rb").read()
    if data.lstrip()[:5] in (b"<?xml", b"<svg ") or src.lower().split("?")[0].endswith(".svg"):
        try:
            import cairosvg
        except ImportError:
            sys.exit("SVG için: pip install cairosvg (ya da PNG ver)")
        data = cairosvg.svg2png(bytestring=data, output_width=1024)
    return Image.open(io.BytesIO(data)).convert("RGBA")


def remove_flat_bg(im, tol=28):
    """Köşelerden başlayıp zemin rengine yakın bağlantılı pikselleri şeffaf yapar (zaten şeffafsa dokunmaz)."""
    a = np.asarray(im).copy()
    if (a[..., 3] < 250).mean() > 0.02 and a[0, 0, 3] < 10:
        return Image.fromarray(a)           # zaten şeffaf zeminli
    h, w = a.shape[:2]
    corners = [a[0, 0, :3], a[0, w - 1, :3], a[h - 1, 0, :3], a[h - 1, w - 1, :3]]
    ref = np.median(np.stack(corners), axis=0)
    if max(np.abs(c.astype(int) - ref).max() for c in corners) > tol:
        print("UYARI: köşeler tek renk değil, zemin silinmedi (elle kontrol et).")
        return Image.fromarray(a)
    near = (np.abs(a[..., :3].astype(int) - ref).max(axis=2) <= tol)
    # kenardan bağlantılı bölge (iç beyazlar, ör. harf içleri, korunur)
    from collections import deque
    seen = np.zeros((h, w), bool); q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True; q.append((ny, nx))
    alpha = np.where(seen, 0, a[..., 3]).astype(np.uint8)
    # kenar yumuşatma (halo azalt)
    al = Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    a[..., 3] = np.asarray(al)
    return Image.fromarray(a)


def trim(im, pad=0, size=512):
    bb = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if not bb: sys.exit("logo tamamen şeffaf/boş çıktı")
    im = im.crop(bb)
    im.thumbnail((size, size), Image.LANCZOS)
    return im


def silhouette(im, rgb):
    out = Image.new("RGBA", im.size, tuple(rgb) + (255,)); out.putalpha(im.getchannel("A")); return out


def visibility(im, bg):
    """Opak piksellerin %'si kaç oranda bg üzerinde kontrastı >= 3:1."""
    a = np.asarray(im); m = a[..., 3] > 128
    if not m.any(): return 0.0
    c = contrast(lum(a[..., :3][m]), lum(bg))
    return float((c >= 3.0).mean())


def main():
    ap = argparse.ArgumentParser(description="EB SIGNAL logo ekle")
    ap.add_argument("--src", required=True, help="logo URL'si veya dosya yolu")
    ap.add_argument("--slug", required=True, help="küçük harf, ASCII, tire (ör. claude-code)")
    ap.add_argument("--name", required=True)
    ap.add_argument("--tags", default="other", help="virgülle: ai-lab,coding,agent,tool,chip,cloud,...")
    ap.add_argument("--source", required=True, help="logonun alındığı sayfa URL'si (press kit, resmi site, Wikimedia)")
    ap.add_argument("--brand", default="", help="marka grubu (varsayılan: slug)")
    ap.add_argument("--kind", default="", help="symbol|wordmark|product (varsayılan: oranla otomatik)")
    ap.add_argument("--license", default=DEFAULT_LICENSE)
    ap.add_argument("--bg-tol", type=int, default=28, help="zemin silme toleransı (0-255)")
    ap.add_argument("--no-bg-removal", action="store_true")
    ap.add_argument("--push", action="store_true", help="pull --rebase, commit, push")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.slug): sys.exit("slug küçük harf/rakam/tire olmalı")
    bad = [t for t in a.tags.split(",") if t.strip() and t.strip() not in TAGS]
    if bad: print(f"UYARI: bilinmeyen etiket {bad}; önerilen: {sorted(TAGS)}")
    csv_path = os.path.join(ROOT, "logos.csv")
    if a.push and not a.dry_run: subprocess.run(["git", "pull", "--rebase", "--autostash"], cwd=ROOT, check=False)
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8"))) if os.path.exists(csv_path) else []
    if any(r["slug"] == a.slug for r in rows):
        sys.exit(f"'{a.slug}' zaten var. Başkasının logosunu ezme; farklı slug seç (ör. {a.slug}-2) ya da düzeltmeyi ayrı commit'te elle yap.")
    if os.path.exists(os.path.join(ROOT, "logos", f"{a.slug}.png")): sys.exit("logos/ içinde bu dosya zaten var")

    im = load(a.src)
    if not a.no_bg_removal: im = remove_flat_bg(im, a.bg_tol)
    im = trim(im)
    on_dark = visibility(im, BG); on_light = visibility(im, LIGHT_TILE)
    main_img, white_img = im, None
    if on_dark < 0.6:                                   # koyu zeminde kaybolur -> açık sürüm
        white_img = silhouette(im, (255, 255, 255)); print(f"koyu logo (koyu zeminde görünürlük %{on_dark*100:.0f}) -> -white sürümü üretildi")
    if on_light < 0.6:                                  # açık karoda kaybolur -> ana dosya koyu silüet
        white_img = im if white_img is None else white_img
        main_img = silhouette(im, BG); print(f"açık logo (açık karoda görünürlük %{on_light*100:.0f}) -> slug.png koyu silüet, orijinal -white")
    asp = im.width / im.height
    kind = a.kind or ("wordmark" if asp > 1.6 else "symbol")
    print(f"{a.slug}: {im.width}x{im.height} {kind}, koyu zeminde %{on_dark*100:.0f} / açık karoda %{on_light*100:.0f} görünür")

    if a.dry_run: print("dry-run: dosya yazılmadı"); return
    os.makedirs(os.path.join(ROOT, "logos"), exist_ok=True)
    main_img.save(os.path.join(ROOT, "logos", f"{a.slug}.png"))
    if white_img: white_img.save(os.path.join(ROOT, "logos", f"{a.slug}-white.png"))
    row = dict(slug=a.slug, name=a.name, kind=kind, svg_url="", png_url=f"{RAW}/{a.slug}.png", source_page=a.source,
               license=a.license, brand=a.brand or a.slug, white_png_url=f"{RAW}/{a.slug}-white.png" if white_img else "",
               tags=",".join(t.strip() for t in a.tags.split(",") if t.strip()))
    with open(csv_path, "a", newline="", encoding="utf-8") as f:   # sadece SATIR EKLE, mevcut satırlara dokunma
        txt = open(csv_path, encoding="utf-8").read()
        if "tags" not in txt.splitlines()[0]:
            print("NOT: logos.csv başlığında 'tags' yok; satır yine de eklendi. tools/make_csv.py tags kolonunu ekler.")
            row = {k: row[k] for k in COLS[:-1]}
        csv.DictWriter(f, fieldnames=list(row.keys()), extrasaction="ignore").writerow(row)
    print(f"OK logos/{a.slug}.png" + (f" + {a.slug}-white.png" if white_img else "") + " ve logos.csv satırı eklendi")
    if a.push:
        g = lambda *c: subprocess.run(["git", *c], cwd=ROOT, check=True)
        g("add", "logos/", "logos.csv"); g("commit", "-m", f"logo: {a.slug} eklendi")
        r = subprocess.run(["git", "push"], cwd=ROOT)
        if r.returncode:
            g("pull", "--rebase"); g("push")


if __name__ == "__main__":
    main()
