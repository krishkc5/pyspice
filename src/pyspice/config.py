"""Runtime configuration and environment checks."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class RuntimeConfig:
    """Resolved runtime dependencies for this vertical slice."""

    openai_api_key: str
    ltspice_executable: str


def load_environment() -> None:
    """Load environment variables from .env if present."""
    load_dotenv(override=False)


def resolve_ltspice_path() -> str:
    """
    Resolve LTspice executable path in priority order:
    1) LTSPICE_PATH
    2) PATH lookup (shutil.which)
    3) macOS default app bundle binary path
    """
    env_path = os.getenv("LTSPICE_PATH")
    if env_path:
        candidate = Path(env_path).expanduser()
        if not candidate.exists():
            raise RuntimeError(
                f"LTSPICE_PATH is set but does not exist: {candidate}. "
                "Fix LTSPICE_PATH or unset it to use auto-discovery."
            )
        if not os.access(candidate, os.X_OK):
            raise RuntimeError(
                f"LTSPICE_PATH is set but is not executable: {candidate}. "
                "Point LTSPICE_PATH to the LTspice executable binary."
            )
        return str(candidate)

    discovered = shutil.which("LTspice")
    if discovered:
        return discovered

    default_macos_path = Path("/Applications/LTspice.app/Contents/MacOS/LTspice")
    if default_macos_path.exists() and os.access(default_macos_path, os.X_OK):
        return str(default_macos_path)

    raise RuntimeError(
        "LTspice executable could not be resolved. "
        "Set LTSPICE_PATH, add `LTspice` to PATH, or install LTspice at "
        "/Applications/LTspice.app/Contents/MacOS/LTspice."
    )


def load_runtime_config() -> RuntimeConfig:
    """Load required environment config and fail fast if missing."""
    load_environment()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY environment variable. "
            "Set OPENAI_API_KEY in your shell or .env before running pyspice."
        )

    ltspice_executable = resolve_ltspice_path()
    return RuntimeConfig(openai_api_key=api_key, ltspice_executable=ltspice_executable)
