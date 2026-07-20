from typing import Any, Dict


def finalize_output(state: Dict[str, Any]) -> Dict[str, Any]:
    # Mark the run complete; downstream callers can rely on this key existing
    state["finalized"] = True
    return state
