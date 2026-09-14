"""Shared template rendering using resources from the viewer checkout."""

from pathlib import Path
import numbers
import shutil

import jinja2
from digital_land_frontend import filters, globals as frontend_globals


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def url_for(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def commanum(value):
    return format(value, ",") if isinstance(value, numbers.Number) else value


def create_environment(base_url: str = "", *, project_root: Path = PROJECT_ROOT):
    """Create an independent Jinja environment for one output base URL."""
    templates = project_root / "templates"
    environment = jinja2.Environment(
        loader=jinja2.ChoiceLoader([
            jinja2.FileSystemLoader([str(templates), str(templates / "components")]),
            jinja2.PrefixLoader({
                "digital-land-frontend": jinja2.PackageLoader("digital_land_frontend", "templates"),
                "govuk_frontend_jinja": jinja2.PackageLoader("govuk_frontend_jinja", "templates"),
            }),
        ]),
        autoescape=True,
    )
    environment.filters.update({
        "is_list": filters.is_list_filter,
        "is_valid_uri": filters.is_valid_uri_filter,
        "make_link": filters.make_link_filter,
        "float_to_int": filters.float_to_int_filter,
        "commanum": commanum,
        "split_to_list": filters.split_to_list_filter,
        "readable_date": filters.readable_date_filter,
        "hex_to_rgb_string": filters.hex_to_rgb_string_filter,
    })
    environment.globals.update(
        base_url=base_url.rstrip("/"),
        assetPath=url_for(base_url, "static"),
        staticPath=url_for(base_url, "static"),
        url_for=lambda path: url_for(base_url, path),
        random_int=frontend_globals.random_int,
    )
    return environment


def copy_static(output_dir: Path, *, project_root: Path = PROJECT_ROOT) -> None:
    """Copy publishable assets, excluding the development README."""
    static = project_root / "static"
    for path in static.rglob("*"):
        if not path.is_file() or path.relative_to(static) == Path("README.md"):
            continue
        target = output_dir / "static" / path.relative_to(static)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
