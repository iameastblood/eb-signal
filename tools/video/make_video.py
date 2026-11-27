#!/usr/bin/env python3
"""EB SIGNAL video pipeline (v1.4): official clip (or Gamma slide images, mode=slides) + Turkish Cartesia VO + EN subtitles + music + HyperFrames motion layer.

One command:
  python tools/video/make_video.py --job tools/video/examples/dot_v2.json --out /workspace/videotest/out [--vo vo.wav] [--music m.mp3]

Pipeline: source -> VO (Cartesia, or --vo) -> timing from VO silences -> base cut synced to VO
          -> music (ElevenLabs, else repo music/ library) -> HyperFrames overlay render -> mux -> final.mp4 + 3 frames.
Never publishes anything. See tools/video/README.md.
"""
import argparse, json, os, re, shutil, subprocess, sys, time, unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
CARTESIA_VERSION = "2026-08-14"
T0 = time.time()
TIMES = {}


def sh(cmd, **kw):
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise SystemExit(f"komut hata verdi:\n{cmd}\n{r.stderr[-2000:]}")
    return r


def step(name):
    class _S:
        def __enter__(s):
            s.t = time.time(); print(f"[{name}] ...", flush=True)
        def __exit__(s, *a):
            TIMES[name] = round(time.time() - s.t, 1); print(f"[{name}] {TIMES[name]}s", flush=True)
    return _S()


def dur(path):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout)


# ---------------------------------------------------------------- script / TTS text
def build_tts_text(job):
    comma = job.get("comma_ms", 220); period = job.get("period_ms", 750)
    out = []
    for i, ln in enumerate(job["lines"]):
        ch = [c.strip().rstrip(",.") for c in ln["tr_chunks"]]
        s = f', <break time="{comma}ms"/> '.join(ch) + "."
        if i < len(job["lines"]) - 1:
            s += f' <break time="{period}ms"/>'
        out.append(s)
    text = " ".join(out)
    preflight(text, job)
    return text


def preflight(text, job):
    """Notion 'Cartesia TTS (Turkce) Bilinen Sorunlar' kurallari."""
    plain = re.sub(r'<break time="\d+ms"/>', " ", text)
    bad = [m for m in ["—", "–", "…", "...", "[", "]", "(", ")", "%", "&", "@", "http", "Ã", "Ä", "Å", "**"] if m in plain]
    if bad: raise SystemExit(f"TTS metni kural ihlali (Notion Cartesia kurali): {bad}")
    if re.search(r"\d", plain): print("UYARI: TTS metninde rakam var; yil disinda yaziyla yaz (kural 7)")
    # kisaltma okunusu: harf adi hedef dilde yazilir (GPT -> Ci Pi Ti); Turkce harf adi yasak
    if re.search(r"\bge pe te\b", plain, re.I):
        raise SystemExit("kisaltma Turkce harf adiyla yazilmis: GPT -> Ci Pi Ti (README: Dil ve okunus)")
    abbr = sorted(set(re.findall(r"\b[A-Z]{2,}\b", plain)))
    if abbr: print("UYARI: kisaltma harf harf yazilmali (or. GPT -> Ci Pi Ti):", abbr)
    for ln in job["lines"]:
        if len(ln["tr_chunks"]) != len(sub_chunks(ln)):
            raise SystemExit("tr_chunks ve sub_chunks (eski: en_chunks) sayisi esit olmali (altyazi her TR parcayi izler)")
        for t in sub_chunks(ln):
            if em_count(t) > 2: raise SystemExit(f"altyazi parcasinda en fazla 2 vurgu (*kelime*): {t}")
        for t in sub_chunks(ln) + ln["tr_chunks"]:
            if "—" in t or "–" in t or t.lstrip().startswith("@"):
                raise SystemExit(f"yasak karakter/@ ile baslama: {t}")
    if len(plain) > 1000: print("UYARI: >1000 karakter; kural 13: parcala (<=900-1000)")


