# EB SIGNAL · Spec v1.3 (VERSION 1.3.0)
@eastblood_tr ortak görsel standardı. X Marabası, Manus, Orva görsel üretmeden önce bunu okur.
Referans kod: `ebstyle.py` + `render.py`. Ölçüler mantıksal piksel (render 2x yapılıp küçültülür).

## 1. Değişmez kurallar
1. Boyut her zaman **1600x900 (16:9)**. Başka oran yok.
2. Şirket/lab/ürün varsa **gerçek logo** `logos/` klasöründen gelir (logos.csv). Logo yapay zekâ ile ASLA çizilmez, yeniden boyanmaz. Logo yoksa: **logoyu sen ekle** (bkz. 10. Logo kütüphanesi büyür); ekleyemezsen harf karosu + şirket adı (yalnız logo yoksa) ve Güncelleme Protokolü'ne not düş.
3. Yapay zekâ sadece **arka plan** üretir (bkz. 6). Yazı, logo, şekil, filigran kodla (render.py) basılır.
4. **Rakam uydurulmaz.** Her rakam resmi kaynaktan. Resmi veri yoksa grafik (T2/T3/T5) yapılmaz.
5. **Kaynak satırı görselin içinde** (sol alt "Kaynak: ..."). render.py `source` ve `date` olmadan çalışmaz.
6. `@eastblood_tr` pill'i alt ortada, render.py otomatik basar. Elle değiştirme.
7. Tek ember vurgu: görselde ember sadece kazanan değer / anahtar ifade / imza çubuğu. Gerisi nötr.
8. Türkçe metin: **em dash (—) yok** (render.py reddeder), "kanka" yok, başlık bir **bulgu cümlesi** (fiil içerir: "X, Y'de önde", "Fiyat yarıya indi"). Soru başlığı yok.
9. Örnek/sahte veri sadece `"example": true` ile, sarı ÖRNEK damgası çıkar. Damgalı görsel yayınlanmaz.

## 2. Palet
bg #0A0C10 · surface #12151C · surface2 #181C25 · line #262B36 · text #F5F6F8 · soft #C3C9D6 · muted #98A0B0 · bar #39414F
ember #FF5A36 (imza, kazanan) · ice #5CC8FF (ikinci seri, nadiren) · green #38D996 (pozitif değişim) · amber #FFB224 (ÖRNEK / DOĞRULANMADI)

## 3. Tipografi (fonts/, SIL OFL)
Başlık Space Grotesk 700 (T1 80px, diğerleri 60px) · Gövde Inter 400-600 (24-32px) · Etiket JetBrains Mono 700 BÜYÜK HARF 20-22px.
Okunacak hiçbir metin 22px altında olmaz.

## 4. Ortak çerçeve
- Kenar boşluğu 72px. Üst: ember çubuk 56x6 @ (72,60) + mono etiket x=144 y=63. Sağ üst opsiyonel damga.
- Alt bant: çizgi y=804; sol kaynak (Inter 22, max 520px, taşarsa …); orta `@eastblood_tr` pill (h52, y 826-878); sağ tarih ("27 Kas 2026").
- **Logo varsa marka adı yazılmaz** (T1-T8): logo ile aynı marka adını yanına bir daha basma. Wordmark logo adı zaten içerir; yalnız sembol olan logoda da ad yazılmaz. Marka adı sadece logo yokken (harf karosu) basılır. T2'de satırın model adı kalır, altına şirket satırı konmaz; T3'te kart adı marka adıyla aynıysa yalnız model/alt satır yazılır (kart adı = model/ürün adı olmalı). `meta` satırı (ör. "Resmi duyuru · 27 Kas") logonun yanında kalabilir.
- Logo karosu: açık #F5F6F8 yuvarlak kare (radius %24), orijinal renkli logo %18-20 iç boşlukla. Wordmark (en/boy > 1.6) T1/T5/T6'da 2.4x geniş karo; T2/T3'te sembol logosu kullan.

