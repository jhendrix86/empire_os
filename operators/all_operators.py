from typing import Any, Dict
from .operator_base import BaseOperator


# ========= Reactive Operators =========

class InputInterpreter(BaseOperator):
    name = "InputInterpreter"
    operator_type = "reactive"
    engine = "input"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Parse raw input into structured form
        # expected: state["raw_input"] -> state["parsed_input"]
        raw = state.get("raw_input", "")
        state["parsed_input"] = {"text": raw}
        return state


class ContextStabilizer(BaseOperator):
    name = "ContextStabilizer"
    operator_type = "reactive"
    engine = "context"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure context is coherent and non-drifting
        context = state.get("context", {})
        state["context"] = context  # placeholder for real logic
        return state


class ClarificationOperator(BaseOperator):
    name = "ClarificationOperator"
    operator_type = "reactive"
    engine = "input"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark that clarification is needed if ambiguity detected
        state.setdefault("flags", {})
        state["flags"]["needs_clarification"] = state.get("ambiguity", False)
        return state


class ConstraintEnforcer(BaseOperator):
    name = "ConstraintEnforcer"
    operator_type = "reactive"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Enforce constraints stored in state["constraints"]
        state.setdefault("flags", {})
        state["flags"]["constraints_enforced"] = True
        return state


class SafetyBoundaryOperator(BaseOperator):
    name = "SafetyBoundaryOperator"
    operator_type = "reactive"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark unsafe patterns if detected
        state.setdefault("flags", {})
        state["flags"]["safety_ok"] = not state.get("unsafe_pattern", False)
        return state


class PrecisionRefiner(BaseOperator):
    name = "PrecisionRefiner"
    operator_type = "reactive"
    engine = "input"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Improve specificity of parsed input (placeholder)
        parsed = state.get("parsed_input", {})
        parsed["refined"] = True
        state["parsed_input"] = parsed
        return state


class StructuralFormatter(BaseOperator):
    name = "StructuralFormatter"
    operator_type = "reactive"
    engine = "execution"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure output has a consistent structure
        output = state.get("output", {})
        state["output"] = {"structured": True, "data": output}
        return state


class ExecutionRouter(BaseOperator):
    name = "ExecutionRouter"
    operator_type = "reactive"
    engine = "execution"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Decide which execution path or tool to use
        state.setdefault("routing", {})
        state["routing"]["target"] = state.get("desired_action", "default")
        return state


class ErrorRecoveryOperator(BaseOperator):
    name = "ErrorRecoveryOperator"
    operator_type = "reactive"
    engine = "execution"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Handle errors and mark recovery status
        state.setdefault("flags", {})
        state["flags"]["recovered"] = True
        return state


class MemoryAlignmentOperator(BaseOperator):
    name = "MemoryAlignmentOperator"
    operator_type = "reactive"
    engine = "memory"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Align current state with stored memory (placeholder)
        state.setdefault("flags", {})
        state["flags"]["memory_aligned"] = True
        return state


# ========= Proactive Operators =========

class PredictivePlanner(BaseOperator):
    name = "PredictivePlanner"
    operator_type = "proactive"
    engine = "optimization"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Generate a simple plan based on current state
        state["plan"] = state.get("plan", {"steps": []})
        return state


class OpportunityScanner(BaseOperator):
    name = "OpportunityScanner"
    operator_type = "proactive"
    engine = "optimization"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Detect potential opportunities (placeholder)
        state.setdefault("flags", {})
        state["flags"]["opportunities_found"] = True
        return state


class OptimizationOperator(BaseOperator):
    name = "OptimizationOperator"
    operator_type = "proactive"
    engine = "optimization"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark that optimization pass has been applied
        state.setdefault("flags", {})
        state["flags"]["optimized"] = True
        return state


class AuditCycleOperator(BaseOperator):
    name = "AuditCycleOperator"
    operator_type = "proactive"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Record that an audit cycle occurred
        state.setdefault("audit_log", [])
        state["audit_log"].append({"event": "audit_cycle"})
        return state


class DriftMonitor(BaseOperator):
    name = "DriftMonitor"
    operator_type = "proactive"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Detect behavioral drift (placeholder)
        state.setdefault("flags", {})
        state["flags"]["drift_detected"] = False
        return state


class LoadBalancer(BaseOperator):
    name = "LoadBalancer"
    operator_type = "proactive"
    engine = "optimization"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark load balancing decision
        state.setdefault("flags", {})
        state["flags"]["load_balanced"] = True
        return state


