import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .llm_providers import get_provider, resolve_api_key, resolve_base_url, resolve_model


@dataclass
class GitHubConfig:
    username: str
    token: str
    cookies: str


@dataclass
class LLMConfig:
    provider: str
    base_url: str
    api_key: str
    model: str
    concurrency: int = 3
    preferences: str = ""


@dataclass
class Config:
    github: GitHubConfig
    concurrency: int = 5
    llm: LLMConfig | None = None


def load_llm_config(
    llm_section: dict,
    *,
    provider_override: str | None = None,
) -> LLMConfig:
    provider = (provider_override or llm_section.get("provider") or "openai").lower().strip()
    get_provider(provider)  # validate

    return LLMConfig(
        provider=provider,
        base_url=resolve_base_url(provider, llm_section),
        api_key=resolve_api_key(provider, llm_section),
        model=resolve_model(provider, llm_section),
        concurrency=int(llm_section.get("concurrency", 3)),
        preferences=str(llm_section.get("preferences", "")).strip(),
    )


def load_config(
    path: Path | None = None,
    *,
    llm_provider: str | None = None,
) -> Config:
    if path is None:
        path = Path("config.toml")

    if not path.exists():
        print(f"Config file not found: {path}")
        print("Copy config.example.toml to config.toml and fill in your credentials.")
        print("Or run: organize-stars init")
        sys.exit(1)

    with open(path, "rb") as f:
        raw = tomllib.load(f)

    gh = raw["github"]
    session = gh.get("session", gh)

    llm_cfg = None
    if "llm" in raw:
        try:
            llm_cfg = load_llm_config(raw["llm"], provider_override=llm_provider)
        except ValueError as exc:
            print(f"[red]LLM config error:[/red] {exc}")
            sys.exit(1)

    return Config(
        github=GitHubConfig(
            username=gh["username"],
            token=gh["token"],
            cookies=session["cookies"],
        ),
        concurrency=int(raw.get("concurrency", 5)),
        llm=llm_cfg,
    )


def config_status(path: Path) -> dict[str, bool | str]:
    if not path.exists():
        return {
            "exists": False,
            "username": "",
            "has_token": False,
            "has_cookies": False,
            "has_llm": False,
            "llm_provider": "",
            "llm_model": "",
        }

    with open(path, "rb") as f:
        raw = tomllib.load(f)

    llm_provider = ""
    llm_model = ""
    has_llm = "llm" in raw
    if has_llm:
        llm = raw["llm"]
        llm_provider = str(llm.get("provider", "openai"))
        try:
            llm_model = resolve_model(llm_provider, llm)
        except ValueError:
            llm_model = str(llm.get("model", ""))

    gh = raw["github"]
    session = gh.get("session", gh)
    return {
        "exists": True,
        "username": gh["username"],
        "has_token": bool(gh.get("token") and gh["token"] != "ghp_xxxx"),
        "has_cookies": bool(session.get("cookies") and "user_session" in session["cookies"]),
        "has_llm": has_llm,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
    }
