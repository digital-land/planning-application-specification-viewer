"""Public view presentation from package-loaded specification metadata."""
from types import SimpleNamespace
from typing import Any, Dict, List


def build_field_display(entry, fields):
    ref = entry["field"]
    base = fields.get(ref)
    def effective(key, default):
        return entry.get(key) or getattr(base, key, default)
    return SimpleNamespace(ref=ref, name=effective("name", ref), description=effective("description", ""),
                           datatype=effective("datatype", "string"), cardinality=effective("cardinality", "1"),
                           codelist=effective("codelist", None), requirement_level=entry.get("requirement-level"))


def national_public_view_field_applicability(
    dataset: Dict[str, Any], field_ref: str
) -> str:
    """Return the one explicit public-view field applicability note, if present."""
    for field in dataset.get("fields", []):
        if field.get("field") != field_ref:
            continue
        application_types = (
            field.get("applies-if", {}).get("application-types", {}).get("in", [])
        )
        if set(application_types) == {"full", "outline-all", "outline-some"}:
            return "Only for full and outline planning applications."
    return ""

def build_national_public_view_datasets(
    public_view: Dict[str, Any],
    dataset_index: Dict[str, Dict[str, Any]],
    field_index: Dict[str, Any],
    url_for,
) -> List[Dict[str, Any]]:
    datasets: List[Dict[str, Any]] = []

    for view_dataset in public_view.get("datasets", []):
        dataset_ref = view_dataset["dataset"]
        dataset = dataset_index.get(dataset_ref, {})
        fields = []
        for field in view_dataset.get("fields", []):
            field_view = build_field_display(field, field_index)
            target_dataset = field.get("dataset")
            fields.append(
                {
                    "ref": field_view.ref,
                    "name": field_view.name,
                    "description": field_view.description,
                    "datatype": field_view.datatype,
                    "cardinality": field_view.cardinality,
                    "requirement_level": field_view.requirement_level,
                    "field_href": url_for(f"/field/{field_view.ref}"),
                    "target_dataset": target_dataset,
                    "target_dataset_href": (
                        url_for(f"/dataset/{target_dataset}")
                        if target_dataset
                        else ""
                    ),
                    "codelist": field_view.codelist,
                    "codelist_href": (
                        url_for(f"/codelist/{field_view.codelist}")
                        if field_view.codelist
                        else ""
                    ),
                    "applicability": national_public_view_field_applicability(
                        dataset, field_view.ref
                    ),
                }
            )

        record_inclusion = view_dataset.get("record-inclusion")
        datasets.append(
            {
                "ref": dataset_ref,
                "name": view_dataset.get("name") or dataset.get("name") or dataset_ref,
                "description": dataset.get("description", ""),
                "href": url_for(f"/view/national-public/#{dataset_ref}"),
                "fields": fields,
                "record_inclusion": record_inclusion,
                "publishing_rule": (
                    record_inclusion.get("description")
                    if record_inclusion
                    else "Publish all records."
                ),
            }
        )
    return datasets
