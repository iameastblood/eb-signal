#!/usr/bin/env python3
"""tools/logo_catalog.json üretir. Katalog tek doğru kaynaktır: slug, ad, marka, tür, kaynak."""
import json, sys
from pathlib import Path

LOBE = Path("/home/ubuntu/src/lobe/package/icons")

# (slug, ad, marka, tur, lobe adı)  tur: wordmark | symbol | product
T = [
    # ---- Anthropic ----
    ("anthropic-symbol", "Anthropic (işaret)", "anthropic", "symbol", "lobe:anthropic"),
    ("claude-code", "Claude Code", "anthropic", "product", "lobe:claudecode"),
    # ---- OpenAI ----
    ("codex", "Codex", "openai", "product", "lobe:codex"),
    ("sora", "Sora", "openai", "product", "lobe:sora"),
    ("dall-e", "DALL·E", "openai", "product", "lobe:dalle"),
    # ---- Google ----
    ("google", "Google", "google", "wordmark", "lobe:google"),
    ("google-deepmind", "Google DeepMind", "google", "wordmark", "lobe:deepmind"),
    ("gemini", "Gemini", "google", "symbol", "url:https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg"),
    ("gemini-cli", "Gemini CLI", "google", "product", "lobe:geminicli"),
    ("gemma", "Gemma", "google", "product", "lobe:gemma"),
    ("notebooklm", "NotebookLM", "google", "product", "lobe:notebooklm"),
    ("antigravity", "Antigravity", "google", "product", "lobe:antigravity"),
    ("nano-banana", "Nano Banana", "google", "product", "lobe:nanobanana"),
    ("google-cloud", "Google Cloud", "google", "wordmark", "lobe:googlecloud"),
    ("google-ai-studio", "Google AI Studio", "google", "product", "lobe:aistudio"),
    # ---- Meta ----
    ("meta-ai", "Meta AI", "meta", "product", "lobe:metaai"),
    # ---- xAI ----
    ("grok", "Grok", "xai", "symbol", "lobe:grok"),
    # ---- Microsoft ----
    ("copilot", "Microsoft Copilot", "microsoft", "product", "lobe:copilot"),
    ("github", "GitHub", "microsoft", "wordmark", "lobe:github"),
    ("github-copilot", "GitHub Copilot", "microsoft", "product", "lobe:githubcopilot"),
    ("azure", "Azure", "microsoft", "wordmark", "lobe:azure"),
    ("azure-ai", "Azure AI", "microsoft", "product", "lobe:azureai"),
    ("samsung", "Samsung", "samsung", "wordmark", "url:https://commons.wikimedia.org/wiki/Special:FilePath/Samsung%20wordmark.svg"),
    # ---- NVIDIA ----
    # ---- Mistral ----
    # ---- DeepSeek ----
    # ---- Alibaba ----
    ("alibaba", "Alibaba", "alibaba", "wordmark", "lobe:alibaba"),
    # ---- Moonshot ----
    ("moonshot", "Moonshot AI", "moonshot", "wordmark", "lobe:moonshot"),
    ("kimi", "Kimi", "moonshot", "symbol", "lobe:kimi"),
    # ---- Zhipu ----
    ("chatglm", "GLM (Zhipu)", "zhipu", "product", "lobe:chatglm"),
    # ---- MiniMax ----
    ("minimax", "MiniMax", "minimax", "symbol", "lobe:minimax"),
    ("hailuo", "Hailuo AI", "minimax", "product", "lobe:hailuo"),
    # ---- ByteDance ----
    ("bytedance", "ByteDance", "bytedance", "wordmark", "lobe:bytedance"),
    ("doubao", "Doubao", "bytedance", "product", "lobe:doubao"),
    ("trae", "Trae", "bytedance", "product", "lobe:trae"),
    ("jimeng", "Jimeng", "bytedance", "product", "lobe:jimeng"),
    # ---- Baidu ----
    ("baidu", "Baidu", "baidu", "wordmark", "lobe:baidu"),
    ("ernie", "ERNIE", "baidu", "product", "lobe:wenxin"),
    # ---- Tencent ----
    ("tencent", "Tencent", "tencent", "wordmark", "lobe:tencent"),
    ("hunyuan", "Hunyuan", "tencent", "product", "lobe:hunyuan"),
    # ---- Amazon ----
    ("bedrock", "Amazon Bedrock", "amazon", "product", "lobe:bedrock"),
    ("nova", "Amazon Nova", "amazon", "product", "lobe:nova"),
    # ---- Perplexity ----
    # ---- Cohere ----
    ("cohere", "Cohere", "cohere", "wordmark", "lobe:cohere"),
    ("commanda", "Command A", "cohere", "product", "lobe:commanda"),
    # ---- Hugging Face ----
    # ---- Görsel / video üreticileri ----
    ("stability", "Stability AI", "stability", "wordmark", "lobe:stability"),
    ("midjourney", "Midjourney", "midjourney", "wordmark", "lobe:midjourney"),
    ("runway", "Runway", "runway", "wordmark", "lobe:runway"),
    ("luma", "Luma AI", "luma", "wordmark", "lobe:luma"),
    ("pika", "Pika", "pika", "wordmark", "lobe:pika"),
    ("kling", "Kling", "kling", "wordmark", "lobe:kling"),
    ("vidu", "Vidu", "vidu", "wordmark", "lobe:vidu"),
    ("flux", "FLUX", "bfl", "product", "lobe:flux"),
    ("bfl", "Black Forest Labs", "bfl", "wordmark", "lobe:bfl"),
    ("ideogram", "Ideogram", "ideogram", "wordmark", "lobe:ideogram"),
    ("recraft", "Recraft", "recraft", "wordmark", "lobe:recraft"),
    ("krea", "Krea", "krea", "wordmark", "lobe:krea"),
    # ---- Ses / müzik ----
    ("elevenlabs", "ElevenLabs", "elevenlabs", "wordmark", "lobe:elevenlabs"),
    ("suno", "Suno", "suno", "wordmark", "lobe:suno"),
    ("udio", "Udio", "udio", "wordmark", "lobe:udio"),
    # ---- Altyapı / çıkarım ----
    ("groq", "Groq", "groq", "wordmark", "lobe:groq"),
    ("cerebras", "Cerebras", "cerebras", "wordmark", "lobe:cerebras"),
    ("sambanova", "SambaNova", "sambanova", "wordmark", "lobe:sambanova"),
    ("together", "Together AI", "together", "wordmark", "lobe:together"),
    ("fireworks", "Fireworks AI", "fireworks", "wordmark", "lobe:fireworks"),
    ("replicate", "Replicate", "replicate", "wordmark", "lobe:replicate"),
    ("openrouter", "OpenRouter", "openrouter", "wordmark", "lobe:openrouter"),
    ("ollama", "Ollama", "ollama", "wordmark", "lobe:ollama"),
    ("lmstudio", "LM Studio", "lmstudio", "wordmark", "lobe:lmstudio"),
    ("vercel", "Vercel", "vercel", "wordmark", "lobe:vercel"),
    ("cloudflare", "Cloudflare", "cloudflare", "wordmark", "lobe:cloudflare"),
    ("snowflake", "Snowflake", "snowflake", "wordmark", "lobe:snowflake"),
    ("ibm", "IBM", "ibm", "wordmark", "lobe:ibm"),
    # ---- Kodlama ajanları ----
    ("devin", "Devin", "cognition", "product", "lobe:devin"),
    ("windsurf", "Windsurf", "cognition", "product", "lobe:windsurf"),
    ("replit", "Replit", "replit", "wordmark", "lobe:replit"),
    ("lovable", "Lovable", "lovable", "wordmark", "lobe:lovable"),
    ("v0", "v0", "vercel", "product", "lobe:v0"),
    ("cline", "Cline", "cline", "product", "lobe:cline"),
    ("roo-code", "Roo Code", "roo-code", "product", "lobe:roocode"),
    ("kilo-code", "Kilo Code", "kilo-code", "product", "lobe:kilocode"),
    ("openhands", "OpenHands", "openhands", "product", "lobe:openhands"),
    ("amp", "Amp", "sourcegraph", "product", "lobe:amp"),
    ("opencode", "OpenCode", "opencode", "product", "lobe:opencode"),
    ("junie", "Junie", "jetbrains", "product", "lobe:junie"),
    ("kiro", "Kiro", "aws", "product", "lobe:kiro"),
    ("goose", "Goose", "block", "product", "lobe:goose"),
    # ---- Ajan / framework ----
    ("manus", "Manus", "manus", "product", "lobe:manus"),
    ("notion", "Notion", "notion", "wordmark", "lobe:notion"),
    ("langchain", "LangChain", "langchain", "wordmark", "lobe:langchain"),
    ("langgraph", "LangGraph", "langchain", "product", "lobe:langgraph"),
    ("llamaindex", "LlamaIndex", "llamaindex", "wordmark", "lobe:llamaindex"),
    ("n8n", "n8n", "n8n", "wordmark", "lobe:n8n"),
    ("crewai", "CrewAI", "crewai", "wordmark", "lobe:crewai"),
    ("dify", "Dify", "dify", "wordmark", "lobe:dify"),
    ("mcp", "Model Context Protocol", "anthropic", "product", "lobe:mcp"),
    ("gradio", "Gradio", "gradio", "wordmark", "lobe:gradio"),
    ("comfyui", "ComfyUI", "comfyui", "product", "lobe:comfyui"),
    ("openwebui", "Open WebUI", "openwebui", "product", "lobe:openwebui"),
    # ---- Diğer lablar ----
    ("sakana", "Sakana AI", "sakana", "wordmark", "lobe:sakana"),
    ("liquid", "Liquid AI", "liquid", "wordmark", "lobe:liquid"),
    ("ai2", "Ai2 (Allen Institute)", "ai2", "wordmark", "lobe:ai2"),
    ("reka", "Reka AI", "reka", "wordmark", "lobe:reka"),
    ("inflection", "Inflection AI", "inflection", "wordmark", "lobe:inflection"),
    ("ai21", "AI21 Labs", "ai21", "wordmark", "lobe:ai21"),
    ("aleph-alpha", "Aleph Alpha", "alephalpha", "wordmark", "lobe:alephalpha"),
    ("stepfun", "StepFun", "stepfun", "wordmark", "lobe:stepfun"),
    ("upstage", "Upstage", "upstage", "wordmark", "lobe:upstage"),
    ("baichuan", "Baichuan", "baichuan", "wordmark", "lobe:baichuan"),
    ("sensenova", "SenseNova", "sensenova", "wordmark", "lobe:sensenova"),
    ("poolside", "Poolside", "poolside", "wordmark", "lobe:poolside"),
    ("magic", "Magic", "magic", "wordmark", "lobe:magic"),
    # ---- Arama / veri ----
    ("exa", "Exa", "exa", "wordmark", "lobe:exa"),
    ("tavily", "Tavily", "tavily", "wordmark", "lobe:tavily"),
    ("jina", "Jina AI", "jina", "wordmark", "lobe:jina"),
    ("firecrawl", "Firecrawl", "firecrawl", "wordmark", "lobe:firecrawl"),
    ("brave", "Brave", "brave", "wordmark", "lobe:brave"),
    ("kagi", "Kagi", "kagi", "wordmark", "lobe:kagi"),
    ("assemblyai", "AssemblyAI", "assemblyai", "wordmark", "lobe:assemblyai"),
    ("fal", "fal.ai", "fal", "wordmark", "lobe:fal"),
    ("novita", "Novita AI", "novita", "wordmark", "lobe:novita"),
    ("hyperbolic", "Hyperbolic", "hyperbolic", "wordmark", "lobe:hyperbolic"),
    ("nebius", "Nebius", "nebius", "wordmark", "lobe:nebius"),
    ("baseten", "Baseten", "baseten", "wordmark", "lobe:baseten"),
    ("vllm", "vLLM", "vllm", "product", "lobe:vllm"),
    ("langfuse", "Langfuse", "langfuse", "wordmark", "lobe:langfuse"),
    ("wandb", "Weights & Biases", "wandb", "wordmark", "lobe:wandb"),
]


def main():
    out, missing, seen = [], [], set()
    for slug, name, brand, kind, src in T:
        if slug in seen:
            print("MÜKERRER:", slug); continue
        seen.add(slug)
        if not src.startswith("lobe"):
            out.append({"slug": slug, "name": name, "brand": brand, "kind": kind, "src": src}); continue
        val = src.split(":", 1)[1]
        pref = "lobe-text" if src.startswith("lobe-text") else "lobe"
        cands = [f"{val}-text.svg"] if pref == "lobe-text" else [f"{val}-color.svg", f"{val}.svg"]
        if not any((LOBE / c).exists() for c in cands):
            missing.append((slug, val))
        out.append({"slug": slug, "name": name, "brand": brand, "kind": kind, "src": src})
    Path("tools/logo_catalog.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"{len(out)} kayıt yazıldı")
    if missing:
        print(f"EKSİK ({len(missing)}):", ", ".join(f"{s}({v})" for s, v in missing))


if __name__ == "__main__":
    main()
