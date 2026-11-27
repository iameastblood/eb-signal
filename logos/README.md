# logos/ · EB SIGNAL logo kütüphanesi

Görsel motoru her logoyu `logos/<slug>.png` olarak arar. Bu klasör tek doğru kaynaktır,
`logos.csv` ise kayıt defteridir. Logo **asla** yapay zekâ ile çizilmez, elle yeniden
boyanmaz; yalnız resmi vektör kaynaktan üretilir.

## Dosya kuralları

| Kural | Değer |
| --- | --- |
| Biçim | PNG, RGBA (şeffaf zemin zorunlu) |
| Boyut | en uzun kenar 512 px, oran korunur, kırpılmış (kenar boşluğu yok) |
| Ad | `slug.png`, küçük harf ASCII, tire ayırıcı (`claude-code.png`) |
| Koyu zemin sürümü | `slug-white.png` (aynı vektörün beyaz silüeti) |
| Kaynak | `logos.csv` içinde `source_page` + `license` |

Şeffaflık denetimi: dört köşe pikseli tam şeffaf olmalı. Opak zeminli dosya kabul edilmez.

## Yeni logo ekleme protokolü (ajanlar için)

1. Logo gerçekten var mı doğrula. Ürün adı uydurma; emin değilsen ekleme, not düş.
2. Kaynağı sırayla ara: resmi brand/press kit > resmi GitHub deposu > Wikimedia Commons >
   lobe-icons (`github.com/lobehub/lobe-icons`).
3. `tools/logo_catalog.json` içine tek satır ekle:
   `{"slug": "...", "name": "...", "brand": "...", "kind": "symbol|wordmark|product", "src": "lobe:<ikon>"}`
   Harici dosya için `"src": "url:https://..."` kullan.
4. Üret: `python tools/build_logos.py logos` ardından `python tools/make_white.py`.
5. Kayıt defterini güncelle: `python tools/make_csv.py` ve `python tools/make_logo_readme.py`.
6. Görseli damalı zeminde gözle kontrol et. Bozuksa ekleme.
7. Tek konu tek commit: `logo: <slug> eklendi` veya `logo: <slug> düzeltildi`.

## Hızlı yol: tek logo (v1.1)

Tek logo için `tools/` zinciri yerine: `python add_logo.py --src <URL|dosya> --slug <slug> --name "Ad" --tags <etiketler> --source <sayfa> [--push]`.
Şeffaflık, kırpma, koyu zemin kontrolü, `-white` sürüm ve `logos.csv` satırını (tags dahil) otomatik yapar. Var olan slug'ı ezmez.

## Koyu zemin notu

`-white.png` sürümü, logonun alfa kanalı korunarak beyaz doldurulmasıyla üretilir. Karar tek
yerde verilir: `tools/make_white.py` içindeki `legible()` fonksiyonu. İçi dolu kare app
ikonlarında silüet okunmadığı için beyaz sürüm üretilmez; bu logolar koyu zeminde renkli
haliyle ya da açık karo içinde kullanılır.

İki elle kontrol dosyası var, ikisi de `build_logos.py` ve `make_white.py` tarafından okunur:

| Dosya | Anlamı |
| --- | --- |
| `tools/white_skip.txt` | Üst bölümdeki slug'lar için beyaz sürüm **asla** üretilmez (elle karar) |
| `tools/white_force.txt` | Otomatik kurala rağmen beyaz sürüm üretilir (koyu çizgi logo) |

`white_skip.txt` iki bölümlüdür: elle atlananlar korunur, `OTOMATİK` bölümü her koşuda
yeniden yazılır. Beyaz sürüm istediğin bir logo otomatik bölümde görünüyorsa slug'ı
`white_force.txt` dosyasına ekle ve `python tools/make_white.py` çalıştır.

## Marka dizini


### Ai2  ·  marka: `ai2`

- `ai2.png` + beyaz · Ai2 (Allen Institute) (wordmark)

### AI21 Labs  ·  marka: `ai21`

- `ai21.png` + beyaz · AI21 Labs (wordmark)

### Aleph Alpha  ·  marka: `alephalpha`

- `aleph-alpha.png` + beyaz · Aleph Alpha (wordmark)

### Alibaba  ·  marka: `alibaba`

- `alibaba.png` + beyaz · Alibaba (wordmark)

### Amazon  ·  marka: `amazon`

- `bedrock.png` + beyaz · Amazon Bedrock (product)
- `nova.png` · Amazon Nova (product)

### Ambi (Mistlabs)  ·  marka: `ambi`

- `ambi.png` + beyaz · Ambi (Mistlabs) (product)

### Anthropic  ·  marka: `anthropic`

