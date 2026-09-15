from types import SimpleNamespace
import pytest
from spec_viewer.data import load_viewer_data
from spec_viewer.pages.datasets import render_datasets
from spec_viewer.rendering import create_environment


@pytest.mark.parametrize("base_url", ["", "/viewer"])
def test_dataset_profile_overrides_guidance_and_needs(tmp_path, base_url):
    source = tmp_path / "source"
    files = {
        "field/reference.md": "field: reference\nname: Reference\ndescription: Base description",
        "dataset/record.schema.md": "dataset: record\nname: Record\nfields:\n  - field: reference",
        "planning-application-data.schema.md": "specification: planning-application-data\ndatasets:\n  - dataset: record\n    name: Profile record\n    fields:\n      - field: reference\n        description: profile description\n        requirement-level: MUST\n        dataset: related",
        "guidance/dataset/record/field/reference.md": "dataset: record\nfield: reference",
    }
    for name, text in files.items():
        path = source / "specification" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\n" + text + "\n---\n" + ("Guidance for the reference." if name.startswith("guidance") else ""))
    data = load_viewer_data(source)
    data.justifications = {
        "whole": {"needs": ["N1"], "satisfied_by": [{"dataset": "record"}], "satisfaction": "full"},
        "field": {"needs": ["N2"], "satisfied_by": {"anyOf": [{"dataset": "record", "field": "reference"}, {"dataset": "related", "field": "name"}]}},
    }
    output = tmp_path / "site"
    assert render_datasets(data, create_environment(base_url), output) == 2
    html = (output / "dataset/record/index.html").read_text()
    assert "Profile record" in html
    assert "Profile description" in html
    assert "Base description" not in html
    assert "MUST" in html
    assert "Guidance for the reference." in html
    assert f'href="{base_url}/dataset/related"' in html
    assert f'href="{base_url}/user-need/N1"' in html
    assert f'href="{base_url}/user-need/N2"' in html
    assert "This field or field" in html
