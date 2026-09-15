"""Present resolved package containers without owning specification rules."""
from spec_viewer.markdown import render_govuk_markdown


def guidance_html(guidance):
    return render_govuk_markdown(guidance.content) if guidance else ""


def container_fields(specification, kind, ref, guidance_container=None):
    guidance_container = guidance_container or {kind: ref}
    fields = []
    for item in specification.resolve_container_items(**{kind: ref}):
        component = getattr(item, "component_ref", None)
        definition = specification.component(component) if component else None
        fields.append({
            "ref": item.ref, "name": item.name, "description": item.description,
            "datatype": item.datatype, "required": item.required,
            "cardinality": item.cardinality,
            "codelist": item.usage.overrides.get("codelist") or item.base.codelist,
            "component_ref": component,
            "component_name": (definition.name or definition.ref) if definition else None,
            "children": container_fields(specification, "component", component, guidance_container) if component else [],
            "guidance": guidance_html(specification.guidance(field=item.ref, **guidance_container)),
        })
    return fields


def linked_record(record, route, url_for):
    return {"ref": record.ref, "name": record.name or record.ref,
            "href": url_for(f"/{route}/{record.ref}")}


def container_usage(specification, kind, ref, url_for):
    if kind == "module":
        return {"applications": [
            {**linked_record(app, "application-type", url_for), "is_combined": bool(app.is_combined)}
            for app in specification.applications_with_module(ref)
        ]}
    usages = specification.component_usages(ref)
    return {
        "fields": [linked_record(field, "field", url_for) for field in usages.fields],
        "modules": [linked_record(match.container, "module", url_for) for match in usages.modules],
    }


def container_detail(specification, kind, record, url_for):
    context = {
        "page_title": f"{kind.capitalize()} {record.ref}", "ref": record.ref,
        "name": record.name or record.ref, "description": record.description or "",
        "guidance": guidance_html(specification.guidance(**{kind: record.ref})),
        "fields": container_fields(specification, kind, record.ref),
        "rules": specification.tables[kind][record.ref].get("rules", []),
        "usage": container_usage(specification, kind, record.ref, url_for),
    }
    if kind == "module":
        context["links"] = {"back": url_for("/module")}
    else:
        context["breadcrumbs"] = []
    return context
