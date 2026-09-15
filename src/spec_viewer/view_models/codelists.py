"""Codelist metadata and usage links for the viewer."""
from spec_viewer.view_models.containers import linked_record

SOURCE_REPOSITORY = "https://github.com/digital-land/planning-application-data-specification/blob/main/"


def source_link(ref, metadata):
    source = metadata.get("source")
    source = source.get("src") if isinstance(source, dict) else source
    if source:
        return SOURCE_REPOSITORY + source if source.startswith("data/") else source
    return SOURCE_REPOSITORY + f"data/codelist/{ref}.csv"


def codelist_detail(specification, metadata, url_for):
    ref = metadata["codelist"]
    usages = specification.codelist_usages(ref)
    usage = {"fields": [linked_record(field, "field", url_for) for field in usages.fields]}
    for collection, route in [("modules", "module"), ("components", "component")]:
        usage[collection] = [
            {**linked_record(match.container, route, url_for), "field_ref": match.usage.original.ref}
            for match in getattr(usages, collection)
        ]
    return {"page_title": f"Codelist {ref}", "codelist": metadata,
            "source_link": source_link(ref, metadata), "usage": usage}
