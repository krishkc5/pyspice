from __future__ import annotations

from types import SimpleNamespace

from pyspice.llm import extract_tran_stop, generate_netlist


def _response_with_content(content: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def test_generate_netlist_retries_then_succeeds(monkeypatch):
    calls = {"count": 0}
    prompt_holder = {"system_prompt": ""}

    class FakeCompletions:
        def create(self, **kwargs):
            calls["count"] += 1
            prompt_holder["system_prompt"] = kwargs["messages"][0]["content"]
            if calls["count"] == 1:
                return _response_with_content("this is prose and invalid")
            return _response_with_content(
                "* RLC netlist\n"
                "V1 in 0 PULSE(0 12 0.8m 2u 2u 0.8m 4m)\n"
                "R1 in out 220\n"
                "L1 out mid 3.3m\n"
                "C1 mid 0 47u\n"
                ".tran 6 ms\n"
                ".end\n"
            )

    class FakeClient:
        def __init__(self, api_key: str):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr("pyspice.llm.OpenAI", FakeClient)

    netlist = generate_netlist(
        api_key="test-key",
        natural_language_spec="spec",
        tran_stop="6ms",
        max_attempts=3,
    )
    assert ".tran 6 ms" in netlist
    assert netlist.strip().endswith(".end")
    assert calls["count"] == 2
    assert "You must include exactly this directive: .tran 6ms" in prompt_holder["system_prompt"]


def test_extract_tran_stop():
    assert extract_tran_stop("Run transient analysis for 6 ms.") == "6ms"
    assert extract_tran_stop("run for 5ms") == "5ms"
    assert extract_tran_stop("simulate over 3 ms total") == "3ms"
    assert extract_tran_stop("run transient analysis for 0.01 s") == "0.01s"
    assert extract_tran_stop("no transient duration here") is None
