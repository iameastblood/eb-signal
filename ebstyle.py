"""EB SIGNAL - @eastblood_tr house style (PIL). All templates 1600x900 (16:9).
Do not edit layout constants without bumping VERSION + CHANGELOG.md."""
import os, json, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
VERSION = open(os.path.join(ROOT, "VERSION")).read().strip()
FONTS = {'head': "SpaceGrotesk-VariableFont_wght.ttf",
         'body': "Inter-VariableFont_opsz-wght.ttf",
         'mono': "JetBrainsMono-VariableFont_wght.ttf"}
C = dict(bg="#0A0C10", surface="#12151C", surface2="#181C25", line="#262B36",
         text="#F5F6F8", soft="#C3C9D6", muted="#98A0B0", dim="#5E6676", bar="#39414F",
         ember="#FF5A36", ice="#5CC8FF", green="#38D996", amber="#FFB224")
W, H, S, M = 1600, 900, 2, 72   # canvas, supersample, safe margin
WATERMARK = "@eastblood_tr"

def hx(h, a=255):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (a,)

_fc = {}
def font(kind, size, wght=700):
    k = (kind, size, wght)
    if k in _fc: return _fc[k]
    f = ImageFont.truetype(os.path.join(ROOT, "fonts", FONTS[kind]), int(size * S))
    vals = []
    for a in f.get_variation_axes():
        n = a['name'] if isinstance(a['name'], str) else a['name'].decode()
        if 'eight' in n: vals.append(wght)
        elif 'ptical' in n: vals.append(min(max(size, a['minimum']), a['maximum']))
        else: vals.append(a['default'])
    f.set_variation_by_axes(vals); f._eb = (kind, size, wght); _fc[k] = f; return f

def logo(slug_or_path):
    p = slug_or_path
    if not os.path.exists(p): p = os.path.join(ROOT, "logos", f"{slug_or_path}.png")
    if not os.path.exists(p): raise SystemExit(f"logo yok: {slug_or_path} (logos.csv'ye bak, AI ile logo ÇİZME)")
    return Image.open(p).convert("RGBA")


# ---------- emphasis markup ----------
_MARK = re.compile(r"\[\[(.+?)\]\]|\*(?!\s)(.+?)(?<!\s)\*")
def parse_marks(t, highlight=None):
    """'Fiyat *yarıya* indi' / 'Fiyat [[yarıya]] indi' -> ('Fiyat yarıya indi', [(6,12)]). Max 2 emphasis per text block."""
    out, hl, last, n = "", [], 0, 0
    for m in _MARK.finditer(t):
        out += t[last:m.start()]; g = m.group(1) or m.group(2)
        hl.append((len(out), len(out)+len(g))); out += g; last = m.end(); n += 1
    out += t[last:]
    if highlight and highlight in out and not hl: i = out.index(highlight); hl.append((i, i+len(highlight))); n += 1
    if n > 2: raise SystemExit(f"bir metin bloğunda en fazla 2 vurgu: {t[:50]}...")
    return out, hl

def plain(t): return parse_marks(t)[0] if t else t

def bold_of(f):
    """Slightly bolder variant of font f (same family/size) for emphasis. Head max 700, body +200."""
    kind, size, wght = f._eb
    return font(kind, size, min(wght+(100 if kind == 'head' else 200), 700 if kind != 'body' else 900))

_brands = {}
def is_brand(text, slug):
    """True when `text` is just the brand name of logo `slug` (name/brand/slug in logos.csv) -> must not be printed next to the logo."""
    import csv
    if not _brands:
        try:
            for r in csv.DictReader(open(os.path.join(ROOT, "logos.csv"), encoding="utf-8")):
                _brands[r["slug"]] = {re.sub(r"\W", "", x.lower()) for x in (r["slug"], r.get("name", ""), r.get("brand", ""))}
        except Exception: pass
    n = re.sub(r"\W", "", (text or "").lower())
    return bool(n) and n in (_brands.get(slug) or {re.sub(r"\W", "", (slug or "").lower())})

def has_logo(slug):
    return bool(slug) and os.path.exists(os.path.join(ROOT, "logos", f"{slug}.png"))

