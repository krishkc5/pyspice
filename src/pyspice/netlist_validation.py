"""Validation for generated LTspice netlists."""

from __future__ import annotations

import re
from typing import Optional


_PROSE_PATTERN = re.compile(r"\b(the|and|from|to|make|should|run|analysis)\b", re.IGNORECASE)


def _normalize_stop_token(token: str) -> str:
    return re.sub(r"\s+", "", token.strip().lower())


def validate_netlist_text(netlist_text: str, tran_stop: Optional[str] = None) -> tuple[bool, str]:
    """Validate basic LTspice netlist requirements for this project."""
    if "```" in netlist_text:
        return False, "Netlist contains markdown backticks."

    stripped = netlist_text.strip()
    if not stripped:
        return False, "Netlist is empty."

    lowered = stripped.lower()
    if ".end" not in lowered:
        return False, "Netlist does not include .end."
    if ".tran" not in lowered:
        return False, "Netlist does not include .tran."

    lines = [line.strip() for line in netlist_text.splitlines() if line.strip()]
    if not lines:
        return False, "Netlist has no lines."

    for line in lines:
        if line.startswith("*") or line.startswith(";"):
            continue
        if _PROSE_PATTERN.search(line):
            return False, f"Line appears to contain English prose: {line!r}"

    if tran_stop is not None:
        required = _normalize_stop_token(tran_stop)
        tran_lines = [
            line
            for line in lines
            if not (line.startswith("*") or line.startswith(";"))
            and line.lower().startswith(".tran")
        ]
        if not tran_lines:
            return False, "Netlist does not include .tran."
        has_required = False
        for tran_line in tran_lines:
            remainder = tran_line[5:].strip()
            if _normalize_stop_token(remainder) == required:
                has_required = True
                break
        if not has_required:
            return False, f"Netlist does not include required '.tran {tran_stop}'."

    return True, "Netlist is valid."
