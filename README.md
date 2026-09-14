# empire_os

A synchronous **reasoning-primitive library** for the AEON fleet: a set of
small, pure operators that read a mutable `state` dict, write derived
keys/flags, and return it — composed into named pipelines. No database, no
async, no import-time side effects. `python -m pytest` → **243 passing in
<1s**.

It is a **separate system** from the standalone `*-engine` microservices
and from `baselayer` — it shares no code or runtime with them. Only its
governance bridge is currently wired to the rest of the fleet; see
[EMPIRE_OS_INTEGRATION_ANALYSIS.md](EMPIRE_OS_INTEGRATION_ANALYSIS.md) for
the full picture and the roadmap for connecting more of it.

## Layout

| Path | What it is |
|------|-----------|
| `operators/all_operators.py` | The 89 `BaseOperator` classes — `execute(state) -> state`. Tagged by `operator_type` (reactive / proactive / conditional / meta) and `engine` (domain namespace). |
| `operators/operator_base.py` | `BaseOperator` and the shared contract. |
| `operators/llm_client.py` | The one operator group that calls out — a real OpenAI client used by the 5-stage `product_pipeline`. |
| `engines/` | Thin dispatchers: `ENGINE_REGISTRY` (36 entries in `engines/__init__.py`) maps a domain name to an engine class that runs its operators. Most `engines/*.py` files are ~9-line pass-throughs; the real logic is in the operators. |
| `orchestrator/` | `chain_loader.py` + `main_orchestrator.py` — load a chain (a YAML pipeline under `chains/`) and run `state` through its operator sequence. |
| `chains/` | YAML pipeline definitions. |
| `manifests/` | Declarative engine/operator manifests; `tests/test_manifest_integrity.py` keeps them in sync with the code. |
| `api.py` | Thin FastAPI surface over the runtime (see below). |
| `tests/` | 243 tests — operators, engines, chains, orchestrator, manifest integrity, the governance bridge, and the stub-operators-now-real regression set. |

### Two unrelated operator groups

- **~48 general reasoning primitives** — `InputInterpreter`,
  `SafetyBoundaryOperator`, `ConstraintEnforcer`, `ErrorRecoveryOperator`,
  `DriftMonitor`, `ValidationOperator`, `PriorityResolver`,
  `EscalationOperator`, `AuditCycleOperator`, `AccessControlOperator`,
  `KnowledgeGraphOperator`, … These are the fleet-relevant ones (input,
  context, governance, execution, memory, optimization, reasoning,
  integration, security, testing/validation domains).
- **~41 talora / content-brand operators** — `ColorwaySpecOperator`,
  `BrandDoctrineComplianceOperator`, `UniverseLayerLookupOperator`, the
  `ResearchDepartment → ShippingPackager` LLM pipeline, … These belong to
  the `os42-talora-system` content/brand vision, which was deliberately
  separated from the engineering fleet on 2026-08-12. Present here for
  history; not in scope for fleet work.

## Run it

```bash
pip install -r requirements.txt
python -m pytest -q                     # 243 passing

# HTTP surface (port 8100)
uvicorn empire_os.api:app --host 0.0.0.0 --port 8100
# or: docker build -t empire_os . && docker run -p 8100:8100 empire_os
```

`api.py` puts both `CascadeProjects/` and `empire_os/` on `sys.path`
because `engines/*.py` import as `empire_os.*` while chains/orchestrator
import bare `orchestrator.*` / `operators.*` — run it as
`empire_os.api:app` from the parent directory, matching
`tests/test_integration.py`.

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | liveness |
| `GET` | `/engines` | list the 36 registered engines |
| `GET` | `/engines/{name}` | describe one engine |
| `POST` | `/engines/{name}/run` | run one engine over a supplied `state` dict |
| `POST` | `/orchestrate` | run an event through a chain via the orchestrator |

## Status

- All 89 operators have real logic (the ~40 placeholder stubs were
  replaced 2026-08-01; `tests/test_stub_operators_real_logic.py` guards
  the regression). HTTP API boots and is tested. CI runs the suite on
  push (`.github/workflows`).
- **Fleet integration is minimal.** Only `engines/governance_engine.py` is
  a real bridge (HTTP to `governance-engine`); the other ~37 dispatchers
  are pass-throughs with no external caller. Connecting more of the
  general-reasoning operators to the fleet is roadmap Step 8 / Phase B —
  see [EMPIRE_OS_INTEGRATION_ANALYSIS.md](EMPIRE_OS_INTEGRATION_ANALYSIS.md)
  and `../AEON_GAP_REGISTER.md` MV-04.

## License

Proprietary — All Rights Reserved. See [LICENSE](LICENSE).

## Business Context

This repo is engineering-only — code, tests, and architecture. Business,
brand, and venture context (product catalog, pricing, offers, brand voice,
sales funnels, platform/channel strategy, ops calendar) lives in the
**Empire OS** Notion workspace, not here:

- [Command Center](https://app.notion.com/p/3a703d47c57e81d4aaf3d1136bc94b55) — master index
- [System Glossary & Structure](https://app.notion.com/p/3a703d47c57e816ea082cbc790ffce1e) — canonical naming (Empire OS / StructuredMenace / TALORA / Verolyn)
- [TALORA — Build Status & Capability Log](https://app.notion.com/p/3cf03d47c57e8192b87ef6f2003323c6) — the business side's view of what's built

**Known gap (2026-09-14, not yet reconciled):** the Notion build-status log
above currently only knows about `baselayer` as a confirmed real repo. It has
no record of this repo (89 operators, 36 engines, 243 tests) or of the ~20
other `*-engine` repos in this account. Until that reconciliation happens,
treat this README, `EMPIRE_OS_INTEGRATION_ANALYSIS.md`, and
`../AEON_GAP_REGISTER.md` as the current source of truth for engineering
state — not the Notion log.
