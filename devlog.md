# Devlog

## 2026-06-08 — OSS refactor

- Restructured into publishable package: `src/stars_organizer/`
- CLI: `organize-stars plan|apply` (no LLM, no hardcoded username)
- Vendored `github_web.py` from luoling8192/github-star-organizer (MIT, see ATTRIBUTION.md)
- Added README, LICENSE, .gitignore, examples/plan.example.json
- User plan (`categorization-plan.json`) and `config.toml` gitignored
- Removed legacy `tool/` clone and `apply_plan.py`

**Next for nishal21:** `cp config.example.toml config.toml` → paste token + cookie → `uv run organize-stars apply --dry-run` → `uv run organize-stars apply`

**Next to publish:** `git init` (done locally), create GitHub repo, `git remote add origin ...`, `git push -u origin main`

**Path:** `C:\Users\hp\github-stars-organizer`
