# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| < 0.2   | No        |

## Reporting a vulnerability

Email or open a **private** security advisory on GitHub if you find a security issue.

Please do **not** open public issues for credential-handling bugs.

## Credential handling

- `config.toml` contains your GitHub token and browser session cookie — **never commit it**
- Cookies grant the same access as your logged-in GitHub session
- Use a token with minimal scopes (`public_repo` only if needed)
- Refresh cookies if you suspect exposure; revoke tokens at https://github.com/settings/tokens

## What this tool sends externally

- **Plan mode:** public GitHub API only (repo name, description, language, topics)
- **LLM mode (optional):** repo metadata sent to your configured LLM provider
- **Apply mode:** unofficial GitHub web endpoints using your local session
