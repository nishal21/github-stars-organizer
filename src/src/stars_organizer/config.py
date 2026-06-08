import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitHubConfig:
    username: str
    token: str
    cookies: str


@dataclass
class LLMConfig:
    base_url: str
    api_key: str
    model: str
    concurrency: int = 3


@dataclass
class Config:
    github: GitHubConfig
    concurrency: int = 5
    llm: LLMConfig | None = None


def load_config(path: Path | None = None) -> Config:
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
        llm = raw["llm"]
        llm_cfg = LLMConfig(
            base_url=llm.get("base_url", "https://api.openai.com/v1"),
            api_key=llm["api_key"],
            model=llm.get("model", "gpt-4o"),
            concurrency=int(llm.get("concurrency", 3)),
        )

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
        }

    cfg = load_config(path)
    return {
        "exists": True,
        "username": cfg.github.username,
        "has_token": bool(cfg.github.token and cfg.github.token != "ghp_xxxx"),
        "has_cookies": bool(cfg.github.cookies and "user_session" in cfg.github.cookies),
        "has_llm": cfg.llm is not None,
    }