class Canvas:
    def __init__(s):
        s.im = Image.new("RGBA", (W*S, H*S), hx(C['bg'])); s.d = ImageDraw.Draw(s.im)
    def px(s, v): return int(round(v*S))
    def rrect(s, b, r, fill=None, outline=None, width=1):
        s.d.rounded_rectangle([s.px(v) for v in b], radius=s.px(r), fill=fill, outline=outline, width=s.px(width) if outline else 0)
    def rect(s, b, fill): s.d.rectangle([s.px(v) for v in b], fill=fill)
    def line(s, xy, fill, width=1): s.d.line([s.px(v) for v in xy], fill=fill, width=s.px(width))
    def text(s, xy, t, f, fill, anchor="la"): s.d.text((s.px(xy[0]), s.px(xy[1])), t, font=f, fill=fill, anchor=anchor)
    def tw(s, t, f): return s.d.textlength(t, font=f)/S
    def tri(s, x, y, up, col, r=9):
        pts = [(x-r, y+r*0.8), (x+r, y+r*0.8), (x, y-r)] if up else [(x-r, y-r*0.8), (x+r, y-r*0.8), (x, y+r)]
        s.d.polygon([(s.px(a), s.px(b)) for a, b in pts], fill=col)
    def wrap(s, t, f, maxw):
        lines, cur = [], ""
        for w in t.split():
            tt = (cur+" "+w).strip()
            if s.tw(tt, f) <= maxw or not cur: cur = tt
            else: lines.append(cur); cur = w
        if cur: lines.append(cur)
        return lines
    def layout(s, t, highlight, f, maxw):
        """Lines of (word, emph) after markup parsing. Emphasis words use the bolder font variant for measuring."""
        t, hl = parse_marks(t, highlight); hf = bold_of(f)
        lines, cur, cw = [], [], 0
        for m in re.finditer(r"\S+", t):
            h = any(a_ < m.end() and m.start() < b_ for a_, b_ in hl); ff = hf if h else f
            ww = s.tw(m.group()+" ", ff)
            if cw+ww-s.tw(" ", ff) > maxw and cur: lines.append(cur); cur, cw = [], 0
            cur.append((m.group(), h)); cw += ww
        if cur: lines.append(cur)
        return lines
    def rich(s, x, y, t, highlight, f, maxw, step, maxlines, col=None, hcol=None):
        """Wrapped text. Emphasis = ember + slightly bolder weight. Mark words with *word* or [[word]] (max 2 per block);
        legacy `highlight` substring still works. Returns the y after the last line."""
        col = col or hx(C['text']); hcol = hcol or hx(C['ember']); hf = bold_of(f)
        lines = s.layout(t, highlight, f, maxw)
        if len(lines) > maxlines: raise SystemExit(f"metin çok uzun ({len(lines)} satır > {maxlines}): {t[:40]}...")
        for i, ln in enumerate(lines):
            xx = x
            for w, h in ln:
                ff = hf if h else f; s.text((xx, y+i*step), w, ff, hcol if h else col); xx += s.tw(w+" ", ff)
        return y+len(lines)*step
    def glow(s, cx, cy, r, color, alpha=80):
        g = Image.new("RGBA", s.im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
        d.ellipse([s.px(v) for v in (cx-r, cy-r, cx+r, cy+r)], fill=hx(color, alpha))
        s.im.alpha_composite(g.filter(ImageFilter.GaussianBlur(s.px(r/2.2))))
    def save(s, path, meta):
        out = s.im.resize((W, H), Image.LANCZOS).convert("RGB"); out.save(path)
        meta = dict(meta, style="EB SIGNAL", version=VERSION, size=[W, H], file=os.path.basename(path))
        json.dump(meta, open(os.path.splitext(path)[0]+".meta.json", "w"), ensure_ascii=False, indent=1)
        return path

# ---------- shared parts ----------
def logo_tile(cv, xy, size, slug, pad=0.2, radius=None, wide=True):
    """White rounded tile + ORIGINAL-colour official logo. Never recolour, never AI-draw.
    Wordmark logos (aspect > 1.6) get a wider tile (2.4x) when wide=True. Returns tile width."""
    x, y = xy; r = size*0.24 if radius is None else radius
    lg = logo(slug).copy(); asp = lg.width/lg.height
    tw = size*2.4 if (wide and asp > 1.6) else size
    cv.rrect((x, y, x+tw, y+size), r, fill=hx("#F5F6F8"))
    iw, ih = cv.px(tw-2*size*pad), cv.px(size*(1-2*pad))
    lg.thumbnail((iw, ih), Image.LANCZOS)
    cv.im.alpha_composite(lg, (cv.px(x)+(cv.px(tw)-lg.width)//2, cv.px(y)+(cv.px(size)-lg.height)//2))
    return tw

def letter_tile(cv, xy, size, name):
    x, y = xy
    cv.rrect((x, y, x+size, y+size), size*0.24, fill=hx(C['surface2']), outline=hx(C['line']), width=2)
    cv.text((x+size/2, y+size/2), name[:1].upper(), font('head', size*0.5, 700), hx(C['muted']), "mm")
    return size

def any_tile(cv, xy, size, slug, name="", **k):
    return logo_tile(cv, xy, size, slug, **k) if slug else letter_tile(cv, xy, size, name or "?")

def bg_image(cv, path, fade_to=1180, floor=0.2):
    p = path if os.path.exists(path) else os.path.join(ROOT, "bg", path)
    bg = Image.open(p).convert("RGBA").resize(cv.im.size, Image.LANCZOS); cv.im.alpha_composite(bg)
    xs = np.linspace(0, 1, cv.im.size[0]); fade = np.clip(1-xs/(fade_to/W), 0, 1)**0.8
    a = np.repeat(((floor+(1-floor)*fade)*255)[None, :], cv.im.size[1], 0).astype(np.uint8)
    ov = Image.new("RGBA", cv.im.size, hx(C['bg'])); ov.putalpha(Image.fromarray(a)); cv.im.alpha_composite(ov)

def top(cv, tag, stamp=None, stamp_col=None):
    cv.rect((M, 60, M+56, 66), hx(C['ember']))
    cv.text((M+72, 63), tag.upper(), font('mono', 22, 700), hx(C['ember']), "lm")
    if stamp:
        col = hx(stamp_col or C['amber']); f = font('mono', 20, 700); w = cv.tw(stamp, f)+36
        cv.rrect((W-M-w, 46, W-M, 80), 17, outline=col, width=2); cv.text((W-M-w/2, 63), stamp, f, col, "mm")

def bottom(cv, source, date, maxw=520):
    cv.line((M, 804, W-M, 804), hx(C['line']), 2)
    fs = font('body', 22, 500); src = "Kaynak: "+source
    if cv.tw(src, fs) > maxw:
        while cv.tw(src+"…", fs) > maxw: src = src[:-1]
        src = src.rstrip()+"…"
    cv.text((M, 852), src, fs, hx(C['muted']), "lm"); cv.text((W-M, 852), date, fs, hx(C['muted']), "rm")
    f = font('body', 26, 600); w = cv.tw(WATERMARK, f)+56
    cv.rrect((W/2-w/2, 826, W/2+w/2, 878), 26, fill=hx(C['surface2']), outline=hx("#343B49"), width=2)
    cv.text((W/2, 852), WATERMARK, f, hx(C['text']), "mm")

def stamp_of(d):
    if d.get("example"): return "ÖRNEK VERİ" if d.get("example") is True else d["example"]
    return d.get("stamp")

# ---------- T1 NEWS ----------
def t1(d, out):
    cv = Canvas()
    if d.get("bg"): bg_image(cv, d["bg"])
    top(cv, d.get("tag", "HABER"), stamp_of(d))
    tw = any_tile(cv, (M, 150), 112, d.get("logo"), d.get("company", ""))
    if has_logo(d.get("logo")): cv.text((M+tw+24, 206), d.get("meta", ""), font('body', 24, 500), hx(C['muted']), "lm")   # logo shown: never repeat the brand name
    else:
        cv.text((M+tw+24, 186), d.get("company", ""), font('head', 40, 700), hx(C['text']), "lm")
        cv.text((M+tw+24, 228), d.get("meta", ""), font('body', 24, 500), hx(C['muted']), "lm")
    y = cv.rich(M, 330, d["headline"], d.get("highlight"), font('head', 80, 700), 880, 92, 3)
    fs = font('body', 32, 400)
    ye = cv.rich(M, y+20, d["sub"], None, fs, 780, 46, 2, col=hx("#B4BBC9")) if d.get("sub") else y
    cy = (ye+36) if d.get("sub") else y+20+36; x = M; fc = font('body', 26, 600)
    for t in d.get("chips", [])[:3]:
        w = cv.tw(t, fc)+48
        if cy+56 > 790: break
        cv.rrect((x, cy, x+w, cy+56), 28, fill=hx(C['surface2'], 235), outline=hx("#343B49"), width=2)
        cv.text((x+w/2, cy+28), t, fc, hx(C['text']), "mm"); x += w+16
    bottom(cv, d["source"], d["date"]); return cv.save(out, dict(template="T1", data=d))

# ---------- T2 BENCHMARK ----------
def t2(d, out):
    cv = Canvas(); top(cv, d.get("tag", "BENCHMARK"), stamp_of(d))
    cv.rich(M, 112, d["title"], d.get("highlight"), font("head", 60, 700), 1150, 70, 2)
    hib = d.get("higher_is_better", True)
    sub = plain(d.get("subtitle", "")) + ("  ·  " if d.get("subtitle") else "") + ("yüksek olan daha iyi" if hib else "düşük olan daha iyi")
    cv.text((M, 274), sub, font('body', 26, 400), hx(C['muted']))
    rows = sorted(d["rows"], key=lambda r: r["value"], reverse=hib)[:6]
    n = len(rows); rh = 86 if n <= 5 else 74; top_y = 340
    vmax = d.get("max") or max(r["value"] for r in rows)*1.08
    x0, x1 = 470, 1380
    for v in (0, .25, .5, .75, 1):
        gx = x0+(x1-x0)*v; cv.line((gx, top_y-4, gx, top_y+rh*n-12), hx("#3A4150") if v == 0 else hx(C['line']), 2 if v == 0 else 1)
    fmt = d.get("format", "{:.1f}"); unit = d.get("unit", "")
    for i, r in enumerate(rows):
        y = top_y+i*rh; win = i == 0
        any_tile(cv, (M, y+2), 60, r.get("logo"), r.get("company", r["name"]), pad=0.18, radius=14, wide=False)
        if has_logo(r.get("logo")): cv.text((M+82, y+33), r["name"], font('head', 34, 700), hx(C['text'] if win else "#D5D9E2"), "lm")   # logo shown: no brand line under the name
        else:
            cv.text((M+82, y+18), r["name"], font('head', 32, 700), hx(C['text'] if win else "#D5D9E2"), "lm")
            cv.text((M+82, y+50), r.get("company", ""), font('body', 22, 500), hx(C['muted']), "lm")
        bw = max((x1-x0)*r["value"]/vmax, 90)
        cv.rrect((x0, y+8, x1, y+56), 10, fill=hx(C['surface']))
        cv.rrect((x0, y+8, x0+bw, y+56), 10, fill=hx(C['ember'] if win else C['bar']))
        cv.text((x0+bw-18, y+33), fmt.format(r["value"])+unit, font('head', 38, 700), hx(C['bg']) if win else hx("#E4E7EE"), "rm")
    bottom(cv, d["source"], d["date"]); return cv.save(out, dict(template="T2", data=d))

# ---------- T3 VERSUS ----------
def t3(d, out):
    """metrics: [{label, values:[a,b] (numbers), display:[str,str], better:'higher'|'lower'|'none'}]"""
    cv = Canvas(); top(cv, d.get("tag", "KARŞILAŞTIRMA"), stamp_of(d))
    cv.rich(M, 104, d["title"], d.get("highlight"), font('head', 60, 700), 1456, 70, 1)
    cv.text((M, 186), plain(d.get("subtitle", "")), font('body', 28, 400), hx(C['muted']))
    cw, y0, y1 = 690, 250, 784
    mets = d["metrics"][:4]
    for ci, side in enumerate([d["left"], d["right"]]):
        x = M if ci == 0 else W-M-cw
        cv.rrect((x, y0, x+cw, y1), 28, fill=hx(C['surface']), outline=hx(C['line']), width=2)
        any_tile(cv, (x+36, y0+32), 84, side.get("logo"), side["name"], radius=20, wide=False)
        if has_logo(side.get("logo")) and is_brand(side["name"], side["logo"]):      # name would just repeat the logo: show only the model/sub line
            cv.text((x+144, y0+74), side.get("sub") or "", font('head', 38, 700), hx(C['text']), "lm")
        else:
            cv.text((x+144, y0+55), side["name"], font('head', 38, 700), hx(C['text']), "lm")
            cv.text((x+144, y0+92), side.get("sub", ""), font('body', 24, 500), hx(C['muted']), "lm")
        for mi, m in enumerate(mets):
            ry = y0+158+mi*88; a, b = m["values"]; bet = m.get("better", "higher")
            cv.line((x+36, ry-10, x+cw-36, ry-10), hx(C['line']), 1)
            lab = m["label"] + ("  ↓ iyi" if bet == "lower" else "")
            cv.text((x+36, ry+36), m["label"], font('body', 26, 500), hx(C['muted']), "lm")
            if bet == "lower": cv.text((x+36+cv.tw(m["label"]+" ", font('body', 26, 500)), ry+37), "(düşük iyi)", font('body', 20, 500), hx(C['dim']), "lm")
            win = None if bet == "none" or a == b else (0 if (a > b) == (bet == "higher") else 1)
            vf = font('head', 44, 700); txt = m.get("display", [str(a), str(b)])[ci]
            w_ = win == ci
            cv.text((x+cw-36, ry+34), txt, vf, hx(C['ember'] if w_ else C['soft']), "rm")
            if w_: cv.tri(x+cw-36-cv.tw(txt, vf)-24, ry+34, bet == "higher", hx(C['ember']))
    cx, cy = W/2, (y0+y1)/2-10
    cv.glow(cx, cy, 60, C['ember'], 60)
    cv.d.ellipse([cv.px(v) for v in (cx-44, cy-44, cx+44, cy+44)], fill=hx(C['bg']), outline=hx(C['ember']), width=cv.px(3))
    cv.text((cx, cy+1), "VS", font('head', 34, 700), hx(C['text']), "mm")
    bottom(cv, d["source"], d["date"]); return cv.save(out, dict(template="T3", data=d))

# ---------- T4 LEAK / SCREENSHOT ----------
def t4(d, out):
    """Left: claim + status; right: screenshot frame. highlight_box = [x0,y0,x1,y1] in screenshot px."""
    cv = Canvas(); top(cv, d.get("tag", "SIZINTI"), stamp_of(d) or d.get("status_stamp"), )
    lx, lw = M, 600
    st = d.get("status", "Doğrulanmadı"); sf = font('mono', 20, 700); sw = cv.tw(st.upper(), sf)+40
    cv.rrect((lx, 140, lx+sw, 180), 20, fill=hx("#2A2312"), outline=hx(C['amber']), width=2)
    cv.text((lx+sw/2, 160), st.upper(), sf, hx(C['amber']), "mm")
    y = cv.rich(lx, 214, d["title"], d.get("highlight"), font('head', 60, 700), lw, 70, 4)
    fs = font('body', 28, 400)
    pts = d.get("points", [])[:3]; yy = y+28
    for p in pts:
        cv.rect((lx, yy+12, lx+10, yy+22), hx(C['ember']))
        yy = cv.rich(lx+28, yy, p, None, fs, lw-28, 40, 2, col=hx(C['soft']))+18
    # frame: fitted to screenshot aspect, centred in y 110..786
    p = d["screenshot"]; p = p if os.path.exists(p) else os.path.join(ROOT, p)
    shot = Image.open(p).convert("RGBA")
    fx0, fx1 = 720, W-M; innerw = fx1-fx0-48
    sc_l = min(innerw/shot.width, 560/shot.height); innerh = shot.height*sc_l
    fh = innerh+53+48; fy0 = 110+(676-fh)/2; fy1 = fy0+fh
    cv.rrect((fx0, fy0, fx1, fy1), 24, fill=hx(C['surface']), outline=hx(C['line']), width=2)
    cv.rect((fx0+2, fy0+52, fx1-2, fy0+53), hx(C['line']))
    for i in range(3):
        cv.d.ellipse([cv.px(v) for v in (fx0+24+i*22, fy0+20, fx0+38+i*22, fy0+34)], fill=hx("#3A4150"))
    cv.text((fx0+100, fy0+27), d.get("handle", ""), font('mono', 20, 700), hx(C['muted']), "lm")
    sc = sc_l*S; sh = shot.resize((int(shot.width*sc), int(shot.height*sc)), Image.LANCZOS)
    mask = Image.new("L", sh.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, sh.width, sh.height), radius=cv.px(14), fill=255)
    ox = cv.px(fx0+24)+(cv.px(innerw)-sh.width)//2; oy = cv.px(fy0+53+24)
    cv.im.paste(sh, (ox, oy), mask)
    if d.get("highlight_box"):
        a, b, c2, e = d["highlight_box"]
        cv.d.rounded_rectangle((ox+a*sc-cv.px(8), oy+b*sc-cv.px(6), ox+c2*sc+cv.px(8), oy+e*sc+cv.px(6)), radius=cv.px(10), outline=hx(C['ember']), width=cv.px(4))
    bottom(cv, d["source"], d["date"]); return cv.save(out, dict(template="T4", data=d))

# ---------- T5 BIG NUMBER ----------
def t5(d, out):
    cv = Canvas()
    if d.get("bg"): bg_image(cv, d["bg"], fade_to=1500, floor=0.35)
    top(cv, d.get("tag", "RAKAM"), stamp_of(d))
    tw = any_tile(cv, (M, 140), 88, d.get("logo"), d.get("company", ""), radius=20)
    if has_logo(d.get("logo")): cv.text((M+tw+24, 184), d.get("meta", ""), font('body', 24, 500), hx(C['muted']), "lm")
    else:
        cv.text((M+tw+24, 168), d.get("company", ""), font('head', 36, 700), hx(C['text']), "lm")
        cv.text((M+tw+24, 206), d.get("meta", ""), font('body', 24, 500), hx(C['muted']), "lm")
    nf = font('head', 250, 700); num = d["number"]
    while cv.tw(num, nf) > 900: nf = font('head', nf.size/S-10, 700)
    cv.text((M-8, 470), num, nf, hx(C['ember']), "ls")
    y = cv.rich(M, 500, d["label"], None, font('head', 48, 700), 900, 58, 2)
    if d.get("context"):
        cv.rich(M, y+24, d["context"], None, font('body', 28, 400), 900, 40, 2, col=hx("#B4BBC9"))
    if d.get("compare"):
        x0, y0, x1 = 1080, 300, W-M
        items = d["compare"][:3]; y = y0
        for it in items:
            cv.rrect((x0, y, x1, y+128), 22, fill=hx(C['surface'], 235), outline=hx(C['line']), width=2)
            cv.text((x0+28, y+38), it["label"], font('body', 24, 500), hx(C['muted']), "lm")
            cv.text((x0+28, y+88), it["value"], font('head', 44, 700), hx(C['text']), "lm")
            y += 148
    bottom(cv, d["source"], d["date"]); return cv.save(out, dict(template="T5", data=d))

# ---------- T6 QUOTE ----------
def t6(d, out):
    cv = Canvas()
    if d.get("bg"): bg_image(cv, d["bg"], fade_to=1600, floor=0.55)
    top(cv, d.get("tag", "ALINTI"), stamp_of(d))
    qf = font('head', 54, 600)
    nlines = len(cv.layout(d["quote"], d.get("highlight"), qf, 1250))
    if nlines > 6: raise SystemExit("alıntı en fazla 6 satır")
    blockh = nlines*68+70+88; y0 = 110+(690-blockh)/2
    cv.text((M-6, y0+130), "“", font('head', 260, 700), hx(C['ember']), "ls")
    y = cv.rich(M+150, y0, d["quote"], d.get("highlight"), qf, 1250, 68, 6)+70
    tw = any_tile(cv, (M+150, y), 88, d.get("logo"), d.get("name", ""), radius=20)
    cv.text((M+150+tw+24, y+28), d["name"], font('head', 36, 700), hx(C['text']), "lm")
    cv.text((M+150+tw+24, y+66), d.get("role", ""), font('body', 24, 500), hx(C['muted']), "lm")
    bottom(cv, d["source"], d["date"]); return cv.save(out, dict(template="T6", data=d))

# ---------- T8 PERSON COMPOSITE ----------
import hashlib, urllib.request, tempfile

def _fetch(path_or_url):
    """Local path or http(s) URL -> local path (URL cached in tmp)."""
    if not str(path_or_url).startswith("http"):
        p = path_or_url if os.path.exists(path_or_url) else os.path.join(ROOT, path_or_url)
        if not os.path.exists(p): raise SystemExit(f"dosya yok: {path_or_url}")
        return p
    cache = os.path.join(tempfile.gettempdir(), "ebsignal_" + hashlib.md5(path_or_url.encode()).hexdigest() + os.path.splitext(path_or_url.split("?")[0])[1][:5])
    if not os.path.exists(cache):
        req = urllib.request.Request(path_or_url, headers={"User-Agent": "Mozilla/5.0 (EB-SIGNAL render)"})
        open(cache, "wb").write(urllib.request.urlopen(req, timeout=60).read())
    return cache

MATTING_CHAIN = ["birefnet-portrait", "birefnet-general", "isnet-general-use", "u2net_human_seg"]
# model download sizes (rembg, one-time, ~/.rembg/models): birefnet-portrait ~928 MB, birefnet-general ~928 MB,
# isnet-general-use ~170 MB, u2net_human_seg ~168 MB. CPU time on a 1600px photo: ~60 s / ~30 s / ~5 s / ~1 s (first run adds download).

def _decontaminate(rgb_img, alpha_img):
    """Remove background colour bleed on the edge (light halo): estimate true foreground colour under soft alpha."""
    try:
        from pymatting import estimate_foreground_ml
        im = np.asarray(rgb_img).astype(np.float64)/255; al = np.asarray(alpha_img).astype(np.float64)/255
        fg = estimate_foreground_ml(im, al)
        return Image.fromarray((np.clip(fg, 0, 1)*255).astype(np.uint8))
    except Exception:
        return rgb_img

def cutout_person(path, max_side=1600, precut=None, model=None):
    """Real photo -> (RGBA cutout, method). Order of preference:
       1. `precut` = an already cut-out RGBA PNG (path/URL) made by any other AI tool -> used as is (only edge refinement after).
       2. `person` itself is a PNG with real transparency -> used as is.
       3. rembg chain (best first): birefnet-portrait > birefnet-general > isnet-general-use (+alpha matting) > u2net_human_seg.
          Force one with model=... or env EB_MATTING_MODEL. Result cached in tmp (re-renders are instant).
       4. rembg/onnx unusable -> the photo in a rounded, feathered frame.
    The face is NEVER regenerated or repainted; only cut, edge-cleaned and colour-graded."""
    if precut:
        pc = Image.open(_fetch(precut)).convert("RGBA")
        if pc.getchannel("A").getextrema()[0] == 255: print("UYARI: precut PNG şeffaf değil")
        return pc, "precut"
    im0 = Image.open(path)
    if im0.mode in ("RGBA", "LA") and im0.getchannel("A").getextrema()[0] < 250: return im0.convert("RGBA"), "png-alpha"
    im = im0.convert("RGB"); im.thumbnail((max_side, max_side), Image.LANCZOS)
    chain = [model or os.environ.get("EB_MATTING_MODEL")] if (model or os.environ.get("EB_MATTING_MODEL")) else MATTING_CHAIN
    try:
        from rembg import remove, new_session
    except Exception as e:  # noqa
        remove = None; print("UYARI: rembg yok:", type(e).__name__)
    if remove:
        key = hashlib.md5((open(path, "rb").read() if os.path.exists(path) else path.encode())[:2000000]).hexdigest()
        for m in chain:
            cache = os.path.join(tempfile.gettempdir(), f"ebsignal_cut_{key}_{m}.png")
            try:
                if os.path.exists(cache): out = Image.open(cache).convert("RGBA")
                else:
                    out = remove(im, session=new_session(m), alpha_matting=(m == "isnet-general-use"),
                                 alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=15,
                                 alpha_matting_erode_size=8).convert("RGBA")
                    out.save(cache)
                if out.getchannel("A").getbbox() is None: raise RuntimeError("empty mask")
                return out, m
            except Exception as e:  # noqa
                print(f"UYARI: {m} başarısız ({type(e).__name__}), sıradaki model deneniyor")
    print("UYARI: hiçbir matting modeli çalışmadı, yumuşak kenarlı çerçeve kullanılıyor")
    rgba = im.convert("RGBA"); m = Image.new("L", rgba.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, rgba.width-1, rgba.height-1], radius=int(min(rgba.size)*0.06), fill=255)
    rgba.putalpha(m.filter(ImageFilter.GaussianBlur(max(2, min(rgba.size)//60)))); return rgba, "frame"

def _cover(im, size):
    r = max(size[0]/im.width, size[1]/im.height); im = im.resize((int(im.width*r)+1, int(im.height*r)+1), Image.LANCZOS)
    l, t = (im.width-size[0])//2, (im.height-size[1])//2; return im.crop((l, t, l+size[0], t+size[1]))

def t8(d, out):
    cv = Canvas(); CW, CH = cv.im.size
    # --- background: topical photo / AI scene, graded dark. Default ember bg. No faces in backdrops.
    bgp = _fetch(d["bg"]) if d.get("bg") and str(d["bg"]).startswith("http") else None
    if not bgp:
        name = d.get("bg") or "ember_01.jpg"
        bgp = name if os.path.exists(name) else os.path.join(ROOT, "bg", name)
    bg = _cover(Image.open(bgp).convert("RGB"), (CW, CH))
    arr = np.asarray(bg).astype(np.float32)/255; lum = arr.mean(axis=2, keepdims=True)
    arr = lum*0.55 + arr*0.45                       # desaturate toward EB SIGNAL dark
    arr = arr*np.array([0.80, 0.86, 1.0]) * 0.62     # cool navy, darker
    bg = Image.fromarray((np.clip(arr, 0, 1)*255).astype(np.uint8)).convert("RGBA"); cv.im.alpha_composite(bg)
    xs = np.linspace(0, 1, CW); fade = np.clip(1-(xs-0.0)/(1060/W), 0, 1)**0.9       # left text-side darkening
    ov = Image.new("RGBA", cv.im.size, hx(C['bg'])); ov.putalpha(Image.fromarray(np.repeat((fade*215)[None, :], CH, 0).astype(np.uint8)))
    cv.im.alpha_composite(ov)
    cv.glow(1320, 760, 420, C['ember'], 70)
    # --- person: AI matting -> edge refine -> colour match -> light wrap -> soft shadow -> alpha-following rim glow
    cut, method = cutout_person(_fetch(d["person"]) if d.get("person") else None, precut=d.get("person_cutout"), model=d.get("matting_model"))
    al = cut.getchannel("A"); bb = al.point(lambda v: 255 if v > 24 else 0).getbbox(); cut = cut.crop(bb)
    W0, H0 = cut.size
    # which sides of the photo frame cut the body (not the real silhouette): those get faded, never glowed or outlined
    keep = float(d.get("person_crop_bottom", 0.66))
    cut = cut.crop((0, 0, W0, int(H0*keep))); H0 = cut.height
    # wide photo (torso spreads sideways): crop to a bust-shaped window centred on the head (centroid of the top of the matte)
    A0 = np.asarray(cut.getchannel("A")).astype(np.float32)/255
    maxar = float(d.get("person_max_aspect", 0.95))
    if W0 > H0*maxar:
        top_rows = A0[:max(1, int(H0*0.22))]; cols = top_rows.sum(axis=0)
        hx_c = int((cols*np.arange(W0)).sum()/max(cols.sum(), 1e-6)); half = int(H0*maxar/2)
        l = min(max(hx_c-half, 0), W0-2*half); cut = cut.crop((l, 0, l+2*half, H0)); W0 = cut.width
        A0 = np.asarray(cut.getchannel("A")).astype(np.float32)/255
    # which sides of the (cropped) photo cut the body rather than the real silhouette: faded later, never glowed or outlined
    touch_l = A0[:int(H0*0.8), :3].mean() > 0.2; touch_r = A0[:int(H0*0.8), -3:].mean() > 0.2
    ph = int(S*(H-50)); pw = int(W0*ph/H0)
    if pw > S*W*0.46: pw = int(S*W*0.46); ph = int(H0*pw/W0)
    cut = cut.resize((pw, ph), Image.LANCZOS)
    rgb_i = _decontaminate(cut.convert("RGB"), cut.getchannel("A")) if method != "frame" else cut.convert("RGB")
    a = np.asarray(cut.getchannel("A")).astype(np.float32)/255
    # edge refinement: tighten the matte a little (kills the faint halo), then 1px soften; contrast curve on the soft band
    a_img = Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(S*0.7))
    a = np.asarray(a_img).astype(np.float32)/255; a = np.clip((a-0.06)/0.88, 0, 1); a = a*a*(3-2*a)
    # frame-cut sides: fade out smoothly so no straight panel edge is visible
    xs_ = np.linspace(0, 1, pw)[None, :]; ys_ = np.linspace(0, 1, ph)[:, None]
    a = a*np.clip((1-ys_)/0.24, 0, 1)                                   # bottom always melts into the scene
    if touch_l: a = a*np.clip(xs_/0.16, 0, 1)
    if touch_r: a = a*np.clip((1-xs_)/0.16, 0, 1)
    px_, py_ = CW-pw-int(S*10), CH-ph
    region = cv.im.crop((px_, py_, px_+pw, py_+ph))
    bgblur = np.asarray(region.convert("RGB").filter(ImageFilter.GaussianBlur(S*30))).astype(np.float32)/255
    rgb = np.asarray(rgb_i).astype(np.float32)/255; l = rgb.mean(axis=2, keepdims=True)
    rgb = l+(rgb-l)*0.90; rgb = np.clip((rgb-0.5)*1.05+0.5, 0, 1)*np.array([0.97, 0.98, 1.0])    # grade (face untouched otherwise)
    fgm = (rgb*a[..., None]).sum((0, 1))/max(a.sum(), 1); bgm = bgblur.reshape(-1, 3).mean(0)
    rgb = np.clip(rgb+(bgm-fgm)*0.18, 0, 1)                                                        # colour match to the scene
    xx = xs_[..., None]; rgb = np.clip(rgb+np.array([0.10, 0.025, 0.0])*(xx**2.2), 0, 1)            # warm ember light from the right
    inner = np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(S*9))).astype(np.float32)/255
    band = np.clip(1-inner, 0, 1)*a                                                                 # thin zone just inside the silhouette
    rgb = rgb*(1-0.45*band[..., None])+bgblur*0.45*band[..., None]*1.15                              # light wrap from the scene
    ember = np.array(hx(C['ember'])[:3], dtype=np.float32)/255
    rgb = np.clip(rgb+ember*(band*np.clip(xs_*1.2, 0, 1))[..., None]*0.35, 0, 1)                    # ember rim kiss on the right edges
    A_img = Image.fromarray((a*255).astype(np.uint8))
    pad = int(S*60); big = (pw+2*pad, ph+2*pad)
    def padded(im_): c_ = Image.new("L", big, 0); c_.paste(im_, (pad, pad)); return c_
    Ap = padded(A_img)
    shadow = Ap.filter(ImageFilter.GaussianBlur(S*26)).point(lambda v: int(v*0.60))                  # soft contact shadow
    sh = Image.new("RGBA", big, (0, 0, 0, 0)); sh.putalpha(shadow)
    cv.im.alpha_composite(sh, (px_-pad-int(S*22), py_-pad+int(S*10)))
    glow = Ap.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(S*9)).point(lambda v: int(v*0.19))   # follows the matte, not a box; ~50% of v1.1.1 opacity
    gl = Image.new("RGBA", big, hx(C['ember'])); gl.putalpha(glow)
    cv.im.alpha_composite(gl, (px_-pad, py_-pad))
    person = Image.fromarray((rgb*255).astype(np.uint8)).convert("RGBA"); person.putalpha(A_img)
    cv.im.alpha_composite(person, (px_, py_))
    # --- text (code only)
    top(cv, d.get("tag", "KİŞİ"), stamp_of(d))
    y = 130
    if d.get("logo") or d.get("company"):
        tw = any_tile(cv, (M, y), 96, d.get("logo"), d.get("company", ""), radius=22)
        if not has_logo(d.get("logo")) and d.get("company"): cv.text((M+tw+22, y+48), d["company"], font('head', 34, 700), hx(C['text']), "lm")   # logo shown: never repeat the brand name
    y = cv.rich(M, 262, d["headline"], d.get("highlight"), font('head', 60, 700), 730, 70, 4)
    if d.get("quote"):
        qf = font('head', 34, 500); ql = cv.layout("“"+d["quote"]+"”", d.get("quote_highlight"), qf, 680)
        if len(ql) > 4: raise SystemExit("alıntı en fazla 4 satır")
        cv.rect((M, y+28, M+5, y+28+len(ql)*46), hx(C['ember']))
        y = cv.rich(M+28, y+28, "“"+d["quote"]+"”", d.get("quote_highlight"), qf, 680, 46, 4, col=hx(C['soft']))
    if d.get("sub"):
        y = cv.rich(M, y+24, d["sub"], None, font('body', 28, 400), 730, 40, 3, col=hx("#B4BBC9"))
    if y > 672: raise SystemExit("metin çok uzun (kişi bloğuna taşıyor)")
    cv.text((M, 716), d["person_name"], font('head', 36, 700), hx(C['text']), "lm")
    cv.text((M, 756), d.get("role", ""), font('body', 24, 500), hx(C['muted']), "lm")
    # --- source line (only a news source; NO photo credit on the image) and watermark
    bottom(cv, d["source"], d["date"], maxw=560)
    return cv.save(out, dict(template="T8", cutout=method, data=d))

TEMPLATES = dict(t1=t1, t2=t2, t3=t3, t4=t4, t5=t5, t6=t6, t8=t8)
