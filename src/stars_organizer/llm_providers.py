"""LLM provider presets and configuration resolution."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderPreset:
    name: str
    base_url: str
    default_model: str
    env_key: str
    docs_url: str


PROVIDERS: dict[str, ProviderPreset] = {
    "openai": ProviderPreset(
        name="openai",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o",
        env_key="OPENAI_API_KEY",
        docs_url="https://platform.openai.com/api-keys",
    ),
    "mistral": ProviderPreset(
        name="mistral",
        base_url="https://api.mistral.ai/v1",
        default_model="mistral-large-latest",
        env_key="MISTRAL_API_KEY",
        docs_url="https://console.mistral.ai/api-keys",
    ),
    "groq": ProviderPreset(
        name="groq",
        base_url="https://api.groq.com/openai/v1",
        default_model="llama-3.3-70b-versatile",
        env_key="GROQ_API_KEY",
        docs_url="https://console.groq.com/keys",
    ),
    "openrouter": ProviderPreset(
        name="openrouter",
        base_url="https://openrouter.ai/api/v1",
        default_model="openai/gpt-4o",
        env_key="OPENROUTER_API_KEY",
        docs_url="https://openrouter.ai/keys",
    ),
    "google": ProviderPreset(
        name="google",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        default_model="gemini-2.0-flash",
        env_key="GOOGLE_API_KEY",
        docs_url="https://aistudio.google.com/apikey",
    ),
    "deepseek": ProviderPreset(
        name="deepseek",
        base_url="https://api.deepseek.com/v1",
        default_model="deepseek-chat",
        env_key="DEEPSEEK_API_KEY",
        docs_url="https://platform.deepseek.com/api_keys",
    ),
    "together": ProviderPreset(
        name="together",
        base_url="https://api.together.xyz/v1",
        default_model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        env_key="TOGETHER_API_KEY",
        docs_url="https://api.together.xyz/settings/api-keys",
    ),
    "fireworks": ProviderPreset(
        name="fireworks",
        base_url="https://api.fireworks.ai/inference/v1",
        default_model="accounts/fireworks/models/llama-v3p3-70b-instruct",
        env_key="FIREWORKS_API_KEY",
        docs_url="https://fireworks.ai/account/api-keys",
    ),
    "cerebras": ProviderPreset(
        name="cerebras",
        base_url="https://api.cerebras.ai/v1",
        default_model="llama-3.3-70b",
        env_key="CEREBRAS_API_KEY",
        docs_url="https://cloud.cerebras.ai/",
    ),
}


def list_providers() -> list[ProviderPreset]:
    return list(PROVIDERS.values())


def get_provider(name: str) -> ProviderPreset:
    key = name.lower().strip()
    if key not in PROVIDERS:
        known = ", ".join(sorted(PROVIDERS))
        raise ValueError(f"Unknown provider '{name}'. Supported: {known}")
    return PROVIDERS[key]


def resolve_api_key(
    provider: str,
    llm_section: dict,
    explicit_key: str | None = None,
) -> str:
    if explicit_key:
        return explicit_key

    if api_key := llm_section.get("api_key"):
        if api_key and not str(api_key).startswith("xxxx"):
            return str(api_key)

    providers_section = llm_section.get("providers", {})
    if isinstance(providers_section, dict):
        provider_cfg = providers_section.get(provider, {})
        if isinstance(provider_cfg, dict) and provider_cfg.get("api_key"):
            return str(provider_cfg["api_key"])

    preset = get_provider(provider)
    env_value = os.environ.get(preset.env_key)
    if env_value:
        return env_value

    raise ValueError(
        f"No API key for provider '{provider}'. "
        f"Set [llm.providers.{provider}] api_key, [llm] api_key, or env {preset.env_key}. "
        f"Get a key: {preset.docs_url}"
    )


def resolve_model(provider: str, llm_section: dict, explicit_model: str | None = None) -> str:
    if explicit_model:
        return explicit_model

    if model := llm_section.get("model"):
        return str(model)

    providers_section = llm_section.get("providers", {})
    if isinstance(providers_section, dict):
        provider_cfg = providers_section.get(provider, {})
        if isinstance(provider_cfg, dict) and provider_cfg.get("model"):
            return str(provider_cfg["model"])

    return get_provider(provider).default_model


def resolve_base_url(provider: str, llm_section: dict, explicit_url: str | None = None) -> str:
    if explicit_url:
        return explicit_url

    if base_url := llm_section.get("base_url"):
        return str(base_url)

    providers_section = llm_section.get("providers", {})
    if isinstance(providers_section, dict):
        provider_cfg = providers_section.get(provider, {})
        if isinstance(provider_cfg, dict) and provider_cfg.get("base_url"):
            return str(provider_cfg["base_url"])

    return get_provider(provider).base_url
