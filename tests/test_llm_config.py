from stars_organizer.config import load_llm_config


def test_load_llm_config_mistral(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text(
        """
[llm]
provider = "mistral"
preferences = "anime and gaming"

[llm.providers.mistral]
api_key = "mistral-test-key"
model = "mistral-small-latest"
""",
        encoding="utf-8",
    )

    import tomllib

    with open(config, "rb") as f:
        raw = tomllib.load(f)

    llm = load_llm_config(raw["llm"])
    assert llm.provider == "mistral"
    assert llm.api_key == "mistral-test-key"
    assert llm.model == "mistral-small-latest"
    assert llm.preferences == "anime and gaming"
    assert llm.base_url == "https://api.mistral.ai/v1"
