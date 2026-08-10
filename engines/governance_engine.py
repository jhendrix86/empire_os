"""
Governance Engine Bridge

Bridges empire_os workflow engine to the real governance-engine service
for policy evaluation and enforcement decisions.
"""

import asyncio
import httpx
import os
from typing import Any, Dict, Optional
from .engine_base import BaseEngine
from empire_os.operators.operator_base import BaseOperator
import structlog

logger = structlog.get_logger()


class GovernanceEngine(BaseEngine):
    """
    Governance Engine that delegates to the real governance-engine service.

    Evaluates policies, enforces constraints, and provides governance decisions
    for workflow execution, resource management, and operational control.
    """

    name = "governance"

    def __init__(self):
        super().__init__()
        # Was defaulting to :8043 (monitoring-engine's real port) instead of
        # governance-engine's actual :8033 - confirmed against
        # governance-engine/app/utils/config.py's real `port: int = 8033`
        # default (2026-08-10 OS42_REPAIR_PLAN.md reconciliation). This bug
        # meant the "governance bridge" was silently calling the wrong
        # service, or nothing, depending on what else was running.
        self.governance_engine_url = os.getenv(
            "GOVERNANCE_ENGINE_URL",
            "http://localhost:8033"
        )
        self.timeout = 30.0  # seconds
        self.client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> None:
        """Initialize the governance engine client"""
        self.client = httpx.AsyncClient(timeout=self.timeout)
        logger.info("governance_engine_initialized", url=self.governance_engine_url)

    async def shutdown(self) -> None:
        """Shutdown the governance engine client"""
        if self.client:
            await self.client.aclose()
        logger.info("governance_engine_shutdown")

    def run_operator(
        self,
        operator: BaseOperator,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sync entry point required by BaseEngine (every other engine in this
        fleet implements run_operator synchronously - GovernanceEngine was
        the sole exception, introduced by the Stage 3.2 governance bridge,
        which broke both this engine's tests and any other synchronous
        caller silently returning a coroutine instead of a result. Found
        during the 2026-08-10 port-bug fix, confirmed pre-existing (fails
        identically on the commit before that fix) via `git stash`. api.py's
        POST /engines/{name}/run calls this from a sync FastAPI endpoint
        (threadpool, no running event loop), so asyncio.run() here is safe.
        """
        return asyncio.run(self._run_operator_async(operator, state))

    async def _run_operator_async(
        self,
        operator: BaseOperator,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run an operator through governance evaluation.

        Delegates to the real governance-engine service for policy evaluation,
        then executes the operator if approved.

        Args:
            operator: The operator to execute
            state: Current system state

        Returns:
            Execution result from the operator
        """
        if not self.client:
            logger.warning("governance_client_not_initialized")
            return operator.execute(state)

        try:
            # Check governance policies
            governance_decision = await self._check_governance(
                operator_name=operator.__class__.__name__,
                operator_type=getattr(operator, "type", "generic"),
                context=state
            )

            if not governance_decision.get("allowed", False):
                logger.warning(
                    "governance_check_failed",
                    operator=operator.__class__.__name__,
                    reason=governance_decision.get("reason")
                )
                return {
                    "success": False,
                    "error": governance_decision.get("reason", "Governance check failed"),
                    "governance_blocked": True
                }

            # Execute the operator
            result = operator.execute(state)

            # Log the execution for audit trail
            await self._log_governance_action(
                operator_name=operator.__class__.__name__,
                operator_type=getattr(operator, "type", "generic"),
                result=result,
                context=state
            )

            return result

        except Exception as e:
            logger.error(
                "governance_engine_error",
                operator=operator.__class__.__name__,
                error=str(e)
            )
            return operator.execute(state)

    async def _check_governance(
        self,
        operator_name: str,
        operator_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check governance policies with the remote service.

        Args:
            operator_name: Name of the operator
            operator_type: Type of operator
            context: Current context/state

        Returns:
            Governance decision {"allowed": bool, "reason": str, ...}
        """
        if not self.client:
            return {"allowed": True}

        try:
            response = await self.client.post(
                f"{self.governance_engine_url}/governance/check",
                json={
                    "operator_name": operator_name,
                    "operator_type": operator_type,
                    "context": context
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(
                    "governance_check_failed",
                    status_code=response.status_code,
                    response=response.text[:200]
                )
                return {
                    "allowed": False,
                    "reason": f"Governance service returned {response.status_code}"
                }

        except httpx.RequestError as e:
            logger.warning(
                "governance_service_unreachable",
                url=self.governance_engine_url,
                error=str(e)
            )
            # Fail open: allow execution if governance service is unreachable
            return {"allowed": True}

    async def _log_governance_action(
        self,
        operator_name: str,
        operator_type: str,
        result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> None:
        """
        Log governance action for audit trail.

        Args:
            operator_name: Name of executed operator
            operator_type: Type of operator
            result: Execution result
            context: Execution context

        KNOWN GAP (2026-08-10 reconciliation, not fixed here): POST
        /governance/log-action does not exist anywhere in governance-engine
        (confirmed against its real controllers - only /governance/check,
        /history/{id}, /rules, /override, /emergency-stop, /rollback, plus
        /dlq/* exist). This call has always 404'd, silently swallowed by the
        except below - operator-execution-result logging has never actually
        worked. Distinct from /governance/check's own decision history
        (GET /governance/history/{entity_id}), which records *policy
        decisions*, not *operator execution outcomes* - so that existing
        endpoint isn't a drop-in fix. Needs a real design decision (add a
        matching endpoint to governance-engine, or decide this audit trail
        isn't needed) before "fixing" it - left as a flagged gap, not
        guessed at, matching this reconciliation's own rule.
        """
        if not self.client:
            return

        try:
            await self.client.post(
                f"{self.governance_engine_url}/governance/log-action",
                json={
                    "operator_name": operator_name,
                    "operator_type": operator_type,
                    "result_success": result.get("success", False),
                    "context": context
                },
                timeout=5.0  # Shorter timeout for logging
            )
        except Exception as e:
            # Don't fail if logging fails
            logger.debug("governance_action_logging_failed", error=str(e))