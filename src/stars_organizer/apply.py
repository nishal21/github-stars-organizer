"""Apply a categorization plan to GitHub Star Lists."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .categorize import load_plan
from .config import Config, load_config
from .github_api import fetch_starred_repos
from .github_web import GitHubWebClient
from .models import Assignment, CategorizationResult


async def apply_plan(
    *,
    dry_run: bool,
    config_path: Path,
    plan_path: Path,
    yes: bool = False,
) -> None:
    cfg = load_config(config_path)
    assignments_map = load_plan(plan_path)

    print(f"Loaded plan: {len(assignments_map)} repos")
    repos = await fetch_starred_repos(cfg.github)
    if not repos:
        print("No starred repos found. Check your GitHub token in config.toml.")
        return

    repo_by_name = {r.full_name: r for r in repos}
    missing = [name for name in assignments_map if name not in repo_by_name]
    if missing:
        print(f"Warning: {len(missing)} repos in plan are no longer starred (skipped).")

    assignments = [
        Assignment(repo=name, list_name=list_name)
        for name, list_name in assignments_map.items()
        if name in repo_by_name
    ]

    by_list: dict[str, list[str]] = defaultdict(list)
    for assignment in assignments:
        by_list[assignment.list_name].append(assignment.repo)

    print("\nPlanned lists:")
    for list_name in sorted(by_list, key=lambda key: (-len(by_list[key]), key)):
        print(f"  {list_name}: {len(by_list[list_name])} repos")

    if dry_run:
        print("\nDry run — no changes applied.")
        return

    if not yes:
        confirm = input("\nApply these lists to GitHub? (y/N): ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return

    result = CategorizationResult(
        assignments=assignments,
        new_lists=sorted(by_list.keys()),
    )

    web = GitHubWebClient(cfg.github)
    try:
        existing_lists = await web.get_lists(repos[0])
        list_name_to_id = {item.name: item.id for item in existing_lists}

        to_create = [name for name in result.new_lists if name not in list_name_to_id]
        if to_create:
            print(f"\nCreating {len(to_create)} lists...")
            for name in to_create:
                created = await web.create_list(name, repos[0])
                if created:
                    list_name_to_id[created.name] = created.id
                    print(f"  + {name}")
                else:
                    print(f"  ! Failed: {name}")

        print(f"\nAssigning {len(assignments)} repos...")
        ok = 0
        for index, assignment in enumerate(assignments, 1):
            repo = repo_by_name.get(assignment.repo)
            target_id = list_name_to_id.get(assignment.list_name)
            if not repo or not target_id:
                continue
            if await web.assign_repo(repo, [target_id]):
                ok += 1
            if index % 25 == 0:
                print(f"  ... {index}/{len(assignments)}")

        print(f"\nDone. Assigned {ok}/{len(assignments)} repos.")
        print(f"View: https://github.com/{cfg.github.username}?tab=stars")
    finally:
        await web.close()