## 5. Şablonlar ve JSON alanları (örnekler: examples/t*.json)
| ID | Ne zaman | Yerleşim | Zorunlu JSON |
|---|---|---|---|
| T1 Haber | Şirket duyurusu, ürün, olay | AI arka plan + sol koyu gradyan; logo 112 @(72,150); başlık 80px y=330 max 3 satır/880px, *vurgu* ember; alt metin 32px max 2 satır; max 3 çip | logo, company, headline, source, date (+meta, highlight, sub, chips, bg) |
| T2 Benchmark | Resmi skor, 3-6 model | Başlık 60px max 2 satır/1150px; alt başlık y=274 + "yüksek/düşük olan daha iyi" otomatik; satır y=340, adım 86; bar x 470-1380; sıralı; kazanan ember | title, rows[{name,company,logo,value}], higher_is_better, source, date (+subtitle, max, unit, format) |
| T3 Versus | 2 ürün, eşleşen metrikler | 2 kart 690x534 (x72 / x838, y250-784); logo 84; max 4 metrik, adım 88; kazanan ember + ▲ (yüksek iyi) / ▼ (düşük iyi); VS rozeti | title, left/right{logo,name,sub}, metrics[{label,values,display,better}], source, date |
| T4 Sızıntı | X'ten sızıntı, iddia, ekran görüntüsü | Sol 600px: durum rozeti (DOĞRULANMADI/DOĞRULANDI), başlık 60px max 4 satır, max 3 madde; sağ: pencere çerçevesi x720-1528, ekran görüntüsü sığdırılır, `highlight_box` ember çerçeve | title, screenshot, handle, status, source, date (+points, highlight_box) |
| T5 Büyük rakam | Tek rakam haberi taşıyor | Logo 88 @(72,140); rakam 250px ember (taşarsa küçülür); etiket 48px; bağlam 28px; sağda max 3 karşılaştırma kartı | number, label, logo, company, source, date (+context, compare, bg) |
| T6 Alıntı | Kişi/kurum sözü | Ember tırnak 260px; alıntı 54px max 6 satır/1250px dikey ortalı; altında logo/avatar + ad + unvan. Kaynak URL post metninin sonunda | quote, name, source, date (+role, logo, highlight, bg) |
| T8 Kişi kompoziti | Haber gerçek bir kişiyle ilgili (açıklama, röportaj, duyuru) | Sağda kişi kesiti (~%45 genişlik, ince ve düşük opaklıklı ember kenar ışıması, alt kısım sahneye erir); koyuya çekilmiş konu zemini (`bg`); solda logo karosu 96 (yanında marka adı YOK), başlık 60px max 4 satır/730px, opsiyonel alıntı (ember çubuk, max 4 satır) ve sub (max 3 satır), altta kişi adı + unvan; alt bantta yalnız kaynak satırı + filigran + tarih (fotoğraf kredisi satırı YOK) | person (yol/URL) ya da person_cutout, person_name, headline, source, date (+bg, quote, sub, role, logo, company, person_crop_bottom, person_max_aspect, matting_model) |

**T3 metrik yönü (better):** higher = yüksek iyi (puan, bağlam, hız token/sn, doğruluk) · lower = düşük iyi (fiyat, gecikme, hata oranı, bellek, maliyet) · none = karşılaştırma yok. Etikete otomatik "(düşük iyi)" eklenir.

## 6. Karar ağacı
1. Resmi sayısal benchmark + 3 veya daha fazla model -> **T2**
2. İki ürün/model yan yana, eşleşen metrikler -> **T3**
3. Tek rakam haberin kendisi (fiyat, kullanıcı, %, gelir) -> **T5**
4. X sızıntısı, iddia, ekran görüntüsü -> **T4** (doğrulanmadıysa status "Doğrulanmadı")
5. Kişi/kurum alıntısı -> **T6**; haber gerçek bir kişinin kendisiyle ilgiliyse (kişi fotoğrafı değer katıyorsa) -> **T8**
6. Diğer şirket/ürün haberi -> **T1**
7. Şirket yok, rakam yok -> görselsiz metin postu. Görsel şartsa T1 (logo alanında konunun baş harfiyle harf karosu, otomatik).
Video kapakları da T1 düzeninde.

