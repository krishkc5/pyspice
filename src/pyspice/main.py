"""End-to-end vertical slice for OpenAI -> LTspice -> parsing -> plotting."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from pyspice.config import load_runtime_config
from pyspice.llm import extract_tran_stop, generate_netlist
from pyspice.ltspice_runner import run_ltspice_headless
from pyspice.plotter import plot_signals_vs_time
from pyspice.raw_parser import LTSpiceRawParser

LOGGER = logging.getLogger(__name__)

SPEC = (
    "A voltage source V1 from node in to 0. Make it a pulse that goes from 0 V to 12 V. "
    "The pulse should begin at 0.8 ms, use 2 us rise and fall times, stay high for 0.8 ms, "
    "and repeat every 4 ms.\n"
    "A 220 ohm resistor R1 from node in to out.\n"
    "A 3.3 mH inductor L1 from node out to mid.\n"
    "A 47 uF capacitor C1 from node mid to 0.\n"
    "Run transient analysis for 6 ms."
)


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def _create_session_dir() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = Path("artifacts") / "sessions" / timestamp
    session_dir.mkdir(parents=True, exist_ok=False)
    return session_dir


def main() -> None:
    _configure_logging()
    config = load_runtime_config()
    session_dir = _create_session_dir()
    circuit_file = session_dir / "circuit.cir"
    tran_stop = extract_tran_stop(SPEC)

    LOGGER.info("Generating LTspice netlist")
    netlist_text = generate_netlist(
        api_key=config.openai_api_key,
        natural_language_spec=SPEC,
        tran_stop=tran_stop,
    )
    circuit_file.write_text(netlist_text + "\n", encoding="utf-8")
    if not circuit_file.exists():
        raise RuntimeError(f"Failed to write circuit netlist: {circuit_file}")

    raw_path, log_path = run_ltspice_headless(
        ltspice_executable=config.ltspice_executable,
        circuit_file=circuit_file,
    )
    if not raw_path.exists() or not log_path.exists():
        raise RuntimeError("Missing LTspice output artifacts after successful run.")

    parser = LTSpiceRawParser(raw_path)
    signals = parser.list_signals()
    print("Available signals:")
    for signal in signals:
        print(f" - {signal}")

    time_axis = parser.get_time_axis()
    vin = parser.get_waveform("V(in)")
    vout = parser.get_waveform("V(out)")

    plot_path = session_dir / "plot_Vout_Vin.png"
    plot_signals_vs_time(
        time_axis=time_axis,
        signals={"V(in)": vin, "V(out)": vout},
        output_png=plot_path,
    )
    if not plot_path.exists():
        raise RuntimeError(f"Plot file was not created: {plot_path}")

    print(f"Session directory: {session_dir.resolve()}")
    print(f"RAW file: {raw_path.resolve()}")
    print(f"Plot file: {plot_path.resolve()}")


if __name__ == "__main__":
    main()
