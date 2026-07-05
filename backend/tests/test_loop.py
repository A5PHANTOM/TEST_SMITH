import pytest
from app.orchestrator.loop import _validate_repo_path


def test_validate_path_allowed():
    assert _validate_repo_path("/tmp/myproject", ["/tmp"]) is True


def test_validate_path_blocked():
    assert _validate_repo_path("/etc/passwd", ["/tmp"]) is False


def test_validate_path_traversal():
    assert _validate_repo_path("/tmp/../etc", ["/tmp"]) is False
