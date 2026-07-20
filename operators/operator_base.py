from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseOperator(ABC):
    name: str = "BaseOperator"
    operator_type: str = "generic"
    engine: str = "none"

    def __init__(self) -> None:
        pass

    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core operator method. Receives and returns a mutable state dict.
        """
        raise NotImplementedError