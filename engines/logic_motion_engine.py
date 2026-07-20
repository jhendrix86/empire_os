from typing import Any, Dict
from .engine_base import BaseEngine
from empire_os.operators.operator_base import BaseOperator


class LogicMotionEngine(BaseEngine):
    name = "logic_motion"

    def run_operator(self, operator: BaseOperator, state: Dict[str, Any]) -> Dict[str, Any]:
        return operator.execute(state)
