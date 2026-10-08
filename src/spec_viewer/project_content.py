"""Prepare a local snapshot of project documents and reporting data."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from uuid import uuid4
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

from spec_viewer.rendering import PROJECT_ROOT

REPOSITORY = "digital-land/planning-application-data-specification"
SNAPSHOT_FORMAT = "spec-viewer-project-content-v1"
REPORT = "bin/admin_data/2024-application-volumes.csv"
DECISIONS = "documentation/design-decisions/"
MAX_FILE_SIZE = 2_000_000


def _read_url(url: str) -> bytes:
    request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "spec-viewer-content-fetch"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and urlsplit(url).scheme == "https" and urlsplit(url).netloc == "api.github.com":
        request.add_header("Authorization", f"Bearer {token}")
    with urlopen(request, timeout=30) as response:
        return response.read()


def _get_json(url: str) -> dict:
    return json.loads(_read_url(url))


def _get_blob(url: str) -> bytes:
    return _read_url(url)


def _selected_paths(tree: dict) -> list[str]:
    if tree.get("truncated"):
        raise ValueError("GitHub tree response was truncated")
    paths = []
    for item in tree.get("tree", []):
        path = item.get("path", "")
        if item.get("type") != "blob" or item.get("mode") not in ("100644", "100755"):
            continue
        if path == REPORT or (path.startswith(DECISIONS) and path.endswith(".md") and "/" not in path[len(DECISIONS):]):
            if item.get("size", 0) > MAX_FILE_SIZE:
                raise ValueError(f"Project content file exceeds size limit: {path}")
            paths.append(path)
    if REPORT not in paths or not any(path.startswith(DECISIONS) for path in paths):
        raise ValueError("Required project content is missing from the selected revision")
    return sorted(paths)


def fetch_project_content(cache: Path, ref: str = "main", *, get_json=_get_json, get_blob=_get_blob, now=None) -> dict:
    """Fetch selected files at one immutable Git revision, then replace the cache."""
    cache = Path(cache).expanduser().resolve()
    ref = ref.strip()
    if not ref:
        raise ValueError("A source ref is required")
    checked_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
    api = f"https://api.github.com/repos/{REPOSITORY}"
    commit = get_json(f"{api}/commits/{quote(ref, safe='')}")
    revision = commit["sha"]
    if len(revision) != 40 or any(char not in "0123456789abcdef" for char in revision.lower()):
        raise ValueError("GitHub returned an invalid commit revision")
    tree = get_json(f"{api}/git/trees/{revision}?recursive=1")
    paths = _selected_paths(tree)
    previous = {}
    prior_metadata = {}
    metadata_path = cache / "metadata.json"
    if cache.exists():
        if not cache.is_dir():
            raise ValueError(f"Cache destination is not a directory: {cache}")
        if any(cache.iterdir()):
            if not metadata_path.is_file():
                raise ValueError(f"Refusing to replace an unmanaged directory: {cache}")
            prior_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if prior_metadata.get("format") != SNAPSHOT_FORMAT or prior_metadata.get("repository") != REPOSITORY or not isinstance(prior_metadata.get("files"), dict):
                raise ValueError(f"Refusing to replace an unmanaged directory: {cache}")
            previous = prior_metadata["files"]

    files = {}
    contents = {}
    for path in paths:
        url = f"https://raw.githubusercontent.com/{REPOSITORY}/{revision}/{path}"
        content = get_blob(url)
        if len(content) > MAX_FILE_SIZE:
            raise ValueError(f"Project content file exceeds size limit: {path}")
        content.decode("utf-8")
        digest = hashlib.sha256(content).hexdigest()
        prior = previous.get(path, {})
        files[path] = {
            "sha256": digest,
            "checked_at": checked_at,
            "last_updated": prior.get("last_updated", checked_at) if prior.get("sha256") == digest else checked_at,
        }
        contents[path] = content

    previous_hashes = {path: entry.get("sha256") for path, entry in previous.items()}
    current_hashes = {path: entry["sha256"] for path, entry in files.items()}
    last_updated = prior_metadata.get("last_updated", checked_at) if previous_hashes == current_hashes else checked_at
    metadata = {"format": SNAPSHOT_FORMAT, "repository": REPOSITORY, "requested_ref": ref, "resolved_revision": revision, "checked_at": checked_at, "last_updated": last_updated, "files": files}
    cache.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=f".{cache.name}-staged-", dir=cache.parent))
    backup = cache.parent / f".{cache.name}-previous-{uuid4().hex}"
    try:
        for path, content in contents.items():
            target = staged / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        (staged / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        if cache.exists():
            os.replace(cache, backup)
        try:
            os.replace(staged, cache)
        except Exception:
            if backup.exists():
                os.replace(backup, cache)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    finally:
        if staged.exists():
            shutil.rmtree(staged)
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="main", help="Source Git ref to resolve to a commit")
    parser.add_argument("--cache", type=Path, default=PROJECT_ROOT / "project-content")
    args = parser.parse_args()
    metadata = fetch_project_content(args.cache, args.ref)
    print(f"Cached {len(metadata['files'])} project files from {metadata['resolved_revision']} in {args.cache.resolve()}")


if __name__ == "__main__":
    main()
