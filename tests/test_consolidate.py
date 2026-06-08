from stars_organizer.consolidate import consolidate_assignments, consolidate_plan, map_list_to_broad
from stars_organizer.categorize import MAX_LISTS


def test_map_anime_variants_to_one_bucket():
    assert map_list_to_broad("Anime & Streaming") == "Anime & Manga"
    assert map_list_to_broad("Anime & Manga Tools") == "Anime & Manga"
    assert map_list_to_broad("Anime Tools") == "Anime & Manga"


def test_consolidate_reduces_many_lists():
    assignments = {}
    list_names = [
        "Anime", "Anime & Manga", "Anime Tools", "Anime & Streaming",
        "Android Tools", "Android Apps", "Mobile Dev",
        "AI & LLM", "Web Dev", "Gaming", "DevOps", "Security",
    ]
    for i, name in enumerate(list_names):
        assignments[f"owner/repo{i}"] = name

    # Add more granular lists to exceed 32
    for i in range(50):
        assignments[f"extra/repo{i}"] = f"Category {i}"

    result = consolidate_assignments(assignments, max_lists=MAX_LISTS)
    assert len(set(result.values())) <= MAX_LISTS


def test_consolidate_plan_structure():
    assignments = {f"owner/r{i}": f"Anime List {i}" for i in range(40)}
    assignments["owner/web"] = "Web Dev"
    plan = {
        "username": "user",
        "total": len(assignments),
        "lists": {},
        "assignments": assignments,
    }
    merged = consolidate_plan(plan)
    assert len(merged["lists"]) <= MAX_LISTS
    assert merged["assignments"]["owner/r0"] == "Anime & Manga"