def cartesia_tts(text, job, out):
    key = os.environ.get("CARTESIA_API_KEY")
    if not key: raise SystemExit("CARTESIA_API_KEY yok. Ya anahtari ortam degiskenine koy ya da --vo ile hazir WAV ver (Cartesia MCP).")
    import requests
    body = {"model_id": job.get("model", "sonic-3.6"), "transcript": text,
            "voice": {"mode": "id", "id": job.get("voice_id", "2bcc6ce6-7c85-40fb-a6cb-26fc8297c6d8")},
            "language": "tr",  # locale GONDERME (400 verir)
            "output_format": {"container": "wav", "encoding": "pcm_s16le", "sample_rate": 44100}}
    sp = job.get("speed", 0.94)
    if sp != 1.0: body["generation_config"] = {"speed": sp}
    for attempt in range(4):
        r = requests.post("https://api.cartesia.ai/tts/bytes", json=body, timeout=180,
                          headers={"X-API-Key": key, "Cartesia-Version": CARTESIA_VERSION, "Content-Type": "application/json"})
        if r.status_code == 200 and len(r.content) > 1000:
            open(out, "wb").write(r.content); return
        if r.status_code in (400, 401, 403, 422): raise SystemExit(f"Cartesia {r.status_code}: {r.text[:300]}")
        if attempt == 0 and body["model_id"] == "sonic-3.6": body["model_id"] = "sonic-3.6-2026-08-27"
        time.sleep(2 ** attempt)
    raise SystemExit("Cartesia 4 denemede basarisiz")


# ---------------------------------------------------------------- timing from VO silences
def silences(wav, noise=-38, d=0.12):
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", wav, "-af", f"silencedetect=noise={noise}dB:d={d}", "-f", "null", "-"],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    en = re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", r)
    return [(s, float(e), float(du)) for s, (e, du) in zip(st, en)]


def vo_timing(wav, job):
    """-> per line: dict(start,end,chunks=[(s,e),...]) in VO-file seconds."""
    total = dur(wav); sil = silences(wav)
    lead = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    tail = sil[-1][0] if sil and sil[-1][1] > total - 0.08 else total
    inner = [s for s in sil if s[0] > lead + 0.05 and s[1] < tail - 0.05]
    lines = job["lines"]; n = len(lines)
    inner_sorted = sorted(inner, key=lambda s: -s[2])
    if len(inner) < sum(len(l["tr_chunks"]) for l in lines) - 1:
        raise SystemExit(f"VO'da yeterli duraklama bulunamadi ({len(inner)}); break etiketleri calismamis olabilir")
    sent = sorted(inner_sorted[:n - 1], key=lambda s: s[0])          # periods = longest pauses
    rest = [s for s in inner if s not in sent]
    bounds = [lead] + [x for s in sent for x in (s[0], s[1])] + [tail]
    out = []
    for i, ln in enumerate(lines):
        a, b = bounds[2 * i], bounds[2 * i + 1]
        k = len(ln["tr_chunks"]) - 1
        inside = sorted([s for s in rest if a <= s[0] and s[1] <= b], key=lambda s: -s[2])[:k]
        if len(inside) < k: raise SystemExit(f"satir {i+1}: virgul duraklamasi eksik")
        inside.sort(key=lambda s: s[0])
        pts = [a] + [x for s in inside for x in (s[0], s[1])] + [b]
        out.append({"start": a, "end": b, "chunks": [(pts[2 * j], pts[2 * j + 1]) for j in range(k + 1)]})
    return out, total


# ---------------------------------------------------------------- music
def pick_music(job, args, outdir):
    if args.music: return args.music, "file"
    genre = job.get("genre", "tech")
    key = os.environ.get("ELEVENLABS_API_KEY")
    prompt = job.get("music_prompt") or json.load(open(os.path.join(ROOT, "music", "index.json")))["genres"][genre]["prompt"]
    if key and not args.no_elevenlabs:
        try:
            import requests
            r = requests.post("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128", timeout=300,
                              headers={"xi-api-key": key},
                              json={"prompt": prompt, "music_length_ms": 60000, "model_id": "music_v2", "force_instrumental": True})
            if r.status_code == 200 and len(r.content) > 20000:
                p = os.path.join(outdir, "music_elevenlabs.mp3"); open(p, "wb").write(r.content); return p, "elevenlabs"
            print("ElevenLabs basarisiz:", r.status_code, r.text[:200])
        except Exception as e:
            print("ElevenLabs hata:", e)
    idx = json.load(open(os.path.join(ROOT, "music", "index.json")))["genres"]
    f = os.path.join(ROOT, "music", idx.get(genre, idx["neutral"])["file"])
    return f, "repo-library"


