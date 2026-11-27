#!/usr/bin/env python3
"""logos/README.md üretir: marka marka dizin + yeni logo ekleme protokolü."""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND_TR = {
    "anthropic": "Anthropic", "openai": "OpenAI", "google": "Google", "meta": "Meta",
    "xai": "xAI", "microsoft": "Microsoft", "nvidia": "NVIDIA", "mistral": "Mistral AI",
    "deepseek": "DeepSeek", "alibaba": "Alibaba", "moonshot": "Moonshot AI",
    "zhipu": "Zhipu AI", "minimax": "MiniMax", "bytedance": "ByteDance", "baidu": "Baidu",
    "tencent": "Tencent", "amazon": "Amazon", "apple": "Apple", "samsung": "Samsung",
    "tesla": "Tesla", "perplexity": "Perplexity", "cohere": "Cohere",
    "huggingface": "Hugging Face", "stability": "Stability AI", "midjourney": "Midjourney",
    "runway": "Runway", "luma": "Luma AI", "pika": "Pika", "kling": "Kling",
    "vidu": "Vidu", "bfl": "Black Forest Labs", "ideogram": "Ideogram",
    "recraft": "Recraft", "krea": "Krea", "elevenlabs": "ElevenLabs", "suno": "Suno",
    "udio": "Udio", "groq": "Groq", "cerebras": "Cerebras", "sambanova": "SambaNova",
    "together": "Together AI", "fireworks": "Fireworks AI", "replicate": "Replicate",
    "openrouter": "OpenRouter", "ollama": "Ollama", "lmstudio": "LM Studio",
    "vercel": "Vercel", "cloudflare": "Cloudflare", "snowflake": "Snowflake", "ibm": "IBM",
    "cursor": "Cursor", "cognition": "Cognition", "replit": "Replit", "lovable": "Lovable",
    "cline": "Cline", "roo-code": "Roo Code", "kilo-code": "Kilo Code",
    "openhands": "OpenHands", "sourcegraph": "Sourcegraph", "opencode": "OpenCode",
    "jetbrains": "JetBrains", "block": "Block", "manus": "Manus", "notion": "Notion",
    "langchain": "LangChain", "llamaindex": "LlamaIndex", "n8n": "n8n", "crewai": "CrewAI",
    "dify": "Dify", "gradio": "Gradio", "comfyui": "ComfyUI", "openwebui": "Open WebUI",
    "sakana": "Sakana AI", "liquid": "Liquid AI", "ai2": "Ai2", "reka": "Reka AI",
    "inflection": "Inflection AI", "ai21": "AI21 Labs", "alephalpha": "Aleph Alpha",
    "stepfun": "StepFun", "upstage": "Upstage", "baichuan": "Baichuan", "sensenova": "SenseNova",
    "poolside": "Poolside", "magic": "Magic", "exa": "Exa", "tavily": "Tavily",
    "jina": "Jina AI", "firecrawl": "Firecrawl", "brave": "Brave", "kagi": "Kagi",
    "assemblyai": "AssemblyAI", "fal": "fal.ai", "novita": "Novita AI",
    "hyperbolic": "Hyperbolic", "nebius": "Nebius", "baseten": "Baseten", "vllm": "vLLM",
    "langfuse": "Langfuse", "wandb": "Weights & Biases",
    "instinct": "Instinct", "hark": "Hark", "poke": "Poke", "wajo": "Wajo (Fo)",
    "wabi": "Wabi", "sharick": "Sharick", "pally": "Pally", "rene": "Rene",
    "town": "Town", "ambi": "Ambi (Mistlabs)", "persona": "Persona",
    "pickle": "Pickle", "underdog": "Underdog",
}

HEAD = """# logos/ · EB SIGNAL logo kütüphanesi

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

`-white.png` sürümü, logonun alfa kanalı korunarak beyaz doldurulmasıyla üretilir. İçi dolu
kare app ikonlarında (codex, sora, kiro, zai, gemini-cli, dall-e, nova, antigravity) silüet
okunmadığı için beyaz sürüm **üretilmez**; bu logolar koyu zeminde renkli haliyle ya da açık
karo içinde kullanılır.

## Marka dizini

"""


def main():
    rows = list(csv.DictReader(open(ROOT / "logos.csv")))
    g = defaultdict(list)
    for r in rows:
        g[r.get("brand") or "diger"].append(r)
    out = [HEAD]
    for brand in sorted(g, key=lambda b: BRAND_TR.get(b, b).lower()):
        items = sorted(g[brand], key=lambda r: r["slug"])
        out.append(f"### {BRAND_TR.get(brand, brand)}  ·  marka: `{brand}`\n")
        for r in items:
            w = " + beyaz" if r.get("white_png_url") else ""
            out.append(f"- `{r['slug']}.png`{w} · {r['name']} ({r['kind']})")
        out.append("")
    out.append(f"\nToplam **{len(rows)}** logo, **{sum(1 for r in rows if r.get('white_png_url'))}** beyaz sürüm.\n")
    (ROOT / "logos" / "README.md").write_text("\n".join(out))
    print(f"README yazıldı: {len(rows)} logo, {len(g)} marka")


if __name__ == "__main__":
    main()
