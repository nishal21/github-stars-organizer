# Portions adapted from github-star-organizer (MIT)
# https://github.com/luoling8192/github-star-organizer
# Copyright (c) luoling8192

import asyncio
import re

import httpx
from bs4 import BeautifulSoup
from rich.console import Console

from .config import GitHubConfig
from .models import StarList, StarredRepo

console = Console()

_debug = False

_BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://github.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

_SKIP_CURL_HEADERS = {"host", "content-length", "transfer-encoding", "content-type"}


def enable_debug() -> None:
    global _debug
    _debug = True


def _build_cookies(cfg: GitHubConfig) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for pair in cfg.cookies.split(";"):
        pair = pair.strip()
        if "=" in pair:
            k, v = pair.split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies


def _to_curl(
    method: str,
    url: str,
    headers: dict[str, str],
    cookies: dict[str, str],
    *,
    data: dict[str, str] | None = None,
    files: dict[str, tuple[None, str]] | list[tuple[str, tuple[None, str]]] | None = None,
) -> str:
    parts = [f"curl --location '{url}'"]

    for k, v in headers.items():
        if k.lower() in _SKIP_CURL_HEADERS:
            continue
        parts.append(f"--header '{k}: {v}'")

    cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
    if cookie_str:
        parts.append(f"--header 'Cookie: {cookie_str}'")

    if data is not None:
        for name, value in data.items():
            escaped = value.replace("'", "'\\''")
            parts.append(f"--data-urlencode '{name}={escaped}'")

    if files is not None:
        items: list[tuple[str, str]] = []
        if isinstance(files, dict):
            items = [(k, v[1]) for k, v in files.items()]
        else:
            items = [(k, v[1]) for k, v in files]
        for name, value in items:
            escaped = value.replace("'", "'\\''")
            parts.append(f"--form '{name}=\"{escaped}\"'")

    return " \\\n  ".join(parts)


def _debug_dump(
    label: str,
    resp: httpx.Response,
    *,
    curl_cmd: str | None = None,
) -> None:
    if not _debug:
        return

    console.print(f"\n[bold red]{'=' * 60}[/bold red]")
    console.print(f"[bold red]DEBUG: {label}[/bold red]")
    console.print(f"[bold]Status:[/bold] {resp.status_code}")
    console.print(f"[bold]URL:[/bold] {resp.request.method} {resp.request.url}")

    console.print("\n[bold]Response Headers:[/bold]")
    for k, v in resp.headers.items():
        console.print(f"  {k}: {v}")

    console.print("\n[bold]Response Body:[/bold]")
    body = resp.text
    if len(body) > 2000:
        console.print(body[:2000])
        console.print(f"[dim]... truncated ({len(body)} chars total)[/dim]")
    else:
        console.print(body)

    if curl_cmd:
        console.print("\n[bold]Curl command to reproduce:[/bold]")
        console.print(f"[green]{curl_cmd}[/green]")

    console.print(f"[bold red]{'=' * 60}[/bold red]\n")


def _normalize_list_name(name: str) -> str:
    name = re.sub(r"\s*\d+\s*repositor(?:y|ies)\s*$", "", name, flags=re.I)
    return name.strip()


def _parse_lists_from_buttons(soup: BeautifulSoup) -> list[StarList]:
    """Parse GitHub's modern ActionList button UI for list IDs."""
    lists: list[StarList] = []
    seen: set[str] = set()

    for btn in soup.find_all("button", attrs={"data-input-name": "list_ids[]"}):
        list_id = btn.get("data-value", "")
        if not list_id or not str(list_id).isdigit():
            continue
        if list_id in seen:
            continue

        label = btn.find("span", class_="ActionListItem-label")
        name = label.get_text(" ", strip=True) if label else btn.get_text(" ", strip=True)
        name = _normalize_list_name(name)
        if name:
            lists.append(StarList(id=str(list_id), name=name))
            seen.add(list_id)

    return lists


