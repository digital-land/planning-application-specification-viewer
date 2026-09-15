from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from spec_viewer.build import build
from spec_viewer.view_models.fields import field_markdown


@pytest.mark.parametrize("base_url", ["", "/viewer"])
def test_build_fields_from_explicit_data(tmp_path, monkeypatch, base_url):
    source = tmp_path / "source"
    fields = source / "specification/field"
    fields.mkdir(parents=True)
    (fields / "description.md").write_text("---\nfield: description\nname: Description\ndescription: A proposal description\nnotes: 'See [name](name.md)'\n---\nMore information.")
    (fields / "name.md").write_text("---\nfield: name\nname: Name\n---\n")
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "site"
    assert build(source, output, base_url) == 3
    index = BeautifulSoup((output / "field/index.html").read_text(), "html.parser")
    assert [a['href'] for a in index.select('[data-field-item] a')] == [f"{base_url}/field/description", f"{base_url}/field/name"]
    assert index.select_one('[data-fields-search]')
    assert (output / "static/javascripts/field-search.js").is_file()
    detail = (output / "field/description/index.html").read_text()
    assert f'href="{base_url}/field/name"' in detail
    assert "More information." in detail


def test_markdown_preserves_external_links_and_field_fragments():
    result = str(field_markdown("[Sibling](name.md#notes) and [External](https://example.com/a.md)", lambda path: "/viewer" + path))
    assert 'href="/viewer/field/name#notes"' in result
    assert 'href="https://example.com/a.md"' in result
