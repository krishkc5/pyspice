"""OpenAI integration for LTspice netlist generation."""

from __future__ import annotations

import logging
import re
from typing import Optional

from openai import OpenAI

from pyspice.netlist_validation import validate_netlist_text

LOGGER = logging.getLogger(__name__)

_DURATION_PATTERNS = [
    re.compile(r"(?i)\b(?:run transient analysis for|run for|over|for)\s*([0-9]*\.?[0-9]+)\s*(ms|s)\b"),
]


def extract_tran_stop(spec_text: str) -> Optional[str]:
    """
    Extract transient stop time token from natural language spec.

    Returns normalized LTspice token like "6ms" or "0.01s", or None.
    """
    for pattern in _DURATION_PATTERNS:
        match = pattern.search(spec_text)
        if match:
            value = match.group(1)
            unit = match.group(2).lower()
            return f"{value}{unit}"
    return None


def _build_system_prompt(tran_stop: Optional[str]) -> str:
    base_prompt = (
        "You are an expert LTspice netlist generator.\n"
        "Return ONLY pure LTspice netlist text.\n"
        "Do not include markdown fences.\n"
        "Do not include explanations.\n"
        "Always include a title comment line at the top.\n"
        "Always include .end as the final directive.\n"
    )
    if tran_stop is not None:
        return base_prompt + f"You must include exactly this directive: .tran {tran_stop}"
    return base_prompt + "A .tran directive must be present."


def generate_netlist(
    *,
    api_key: str,
    natural_language_spec: str,
    tran_stop: Optional[str] = None,
    max_attempts: int = 3,
) -> str:
    """
    Generate a valid LTspice netlist with retry-on-validation-failure.

    max_attempts=3 means 1 initial attempt + up to 2 retries.
    """
    client = OpenAI(api_key=api_key)
    last_error = "Unknown validation failure."

    for attempt in range(1, max_attempts + 1):
        LOGGER.info("Requesting netlist from OpenAI", extra={"attempt": attempt, "max_attempts": max_attempts})
        response = client.chat.completions.create(
            model="gpt-4.1",
            temperature=0.1,
            messages=[
                {"role": "system", "content": _build_system_prompt(tran_stop)},
                {"role": "user", "content": natural_language_spec},
            ],
        )
        netlist_text = (response.choices[0].message.content or "").strip()
        is_valid, reason = validate_netlist_text(netlist_text, tran_stop=tran_stop)
        if is_valid:
            LOGGER.info("Generated netlist passed validation", extra={"attempt": attempt})
            return netlist_text

        last_error = reason
        LOGGER.warning("Generated netlist failed validation", extra={"attempt": attempt, "reason": reason})

    raise RuntimeError(f"Failed to generate a valid LTspice netlist after {max_attempts} attempts: {last_error}")


def generate_netlist_with_retries(
    *,
    api_key: str,
    natural_language_spec: str,
    tran_stop: Optional[str] = None,
    max_attempts: int = 3,
) -> str:
    """Backward-compatible alias for generate_netlist()."""
    return generate_netlist(
        api_key=api_key,
        natural_language_spec=natural_language_spec,
        tran_stop=tran_stop,
        max_attempts=max_attempts,
    )
