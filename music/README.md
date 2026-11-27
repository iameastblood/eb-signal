# music/ · EB SIGNAL hazır müzik kütüphanesi

5 enstrümantal parça (ElevenLabs Music `eleven_music_v2` ile üretildi, 75 sn, mp3 96 kbps, ~0,9 MB). Vokal yok.

| Dosya | Tür | Ne zaman |
|---|---|---|
| `tech.mp3` | Teknoloji / lansman, minimal elektronik | model duyurusu, ürün, AI aracı, kodlama |
| `finance.mp3` | Finans, piyano + nabız | yatırım, gelir, şirket, piyasa |
| `mystery.mp3` | Gizem / sızıntı, koyu ambiyans | sızıntı, gizli proje, güvenlik |
| `space.mp3` | Robotik / uzay, sinematik pad | robot, uzay, donanım, bilim |
| `neutral.mp3` | Nötr, enerjik | genel haber, emin değilsen |

`index.json` aynı listeyi ve her türün ElevenLabs prompt'unu içerir (`tools/video/make_video.py` bunu okur).

## Kural: önce ElevenLabs, sonra kütüphane
1. Videoya müzik gerekiyorsa ajan önce ElevenLabs'te konuya uygun enstrümantal üretir (`music_v2`, `force_instrumental=true`, ~60 sn; prompt için `index.json`'daki tür prompt'unu başlangıç al).
2. **ElevenLabs bağlı değilse (Orva), bağlantı hatası verirse, kredi biterse veya herhangi bir anormallik olursa** bu klasörden türe uygun parçayı seç. Uzun beklemek yok, video aynı koşuda çıkar.
3. Seviye her iki durumda aynı: ana müzik **konuşmanın yaklaşık 20 dB altında** (VO -16 LUFS, müzik -36 LUFS). `make_video.py` bunu otomatik yapar.
4. Orijinal videonun sesi VO varken tamamen kapalıdır.

Yeni parça eklemek: aynı biçimde (`ffmpeg -ac 2 -ar 44100 -b:a 96k`, kısa fade) `music/` altına koy, `index.json`'a tür ekle, CHANGELOG'a PATCH yaz. Dosya başına 1,5 MB üstüne çıkma.
