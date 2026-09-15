"""Application page contexts using package definitions and authored display metadata."""
import csv
from planning_application_specification.applications import get_active_combined_application_refs
from planning_application_specification.models import ComponentUsage, FieldUsage
from spec_viewer.view_models.containers import linked_record


def combined_applications(specification):
    # The package owns approval/resolution. The CSV preserves the original index
    # ordering and its exclusion of ended entries, neither exposed by that query.
    active = get_active_combined_application_refs(specification.tables)
    path = specification.source_path / "specification/combined-application-types.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as stream:
        return [specification.application(row["application-types"]) for row in csv.DictReader(stream)
                if row["application-types"] in active and not (row.get("end-date") or "").strip()]


def authored_fields(specification, ref, visited=None):
    """Retain the original field order and inheritance labels for display.

    ApplicationDef currently resolves inherited modules, but not inherited
    application-level fields or their provenance. Use package-loaded metadata.
    """
    visited = set() if visited is None else visited
    if ref in visited:
        return []
    visited.add(ref)
    record = specification.tables["application"][ref]
    parents = record.get("extends") or []
    parents = [parents] if isinstance(parents, str) else parents
    fields = {}
    for parent in parents:
        if parent in specification.tables["application"]:
            for entry, origin in authored_fields(specification, parent, visited):
                fields[entry["field"]] = (entry, origin or parent)
    for entry in record.get("fields", []) or []:
        fields[entry["field"]] = (entry, None)
    return list(fields.values())


def field_display(specification, entry, origin=None):
    ref = entry["field"]
    field = specification.fields.get(ref)
    return {"ref": ref, "name": entry.get("name") or (field.name if field else ref),
            "description": entry.get("description") or (field.description if field else ""),
            "required": entry.get("required"), "inherited_from": origin}


def combined_fields(application):
    fields = []
    for item in application.items:
        if isinstance(item, ComponentUsage):
            item = item.referenced_by_field
        if item is None:
            continue
        field = item.original if isinstance(item, FieldUsage) else item
        overrides = item.overrides if isinstance(item, FieldUsage) else {}
        fields.append({"ref": field.ref, "name": overrides.get("name") or field.name,
                       "description": overrides.get("description") or field.description,
                       "required": overrides.get("required") if overrides.get("required") is not None else field.required,
                       "inherited_from": None})
    return fields


def application_detail(specification, application, url_for):
    record = {} if application.is_combined else specification.tables["application"][application.ref]
    parents = record.get("extends") or []
    parents = [parents] if isinstance(parents, str) else parents
    own_modules = {item if isinstance(item, str) else item.get("module") for item in record.get("modules", []) or []}
    # Inherited modules use package order; non-inherited modules retain authored order.
    modules = application.modules
    if not parents and not application.is_combined:
        modules = [specification.modules[ref] for item in record.get("modules", []) or []
                   if (ref := item if isinstance(item, str) else item.get("module")) in specification.modules]
    return {
        "page_title": f"Application {application.ref}", "title": application.name,
        "description": application.description, "application": application.ref,
        "application_types": application.application_types if application.is_combined else [],
        "base_type": record.get("base-type", False),
        "extends": {"ref": record["extends"], "href": url_for(f"/application-type/{record['extends']}")} if parents else None,
        "synonyms": application.synonyms, "notes": application.notes,
        "entry_date": application.entry_date, "legislation": application.legislation,
        "fields": combined_fields(application) if application.is_combined else [field_display(specification, entry, origin) for entry, origin in authored_fields(specification, application.ref)],
        "modules": [{**linked_record(module, "module", url_for), "description": module.description or "",
                     "inherited_from": ", ".join(parents) if parents and module.ref not in own_modules else None} for module in modules],
        "links": {"back": url_for("/application-type")},
    }
