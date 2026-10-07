import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

from spec_viewer.pages.project import render_project_pages
from spec_viewer.rendering import create_environment


def test_project_pages_read_separate_project_root(tmp_path):
    specification_root = tmp_path / "specification-source"
    specification_root.mkdir()
    project_root = tmp_path / "project-source"
    decisions = project_root / "documentation/design-decisions"
    decisions.mkdir(parents=True)
    (decisions / "0001-test.md").write_text("## Decision: Separate content\n\nProject text.\n")
    report = project_root / "bin/admin_data/2024-application-volumes.csv"
    report.parent.mkdir(parents=True)
    report.write_text("application-name,form-name,stats-app-name,2024-total,applications-types,notes\nHouseholder,,,12,hh,\n")
    specification = SimpleNamespace(source_path=specification_root, applications={"hh": object()}, tables={"__root_path__": specification_root})
    output = tmp_path / "output"

    render_project_pages(specification, create_environment(""), output, project_root)

    assert "Separate content" in (output / "design-decision/0001-test/index.html").read_text()
    progress = json.loads((output / "submissions/progress/data.json").read_text())
    assert progress["summary"]["total_2024_volume"] == 12
    assert progress["summary"]["input"] == "bin/admin_data/2024-application-volumes.csv"


def test_cli_rejects_missing_project_content_before_writing_output(tmp_path):
    output = tmp_path / "output"
    result = subprocess.run(
        [sys.executable, "-m", "spec_viewer.build", "--project-root", str(tmp_path / "missing"), "--output", str(output)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Project content is incomplete" in result.stderr
    assert not output.exists()
