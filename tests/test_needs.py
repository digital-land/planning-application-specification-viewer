from types import SimpleNamespace
import pytest
from spec_viewer.pages.needs import render_needs
from spec_viewer.rendering import create_environment
from spec_viewer.view_models.needs import need_status, justification_search_references


@pytest.mark.parametrize("base_url", ["", "/viewer"])
def test_needs_links_facets_and_justification_body(tmp_path, base_url):
    data = SimpleNamespace(needs={"N1": {"need": "N1", "name": "Find a record", "themes": ["access"], "actors": ["resident"]}},
        justifications={"J1": {"id": "J1", "needs": ["N1"], "satisfaction": "partial", "body": "**Evidence** for this link", "satisfied_by": {"anyOf": [{"dataset": "record", "field": "reference"}]}}})
    assert render_needs(data, create_environment(base_url), tmp_path) == 4
    index = (tmp_path / "user-need/index.html").read_text()
    assert "Not specified" in index
    assert "Resident" in index
    assert "Partially satisfied" in index
    assert f'href="{base_url}/user-need/N1"' in index
    detail = (tmp_path / "user-need/N1/index.html").read_text()
    assert f'href="{base_url}/justification/J1"' in detail
    justification = (tmp_path / "justification/J1/index.html").read_text()
    assert "<strong>Evidence</strong>" in justification
    assert f'href="{base_url}/user-need/N1"' in justification
    assert "justification-search.js" in (tmp_path / "justification/index.html").read_text()


def test_status_precedence_and_nested_search_references():
    assert need_status([])[0] == "Not satisfied"
    assert need_status([{"satisfaction": "proposed"}])[0] == "Proposed"
    assert need_status([{"satisfaction": "partial"}, {"satisfaction": "full"}])[0] == "Satisfied"
    assert justification_search_references({"allOf": [{"field": "name"}, {"anyOf": [{"field": "name"}, {"codelist": "kind", "includes": ["a"]}]}]}) == ["Field: name", "Codelist: kind", "Code: a"]
