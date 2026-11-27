## tools/video · 2026-11-27 (video hattı 1.3.0)
- Kısaltma okunuşu kuralı: hedef dilin harf adı yazılır (GPT -> Ci Pi Ti). "Ge Pe Te" gibi Türkçe harf adı `preflight` tarafından reddedilir; büyük harfli kısaltma kalırsa uyarı verilir.
- Duraklama ritmi: varsayılan `comma_ms` 220, `period_ms` 750, `speed` 0.94. Ölçülen: nokta sonu ~1,0 sn, virgül arası ~0,35 sn.
- `silences()` artık `-nostdin` ve `stdin=DEVNULL` ile çalışır; terminalde ffmpeg takılması giderildi.
- README'ye "Dil ve okunuş" bölümü eklendi (harf adı tablosu, ASR doğrulama tuzağı, ölçüm komutu).

# CHANGELOG · EB SIGNAL

Kural: her değişiklik VERSION'ı artırır. MAJOR = şablon yapısı/palet değişimi, MINOR = yeni şablon veya yeni alan, PATCH = ölçü/renk ince ayarı, logo ekleme.
Haftada en fazla 1-2 değişiklik, Doğukan onayından sonra. Her satır: tarih, sürüm, ne değişti, neden (hangi veri).

## 1.4.1 · 2026-11-27
- PATCH: duraklama standardı Manus ritmine eşitlendi (Doğukan t200u): virgül `<break 220ms>`, nokta `<break 750ms>`, speed 0.94. Spec 13, README ve örnek job'lar (dot_v2, gamma_slides) güncellendi; araç varsayılanları zaten 220/750/0.94.
- Gamma slayt yedeği yalnız Orva (ve X Marabası); Manus kullanmaz. Haftada en fazla 1-2 slayt videosu, yalnız gerçek video yoksa.

## 1.4.0 · 2026-11-27
- MINOR: **Gamma slayt videosu (yedek)**: `make_video.py` `"mode": "slides"` (Gamma PNG export > HyperFrames slayt katmanı: blur+ölçek+kayma giriş/çıkış, Ken Burns, ember tarama çizgisi; geçişler cümle arası sessizlikte). Yeni alanlar `slides`, `lines[].slide`, `title_card`. Örnek `examples/gamma_slides.json`.
- Değişen kural (Doğukan t196u/t197u): **altyazı tek dil**: küresel konu EN, yalnız Türkiye konusu TR (`sub_lang`, `sub_chunks`; `en_chunks` geriye uyumlu). Altyazıda **1-2 ember vurgu** `*kelime*` / `[[kelime]]` (800 ağırlık, noktalama yapışık), 3. işaret hata.
- Spec 13 + yeni 13.1: Gamma yalnız gerçek video yoksa, günlük alışkanlık değil; Higgsfield/Runway yalnız gerektiğinde (sınırlı kredi).
- Neden: Doğukan t199u (Gamma/Higgsfield/Runway bağlandı), Gamma test videosu.

## 1.3.0 · 2026-11-27
- MINOR: tüm şablonlarda **vurgu standardı** `*kelime*` / `[[kelime]]` (ember + biraz daha kalın, blok başına en fazla 2; T1 sub, T4 maddeler, T5 context, T6/T8 alıntı dahil). `highlight` alanı geriye uyumlu.
- **Logo varsa marka adı yazılmaz** (T1, T2, T3, T5, T8): logonun yanındaki şirket adı / T2 şirket satırı kaldırıldı; T3'te kart adı marka adıyla aynıysa yalnız model satırı. Marka adı sadece logo yokken (harf karosu).
- T8: **fotoğraf kredisi satırı ve `photo_credit` kaldırıldı**; kenar ışıması opaklığı ~yarıya (0.38 -> 0.19) ve daha dar/temiz; alt bantta yalnız kaynak + filigran + tarih; yerleşim yeniden düzenlendi (logo 96, başlık 60px/730, isim bloğu aşağı). Geniş fotoğraflar kafa merkezli omuz kadrajına otomatik kesilir (`person_max_aspect`).
- T8 örnek fotoğraf kuralı: kameraya bakan/önden kare; örnek foto Dario Amodei TechCrunch Disrupt 2023 07 (CC BY 2.0, TechCrunch). Eski profil fotoğrafı kaldırıldı.
- T1-T6 örnekleri yeniden üretildi (logo adı kaldırıldı, vurgu işaretleri).
- Neden: Doğukan t195u geri bildirimi.

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
