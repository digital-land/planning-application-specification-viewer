"""Read project decision documents independently of the specification API."""
import re
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote
from spec_viewer.markdown import render_govuk_markdown

def load_design_decisions(documentation_root: Path) -> List[Dict[str, Any]]:
    decisions_path = documentation_root / "design-decisions"
    if not decisions_path.exists():
        return []

    decisions = [
        parse_design_decision(path) for path in sorted(decisions_path.glob("*.md"))
    ]
    return sorted(decisions, key=lambda decision: decision["decision_id"])

def parse_design_decision(path: Path) -> Dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    slug = path.stem
    decision_id = slug.split("-", 1)[0]
    title = extract_design_decision_title(content, slug)
    body_markdown = strip_design_decision_page_metadata(content)

    return {
        "decision_id": decision_id,
        "slug": slug,
        "title": title,
        "date": extract_design_decision_metadata(content, "Date"),
        "status": extract_design_decision_metadata(content, "Status"),
        "body": render_govuk_markdown(body_markdown),
    }

def extract_design_decision_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        match = re.match(r"^#{1,2}\s+(.*)$", line.strip())
        if match:
            title = match.group(1).strip()
            return re.sub(r"^Decision:\s*", "", title, flags=re.IGNORECASE)
    return fallback.replace("-", " ").capitalize()

def extract_design_decision_metadata(content: str, label: str) -> str:
    pattern = rf"^\*\*{re.escape(label)}:\*\*\s*(.*?)\s*$"
    for line in content.splitlines():
        match = re.match(pattern, line.strip())
        if match:
            return match.group(1).strip()
    return ""

def strip_design_decision_page_metadata(content: str) -> str:
    lines = []
    skipped_heading = False
    for line in content.splitlines():
        stripped = line.strip()
        if not skipped_heading and re.match(r"^#{1,2}\s+", stripped):
            skipped_heading = True
            continue
        if re.match(r"^\*\*(Date|Status):\*\*", stripped):
            continue
        lines.append(line)
    return "\n".join(lines).strip()

def design_decision_feedback_url(decision: Dict[str, Any]) -> str:
    title = (
        f"[{decision['decision_id']}] Feedback on design decision: {decision['title']}"
    )
    encoded_title = quote(title)
    return (
        "https://github.com/digital-land/planning-application-data-specification/"
        f"issues/new?title={encoded_title}"
    )
