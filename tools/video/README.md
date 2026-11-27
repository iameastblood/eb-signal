# tools/video · EB SIGNAL video hattı (v1.4.0)

Resmi bir şirket videosunu (kaynak) ya da gerçek video yoksa Gamma slayt PNG'lerini (`mode: slides`) alır; Türkçe Cartesia seslendirmesi, yakılmış tek dil altyazı (küresel konu EN, Türkiye konusu TR), müzik ve HyperFrames hareket katmanıyla `@eastblood_tr` videosuna çevirir. **Hiçbir yere yayınlamaz.** Çıktı: `final.mp4` + 3 kare PNG + `report.json`.

## Tek komut
```bash
python tools/video/make_video.py --job tools/video/examples/dot_v2.json --out /workspace/video_out
# hazır VO WAV ile (Cartesia MCP/başka yerde üretildiyse): --vo vo.wav
# hazır müzik ile: --music music/tech.mp3      # verilmezse: ElevenLabs, o olmazsa music/ kütüphanesi
```
Anahtarlar yalnız ortam değişkeninden: `CARTESIA_API_KEY` (TTS), `ELEVENLABS_API_KEY` (müzik, isteğe bağlı).

## Job dosyası (JSON)
| Alan | Anlam |
|---|---|
| `source` | resmi video URL (yt-dlp) veya yerel MP4 (`--source` ile geçersiz kılınır) |
| `title`, `tag` | üstteki kısa başlık kartı (Space Grotesk) ve ember etiket |
| `logo` | `logos/<slug>.png`; varsa `-white` sürümü seçilir. Logo yoksa `add_logo.py` ile ekle, çizme |
| `genre` | `tech/finance/mystery/space/neutral` (müzik) |
| `lines[]` | her satır = bir VO cümlesi: `tr_chunks` (virgülle bölünen Türkçe parçalar, TTS okunuşuyla), `sub_chunks` (aynı sayıda, ekrana basılan altyazı, parça başına max 2 satır, 1-2 kelime `*ember*`; eski ad `en_chunks` da çalışır), `src_start` (kaynak saniyesi) ya da slayt modunda `slide` (0'dan slayt sırası) |
| `sub_lang` | `en` (küresel konu, varsayılan) ya da `tr` (yalnız Türkiye konusu). Tek dil; çift dil altyazı yok |
| `mode`, `slides`, `title_card` | `"mode": "slides"` + `"slides": ["slides/1.png", ...]` (job dosyasına göre yol) = Gamma slayt videosu; `title_card: false` başlık kartını kapatır (ilk slayt kanca olduğunda) |
| `comma_ms` / `period_ms` | virgül ve nokta için eklenen `<break>` süresi (varsayılan 220 / 750; ölçülen toplam duraklama virgülde ~0,35 sn, noktada ~1,0 sn) |
| `speed`, `voice_id`, `model` | varsayılan 0.94, My Turkish Voice, sonic-3.6 |
| `lead`, `tail` | VO'dan önce 0,5 sn, sonra 1,2 sn; `sub_font_px` 41 |

## Ne yapar (sıra)
1. Kaynak indirilir. 2. TTS metni kurulur (kural denetimi: em dash, @, `[...]`, mojibake, rakam ve kısaltma uyarısı). Virgüle `<break 220ms>`, noktaya `<break 750ms>`. VO üretilir (tek istek, doğal prozodi). 3. VO'daki sessizlikler ölçülür: en uzun N-1 sessizlik cümle sınırı, satır içi en uzunlar virgül sınırı. Altyazı ve görüntü bu zamanlara bağlanır, Whisper gerekmez (`--qa` ile geri dinleme dosyası). 4. **Senkron:** her cümle için kaynakta `src_start` (ya da önceki kesimin bittiği yer, hangisi geçse) noktasından o cümlenin VO süresi kadar görüntü kesilir; kesimler konuşmanın boşluk ortasındadır; VO hiç kesilip yapıştırılmaz. 5. Ses: VO -16 LUFS (sıkıştırıcı yok, linear loudnorm + alimiter), müzik -36 LUFS (VO'nun ~20 dB altı), orijinal ses tamamen kapalı. 6. HyperFrames projesi üretilir (`out/hf/`): başlık kartı, altyazılar, filigran; `render` ile MP4. 7. Ses VO+müzik karışımıyla mux, 3 kare.

## Gamma slayt modu (yedek, sadece gerçek video yoksa)
Gerçek görüntü önceliklidir; slayt videosu günlük alışkanlık olmaz (spec 13.1). Yalnız Orva ve X Marabası, haftada en fazla 1-2; Manus kullanmaz. Akış: Gamma `generate` (16:9, `cardSplit: inputTextBreaks`, `textMode: preserve`, tema `canaveral`, `exportAs: png`) > ZIP'i aç > `slides/1.png...` > job'da `mode: slides` > aynı komut. Örnek: `examples/gamma_slides.json`. Slaytlar 1920x1080'e kırpılır; giriş blur+ölçek+kayma, içte Ken Burns, geçişte ember tarama çizgisi; geçiş cümle arası sessizliğin ortasında. Higgsfield/Runway yalnız gerçekten gerekirse (sınırlı kredi).

