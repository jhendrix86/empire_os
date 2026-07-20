from typing import Any, Dict
from .engine_base import BaseEngine
from empire_os.operators.operator_base import BaseOperator


class InputEngine(BaseEngine):
    name = "input"

    def run_operator(self, operator: BaseOperator, state: Dict[str, Any]) -> Dict[str, Any]:
        # Place for input-specific pre/post hooks if needed
        return operator.execute(state)