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
class Config:
    github: GitHubConfig
    concurrency: int = 5


def load_config(path: Path | None = None) -> Config:
    if path is None:
        path = Path("config.toml")

    if not path.exists():
        print(f"Config file not found: {path}")
        print("Copy config.example.toml to config.toml and fill in your credentials.")
        sys.exit(1)

    with open(path, "rb") as f:
        raw = tomllib.load(f)

    gh = raw["github"]
    session = gh.get("session", gh)

    return Config(
        github=GitHubConfig(
            username=gh["username"],
            token=gh["token"],
            cookies=session["cookies"],
        ),
        concurrency=raw.get("concurrency", 5),
    )
