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
3. Add `PYPI_API_TOKEN` secret to GitHub repo → Settings → Secrets → Actions
4. Bump version in `pyproject.toml` (PyPI **never** allows re-uploading the same version)
5. Tag and push:

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Release v0.2.1"
git tag v0.2.1
git push origin main
git push origin v0.2.1
```

The release workflow publishes automatically. Re-running an existing tag is safe (`skip-existing: true`).

**If you see `400 File already exists`:** version `0.2.0` is already on PyPI — bump to `0.2.1` (or higher) and push a new tag.

### Trusted Publishing (optional, no API token)

PyPI suggested Trusted Publishing — configure at:
https://pypi.org/manage/project/github-stars-organizer/settings/publishing/

Then remove `password:` from `release.yml` and use OIDC instead.
