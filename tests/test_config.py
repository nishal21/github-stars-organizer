import sys

import pytest

from stars_organizer.config import load_config


def test_missing_config_exits(tmp_path, monkeypatch):
    missing = tmp_path / "missing.toml"
    monkeypatch.setattr(sys, "exit", lambda code: (_ for _ in ()).throw(SystemExit(code)))
    with pytest.raises(SystemExit) as exc:
        load_config(missing)
    assert exc.value.code == 1


def test_load_config_parses_github_section(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text(
        """
[github]
username = "testuser"
token = "ghp_test"

[github.session]
cookies = "logged_in=yes; user_session=abc"
""",
        encoding="utf-8",
    )
    cfg = load_config(config)
    assert cfg.github.username == "testuser"
    assert cfg.github.token == "ghp_test"
    assert "user_session" in cfg.github.cookies
