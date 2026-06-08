"""Command-line interface for github-stars-organizer."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from rich.console import Console

from .apply import apply_plan
from .categorize import build_plan, load_categories, merge_categories, save_plan
from .config import config_status, load_config, load_llm_config
from .github_api import fetch_public_starred_repos, fetch_starred_repos
from .github_web import GitHubWebClient
from .llm_categorize import categorize_repos_llm, llm_result_to_plan
from .llm_providers import list_providers
from .state import DEFAULT_STATE_PATH, ApplyState

console = Console()


def _resolve_categories(path: str | None) -> dict[str, list[tuple[str, int]]] | None:
    if not path:
        return None
    custom = load_categories(Path(path))
    return merge_categories(custom)


def _cmd_plan(args: argparse.Namespace) -> None:
    async def run() -> None:
        if args.config:
            cfg = load_config(Path(args.config))
            target_user = cfg.github.username
            repos = await fetch_starred_repos(cfg.github)
        else:
            target_user = args.username
            if not target_user:
                console.print("[red]Provide --username or --config with github.username set.[/red]")
                sys.exit(1)
            repos = await fetch_public_starred_repos(target_user, token=args.token)

        if not repos:
            console.print("[red]No starred repos found.[/red]")
            sys.exit(1)

        categories = _resolve_categories(args.categories)

        if args.llm:
            cfg_path = Path(args.config) if args.config else Path("config.toml")
            if not cfg_path.exists():
                console.print("[red]--llm requires config.toml with [llm] section.[/red]")
                sys.exit(1)

            import tomllib

            with open(cfg_path, "rb") as f:
                raw = tomllib.load(f)
            if "llm" not in raw:
                console.print("[red]config.toml missing [llm] section.[/red]")
                sys.exit(1)

            try:
                llm_cfg = load_llm_config(raw["llm"], provider_override=args.provider)
            except ValueError as exc:
                console.print(f"[red]{exc}[/red]")
                sys.exit(1)

            existing_lists = []
            if args.config:
                cfg = load_config(cfg_path)
                web = GitHubWebClient(cfg.github)
                try:
                    existing_lists = await web.get_lists(repos[0])
                    if existing_lists:
                        console.print(f"Found {len(existing_lists)} existing Star Lists on GitHub.")
                except Exception:
                    console.print(
                        "[yellow]Could not fetch existing lists; AI will create new ones.[/yellow]"
                    )
                finally:
                    await web.close()

            console.print("Categorizing with LLM...")
            result = await categorize_repos_llm(llm_cfg, repos, existing_lists=existing_lists)
            plan = llm_result_to_plan(target_user, result)
        else:
            plan = build_plan(target_user, repos, categories=categories)

        output = Path(args.output)
        save_plan(plan, output)

        console.print(f"[green]Saved plan for {plan['total']} repos -> {output}[/green]")
        console.print("\nLists:")
        for name, count in plan["lists"].items():
            console.print(f"  {name}: {count}")

    asyncio.run(run())


def _cmd_apply(args: argparse.Namespace) -> None:
    asyncio.run(
        apply_plan(
            dry_run=args.dry_run,
            config_path=Path(args.config),
            plan_path=Path(args.plan),
            yes=args.yes,
            resume=args.resume,
        )
    )


def _cmd_init(args: argparse.Namespace) -> None:
    config_path = Path(args.config)
    if config_path.exists() and not args.force:
        console.print(f"[yellow]{config_path} already exists. Use --force to overwrite.[/yellow]")
        sys.exit(1)

    username = console.input("GitHub username: ").strip()
    token = console.input("GitHub token (ghp_...): ").strip()
    console.print("Paste browser Cookie header (from DevTools → Network → github.com):")
    cookies = console.input("Cookie: ").strip()

    content = f"""[github]
username = "{username}"
token = "{token}"

[github.session]
cookies = "{cookies}"

