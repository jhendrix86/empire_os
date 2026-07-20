import inspect
import sys
from pathlib import Path

import pytest
import yaml

_EMPIRE_OS_DIR = Path(__file__).resolve().parents[1]
_CASCADE_PROJECTS_DIR = _EMPIRE_OS_DIR.parent

for _path in (str(_CASCADE_PROJECTS_DIR), str(_EMPIRE_OS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from operators import all_operators as ops  # noqa: E402
from operators.operator_base import BaseOperator  # noqa: E402

MANIFESTS_DIR = _EMPIRE_OS_DIR / "manifests"


def _real_operator_engines():
    """Ground truth: the `engine` attribute actually set on each operator class."""
    real = {}
    for _, cls in inspect.getmembers(ops, inspect.isclass):
        if issubclass(cls, BaseOperator) and cls is not BaseOperator:
            real[cls.name] = cls.engine
    return real


def test_bindings_yaml_matches_real_operator_engines():
    real = _real_operator_engines()
    bindings = yaml.safe_load(open(MANIFESTS_DIR / "bindings.yaml"))["bindings"]

    unknown = [name for name in bindings if name not in real]
    assert unknown == [], f"bindings.yaml references operators not in code: {unknown}"

    mismatched = [
        (name, claimed, real[name])
        for name, claimed in bindings.items()
        if real.get(name) is not None and real[name] != claimed
    ]
    assert mismatched == [], f"bindings.yaml disagrees with code on engine: {mismatched}"


def test_operators_yaml_matches_real_operator_engines():
    real = _real_operator_engines()
    manifest = yaml.safe_load(open(MANIFESTS_DIR / "operators.yaml"))["operators"]

    unknown = [e["name"] for e in manifest if e["name"] not in real]
    assert unknown == [], f"operators.yaml references operators not in code: {unknown}"

    mismatched = [
        (e["name"], e["engine"], real[e["name"]])
        for e in manifest
        if real.get(e["name"]) is not None and real[e["name"]] != e["engine"]
    ]
    assert mismatched == [], f"operators.yaml disagrees with code on engine: {mismatched}"


def test_triggers_yaml_has_no_duplicate_keys():
    raw = open(MANIFESTS_DIR / "triggers.yaml").read()
    seen = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line == "triggers:" or line.startswith("#"):
            continue
        key = line.split(":")[0].strip()
        seen[key] = seen.get(key, 0) + 1
    duplicates = [key for key, count in seen.items() if count > 1]
    assert duplicates == [], f"triggers.yaml has duplicate event keys: {duplicates}"


def test_triggers_yaml_only_points_to_real_operators():
    real = _real_operator_engines()
    triggers = yaml.safe_load(open(MANIFESTS_DIR / "triggers.yaml"))["triggers"]
    dangling = [(event, op) for event, op in triggers.items() if op not in real]
    assert dangling == [], f"triggers.yaml points to operators not in code: {dangling}"


@pytest.mark.parametrize("manifest_file", ["bindings.yaml", "operators.yaml", "triggers.yaml"])
def test_every_manifest_entry_count_matches_real_operator_count(manifest_file):
    real = _real_operator_engines()
    data = yaml.safe_load(open(MANIFESTS_DIR / manifest_file))
    entries = next(iter(data.values()))
    assert len(entries) == len(real), (
        f"{manifest_file} has {len(entries)} entries but code defines {len(real)} operators -- "
        "an operator was added/removed without updating this manifest"
    )
