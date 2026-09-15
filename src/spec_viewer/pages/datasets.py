"""Render datasets selected by the planning application data specification."""
from markdown import markdown
from spec_viewer.pages.data_model import write_page
from spec_viewer.rendering import PROJECT_ROOT
from spec_viewer.markdown import render_govuk_markdown
from spec_viewer.view_models.containers import guidance_html
from spec_viewer.view_models.dataset_examples import render_dataset_examples_content
from spec_viewer.view_models.needs import build_need_maps, satisfaction_messages_for_field


def render_datasets(data, environment, output_dir):
    specification = data.specification
    url_for = environment.globals["url_for"]
    profile = specification.tables["specification"].get("planning-application-data", {})
    datasets = [{**specification.tables["dataset"].get(entry["dataset"], {}), **entry} for entry in profile.get("datasets", [])]
    write_page(environment, output_dir, "dataset", "dataset_index.html", {
        "page_title": "Datasets",
        "datasets": [{"name": ds.get("name", ds["dataset"]), "description": ds.get("description", ""), "href": url_for(f"/dataset/{ds['dataset']}")} for ds in datasets],
        "links": {"needs": url_for("/user-need"), "github_feedback": "https://github.com/digital-land/planning-application-data-specification/issues/new"},
    })
    need_map, dataset_map = build_need_maps({"need": data.needs, "justification": data.justifications})
    all_justifications = [(need, justification) for need, records in need_map.items() for justification in records]
    for dataset in datasets:
        ref = dataset["dataset"]
        fields = []
        for entry in dataset.get("fields", []):
            field_ref = entry["field"]
            base = specification.fields.get(field_ref)
            target = entry.get("dataset")
            fields.append({
                "ref": field_ref, "name": entry.get("name") or (base.name if base else field_ref),
                "description": render_govuk_markdown(entry.get("description") or (base.description if base else ""), capitalise=True),
                "cardinality": entry.get("cardinality") or (base.cardinality if base else "1"),
                "datatype": entry.get("datatype") or (base.datatype if base else "string"),
                "codelist": entry.get("codelist") or (base.codelist if base else None),
                "requirement_level": entry.get("requirement-level"),
                "target_dataset": target, "target_dataset_href": url_for(f"/dataset/{target}") if target else "",
                "guidance": guidance_html(specification.guidance(dataset=ref, field=field_ref)),
                "satisfactions": satisfaction_messages_for_field(all_justifications, ref, field_ref, url_for),
            })
        needs = []
        for item in dataset_map.get(ref, []):
            justification = item["justification"]
            needs.append({
                "need_id": item["need"], "need_href": url_for(f"/user-need/{item['need']}"),
                "just_id": justification.get("id", ""), "satisfaction": justification.get("satisfaction", "justification"),
                "confidence": justification.get("confidence", ""), "notes": markdown(justification.get("notes", "") or ""),
                "justification_body": markdown(getattr(justification, "content", "") or justification.get("body", "") or justification.get("notes", "") or ""),
                "requires_dataset": True,
            })
        write_page(environment, output_dir, f"dataset/{ref}", "dataset_detail.html", {
            "page_title": f"Dataset {ref}", "title": dataset.get("name", ref), "description": dataset.get("description", ""),
            "guidance": guidance_html(specification.guidance(dataset=ref)), "fields": fields, "needs": needs,
            "examples": render_dataset_examples_content(dataset_ref=ref, allowed_fields={field["ref"] for field in fields},
                examples_root=specification.source_path / "specification/example/dataset", content_root=PROJECT_ROOT / "content", template_environment=environment),
        })
    return len(datasets) + 1
