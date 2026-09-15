from pathlib import Path

import pytest

from spec_viewer.data import load_viewer_data


def test_loads_explicit_source_from_another_directory(tmp_path, monkeypatch):
    source = tmp_path / "source"
    files = {
        "specification/field/description.md": "---\nfield: description\nname: Description\ndatatype: string\n---\nField explanation.\n",
        "user-needs/need/001.md": "---\nneed: '001'\nname: Understand an application\n---\nNeed explanation.\n",
        "user-needs/justification/001.md": "---\nid: justification-001\n---\nJustification explanation.\n",
    }
    for name, content in files.items():
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    data = load_viewer_data(source)

    assert Path.cwd() == elsewhere
    assert data.specification.source_path == source
    assert data.specification.field("description").name == "Description"
    assert data.specification.field("description").body == "Field explanation."
    assert data.needs["001"]["__body__"] == "Need explanation."
    assert data.justifications["justification-001"]["__body__"] == "Justification explanation."


def test_invalid_explicit_source_does_not_fall_back_to_working_directory(tmp_path, monkeypatch):
    (tmp_path / "specification").mkdir()
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError, match="Could not find a specification directory"):
        load_viewer_data(tmp_path / "missing")
