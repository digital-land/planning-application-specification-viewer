"""Render the data model landing page and its container/codelist families."""
from spec_viewer.view_models.containers import container_detail, linked_record
from spec_viewer.view_models.codelists import codelist_detail


def write_page(environment, output_dir, path, template, context):
    target = output_dir / path / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(environment.get_template(template).render(**context), encoding="utf-8")


def render_data_model(specification, environment, output_dir):
    url_for = environment.globals["url_for"]
    write_page(environment, output_dir, "data-model", "data_model.html", {
        "page_title": "Data model",
        "links": {key: url_for(f"/{route}/") for key, route in [
            ("application_types", "application-type"), ("modules", "module"),
            ("components", "component"), ("fields", "field"), ("codelists", "codelist"),
            ("datasets", "dataset"), ("needs", "user-need"),
            ("justifications", "justification"), ("design_decisions", "design-decision"),
        ]},
    })
    count = 1
    for kind, collection in [("module", specification.modules), ("component", specification.components)]:
        records = sorted(collection.values(), key=lambda record: (record.name or record.ref) if kind == "module" else record.ref)
        context = {
            "page_title": kind.capitalize() + "s",
            kind + "s": [{**linked_record(record, kind, url_for), "description": record.description or ""} for record in records],
        }
        if kind == "module":
            context["links"] = {"back": url_for("/data-model")}
        else:
            context["breadcrumbs"] = []
        write_page(environment, output_dir, kind, f"{kind}_index.html", context)
        for record in records:
            write_page(environment, output_dir, f"{kind}/{record.ref}", f"{kind}_detail.html", container_detail(specification, kind, record, url_for))
        count += len(records) + 1
    codelists = sorted(specification.tables["codelist"].values(), key=lambda record: record["codelist"])
    write_page(environment, output_dir, "codelist", "codelist_index.html", {
        "page_title": "Codelists",
        "codelists": [{"ref": record["codelist"], "codelist": record["codelist"],
                       "name": record.get("name", record["codelist"]),
                       "description": record.get("description", ""),
                       "href": url_for(f"/codelist/{record['codelist']}")} for record in codelists],
    })
    for record in codelists:
        write_page(environment, output_dir, f"codelist/{record['codelist']}", "codelist_detail.html", codelist_detail(specification, record, url_for))
    return count + len(codelists) + 1
