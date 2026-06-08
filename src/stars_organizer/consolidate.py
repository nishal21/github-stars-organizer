"""Merge granular AI list names down to GitHub's 32-list limit."""

from __future__ import annotations

from collections import defaultdict
import re

from .categorize import DEFAULT_CATEGORY, MAX_LISTS

# Map granular list titles → broad buckets (matched against list name text).
BROAD_BUCKETS: dict[str, list[str]] = {
    "AI & LLM": [
        r"ai\b", r"llm", r"machine", r"data.?science", r"notebook", r"algorithm",
    ],
    "Web Dev & Frontend": [
        r"web", r"frontend", r"browser", r"extension", r"personal.?website", r"portfolio",
    ],
    "Mobile & Android": [
        r"mobile", r"android", r"ios", r"flutter", r"scrcpy",
    ],
    "Dev Tools & CLI": [
        r"dev(eloper)?\s*tool", r"cli\b", r"terminal", r"editor", r"ide", r"github.?tool",
        r"git\b", r"productivity", r"utility", r"utilities", r"automation", r"scripting",
    ],
    "Backend & APIs": [
        r"backend", r"api\b", r"server",
    ],
    "Security & Privacy": [
        r"security", r"privacy", r"hack", r"osint", r"scraping", r"scrape",
    ],
    "Media & Creative": [
        r"media", r"video", r"audio", r"animation", r"graphics", r"design", r"stream",
        r"player",
    ],
    "Self-hosting & DevOps": [
        r"devops", r"network", r"linux", r"windows.?tool", r"system", r"infra",
        r"iot", r"home.?auto", r"wearable", r"hardware",
    ],
    "Gaming & Entertainment": [
        r"game", r"gaming", r"emulat",
    ],
    "Anime & Manga": [
        r"anime", r"manga", r"otaku",
    ],
    "Learning & Inspiration": [
        r"learn", r"resource", r"education", r"tutorial",
    ],
    "Go & Systems": [
        r"system", r"low.?level", r"embedded", r"compiler", r"kernel",
    ],
    "Business & Finance": [
        r"business", r"finance", r"commerce", r"e.?commerce",
    ],
    "Desktop Apps": [
        r"desktop",
    ],
    DEFAULT_CATEGORY: [],
}


def _score_list_name(list_name: str, patterns: list[str]) -> int:
    text = list_name.lower()
    return sum(1 for pat in patterns if re.search(pat, text))


def map_list_to_broad(list_name: str) -> str:
    text = list_name.lower()
    if re.search(r"anime|manga|otaku", text):
        return "Anime & Manga"

    scores: dict[str, int] = {}
    for bucket, patterns in BROAD_BUCKETS.items():
        if bucket == DEFAULT_CATEGORY:
            continue
        score = _score_list_name(list_name, patterns)
        if score:
            scores[bucket] = score

    if not scores:
        return DEFAULT_CATEGORY

    return max(scores.items(), key=lambda item: item[1])[0]


def consolidate_assignments(
    assignments: dict[str, str],
    *,
    max_lists: int = MAX_LISTS,
) -> dict[str, str]:
    """Remap repo assignments so unique list count is <= max_lists."""
    unique = set(assignments.values())
    if len(unique) <= max_lists:
        return dict(assignments)

    list_mapping = {name: map_list_to_broad(name) for name in unique}
    consolidated = {repo: list_mapping[list_name] for repo, list_name in assignments.items()}

    # If still too many (unlikely), merge smallest buckets into Misc.
    while True:
        by_list: dict[str, list[str]] = defaultdict(list)
        for repo, list_name in consolidated.items():
            by_list[list_name].append(repo)

        if len(by_list) <= max_lists:
            break

        smallest = min(by_list.items(), key=lambda item: len(item[1]))[0]
        if smallest == DEFAULT_CATEGORY:
            # Merge second-smallest instead to avoid infinite loop
            candidates = sorted(by_list.items(), key=lambda item: len(item[1]))
            smallest = candidates[1][0] if len(candidates) > 1 else smallest

        for repo, list_name in list(consolidated.items()):
            if list_name == smallest:
                consolidated[repo] = DEFAULT_CATEGORY

    return consolidated


def consolidate_plan(plan: dict, *, max_lists: int = MAX_LISTS) -> dict:
    """Return a new plan dict with merged list assignments."""
    assignments = consolidate_assignments(plan["assignments"], max_lists=max_lists)
    by_list: dict[str, list[str]] = defaultdict(list)
    for repo, list_name in assignments.items():
        by_list[list_name].append(repo)

    return {
        "username": plan["username"],
        "total": plan["total"],
        "lists": {
            name: len(items)
            for name, items in sorted(by_list.items(), key=lambda x: -len(x[1]))
        },
        "assignments": assignments,
        "consolidated": True,
        "original_list_count": len(plan.get("lists", {})),
    }
