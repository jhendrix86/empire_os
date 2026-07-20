from typing import Any, Dict


def handle_escalation(error: Exception, state: Dict[str, Any]) -> Dict[str, Any]:
    # Record the failure on state instead of letting it crash the run
    state.setdefault("flags", {})
    state["flags"]["escalated"] = True
    state["escalation_error"] = str(error)
    return state
