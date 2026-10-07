from datetime import datetime, timezone
import pytest

from spec_viewer.project_content import fetch_project_content


REVISION = "a" * 40
REPORT = "bin/admin_data/2024-application-volumes.csv"
DECISION = "documentation/design-decisions/001.md"


def tree(*paths):
    return {"truncated": False, "tree": [{"path": path, "type": "blob", "mode": "100644", "size": 20} for path in paths]}


def test_fetch_tracks_checks_changes_and_removes_stale_files(tmp_path):
    cache = tmp_path / "project-content"
    responses = {REPORT: b"heading\nvalue\n", DECISION: b"# Decision\n"}
    selected = [REPORT, DECISION]
    requests = []

    def get_json(url):
        requests.append(url)
        return {"sha": REVISION} if "/commits/" in url else tree(*selected)

    def get_blob(url):
        requests.append(url)
        assert f"/{REVISION}/" in url
        return responses[next(path for path in responses if url.endswith(path))]

    first = datetime(2026, 10, 7, 8, tzinfo=timezone.utc)
    second = datetime(2026, 10, 8, 8, tzinfo=timezone.utc)
    third = datetime(2026, 10, 9, 8, tzinfo=timezone.utc)
    metadata = fetch_project_content(cache, "main", get_json=get_json, get_blob=get_blob, now=first)
    assert metadata["resolved_revision"] == REVISION
    assert metadata["requested_ref"] == "main"
    assert (cache / DECISION).read_bytes() == responses[DECISION]
    assert metadata["files"][DECISION]["last_updated"] == first.isoformat()
    assert metadata["last_updated"] == first.isoformat()
    assert requests[0].endswith("/commits/main")

    unchanged = fetch_project_content(cache, "main", get_json=get_json, get_blob=get_blob, now=second)
    assert unchanged["files"][DECISION]["checked_at"] == second.isoformat()
    assert unchanged["files"][DECISION]["last_updated"] == first.isoformat()
    assert unchanged["files"][REPORT]["last_updated"] == first.isoformat()
    assert unchanged["last_updated"] == first.isoformat()

    responses[DECISION] = b"# Changed decision\n"
    changed = fetch_project_content(cache, "main", get_json=get_json, get_blob=get_blob, now=second)
    assert changed["files"][DECISION]["last_updated"] == second.isoformat()
    assert changed["files"][REPORT]["last_updated"] == first.isoformat()
    assert changed["last_updated"] == second.isoformat()

    selected[:] = [REPORT, "documentation/design-decisions/002.md"]
    responses.pop(DECISION)
    responses[selected[1]] = b"# New decision\n"
    removed = fetch_project_content(cache, "main", get_json=get_json, get_blob=get_blob, now=third)
    assert not (cache / DECISION).exists()
    assert (cache / selected[1]).is_file()
    assert removed["last_updated"] == third.isoformat()


def test_failed_fetch_preserves_complete_previous_snapshot(tmp_path):
    cache = tmp_path / "cache"
    def get_json(url):
        return {"sha": REVISION} if "/commits/" in url else tree(REPORT, DECISION)
    content = {REPORT: b"report\n", DECISION: b"# Decision\n"}
    fetch_project_content(cache, get_json=get_json, get_blob=lambda url: content[next(path for path in content if url.endswith(path))])
    previous = (cache / "metadata.json").read_bytes()
    with pytest.raises(OSError, match="fetch failed"):
        fetch_project_content(cache, get_json=get_json, get_blob=lambda url: (_ for _ in ()).throw(OSError("fetch failed")))
    assert (cache / "metadata.json").read_bytes() == previous
    assert (cache / DECISION).read_bytes() == content[DECISION]


def test_rejects_incomplete_or_truncated_source(tmp_path):
    cache = tmp_path / "cache"
    for source in (tree(REPORT), {"truncated": True, "tree": []}):
        with pytest.raises(ValueError):
            fetch_project_content(cache, get_json=lambda url: {"sha": REVISION} if "/commits/" in url else source, get_blob=lambda url: b"")
    assert not cache.exists()


def test_refuses_to_replace_unmanaged_directory(tmp_path):
    cache = tmp_path / "unmanaged"
    cache.mkdir()
    (cache / "user-file.txt").write_text("keep me")
    def get_json(url):
        return {"sha": REVISION} if "/commits/" in url else tree(REPORT, DECISION)
    with pytest.raises(ValueError, match="unmanaged"):
        fetch_project_content(cache, get_json=get_json, get_blob=lambda url: b"valid text\n")
    assert (cache / "user-file.txt").read_text() == "keep me"
