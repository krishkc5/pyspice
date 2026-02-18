from __future__ import annotations

import pytest

from pyspice.config import load_runtime_config, resolve_ltspice_path


def test_load_runtime_config_raises_when_ltspice_missing(monkeypatch):
    monkeypatch.setattr("pyspice.config.load_environment", lambda: None)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("pyspice.config.shutil.which", lambda _: None)
    monkeypatch.setattr("pyspice.config.Path.exists", lambda self: False)

    with pytest.raises(RuntimeError, match="LTspice executable could not be resolved"):
        load_runtime_config()


def test_load_runtime_config_raises_when_openai_key_missing(monkeypatch):
    monkeypatch.setattr("pyspice.config.load_environment", lambda: None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("pyspice.config.resolve_ltspice_path", lambda: "/usr/local/bin/LTspice")

    with pytest.raises(RuntimeError, match="Missing OPENAI_API_KEY"):
        load_runtime_config()


def test_resolve_ltspice_path_prefers_ltspice_path_env(monkeypatch):
    monkeypatch.setenv("LTSPICE_PATH", "/opt/LTspice")
    monkeypatch.setattr("pyspice.config.Path.exists", lambda self: True)
    monkeypatch.setattr("pyspice.config.os.access", lambda path, mode: True)

    assert resolve_ltspice_path() == "/opt/LTspice"
