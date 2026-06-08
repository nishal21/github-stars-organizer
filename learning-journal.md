# Learning Journal

## GitHub Star Lists

- Profile → **Stars** tab; ~32 lists max per user
- Official REST API: star/unstar only — **no lists API**
- Lists need browser cookie + CSRF (unofficial web endpoints)

## This tool (OSS)

| Command | Purpose |
|---------|---------|
| `organize-stars plan --username X` | Fetch public stars → `categorization-plan.json` |
| `organize-stars apply --dry-run` | Preview list creation |
| `organize-stars apply` | Create lists + assign repos on GitHub |

| File | Purpose |
|------|---------|
| `config.toml` | username, token, cookies (local, gitignored) |
| `categorization-plan.json` | repo → list mapping (generated, gitignored) |
| `src/stars_organizer/categorize.py` | keyword scoring rules |
| `src/stars_organizer/github_web.py` | adapted from luoling8192 (MIT) |

## Publish checklist

1. Create repo on GitHub (e.g. `nishal21/github-stars-organizer`)
2. `git add . && git commit -m "Initial release"`
3. `git remote add origin git@github.com:USER/REPO.git`
4. `git push -u origin main`

## Cookie refresh

CSRF/403 on apply → DevTools → Network → copy fresh Cookie from github.com.
