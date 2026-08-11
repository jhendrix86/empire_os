"""
Real-contract tests for engines/governance_engine.py's HTTP bridge to the
real governance-engine service.

Nothing exercised this bridge's actual request/response handling before
2026-08-11 (confirmed by grep - no prior test file referenced
GovernanceEngine or _check_governance). That's how two real bugs went
undiscovered: the request body never satisfied governance-engine's real
GovernanceCheckRequest schema (missing request_type/request_data/requester
- every real call would have 422'd), and the response parsing read a
top-level "allowed" key that doesn't exist on the real GovernanceCheckResponse
shape (the real field is response["decision"]["approved"]) - meaning even a
schema-valid request would have always come back denied. Both fixed in
engines/governance_engine.py; these tests pin the corrected contract using
httpx.MockTransport so they don't need a live governance-engine or RabbitMQ.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import httpx
import pytest

from empire_os.engines.governance_engine import GovernanceEngine
from empire_os.operators.operator_base import BaseOperator


class _RealOperator(BaseOperator):
    name = "RealOperator"
    type = "content"

    def execute(self, state):
        state["executed"] = True
        return state


def _engine_with_mock_transport(handler) -> GovernanceEngine:
    engine = GovernanceEngine()
    engine.client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url=engine.governance_engine_url,
    )
    return engine


@pytest.mark.asyncio
async def test_check_governance_sends_a_schema_valid_request():
    """
    The real bug: this used to POST {"operator_name", "operator_type",
    "context"} - none of which satisfy governance-engine's real
    GovernanceCheckRequest (requires request_type/request_data/requester).
    Asserts the actual fixed payload shape, not just that *a* call happens.
    """
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = __import__("json").loads(request.content)
        return httpx.Response(200, json={
            "success": True,
            "decision": {
                "decision_id": "d1", "request_id": "r1",
                "request_type": "operator.execute_request",
                "approved": True, "status": "approved", "confidence": 1.0,
                "rationale": "All rules passed", "conditions": None,
                "expires_at": None, "version": "1.0.0",
                "trace_id": "t1", "correlation_id": "c1", "causation_id": None,
                "evaluated_by": "governance-engine",
                "evaluated_at": "2026-08-11T00:00:00",
                "rule_evaluations": [], "metadata": {},
            },
            "error": None, "trace_id": "t1", "processing_time_ms": 1.0,
        })

    engine = _engine_with_mock_transport(handler)
    result = await engine._check_governance(
        operator_name="RealOperator", operator_type="content", context={"tenant_id": "t1"}
    )

    assert result["allowed"] is True
    body = captured["json"]
    assert body["request_type"] == "operator.execute_request"
    assert body["request_data"] == {"operator_name": "RealOperator", "operator_type": "content"}
    assert body["requester"] == "empire_os"
    assert body["context"] == {"tenant_id": "t1"}


@pytest.mark.asyncio
async def test_check_governance_parses_the_real_nested_response_shape():
    """
    The real bug: reading response.json().get("allowed", False) directly -
    the real response has no top-level "allowed" key, only
    decision.approved nested under "decision". Before the fix this always
    evaluated to False (denied) even on a real success=True/approved=True
    response.
    """
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "success": True,
            "decision": {
                "decision_id": "d2", "request_id": "r2",
                "request_type": "operator.execute_request",
                "approved": False, "status": "rejected", "confidence": 1.0,
                "rationale": "1 blocking rule(s) triggered", "conditions": None,
                "expires_at": None, "version": "1.0.0",
                "trace_id": "t2", "correlation_id": "c2", "causation_id": None,
                "evaluated_by": "governance-engine",
                "evaluated_at": "2026-08-11T00:00:00",
                "rule_evaluations": [], "metadata": {},
            },
            "error": None, "trace_id": "t2", "processing_time_ms": 1.0,
        })

    engine = _engine_with_mock_transport(handler)
    result = await engine._check_governance(
        operator_name="RealOperator", operator_type="content", context={}
    )

    assert result["allowed"] is False
    assert result["reason"] == "1 blocking rule(s) triggered"


@pytest.mark.asyncio
async def test_check_governance_fails_open_when_decision_missing():
    """success=False / decision=None (e.g. governance-engine's own internal
    error path) must be treated as denied, not crash on None.get(...)."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "success": False, "decision": None, "error": "boom",
            "trace_id": "t3", "processing_time_ms": 1.0,
        })

    engine = _engine_with_mock_transport(handler)
    result = await engine._check_governance(
        operator_name="RealOperator", operator_type="content", context={}
    )

    assert result["allowed"] is False
    assert result["reason"] == "boom"


def test_run_operator_executes_when_governance_approves():
    """
    End-to-end through run_operator() -> _run_operator_async() -> the real
    operator, against the real corrected request/response contract.
    Deliberately NOT an async test: run_operator() is the sync entry point
    (calls asyncio.run() internally, per its own docstring on why - the
    real api.py caller is a sync FastAPI endpoint with no running loop to
    conflict with) - calling it from an already-running event loop (as an
    @pytest.mark.asyncio test would) is exactly the RuntimeError scenario
    that contract is designed to avoid, not something to work around here.
    """
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "success": True,
            "decision": {
                "decision_id": "d4", "request_id": "r4",
                "request_type": "operator.execute_request",
                "approved": True, "status": "approved", "confidence": 1.0,
                "rationale": "All rules passed", "conditions": None,
                "expires_at": None, "version": "1.0.0",
                "trace_id": "t4", "correlation_id": "c4", "causation_id": None,
                "evaluated_by": "governance-engine",
                "evaluated_at": "2026-08-11T00:00:00",
                "rule_evaluations": [], "metadata": {},
            },
            "error": None, "trace_id": "t4", "processing_time_ms": 1.0,
        })

    engine = _engine_with_mock_transport(handler)
    result = engine.run_operator(_RealOperator(), {"tenant_id": "t1"})

    assert result["executed"] is True
    assert "governance_blocked" not in result
