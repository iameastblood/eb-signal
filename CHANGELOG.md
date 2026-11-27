# CHANGELOG · EB SIGNAL

Kural: her değişiklik VERSION'ı artırır. MAJOR = şablon yapısı/palet değişimi, MINOR = yeni şablon veya yeni alan, PATCH = ölçü/renk ince ayarı, logo ekleme.
Haftada en fazla 1-2 değişiklik, Doğukan onayından sonra. Her satır: tarih, sürüm, ne değişti, neden (hangi veri).

## 1.2.0 · 2026-11-27
- MINOR: **video standardı ve hattı.** `tools/video/make_video.py` (tek komut: kaynak > Cartesia TR VO > senkron kesim > EN altyazı > müzik > HyperFrames hareket katmanı > final.mp4 + 3 kare), `tools/video/README.md`, `tools/video/examples/dot_v2.json`.
- Yeni: `music/` (5 ElevenLabs enstrümantal parça: tech, finance, mystery, space, neutral; README + index.json). Kural: önce ElevenLabs, hata/kredi/bağlı değil (Orva) ise kütüphane.
- Değişen kural (Doğukan t194u): altyazı kutusuz ve şeffaf (kontur + gölge), ~%11 küçük (46 > 41 px); virgül/nokta duraklamaları `<break>` ile; ses ekranla senkron; giriş/çıkış animasyonları ve hareketli filigran (HyperFrames).
- Spec bölüm 13. Neden: v1 test videosu geri bildirimi.

## 1.1.1 · 2026-11-27
- PATCH: T8 kesimi yapay zekâ matting'e geçti. Zincir birefnet-portrait > birefnet-general > isnet-general-use > u2net_human_seg > yumuşak çerçeve; `person_cutout` ile hazır şeffaf PNG verilebilir; `matting_model` / `EB_MATTING_MODEL` ile model zorlanır.
- T8 entegrasyonu: kenar inceltme, halo temizliği (pymatting), sahneye renk eşitleme, light wrap, yumuşak temas gölgesi, alfayı izleyen ember ışıma, fotoğraf çerçevesinin kestiği kenarların sahneye erimesi. `person_crop_bottom` varsayılanı 0.66 (eller/masa nesneleri kadraj dışı).
- Neden: eski u2net_human_seg saçta açık halo bırakıyordu, kişi sahneye oturmuyordu (Doğukan geri bildirimi).
- Spec bölüm 12: görsel yazısı ile post metni birbirini tamamlar, aynı cümle tekrar edilmez.
- Not: başka bir işçi `music/` ve `tools/video/` ekliyor; sürüm bu değişiklikle uyumlu şekilde PATCH artırıldı.

## 1.1.0 · 2026-11-27
- MINOR: yeni şablon **T8 Kişi kompoziti** (gerçek kişi fotoğrafı + rembg ile otomatik kesim, konu zemini, ember kenar ışıması, EB SIGNAL fontları ve filigran). rembg yoksa yumuşak kenarlı çerçeve yedeği. Sert kurallar: yüz AI ile üretilmez/değiştirilmez, sahte alıntı yok, fiziksel varlık ima edilmez, foto kredisi.
- Yeni `add_logo.py`: URL/dosya -> şeffaf kırpılmış PNG, #0A0C10 kontrast kontrolü, gerekirse `-white` sürüm, logos.csv satırı, `--push`.
- logos.csv'ye `tags` kolonu (ai-lab/coding/agent/tool/chip/cloud/model/...); tools/make_csv.py tags'i korur.
- Logo kütüphanesi büyür kuralı spec'e (bölüm 10) ve Notion'a eklendi. Yeni arka plan `bg/datacenter_01.jpg` (AI üretimi, yüz/yazı yok).
- render.py `t8` kabul eder; `bottom()` kaynak satırı genişliği parametrik (varsayılan değişmedi, T1-T6 çıktıları aynı).
- Neden: Doğukan t193u kuralları (gerçek kişi haberleri, sürekli büyüyen logo kütüphanesi).

## 1.0.0 · 2026-11-27
- İlk sürüm. 6 şablon (T1 haber, T2 benchmark, T3 versus, T4 sızıntı, T5 büyük rakam, T6 alıntı), hepsi 1600x900.
- İmza renk ember #FF5A36, fontlar Space Grotesk / Inter / JetBrains Mono (OFL).
- 24 logo (Wikimedia Commons), logos.csv.
- render.py JSON -> PNG + .meta.json (template, version).
