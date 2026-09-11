"""Check the installed specification API against an explicit source directory."""
import argparse
import json
from importlib.metadata import distribution
from pathlib import Path
import sys

import planning_application_specification
from planning_application_specification import Specification


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Specification repository directory")
    args = parser.parse_args()
    source = args.source.resolve()
    installed = distribution("planning-application-specification")
    direct_url = json.loads(installed.read_text("direct_url.json") or "{}")
    spec = Specification.load(source)
    checks = {
        "field": spec.field("description"),
        "module": spec.module("proposal-details"),
        "application": spec.application("full"),
        "codelist": spec.codelist("decision").items,
        "guidance": spec.guidance(
            dataset="decision-notice", field="planning-officer-recommendation"
        ),
    }
    for name, value in checks.items():
        if not value:
            raise RuntimeError(f"Smoke test failed: no {name} returned")
    print(json.dumps({
        "status": "PASS",
        "python": sys.executable,
        "package_version": installed.version,
        "package_location": planning_application_specification.__file__,
        "editable": direct_url.get("dir_info", {}).get("editable", False),
        "data_path": str(source),
        "checks": list(checks),
    }, indent=2))


if __name__ == "__main__":
    main()
