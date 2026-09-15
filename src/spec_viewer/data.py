"""Load viewer inputs through the installed specification package."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from planning_application_specification import Specification
from planning_application_specification.loader import load_needs


@dataclass
class ViewerData:
    """Package models shared by page builders during a single build."""

    specification: Specification
    needs: dict[str, Any]
    justifications: dict[str, Any]


def load_viewer_data(source: str | Path) -> ViewerData:
    """Read an explicit repository root without changing the working directory.

    Keep package models intact: resolution, inheritance, codelists and guidance
    remain the responsibility of the installed specification package.
    """
    source = Path(source).expanduser().resolve()
    specification = Specification.load(source)
    need_records = load_needs(source)
    return ViewerData(
        specification=specification,
        needs=need_records["need"],
        justifications=need_records["justification"],
    )
