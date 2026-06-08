import json

from stars_organizer.categorize import build_plan, load_plan, save_plan
from stars_organizer.models import StarredRepo


def _repo(full_name: str) -> StarredRepo:
    return StarredRepo(
        id=1,
        full_name=full_name,
        description="",
        language="Python",
        topics=[],
        html_url=f"https://github.com/{full_name}",
    )


def test_build_and_load_plan_round_trip(tmp_path):
    repos = [_repo("openai/openai-python"), _repo("vercel/next.js")]
    plan = build_plan("testuser", repos)

    assert plan["username"] == "testuser"
    assert plan["total"] == 2
    assert len(plan["assignments"]) == 2
    assert len(plan["lists"]) >= 1

    out = tmp_path / "plan.json"
    save_plan(plan, out)
    loaded = load_plan(out)
    assert loaded == plan["assignments"]


def test_plan_json_structure(tmp_path):
    plan = {
        "username": "user",
        "total": 1,
        "lists": {"Dev Tools & CLI": 1},
        "assignments": {"cli/cli": "Dev Tools & CLI"},
    }
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan), encoding="utf-8")
    assert load_plan(path)["cli/cli"] == "Dev Tools & CLI"
