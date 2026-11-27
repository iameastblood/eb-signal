# EB SIGNAL · @eastblood_tr görsel standardı

X Marabası, Manus ve Orva'nın ortak görsel sistemi. Tüm görseller **1600x900 (16:9)**, aynı palet, aynı font, aynı alt bant.

## Hızlı kullanım
```bash
git clone https://github.com/iameastblood/eb-signal.git   # her koşuda: git pull
pip install -r requirements.txt
python render.py t2 veri.json cikti.png    # cikti.png + cikti.meta.json
```
Şablonlar: `t1` haber · `t2` benchmark · `t3` karşılaştırma · `t4` sızıntı/ekran görüntüsü · `t5` büyük rakam · `t6` alıntı · `t8` gerçek kişi kompoziti.
JSON örnekleri: `examples/t1.json ... t6.json, t8.json`. Kurallar ve karar ağacı: **EB_SIGNAL_SPEC.md**.

## Yeni (v1.1): T8 kişi kompoziti ve logo ekleme
```bash
# T8: gerçek kişi fotoğrafı (yol ya da URL) -> otomatik kesim (rembg) -> konu zemini -> yazı + filigran
python render.py t8 examples/t8.json examples/T8.png
# Eksik logoyu kütüphaneye ekle (şeffaf yapar, kırpar, koyu zemin kontrolü, logos.csv satırı, push)
python add_logo.py --src https://.../logo.png --slug claude-code --name "Claude Code" \
    --tags coding,agent --source https://resmi-site/press --push
```
- T8 sert kuralları: yüz asla AI ile üretilmez/değiştirilmez (yalnız kesme, kırpma, renk, ışık); sahte alıntı yok; kişinin orada olduğu ima edilmez; foto kaynağı kredilenir. Ayrıntı: EB_SIGNAL_SPEC.md bölüm 11.
- Logo kütüphanesi büyür: haberdeki logo yoksa üreten ajan ekler, `git pull --rebase` ile push eder, başkasının logosunu silmez/yeniden adlandırmaz. Ayrıntı: bölüm 10, `add_logo.py --help`.
- T8 kesimi AI matting: `birefnet-portrait` (varsayılan, ~928 MB indirme) > `birefnet-general` (~928 MB) > `isnet-general-use` (~170 MB) > `u2net_human_seg` (~168 MB) > yumuşak çerçeve. Kendi AI aracınla kestiysen JSON'a `"person_cutout": "kesilmis.png"` ver. Ayrıntı: spec bölüm 11.
- Görsel yazısı ile post metni birbirini tamamlar, aynı cümleyi tekrar etmez: spec bölüm 12.
- `examples/amodei_2023.jpg`: Wikimedia Commons, "Dario Amodei in 2023", fotoğraf UK Prime Minister (Flickr), CC BY 2.0. Sadece örnek içindir.

## Değişmez kurallar
- Logo sadece `logos/` klasöründen (logos.csv). Yapay zekâ ile logo **asla** çizilmez.
- Logo kütüphanesi: 143 logo, 94 marka, koyu zemin için `-white` sürümleri. Dizin ve yeni logo ekleme protokolü: **logos/README.md**. Üretim araçları: `tools/`.
- Yapay zekâ sadece arka plan üretir (spec'teki tarif). Yazı, logo, şekil kodla basılır.
- Rakam uydurulmaz. Kaynak satırı görselin içinde. `@eastblood_tr` alt ortada (render.py otomatik basar).
- Em dash (—) yok. Başlık bir bulgu cümlesidir.

Notion: [Görsel Standart · EB SIGNAL](https://app.notion.com/p/425dfcae38b1810b969ccc7675aadb85) (Tasarım İlhamı tablosu orada)

Sürüm: `VERSION` · değişiklikler: `CHANGELOG.md` · ilham arşivi: `ilham/`
Fontlar SIL OFL 1.1 (fonts/OFL-*.txt). Logolar ilgili şirketlerin markasıdır; burada yalnızca haber/yorum amaçlı tutulur.
