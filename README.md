# GitHub Stars Organizer

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/nishal21/github-stars-organizer/actions/workflows/ci.yml/badge.svg)](https://github.com/nishal21/github-stars-organizer/actions/workflows/ci.yml)

**Organize 300+ GitHub stars into lists in minutes — free, no AI required.**

GitHub's official API can star/unstar repos, but **cannot create or manage Star Lists**. This CLI:

1. Fetches your starred repos (public GitHub API)
2. Categorizes them by name, description, language, and topics
3. Creates lists and assigns repos via your browser session

### Why this tool?

| Tool | Drawback | This project |
|------|----------|--------------|
| [github-star-organizer](https://github.com/luoling8192/github-star-organizer) | Requires paid LLM API | **Free heuristic by default** |
| [ghstars](https://github.com/snowfluke/github-manage-stars-unofficial) | Manual category files only | **Auto-plan + custom rules + optional LLM** |
| [starred](https://github.com/amirhmoradi/starred) | AI-first, complex | **Simple: plan → review → apply** |

## Install

```bash
# From source
git clone https://github.com/nishal21/github-stars-organizer.git
cd github-stars-organizer
uv sync

# Or from PyPI (after v0.2.0 release)
pip install github-stars-organizer
```

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/) (recommended).

**Windows note:** If `pip install` says scripts are not on PATH, either add  
`%APPDATA%\Python\Python313\Scripts` to your PATH, or run:

```bash
python -m stars_organizer init
```

From the project folder you can also use: `uv run organize-stars init`

## Quick start

### 1. Build a plan (no credentials needed)

```bash
organize-stars plan --username YOUR_USERNAME
```

Review `categorization-plan.json`. Edit assignments or add custom rules:

```bash
cp categories.example.toml categories.toml
# edit categories.toml
organize-stars plan --username YOUR_USERNAME --categories categories.toml
```

### 2. Configure credentials

```bash
organize-stars init
```

Or copy and edit manually:

```bash
cp config.example.toml config.toml
```

| Field | How to get it |
|-------|----------------|
| `username` | Your GitHub username |
| `token` | [GitHub token settings](https://github.com/settings/tokens) (classic; `public_repo` if you star private repos) |
| `cookies` | See [Getting your cookie](#getting-your-browser-cookie) below |

### 3. Preview and apply

```bash
organize-stars apply --dry-run
organize-stars apply
```

View result: `https://github.com/YOUR_USERNAME?tab=stars`

If interrupted, resume with:

```bash
organize-stars apply --resume
```

## Getting your browser cookie

GitHub Star Lists have no public API — applying lists uses your browser session.

1. Log into [github.com](https://github.com) in Chrome or Edge
2. Press **F12** to open DevTools
3. Open the **Network** tab
4. Refresh the page
5. Click any request to `github.com`
6. Under **Headers**, find **Cookie**
7. Copy the **entire** cookie string into `config.toml` → `[github.session]` → `cookies`

Cookies expire every few weeks. Refresh from DevTools if you get CSRF or 403 errors.

## CLI reference

```bash
organize-stars init [--config config.toml] [--force]
organize-stars status [--config config.toml]
organize-stars lists [--config config.toml]

organize-stars plan --username USER [--categories categories.toml] [--output plan.json]
organize-stars plan --config config.toml [--categories categories.toml]
organize-stars plan --config config.toml --llm          # optional AI mode

organize-stars apply [--config config.toml] [--plan plan.json] [--dry-run] [--yes] [--resume]
```

## Optional AI mode (multi-provider)

Install the LLM extra:

```bash
uv sync --extra llm
organize-stars providers    # list all supported providers
```

Add to `config.toml` (see `config.example.toml`):

```toml
[llm]
provider = "mistral"
preferences = "I'm a web designer, gamer, and anime fan."

[llm.providers.mistral]
api_key = "your-mistral-key"

[llm.providers.openai]
api_key = "sk-..."

[llm.providers.groq]
api_key = "gsk_..."
```

Supported providers: **openai**, **mistral**, **groq**, **openrouter**, **google**, **deepseek**, **together**, **fireworks**, **cerebras**.

API keys can also be set via env vars (`MISTRAL_API_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`, etc.).

```bash
organize-stars plan --config config.toml --llm
organize-stars plan --config config.toml --llm --provider groq
```

Heuristic mode (no API key) remains the default without `--llm`.

## Default categories

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

Customize via `categories.toml` or edit the plan JSON before applying.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| CSRF / 403 error | Refresh browser cookie in `config.toml` |
| Rate limited | Wait a few minutes; reduce `concurrency` in config |
| More than 32 lists | GitHub hard limit — merge categories in plan or `categories.toml` |
| Apply interrupted | Run `organize-stars apply --resume` |
| `config.toml not found` | Run `organize-stars init` |

Check setup anytime:

```bash
organize-stars status
```

## Privacy and security

- Token and cookies stay in local `config.toml` (gitignored) — never commit them
- Plan mode reads only **public** repo metadata
- LLM mode (optional) sends metadata to your configured provider
- See [SECURITY.md](SECURITY.md)

## Development

```bash
uv sync --dev
uv run pytest
uv run ruff check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Attribution

Web client adapted from [luoling8192/github-star-organizer](https://github.com/luoling8192/github-star-organizer) (MIT). See [ATTRIBUTION.md](ATTRIBUTION.md).

## License

MIT — see [LICENSE](LICENSE).
