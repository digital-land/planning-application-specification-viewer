import pytest
from bs4 import BeautifulSoup
from spec_viewer.build import build


@pytest.mark.parametrize("base_url", ["", "/viewer"])
def test_nested_fields_guidance_and_links(tmp_path, base_url):
    source = tmp_path / "source"
    files = {
        "field/choice.md": "field: choice\nname: Choice\ndatatype: enum\ncodelist: choices",
        "field/details.md": "field: details\nname: Details\ndatatype: object\ncomponent: details",
        "component/details.md": "component: details\nname: Details\nfields:\n  - field: choice\n    required: true",
        "module/proposal.schema.md": "module: proposal\nname: Proposal\nfields:\n  - field: details\n    required: true",
        "codelist/choices.schema.md": "codelist: choices\nname: Choices\nsource:\n  src: https://example.com/choices.csv",
    }
    for name, content in files.items():
        path = source / "specification" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\n" + content + "\n---\n")
    guide = source / "specification/guidance/module/proposal/field/choice.md"
    guide.parent.mkdir(parents=True)
    guide.write_text("---\nmodule: proposal\nfield: choice\n---\nExplain this choice.")
    output = tmp_path / "site"
    build(source, output, base_url)
    data_model = BeautifulSoup((output / "data-model/index.html").read_text(), "html.parser")
    assert "Select a marker to explore each part and how it connects to the others." in data_model.get_text(" ", strip=True)
    assert "How an application submission is structured" in data_model.get_text(" ", strip=True)
    assert "How planning authorities record information" in data_model.get_text(" ", strip=True)
    assert "How views select information" in data_model.get_text(" ", strip=True)
    assert data_model.select_one('[data-embed-id="planning-spec-three-parts-no-a6"]')
    assert len(data_model.select(".ia-hotspot")) == 5
    assert not data_model.select_one('[data-annotation-id="A6"]')
    assert data_model.find("a", href=f"{base_url}/view/national-public/")
    assert data_model.find("a", href=f"{base_url}/view/national-public/info/")
    assert not data_model.find("h2", string="Model elements")
    module = (output / "module/proposal/index.html").read_text()
    assert "Details component" in module
    assert "Explain this choice." in module
    assert f'href="{base_url}/codelist/choices"' in module
    component = (output / "component/details/index.html").read_text()
    assert f'href="{base_url}/module/proposal"' in component
    codelist = (output / "codelist/choices/index.html").read_text()
    assert 'href="https://example.com/choices.csv"' in codelist
    assert f'href="{base_url}/field/choice"' in codelist
    for family in ["module", "component", "codelist"]:
        soup = BeautifulSoup((output / family / "index.html").read_text(), "html.parser")
        assert soup.select_one(f"[data-{family}s-search]")
        assert "initIndexSearch" in str(soup)
