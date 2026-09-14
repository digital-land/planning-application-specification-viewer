from pathlib import Path

import pytest

from spec_viewer.rendering import copy_static, create_environment


@pytest.mark.parametrize("base_url", ["", "/planning-application-specification-viewer"])
def test_shared_layout_uses_output_base_and_escapes_content(base_url):
    env = create_environment(base_url)
    page = env.from_string(
        '{% extends "base.html" %}{% block content %}<h1>{{ heading }}</h1>{% endblock %}'
    ).render(page_title="Example", heading="<Example>", isHomepage=True)
    assert "&lt;Example&gt;" in page
    assert f'href="{base_url}/dataset/"' in page
    assert f'{base_url}/static/stylesheets/application.css' in page
    assert f'{base_url}/static/vendor/govuk/govuk-frontend-6.4.0.min.js' in page
    assert "proof of concept viewer" in page
    assert "Open Government Licence" in page


def test_all_shared_templates_compile():
    env = create_environment()
    for template in Path("templates").rglob("*.html"):
        env.get_template(template.relative_to("templates").as_posix())


def test_static_copy_preserves_assets_and_excludes_development_readme(tmp_path):
    copy_static(tmp_path)
    assert not (tmp_path / "static/README.md").exists()
    for path in Path("static").rglob("*"):
        if path.is_file() and path != Path("static/README.md"):
            assert (tmp_path / path).read_bytes() == path.read_bytes()
