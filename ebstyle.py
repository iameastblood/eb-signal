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
    f.set_variation_by_axes(vals); _fc[k] = f; return f

def logo(slug_or_path):
    p = slug_or_path
    if not os.path.exists(p): p = os.path.join(ROOT, "logos", f"{slug_or_path}.png")
    if not os.path.exists(p): raise SystemExit(f"logo yok: {slug_or_path} (logos.csv'ye bak, AI ile logo ÇİZME)")
    return Image.open(p).convert("RGBA")

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
    def rich(s, x, y, t, highlight, f, maxw, step, maxlines, col=None, hcol=None):
        """Wrapped text; words inside `highlight` substring drawn in ember."""
        col = col or hx(C['text']); hcol = hcol or hx(C['ember'])
        hs = he = -1
        if highlight and highlight in t: hs = t.index(highlight); he = hs+len(highlight)
        words, pos = [], 0
        for m in re.finditer(r"\S+", t): words.append((m.group(), hs <= m.start() < he))
        lines, cur, cw = [], [], 0
        for w, h in words:
            ww = s.tw(w+" ", f)
            if cw+ww-s.tw(" ", f) > maxw and cur: lines.append(cur); cur, cw = [], 0
            cur.append((w, h)); cw += ww
        if cur: lines.append(cur)
        if len(lines) > maxlines: raise SystemExit(f"metin çok uzun ({len(lines)} satır > {maxlines}): {t[:40]}...")
        for i, ln in enumerate(lines):
            xx = x
            for w, h in ln:
                s.text((xx, y+i*step), w, f, hcol if h else col); xx += s.tw(w+" ", f)
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

def bottom(cv, source, date):
    cv.line((M, 804, W-M, 804), hx(C['line']), 2)
    fs = font('body', 22, 500); src = "Kaynak: "+source
    if cv.tw(src, fs) > 520:
        while cv.tw(src+"…", fs) > 520: src = src[:-1]
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
    cv.text((M+tw+24, 186), d.get("company", ""), font('head', 40, 700), hx(C['text']), "lm")
    cv.text((M+tw+24, 228), d.get("meta", ""), font('body', 24, 500), hx(C['muted']), "lm")
    y = cv.rich(M, 330, d["headline"], d.get("highlight"), font('head', 80, 700), 880, 92, 3)
    fs = font('body', 32, 400); sub = cv.wrap(d.get("sub", ""), fs, 780) if d.get("sub") else []
    if len(sub) > 2: raise SystemExit("sub en fazla 2 satır")
    for i, t in enumerate(sub): cv.text((M, y+20+i*46), t, fs, hx("#B4BBC9"))
    cy = y+20+len(sub)*46+36; x = M; fc = font('body', 26, 600)
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
    sub = d.get("subtitle", "") + ("  ·  " if d.get("subtitle") else "") + ("yüksek olan daha iyi" if hib else "düşük olan daha iyi")
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
    cv.text((M, 186), d.get("subtitle", ""), font('body', 28, 400), hx(C['muted']))
    cw, y0, y1 = 690, 250, 784
    mets = d["metrics"][:4]
    for ci, side in enumerate([d["left"], d["right"]]):
        x = M if ci == 0 else W-M-cw
        cv.rrect((x, y0, x+cw, y1), 28, fill=hx(C['surface']), outline=hx(C['line']), width=2)
        any_tile(cv, (x+36, y0+32), 84, side.get("logo"), side["name"], radius=20, wide=False)
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
        ls = cv.wrap(p, fs, lw-28)
        cv.rect((lx, yy+12, lx+10, yy+22), hx(C['ember']))
        for j, t in enumerate(ls[:2]): cv.text((lx+28, yy+j*40), t, fs, hx(C['soft']))
        yy += 40*min(len(ls), 2)+18
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
    cv.text((M+tw+24, 168), d.get("company", ""), font('head', 36, 700), hx(C['text']), "lm")
    cv.text((M+tw+24, 206), d.get("meta", ""), font('body', 24, 500), hx(C['muted']), "lm")
    nf = font('head', 250, 700); num = d["number"]
    while cv.tw(num, nf) > 900: nf = font('head', nf.size/S-10, 700)
    cv.text((M-8, 470), num, nf, hx(C['ember']), "ls")
    y = cv.rich(M, 500, d["label"], None, font('head', 48, 700), 900, 58, 2)
    if d.get("context"):
        for i, t in enumerate(cv.wrap(d["context"], font('body', 28, 400), 900)[:2]):
            cv.text((M, y+24+i*40), t, font('body', 28, 400), hx("#B4BBC9"))
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
    nlines = len(cv.wrap(d["quote"], qf, 1250))
    if nlines > 6: raise SystemExit("alıntı en fazla 6 satır")
    blockh = nlines*68+70+88; y0 = 110+(690-blockh)/2
    cv.text((M-6, y0+130), "“", font('head', 260, 700), hx(C['ember']), "ls")
    y = cv.rich(M+150, y0, d["quote"], d.get("highlight"), qf, 1250, 68, 6)+70
    tw = any_tile(cv, (M+150, y), 88, d.get("logo"), d.get("name", ""), radius=20)
    cv.text((M+150+tw+24, y+28), d["name"], font('head', 36, 700), hx(C['text']), "lm")
    cv.text((M+150+tw+24, y+66), d.get("role", ""), font('body', 24, 500), hx(C['muted']), "lm")
    bottom(cv, d["source"], d["date"]); return cv.save(out, dict(template="T6", data=d))

TEMPLATES = dict(t1=t1, t2=t2, t3=t3, t4=t4, t5=t5, t6=t6)
