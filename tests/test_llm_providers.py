import pytest

from stars_organizer.llm_providers import (
    get_provider,
    list_providers,
    resolve_api_key,
    resolve_model,
)


def test_list_providers_includes_mistral():
    names = {p.name for p in list_providers()}
    assert "mistral" in names
    assert "openai" in names
    assert "groq" in names


def test_get_provider_mistral_defaults():
    preset = get_provider("mistral")
    assert preset.base_url == "https://api.mistral.ai/v1"
    assert preset.default_model == "mistral-large-latest"


def test_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("not-a-provider")


def test_resolve_api_key_from_providers_section():
    llm = {
        "provider": "mistral",
        "providers": {"mistral": {"api_key": "test-mistral-key"}},
    }
    assert resolve_api_key("mistral", llm) == "test-mistral-key"


def test_resolve_api_key_from_env(monkeypatch):
    monkeypatch.setenv("MISTRAL_API_KEY", "env-mistral-key")
    assert resolve_api_key("mistral", {}) == "env-mistral-key"


def test_resolve_model_override():
    llm = {
        "providers": {"groq": {"model": "llama-3.1-8b-instant"}},
    }
    assert resolve_model("groq", llm) == "llama-3.1-8b-instant"


def test_resolve_model_default():
    assert resolve_model("mistral", {}) == "mistral-large-latest"
