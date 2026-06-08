# GitHub Stars Organizer

Organize your GitHub starred repositories into **Star Lists** automatically — no LLM or paid API required.

GitHub's official API can star/unstar repos, but **cannot create or manage Star Lists**. This tool:

1. Fetches your starred repos (public API)
2. Categorizes them by name, description, language, and topics
3. Creates lists and assigns repos via GitHub's web session (browser cookie)

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- GitHub personal access token
- Browser session cookie from github.com (for applying lists)

## Install

```bash
git clone https://github.com/YOUR_USERNAME/github-stars-organizer.git
cd github-stars-organizer
uv sync
```

## Quick start

### 1. Create a categorization plan

For any public GitHub user (no auth required):

```bash
uv run organize-stars plan --username YOUR_USERNAME
```

Or using your config:

```bash
cp config.example.toml config.toml
# edit config.toml
uv run organize-stars plan --config config.toml
```

This writes `categorization-plan.json` with suggested lists. Review and edit before applying.

### 2. Configure credentials (apply only)

```bash
cp config.example.toml config.toml
```

Edit `config.toml`:

| Field | How to get it |
|-------|----------------|
| `username` | Your GitHub username |
| `token` | [Settings → Developer settings → Tokens](https://github.com/settings/tokens) (classic token; `public_repo` if you star private repos) |
| `cookies` | Log into GitHub → F12 → Network → refresh → click any `github.com` request → copy full **Cookie** header |

### 3. Preview, then apply

```bash
# Preview — no changes
uv run organize-stars apply --dry-run

# Apply — creates lists and assigns repos
uv run organize-stars apply
```

View result: `https://github.com/YOUR_USERNAME?tab=stars`

## CLI reference

```bash
organize-stars plan --username USER [--output plan.json] [--token TOKEN]
organize-stars plan --config config.toml [--output plan.json]
organize-stars apply [--config config.toml] [--plan plan.json] [--dry-run] [--yes]
```

Equivalent module form:

```bash
uv run python -m stars_organizer plan --username USER
uv run python -m stars_organizer apply --dry-run
```

## Default categories

Repos are sorted into broad lists (max ~12 categories):

- AI & LLM
- Web Dev & Frontend
- Mobile & Android
- Backend & APIs
- Dev Tools & CLI
- Self-hosting & DevOps
- Security & Privacy
- Media & Creative
- Gaming & Entertainment
- Go & Systems
- Learning & Inspiration
- Misc & Tools

Edit `src/stars_organizer/categorize.py` to customize rules, or hand-edit `categorization-plan.json` before applying.

## Plan file format

See `examples/plan.example.json`. Each repo maps to exactly one list name.

## Privacy & security

- **Token** and **cookies** stay in local `config.toml` (gitignored). Never commit them.
- Plan generation only reads **public** repo metadata (name, description, language, topics).
- Applying lists uses your browser session cookie — same access as if you clicked in the GitHub UI.
- Cookies expire periodically; refresh from DevTools if you get CSRF or 403 errors.

## Limitations

- GitHub allows roughly **32 Star Lists** per user — categories are kept broad on purpose.
- List management uses **unofficial** web endpoints (no public GitHub API exists).
- Rate limiting: ~1 second delay between list operations to avoid throttling.

## Attribution

Web client code adapted from [luoling8192/github-star-organizer](https://github.com/luoling8192/github-star-organizer) (MIT). See [ATTRIBUTION.md](ATTRIBUTION.md).

## License

MIT — see [LICENSE](LICENSE).
