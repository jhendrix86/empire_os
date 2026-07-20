from pathlib import Path

import yaml
from importlib import import_module

CHAINS_DIR = Path(__file__).resolve().parent.parent / "chains"

def load_chain(chain_name):
    with open(CHAINS_DIR / f"{chain_name}.yaml") as f:
        data = yaml.safe_load(f)

    operators = []
    for op in data["sequence"]:
        module_path = op["module"].replace("/", ".").replace(".py", "")
        module = import_module(module_path)
        operator_class = getattr(module, op["class"])
        operators.append(operator_class())

    return operators


def resolve_engine_for_operator(operator_name):
    # Look up which engine a triggered operator belongs to by reading its
    # real `engine` class attribute in operators.all_operators -- not a
    # manifest file, so this can never drift out of sync with the code.
    module = import_module("operators.all_operators")
    operator_class = getattr(module, operator_name, None)
    if operator_class is None:
        raise ValueError(f"Unknown operator: {operator_name}")
    return operator_class.engine