- `anthropic-symbol.png` + beyaz · Anthropic (işaret) (symbol)
- `claude-code.png` + beyaz · Claude Code (product)
- `claude-duet.png` · Claude Duet (product)
- `mcp.png` + beyaz · Model Context Protocol (product)

### AssemblyAI  ·  marka: `assemblyai`

- `assemblyai.png` + beyaz · AssemblyAI (wordmark)

### aws  ·  marka: `aws`

- `kiro.png` · Kiro (product)

### Baichuan  ·  marka: `baichuan`

- `baichuan.png` + beyaz · Baichuan (wordmark)

### Baidu  ·  marka: `baidu`

- `baidu.png` + beyaz · Baidu (wordmark)
- `ernie.png` + beyaz · ERNIE (product)

### Baseten  ·  marka: `baseten`

- `baseten.png` + beyaz · Baseten (wordmark)

### Black Forest Labs  ·  marka: `bfl`

- `bfl.png` + beyaz · Black Forest Labs (wordmark)
- `flux.png` + beyaz · FLUX (product)

### Block  ·  marka: `block`

- `goose.png` + beyaz · Goose (product)

### Brave  ·  marka: `brave`

- `brave.png` + beyaz · Brave (wordmark)

### ByteDance  ·  marka: `bytedance`

- `bytedance.png` + beyaz · ByteDance (wordmark)
- `doubao.png` + beyaz · Doubao (product)
- `jimeng.png` + beyaz · Jimeng (product)
- `trae.png` + beyaz · Trae (product)

### Cerebras  ·  marka: `cerebras`

- `cerebras.png` + beyaz · Cerebras (wordmark)

### Cline  ·  marka: `cline`

- `cline.png` + beyaz · Cline (product)

### Cloudflare  ·  marka: `cloudflare`

- `cloudflare.png` + beyaz · Cloudflare (wordmark)

### Cognition  ·  marka: `cognition`

- `devin.png` + beyaz · Devin (product)
- `windsurf.png` + beyaz · Windsurf (product)

### Cohere  ·  marka: `cohere`

- `cohere.png` + beyaz · Cohere (wordmark)
- `commanda.png` + beyaz · Command A (product)

### ComfyUI  ·  marka: `comfyui`

- `comfyui.png` + beyaz · ComfyUI (product)

### CrewAI  ·  marka: `crewai`

- `crewai.png` + beyaz · CrewAI (wordmark)

### Dify  ·  marka: `dify`

- `dify.png` + beyaz · Dify (wordmark)

### diger  ·  marka: `diger`

- `amazon.png` + beyaz · Amazon (wordmark)
- `anthropic.png` + beyaz · Anthropic (wordmark)
- `apple.png` + beyaz · Apple (symbol)
- `aws.png` + beyaz · Amazon Web Services (wordmark)
- `claude.png` + beyaz · Claude (Anthropic) (symbol)
- `cursor.png` + beyaz · Cursor (wordmark)
- `deepseek.png` + beyaz · DeepSeek (symbol)
- `huggingface.png` + beyaz · Hugging Face (symbol)
- `meta.png` + beyaz · Meta (symbol)
- `meta-wordmark.png` + beyaz · Meta (wordmark) (wordmark)
- `microsoft.png` + beyaz · Microsoft (wordmark)
- `mistral.png` + beyaz · Mistral AI (symbol)
- `nvidia.png` + beyaz · NVIDIA (wordmark)
- `openai.png` + beyaz · OpenAI (symbol)
- `openai-wordmark.png` + beyaz · OpenAI (wordmark) (wordmark)
- `perplexity.png` + beyaz · Perplexity (wordmark)
- `qwen.png` + beyaz · Qwen (Alibaba) (symbol)
- `tesla.png` + beyaz · Tesla (symbol)
- `xai.png` + beyaz · xAI (symbol)
- `zai.png` · Z.ai (Zhipu) (symbol)

### ElevenLabs  ·  marka: `elevenlabs`

- `elevenlabs.png` + beyaz · ElevenLabs (wordmark)

### Exa  ·  marka: `exa`

- `exa.png` + beyaz · Exa (wordmark)

### fal.ai  ·  marka: `fal`

- `fal.png` + beyaz · fal.ai (wordmark)

### Firecrawl  ·  marka: `firecrawl`

- `firecrawl.png` + beyaz · Firecrawl (wordmark)

### Fireworks AI  ·  marka: `fireworks`

- `fireworks.png` + beyaz · Fireworks AI (wordmark)

### Google  ·  marka: `google`

