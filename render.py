#!/usr/bin/env python3
"""EB SIGNAL render CLI.  python render.py t2 data.json out.png
Writes out.png (1600x900) + out.meta.json (template, version). Requires: pillow, numpy (+ rembg/onnxruntime for T8 auto cutout; falls back to a feathered frame)."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ebstyle
if len(sys.argv) != 4 or sys.argv[1].lower() not in ebstyle.TEMPLATES:
    sys.exit("kullanım: python render.py t1|t2|t3|t4|t5|t6|t8 data.json out.png")
d = json.load(open(sys.argv[2], encoding="utf-8"))
for k in ("source", "date"):
    if not d.get(k): sys.exit(f"'{k}' zorunlu (kaynak satırı görselin içinde olmalı)")
if sys.argv[1].lower() == "t8":
    for k in ("person", "person_name", "headline"):
        if not d.get(k): sys.exit(f"T8 için '{k}' zorunlu (gerçek kişi fotoğrafı: yol veya URL; yüz asla AI ile üretilmez)")
txt = json.dumps(d, ensure_ascii=False)
if "—" in txt: sys.exit("em dash (—) yasak")
p = ebstyle.TEMPLATES[sys.argv[1].lower()](d, sys.argv[3])
print(f"OK {p}  EB SIGNAL v{ebstyle.VERSION} {sys.argv[1].upper()}")