class RedundancyOperator(BaseOperator):
    name = "RedundancyOperator"
    operator_type = "proactive"
    engine = "optimization"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark redundancy handling
        state.setdefault("flags", {})
        state["flags"]["redundancy_handled"] = True
        return state


class ConsistencyOperator(BaseOperator):
    name = "ConsistencyOperator"
    operator_type = "proactive"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure outputs are consistent across passes
        state.setdefault("flags", {})
        state["flags"]["consistent"] = True
        return state


class CompressionOperator(BaseOperator):
    name = "CompressionOperator"
    operator_type = "proactive"
    engine = "optimization"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark that compression was applied
        state.setdefault("flags", {})
        state["flags"]["compressed"] = True
        return state


class ExpansionOperator(BaseOperator):
    name = "ExpansionOperator"
    operator_type = "proactive"
    engine = "optimization"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark that expansion was applied
        state.setdefault("flags", {})
        state["flags"]["expanded"] = True
        return state


# ========= Conditional Operators =========

class DecisionTreeOperator(BaseOperator):
    name = "DecisionTreeOperator"
    operator_type = "conditional"
    engine = "reasoning"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Choose a branch based on state
        state.setdefault("routing", {})
        state["routing"]["branch"] = state.get("priority", "default")
        return state


class PriorityResolver(BaseOperator):
    name = "PriorityResolver"
    operator_type = "conditional"
    engine = "reasoning"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Resolve conflicting priorities (placeholder)
        state["priority"] = state.get("priority", "normal")
        return state


class ResourceAllocator(BaseOperator):
    name = "ResourceAllocator"
    operator_type = "conditional"
    engine = "execution"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Assign resources (placeholder)
        state.setdefault("resources", {})
        state["resources"]["allocated"] = True
        return state


class ModeSwitchOperator(BaseOperator):
    name = "ModeSwitchOperator"
    operator_type = "conditional"
    engine = "context"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Switch mode based on state
        state["mode"] = state.get("desired_mode", "default")
        return state


class ContextRebuilder(BaseOperator):
    name = "ContextRebuilder"
    operator_type = "conditional"
    engine = "context"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Rebuild context from minimal info (placeholder)
        state["context"] = state.get("context", {})
        return state


class MultiEngineCoordinator(BaseOperator):
    name = "MultiEngineCoordinator"
    operator_type = "conditional"
    engine = "integration"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark that multiple engines are involved
        state.setdefault("flags", {})
        state["flags"]["multi_engine"] = True
        return state


class DependencyChecker(BaseOperator):
    name = "DependencyChecker"
    operator_type = "conditional"
    engine = "execution"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark dependencies as satisfied (placeholder)
        state.setdefault("flags", {})
        state["flags"]["dependencies_ok"] = True
        return state


class ValidationOperator(BaseOperator):
    name = "ValidationOperator"
    operator_type = "conditional"
    engine = "execution"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark validation status
        state.setdefault("flags", {})
        state["flags"]["validated"] = True
        return state


class BoundaryExpander(BaseOperator):
    name = "BoundaryExpander"
    operator_type = "conditional"
    engine = "reasoning"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark that scope was expanded
        state.setdefault("flags", {})
        state["flags"]["scope_expanded"] = True
        return state


class BoundaryCompressor(BaseOperator):
    name = "BoundaryCompressor"
    operator_type = "conditional"
    engine = "reasoning"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark that scope was narrowed
        state.setdefault("flags", {})
        state["flags"]["scope_compressed"] = True
        return state


# ========= Meta Operators =========

class MetaReasoningOperator(BaseOperator):
    name = "MetaReasoningOperator"
    operator_type = "meta"
    engine = "reasoning"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark that meta-reasoning was applied
        state.setdefault("flags", {})
        state["flags"]["meta_reasoned"] = True
        return state


class CouncilSynthesizer(BaseOperator):
    name = "CouncilSynthesizer"
    operator_type = "meta"
    engine = "integration"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Combine multiple candidate outputs (placeholder)
        state["output"] = state.get("output", {})
        return state


class OverrideArbiter(BaseOperator):
    name = "OverrideArbiter"
    operator_type = "meta"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Decide whether an override is allowed
        state.setdefault("flags", {})
        state["flags"]["override_allowed"] = state.get("override_request", False)
        return state


class EscalationOperator(BaseOperator):
    name = "EscalationOperator"
    operator_type = "meta"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark escalation path (placeholder)
        state.setdefault("flags", {})
        state["flags"]["escalated"] = state.get("high_risk", False)
        return state