- `antigravity.png` + beyaz · Antigravity (product)
- `gemini.png` + beyaz · Gemini (symbol)
- `gemini-cli.png` · Gemini CLI (product)
- `gemma.png` + beyaz · Gemma (product)
- `google.png` + beyaz · Google (wordmark)
- `google-ai-studio.png` + beyaz · Google AI Studio (product)
- `google-cloud.png` + beyaz · Google Cloud (wordmark)
- `google-deepmind.png` + beyaz · Google DeepMind (wordmark)
- `nano-banana.png` + beyaz · Nano Banana (product)
- `notebooklm.png` + beyaz · NotebookLM (product)

### Gradio  ·  marka: `gradio`

- `gradio.png` + beyaz · Gradio (wordmark)

### Groq  ·  marka: `groq`

- `groq.png` + beyaz · Groq (wordmark)

### Hark  ·  marka: `hark`

- `hark.png` + beyaz · Hark (product)

### Hyperbolic  ·  marka: `hyperbolic`

- `hyperbolic.png` + beyaz · Hyperbolic (wordmark)

### IBM  ·  marka: `ibm`

- `ibm.png` + beyaz · IBM (wordmark)

### Ideogram  ·  marka: `ideogram`

- `ideogram.png` + beyaz · Ideogram (wordmark)

### Inflection AI  ·  marka: `inflection`

- `inflection.png` + beyaz · Inflection AI (wordmark)

### Instinct  ·  marka: `instinct`

- `instinct.png` + beyaz · Instinct (product)

### JetBrains  ·  marka: `jetbrains`

- `junie.png` + beyaz · Junie (product)

### Jina AI  ·  marka: `jina`

- `jina.png` + beyaz · Jina AI (wordmark)

### Kagi  ·  marka: `kagi`

- `kagi.png` + beyaz · Kagi (wordmark)

### Kilo Code  ·  marka: `kilo-code`

- `kilo-code.png` + beyaz · Kilo Code (product)

### Kling  ·  marka: `kling`

- `kling.png` + beyaz · Kling (wordmark)

### Krea  ·  marka: `krea`

- `krea.png` + beyaz · Krea (wordmark)

### LangChain  ·  marka: `langchain`

- `langchain.png` + beyaz · LangChain (wordmark)
- `langgraph.png` + beyaz · LangGraph (product)

### Langfuse  ·  marka: `langfuse`

- `langfuse.png` + beyaz · Langfuse (wordmark)

### Liquid AI  ·  marka: `liquid`

- `liquid.png` + beyaz · Liquid AI (wordmark)

### LlamaIndex  ·  marka: `llamaindex`

- `llamaindex.png` + beyaz · LlamaIndex (wordmark)

### LM Studio  ·  marka: `lmstudio`

- `lmstudio.png` + beyaz · LM Studio (wordmark)

### Lovable  ·  marka: `lovable`

- `lovable.png` + beyaz · Lovable (wordmark)

### Luma AI  ·  marka: `luma`

- `luma.png` + beyaz · Luma AI (wordmark)

### Magic  ·  marka: `magic`

- `magic.png` + beyaz · Magic (wordmark)

### Manus  ·  marka: `manus`

- `manus.png` + beyaz · Manus (product)
- `manus-cue.png` · Manus Cue (product)

### Meta  ·  marka: `meta`

- `meta-ai.png` + beyaz · Meta AI (product)
- `meta-muse.png` + beyaz · Meta Muse (product)

### Microsoft  ·  marka: `microsoft`

- `azure.png` + beyaz · Azure (wordmark)
- `azure-ai.png` + beyaz · Azure AI (product)
- `copilot.png` + beyaz · Microsoft Copilot (product)
- `github.png` + beyaz · GitHub (wordmark)
- `github-copilot.png` + beyaz · GitHub Copilot (product)

### Midjourney  ·  marka: `midjourney`

- `midjourney.png` + beyaz · Midjourney (wordmark)

### MiniMax  ·  marka: `minimax`

- `hailuo.png` + beyaz · Hailuo AI (product)
- `minimax.png` + beyaz · MiniMax (symbol)

### Moonshot AI  ·  marka: `moonshot`

- `kimi.png` + beyaz · Kimi (symbol)
- `moonshot.png` + beyaz · Moonshot AI (wordmark)

### n8n  ·  marka: `n8n`

- `n8n.png` + beyaz · n8n (wordmark)

### Nebius  ·  marka: `nebius`

- `nebius.png` + beyaz · Nebius (wordmark)

### Notion  ·  marka: `notion`

- `notion.png` + beyaz · Notion (wordmark)

### Novita AI  ·  marka: `novita`

- `novita.png` + beyaz · Novita AI (wordmark)

### Ollama  ·  marka: `ollama`

- `ollama.png` + beyaz · Ollama (wordmark)

### Open WebUI  ·  marka: `openwebui`

- `openwebui.png` + beyaz · Open WebUI (product)

