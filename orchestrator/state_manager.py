from typing import Any, Dict


class StateManager:
    @staticmethod
    def initialize(event: Dict[str, Any]) -> Dict[str, Any]:
        # Seed state from every event field an operator might expect directly
        # (e.g. complexity_score, device_record) -- "type" is routing-only.
        state = {key: value for key, value in event.items() if key != "type"}
        state.setdefault("raw_input", event.get("payload", ""))
        state["event"] = event
        state.setdefault("flags", {})
        return state
