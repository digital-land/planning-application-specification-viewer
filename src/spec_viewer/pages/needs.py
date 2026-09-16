"""User needs and justification pages from the package needs loader."""
from typing import Any, Dict, List
from markdown import markdown as render_markdown
from spec_viewer.view_models.needs import build_need_maps, need_status, need_status_dict, build_need_meta, justification_search_references


def write_html(output_dir, route, html):
    target = output_dir / route / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


def render_justifications_index(
    environment, output_dir,
    justifications: List[Dict[str, Any]],
) -> None:
    url_for = environment.globals["url_for"]
    # Justification index page
    justification_index_ctx = {
        "page_title": "Justifications",
        "justifications": [
            {
                "id": j.get("id"),
                "needs": [
                    f'<a class="govuk-link" href="{url_for(f"/user-need/{n}")}">{n}</a>'
                    for n in j.get("needs", [])
                ],
                "satisfaction": j.get("satisfaction", ""),
                "confidence": j.get("confidence", ""),
                "status": j.get("status", ""),
                "search_references": justification_search_references(j.get("satisfied_by", {})),
                "search_body": render_markdown(
                    getattr(j, "content", "") or j.get("body", "") or j.get("notes", "") or ""
                ),
                "href": url_for(f"/justification/{j.get('id')}"),
            }
            for j in justifications
        ],
    }
    justification_index_template = environment.get_template("justification_index.html").render(**justification_index_ctx)
    write_html(output_dir, "justification", justification_index_template)

def render_needs(data, environment, output_dir):
    url_for = environment.globals["url_for"]
    needs_data = {"need": data.needs, "justification": data.justifications}
    need_records = sorted(data.needs.values(), key=lambda need: need.get("need", ""))
    need_to_justifications, _ = build_need_maps(needs_data)
    # Planning application data specification needs list
    needs_ctx = {
        "page_title": "Planning application data needs",
        "needs": [
            {
                "id": need.get("need"),
                "scope": need.get("scope") or "unspecified",
                "themes": need.get("themes") or [],
                "actors": need.get("actors") or [],
                "name": need.get("name", ""),
                "statement": need.get("statement") or need.get("name") or "",
                "href": url_for(f"/user-need/{need.get('need')}"),
                **need_status_dict(
                    need_to_justifications.get(need.get("need"), [])
                ),
            }
            for need in need_records
        ],
    }
    needs_ctx["facets"] = [
        {"name": "scope", "label": "Scope", "options": [("in", "In scope"), ("out-of-spec", "Out of scope")] + ([("unspecified", "Not specified")] if any(n["scope"] == "unspecified" for n in needs_ctx["needs"]) else [])},
        {"name": "satisfaction", "label": "Satisfaction", "options": [("full", "Satisfied"), ("partial", "Partially satisfied"), ("none", "Not satisfied")]},
    ] + [
        {"name": name, "label": label, "options": [(value, value.replace("-", " ").capitalize()) for value in sorted({value for need in needs_ctx["needs"] for value in need[key]})]}
        for name, label, key in [("theme", "Themes", "themes"), ("actor", "Actors", "actors")]
    ]
    needs_html = environment.get_template("needs_index.html").render(**needs_ctx)
    write_html(output_dir, "user-need", needs_html)

    # Planning application data specification need detail pages
    need_template = environment.get_template("need_detail.html")
    for need in need_records:
        n_id = need.get("need")
        justs = need_to_justifications.get(n_id, [])
        label, cls = need_status(justs)
        need_meta = build_need_meta(need)
        need_ctx = {
            "need_ref": n_id,
            "page_title": f"Need {n_id}",
            "links": {"back": url_for("/user-need")},
            "tag_label": label,
            "tag_class": cls,
            "title": need.get("name") or n_id,
            "statement": need.get("statement") or "",
            "meta": need_meta,
            "justifications": [
                {
                    "id": j.get("id", ""),
                    "satisfaction": j.get("satisfaction", ""),
                    "confidence": j.get("confidence", ""),
                    "notes": j.get("notes", ""),
                    "body": j.get("__body__", ""),
                    "satisfied_by": j.get("satisfied_by"),
                    "href": url_for(f"/justification/{j.get('id', '')}"),
                }
                for j in justs
            ],
        }
        need_html = need_template.render(**need_ctx)
        write_html(output_dir, f"user-need/{n_id}", need_html)

    # Justification index and detail pages
    justification_template = environment.get_template("justification_detail.html")
    justifications = list(needs_data.get("justification", {}).values())
    justifications.sort(key=lambda j: j.get("id", ""))

    render_justifications_index(environment, output_dir, justifications)

    for j in justifications:
        j_ctx = {
            "page_title": f"Justification {j.get('id')}",
            "id": j.get("id", ""),
            "needs": j.get("needs", []),
            "needs_links": [
                f'<a class="govuk-link" href="{url_for(f"/user-need/{n}")}">{n}</a>'
                for n in j.get("needs", [])
            ],
            "satisfaction": j.get("satisfaction", ""),
            "confidence": j.get("confidence", ""),
            "status": j.get("status", ""),
            "body": render_markdown(
                getattr(j, "content", "")
                or j.get("body", "")
                or j.get("notes", "")
                or ""
            ),
            "raw": j,
            "links": {"back": url_for("/justification")},
            "github_issue_url": f"https://github.com/digital-land/planning-application-data-specification/issues/new?title=Feedback%20on%20justification%20{j.get('id')}",
            "github_edit_url": f"https://github.com/digital-land/planning-application-data-specification/edit/main/user-needs/justification/{j.get('id')}.md",
        }
        j_html = justification_template.render(**j_ctx)
        write_html(output_dir, f"justification/{j.get('id')}", j_html)

    return 2 + len(need_records) + len(justifications)