def _parse_lists_from_checkboxes(soup: BeautifulSoup) -> list[StarList]:
    """Legacy checkbox UI fallback."""
    lists: list[StarList] = []
    for checkbox in soup.find_all("input", {"type": "checkbox", "name": "list_ids[]"}):
        list_id = checkbox.get("value", "")
        if not list_id:
            continue
        label = checkbox.find_parent("label") or checkbox.find_next("label")
        name = ""
        if label:
            truncate = label.find(class_="Truncate-text")
            name = truncate.get_text(strip=True) if truncate else label.get_text(strip=True)
        name = _normalize_list_name(name)
        if name:
            lists.append(StarList(id=str(list_id), name=name))
    return lists


def _parse_lists_from_html(html: str) -> list[StarList]:
    soup = BeautifulSoup(html, "html.parser")
    lists = _parse_lists_from_buttons(soup)
    if lists:
        return lists
    return _parse_lists_from_checkboxes(soup)


def _parse_profile_list_links(html: str, username: str) -> list[StarList]:
    """Parse list names from the profile stars tab (no numeric IDs)."""
    soup = BeautifulSoup(html, "html.parser")
    pattern = re.compile(rf"^/stars/{re.escape(username)}/lists/([^/?#]+)$")
    found: dict[str, StarList] = {}

    for link in soup.find_all("a", href=True):
        match = pattern.match(link["href"])
        if not match:
            continue
        slug = match.group(1)
        if slug in {"new", "edit"}:
            continue
        name = _normalize_list_name(link.get_text(strip=True) or slug)
        if slug not in found:
            found[slug] = StarList(id=slug, name=name)

    return sorted(found.values(), key=lambda item: item.name.lower())


def _merge_lists_by_name(id_lists: list[StarList], name_lists: list[StarList]) -> list[StarList]:
    """Combine ID-bearing lists with profile lists, matching by name."""
    by_name = {item.name.lower(): item for item in id_lists}
    merged = list(id_lists)

    for item in name_lists:
        key = item.name.lower()
        if key not in by_name:
            merged.append(item)

    return sorted(merged, key=lambda item: item.name.lower())


def _extract_csrf_token(html: str, action_url: str | None = None) -> str:
    soup = BeautifulSoup(html, "html.parser")

    if action_url:
        form = soup.find("form", {"action": action_url})
        if form:
            token = form.find("input", {"name": "authenticity_token"})
            if token and token.get("value"):
                return token["value"]

    token_input = soup.find("input", {"name": "authenticity_token"})
    if token_input and token_input.get("value"):
        return token_input["value"]
    raise ValueError("Could not find CSRF token. Session cookie may be expired.")


async def fetch_profile_star_lists(
    client: httpx.AsyncClient,
    cfg: GitHubConfig,
) -> list[StarList]:
    """Fetch list names from the user's stars profile page."""
    url = (
        f"https://github.com/{cfg.username}?tab=stars"
        "&user_lists_direction=desc&user_lists_sort=created_at"
    )
    headers = {
        **_BROWSER_HEADERS,
        "Accept": "text/html, application/xhtml+xml",
        "Turbo-Frame": "user-profile-frame",
        "Referer": f"https://github.com/{cfg.username}?tab=stars",
    }
    cookies = _build_cookies(cfg)

    resp = await client.get(url, headers=headers, cookies=cookies, follow_redirects=True)
    if resp.status_code != 200:
        curl = _to_curl("GET", url, headers, cookies)
        _debug_dump("fetch_profile_star_lists failed", resp, curl_cmd=curl)
        return []

    return _parse_profile_list_links(resp.text, cfg.username)


async def fetch_star_lists(
    client: httpx.AsyncClient,
    cfg: GitHubConfig,
    repo: StarredRepo,
) -> tuple[list[StarList], str]:
    url = f"https://github.com/{repo.full_name}/lists?experimental=1"
    headers = {
        **_BROWSER_HEADERS,
        "Accept": "text/fragment+html",
        "Referer": f"https://github.com/{repo.full_name}",
        "X-Requested-With": "XMLHttpRequest",
    }
    cookies = _build_cookies(cfg)

    resp = await client.get(url, headers=headers, cookies=cookies)

    if resp.status_code != 200:
        curl = _to_curl("GET", url, headers, cookies)
        _debug_dump("fetch_star_lists failed", resp, curl_cmd=curl)
        resp.raise_for_status()

    html = resp.text
    try:
        csrf_token = _extract_csrf_token(html)
    except ValueError:
        csrf_token = ""

    lists = _parse_lists_from_html(html)

    if not lists:
        profile_lists = await fetch_profile_star_lists(client, cfg)
        return profile_lists, csrf_token

    profile_lists = await fetch_profile_star_lists(client, cfg)
    if profile_lists:
        lists = _merge_lists_by_name(lists, profile_lists)

    return lists, csrf_token


