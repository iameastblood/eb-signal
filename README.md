# EB SIGNAL · @eastblood_tr görsel standardı

X Marabası, Manus ve Orva'nın ortak görsel sistemi. Tüm görseller **1600x900 (16:9)**, aynı palet, aynı font, aynı alt bant.

## Hızlı kullanım
```bash
git clone https://github.com/iameastblood/eb-signal.git   # her koşuda: git pull
pip install -r requirements.txt
python render.py t2 veri.json cikti.png    # cikti.png + cikti.meta.json
```
Şablonlar: `t1` haber · `t2` benchmark · `t3` karşılaştırma · `t4` sızıntı/ekran görüntüsü · `t5` büyük rakam · `t6` alıntı.
JSON örnekleri: `examples/t1.json ... t6.json`. Kurallar ve karar ağacı: **EB_SIGNAL_SPEC.md**.

## Değişmez kurallar
- Logo sadece `logos/` klasöründen (logos.csv). Yapay zekâ ile logo **asla** çizilmez.
- Logo kütüphanesi: 143 logo, 94 marka, koyu zemin için `-white` sürümleri. Dizin ve yeni logo ekleme protokolü: **logos/README.md**. Üretim araçları: `tools/`.
- Yapay zekâ sadece arka plan üretir (spec'teki tarif). Yazı, logo, şekil kodla basılır.
- Rakam uydurulmaz. Kaynak satırı görselin içinde. `@eastblood_tr` alt ortada (render.py otomatik basar).
- Em dash (—) yok. Başlık bir bulgu cümlesidir.

Notion: [Görsel Standart · EB SIGNAL](https://app.notion.com/p/425dfcae38b1810b969ccc7675aadb85) (Tasarım İlhamı tablosu orada)

Sürüm: `VERSION` · değişiklikler: `CHANGELOG.md` · ilham arşivi: `ilham/`
Fontlar SIL OFL 1.1 (fonts/OFL-*.txt). Logolar ilgili şirketlerin markasıdır; burada yalnızca haber/yorum amaçlı tutulur.
