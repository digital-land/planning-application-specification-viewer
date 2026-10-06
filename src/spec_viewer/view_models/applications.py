"""Application page contexts using package definitions and authored display metadata."""
from planning_application_specification.models import ComponentUsage, FieldUsage
from spec_viewer.view_models.containers import linked_record


def combined_applications(specification):
    """Use package-owned ordering, resolution and current-status rules."""
    return list(specification.combined_applications())


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
    parents = application.extends or []
    parents = [parents] if isinstance(parents, str) else parents
    return {
        "page_title": f"Application {application.ref}", "title": application.name,
        "description": application.description, "application": application.ref,
        "application_types": application.application_types if application.is_combined else [],
        "base_type": application.is_base_type,
        "extends": {"ref": parents[0], "href": url_for(f"/application-type/{parents[0]}")} if len(parents) == 1 else None,
        "extends_many": [{"ref": parent, "href": url_for(f"/application-type/{parent}")} for parent in parents] if len(parents) > 1 else [],
        "synonyms": application.synonyms, "notes": application.notes,
        "entry_date": application.entry_date, "legislation": application.legislation,
        "fields": combined_fields(application) if application.is_combined else [field_display(specification, item.definition, item.inherited_from) for item in application.resolved_fields],
        "modules": [{**linked_record(usage.module, "module", url_for), "description": usage.module.description or "",
                     "inherited_from": ", ".join(usage.included_by) if usage.is_inherited else None}
                    for usage in application.resolved_modules],
        "links": {"back": url_for("/application-type")},
    }
