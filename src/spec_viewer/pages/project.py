"""Homepage, project documents, examples and coverage report."""
import json
from pathlib import Path
from typing import Any, Dict, List
import frontmatter
from planning_application_specification.applications import get_active_combined_application_refs
from spec_viewer.rendering import PROJECT_ROOT
from spec_viewer.markdown import render_govuk_markdown
from spec_viewer.view_models.design_decisions import load_design_decisions, design_decision_feedback_url
from spec_viewer.view_models.examples import EXAMPLE_GROUPS
from spec_viewer.view_models.progress import build_progress_view_model


class PageWriter:
    def __init__(self, environment, output_dir):
        self.env = environment
        self.output_dir = output_dir
        self.url_for = environment.globals["url_for"]
        self.count = 0

    def render(self, template, context):
        return self.env.get_template(template).render(**context)

    def write_page(self, path, content):
        target = self.output_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self.count += path.endswith(".html")


def render_index(renderer) -> None:
    # render the main Index page
    index_ctx = {
        "page_title": "Planning application data standard",
        "isHomepage": True,
        "links": {
            "application_types": renderer.url_for("/application-type/"),
            "datasets": renderer.url_for("/dataset/"),
            "data_model": renderer.url_for("/data-model/"),
            "national_public_view": renderer.url_for("/view/national-public/"),
            "github_feedback": "https://github.com/digital-land/planning-application-data-specification/issues/new",
        },
    }
    index_html = renderer.render("index.html", index_ctx)
    renderer.write_page("index.html", index_html)

def render_examples(renderer, spec_root: Path) -> None:
    """Render the examples index and each complete JSON example."""
    groups = []
    for group in EXAMPLE_GROUPS:
        examples = []
        for example in group["examples"]:
            example_route = f"/example/{group['route']}/{example['slug']}/"
            examples.append(
                {
                    **example,
                    "href": renderer.url_for(example_route),
                }
            )
        groups.append({**group, "examples": examples})

    index_html = renderer.render(
        "example_index.html",
        {
            "page_title": "Examples",
            "groups": groups,
        },
    )
    renderer.write_page("example/index.html", index_html)

    for group in EXAMPLE_GROUPS:
        for example in group["examples"]:
            example_path = spec_root / "example" / example["source"]
            example_json = example_path.read_text(encoding="utf-8")

            content_path = (
                PROJECT_ROOT
                / "content"
                / "example"
                / group["route"]
                / f"{example['slug']}.md"
            )
            content = frontmatter.load(content_path)
            rendered_content = renderer.env.from_string(content.content).render()

            output_path = f"example/{group['route']}/{example['slug']}"
            download_path = f"{output_path}/example.json"
            detail_html = renderer.render(
                "example_detail.html",
                {
                    "page_title": example["title"],
                    "title": example["title"],
                    "description": render_govuk_markdown(rendered_content),
                    "example_json": example_json,
                    "download_href": renderer.url_for(f"/{download_path}"),
                },
            )
            renderer.write_page(f"{output_path}/index.html", detail_html)

            download_target = renderer.output_dir / download_path
            download_target.parent.mkdir(parents=True, exist_ok=True)
            download_target.write_bytes(example_path.read_bytes())

def render_design_decisions(
    renderer,
    design_decisions: List[Dict[str, Any]],
) -> None:
    decisions = [
        {
            **decision,
            "href": renderer.url_for(f"/design-decision/{decision['slug']}"),
            "feedback_href": design_decision_feedback_url(decision),
        }
        for decision in design_decisions
    ]
    index_html = renderer.render(
        "design_decision_index.html",
        {
            "page_title": "Design decisions",
            "decisions": decisions,
        },
    )
    renderer.write_page("design-decision/index.html", index_html)

    for decision in decisions:
        detail_html = renderer.render(
            "design_decision_detail.html",
            {
                "page_title": f"Design decision {decision['decision_id']}",
                "decision": decision,
            },
        )
        renderer.write_page(
            f"design-decision/{decision['slug']}/index.html", detail_html
        )

def render_submission_progress_page(
    renderer,
    progress_data: dict,
) -> None:

    def prepare_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prepared: List[Dict[str, Any]] = []
        for row in rows:
            refs = row.get("refs", []) or []
            trailing = f"({','.join(refs)})" if refs else ""
            display_name = row.get("label", "")
            if trailing and display_name.endswith(trailing):
                display_name = display_name[: -len(trailing)].rstrip()
            prepared.append(
                {
                    **row,
                    "display_name": display_name,
                    "refs_with_href": [
                        {
                            "ref": ref,
                            "href": renderer.url_for(f"/application-type/{ref}"),
                        }
                        for ref in refs
                    ],
                    "used_for_inheritance": "Inheritance-only application type"
                    in (row.get("notes") or ""),
                }
            )
        return prepared

    progress_ctx = {
        "page_title": "Submission progress",
        "summary": progress_data["summary"],
        "covered_rows": prepare_rows(progress_data["covered_by_spec"]),
        "not_covered_rows": prepare_rows(progress_data["not_covered_by_spec"]),
        "links": {
            "home": renderer.url_for("/"),
            "back": renderer.url_for("/application-type"),
            "application_types": renderer.url_for("/application-type"),
            "github_issue_url": "https://github.com/digital-land/planning-application-data-specification/issues/new?title=Feedback%20on%20submission%20progress%20page",
            "github_edit_url": "https://github.com/digital-land/planning-application-data-specification/edit/main/bin/templates/submission_progress.html",
        },
    }
    progress_html = renderer.render("submission_progress.html", progress_ctx)
    renderer.write_page("submissions/progress/index.html", progress_html)

def render_project_pages(specification, environment, output_dir):
    renderer = PageWriter(environment, output_dir)
    render_index(renderer)
    render_design_decisions(renderer, load_design_decisions(specification.source_path / "documentation"))
    # Small synthetic sources used by tests need not include the curated examples/report.
    if (specification.source_path / "specification/example").is_dir():
        render_examples(renderer, specification.source_path / "specification")
    progress_input = specification.source_path / "bin/admin_data/2024-application-volumes.csv"
    if progress_input.is_file():
        progress = build_progress_view_model(progress_input, spec_application_refs=set(specification.applications),
            active_combined_application_refs=get_active_combined_application_refs(specification.tables))
        render_submission_progress_page(renderer, progress)
        renderer.write_page("submissions/progress/data.json", json.dumps(progress, indent=2))
    return renderer.count