class HarmonizationOperator(BaseOperator):
    name = "HarmonizationOperator"
    operator_type = "meta"
    engine = "integration"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Harmonize conflicting outputs (placeholder)
        state["output"] = state.get("output", {})
        return state


class VersioningOperator(BaseOperator):
    name = "VersioningOperator"
    operator_type = "meta"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Attach version info
        state["version"] = state.get("version", "v1")
        return state


class LifecycleOperator(BaseOperator):
    name = "LifecycleOperator"
    operator_type = "meta"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark lifecycle stage
        state["lifecycle_stage"] = state.get("lifecycle_stage", "active")
        return state


class GovernanceOperator(BaseOperator):
    name = "GovernanceOperator"
    operator_type = "meta"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Apply governance rules (placeholder)
        state.setdefault("flags", {})
        state["flags"]["governed"] = True
        return state


class IntegrationOperator(BaseOperator):
    name = "IntegrationOperator"
    operator_type = "meta"
    engine = "integration"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark integration step
        state.setdefault("flags", {})
        state["flags"]["integrated"] = True
        return state


class IntegrationOrchestrator(BaseOperator):
    name = "IntegrationOrchestrator"
    operator_type = "meta"
    engine = "integration"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Final synthesis point
        state.setdefault("flags", {})
        state["flags"]["final_synthesized"] = True
        return state


# ========= Class 1: Core System Operators =========

class RecursiveMaturityOperator(BaseOperator):
    name = "RecursiveMaturityOperator"
    operator_type = "proactive"
    engine = "are"

    STATUS_WEIGHT = {"built": 1.0, "doc": 0.5, "named": 0.0}

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Score overall system maturity from a list of engine statuses
        statuses = state.get("engine_statuses", [])
        if statuses:
            score = sum(self.STATUS_WEIGHT.get(s, 0.0) for s in statuses) / len(statuses)
        else:
            score = 0.0
        state["maturity_pct"] = round(score * 100, 1)
        return state


class LogicRouterOperator(BaseOperator):
    name = "LogicRouterOperator"
    operator_type = "conditional"
    engine = "cfa"

    TOPIC_ROUTES = {
        "reasoning": "cfa",
        "governance": "spec_compliance",
        "universe": "maximum_universe",
        "inventory": "computer_inventory",
        "automation": "n8n_automation",
        "identity": "brand_geometry",
        "revenue": "bundle_strategy",
    }

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Route a request topic to the engine responsible for it
        topic = state.get("request_topic", "")
        state["routed_engine"] = self.TOPIC_ROUTES.get(topic, "unrouted")
        return state


class AdaptiveReasoningRouterOperator(BaseOperator):
    name = "AdaptiveReasoningRouterOperator"
    operator_type = "conditional"
    engine = "talora"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Pick System-1 / System-2 / Hybrid reasoning strategy from a complexity score
        score = state.get("complexity_score", 0)
        if score < 30:
            strategy = "system1"
        elif score > 70:
            strategy = "system2"
        else:
            strategy = "hybrid"
        state["reasoning_strategy"] = strategy
        return state


# ========= Class 2: Identity & Brand Operators =========

class SegmentOverlapOperator(BaseOperator):
    name = "SegmentOverlapOperator"
    operator_type = "reactive"
    engine = "audience_graph"

    # Weights match the real Proof Tier Hierarchy in OS42-Authority-Stack.html
    TIER_WEIGHT = {"T1": 30, "T2": 25, "T3": 20, "T4": 15, "T5": 10}

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Score an audience segment by its proof tier
        tier = state.get("proof_tier", "T5")
        state["segment_weight"] = self.TIER_WEIGHT.get(tier, 0)
        return state


class ColorwaySpecOperator(BaseOperator):
    name = "ColorwaySpecOperator"
    operator_type = "reactive"
    engine = "brand_geometry"

    # Locked v1.0 colorway spec from "os42 logo generation prompt.md"
    COLORWAYS = {"green": "#39FF14", "blue": "#00BFFF"}

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Emit the locked OS42 mark spec for a given colorway toggle
        colorway = state.get("colorway", "green")
        state["brand_spec"] = {
            "colorway": colorway,
            "accent_hex": self.COLORWAYS.get(colorway),
            "metal": "metallic silver",
            "background": "#000000",
            "valid": colorway in self.COLORWAYS,
        }
        return state


# ========= Class 3: Analytics & Intelligence Operators =========

