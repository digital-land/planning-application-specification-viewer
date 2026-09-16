"""Build the implemented viewer page families from specification package data."""
import argparse
import json
from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

from spec_viewer.data import load_viewer_data
from spec_viewer.pages.fields import render_fields
from spec_viewer.pages.project import render_project_pages
from spec_viewer.pages.needs import render_needs
from spec_viewer.pages.views import render_views
from spec_viewer.pages.datasets import render_datasets
from spec_viewer.pages.applications import render_applications
from spec_viewer.pages.data_model import render_data_model
from spec_viewer.rendering import PROJECT_ROOT, create_environment, copy_static


def build(source: Path, output_dir: Path, base_url: str = "") -> int:
    data = load_viewer_data(source)
    environment = create_environment(base_url)
    output_dir.mkdir(parents=True, exist_ok=True)
    count = render_fields(data.specification, environment, output_dir)
    count += render_data_model(data.specification, environment, output_dir)
    count += render_applications(data.specification, environment, output_dir)
    count += render_datasets(data, environment, output_dir)
    count += render_views(data.specification, environment, output_dir)
    count += render_needs(data, environment, output_dir)
    count += render_project_pages(data.specification, environment, output_dir)
    profile = data.specification.tables["specification"].get("planning-application-data", {})
    site_map = {
        "index": "index.html",
        "needs": [f"user-need/{n.get('need')}/index.html" for n in sorted(data.needs.values(), key=lambda n: n.get("need", ""))],
        "datasets": [f"dataset/{ds.get('dataset')}/index.html" for ds in profile.get("datasets", [])],
        "application_types": "application-type/index.html",
        "submission_progress": "submissions/progress/index.html",
        "data_model": "data-model/index.html",
        "views": "view/index.html",
        "national_public_view": "view/national-public/index.html",
        "examples": "example/index.html",
    }
    (output_dir / "sitemap.json").write_text(json.dumps(site_map, indent=2), encoding="utf-8")
    copy_static(output_dir)
    return count


def main():
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as stream:
        config = tomllib.load(stream)
    default_output = PROJECT_ROOT / config["tool"]["spec-viewer"]["output-directory"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-root", required=True, type=Path, help="Specification repository root")
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--base-url", default="")
    args = parser.parse_args()
    count = build(args.spec_root, args.output, args.base_url)
    print(f"Built {count} pages in {args.output.resolve()}")


if __name__ == "__main__":
    main()
