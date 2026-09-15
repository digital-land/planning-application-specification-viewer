"""Render individual, base and combined application types."""
from spec_viewer.pages.data_model import write_page
from spec_viewer.view_models.applications import application_detail, combined_applications


def render_applications(specification, environment, output_dir):
    url_for = environment.globals["url_for"]
    applications = [specification.application(ref) for ref in sorted(specification.applications)]
    combined = combined_applications(specification)
    def index_record(application):
        return {"name": application.name, "description": application.description,
                "href": url_for(f"/application-type/{application.ref}")}
    write_page(environment, output_dir, "application-type", "submission_index.html", {
        "page_title": "Application types",
        "applications": [index_record(app) for app in applications if not specification.tables["application"][app.ref].get("base-type")],
        "combined_applications": [index_record(app) for app in combined],
        "links": {"progress": url_for("/submissions/progress"),
                  "combined_application_decision": url_for("/design-decision/0012-use-a-controlled-list-for-combined-application-types/")},
    })
    for application in applications + combined:
        write_page(environment, output_dir, f"application-type/{application.ref}", "submission_application_detail.html", application_detail(specification, application, url_for))
    return 1 + len(applications) + len(combined)