## Görünüm (kural)
- Altyazı **tek dil, kutusuz**: Inter 700, ~38-41 px, ince koyu kontur + yumuşak gölge, 1-2 anahtar kelime ember (800). İki satırı geçmez. Her altyazı kelime kelime blur+yükselme ile girer, blur ile çıkar.
- Başlık kartı: panel soldan açılır, ember çubuk iner, logo yaylanarak gelir, başlık kelime kelime girer; çıkış hızlı blur+kayma.
- Filigran `@eastblood_tr` alt orta: yumuşak giriş, ember çizgi, nabız atan nokta, ~9 sn'de bir ışık süpürmesi, sonda çıkış. Her zaman okunur (kontur), altyazı üstünde durur.

## Dil ve okunuş (kural, 27 Kas 2026)
- **Kısaltma hedef dilin harf adıyla yazılır.** Türkçe ses Latin kısaltmayı Türkçe harf adıyla okuyor: "Ge Pe Te" yazarsan seslendirme "ge pe te" der, video amatör durur. İngilizce okunan kısaltmalar İngilizce harf adıyla, Türkçe imlayla yazılır: GPT → **Ci Pi Ti**, AI → **Ey Ay**, API → **Ey Pi Ay**, LLM → **El El Em**, CPU → **Si Pi Yu**, GPU → **Ci Pi Yu**, CEO → **Si İ Ou**, X → **Eks**. Sürüm ve sayı Türkçe kalır: 6.2 → "altı nokta iki".
- İngilizce harf adları (Türkçe imla): A Ey · B Bi · C Ci · D Di · E İ · F Ef · G Ci · H Eyç · I Ay · J Cey · K Key · L El · M Em · N En · O Ou · P Pi · Q Kyu · R Ar · S Es · T Ti · U Yu · V Vi · W Dabılyu · X Eks · Y Vay · Z Zi
- **ASR doğrulaması tek başına yetmez:** model kısaltmayı normalize ediyor, "Ge Pe Te" de "Ci Pi Ti" de yazıya "GPT" olarak dökülüyor. Kısaltmalı cümle kulakla dinlenir.
- **Duraklama ritmi:** cümle sonu `<break time="750ms"/>`, parça ve virgül arası `<break time="220ms"/>`, `speed` 0.94. Ölçülen sonuç: nokta sonları 0,93–1,02 sn, virgül araları 0,30–0,42 sn. Cümle sonu 500 ms altına düşerse akış üst üste biner, "her şeyi bir anda okuyor" hissi oluşur.
- Liste okumaları tek parça bırakılır; her öğeyi ayrı `tr_chunks` yapmak duraklamaları yığıyor ve kesik duyuruyor.
- Duraklamayı mix üzerinde değil VO dosyasında ölç, müzik eşiği bozuyor: `ffmpeg -i vo.wav -af silencedetect=noise=-40dB:d=0.18 -f null -`

## Ortam
Python 3.10+ (`requests`, isteğe bağlı `faster-whisper`), `ffmpeg` (libx264, aac), Node 20+ ve Chrome (HyperFrames; ilk çalıştırmada `npx hyperframes@0.9.99` iner), yt-dlp (URL kaynağı). HyperFrames komutu: `HF_CMD="npx --yes hyperframes@0.9.99"` (varsayılan) ya da `--hf-cmd`. GSAP CDN'den yüklenir (ağ gerekir). Render ~65 sn / 45 sn video (8 çekirdek), tüm hat ~100 sn.

## Orva / Manus
- **Orva:** ElevenLabs yok → `--music` verme, hat otomatik `music/` kütüphanesinden `genre` parçasını alır. Cartesia anahtarı ortamda olmalı. Chrome yoksa HyperFrames render başlamaz, bu durumda hat hata verir; çıktıyı `--no-render` ile `hf/` projesine kadar alıp Chrome'lu ortamda render et.
- **Manus:** repoyu çek, aynı komut. Chrome ve Node kontrol et.
- Yeni video için sadece yeni bir job JSON'u yaz (`examples/dot_v2.json` örnek).

## Bilinen sınırlar
- `cartesia_tts` ve ElevenLabs REST yolları bu ortamda canlı denenmedi (anahtar yok); denenen yol: Cartesia MCP'den gelen WAV (`--vo`) ve MCP ile üretilmiş müzik. İlk gerçek çalıştırmada hata görürsen README'ye ve CHANGELOG'a yaz.
- Zamanlama sessizlik tespitine dayanır; çok gürültülü bir VO'da `silencedetect` eşiği ayarlanmalı (`silences()`).
- X'in otomatik çevirisi gönderi metnini çevirir; yakılmış altyazıyı ve sesi çevirmez.
