"""Build the implemented viewer page families from specification package data."""
import argparse
from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

from spec_viewer.data import load_viewer_data
from spec_viewer.pages.fields import render_fields
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
