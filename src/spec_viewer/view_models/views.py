"""Presentation of package-resolved public view definitions."""


def applicability_note(field):
    condition = field.dataset_field.applies_if or {}
    application_types = condition.get("application-types", {}).get("in", []) if isinstance(condition, dict) else []
    if set(application_types) == {"full", "outline-all", "outline-some"}:
        return "Only for full and outline planning applications."
    return ""


def build_national_public_view_datasets(view, url_for):
    datasets = []
    for dataset in view.datasets():
        fields = []
        for field in view.resolve_container_items(dataset=dataset.ref):
            target = field.target_dataset
            codelist = field.codelist
            fields.append({
                "ref": field.ref, "name": field.name, "description": field.description,
                "datatype": field.datatype, "cardinality": field.cardinality,
                "requirement_level": field.requirement_level,
                "field_href": url_for(f"/field/{field.ref}"),
                "target_dataset": target,
                "target_dataset_href": url_for(f"/dataset/{target}") if target else "",
                "codelist": codelist,
                "codelist_href": url_for(f"/codelist/{codelist}") if codelist else "",
                "applicability": applicability_note(field),
            })
        rule = dataset.record_inclusion
        datasets.append({
            "ref": dataset.ref, "name": dataset.name, "description": dataset.description,
            "href": url_for(f"/view/national-public/#{dataset.ref}"),
            "fields": fields, "record_inclusion": rule,
            "publishing_rule": rule.get("description") if rule else "Publish all records.",
        })
    return datasets
