from stars_organizer.github_web import (
    _parse_lists_from_html,
    _parse_profile_list_links,
)


def test_parse_modern_button_ui():
    html = """
    <button data-input-name="list_ids[]" data-value="12345" aria-selected="false">
      <span class="ActionListItem-label">Web Dev</span>
    </button>
    <button data-input-name="list_ids[]" data-value="67890" aria-selected="true">
      <span class="ActionListItem-label">Anime &amp; Manga</span>
    </button>
    """
    lists = _parse_lists_from_html(html)
    assert len(lists) == 2
    assert lists[0].id == "12345"
    assert lists[0].name == "Web Dev"


def test_parse_profile_links():
    html = """
    <a href="/stars/nishal21/lists/web-dev">Web Dev</a>
    <a href="/stars/nishal21/lists/anime-manga">Anime & Manga</a>
    <a href="/stars/nishal21/lists/new">New list</a>
    """
    lists = _parse_profile_list_links(html, "nishal21")
    assert len(lists) == 2
    names = {item.name for item in lists}
    assert "Web Dev" in names
    assert "Anime & Manga" in names