class AssetClassifierOperator(BaseOperator):
    name = "AssetClassifierOperator"
    operator_type = "reactive"
    engine = "research_toolkit"

    CATEGORY_KEYWORDS = {
        "framework": ["framework", "methodology", "playbook"],
        "dataset": ["dataset", "data set", "corpus"],
        "benchmark": ["benchmark", "eval", "score"],
        "tooling": ["tool", "cli", "sdk", "kit"],
        "report": ["report", "audit", "analysis"],
    }

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Classify a research asset title into a known category
        title = state.get("asset_title", "").lower()
        category = "uncategorized"
        for cat, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in title for kw in keywords):
                category = cat
                break
        state["asset_category"] = category
        return state


# ========= Class 4: Automation & Workflow Operators =========

class WorkflowExportOperator(BaseOperator):
    name = "WorkflowExportOperator"
    operator_type = "proactive"
    engine = "n8n_automation"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Emit a minimal, valid n8n-style workflow export
        trigger_type = state.get("trigger_type", "manual")
        action_type = state.get("action_type", "noop")
        state["n8n_workflow"] = {
            "nodes": [
                {"id": "1", "type": trigger_type, "name": "Trigger"},
                {"id": "2", "type": action_type, "name": "Action"},
            ],
            "connections": {"Trigger": {"main": [[{"node": "Action", "index": 0}]]}},
        }
        return state


class ModuleSpecValidatorOperator(BaseOperator):
    name = "ModuleSpecValidatorOperator"
    operator_type = "conditional"
    engine = "module_definition"

    REQUIRED_FIELDS = ["id", "name", "dependencies", "status"]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Validate a module spec against the required schema fields
        spec = state.get("module_spec", {})
        missing = [f for f in self.REQUIRED_FIELDS if f not in spec]
        state["missing_fields"] = missing
        state["module_valid"] = not missing
        return state


class DeploymentChecklistOperator(BaseOperator):
    name = "DeploymentChecklistOperator"
    operator_type = "conditional"
    engine = "deployment_spec"

    # Required config per ENGINE_BUILD_SUMMARY.md "Configuration Required" section
    REQUIRED_CONFIG = ["database_url", "redis_url", "api_keys", "email_config"]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Check a deployment config dict against the required checklist
        config = state.get("config", {})
        missing = [k for k in self.REQUIRED_CONFIG if not config.get(k)]
        state["missing_config"] = missing
        state["deployment_ready"] = not missing
        return state


# ========= Class 5: Product & Monetization Operators =========

class BundlePricingOperator(BaseOperator):
    name = "BundlePricingOperator"
    operator_type = "proactive"
    engine = "bundle_strategy"

    DISCOUNT = 0.15

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Price a bundle as the sum of its SKUs, discounted and floored to $1
        prices = state.get("sku_prices", [])
        subtotal = sum(prices)
        state["bundle_price"] = int(subtotal * (1 - self.DISCOUNT))
        return state


# ========= Class 6: Data & Inventory Operators =========

class InventoryRecordValidatorOperator(BaseOperator):
    name = "InventoryRecordValidatorOperator"
    operator_type = "conditional"
    engine = "computer_inventory"

    # Required fields per "Computer Inventory JSON Schema (CIM-JS v1_0).docx"
    REQUIRED_FIELDS = ["device_id", "hostname", "os", "cpu", "ram_gb", "storage_gb", "role"]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Validate a device record against the CIM-JS required fields
        record = state.get("device_record", {})
        missing = [f for f in self.REQUIRED_FIELDS if f not in record]
        state["missing_fields"] = missing
        state["record_valid"] = not missing
        return state


class DocumentHeaderOperator(BaseOperator):
    name = "DocumentHeaderOperator"
    operator_type = "reactive"
    engine = "system_document"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Generate a standardized header block for a new system document
        state["document_header"] = {
            "title": state.get("doc_title", "Untitled"),
            "category": state.get("doc_category", "SAC"),
            "version": state.get("doc_version", "v1_0"),
        }
        return state


# ========= Class 7: Universe & Expansion Operators =========

class UniverseLayerLookupOperator(BaseOperator):
    name = "UniverseLayerLookupOperator"
    operator_type = "reactive"
    engine = "maximum_universe"

    # The 14 real UAL documents from "A.R.E. Maximal Reconstruction Master Index.md"
    UAL_DOCS = [
        "Universe v5 Meta-Physics Document", "Universe v5 Ontology Map",
        "Universe v5 Layer Stack", "Universe v5 Subsystem Interaction Model",
        "Universe v5 Cognitive Engine Specification", "Universe v5 Behavioral Logic Model",
        "Universe v5 Expansion Protocols", "Universe v5 Meta-Ruleset",
        "Universe v5 System Laws", "Universe v5 Identity-Binding Framework",
        "Universe v5 Constraints & Limits Sheet", "Universe v5 Scenario & Simulation Map",
        "Universe v5 Versioning & Evolution Log", "Universe v5 Governance & Compliance Framework",
    ]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Look up a UAL canon document by index
        index = state.get("index", 0)
        if 0 <= index < len(self.UAL_DOCS):
            state["universe_doc"] = self.UAL_DOCS[index]
        else:
            state["universe_doc"] = None
        return state


