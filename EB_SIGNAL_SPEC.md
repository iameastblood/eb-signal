# EB SIGNAL · Spec v1.0 (VERSION 1.0.0)
@eastblood_tr ortak görsel standardı. X Marabası, Manus, Orva görsel üretmeden önce bunu okur.
Referans kod: `ebstyle.py` + `render.py`. Ölçüler mantıksal piksel (render 2x yapılıp küçültülür).

## 1. Değişmez kurallar
1. Boyut her zaman **1600x900 (16:9)**. Başka oran yok.
2. Şirket/lab/ürün varsa **gerçek logo** `logos/` klasöründen gelir (logos.csv). Logo yapay zekâ ile ASLA çizilmez, yeniden boyanmaz. Logo yoksa: harf karosu + şirket adı, ve logos.csv'ye eklenmesi için not düş.
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
- Logo karosu: açık #F5F6F8 yuvarlak kare (radius %24), orijinal renkli logo %18-20 iç boşlukla. Wordmark (en/boy > 1.6) T1/T5/T6'da 2.4x geniş karo; T2/T3'te sembol logosu kullan.

## 5. Şablonlar ve JSON alanları (örnekler: examples/t*.json)
| ID | Ne zaman | Yerleşim | Zorunlu JSON |
|---|---|---|---|
| T1 Haber | Şirket duyurusu, ürün, olay | AI arka plan + sol koyu gradyan; logo 112 @(72,150); başlık 80px y=330 max 3 satır/880px, `highlight` ember; alt metin 32px max 2 satır; max 3 çip | logo, company, headline, source, date (+meta, highlight, sub, chips, bg) |
| T2 Benchmark | Resmi skor, 3-6 model | Başlık 60px max 2 satır/1150px; alt başlık y=274 + "yüksek/düşük olan daha iyi" otomatik; satır y=340, adım 86; bar x 470-1380; sıralı; kazanan ember | title, rows[{name,company,logo,value}], higher_is_better, source, date (+subtitle, max, unit, format) |
| T3 Versus | 2 ürün, eşleşen metrikler | 2 kart 690x534 (x72 / x838, y250-784); logo 84; max 4 metrik, adım 88; kazanan ember + ▲ (yüksek iyi) / ▼ (düşük iyi); VS rozeti | title, left/right{logo,name,sub}, metrics[{label,values,display,better}], source, date |
| T4 Sızıntı | X'ten sızıntı, iddia, ekran görüntüsü | Sol 600px: durum rozeti (DOĞRULANMADI/DOĞRULANDI), başlık 60px max 4 satır, max 3 madde; sağ: pencere çerçevesi x720-1528, ekran görüntüsü sığdırılır, `highlight_box` ember çerçeve | title, screenshot, handle, status, source, date (+points, highlight_box) |
| T5 Büyük rakam | Tek rakam haberi taşıyor | Logo 88 @(72,140); rakam 250px ember (taşarsa küçülür); etiket 48px; bağlam 28px; sağda max 3 karşılaştırma kartı | number, label, logo, company, source, date (+context, compare, bg) |
| T6 Alıntı | Kişi/kurum sözü | Ember tırnak 260px; alıntı 54px max 6 satır/1250px dikey ortalı; altında logo/avatar + ad + unvan. Kaynak URL post metninin sonunda | quote, name, source, date (+role, logo, highlight, bg) |

**T3 metrik yönü (better):** higher = yüksek iyi (puan, bağlam, hız token/sn, doğruluk) · lower = düşük iyi (fiyat, gecikme, hata oranı, bellek, maliyet) · none = karşılaştırma yok. Etikete otomatik "(düşük iyi)" eklenir.

## 6. Karar ağacı
1. Resmi sayısal benchmark + 3 veya daha fazla model -> **T2**
2. İki ürün/model yan yana, eşleşen metrikler -> **T3**
3. Tek rakam haberin kendisi (fiyat, kullanıcı, %, gelir) -> **T5**
4. X sızıntısı, iddia, ekran görüntüsü -> **T4** (doğrulanmadıysa status "Doğrulanmadı")
5. Kişi/kurum alıntısı -> **T6**
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
