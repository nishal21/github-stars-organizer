"""Optional LLM-based categorization for starred repositories."""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Callable

from rich.console import Console

from .categorize import MAX_LISTS
from .config import LLMConfig
from .models import Assignment, CategorizationResult, StarList, StarredRepo

console = Console()

SYSTEM_PROMPT = """You are a GitHub repository organizer. Categorize starred repositories into meaningful Star Lists.

CRITICAL RULES:
1. Use at most 20 broad lists total. NEVER exceed 25. GitHub hard limit is 32.
2. Use SHORT, BROAD list names only (2-3 words max). Examples: "AI & LLM", "Web Dev", "Anime & Manga", "Dev Tools", "Gaming", "Mobile", "Security", "DevOps", "Media", "Misc".
3. Do NOT create overlapping or hyper-specific lists (bad: "Anime & Streaming", "Anime Tools", "Android Apps" — good: one "Anime & Manga" list).
4. Prefer reusing existing list names when provided.
5. Each repo goes to exactly ONE list.
6. Respond ONLY with valid JSON, no markdown fences."""

USER_PROMPT_TEMPLATE = """Existing star lists:
{existing_lists}

User preferences:
{preferences}

Repositories to categorize:
{repo_summaries}

Return JSON:
{{
  "assignments": [{{"repo": "owner/name", "list": "List Name"}}],
  "new_lists": ["New List 1"]
}}

"new_lists" contains only names not in existing lists.

REMINDER: Use at most 20 broad lists. Merge similar topics (all anime → "Anime & Manga", all android → "Mobile")."""

BATCH_SIZE = 80


def _build_repo_summaries(repos: list[StarredRepo]) -> str:
    return "\n".join(repo.summary() for repo in repos)


def _build_existing_lists(lists: list[StarList]) -> str:
    if not lists:
        return "(none yet)"
    return "\n".join(f"- {item.name}" for item in lists)


def _parse_json_response(content: str) -> dict:
    text = content.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


async def _categorize_batch(
    client,
    cfg: LLMConfig,
    batch: list[StarredRepo],
    existing_lists: list[StarList],
    semaphore: asyncio.Semaphore,
) -> tuple[list[Assignment], set[str]]:
    async with semaphore:
        prompt = USER_PROMPT_TEMPLATE.format(
            existing_lists=_build_existing_lists(existing_lists),
            preferences=cfg.preferences or "(none)",
            repo_summaries=_build_repo_summaries(batch),
            max_lists=MAX_LISTS,
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        content = "{}"
        try:
            response = await client.chat.completions.create(
                model=cfg.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            content = response.choices[0].message.content or "{}"
        except Exception:
            response = await client.chat.completions.create(
                model=cfg.model,
                messages=messages,
                temperature=0.3,
            )
            content = response.choices[0].message.content or "{}"

        data = _parse_json_response(content)

        assignments = [
            Assignment(repo=item["repo"], list_name=item["list"])
            for item in data.get("assignments", [])
        ]
        return assignments, set(data.get("new_lists", []))


async def categorize_repos_llm(
    cfg: LLMConfig,
    repos: list[StarredRepo],
    existing_lists: list[StarList] | None = None,
    on_batch: Callable[[int, int, int], None] | None = None,
) -> CategorizationResult:
    try:
        from openai import AsyncOpenAI
    except ImportError as exc:
        raise ImportError(
            "LLM mode requires openai. Install with: uv sync --extra llm"
        ) from exc

    console.print(
        f"[cyan]LLM provider:[/cyan] {cfg.provider}  "
        f"[cyan]model:[/cyan] {cfg.model}"
    )

    client = AsyncOpenAI(base_url=cfg.base_url, api_key=cfg.api_key)
    semaphore = asyncio.Semaphore(cfg.concurrency)
    existing = existing_lists or []
    known_names = {item.name for item in existing}
    batches = [repos[i : i + BATCH_SIZE] for i in range(0, len(repos), BATCH_SIZE)]

    completed = 0

    async def run_batch(batch_idx: int, batch: list[StarredRepo]):
        nonlocal completed
        result = await _categorize_batch(client, cfg, batch, existing, semaphore)
        completed += 1
        if on_batch:
            on_batch(completed, len(batches), len(batch))
        return result

    results = await asyncio.gather(*(run_batch(i, batch) for i, batch in enumerate(batches)))

    all_assignments: list[Assignment] = []
    all_new_lists: set[str] = set()
    for assignments, new_lists in results:
        all_assignments.extend(assignments)
        for name in new_lists:
            if name not in known_names:
                all_new_lists.add(name)
                known_names.add(name)

    return CategorizationResult(
        assignments=all_assignments,
        new_lists=sorted(all_new_lists),
    )


def llm_result_to_plan(username: str, result: CategorizationResult) -> dict:
    assignments: dict[str, str] = {}
    by_list: dict[str, list[str]] = {}

    for assignment in result.assignments:
        assignments[assignment.repo] = assignment.list_name
        by_list.setdefault(assignment.list_name, []).append(assignment.repo)

    return {
        "username": username,
        "total": len(assignments),
        "lists": {
            name: len(items)
            for name, items in sorted(by_list.items(), key=lambda x: -len(x[1]))
        },
        "assignments": assignments,
    }