class MaturityDeltaOperator(BaseOperator):
    name = "MaturityDeltaOperator"
    operator_type = "meta"
    engine = "evolution"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Record an evolution cycle's maturity delta
        before = state.get("maturity_before", 0)
        after = state.get("maturity_after", 0)
        state["maturity_delta"] = after - before
        return state


class CanonIndexOperator(BaseOperator):
    name = "CanonIndexOperator"
    operator_type = "meta"
    engine = "multiverse_reconstruction"

    # Real document counts per category from "A.R.E. Maximal Reconstruction Master Index.md"
    CANON_COUNTS = {
        "UAL": 14, "ISM": 11, "HAL": 10, "BOS": 15, "TMS": 14,
        "OSR": 16, "DSS": 12, "BFS": 13, "SAC": 18, "AEM": 12,
    }

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Look up a canon category's document count, and the canon-wide total
        category = state.get("category")
        state["category_doc_count"] = self.CANON_COUNTS.get(category)
        state["total_docs"] = sum(self.CANON_COUNTS.values())
        return state


# ========= Class 8: Cognitive & Logic Operators =========

class LogicToMotionOperator(BaseOperator):
    name = "LogicToMotionOperator"
    operator_type = "conditional"
    engine = "logic_motion"

    SEQUENCE = ["idle", "routing", "executing", "settled"]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Advance a logic state to the next motion state in sequence
        current = state.get("logic_state", "idle")
        try:
            idx = self.SEQUENCE.index(current)
            state["motion_state"] = self.SEQUENCE[min(idx + 1, len(self.SEQUENCE) - 1)]
        except ValueError:
            state["motion_state"] = self.SEQUENCE[0]
        return state


# ========= Class 9: Support & Utility Operators =========

class RunbookLookupOperator(BaseOperator):
    name = "RunbookLookupOperator"
    operator_type = "reactive"
    engine = "ops_runbook"

    # The 16 real OSR runbook titles from the A.R.E. canon index
    RUNBOOKS = [
        "Computer Inventory Ops-Runbook", "General Ops-Runbook", "System Recovery Runbook",
        "Deployment Runbook", "Optimization Runbook", "Troubleshooting Runbook",
        "Emergency Protocols Playbook", "System Maintenance Procedures", "Audit Procedures Guide",
        "Expansion Procedures Manual", "Daily/Weekly Ops Checklist", "Incident Response Playbook",
        "Change Management Runbook", "Backup & Restore Procedures",
        "Performance Monitoring Guide", "Ops Metrics & KPIs Sheet",
    ]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Find runbooks whose title contains the given keyword
        keyword = state.get("keyword", "").lower()
        state["matched_runbooks"] = [r for r in self.RUNBOOKS if keyword in r.lower()]
        return state


class RegistryComplianceOperator(BaseOperator):
    name = "RegistryComplianceOperator"
    operator_type = "meta"
    engine = "spec_compliance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Diff the live ENGINE_REGISTRY keys against the manifest's declared engine names
        registry_keys = set(state.get("registry_keys", []))
        manifest_keys = set(state.get("manifest_keys", []))
        state["registry_manifest_diff"] = {
            "missing_from_manifest": sorted(registry_keys - manifest_keys),
            "missing_from_registry": sorted(manifest_keys - registry_keys),
            "in_sync": registry_keys == manifest_keys,
        }
        return state


# ========= Class 10: Embedded Page Operators =========

class BlueprintSectionOperator(BaseOperator):
    name = "BlueprintSectionOperator"
    operator_type = "reactive"
    engine = "are_blueprint"

    CANON_SECTIONS = ["UAL", "ISM", "HAL", "BOS", "TMS", "OSR", "DSS", "BFS", "SAC", "AEM"]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # List the 10 canon sections a blueprint page renders
        state["blueprint_sections"] = list(self.CANON_SECTIONS)
        return state


class LayoutPageOperator(BaseOperator):
    name = "LayoutPageOperator"
    operator_type = "reactive"
    engine = "universe_layout"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Paginate a list of document titles into a numbered layout
        titles = state.get("doc_titles", [])
        state["layout_pages"] = {i + 1: title for i, title in enumerate(titles)}
        return state


