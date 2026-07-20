"""
Thin HTTP surface over the empire_os engine/operator/orchestrator runtime.
Makes the 36 registered engines visible and triggerable from any UI --
previously the only way to touch any of this was running Python directly.
"""
import sys
from pathlib import Path
from typing import Any, Dict, Optional

_EMPIRE_OS_DIR = Path(__file__).resolve().parent
_CASCADE_PROJECTS_DIR = _EMPIRE_OS_DIR.parent

# engines/*.py import via the fully-qualified "empire_os.*" path, while the
# orchestrator and chain YAMLs import bare "orchestrator.*" / "operators.*".
# Both roots must be on sys.path -- same requirement as tests/test_integration.py.
for _path in (str(_CASCADE_PROJECTS_DIR), str(_EMPIRE_OS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from empire_os.engines import ENGINE_REGISTRY
from orchestrator.chain_loader import load_chain
from orchestrator.main_orchestrator import orchestrate

app = FastAPI(title="empire_os API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunEngineRequest(BaseModel):
    state: Dict[str, Any] = {}


class OrchestrateRequest(BaseModel):
    type: str
    payload: Optional[Any] = None
    extra: Dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "empire_os-api", "engine_count": len(ENGINE_REGISTRY)}


@app.get("/engines")
def list_engines():
    return {"engines": sorted(ENGINE_REGISTRY.keys()), "count": len(ENGINE_REGISTRY)}


@app.get("/engines/{name}")
def engine_detail(name: str):
    if name not in ENGINE_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Unknown engine: {name}")
    try:
        chain = load_chain(f"{name}_chain")
        operators = [op.__class__.__name__ for op in chain]
    except FileNotFoundError:
        operators = []
    return {"name": name, "operators": operators}


@app.post("/engines/{name}/run")
def run_engine(name: str, req: RunEngineRequest):
    if name not in ENGINE_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Unknown engine: {name}")
    try:
        chain = load_chain(f"{name}_chain")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No chain file for engine: {name}")

    engine = ENGINE_REGISTRY[name]()
    state = dict(req.state)
    for operator in chain:
        state = engine.run_operator(operator, state)
    return {"engine": name, "result": state}


@app.post("/orchestrate")
def orchestrate_event(req: OrchestrateRequest):
    event: Dict[str, Any] = {"type": req.type, **req.extra}
    if req.payload is not None:
        event["payload"] = req.payload
    try:
        return orchestrate(event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
