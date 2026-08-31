# empire_os Integration Analysis — Roadmap Step 8, Phase A

**By the Acer session, 2026-08-31.** Read every one of the 89
`BaseOperator` classes in `operators/all_operators.py`, `operator_base.py`,
all 40 `engines/*.py`, `llm_client.py`, and `monitoring_engine_bridge.py`.
Output: what empire_os actually is, how it relates to `os42-orchestrator`,
and a scoped Phase B recommendation for the user to approve.

---

## 1. What empire_os actually is

**A synchronous reasoning-primitive library.** Every operator is a pure
`execute(state: Dict[str, Any]) -> Dict[str, Any]` — reads some keys off a
mutable `state` dict, writes derived keys/flags, returns it. No DB, no
HTTP, no async, no import-time dependencies. 89 of them; `python -m pytest`
= **243 pass in <1s**.

Operators are tagged `operator_type` (reactive / proactive / conditional /
meta) and `engine` (a domain namespace string). They compose into
pipelines — feed `state` through a sequence, each step enriches it.

### The 89 split into two unrelated groups

| group | count | examples | relevance |
|-------|-------|----------|-----------|
| **General reasoning primitives** | ~48 | `InputInterpreter`, `SafetyBoundaryOperator`, `ConstraintEnforcer`, `ErrorRecoveryOperator`, `DriftMonitor`, `ValidationOperator`, `DependencyChecker`, `PriorityResolver`, `EscalationOperator`, `LifecycleOperator`, `VersioningOperator`, `OverrideArbiter`, `AuditCycleOperator`, `AccessControlOperator`, `EnvironmentProfileOperator`, `KnowledgeGraphOperator` | **fleet-relevant** — domains input/context/governance/execution/memory/optimization/reasoning/integration/security_governance/testing_validation |
| **talora / content-brand operators** | ~41 | `ColorwaySpecOperator`, `BrandDoctrineComplianceOperator`, `UniverseLayerLookupOperator`, `CanonIndexOperator`, `SegmentOverlapOperator` ("Proof Tier Hierarchy"), `LogicToMotionOperator`, `ResearchDepartmentOperator`, the 5-stage `ResearchDepartment→ShippingPackager` LLM pipeline | **out of scope** — these belong to `os42-talora-system`, the content/brand vision explicitly separated from the engineering fleet on 2026-08-12 (engines `cfa`/`talora`/`brand_geometry`/`audience_graph`/`brand_enforcement`/`maximum_universe`/`bundle_strategy`) |

### The `engines/` directory is mostly dead scaffolding

40 files, each ~9 lines: `class XEngine(BaseEngine): def run_operator(self,
operator, state): return operator.execute(state)` — a pure pass-through
that adds **nothing**. Only **`governance_engine.py`** (266 lines) does
real work: it's the HTTP bridge to the standalone `governance-engine`
FastAPI service (Stage 3.2). `monitoring_engine_bridge.py` (28 lines) is a
newer, working *prototype* of the right pattern — pulls real metrics from
`monitoring-engine/performance/summary` and pipes them through the
`DriftMonitor` operator, honest-failure on error — but nothing calls it
yet.

---

## 2. Relationship to `os42-orchestrator` — NOT competing

The roadmap's open question ("reasoning substrate *under* the orchestrator,
or a second decision-maker?"). Answer: **neither overlaps the other at
all.**

| | `os42-orchestrator` | `empire_os` operators |
|---|---|---|
| unit of work | a multi-step business workflow across engines | one enrichment of a `state` dict |
| I/O | async HTTP to engine REST APIs | none — pure in-process |
| what it decides | "scale budget", "pause campaign" from live business metrics | "needs_clarification", "safety_ok", "recovery_action=retry" from the request itself |
| where it runs | its own service (:8050), a background loop | inline, inside whatever calls it |

The word "engine" is a false cognate — orchestrator's `ENGINE_URLS`
(HTTP peers) and empire_os's `engines/*.py` (namespace wrappers) are
unrelated. **There is no redundancy to resolve.** empire_os could be the
per-request reasoning layer that runs *before* an orchestrator step or
*inside* an engine handler, but it is not an alternative to either.

---

## 3. The real integration value

Step 12's security pass just confirmed the fleet has **no input
hardening, no per-request auth, no output-constraint enforcement, no
structured audit trail, no drift detection**. Several general operators
encode exactly those policies, already tested:

| operator | fleet gap it fills |
|----------|--------------------|
| `SafetyBoundaryOperator` | scans text for prompt-injection / `drop table` / `<script` patterns — the fleet does **zero** input sanitisation (SECURITY_REVIEW dynamic pass) |
| `AccessControlOperator` | role → {read, execute, write, admin} — the fleet has **no auth at all** on ~10 engines |
| `ErrorRecoveryOperator` | classify an error (timeout / validation / unknown) → retry-vs-abort with a retry ceiling — per-request, complements the DLQ chain's queue-level retry |
| `ConstraintEnforcer` / `ValidationOperator` | output length / forbidden-words / required-fields checks before a response leaves an engine |
| `AuditCycleOperator` | append a timestamped flags snapshot — a real audit entry, which no engine writes today |
| `DriftMonitor` | metric-vs-baseline % deviation — `monitoring-engine` polls `/health` but does **not** do drift |
| `EnvironmentProfileOperator` | local/staging/production → tier ceiling + external-calls-allowed gate |

---

## 4. Recommended Phase B (needs user approval)

**Do:**
1. **Package the ~48 general operators as an installable shared lib**
   (`empire-operators/`, same sibling-package pattern as `autonomy-events`
   / `unkey-auth` / `ab-testing`). Leave the 41 talora operators behind in
   `empire_os` (or move them to `os42-talora-system`).
2. **First real wire: `SafetyBoundaryOperator` as ASGI middleware** on the
   write-heavy engines (`sales` / `customer-support` / `integration` /
   `notification` / `content`) — reject requests whose body matches an
   unsafe pattern. Directly closes a Step 12 HIGH finding. ~1 middleware
   file, reused across engines.
3. **Second: promote `monitoring_engine_bridge.py`'s pattern** to a real
   scheduled job — pull `monitoring-engine` metrics through `DriftMonitor`
   on an interval, raise a `notification-engine` alert on drift. Gives the
   fleet its first real drift detection.

**Don't:**
- Build out the 40 empty `engines/*.py` wrappers.
- Treat empire_os as a service to HTTP-call (only the governance bridge
  should stay that shape, because it fronts a real remote service).
- Touch the ~41 talora/CFA/brand operators — that's the separated system.
- Aim for "wire all 88" — that was never the right goal; it's why the
  original estimate was 10–15 sessions.

**Effort:** packaging + the SafetyBoundary middleware ≈ **1 session**. The
drift job ≈ another half.

**Open question for the user:** is the reasoning layer worth adding *now*
(before real traffic / real tenants / real auth exist), or is it better
sequenced after decisions 4.1 (tenant enforcement) and 4.5 (inter-engine
auth)? `SafetyBoundaryOperator` middleware is worth doing regardless — it's
cheap and it's defense the fleet has none of.