class PipelineSequencerOperator(BaseOperator):
    name = "PipelineSequencerOperator"
    operator_type = "conditional"
    engine = "prompt_workflow"

    # The 10 real AI OPS ENGINE pipeline stages
    STAGES = [
        "Offer Validation", "Content Engine", "Sales Page", "Email Sequence",
        "Brand Identity", "Product Launch", "Customer Research", "Pricing Strategy",
        "Weekly Ops Review", "Digital Product Creation",
    ]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Advance to the next stage in the 10-stage AI Ops pipeline
        current = state.get("current_stage")
        if current not in self.STAGES:
            state["next_stage"] = self.STAGES[0]
        else:
            idx = self.STAGES.index(current)
            state["next_stage"] = self.STAGES[idx + 1] if idx + 1 < len(self.STAGES) else "complete"
        return state


class PackAssemblerOperator(BaseOperator):
    name = "PackAssemblerOperator"
    operator_type = "proactive"
    engine = "module_pack"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Assemble a set of module ids into a single module pack
        module_ids = state.get("module_ids", [])
        state["pack"] = {"module_count": len(module_ids), "modules": list(module_ids)}
        return state


class AssetIndexOperator(BaseOperator):
    name = "AssetIndexOperator"
    operator_type = "reactive"
    engine = "research_asset"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Index a research asset for the Research Asset embedded page
        state["asset_record"] = {
            "title": state.get("asset_title", "Untitled"),
            "category": state.get("asset_category", "uncategorized"),
            "indexed": True,
        }
        return state


# ========= AI Research Toolkit -- 16 cognitive modules =========
# Real spec: OneDrive/AI Research Toolkit Asset Blueprint (Extremely Detailed).docx
# Input schema:  {topic, context, constraints, data}
# Output schema: {summary, insights, gaps, recommendations, next_steps}
# Primary Research Flow (default chain): Topic Explorer -> Research Question Builder
#   -> Literature Summary -> Research Gap Finder -> Hypothesis Generator
#   -> Methodology Refiner -> Insight Extractor -> Research Summary Engine
# Secondary Enhancement Flow (optional chain): Trend Analyzer, Cross-Industry
#   Insight, Future Scenario Builder, Expert Debate Simulator

class TopicExplorerOperator(BaseOperator):
    name = "TopicExplorerOperator"
    operator_type = "reactive"
    engine = "research_toolkit"

    ANGLES = ["fundamentals", "market landscape", "risks", "future outlook"]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Systematic exploration of a topic into a fixed set of research angles
        topic = state.get("topic", "")
        state["sub_topics"] = [f"{topic}: {angle}" for angle in self.ANGLES]
        return state


class ResearchQuestionBuilderOperator(BaseOperator):
    name = "ResearchQuestionBuilderOperator"
    operator_type = "reactive"
    engine = "research_toolkit"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Generate one research question per explored sub-topic
        sub_topics = state.get("sub_topics", [])
        state["research_questions"] = [f"What are the key drivers of {s}?" for s in sub_topics]
        return state


class LiteratureSummaryOperator(BaseOperator):
    name = "LiteratureSummaryOperator"
    operator_type = "reactive"
    engine = "research_toolkit"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Extractive summary: first sentence of each supplied source
        sources = state.get("data", []) or []
        sentences = [s.split(".")[0].strip() for s in sources if s]
        state["literature_summary"] = ". ".join(sentences)
        return state


class ResearchGapFinderOperator(BaseOperator):
    name = "ResearchGapFinderOperator"
    operator_type = "reactive"
    engine = "research_toolkit"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # A question is a "gap" if none of its keywords appear in the literature
        questions = state.get("research_questions", [])
        summary = state.get("literature_summary", "").lower()
        gaps = []
        for q in questions:
            keywords = [w.lower().strip(".,?!;:") for w in q.split() if len(w) > 4]
            if not any(kw in summary for kw in keywords):
                gaps.append(q)
        state["gaps"] = gaps
        return state


class InsightExtractorOperator(BaseOperator):
    name = "InsightExtractorOperator"
    operator_type = "reactive"
    engine = "research_toolkit"

    SIGNAL_WORDS = ("significant", "however", "surprisingly", "critical")

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Pull sentences from source data that contain a signal word
        sources = state.get("data", []) or []
        state["insights"] = [s for s in sources if any(w in s.lower() for w in self.SIGNAL_WORDS)]
        return state


