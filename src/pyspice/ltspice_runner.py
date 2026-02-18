"""LTspice headless runner."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def run_ltspice_headless(*, ltspice_executable: str, circuit_file: Path) -> tuple[Path, Path]:
    """Run LTspice in batch mode and return produced .raw and .log paths."""
    if not circuit_file.exists():
        raise RuntimeError(f"Circuit file does not exist: {circuit_file}")

    LOGGER.info("Running LTspice headless", extra={"circuit_file": str(circuit_file)})
    result = subprocess.run(
        [ltspice_executable, "-b", circuit_file.name],
        cwd=circuit_file.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "LTspice command failed.\n"
            f"Return code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    raw_path = circuit_file.with_suffix(".raw")
    log_path = circuit_file.with_suffix(".log")
    if not raw_path.exists() or not log_path.exists():
        raise RuntimeError(
            "LTspice completed but expected outputs were missing.\n"
            f"Expected raw: {raw_path} (exists={raw_path.exists()})\n"
            f"Expected log: {log_path} (exists={log_path.exists()})"
        )

    LOGGER.info(
        "LTspice run completed",
        extra={"raw_path": str(raw_path), "log_path": str(log_path)},
    )
    return raw_path, log_path
