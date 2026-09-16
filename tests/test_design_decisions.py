from spec_viewer.view_models.design_decisions import parse_design_decision, design_decision_feedback_url


def test_decision_metadata_and_markdown(tmp_path):
    path = tmp_path / "0042-test-decision.md"
    path.write_text("# Decision: A choice\n\n**Date:** 2026-09-16\n**Status:** Accepted\n\n## Reason\n\nKeep **clear** records.")
    result = parse_design_decision(path)
    assert result["decision_id"] == "0042"
    assert result["title"] == "A choice"
    assert result["status"] == "Accepted"
    assert "<strong>clear</strong>" in result["body"]
    assert "**Date:**" not in result["body"]
    assert "%5B0042%5D" in design_decision_feedback_url(result)
