"""Waveform plotting utilities."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pathlib import Path


def plot_signals_vs_time(*, time_axis, signals: dict[str, object], output_png: Path) -> None:
    """Plot multiple signals against time and save as a PNG file."""
    fig, ax = plt.subplots(figsize=(10, 5))
    for label, waveform in signals.items():
        ax.plot(time_axis, waveform, label=label)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    ax.set_title("LTspice Waveforms")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_png, format="png", dpi=150)
    plt.close(fig)