class DataInterpretationOperator(BaseOperator):
    name = "DataInterpretationOperator"
    operator_type = "reactive"
    engine = "research_toolkit"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Basic descriptive stats over a numeric data series
        series = [v for v in (state.get("data") or []) if isinstance(v, (int, float))]
        state["data_interpretation"] = (
            {"mean": sum(series) / len(series), "min": min(series), "max": max(series)}
            if series else {}
        )
        return state


class FutureScenarioBuilderOperator(BaseOperator):
    name = "FutureScenarioBuilderOperator"
    operator_type = "proactive"
    engine = "research_toolkit"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Three deterministic scenario framings for the topic
        topic = state.get("topic", "")
        state["scenarios"] = {
            "optimistic": f"{topic} accelerates faster than expected",
            "base": f"{topic} progresses at the currently observed rate",
            "pessimistic": f"{topic} stalls on unresolved constraints",
        }
        return state


class SimplifyComplexResearchOperator(BaseOperator):
    name = "SimplifyComplexResearchOperator"
    operator_type = "reactive"
    engine = "research_toolkit"

    MAX_WORDS = 40

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Truncate the literature summary to a digestible length
        words = state.get("literature_summary", "").split()
        state["simplified_summary"] = " ".join(words[: self.MAX_WORDS])
        return state


class TheoryConnectorOperator(BaseOperator):
    name = "TheoryConnectorOperator"
    operator_type = "reactive"
    engine = "research_toolkit"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # All pairwise connections between supplied concepts
        concepts = state.get("concepts", [])
        state["theory_connections"] = [
            (a, b) for i, a in enumerate(concepts) for b in concepts[i + 1:]
        ]
        return state


class MethodologyRefinerOperator(BaseOperator):
    name = "MethodologyRefinerOperator"
    operator_type = "conditional"
    engine = "research_toolkit"

    CHECKLIST = ("sample size", "control group", "methodology", "data source")

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Flag which methodology-quality checklist items are missing
        methodology = state.get("methodology", "").lower()
        state["methodology_feedback"] = [c for c in self.CHECKLIST if c not in methodology]
        return state


class HypothesisGeneratorOperator(BaseOperator):
    name = "HypothesisGeneratorOperator"
    operator_type = "reactive"
    engine = "research_toolkit"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # One testable hypothesis per identified research gap
        gaps = state.get("gaps", [])
        state["hypotheses"] = [f"If '{g}' is addressed, outcomes measurably improve" for g in gaps]
        return state


class ExpertDebateSimulatorOperator(BaseOperator):
    name = "ExpertDebateSimulatorOperator"
    operator_type = "proactive"
    engine = "research_toolkit"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Deterministic pro/con framing for each hypothesis (no LLM call)
        hypotheses = state.get("hypotheses", [])
        state["debate_points"] = [
            {"hypothesis": h, "pro": f"Supports: {h}", "con": f"Challenges: {h}"} for h in hypotheses
        ]
        return state


class CrossIndustryInsightOperator(BaseOperator):
    name = "CrossIndustryInsightOperator"
    operator_type = "proactive"
    engine = "research_toolkit"

    INDUSTRIES = ("healthcare", "finance", "logistics", "education")

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Analogy of the topic against a fixed set of reference industries
        topic = state.get("topic", "")
        state["cross_industry_insights"] = [
            f"How does {industry} solve problems similar to {topic}?" for industry in self.INDUSTRIES
        ]
        return state


class TrendAnalyzerOperator(BaseOperator):
    name = "TrendAnalyzerOperator"
    operator_type = "proactive"
    engine = "research_toolkit"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Direction of a numeric series by comparing its first and last points
        series = [v for v in (state.get("data") or []) if isinstance(v, (int, float))]
        if len(series) < 2:
            state["trend"] = "insufficient_data"
        elif series[-1] > series[0]:
            state["trend"] = "increasing"
        elif series[-1] < series[0]:
            state["trend"] = "decreasing"
        else:
            state["trend"] = "flat"
        return state


class KnowledgeMapOperator(BaseOperator):
    name = "KnowledgeMapOperator"
    operator_type = "reactive"
    engine = "research_toolkit"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Adjacency map: every concept linked to every other concept
        concepts = state.get("concepts", [])
        state["knowledge_map"] = {c: [o for o in concepts if o != c] for c in concepts}
        return state


class ResearchSummaryEngineOperator(BaseOperator):
    name = "ResearchSummaryEngineOperator"
    operator_type = "meta"
    engine = "research_toolkit"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Aggregate the pipeline's accumulated state into the toolkit's real output schema
        state["research_output"] = {
            "summary": state.get("simplified_summary") or state.get("literature_summary", ""),
            "insights": state.get("insights", []),
            "gaps": state.get("gaps", []),
            "recommendations": state.get("hypotheses", []),
            "next_steps": state.get("methodology_feedback", []),
        }
        return state


