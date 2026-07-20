from pathlib import Path

import yaml

_TRIGGERS_PATH = Path(__file__).resolve().parent.parent / "manifests" / "triggers.yaml"

with open(_TRIGGERS_PATH) as f:
    TRIGGERS = yaml.safe_load(f)["triggers"]

def route_event(event):
    return TRIGGERS.get(event["type"])