async def fetch_repo_list_state(
    client: httpx.AsyncClient,
    cfg: GitHubConfig,
    repo: StarredRepo,
) -> tuple[list[str], str]:
    url = f"https://github.com/{repo.full_name}/lists?experimental=1"
    headers = {
        **_BROWSER_HEADERS,
        "Accept": "text/fragment+html",
        "Referer": f"https://github.com/{repo.full_name}",
        "X-Requested-With": "XMLHttpRequest",
    }
    cookies = _build_cookies(cfg)

    resp = await client.get(url, headers=headers, cookies=cookies)

    if resp.status_code != 200:
        curl = _to_curl("GET", url, headers, cookies)
        _debug_dump("fetch_repo_list_state failed", resp, curl_cmd=curl)
    resp.raise_for_status()

    html = resp.text
    csrf_token = _extract_csrf_token(html)
    soup = BeautifulSoup(html, "html.parser")

    checked_ids: list[str] = []
    for btn in soup.find_all("button", attrs={"data-input-name": "list_ids[]"}):
        if btn.get("aria-selected") == "true":
            val = btn.get("data-value", "")
            if val:
                checked_ids.append(str(val))

    if not checked_ids:
        for checkbox in soup.find_all(
            "input", {"type": "checkbox", "name": "list_ids[]", "checked": True}
        ):
            val = checkbox.get("value", "")
            if val:
                checked_ids.append(str(val))

    return checked_ids, csrf_token


async def _fetch_create_list_csrf(
    client: httpx.AsyncClient,
    cfg: GitHubConfig,
) -> str:
    url = f"https://github.com/{cfg.username}?tab=stars"
    headers = {
        **_BROWSER_HEADERS,
        "Accept": "text/html",
    }
    cookies = _build_cookies(cfg)

    resp = await client.get(url, headers=headers, cookies=cookies, follow_redirects=True)

    if resp.status_code != 200:
        curl = _to_curl("GET", url, headers, cookies)
        _debug_dump("_fetch_create_list_csrf failed", resp, curl_cmd=curl)
    resp.raise_for_status()
    return _extract_csrf_token(resp.text, action_url=f"/stars/{cfg.username}/lists")


async def create_star_list(
    client: httpx.AsyncClient,
    cfg: GitHubConfig,
    name: str,
    csrf_token: str,
    description: str = "",
) -> str | None:
    url = f"https://github.com/stars/{cfg.username}/lists"

    files = {
        "authenticity_token": (None, csrf_token),
        "user_list[name]": (None, name),
        "user_list[description]": (None, description),
        "user_list[private]": (None, "0"),
    }
    headers = {
        **_BROWSER_HEADERS,
        "Accept": "text/html",
        "Referer": f"https://github.com/{cfg.username}?tab=stars",
        "X-Requested-With": "XMLHttpRequest",
    }
    cookies = _build_cookies(cfg)

    resp = await client.post(
        url, files=files, headers=headers, cookies=cookies, follow_redirects=False,
    )

    if resp.status_code in (301, 302, 303):
        location = resp.headers.get("location", "")
        match = re.search(r"/lists/([^/?]+)", location)
        return match.group(1) if match else None

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")
        link = soup.find("a", {"class": "js-target-url"})
        if link:
            href = link.get("href", "")
            match = re.search(r"/lists/([^/?]+)", href)
            if match:
                return match.group(1)
        meta = soup.find("meta", {"http-equiv": "refresh"})
        if meta:
            content = meta.get("content", "")
            match = re.search(r"/lists/([^/?]+)", content)
            return match.group(1) if match else None

    curl = _to_curl("POST", url, headers, cookies, files=files)
    _debug_dump(f"create_star_list '{name}' failed", resp, curl_cmd=curl)
    console.print(f"[yellow]Warning: status {resp.status_code} creating list '{name}'[/yellow]")
    return None