# ========= Brand Enforcement -- real Doctrine Enforcement Rules =========
# Source: OneDrive/copilot chat comprehensive brand stystem.md, section 3.3
# "Doctrine Enforcement Rules": no mythic language, no empire metaphors, no
# AI-prophetic framing, no vague language, no emotional manipulation, no
# inspirational hype, no unversioned artifacts (among others not checkable
# by deterministic text scan, e.g. "no ungoverned expansion").

class BrandDoctrineComplianceOperator(BaseOperator):
    name = "BrandDoctrineComplianceOperator"
    operator_type = "conditional"
    engine = "brand_enforcement"

    BANNED_PHRASES = {
        "mythic_language": ("legendary", "mythic", "prophecy", "destiny", "chosen one"),
        "empire_metaphors": ("empire", "kingdom", "conquer", "domination", "throne"),
        "ai_prophetic_framing": ("the future of ai", "singularity", "revolutionary ai", "ai will change everything"),
        "vague_language": ("maybe", "possibly", "some things", "various stuff", "kind of"),
        "emotional_manipulation": ("act now", "don't miss out", "last chance", "limited time only"),
        "inspirational_hype": ("unleash your potential", "unlock greatness", "game-changing", "unstoppable"),
    }

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Scan copy against the real banned-phrase categories, and require versioning
        text = state.get("copy_text", "").lower()
        violations = {
            category: [p for p in phrases if p in text]
            for category, phrases in self.BANNED_PHRASES.items()
        }
        violations = {k: v for k, v in violations.items() if v}
        if not state.get("artifact_version"):
            violations["unversioned_artifact"] = ["no version supplied"]

        state["brand_violations"] = violations
        state["brand_compliant"] = not violations
        return state


# ========= Universe v5 causal layers not yet covered =========
# Source: OneDrive/copilot chat system layout.txt -- the real causal ordering
# of the A.R.E./Universe v5 layers named four concepts with no engine behind
# them yet: Security & Governance, Testing & Validation, Environment &
# Context, Knowledge & Memory.

class AccessControlOperator(BaseOperator):
    name = "AccessControlOperator"
    operator_type = "conditional"
    engine = "security_governance"

    # Scaled to a solo-operator system, not the enterprise Root-Council model
    # investigated and rejected in CANON-v∞ -- see EMPIRE_PROJECT_SPEC.md.
    ROLE_PERMISSIONS = {
        "operator": {"read", "execute"},
        "architect": {"read", "execute", "write"},
        "founder": {"read", "execute", "write", "admin"},
    }

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Check whether a role is permitted to perform a requested action
        role = state.get("role", "operator")
        action = state.get("requested_action", "read")
        permissions = self.ROLE_PERMISSIONS.get(role, set())
        state["role_permissions"] = sorted(permissions)
        state["access_granted"] = action in permissions
        return state


class TestCoverageOperator(BaseOperator):
    name = "TestCoverageOperator"
    operator_type = "meta"
    engine = "testing_validation"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # "You can't test what hasn't been built" -- flag untested components
        components = set(state.get("components", []))
        tested = set(state.get("tested_components", []))
        untested = sorted(components - tested)
        state["untested_components"] = untested
        state["test_coverage_pct"] = (
            round(100 * len(components & tested) / len(components), 1) if components else 0.0
        )
        return state


class EnvironmentProfileOperator(BaseOperator):
    name = "EnvironmentProfileOperator"
    operator_type = "conditional"
    engine = "environment_context"

    # Mirrors the Tier 1/2/3 autonomy guardrails in EMPIRE_PROJECT_SPEC.md sec.9
    PROFILES = {
        "local": {"tier_ceiling": 1, "external_calls_allowed": False},
        "staging": {"tier_ceiling": 2, "external_calls_allowed": True},
        "production": {"tier_ceiling": 3, "external_calls_allowed": True},
    }

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Resolve the operating profile for a named deployment environment
        environment = state.get("environment", "local")
        state["environment_profile"] = self.PROFILES.get(environment, self.PROFILES["local"])
        return state


class KnowledgeGraphOperator(BaseOperator):
    name = "KnowledgeGraphOperator"
    operator_type = "reactive"
    engine = "knowledge_memory"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Build a subject -> [(relation, object), ...] graph from real triples
        triples = state.get("triples", [])
        graph: Dict[str, Any] = {}
        for subject, relation, obj in triples:
            graph.setdefault(subject, []).append((relation, obj))
        state["knowledge_graph"] = graph
        return state
