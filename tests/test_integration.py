import sys
from pathlib import Path

import pytest

_EMPIRE_OS_DIR = Path(__file__).resolve().parents[1]
_CASCADE_PROJECTS_DIR = _EMPIRE_OS_DIR.parent

# engines/*.py import via the fully-qualified "empire_os.*" path, while the
# orchestrator and chain YAMLs import bare "orchestrator.*" / "operators.*".
# Both roots must be on sys.path for the two halves of the system to load together.
for _path in (str(_CASCADE_PROJECTS_DIR), str(_EMPIRE_OS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from empire_os.engines import ENGINE_REGISTRY  # noqa: E402
from orchestrator.chain_loader import load_chain  # noqa: E402

ALL_ENGINE_NAMES = sorted(ENGINE_REGISTRY.keys())


def test_every_registered_engine_has_a_chain_file():
    # Every engine in ENGINE_REGISTRY must resolve to a real chains/{name}_chain.yaml
    missing = []
    for engine_key in ALL_ENGINE_NAMES:
        try:
            load_chain(f"{engine_key}_chain")
        except FileNotFoundError:
            missing.append(engine_key)
    assert missing == []


@pytest.mark.parametrize("engine_key", ALL_ENGINE_NAMES)
def test_engine_chain_runs_end_to_end(engine_key):
    # Load the real chain, resolve its real operator classes, and run them
    # through the real engine exactly the way chain_loader + BaseEngine intend.
    chain = load_chain(f"{engine_key}_chain")
    assert len(chain) > 0

    engine = ENGINE_REGISTRY[engine_key]()
    state = {}
    for operator in chain:
        state = engine.run_operator(operator, state)

    assert isinstance(state, dict)


def test_all_engines_interoperate_on_shared_state():
    # Pipe one shared state dict through three unrelated engines' chains back
    # to back -- the same state-threading pattern main_orchestrator.orchestrate()
    # uses, just spanning multiple engines to prove they compose.
    keys = list(ENGINE_REGISTRY.keys())
    state = {
        "complexity_score": 80,
        "device_record": {
            "device_id": "d1", "hostname": "h1", "os": "Windows", "cpu": "i7",
            "ram_gb": 16, "storage_gb": 512, "role": "workstation",
        },
        "registry_keys": keys,
        "manifest_keys": keys,
    }

    for engine_key in ("talora", "computer_inventory", "spec_compliance"):
        chain = load_chain(f"{engine_key}_chain")
        engine = ENGINE_REGISTRY[engine_key]()
        for operator in chain:
            state = engine.run_operator(operator, state)

    assert state["reasoning_strategy"] == "system2"
    assert state["record_valid"] is True
    assert state["registry_manifest_diff"]["in_sync"] is True


# ---- Full main_orchestrator.orchestrate() pipeline ----
#
# This is the one entry point that ties event routing, chain loading, and
# state management together. It relies on route_event() (triggers.yaml) and
# resolve_engine_for_operator() (real operator.engine attributes) agreeing --
# exactly the drift that test_manifest_integrity.py now guards against.

from orchestrator.main_orchestrator import orchestrate  # noqa: E402


def test_orchestrate_runs_end_to_end_for_new_input_event():
    result = orchestrate({"type": "new_input", "payload": "hello world"})
    assert result["finalized"] is True
    assert result["raw_input"] == "hello world"


def test_orchestrate_runs_end_to_end_for_reasoning_request_event():
    result = orchestrate({"type": "reasoning_request", "complexity_score": 90})
    assert result["finalized"] is True
    assert result["reasoning_strategy"] == "system2"


def test_orchestrate_runs_end_to_end_for_governance_request_event():
    result = orchestrate({"type": "governance_request"})
    assert result["finalized"] is True
    assert result["flags"]["governed"] is True


def test_orchestrate_escalates_instead_of_crashing_on_operator_failure(monkeypatch):
    from orchestrator import main_orchestrator

    class _BoomOperator:
        def execute(self, state):
            raise RuntimeError("boom")

    monkeypatch.setattr(main_orchestrator, "load_chain", lambda name: [_BoomOperator()])
    result = main_orchestrator.orchestrate({"type": "new_input", "payload": "x"})

    assert result["finalized"] is True
    assert result["flags"]["escalated"] is True
    assert "boom" in result["escalation_error"]