# ---------------------------------------------------------------- HyperFrames project
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def sub_chunks(ln):
    """Altyazi metni: tek dil (sub_lang: en kuresel konu, tr sadece Turkiye konusu). Eski alan en_chunks da kabul edilir."""
    return ln.get("sub_chunks") or ln["en_chunks"]


EM_RE = re.compile(r"\*([^*]+)\*|\[\[(.+?)\]\]")


def em_count(t): return len(EM_RE.findall(t))


def words_html(text):
    """*kelime* / [[kelime]] -> ember + biraz kalin (EB SIGNAL vurgu standardi), isaretler ciktida gorunmez.
    Noktalama kelimeye yapisik kalir ("*Rust*," -> Rust + beyaz virgul, arada bosluk yok)."""
    out = []
    for ln in text.split("\n"):
        chars = []; pos = 0
        for m in EM_RE.finditer(ln):
            chars += [(c, False) for c in ln[pos:m.start()]]
            chars += [(c, True) for c in (m.group(1) or m.group(2))]
            pos = m.end()
        chars += [(c, False) for c in ln[pos:]]
        words = []; cur = []
        for c, e in chars + [(" ", False)]:
            if c.isspace():
                if cur: words.append(cur); cur = []
            else: cur.append((c, e))
        spans = []
        for w in words:
            runs = []
            for c, e in w:
                if runs and runs[-1][1] == e: runs[-1][0] += c
                else: runs.append([c, e])
            inner = "".join(f'<span class="em">{esc(t)}</span>' if e else esc(t) for t, e in runs)
            spans.append(f'<span class="w">{inner}</span> ')
        out.append('<span class="ln">' + "".join(spans) + "</span>")
    return "".join(out)


FONT_CSS = """@font-face{font-family:'EBInter';src:url('assets/fonts/Inter.ttf');font-weight:100 900;}
@font-face{font-family:'EBGrotesk';src:url('assets/fonts/SpaceGrotesk.ttf');font-weight:300 700;}
@font-face{font-family:'EBMono';src:url('assets/fonts/JetBrainsMono.ttf');font-weight:100 800;}"""


def slides_layer(slide_segs, T):
    """Gamma slide modu: her slayt bir clip; giris blur+olcek+kayma, icte yavas Ken Burns, cikista blur; gecislerde ember tarama cizgisi."""
    X = 0.38  # gecis yarim suresi (cumle arasi sessizligin ortasinda)
    html = []; js = []
    for k, (a, b, src) in enumerate(slide_segs):
        st = 0.0 if k == 0 else max(0.0, a - X); en = T if k == len(slide_segs) - 1 else min(T, b + X)
        dz = (1.0, 1.045) if k % 2 == 0 else (1.045, 1.0)
        px = (-14, 14) if k % 2 == 0 else (14, -14)
        html.append(f'<div id="s{k}" class="sl clip" data-start="{st:.3f}" data-duration="{en-st:.3f}" data-track-index="{k % 2}"><img id="s{k}i" class="sli" src="{src}"/></div>')
        js.append(f'tl.fromTo("#s{k}i",{{scale:{dz[0]},x:{px[0]}}},{{scale:{dz[1]},x:{px[1]},duration:{en-st:.3f},ease:"none"}},{st:.3f});')
        if k == 0:
            js.append(f'tl.fromTo("#s{k}",{{opacity:0,scale:1.06,filter:"blur(16px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:0.9,ease:"expo.out"}},0.0);')
        else:
            js.append(f'tl.fromTo("#s{k}",{{opacity:0,scale:1.05,x:60,filter:"blur(14px)"}},{{opacity:1,scale:1,x:0,filter:"blur(0px)",duration:{2*X:.3f},ease:"power3.out"}},{st:.3f});')
            js.append(f'tl.fromTo("#sweep",{{x:-80,opacity:0.0}},{{x:2000,opacity:0.0,duration:0.7,ease:"power2.inOut",keyframes:{{opacity:[0,0.9,0.9,0]}}}},{st:.3f});')
        if k < len(slide_segs) - 1:
            js.append(f'tl.to("#s{k}",{{opacity:0,scale:0.97,x:-50,filter:"blur(10px)",duration:{2*X:.3f},ease:"power2.in"}},{b-X:.3f});')
        else:
            js.append(f'tl.to("#s{k}",{{opacity:0,filter:"blur(8px)",duration:0.6,ease:"power2.in"}},{T-0.65:.3f});')
    css = ("#slides{position:absolute;inset:0;overflow:hidden;background:#0A0C10}.sl{position:absolute;inset:0;overflow:hidden}"
           ".sli{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}"
           "#sweep{position:absolute;top:0;left:0;width:6px;height:1080px;background:linear-gradient(180deg,transparent,#FF5A36 30%,#FF5A36 70%,transparent);"
           "box-shadow:0 0 28px rgba(255,90,54,.7);opacity:0}")
    return css, "".join(html) + '<div id="sweep"></div>', "\n".join(js)


