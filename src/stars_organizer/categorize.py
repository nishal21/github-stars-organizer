"""Heuristic categorization of starred repositories into broad lists."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from .models import StarredRepo

CATEGORIES: dict[str, list[tuple[str, int]]] = {
    "AI & LLM": [
        (r"\b(llm|gpt|claude|openai|gemini|mistral|ollama|whisper|transformer|langchain|copilot|codex|inference|embedding|rag\b|fine-?tun|huggingface|pytorch|tensorflow|neural|speech|tts|text-to-speech|voice|skill\b|agent\b|mcp\b|synthid|deepseek|llama|anthropic)", 3),
        (r"\b(ai\b|machine-learning|ml\b|computer-vision|nlp\b|generative)", 2),
    ],
    "Web Dev & Frontend": [
        (r"\b(react|nextjs|next\.js|vue|svelte|tailwind|frontend|responsive|portfolio|css|html|ui\b|component|design-system|landing|website|web-app|browser|electron|vite|webpack|angular)", 3),
        (r"\b(javascript|typescript|web\b|frontend|css-framework)", 1),
    ],
    "Mobile & Android": [
        (r"\b(android|ios|flutter|dart|kotlin|swift|scrcpy|mobile|apk|iphone|ipad|react-native|expo)", 3),
    ],
    "Dev Tools & CLI": [
        (r"\b(cli\b|terminal|vscode|cursor|git\b|github|developer-tool|devtools|automation|workflow|productivity|dotfiles|neovim|vim|shell|bash|zsh|toolkit|utility|script)", 2),
        (r"\b(debug|lint|format|test|benchmark|monitor|log\b|trace)", 1),
    ],
    "Backend & APIs": [
        (r"\b(api\b|backend|server|fastapi|express|graphql|rest\b|microservice|database|postgres|redis|mongodb|mysql|orm\b|grpc|websocket|auth\b|oauth|jwt)", 3),
        (r"\b(node\b|django|flask|rails|laravel|spring)", 2),
    ],
    "Security & Privacy": [
        (r"\b(security|privacy|vpn|proxy|encrypt|pentest|malware|reverse-engineer|exploit|vulnerability|firewall|tor\b|anonymous|hack\b|ctf\b|red-team|blue-team|atomic-red)", 3),
    ],
    "Media & Creative": [
        (r"\b(video|audio|image|ffmpeg|media|edit|creative|photo|music|podcast|stream|youtube|animation|render|graphics|canvas|figma|design\b|art\b|tts|speech)", 2),
    ],
    "Self-hosting & DevOps": [
        (r"\b(self-host|docker|kubernetes|k8s|homelab|raspberry|router|linux|infra|deploy|cloud|aws|azure|gcp|terraform|ansible|ci/cd|github-actions|nginx|proxy-server|serverless)", 3),
        (r"\b(devops|infrastructure|container|helm|monitoring|grafana|prometheus)", 2),
    ],
    "Gaming & Entertainment": [
        (r"\b(game|gaming|minecraft|steam|emulator|retro|unity|unreal|godot|anime|manga|otaku|dating-app)", 3),
    ],
    "Learning & Inspiration": [
        (r"\b(tutorial|learn|course|awesome-|education|docs\b|guide|example|sample|template|starter|boilerplate|thesis|defense|portfolio|inspiration|list-of|curated|collection)", 2),
    ],
    "Go & Systems": [
        (r"\b(go\b|golang|rust|systems|kernel|embedded|firmware|hardware|c\b|c\+\+|assembly|low-level|performance|memory|compiler)", 2),
    ],
}

LANG_HINTS = {
    "typescript": "Web Dev & Frontend",
    "javascript": "Web Dev & Frontend",
    "python": "AI & LLM",
    "go": "Go & Systems",
    "rust": "Go & Systems",
    "kotlin": "Mobile & Android",
    "swift": "Mobile & Android",
    "dart": "Mobile & Android",
    "php": "Backend & APIs",
    "ruby": "Backend & APIs",
    "java": "Backend & APIs",
}

DEFAULT_CATEGORY = "Misc & Tools"


def _repo_text(repo: StarredRepo) -> str:
    return " ".join(
        filter(
            None,
            [
                repo.full_name,
                repo.description,
                repo.language,
                " ".join(repo.topics),
            ],
        )
    ).lower()


def categorize_repo(repo: StarredRepo) -> str:
    text = _repo_text(repo)
    scores: dict[str, int] = defaultdict(int)

    for category, patterns in CATEGORIES.items():
        for pattern, weight in patterns:
            if re.search(pattern, text):
                scores[category] += weight

    lang = repo.language.lower() if repo.language else ""
    if lang in LANG_HINTS and not scores:
        scores[LANG_HINTS[lang]] += 1

    if not scores:
        return DEFAULT_CATEGORY

    return max(scores.items(), key=lambda item: item[1])[0]


def build_plan(username: str, repos: list[StarredRepo]) -> dict:
    assignments: dict[str, str] = {}
    by_list: dict[str, list[str]] = defaultdict(list)

    for repo in repos:
        category = categorize_repo(repo)
        assignments[repo.full_name] = category
        by_list[category].append(repo.full_name)

    return {
        "username": username,
        "total": len(repos),
        "lists": {name: len(items) for name, items in sorted(by_list.items(), key=lambda x: -len(x[1]))},
        "assignments": assignments,
    }


def save_plan(plan: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_plan(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["assignments"]
