# Publishing guide

## GitHub repository

```bash
cd github-stars-organizer
git branch -M main
git add .
git commit -m "Initial release v0.2.0"
gh repo create nishal21/github-stars-organizer --public --source=. --remote=origin --push
```

Add topics on GitHub: `github`, `cli`, `python`, `stars`, `productivity`, `open-source`

## Dogfood (organize your stars)

```bash
# If `organize-stars` is not found on Windows after pip install, use:
python -m stars_organizer init
python -m stars_organizer plan --username nishal21
python -m stars_organizer apply --dry-run
python -m stars_organizer apply

# Or from this repo with uv:
uv run organize-stars init
```

Screenshot https://github.com/nishal21?tab=stars and add to README.

## PyPI release

1. Create account at https://pypi.org
2. Create API token
3. Add `PYPI_API_TOKEN` secret to GitHub repo settings
4. Tag and push:

```bash
git tag v0.2.0
git push origin v0.2.0
```

The release workflow publishes automatically.

Manual publish:

```bash
uv build
uv publish --token $PYPI_API_TOKEN
```