## 7. Yapay zekâ arka plan tarifi (tutarlılık için sabit)
Önce `bg/` içindeki hazır arka planları kullan. Yeni arka plan gerekiyorsa bu prompt aynen kullanılır, sadece [KONU] değişir:
> Abstract dark cinematic background, deep near-black navy base (#0A0C10), soft ember-orange and crimson light bloom from the lower right corner, faint thin grid lines, a few translucent glass geometric shapes, subtle hint of [KONU: ör. chips / servers / neural network] as abstract forms, shallow depth of field, premium editorial tech look. Left 60% of frame empty and dark. Absolutely no text, letters, numbers, logos, faces or people. 16:9.
Kontrol: arka planda yazı/logo/yüz çıktıysa at, yeniden üret. Yeni iyi arka planlar `bg/` klasörüne `ember_NN.jpg` olarak eklenir (PATCH sürüm).

## 8. Çıktı ve kayıt
render.py `cikti.png` + `cikti.meta.json` (template, version) yazar. Görsele sürüm basılmaz.
İçerik Takvimi'nde her post için **Şablon** (T1-T6 / Yok) ve **Stil Sürümü** (ör. 1.0.0) doldurulur.

## 9. Geliştirme döngüsü (haftalık)
1. Son 7 günün postları şablon ve sürüme göre gruplanır; 1.000 gösterim başına beğeni, yer işareti, repost karşılaştırılır (gösterim, beğeni, yer işareti, repost ham sayıları da yazılır).
2. En iyi 3 ve en kötü 3 görsel incelenir: ne farklıydı?
3. Güçlü hesaplardan 3-5 yeni referans tasarım `ilham/` + Notion "Tasarım İlhamı" tablosuna eklenir.
4. En fazla 1-2 değişiklik önerilir. **A/B kuralı: aynı anda tek değişken** (ör. sadece başlık boyutu). Az veriyle (<5 post/şablon) karar verilmez.
5. Doğukan onaylar -> kod değişir -> VERSION artar -> CHANGELOG.md'ye tarih, değişiklik, gerekçe (veri) yazılır.

## 10. Logo kütüphanesi büyür (v1.1, Doğukan onaylı 27 Kas 2026)
Haberdeki şirket/araç logosu `logos.csv`'de yoksa **üreten ajan** (X Marabası, Manus, Orva) ekler:
1. Resmi logoyu bul: önce press kit / resmi site, sonra Wikimedia Commons. Yapay zekâ ile logo çizilmez.
2. `python add_logo.py --src <URL|dosya> --slug <küçük-harf-slug> --name "Ad" --tags ai-lab,coding,agent,tool,chip,cloud --source <kaynak sayfa>`: düz zemini şeffaf yapar, kırpar, 512px'e getirir, #0A0C10 üzerinde kontrastı ölçer; koyu logo ise otomatik `slug-white.png` (beyaz silüet) üretir; `logos.csv`'ye satır ekler (kolonlar: slug,name,kind,svg_url,png_url,source_page,license,brand,white_png_url,tags). `--push` ile `git pull --rebase` + commit + push yapar.
3. Logo koyu zeminde kaybolmamalı (#0A0C10). Görselde logo her zaman açık karoda (#F5F6F8) orijinal renkte basılır; karoda kaybolan çok açık logo için ana dosya koyu silüete çevrilir.
4. Commit: `logo: <slug> eklendi`. Push öncesi her zaman `git pull --rebase`. **Başkasının logosunu ve logos.csv satırlarını asla silme, yeniden adlandırma ya da ezme** (araç var olan slug'ı reddeder).
5. GitHub'a yazamıyorsan: eksik logoyu Notion **Güncelleme Protokolü**'ne (başlık "Logo eksik: <şirket>", kaynak linkiyle) yaz; başka bir ajan ekler. Post harf karosuyla yine çıkabilir.
Toplu genişletme (şu an Manus) `tools/` ile yapılır; tek logoluk eklemeler `add_logo.py` iledir. Etiketler: ai-lab, coding, agent, tool, chip, cloud, model, app, framework, other.

## 11. T8 Gerçek kişi kompoziti (v1.1, Doğukan onaylı 27 Kas 2026)
Akış: (1) kişinin **gerçek** fotoğrafı (resmi basın fotoğrafı, şirket sitesi, Wikimedia Commons, güvenilir basın; lisans/kaynak not edilir) -> (2) arka plan **yapay zekâ matting** ile kesilir (`rembg`; en iyi model varsayılan, bkz. aşağıdaki zincir) -> (3) konuya uygun zemin (gerçek fotoğraf ya da AI sahne, ör. veri merkezi; zemin koyuya çekilir, ember vurgu) -> (4) entegrasyon: kenar inceltme + renk bulaşması (halo) temizliği, sahneye renk eşitleme, kenarda ışık sarma (light wrap), yumuşak temas gölgesi, **alfayı izleyen**, tek renk ember ince kenar ışıması (opaklık ~%19, v1.1.1'in yarısı) (kutu/panel kenarı görünmez; fotoğraf çerçevesinin kestiği yanlar ve alt kısım sahneye eritilir) -> (5) yazılar EB SIGNAL fontlarıyla kodla, `@eastblood_tr` filigranı ve kaynak satırı.
`python render.py t8 veri.json cikti.png` (örnek: examples/t8.json -> examples/T8.png).
**Sert kurallar**
- Kişinin yüzü **asla** yapay zekâ ile üretilmez veya değiştirilmez. Yalnız kesme, kırpma, renk eşitleme, ışık/kontrast. Yeniden çizme, yüz düzeltme, "AI portre" yasak.
- **Sahte alıntı yok.** `quote` alanı yalnız kaynakta geçen sözdür; çeviriyse anlam değişmez. Kaynak `source` alanında.
- Kişinin o mekanda **fiziksel olarak bulunduğu ima edilmez**: zemin açıkça tasarlanmış bir fondur (koyu, ember vurgu, kişi kesik ve ışımalı). Zeminde kişi/yüz olmaz.
- **Görselde fotoğraf kredisi yazılmaz** ("Foto: ...", "Wikimedia" vb. yok; `photo_credit` alanı kaldırıldı). Kaynak satırı ("Kaynak: ...") yalnız haber kaynağı varsa kalır. Fotoğraf lisans notu sadece repo README'sinde örnek dosya için tutulur.
- **Fotoğraf seçimi:** kişi **kameraya bakar / önden** durur; net, iyi ışıklı, yüksek çözünürlük. Yan bakış, profil, başı çevrilmiş, gözleri kapalı, el/bardak/mikrofon gibi nesnelerin yüzü kapattığı kareler seçilmez. Sahne arkası TechCrunch gibi logolu panolar sorun değil (kesilir). Eller kadrajda kalıyorsa `person_crop_bottom` ile bel üstünde kes. Resmi basın fotoğrafı > şirket sitesi > Wikimedia Commons (özgür lisans) > güvenilir basın. Adaylardan en az 3 kare karşılaştır, en iyisini al.
- Kadraj: geniş fotoğrafta kişi otomatik olarak kafa merkezli omuz kadrajına kesilir (`person_max_aspect`, varsayılan 0.95); kesilen yanlar sahneye eritilir.
- Kişinin logosu/şirketi varsa `logos/` klasöründen (bölüm 10).
- Örnek/sahte içerik `"example": true` damgalıdır, yayınlanmaz.

### T8 matting modeli (v1.1.1)
`render.py t8` kesimi şu zincirle dener, ilk çalışan kazanır (sonuç tmp'de önbelleğe alınır):
1. `person_cutout`: ajanın kendi AI görsel aracıyla önceden kestiği **şeffaf PNG** (yol/URL). Verilirse model çalışmaz; yalnız kenar inceltme ve entegrasyon uygulanır. `person` zaten gerçek şeffaflıklı PNG ise de aynen kullanılır.
2. **birefnet-portrait** (varsayılan, saç kenarları en temiz; ~928 MB indirme, CPU'da ~1 dk) -> 3. **birefnet-general** (~928 MB, ~30 sn; camı biraz kirli bırakabilir) -> 4. **isnet-general-use** + alpha matting (~170 MB, ~5 sn; kenarlar daha yumuşak) -> 5. **u2net_human_seg** (~168 MB, ~1 sn; saçta açık halo bırakır, son çare) -> 6. rembg/onnx yoksa fotoğraf yumuşak kenarlı yuvarlak çerçevede.
Tek modeli zorlamak: JSON'da `"matting_model"` ya da ortam değişkeni `EB_MATTING_MODEL`. Modeller ilk kullanımda `~/.rembg/models` içine iner (ortam internete kapalıysa `person_cutout` ver). `person_crop_bottom` (varsayılan 0.66): kesilen kişinin üst yüzde kaçı tutulacak (bel altı, eller, masa nesneleri dışarıda kalır).
Karşılaştırma (Amodei örneği, saç üstü): birefnet-portrait temiz; birefnet-general temiz ama gözlük camında arka plan sızıntısı; isnet-general-use hafif bulanık kenar; u2net_human_seg saçta belirgin açık halo (eski T8'deki kötü kırpmanın nedeni). Yüz hiçbir adımda yeniden çizilmez.

## 12. Görsel yazısı ve post metni birbirini TAMAMLAR (v1.1.1, Doğukan onaylı 27 Kas 2026)
Görselin üstündeki yazı ile post metni aynı cümleyi **asla** tekrar etmez.
- **Post metni = kanca (hook):** güçlü, merak uyandıran, algoritma kurallarına uygun (ilk 280 karakter, tartışmaya açık iddia, soruyla bitirme yok). Görselde ne yazdığını anlatmaz.
- **Görsel başlığı = bulgu / rakam / bağlam:** postun söylemediği şeyi ekler (sayı, karşılaştırma, kaynak, unvan, tarih).
- Aynı cümle ya da aynı rakam-iddia ikilisi iki yerde de varsa: görsel başlığını değiştir.
- Kontrol (yayından önce): postu ve görsel başlığını yan yana oku. Biri diğerinin kopyası ya da yeniden ifadesiyse yeniden yaz.
- (Aşağıdaki örnekler kurgusaldır, gerçek veri değildir.)
- **İyi:** Post: "Frontier laboratuvarlarından biri sessizce fiyatı yarıya indirdi. Rakipler bunu henüz fark etmedi." Görsel başlığı (T5): "1M token: $5 → $2,5" + bağlam satırı "Resmi fiyat sayfası, 27 Kas 2026".
- **Kötü:** Post: "DeepSeek yeni modelini duyurdu, fiyat yarıya indi." Görsel başlığı: "DeepSeek yeni modelini duyurdu, fiyat yarıya indi". Aynı cümle iki kez, görsel hiçbir şey eklemiyor.
- T8 için: görsel başlığı kişinin söylediği şeyin özü + unvan; post metni, o sözün neden önemli olduğuna dair kanca.


## 13. Video standardı (v1.2.0)
Kural kaynağı: Notion Görsel Standart · EB SIGNAL > VİDEO STANDARDI. Uygulama: `tools/video/` (tek komut), müzik: `music/`.
- Türkçe Cartesia seslendirme (My Turkish Voice, sonic-3.6, `language: tr`), yabancı kelimeler TTS metninde Türkçe okunuşla (Open ey ay, Liniyır), ekranda doğru yazım.
- Virgülde kısa nefes (`<break 200ms>`, ölçülen ~0,5 sn), noktada daha uzun (`<break 480ms>`, ~0,75 sn). Her şey tek nefes olmaz.
- Ses ekranla senkron: her cümle kaynak videoda o anlatılanın göründüğü kesitle eşlenir.
- İngilizce altyazı yakılır: kutu yok, şeffaf; kontur + yumuşak gölge, Inter 700 ~41 px, max 2 satır, giriş ve çıkış animasyonlu.
- Başlık kartı ve filigran (`@eastblood_tr` alt orta) animasyonlu, filigran nazik ve her zaman okunur.
- Müzik: önce ElevenLabs (VO'nun ~20 dB altı), olmazsa `music/` kütüphanesi. VO varken orijinal ses tamamen kapalı.
- 16:9 H.264/AAC, 1920x1080, 30 fps. Hareket katmanı HyperFrames (HTML+GSAP).

## 13. Vurgu standardı (v1.3, Doğukan onaylı 27 Kas 2026)
Önemli kelime/ifadeler **ember #FF5A36 + biraz daha kalın ağırlıkla** vurgulanır. Tüm şablonlarda aynı:
- JSON metninde `*kelime*` ya da `[[kelime]]` ile işaretle: `"headline": "Fiyat *yarıya* indi"`. İşaretler çıktıda görünmez.
- Her metin bloğunda **en fazla 1-2 vurgu** (3. işaret hata verir). Tüm metne ya da cümlenin çoğuna vurgu yapılmaz; vurgu rakam, karar, yeni bilgi gibi anahtar ifadeye gider.
- Desteklenen alanlar: `headline`, `title`, `label`, `quote`, `sub`, `context`, `points[]` (T4), T8 `quote` ve `sub`. Eski `highlight` alanı çalışmaya devam eder ama yeni içerikte işaret kullan.
- Ağırlık: başlık fontu (Space Grotesk, 700 üst sınır) zaten tam kalınsa renk değişir; gövde fontu (Inter) 400 -> 600, alıntı 600 -> 700.
- Başlık ile alıntı birlikte olduğunda (T8) ikisinde de birer vurgu olabilir.
