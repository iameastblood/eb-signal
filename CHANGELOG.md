# CHANGELOG · EB SIGNAL

Kural: her değişiklik VERSION'ı artırır. MAJOR = şablon yapısı/palet değişimi, MINOR = yeni şablon veya yeni alan, PATCH = ölçü/renk ince ayarı, logo ekleme.
Haftada en fazla 1-2 değişiklik, Doğukan onayından sonra. Her satır: tarih, sürüm, ne değişti, neden (hangi veri).

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