def write_hf(hf, total, cues, job, args, logo_name, slide_segs=None):
    for d in ("compositions", "assets/fonts"): os.makedirs(os.path.join(hf, d), exist_ok=True)
    for src, dst in (("Inter-VariableFont_opsz-wght.ttf", "Inter.ttf"), ("SpaceGrotesk-VariableFont_wght.ttf", "SpaceGrotesk.ttf"),
                     ("JetBrainsMono-VariableFont_wght.ttf", "JetBrainsMono.ttf")):
        shutil.copy(os.path.join(ROOT, "fonts", src), os.path.join(hf, "assets/fonts", dst))
    T = f"{total:.3f}"; title_dur = min(8.6, total - 0.5)
    show_title = job.get("title_card", True)
    if slide_segs:
        s_css, s_html, s_js = slides_layer(slide_segs, total)
        base_el = f'<div id="slides" data-start="0" data-duration="{T}">{s_html}</div>'
    else:
        s_css, s_js = "", ""
        base_el = f'<video id="base" class="clip" data-start="0" data-duration="{T}" data-track-index="0" src="assets/base.mp4" muted playsinline></video>'
    title_el = (f'<div id="title" class="host clip" data-composition-id="title" data-composition-src="compositions/title.html" data-start="0" data-duration="{title_dur:.3f}" data-track-index="2" data-track-kind="graphics" data-width="1920" data-height="1080"></div>'
                if show_title else "")
    index = f"""<!doctype html>
<html lang="tr"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>{FONT_CSS}
*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#0A0C10}}
#base{{position:absolute;left:0;top:0;width:1920px;height:1080px;object-fit:cover}}
.host{{position:absolute;left:0;top:0;width:1920px;height:1080px}}{s_css}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-width="1920" data-height="1080">
  {base_el}
  {title_el}
  <div id="subs" class="host clip" data-composition-id="subs" data-composition-src="compositions/subs.html" data-start="0" data-duration="{T}" data-track-index="3" data-track-kind="captions" data-width="1920" data-height="1080"></div>
  <div id="mark" class="host clip" data-composition-id="mark" data-composition-src="compositions/mark.html" data-start="0" data-duration="{T}" data-track-index="4" data-track-kind="graphics" data-width="1920" data-height="1080"></div>
</div>
<script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});
{s_js}
window.__timelines["main"]=tl;tl.seek(0);</script>
</body></html>"""
    open(os.path.join(hf, "index.html"), "w").write(index)

    tag = esc(job.get("tag", "RESMİ VİDEO · AI HABER")); title = esc(job["title"])
    tw = "".join(f'<span class="tw">{esc(w)}</span> ' for w in job["title"].split())
    t_in = 0.5; t_out = title_dur - 0.55
    open(os.path.join(hf, "compositions/title.html"), "w").write(f"""<template>
<style>{FONT_CSS}
#root{{position:absolute;inset:0}}
#t-card{{position:absolute;left:64px;top:52px;display:flex;align-items:center;gap:26px;padding:20px 40px 20px 34px;border-radius:16px;background:rgba(10,12,16,.80);overflow:hidden;filter:drop-shadow(0 8px 24px rgba(0,0,0,.45))}}
#t-bar{{position:absolute;left:0;top:0;width:9px;height:100%;background:#FF5A36;transform-origin:50% 0}}
#t-logo{{height:68px;width:auto;display:block}}
#t-tag{{font:600 21px 'EBMono',monospace;letter-spacing:.14em;color:#FF5A36;margin-bottom:6px;white-space:nowrap}}
#t-title{{font:700 42px/1.12 'EBGrotesk',sans-serif;color:#F5F6F8;white-space:nowrap}}
.tw{{display:inline-block}}
</style>
<div id="root" data-composition-id="title" data-width="1920" data-height="1080">
 <div id="t-card"><div id="t-bar"></div><img id="t-logo" src="assets/{logo_name}"/><div><div id="t-tag">{tag}</div><div id="t-title">{tw}</div></div></div>
</div>
<script>
const tl=gsap.timeline({{paused:true}});
tl.fromTo("#t-card",{{clipPath:"inset(0 100% 0 0 round 16px)",x:-30,opacity:1}},{{clipPath:"inset(0 0% 0 0 round 16px)",x:0,duration:0.75,ease:"expo.out"}},{t_in});
tl.fromTo("#t-bar",{{scaleY:0}},{{scaleY:1,duration:0.55,ease:"power4.out"}},{t_in+0.1});
tl.fromTo("#t-logo",{{scale:0.55,opacity:0,filter:"blur(10px)"}},{{scale:1,opacity:1,filter:"blur(0px)",duration:0.8,ease:"back.out(1.5)"}},{t_in+0.2});
tl.fromTo("#t-tag",{{opacity:0,x:18}},{{opacity:1,x:0,duration:0.55,ease:"expo.out"}},{t_in+0.4});
tl.fromTo(".tw",{{opacity:0,y:14,filter:"blur(8px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.45,ease:"power3.out",stagger:0.07}},{t_in+0.5});
tl.to("#t-logo",{{scale:0.8,opacity:0,filter:"blur(6px)",duration:0.3,ease:"power3.in"}},{t_out});
tl.to(".tw",{{opacity:0,y:-6,filter:"blur(6px)",duration:0.2,ease:"power2.in",stagger:0.025}},{t_out});
tl.to("#t-card",{{x:-70,opacity:0,filter:"blur(8px)",duration:0.38,ease:"power3.in"}},{t_out+0.12});
tl.set("#t-card",{{opacity:0,visibility:"hidden"}},{title_dur-0.02:.3f});
window.__timelines["title"]=tl;
</script></template>""")

    cue_html = []; cue_js = []
    for i, c in enumerate(cues):
        d = c["e"] - c["s"]
        cue_html.append(f'<div id="c{i}" class="cue clip" data-start="{c["s"]:.3f}" data-duration="{d:.3f}" data-track-index="0"><div class="txt" id="c{i}t">{words_html(c["en"])}</div></div>')
        cue_js.append(f"""tl.fromTo("#c{i}t .w",{{opacity:0,y:16,filter:"blur(6px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.38,ease:"expo.out",stagger:0.05}},{c["s"]:.3f});
tl.to("#c{i}t",{{opacity:0,y:-10,filter:"blur(6px)",duration:0.2,ease:"power2.in"}},{c["e"]-0.2:.3f});
""")
    fs = job.get("sub_font_px", 41)
    scrim = "" if not job.get("scrim") else '<div id="scrim"></div>'
    open(os.path.join(hf, "compositions/subs.html"), "w").write(f"""<template>
<style>{FONT_CSS}
#root{{position:absolute;inset:0}}
.cue{{position:absolute;left:0;width:1920px;bottom:104px;text-align:center}}
.txt{{font:700 {fs}px/1.24 'EBInter',sans-serif;color:#F5F6F8;
 -webkit-text-stroke:4px rgba(10,12,16,.92);paint-order:stroke fill;
 text-shadow:0 2px 10px rgba(0,0,0,.65),0 0 3px rgba(0,0,0,.5);letter-spacing:.012em;word-spacing:.1em}}
.ln{{display:block}}.w{{display:inline-block}}.em{{color:#FF5A36;font-weight:800}}
</style>
<div id="root" data-composition-id="subs" data-width="1920" data-height="1080">{scrim}{''.join(cue_html)}</div>
<script>
const tl=gsap.timeline({{paused:true}});
{chr(10).join(cue_js)}
window.__timelines["subs"]=tl;
</script></template>""")

    sweeps = []; t = 5.0
    while t < total - 3: sweeps.append(t); t += 9.0
    sw = "\n".join(f'tl.fromTo("#m-shine",{{backgroundPosition:"110% 0"}},{{backgroundPosition:"-10% 0",duration:1.3,ease:"power1.inOut"}},{x:.2f});' for x in sweeps)
    reps = max(1, int((total - 1.5) / 1.8))
    open(os.path.join(hf, "compositions/mark.html"), "w").write(f"""<template>
<style>{FONT_CSS}
#root{{position:absolute;inset:0}}
#m-wrap{{position:absolute;left:0;width:1920px;bottom:34px;display:flex;justify-content:center;filter:drop-shadow(0 2px 6px rgba(0,0,0,.7))}}
#m-box{{position:relative;display:flex;align-items:center;gap:14px;opacity:0}}
#m-dot{{width:11px;height:11px;border-radius:50%;background:#FF5A36;box-shadow:0 0 12px rgba(255,90,54,.8)}}
.mt{{font:600 31px 'EBGrotesk',sans-serif;letter-spacing:.045em;white-space:nowrap}}
#m-base{{color:#F5F6F8;-webkit-text-stroke:3.5px rgba(10,12,16,.9);paint-order:stroke fill}}
#m-shine{{position:absolute;left:25px;top:0;color:transparent;background:linear-gradient(100deg,transparent 38%,rgba(255,150,120,.95) 50%,transparent 62%);background-size:300% 100%;background-position:110% 0;-webkit-background-clip:text;background-clip:text}}
#m-line{{position:absolute;left:25px;right:0;bottom:-9px;height:2px;background:#FF5A36;transform-origin:50% 50%;transform:scaleX(0);border-radius:2px}}
</style>
<div id="root" data-composition-id="mark" data-width="1920" data-height="1080">
 <div id="m-wrap"><div id="m-box"><div id="m-dot"></div><div class="mt" id="m-base">@eastblood_tr</div><div class="mt" id="m-shine" data-layout-allow-overlap data-layout-allow-occlusion>@eastblood_tr</div><div id="m-line"></div></div></div>
</div>
<script>
const tl=gsap.timeline({{paused:true}});
tl.set("#m-shine",{{backgroundPosition:"110% 0"}},0);
tl.fromTo("#m-box",{{opacity:0,y:22,filter:"blur(8px)"}},{{opacity:0.94,y:0,filter:"blur(0px)",duration:0.95,ease:"expo.out"}},0.9);
tl.fromTo("#m-line",{{scaleX:0}},{{scaleX:1,duration:0.8,ease:"power3.out"}},1.25);
tl.to("#m-line",{{opacity:0.45,duration:0.6,ease:"power2.out"}},2.2);
tl.fromTo("#m-dot",{{scale:1,opacity:1}},{{scale:1.3,opacity:0.7,duration:0.9,ease:"sine.inOut",yoyo:true,repeat:{reps}}},1.8);
{sw}
tl.to("#m-box",{{opacity:0,y:8,filter:"blur(6px)",duration:0.5,ease:"power2.in"}},{total-0.6:.3f});
tl.set("#m-box",{{opacity:0,visibility:"hidden"}},{total-0.02:.3f});
window.__timelines["mark"]=tl;
</script></template>""")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--vo"); ap.add_argument("--music"); ap.add_argument("--no-elevenlabs", action="store_true")
    ap.add_argument("--source"); ap.add_argument("--qa", action="store_true", help="faster-whisper ile VO geri dinleme")
    ap.add_argument("--hf-cmd", default=os.environ.get("HF_CMD", "npx --yes hyperframes@0.9.99"))
    ap.add_argument("--quality", default="delivery"); ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()
    job = json.load(open(args.job)); out = os.path.abspath(args.out); os.makedirs(out, exist_ok=True)
    slides = job.get("mode") == "slides"
    jdir = os.path.dirname(os.path.abspath(args.job))

    with step("1_source"):
      if slides:
        sl = [p if os.path.isabs(p) else os.path.join(jdir, p) for p in job["slides"]]
        miss = [p for p in sl if not os.path.exists(p)]
        if miss: raise SystemExit(f"slayt bulunamadi: {miss}")
        src = None; src_dur = 0.0
      else:
        src = args.source or job["source"]
        if re.match(r"https?://", src):
            p = os.path.join(out, "src.mp4")
            if not os.path.exists(p):
                ytd = shutil.which("yt-dlp") or [sys.executable, "-m", "yt_dlp"]
                cmd = (ytd if isinstance(ytd, list) else [ytd]) + ["-f", "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b", "--merge-output-format", "mp4", "-o", p, src]
                sh(cmd)
            src = p
        src_dur = dur(src)

    tts_text = build_tts_text(job); open(os.path.join(out, "tts.txt"), "w").write(tts_text)
    vo_raw = os.path.join(out, "vo_raw.wav")
    with step("2_vo"):
        if args.vo: shutil.copy(args.vo, vo_raw)
        else: cartesia_tts(tts_text, job, vo_raw)

    with step("3_timing"):
        timing, vo_total = vo_timing(vo_raw, job)
        if args.qa:
            import numpy as np
            from faster_whisper import WhisperModel
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", vo_raw, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout
            segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(np.frombuffer(raw, dtype=np.float32), language="tr")
            open(os.path.join(out, "vo_asr.txt"), "w").write("\n".join(f"{s.start:.2f}-{s.end:.2f} {s.text}" for s in segs))
        lead = job.get("lead", 0.5); tail = job.get("tail", 1.2)
        n = len(timing)
        seg_t = [0.0] + [lead + (timing[i - 1]["end"] + timing[i]["start"]) / 2 for i in range(1, n)]
        total = lead + timing[-1]["end"] + tail
        seg_t.append(total)
        cues = []
        for i, (tm, ln) in enumerate(zip(timing, job["lines"])):
            for j, (a, b) in enumerate(tm["chunks"]):
                cues.append({"s": lead + a - 0.06, "e": lead + b + 0.28, "en": sub_chunks(ln)[j], "line": i})
        for k in range(len(cues) - 1):
            cues[k]["e"] = min(cues[k]["e"], cues[k + 1]["s"] - 0.03)
        for c in cues: c["e"] = max(c["e"], c["s"] + 0.8)
        cues[-1]["e"] = min(cues[-1]["e"], total - 0.5)
        json.dump({"segments": seg_t, "cues": cues, "total": total, "vo": timing}, open(os.path.join(out, "timing.json"), "w"), indent=1, ensure_ascii=False)

    with step("4_base_cut"):
      slide_segs = None
      if slides:
        slide_segs = []
        for i, ln in enumerate(job["lines"]):
            k = ln.get("slide", i)
            if slide_segs and slide_segs[-1][3] == k: slide_segs[-1][1] = seg_t[i + 1]
            else: slide_segs.append([seg_t[i], seg_t[i + 1], f"assets/slide{k}.png", k])
        slide_segs = [tuple(x[:3]) for x in slide_segs]
        base = None
      else:
        parts = []; prev_end = 0.0; fc = []
        for i, ln in enumerate(job["lines"]):
            L = seg_t[i + 1] - seg_t[i]
            s = max(ln.get("src_start", prev_end), prev_end) if job.get("monotonic", True) else ln.get("src_start", prev_end)
            e = s + L
            pad = max(0.0, e - src_dur)
            fc.append(f"[0:v]trim=start={s:.3f}:end={min(e, src_dur):.3f},setpts=PTS-STARTPTS,fps=30,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1"
                      + (f",tpad=stop_mode=clone:stop_duration={pad:.3f}" if pad > 0 else "") + f"[v{i}]")
            prev_end = min(e, src_dur)
        n_ = len(job["lines"])
        fc.append("".join(f"[v{i}]" for i in range(n_)) + f"concat=n={n_}:v=1:a=0[outv]")
        base = os.path.join(out, "base.mp4")
        sh(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", ";".join(fc), "-map", "[outv]", "-t", f"{total:.3f}", "-an",
            "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-g", "15", "-pix_fmt", "yuv420p", "-r", "30", base])

    with step("5_audio"):
        mus, mus_src = pick_music(job, args, out)
        m = sh(["ffmpeg", "-hide_banner", "-i", vo_raw, "-af", "aresample=48000,loudnorm=I=-16:TP=-2.2:LRA=11:print_format=json", "-f", "null", "-"]).stderr
        j = json.loads(m[m.rindex("{"):m.rindex("}") + 1]); ms = int(lead * 1000)
        sh(["ffmpeg", "-v", "error", "-y", "-i", vo_raw, "-af",
            f"aresample=48000,pan=stereo|c0=c0|c1=c0,loudnorm=I=-16:TP=-2.2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,alimiter=limit=0.776:level=disabled:attack=5:release=50,adelay={ms}|{ms},apad=whole_dur={total:.3f}",
            "-t", f"{total:.3f}", "-c:a", "pcm_s16le", os.path.join(out, "vo48.wav")])
        sh(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", mus, "-t", f"{total:.3f}", "-af",
            f"aresample=48000,pan=stereo|c0=c0|c1=c1,loudnorm=I=-36:TP=-9:LRA=7,afade=t=in:d=1.5,afade=t=out:st={total-3:.3f}:d=3", "-c:a", "pcm_s16le", os.path.join(out, "mus48.wav")])
        sh(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(out, "vo48.wav"), "-i", os.path.join(out, "mus48.wav"), "-filter_complex",
            "[0][1]amix=inputs=2:duration=first:normalize=0[a]", "-map", "[a]", "-c:a", "pcm_s16le", os.path.join(out, "mix.wav")])

    with step("6_hyperframes"):
        hf = os.path.join(out, "hf"); shutil.rmtree(hf, ignore_errors=True); os.makedirs(os.path.join(hf, "assets"))
        if slides:
            for k, pth in enumerate(sl):
                sh(["ffmpeg", "-v", "error", "-y", "-i", pth, "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080", os.path.join(hf, f"assets/slide{k}.png")])
        else:
            shutil.copy(base, os.path.join(hf, "assets/base.mp4"))
        slug = job.get("logo", "")
        cand = [os.path.join(ROOT, "logos", f"{slug}-white.png"), os.path.join(ROOT, "logos", f"{slug}.png")]
        if slug.endswith("-white"): cand = cand[::-1] if False else [os.path.join(ROOT, "logos", f"{slug}.png")]
        lp = next((c for c in cand if os.path.exists(c)), None)
        if not lp: raise SystemExit(f"logo yok: {slug} (logos.csv'ye bak; AI ile logo CIZME, add_logo.py ile ekle)")
        shutil.copy(lp, os.path.join(hf, "assets/logo.png"))
        write_hf(hf, total, cues, job, args, "logo.png", slide_segs)
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json"}, open(os.path.join(hf, "hyperframes.json"), "w")) if not os.path.exists(os.path.join(hf, "hyperframes.json")) else None
        if args.no_render: return
        hfo = os.path.join(out, "hf_overlay.mp4")
        sh(f'cd "{hf}" && {args.hf_cmd} check', cwd=hf) if os.environ.get("HF_CHECK") else None
        sh(f'cd "{hf}" && {args.hf_cmd} render --quality {args.quality} -o "{hfo}"', cwd=hf)

    with step("7_mux_frames"):
        final = os.path.join(out, "final.mp4")
        sh(["ffmpeg", "-v", "error", "-y", "-i", hfo, "-i", os.path.join(out, "mix.wav"), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264",
            "-preset", "medium", "-crf", "19", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-movflags", "+faststart", "-t", f"{total:.3f}", final])
        for k, t in enumerate((job.get("frames") or [2.6, (cues[len(cues) // 2]["s"] + cues[len(cues) // 2]["e"]) / 2, (cues[-3]["s"] + cues[-3]["e"]) / 2 + 0.2]), 1):
            sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", final, "-frames:v", "1", os.path.join(out, f"frame{k}.png")])
    rep = {"final": final, "duration": dur(final), "total_s": round(time.time() - T0, 1), "step_seconds": TIMES, "music_source": mus_src, "mode": job.get("mode", "clip"),
           "audio": {"tts_chars": len(tts_text)}}
    json.dump(rep, open(os.path.join(out, "report.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