concurrency = 5
"""
    config_path.write_text(content, encoding="utf-8")
    console.print(f"[green]Wrote {config_path}[/green]")
    console.print("Optional: add [llm] section for AI categorization (see config.example.toml).")


def _cmd_status(args: argparse.Namespace) -> None:
    config_path = Path(args.config)
    status = config_status(config_path)

    console.print(f"Config: {config_path}")
    if not status["exists"]:
        console.print("[red]Not found. Run: organize-stars init[/red]")
        sys.exit(1)

    console.print(f"  Username: {status['username']}")
    console.print(f"  Token set: {'yes' if status['has_token'] else 'no'}")
    console.print(f"  Cookies set: {'yes' if status['has_cookies'] else 'no'}")
    console.print(f"  LLM configured: {'yes' if status['has_llm'] else 'no'}")
    if status["has_llm"]:
        console.print(f"  LLM provider: {status['llm_provider']}")
        console.print(f"  LLM model: {status['llm_model']}")

    state = ApplyState.load(DEFAULT_STATE_PATH)
    if state:
        console.print(f"\nResume state: {DEFAULT_STATE_PATH}")
        console.print(f"  Assigned: {len(state.assigned_repos)}")
        console.print(f"  Failed: {len(state.failed_repos)}")
        console.print(f"  Lists created: {len(state.lists_created)}")
        console.print("  Run: organize-stars apply --resume")
    else:
        console.print("\nNo pending resume state.")


def _cmd_lists(args: argparse.Namespace) -> None:
    async def run() -> None:
        cfg = load_config(Path(args.config))
        repos = await fetch_starred_repos(cfg.github)
        if not repos:
            console.print("[red]No starred repos found.[/red]")
            sys.exit(1)

        web = GitHubWebClient(cfg.github)
        try:
            lists = await web.get_lists(repos[0])
            if not lists:
                console.print("No Star Lists yet.")
                return
            for item in lists:
                console.print(f"  - {item.name} (id: {item.id})")
        finally:
            await web.close()

    asyncio.run(run())


def _cmd_providers(_args: argparse.Namespace) -> None:
    console.print("[bold]Supported LLM providers[/bold]\n")
    for preset in list_providers():
        console.print(f"  [cyan]{preset.name}[/cyan]")
        console.print(f"    model: {preset.default_model}")
        console.print(f"    base_url: {preset.base_url}")
        console.print(f"    env var: {preset.env_key}")
        console.print(f"    keys: {preset.docs_url}\n")
    console.print("Use in config.toml: [bold]provider = \"mistral\"[/bold]")
    console.print(
        "Run: [bold]organize-stars plan --config config.toml --llm --provider mistral[/bold]"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="organize-stars",
        description="Organize GitHub starred repos into Star Lists",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Fetch stars and build a categorization plan")
    plan_parser.add_argument("--username", help="GitHub username (for public stars)")
    plan_parser.add_argument("--token", help="Optional GitHub token (higher rate limits)")
    plan_parser.add_argument("--config", help="Use username/token from config.toml")
    plan_parser.add_argument("--categories", help="Custom categories TOML file")
    plan_parser.add_argument(
        "--llm", action="store_true", help="LLM categorization (needs [llm] in config)"
    )
    plan_parser.add_argument(
        "--provider",
        help="LLM provider (mistral, openai, groq, openrouter, google, deepseek, ...)",
    )
    plan_parser.add_argument(
        "--output", default="categorization-plan.json", help="Output plan JSON path"
    )
    plan_parser.set_defaults(func=_cmd_plan)

    apply_parser = subparsers.add_parser("apply", help="Apply a plan to GitHub Star Lists")
    apply_parser.add_argument("--config", default="config.toml", help="Config file path")
    apply_parser.add_argument("--plan", default="categorization-plan.json", help="Plan JSON path")
    apply_parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    apply_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    apply_parser.add_argument("--resume", action="store_true", help="Resume interrupted apply")
    apply_parser.set_defaults(func=_cmd_apply)

    init_parser = subparsers.add_parser("init", help="Interactive setup for config.toml")
    init_parser.add_argument("--config", default="config.toml", help="Config file path")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing config")
    init_parser.set_defaults(func=_cmd_init)

    status_parser = subparsers.add_parser("status", help="Show config and resume state")
    status_parser.add_argument("--config", default="config.toml", help="Config file path")
    status_parser.set_defaults(func=_cmd_status)

    lists_parser = subparsers.add_parser("lists", help="List current GitHub Star Lists")
    lists_parser.add_argument("--config", default="config.toml", help="Config file path")
    lists_parser.set_defaults(func=_cmd_lists)

    providers_parser = subparsers.add_parser("providers", help="List supported LLM providers")
    providers_parser.set_defaults(func=_cmd_providers)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
