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
organize-stars init
organize-stars plan --username nishal21
organize-stars apply --dry-run
organize-stars apply
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
