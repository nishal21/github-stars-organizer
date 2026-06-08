from collections.abc import Callable

import httpx

from .config import GitHubConfig
from .models import StarredRepo


def _parse_repo(item: dict) -> StarredRepo:
    return StarredRepo(
        id=item["id"],
        full_name=item["full_name"],
        description=item.get("description") or "",
        language=item.get("language") or "",
        topics=item.get("topics") or [],
        html_url=item["html_url"],
    )


async def _fetch_pages(
    url: str,
    headers: dict[str, str],
    on_page: Callable[[int, int], None] | None = None,
) -> list[StarredRepo]:
    repos: list[StarredRepo] = []
    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        page = 1
        while True:
            resp = await client.get(url, params={"per_page": "100", "page": str(page)})
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break

            for item in data:
                repos.append(_parse_repo(item))

            if on_page:
                on_page(page, len(repos))

            if 'rel="next"' not in resp.headers.get("link", ""):
                break
            page += 1
    return repos


async def fetch_starred_repos(
    cfg: GitHubConfig,
    on_page: Callable[[int, int], None] | None = None,
) -> list[StarredRepo]:
    """Fetch starred repos for the authenticated user (token required)."""
    headers = {
        "Authorization": f"Bearer {cfg.token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-stars-organizer",
    }
    return await _fetch_pages("https://api.github.com/user/starred", headers, on_page)


async def fetch_public_starred_repos(
    username: str,
    token: str | None = None,
    on_page: Callable[[int, int], None] | None = None,
) -> list[StarredRepo]:
    """Fetch public starred repos for any GitHub user."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-stars-organizer",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return await _fetch_pages(
        f"https://api.github.com/users/{username}/starred",
        headers,
        on_page,
    )
