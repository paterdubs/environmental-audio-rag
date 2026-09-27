import pytest

from scripts import check_inference_parity as parity


def _no_git(root):
    raise FileNotFoundError("git")


def test_revision_uses_env_when_git_binary_missing(monkeypatch):
    monkeypatch.setattr(parity, "git_state", _no_git)
    monkeypatch.setenv("GIT_REVISION", "abc123")
    monkeypatch.setenv("GIT_DIRTY", "False")
    assert parity.revision() == {"revision": "abc123", "dirty": "False", "source": "env"}


def test_revision_refuses_without_git_or_env(monkeypatch):
    monkeypatch.setattr(parity, "git_state", _no_git)
    monkeypatch.delenv("GIT_REVISION", raising=False)
    with pytest.raises(RuntimeError, match="GIT_REVISION"):
        parity.revision()
