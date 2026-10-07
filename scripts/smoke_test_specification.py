"""Check the installed specification API and optional local checkout override."""
import argparse
import json
from importlib.metadata import distribution
from pathlib import Path
import sys

import planning_application_specification
from spec_viewer.data import load_viewer_data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path, help="Optional local specification checkout")
    args = parser.parse_args()
    source = args.source.resolve() if args.source is not None else None
    installed = distribution("planning-application-specification")
    direct_url = json.loads(installed.read_text("direct_url.json") or "{}")
    data = load_viewer_data(source)
    spec = data.specification
    checks = {
        "field": spec.field("description"),
        "needs": data.needs,
        "justifications": data.justifications,
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
        "data_path": str(spec.source_path),
        "checks": list(checks),
        "counts": {
            "fields": len(spec.fields),
            "modules": len(spec.modules),
            "components": len(spec.components),
            "datasets": len(spec.datasets),
            "applications": len(spec.applications),
            "needs": len(data.needs),
            "justifications": len(data.justifications),
        },
    }, indent=2))


if __name__ == "__main__":
    main()
