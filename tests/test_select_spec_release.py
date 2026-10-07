import pytest

from scripts.select_spec_release import select_release


SHA = "a" * 40


def release(tag, published="2026-10-07T12:00:00Z", *, draft=False, prerelease=True):
    return {"tag_name": tag, "published_at": published, "draft": draft, "prerelease": prerelease}


def api(pages, *, sha=SHA):
    requested = []

    def fetch(url):
        requested.append(url)
        if "/releases?" in url:
            page = int(url.rsplit("page=", 1)[1])
            return pages.get(page, [])
        return {"sha": sha}

    return fetch, requested


def test_selects_most_recent_published_eligible_release():
    fetch, requested = api({1: [
        release("2026.10.7.dev1", "2026-10-07T10:00:00Z"),
        release("2026.9.30.dev9", "2026-10-08T10:00:00Z"),
        release("2026.10.8.dev1", "2026-10-09T10:00:00Z", draft=True),
        release("2026.10.9.dev1", "2026-10-10T10:00:00Z", prerelease=False),
        release("2026.10.40.dev1", "2026-10-11T10:00:00Z"),
        release("v2026.10.10.dev1", "2026-10-12T10:00:00Z"),
    ]})
    selected = select_release(fetch_json=fetch)
    assert selected["tag"] == "2026.9.30.dev9"
    assert selected["version"] == "2026.9.30.dev9"
    assert selected["resolved_revision"] == SHA
    assert requested[-1].endswith("/commits/2026.9.30.dev9")


def test_paginated_listing_and_published_override():
    first_page = [release("2026.10.1.dev1", "2026-10-01T10:00:00Z")] * 100
    fetch, requested = api({1: first_page, 2: [release("2026.10.7.dev1", "2026-10-07T10:00:00Z")]})
    assert select_release(fetch_json=fetch)["tag"] == "2026.10.7.dev1"
    assert any("page=2" in url for url in requested)
    assert select_release(tag="2026.10.1.dev1", fetch_json=fetch)["tag"] == "2026.10.1.dev1"
    with pytest.raises(ValueError, match="No published dated development prerelease found for tag"):
        select_release(tag="main", fetch_json=fetch)


def test_no_eligible_release_fails_without_main_fallback():
    fetch, requested = api({1: [release("2026.10.7.dev1", draft=True), release("latest", prerelease=True)]})
    with pytest.raises(ValueError, match="publish one"):
        select_release(fetch_json=fetch)
    assert not any("/commits/" in url for url in requested)


def test_padded_tag_keeps_tag_and_normalises_installed_version():
    fetch, _ = api({1: [release("2026.10.07.dev1")]})
    selected = select_release(fetch_json=fetch)
    assert selected["tag"] == "2026.10.07.dev1"
    assert selected["version"] == "2026.10.7.dev1"


def test_rejects_invalid_revision_and_response():
    fetch, _ = api({1: [release("2026.10.7.dev1")]}, sha="main")
    with pytest.raises(ValueError, match="invalid release commit SHA"):
        select_release(fetch_json=fetch)
    with pytest.raises(ValueError, match="not a list"):
        select_release(fetch_json=lambda url: {})
