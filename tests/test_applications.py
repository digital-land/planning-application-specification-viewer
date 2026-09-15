from pathlib import Path

from bs4 import BeautifulSoup
import pytest
import yaml

from spec_viewer.data import load_viewer_data
from spec_viewer.pages.applications import render_applications
from spec_viewer.rendering import create_environment
from spec_viewer.view_models.applications import application_detail


@pytest.mark.parametrize("base_url", ["", "/viewer"])
def test_application_inheritance_combinations_and_index(tmp_path, base_url):
    source = tmp_path / "source"
    def record(kind, ref, **metadata):
        path = source / "specification" / kind / f"{ref}.schema.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\n" + yaml.safe_dump({kind: ref, "name": ref, **metadata}, sort_keys=False) + "---\n")
    record("field", "reference", description="Canonical reference")
    record("field", "name", description="Canonical name")
    record("module", "shared", fields=[])
    record("module", "extra", fields=[])
    record("application", "base", **{"base-type": True}, fields=[{"field": "reference", "required": True}, {"field": "name", "required": True}], modules=[{"module": "shared"}])
    record("application", "child", extends="base", fields=[{"field": "name", "name": "Child name", "required": False}], modules=[{"module": "extra"}])
    record("application", "other", fields=[{"field": "reference", "required": True}], modules=[{"module": "shared"}])
    (source / "specification/combined-application-types.csv").write_text(
        "application-types,name,description,start-date,end-date\n"
        "child;other,Approved combination,Combined description,2026-01-01,\n"
        "base;other,Future combination,Future description,,\n"
        "base;child,Ended combination,Ended description,2025-01-01,2025-12-31\n"
    )
    specification = load_viewer_data(source).specification
    environment = create_environment(base_url)
    context = application_detail(specification, specification.application("child"), environment.globals["url_for"])
    assert [(field["ref"], field["required"], field["inherited_from"]) for field in context["fields"]] == [("reference", True, "base"), ("name", False, None)]
    assert context["fields"][1]["name"] == "Child name"
    assert [(module["ref"], module["inherited_from"]) for module in context["modules"]] == [("extra", None), ("shared", "base")]
    output = tmp_path / "site"
    assert render_applications(specification, environment, output) == 5
    index = BeautifulSoup((output / "application-type/index.html").read_text(), "html.parser")
    assert [a["href"] for a in index.select("[data-individual-application-type] a")] == [f"{base_url}/application-type/child", f"{base_url}/application-type/other"]
    assert [a["href"] for a in index.select("[data-combined-application-type] a")] == [f"{base_url}/application-type/child;other"]
    assert index.select_one("[data-application-types-search]")
    assert "Base type" in (output / "application-type/base/index.html").read_text()
    combined = BeautifulSoup((output / "application-type/child;other/index.html").read_text(), "html.parser")
    assert {a["href"] for a in combined.select('a[href*="/module/"]')} == {f"{base_url}/module/extra", f"{base_url}/module/shared"}
    assert "Combined description" in combined.get_text()
