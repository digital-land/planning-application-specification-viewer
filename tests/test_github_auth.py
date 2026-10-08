"""Check authentication at the HTTP boundary for both GitHub callers."""
from io import BytesIO

import pytest

from scripts import select_spec_release
from spec_viewer import project_content


@pytest.mark.parametrize("module,caller", [
    (select_spec_release, select_spec_release.get_json),
    (project_content, project_content._read_url),
])
@pytest.mark.parametrize("url,authenticated", [
    ("https://api.github.com/repos/example/spec/releases", True),
    ("https://raw.githubusercontent.com/example/spec/main/file.md", False),
    ("https://api.github.com.example.org/releases", False),
    ("http://api.github.com/releases", False),
])
@pytest.mark.parametrize("token", [None, "test-token"])
def test_github_authentication(monkeypatch, module, caller, url, authenticated, token):
    if token:
        monkeypatch.setenv("GITHUB_TOKEN", token)
    else:
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    requests = []

    def open_request(request, timeout):
        requests.append(request)
        assert timeout == 30
        return BytesIO(b'{}')

    monkeypatch.setattr(module, "urlopen", open_request)
    caller(url)
    expected = f"Bearer {token}" if token and authenticated else None
    assert requests[0].get_header("Authorization") == expected
