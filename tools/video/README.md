# tools/video · EB SIGNAL video hattı (v1.2.0)

Resmi bir şirket videosunu (kaynak) alır; Türkçe Cartesia seslendirmesi, yakalanmış İngilizce altyazı, müzik ve HyperFrames hareket katmanıyla `@eastblood_tr` videosuna çevirir. **Hiçbir yere yayınlamaz.** Çıktı: `final.mp4` + 3 kare PNG + `report.json`.

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
| `lines[]` | her satır = bir VO cümlesi: `tr_chunks` (virgülle bölünen Türkçe parçalar, TTS okunuşuyla), `en_chunks` (aynı sayıda, ekrana basılan İngilizce, parça başına max 2 satır), `src_start` (bu cümlenin ekranla eşleşeceği kaynak saniyesi) |
| `comma_ms` / `period_ms` | virgül ve nokta için eklenen `<break>` süresi (varsayılan 200 / 480; ölçülen toplam duraklama virgülde ~0,5 sn, noktada ~0,75 sn) |
| `speed`, `voice_id`, `model` | varsayılan 0.95, My Turkish Voice, sonic-3.6 |
| `lead`, `tail` | VO'dan önce 0,5 sn, sonra 1,2 sn; `sub_font_px` 41 |

## Ne yapar (sıra)
1. Kaynak indirilir. 2. TTS metni kurulur (kural denetimi: em dash, @, `[...]`, mojibake, rakam uyarısı). Virgüle `<break 200ms>`, noktaya `<break 480ms>`. VO üretilir (tek istek, doğal prozodi). 3. VO'daki sessizlikler ölçülür: en uzun N-1 sessizlik cümle sınırı, satır içi en uzunlar virgül sınırı. Altyazı ve görüntü bu zamanlara bağlanır, Whisper gerekmez (`--qa` ile geri dinleme dosyası). 4. **Senkron:** her cümle için kaynakta `src_start` (ya da önceki kesimin bittiği yer, hangisi geçse) noktasından o cümlenin VO süresi kadar görüntü kesilir; kesimler konuşmanın boşluk ortasındadır; VO hiç kesilip yapıştırılmaz. 5. Ses: VO -16 LUFS (sıkıştırıcı yok, linear loudnorm + alimiter), müzik -36 LUFS (VO'nun ~20 dB altı), orijinal ses tamamen kapalı. 6. HyperFrames projesi üretilir (`out/hf/`): başlık kartı, altyazılar, filigran; `render` ile MP4. 7. Ses VO+müzik karışımıyla mux, 3 kare.

## Görünüm (kural)
- Altyazı **kutusuz**: Inter 700, ~41 px, ince koyu kontur + yumuşak gölge. İki satırı geçmez. Her altyazı kelime kelime blur+yükselme ile girer, blur ile çıkar.
- Başlık kartı: panel soldan açılır, ember çubuk iner, logo yaylanarak gelir, başlık kelime kelime girer; çıkış hızlı blur+kayma.
- Filigran `@eastblood_tr` alt orta: yumuşak giriş, ember çizgi, nabız atan nokta, ~9 sn'de bir ışık süpürmesi, sonda çıkış. Her zaman okunur (kontur), altyazı üstünde durur.

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
