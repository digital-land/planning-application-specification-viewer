import yaml
from planning_application_specification import Specification
import pytest
from spec_viewer.pages.views import render_views
from spec_viewer.rendering import create_environment
from spec_viewer.view_models.views import build_national_public_view_datasets


@pytest.mark.parametrize("base_url", ["", "/viewer"])
def test_view_selection_rules_and_links(tmp_path, base_url):
    source = tmp_path / "source"
    def record(relative, metadata):
        path = source / "specification" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---\n")
    record("field/choice.md", {"field": "choice", "name": "Choice", "description": "A choice", "datatype": "enum", "codelist": "choices"})
    record("dataset/record.schema.md", {"dataset": "record", "name": "Record", "fields": [{"field": "choice", "applies-if": {"application-types": {"in": ["full", "outline-all", "outline-some"]}}}]})
    record("national-public-view.schema.md", {"specification": "national-public-view", "name": "National public view", "datasets": [{"dataset": "record", "record-inclusion": {"description": "Publish selected records.", "field": "choice", "include-values": ["publish"]}, "fields": [{"field": "choice", "requirement-level": "MUST", "dataset": "related"}]}]})
    spec = Specification.load(source)
    view = spec.view("national-public")
    environment = create_environment(base_url)
    records = build_national_public_view_datasets(view, environment.globals["url_for"])
    assert [record["ref"] for record in records] == ["record"]
    assert records[0]["publishing_rule"] == "Publish selected records."
    field = records[0]["fields"][0]
    assert field["requirement_level"] == "MUST"
    assert field["applicability"] == "Only for full and outline planning applications."
    assert field["codelist_href"] == f"{base_url}/codelist/choices"
    assert field["target_dataset_href"] == f"{base_url}/dataset/related"
    assert render_views(spec, environment, tmp_path) == 3
    html = (tmp_path / "view/national-public/index.html").read_text()
    assert "Publish selected records." in html
    assert f'href="{base_url}/view/national-public/info/"' in html
    assert (tmp_path / "view/national-public/info/index.html").is_file()
