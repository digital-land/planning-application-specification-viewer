"""Field presentation built from package models and usage queries."""
import re
from markupsafe import Markup
from spec_viewer.markdown import render_govuk_markdown


def field_markdown(text, url_for):
    soup = render_govuk_markdown(text, make_safe=False)
    for link in soup.select("a[href]"):
        match = re.fullmatch(r"([^/#]+)\.md(#[^#]*)?", link["href"])
        if match:
            link["href"] = url_for(f"/field/{match.group(1)}") + (match.group(2) or "")
    return Markup(str(soup))


def field_index(specification, url_for):
    return {
        "page_title": "Fields",
        "fields": [
            {"ref": field.ref, "name": field.name, "description": field.description,
             "href": url_for(f"/field/{field.ref}")}
            for field in sorted(specification.fields.values(), key=lambda field: field.ref)
        ],
    }


def field_detail(specification, field, url_for):
    usages = specification.field_usages(field.ref)
    usage = {
        collection: [
            {"ref": match.container.ref,
             "name": match.container.name or match.container.ref,
             "href": url_for(f"/{route}/{match.container.ref}")}
            for match in getattr(usages, collection)
        ]
        for collection, route in [("datasets", "dataset"), ("modules", "module"), ("components", "component")]
    }
    return {
        "page_title": f"Field {field.ref}", "field": field,
        "field_notes": field_markdown(field.notes, url_for),
        "field_body": field_markdown(field.body, url_for), "usage": usage,
    }
