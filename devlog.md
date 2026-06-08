# Devlog

## 2026-06-08 — v0.2.2 multi-provider AI

- Added 9 LLM providers: OpenAI, Mistral, Groq, OpenRouter, Google, DeepSeek, Together, Fireworks, Cerebras
- `[llm.providers.*]` blocks for multiple API keys; env var fallback per provider
- `organize-stars providers`, `--provider` flag, `[llm] preferences`

**User setup (Mistral):** Add `[llm] provider = "mistral"` + `[llm.providers.mistral] api_key` → `organize-stars plan --config config.toml --llm`
