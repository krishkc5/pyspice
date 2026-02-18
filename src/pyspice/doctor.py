"""Prerequisite diagnostics for pyspice."""

from __future__ import annotations

import argparse
import os

from pyspice.config import load_environment, resolve_ltspice_path


def run_doctor() -> None:
    """Print prerequisite report and raise helpful errors when missing."""
    load_environment()

    api_key_present = bool(os.getenv("OPENAI_API_KEY"))
    ltspice_path_override = os.getenv("LTSPICE_PATH")

    resolved_ltspice_path: str | None = None
    ltspice_error: str | None = None
    try:
        resolved_ltspice_path = resolve_ltspice_path()
    except RuntimeError as exc:
        ltspice_error = str(exc)

    print("pyspice doctor")
    print(f"OPENAI_API_KEY present: {'yes' if api_key_present else 'no'}")
    print(f"LTSPICE_PATH set: {'yes' if ltspice_path_override else 'no'}")
    print(f"Resolved LTspice path: {resolved_ltspice_path or '(not found)'}")

    errors: list[str] = []
    if not api_key_present:
        errors.append(
            "Missing OPENAI_API_KEY. Add it to your shell or .env file."
        )
    if ltspice_error:
        errors.append(ltspice_error)

    if errors:
        raise RuntimeError("Prerequisite check failed:\n- " + "\n- ".join(errors))


def main() -> None:
    parser = argparse.ArgumentParser(prog="pyspice", description="pyspice utilities")
    parser.add_argument(
        "command",
        choices=["doctor"],
        help="Command to run. Use 'doctor' for prerequisite diagnostics.",
    )
    args = parser.parse_args()

    if args.command == "doctor":
        run_doctor()


if __name__ == "__main__":
    main()
