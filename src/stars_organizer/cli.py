"""Command-line interface for github-stars-organizer."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from .apply import apply_plan
from .categorize import build_plan, save_plan
from .config import load_config
from .github_api import fetch_public_starred_repos, fetch_starred_repos


def _cmd_plan(args: argparse.Namespace) -> None:
    username = args.username

    async def run() -> None:
        if args.config:
            cfg = load_config(Path(args.config))
            username = cfg.github.username
            token = cfg.github.token or None
            repos = await fetch_starred_repos(cfg.github)
        else:
            if not username:
                print("Provide --username or --config with github.username set.")
                sys.exit(1)
            token = args.token
            repos = await fetch_public_starred_repos(username, token=token)

        if not repos:
            print("No starred repos found.")
            sys.exit(1)

        plan = build_plan(username, repos)
        output = Path(args.output)
        save_plan(plan, output)

        print(f"Saved plan for {plan['total']} repos → {output}")
        print("\nLists:")
        for name, count in plan["lists"].items():
            print(f"  {name}: {count}")

    asyncio.run(run())


def _cmd_apply(args: argparse.Namespace) -> None:
    asyncio.run(
        apply_plan(
            dry_run=args.dry_run,
            config_path=Path(args.config),
            plan_path=Path(args.plan),
            yes=args.yes,
        )
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
    plan_parser.add_argument(
        "--output",
        default="categorization-plan.json",
        help="Output plan JSON path",
    )
    plan_parser.set_defaults(func=_cmd_plan)

    apply_parser = subparsers.add_parser("apply", help="Apply a plan to GitHub Star Lists")
    apply_parser.add_argument("--config", default="config.toml", help="Config file path")
    apply_parser.add_argument("--plan", default="categorization-plan.json", help="Plan JSON path")
    apply_parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    apply_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    apply_parser.set_defaults(func=_cmd_apply)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
