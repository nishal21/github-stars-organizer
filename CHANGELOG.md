# Changelog

## [0.2.0] - 2026-06-08

### Added

- `organize-stars init` — interactive config setup
- `organize-stars status` — config and resume state check
- `organize-stars lists` — show current Star Lists
- `organize-stars plan --categories` — custom `categories.toml` rules
- `organize-stars plan --llm` — optional AI categorization (`uv sync --extra llm`)
- `organize-stars apply --resume` — checkpoint resume via `.organize-stars-state.json`
- Rich progress bar during apply
- PyPI publish workflow on version tags

### Fixed

- Removed Python → AI & LLM language bias
- Language hints used as tie-breakers only
- Pre-apply guard when plan exceeds GitHub's 32-list limit

## [0.1.0] - 2026-06-08

### Added

- `organize-stars plan` — fetch stars and build categorization plan
- `organize-stars apply` — create Star Lists and assign repos
- Heuristic categorization (no LLM required)
- MIT license, tests, CI
