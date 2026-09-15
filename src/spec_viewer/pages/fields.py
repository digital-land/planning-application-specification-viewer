"""Render the field index and canonical field detail pages."""
from pathlib import Path
from spec_viewer.view_models.fields import field_index, field_detail


def render_fields(specification, environment, output_dir: Path) -> int:
    url_for = environment.globals["url_for"]
    field_dir = output_dir / "field"
    field_dir.mkdir(parents=True, exist_ok=True)
    (field_dir / "index.html").write_text(
        environment.get_template("fields_index.html").render(**field_index(specification, url_for)),
        encoding="utf-8",
    )
    template = environment.get_template("field_detail.html")
    for field in specification.fields.values():
        target = field_dir / field.ref / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(template.render(**field_detail(specification, field, url_for)), encoding="utf-8")
    return len(specification.fields) + 1
