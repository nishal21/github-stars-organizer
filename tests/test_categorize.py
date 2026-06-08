from stars_organizer.categorize import (
    MAX_LISTS,
    categorize_repo,
    load_categories,
    merge_categories,
)
from stars_organizer.models import StarredRepo


def _repo(
    full_name: str,
    description: str = "",
    language: str = "",
    topics: list[str] | None = None,
) -> StarredRepo:
    return StarredRepo(
        id=1,
        full_name=full_name,
        description=description,
        language=language,
        topics=topics or [],
        html_url=f"https://github.com/{full_name}",
    )


def test_nextjs_is_web_dev():
    repo = _repo("vercel/next.js", "The React Framework", "TypeScript", ["react", "nextjs"])
    assert categorize_repo(repo) == "Web Dev & Frontend"


def test_openai_python_is_ai():
    repo = _repo("openai/openai-python", "OpenAI Python library", "Python", ["openai", "llm"])
    assert categorize_repo(repo) == "AI & LLM"


def test_scrcpy_is_mobile():
    repo = _repo("Genymobile/scrcpy", "Display and control your Android device", "C", ["android"])
    assert categorize_repo(repo) == "Mobile & Android"


def test_plain_python_repo_not_forced_to_ai():
    repo = _repo("psf/requests", "HTTP library for Python", "Python", ["http"])
    assert categorize_repo(repo) != "AI & LLM"


def test_tie_breaker_uses_language_hint():
    repo = _repo("owner/mixed", "A go golang rust project", "Go")
    assert categorize_repo(repo) == "Go & Systems"


def test_custom_category_from_toml(tmp_path):
    categories_file = tmp_path / "categories.toml"
    categories_file.write_text(
        """
[[category]]
name = "Anime & APIs"
patterns = ["anime", "jikan"]
weight = 5
""",
        encoding="utf-8",
    )
    custom = load_categories(categories_file)
    merged = merge_categories(custom)
    repo = _repo("user/anime-api", "Anime API wrapper", "Python", ["anime"])
    assert categorize_repo(repo, categories=merged) == "Anime & APIs"


def test_max_lists_constant():
    assert MAX_LISTS == 32
