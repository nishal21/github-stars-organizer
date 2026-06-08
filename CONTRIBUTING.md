# Contributing

Thanks for helping improve GitHub Stars Organizer!

## Development setup

```bash
git clone https://github.com/nishal21/github-stars-organizer.git
cd github-stars-organizer
uv sync --dev
```

## Run tests

```bash
uv run pytest
uv run ruff check .
```

## Adding category rules

**Default rules:** edit [`src/stars_organizer/categorize.py`](src/stars_organizer/categorize.py)

**User-facing rules:** add patterns to `categories.toml` (see [`categories.example.toml`](categories.example.toml))

Add a test case in [`tests/test_categorize.py`](tests/test_categorize.py) for new default rules.

## Pull requests

1. Fork and create a feature branch
2. Keep changes focused
3. Ensure CI passes (`pytest` + `ruff`)
4. Update [`CHANGELOG.md`](CHANGELOG.md) for user-visible changes

## Reporting issues

Use the bug report or feature request templates on GitHub Issues.
