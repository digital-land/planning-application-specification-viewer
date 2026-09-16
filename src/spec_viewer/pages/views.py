"""Render the views index, public contract and explanatory page."""
from spec_viewer.pages.data_model import write_page
from spec_viewer.view_models.views import build_national_public_view_datasets

REQUIREMENT_LEVELS_DOCUMENTATION_URL = (
    "https://github.com/digital-land/planning-application-data-specification/"
    "blob/main/documentation/requirement-levels.md"
)


def render_views(specification, environment, output_dir):
    public_view = specification.tables["specification"].get("national-public-view")
    if public_view is None:
        return 0
    url_for = environment.globals["url_for"]
    datasets = build_national_public_view_datasets(public_view, specification.tables["dataset"], specification.fields, url_for)
    write_page(environment, output_dir, "view", "view_index.html", {
        "page_title": "Views", "views": [{"name": public_view.get("name", "National public view"),
            "description": "The data that planning authorities must publish as open data.", "href": url_for("/view/national-public/")}],
    })
    write_page(environment, output_dir, "view/national-public", "national_public_view.html", {
        "page_title": "National public view", "specification_status": public_view.get("specification-status"), "datasets": datasets,
        "raw_schema_href": "https://github.com/digital-land/planning-application-data-specification/blob/main/specification/national-public-view.schema.md?plain=1",
        "info_href": url_for("/view/national-public/info/"), "requirement_levels_href": REQUIREMENT_LEVELS_DOCUMENTATION_URL,
    })
    write_page(environment, output_dir, "view/national-public/info", "national_public_view_info.html", {
        "page_title": "About the national public view", "public_view_href": url_for("/view/national-public/"),
        "documentation_href": "https://github.com/digital-land/planning-application-data-specification/blob/main/documentation/national-public-view.md",
        "derivation_href": "https://github.com/digital-land/planning-application-data-specification/blob/main/documentation/required-national-public-view-output-and-rules-for-deriving-it.md",
    })
    return 3
