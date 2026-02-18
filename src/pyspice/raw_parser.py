"""Parser utilities for LTspice .raw files."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from PyLTSpice import RawRead


class LTSpiceRawParser:
    """Thin wrapper around PyLTSpice RawRead."""

    def __init__(self, raw_path: Path) -> None:
        if not raw_path.exists():
            raise RuntimeError(f"RAW file not found: {raw_path}")
        self._raw = RawRead(str(raw_path))

    def list_signals(self) -> Sequence[str]:
        return self._raw.get_trace_names()

    def get_waveform(self, signal_name: str):
        return self._raw.get_trace(signal_name).get_wave(0)

    def get_time_axis(self):
        try:
            return self._raw.get_axis(0)
        except Exception:
            return self._raw.get_trace("time").get_wave(0)
