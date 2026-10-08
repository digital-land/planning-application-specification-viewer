"""Select a published dated development release of the specification package."""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen


REPOSITORY = "digital-land/planning-application-data-specification"
API = f"https://api.github.com/repos/{REPOSITORY}"
TAG_PATTERN = re.compile(r"^(\d{4})\.(\d{1,2})\.(\d{1,2})\.dev([1-9]\d*)$")


def get_json(url):
    request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "spec-viewer-release-selector"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and urlsplit(url).scheme == "https" and urlsplit(url).netloc == "api.github.com":
        request.add_header("Authorization", f"Bearer {token}")
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def release_version(release):
    if release.get("draft") or not release.get("prerelease"):
        return None
    tag = release.get("tag_name", "")
    match = TAG_PATTERN.fullmatch(tag)
    if not match:
        return None
    try:
        datetime(int(match[1]), int(match[2]), int(match[3]))
        published = datetime.fromisoformat(release["published_at"].replace("Z", "+00:00"))
    except (ValueError, KeyError, AttributeError):
        return None
    if published.tzinfo is None:
        return None
    return published


def select_release(*, tag=None, fetch_json=get_json):
    """Return a published release and its immutable commit SHA."""
    eligible = []
    for page in range(1, 101):
        releases = fetch_json(f"{API}/releases?per_page=100&page={page}")
        if not isinstance(releases, list):
            raise ValueError("GitHub releases response was not a list")
        for item in releases:
            published = release_version(item)
            if published is not None:
                eligible.append((published, item))
        if len(releases) < 100:
            break
    else:
        raise ValueError("Release listing exceeded 100 pages")

    if tag:
        matches = [item for published, item in eligible if item["tag_name"] == tag]
        if not matches:
            raise ValueError(f"No published dated development prerelease found for tag {tag!r}")
        release = matches[0]
    else:
        if not eligible:
            raise ValueError("No published dated development prerelease found; publish one before running the viewer workflow")
        release = max(eligible, key=lambda item: item[0])[1]

    resolved = fetch_json(f"{API}/commits/{quote(release['tag_name'], safe='')}")
    revision = resolved.get("sha", "")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
        raise ValueError("GitHub returned an invalid release commit SHA")
    match = TAG_PATTERN.fullmatch(release["tag_name"])
    version = f"{int(match[1])}.{int(match[2])}.{int(match[3])}.dev{int(match[4])}"
    return {
        "repository": REPOSITORY,
        "version": version,
        "tag": release["tag_name"],
        "published_at": release["published_at"],
        "resolved_revision": revision.lower(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="Use this published dated development prerelease tag")
    parser.add_argument("--output", type=Path, help="Write selected release JSON")
    parser.add_argument("--github-env", type=Path, help="Append values to GitHub Actions environment file")
    args = parser.parse_args()
    try:
        selected = select_release(tag=args.tag)
    except ValueError as error:
        parser.exit(1, f"{error}\n")
    if args.output:
        args.output.write_text(json.dumps(selected, indent=2) + "\n", encoding="utf-8")
    if args.github_env:
        with args.github_env.open("a", encoding="utf-8") as stream:
            for key in ("version", "tag", "resolved_revision"):
                stream.write(f"SPEC_RELEASE_{key.upper()}={selected[key]}\n")
    print(json.dumps(selected, indent=2))


if __name__ == "__main__":
    main()