### OpenAI  ·  marka: `openai`

- `chatgpt-dots.png` + beyaz · ChatGPT Dots (product)
- `codex.png` · Codex (product)
- `dall-e.png` + beyaz · DALL·E (product)
- `sora.png` · Sora (product)

### OpenCode  ·  marka: `opencode`

- `opencode.png` + beyaz · OpenCode (product)

### OpenHands  ·  marka: `openhands`

- `openhands.png` + beyaz · OpenHands (product)

### OpenRouter  ·  marka: `openrouter`

- `openrouter.png` + beyaz · OpenRouter (wordmark)

### Pally  ·  marka: `pally`

- `pally.png` · Pally (product)

### Persona  ·  marka: `persona`

- `persona.png` + beyaz · Persona (product)

### Pickle  ·  marka: `pickle`

- `pickle.png` · Pickle (product)

### Pika  ·  marka: `pika`

- `pika.png` + beyaz · Pika (wordmark)

### Poke  ·  marka: `poke`

- `poke.png` · Poke (product)

### Poolside  ·  marka: `poolside`

- `poolside.png` + beyaz · Poolside (wordmark)

### Recraft  ·  marka: `recraft`

- `recraft.png` + beyaz · Recraft (wordmark)

### Reka AI  ·  marka: `reka`

- `reka.png` + beyaz · Reka AI (wordmark)

### Rene  ·  marka: `rene`

- `rene.png` + beyaz · Rene (product)

### Replicate  ·  marka: `replicate`

- `replicate.png` + beyaz · Replicate (wordmark)

### Replit  ·  marka: `replit`

- `replit.png` + beyaz · Replit (wordmark)

### Roo Code  ·  marka: `roo-code`

- `roo-code.png` + beyaz · Roo Code (product)

### Runway  ·  marka: `runway`

- `runway.png` + beyaz · Runway (wordmark)

### Sakana AI  ·  marka: `sakana`

- `sakana.png` + beyaz · Sakana AI (wordmark)

### SambaNova  ·  marka: `sambanova`

- `sambanova.png` + beyaz · SambaNova (wordmark)

### Samsung  ·  marka: `samsung`

- `samsung.png` + beyaz · Samsung (wordmark)

### SenseNova  ·  marka: `sensenova`

- `sensenova.png` + beyaz · SenseNova (wordmark)

### Sharick  ·  marka: `sharick`

- `sharick.png` · Sharick (product)

### Snowflake  ·  marka: `snowflake`

- `snowflake.png` + beyaz · Snowflake (wordmark)

### Sourcegraph  ·  marka: `sourcegraph`

- `amp.png` + beyaz · Amp (product)

### Stability AI  ·  marka: `stability`

- `stability.png` + beyaz · Stability AI (wordmark)

### StepFun  ·  marka: `stepfun`

- `stepfun.png` + beyaz · StepFun (wordmark)

### Suno  ·  marka: `suno`

- `suno.png` + beyaz · Suno (wordmark)

### Tavily  ·  marka: `tavily`

- `tavily.png` + beyaz · Tavily (wordmark)

### Tencent  ·  marka: `tencent`

- `hunyuan.png` + beyaz · Hunyuan (product)
- `tencent.png` + beyaz · Tencent (wordmark)

### Together AI  ·  marka: `together`

- `together.png` + beyaz · Together AI (wordmark)

### Town  ·  marka: `town`

- `town.png` · Town (product)

### Udio  ·  marka: `udio`

- `udio.png` + beyaz · Udio (wordmark)

### Underdog  ·  marka: `underdog`

- `underdog.png` · Underdog (product)

### Upstage  ·  marka: `upstage`

- `upstage.png` + beyaz · Upstage (wordmark)

### Vercel  ·  marka: `vercel`

- `v0.png` + beyaz · v0 (product)
- `vercel.png` + beyaz · Vercel (wordmark)

### Vidu  ·  marka: `vidu`

- `vidu.png` + beyaz · Vidu (wordmark)

### vLLM  ·  marka: `vllm`

- `vllm.png` + beyaz · vLLM (product)

### Wabi  ·  marka: `wabi`

- `wabi.png` + beyaz · Wabi (product)

### Wajo (Fo)  ·  marka: `wajo`

- `fo.png` · Fo (Wajo) (product)

### Weights & Biases  ·  marka: `wandb`

- `wandb.png` + beyaz · Weights & Biases (wordmark)

### xAI  ·  marka: `xai`

- `grok.png` + beyaz · Grok (symbol)
- `grok-bot.png` · Grok Bot (product)

### Zhipu AI  ·  marka: `zhipu`

- `chatglm.png` + beyaz · GLM (Zhipu) (product)


Toplam **161** logo, **145** beyaz sürüm.
