from types import SimpleNamespace
import pytest
from spec_viewer.pages.views import render_views
from spec_viewer.rendering import create_environment
from spec_viewer.view_models.views import build_national_public_view_datasets


@pytest.mark.parametrize("base_url", ["", "/viewer"])
def test_view_selection_rules_and_links(tmp_path, base_url):
    fields = {"choice": SimpleNamespace(name="Choice", description="A choice", datatype="enum", cardinality="1", codelist="choices")}
    dataset = {"name": "Record", "fields": [{"field": "choice", "applies-if": {"application-types": {"in": ["full", "outline-all", "outline-some"]}}}]}
    view = {"name": "National public view", "datasets": [{"dataset": "record", "record-inclusion": {"description": "Publish selected records."}, "fields": [{"field": "choice", "requirement-level": "MUST", "dataset": "related"}]}]}
    spec = SimpleNamespace(tables={"specification": {"national-public-view": view}, "dataset": {"record": dataset, "excluded": {}}}, fields=fields)
    environment = create_environment(base_url)
    records = build_national_public_view_datasets(view, spec.tables["dataset"], fields, environment.globals["url_for"])
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
