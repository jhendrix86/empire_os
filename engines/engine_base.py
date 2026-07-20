from abc import ABC, abstractmethod
from typing import Any, Dict
from empire_os.operators.operator_base import BaseOperator


class BaseEngine(ABC):
    name: str = "base"

    def __init__(self) -> None:
        pass

    @abstractmethod
    def run_operator(self, operator: BaseOperator, state: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