async def assign_repo_to_lists(
    client: httpx.AsyncClient,
    cfg: GitHubConfig,
    repo: StarredRepo,
    list_ids: list[str],
    csrf_token: str,
) -> bool:
    url = f"https://github.com/{repo.full_name}/lists"

    fields: list[tuple[str, tuple[None, str]]] = [
        ("_method", (None, "put")),
        ("authenticity_token", (None, csrf_token)),
        ("repository_id", (None, str(repo.id))),
        ("context", (None, "user_list_menu")),
        ("user_list_menu_dirty", (None, "1")),
        ("list_ids[]", (None, "")),
    ]
    for lid in list_ids:
        fields.append(("list_ids[]", (None, lid)))

    headers = {
        **_BROWSER_HEADERS,
        "Accept": "application/json",
        "Referer": f"https://github.com/{repo.full_name}",
        "X-Requested-With": "XMLHttpRequest",
    }
    cookies = _build_cookies(cfg)

    resp = await client.post(url, files=fields, headers=headers, cookies=cookies)

    if resp.status_code in (200, 302):
        return True

    curl = _to_curl("POST", url, headers, cookies, files=fields)
    _debug_dump(f"assign_repo_to_lists {repo.full_name} failed", resp, curl_cmd=curl)
    console.print(f"[yellow]Warning: Failed to assign {repo.full_name}, status {resp.status_code}[/yellow]")
    return False


class GitHubWebClient:
    def __init__(self, cfg: GitHubConfig):
        self.cfg = cfg
        self.client = httpx.AsyncClient(timeout=30)
        self._lists: list[StarList] = []
        self._delay = 1.0

    async def close(self) -> None:
        await self.client.aclose()

    async def get_lists(self, any_repo: StarredRepo | None = None) -> list[StarList]:
        if any_repo is not None:
            self._lists, _ = await fetch_star_lists(self.client, self.cfg, any_repo)
            if self._lists and all(sl.id.isdigit() for sl in self._lists):
                return self._lists

        profile_lists = await fetch_profile_star_lists(self.client, self.cfg)
        if any_repo is not None:
            repo_lists, _ = await fetch_star_lists(self.client, self.cfg, any_repo)
            id_by_name = {
                sl.name.lower(): sl.id for sl in repo_lists if sl.id.isdigit()
            }
            resolved: list[StarList] = []
            for item in profile_lists:
                list_id = id_by_name.get(item.name.lower(), item.id)
                resolved.append(StarList(id=list_id, name=item.name))
            self._lists = resolved or repo_lists or profile_lists
        else:
            self._lists = profile_lists

        return self._lists

    def _find_list_by_name(self, name: str) -> StarList | None:
        target = name.strip().lower()
        for item in self._lists:
            if item.name.strip().lower() == target:
                return item
        return None

    async def create_list(self, name: str, any_repo: StarredRepo) -> StarList | None:
        existing = self._find_list_by_name(name)
        if existing and existing.id.isdigit():
            return existing

        csrf = await _fetch_create_list_csrf(self.client, self.cfg)
        await asyncio.sleep(self._delay)

        slug = await create_star_list(self.client, self.cfg, name, csrf)
        await asyncio.sleep(self._delay)

        if slug is None:
            return None

        await self.get_lists(any_repo)
        created = self._find_list_by_name(name)
        if created and created.id.isdigit():
            return created

        console.print(f"[yellow]Created list '{name}' but couldn't find its ID[/yellow]")
        return None

    async def assign_repo(self, repo: StarredRepo, target_list_ids: list[str]) -> bool:
        current_ids, csrf = await fetch_repo_list_state(self.client, self.cfg, repo)
        await asyncio.sleep(self._delay)

        merged = list(set(current_ids) | set(target_list_ids))

        result = await assign_repo_to_lists(self.client, self.cfg, repo, merged, csrf)
        await asyncio.sleep(self._delay)
        return result
