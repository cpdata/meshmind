from scripts.check_docs_sync import check_docs


def test_docs_guard_passes_when_docs_cover_changes(monkeypatch):
    monkeypatch.setattr("scripts.check_docs_sync._git_diff", lambda base: ["meshmind/api/memory_manager.py", "docs/api.md"])
    assert check_docs("HEAD") == 0


def test_docs_guard_fails_when_docs_missing(monkeypatch):
    monkeypatch.setattr("scripts.check_docs_sync._git_diff", lambda base: ["meshmind/core/config.py"])
    result = check_docs("HEAD")
    assert result == 1


def test_docs_guard_requires_setup_for_compose(monkeypatch):
    monkeypatch.setattr("scripts.check_docs_sync._git_diff", lambda base: ["docker-compose.yml"])
    assert check_docs("HEAD") == 1


def test_docs_guard_passes_when_setup_updated(monkeypatch):
    monkeypatch.setattr(
        "scripts.check_docs_sync._git_diff",
        lambda base: ["docker-compose.yml", "SETUP.md"],
    )
    assert check_docs("HEAD") == 0
