"""Apply a categorization plan to GitHub Star Lists."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

from .categorize import MAX_LISTS, load_plan
from .config import load_config
from .github_api import fetch_starred_repos
from .github_web import GitHubWebClient
from .models import Assignment, CategorizationResult
from .state import DEFAULT_STATE_PATH, ApplyState

console = Console()


async def apply_plan(
    *,
    dry_run: bool,
    config_path: Path,
    plan_path: Path,
    yes: bool = False,
    resume: bool = False,
    state_path: Path = DEFAULT_STATE_PATH,
) -> None:
    if not plan_path.exists():
        console.print(f"[red]Plan file not found: {plan_path}[/red]")
        console.print("Create one first:")
        console.print("  organize-stars plan --config config.toml")
        console.print("  organize-stars plan --username YOUR_USERNAME")
        return

    cfg = load_config(config_path)
    assignments_map = load_plan(plan_path)

    console.print(f"Loaded plan: {len(assignments_map)} repos")
    repos = await fetch_starred_repos(cfg.github)
    if not repos:
        console.print("[red]No starred repos found. Check your GitHub token in config.toml.[/red]")
        return

    repo_by_name = {r.full_name: r for r in repos}
    missing = [name for name in assignments_map if name not in repo_by_name]
    if missing:
        console.print(
            f"[yellow]Warning: {len(missing)} repos no longer starred (skipped).[/yellow]"
        )

    assignments = [
        Assignment(repo=name, list_name=list_name)
        for name, list_name in assignments_map.items()
        if name in repo_by_name
    ]

    by_list: dict[str, list[str]] = defaultdict(list)
    for assignment in assignments:
        by_list[assignment.list_name].append(assignment.repo)

    console.print("\nPlanned lists:")
    for list_name in sorted(by_list, key=lambda key: (-len(by_list[key]), key)):
        console.print(f"  {list_name}: {len(by_list[list_name])} repos")

    if len(by_list) > MAX_LISTS:
        console.print(
            f"\n[red]Error: plan has {len(by_list)} lists; GitHub max is {MAX_LISTS}.[/red]"
            " Merge categories before applying."
        )
        return

    if dry_run:
        console.print("\n[yellow]Dry run — no changes applied.[/yellow]")
        return

    if not yes:
        confirm = console.input(
            "\n[bold]Apply these lists to GitHub? (y/N): [/bold]"
        ).strip().lower()
        if confirm != "y":
            console.print("Aborted.")
            return

    state = ApplyState.load(state_path) if resume else None
    if state and state.plan_path != str(plan_path.resolve()):
        console.print("[yellow]Resume state is for a different plan; starting fresh.[/yellow]")
        state = None

    if state is None:
        state = ApplyState(plan_path=str(plan_path.resolve()))

    already_assigned = set(state.assigned_repos)
    pending = [a for a in assignments if a.repo not in already_assigned]

    result = CategorizationResult(
        assignments=pending,
        new_lists=sorted(name for name in by_list if name not in state.lists_created),
    )

    web = GitHubWebClient(cfg.github)
    try:
        existing_lists = await web.get_lists(repos[0])
        list_name_to_id = {item.name: item.id for item in existing_lists}
        for name in state.lists_created:
            for item in existing_lists:
                if item.name == name:
                    list_name_to_id[item.name] = item.id

        if result.new_lists:
            console.print(f"\nCreating {len(result.new_lists)} lists...")
            for name in result.new_lists:
                if name in list_name_to_id:
                    continue
                created = await web.create_list(name, repos[0])
                if created:
                    list_name_to_id[created.name] = created.id
                    state.lists_created.append(created.name)
                    state.save(state_path)
                    console.print(f"  [green]+[/green] {name}")
                else:
                    console.print(f"  [red]![/red] Failed: {name}")

        console.print(f"\nAssigning {len(pending)} repos...")
        ok = len(already_assigned)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Assigning repos...", total=len(pending))
            for assignment in pending:
                repo = repo_by_name.get(assignment.repo)
                target_id = list_name_to_id.get(assignment.list_name)
                if not repo or not target_id:
                    progress.advance(task)
                    continue
                if await web.assign_repo(repo, [target_id]):
                    ok += 1
                    state.assigned_repos.append(assignment.repo)
                else:
                    state.failed_repos.append(assignment.repo)
                state.save(state_path)
                progress.advance(task)

        if state.failed_repos:
            console.print(
                f"\n[yellow]Done with {len(state.failed_repos)} failures. "
                f"Re-run with --resume to retry.[/yellow]"
            )
        else:
            ApplyState.clear(state_path)
            console.print(
                f"\n[bold green]Done![/bold green] Assigned {ok}/{len(assignments)} repos."
            )
        console.print(f"View: https://github.com/{cfg.github.username}?tab=stars")
    finally:
        await web.close()
