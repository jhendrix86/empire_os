import json
import re
from pathlib import Path
from typing import Any, Dict
from .operator_base import BaseOperator
from .llm_client import call_llm


# ========= Reactive Operators =========

class InputInterpreter(BaseOperator):
    name = "InputInterpreter"
    operator_type = "reactive"
    engine = "input"

    FILLER_WORDS = {"um", "uh", "like", "basically", "actually", "you know"}

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Parse raw input into a structured form the rest of the chain can use
        raw = state.get("raw_input", "") or ""
        tokens = raw.split()
        state["parsed_input"] = {
            "text": raw.strip(),
            "tokens": tokens,
            "word_count": len(tokens),
            "is_question": raw.strip().endswith("?"),
            "filler_word_count": sum(1 for t in tokens if t.lower().strip(",.!?") in self.FILLER_WORDS),
        }
        return state


class ContextStabilizer(BaseOperator):
    name = "ContextStabilizer"
    operator_type = "reactive"
    engine = "context"

    OVERLAP_THRESHOLD = 0.5

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Compare current context against the previous snapshot to detect drift
        context = state.get("context", {}) or {}
        previous = state.get("previous_context")

        if previous:
            shared = set(context.keys()) & set(previous.keys())
            union = set(context.keys()) | set(previous.keys())
            overlap_ratio = (len(shared) / len(union)) if union else 1.0
            stable = overlap_ratio >= self.OVERLAP_THRESHOLD
            # Preserve prior keys the new context dropped, when still stable
            if stable:
                context = {**previous, **context}
        else:
            overlap_ratio = 1.0
            stable = True

        state["context"] = context
        state["context_stability"] = {"stable": stable, "overlap_ratio": round(overlap_ratio, 2)}
        return state


class ClarificationOperator(BaseOperator):
    name = "ClarificationOperator"
    operator_type = "reactive"
    engine = "input"

    VAGUE_WORDS = {"this", "that", "it", "something", "stuff", "thing"}

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Mark that clarification is needed, from an explicit flag or heuristics
        state.setdefault("flags", {})
        if "ambiguity" in state:
            needs_clarification = bool(state["ambiguity"])
        else:
            parsed = state.get("parsed_input", {})
            tokens = [t.lower().strip(",.!?") for t in parsed.get("tokens", [])]
            too_short = 0 < parsed.get("word_count", 0) <= 2
            vague = any(t in self.VAGUE_WORDS for t in tokens)
            needs_clarification = too_short or vague
        state["flags"]["needs_clarification"] = needs_clarification
        return state


class ConstraintEnforcer(BaseOperator):
    name = "ConstraintEnforcer"
    operator_type = "reactive"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Enforce constraints stored in state["constraints"] against the output
        constraints = state.get("constraints", {}) or {}
        text = self._output_text(state)
        violations = []

        max_length = constraints.get("max_length")
        if max_length is not None and len(text) > max_length:
            violations.append(f"output exceeds max_length ({len(text)} > {max_length})")

        for word in constraints.get("forbidden_words", []):
            if word and word.lower() in text.lower():
                violations.append(f"forbidden word present: {word}")

        state["constraint_violations"] = violations
        state.setdefault("flags", {})
        state["flags"]["constraints_enforced"] = len(violations) == 0
        return state

    @staticmethod
    def _output_text(state: Dict[str, Any]) -> str:
        output = state.get("output")
        if isinstance(output, str):
            return output
        if output is not None:
            return json.dumps(output, default=str)
        return state.get("parsed_input", {}).get("text", "") or state.get("raw_input", "") or ""


class SafetyBoundaryOperator(BaseOperator):
    name = "SafetyBoundaryOperator"
    operator_type = "reactive"
    engine = "governance"

    UNSAFE_PATTERNS = [
        "ignore previous instructions",
        "ignore all previous",
        "disregard the system prompt",
        "<script",
        "drop table",
    ]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Scan the raw/parsed text for known-unsafe patterns, in addition to any explicit flag
        text = (state.get("parsed_input", {}).get("text") or state.get("raw_input", "") or "").lower()
        detected = [p for p in self.UNSAFE_PATTERNS if p in text]
        explicit_flag = bool(state.get("unsafe_pattern", False))

        state["unsafe_patterns_detected"] = detected
        state.setdefault("flags", {})
        state["flags"]["safety_ok"] = not (detected or explicit_flag)
        return state


class PrecisionRefiner(BaseOperator):
    name = "PrecisionRefiner"
    operator_type = "reactive"
    engine = "input"

    FILLER_PATTERN = re.compile(r"\b(um|uh|like|you know|basically|actually)\b[, ]*", re.IGNORECASE)

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Strip filler words and collapse whitespace to sharpen parsed input
        parsed = state.get("parsed_input", {}) or {}
        original = parsed.get("text", "")
        cleaned = self.FILLER_PATTERN.sub("", original)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        parsed["refined_text"] = cleaned
        parsed["refined"] = cleaned != original
        state["parsed_input"] = parsed
        return state


class StructuralFormatter(BaseOperator):
    name = "StructuralFormatter"
    operator_type = "reactive"
    engine = "execution"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Normalize output into a consistent envelope regardless of its original shape
        output = state.get("output")
        if isinstance(output, dict):
            data_type = "object"
        elif isinstance(output, list):
            data_type = "array"
        elif output is None:
            data_type = "empty"
        else:
            data_type = "scalar"

        state["output"] = {"structured": True, "type": data_type, "data": output}
        return state


class ExecutionRouter(BaseOperator):
    name = "ExecutionRouter"
    operator_type = "reactive"
    engine = "execution"

    ACTION_HANDLERS = {
        "generate": "generation_handler",
        "fetch": "retrieval_handler",
        "validate": "validation_handler",
        "notify": "notification_handler",
    }

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Decide which execution handler to use for the requested action
        action = state.get("desired_action", "default")
        state.setdefault("routing", {})
        state["routing"]["target"] = action
        state["routing"]["handler"] = self.ACTION_HANDLERS.get(action, "default_handler")
        return state


class ErrorRecoveryOperator(BaseOperator):
    name = "ErrorRecoveryOperator"
    operator_type = "reactive"
    engine = "execution"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Classify any recorded error and decide a concrete recovery action
        error = state.get("error")
        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 3)

        state.setdefault("flags", {})
        if not error:
            state["flags"]["recovered"] = True
            state["recovery_action"] = "none_needed"
            return state

        error_text = str(error).lower()
        if "timeout" in error_text:
            error_type = "timeout"
        elif "valid" in error_text:
            error_type = "validation"
        else:
            error_type = "unknown"

        if retry_count < max_retries:
            recovery_action = "retry"
            recovered = True
        else:
            recovery_action = "abort"
            recovered = False

        state["error_type"] = error_type
        state["recovery_action"] = recovery_action
        state["flags"]["recovered"] = recovered
        return state


class MemoryAlignmentOperator(BaseOperator):
    name = "MemoryAlignmentOperator"
    operator_type = "reactive"
    engine = "memory"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Align current context with stored memory, flagging real conflicts
        memory = state.get("memory", {}) or {}
        context = state.get("context", {}) or {}

        conflicts = [k for k in memory if k in context and memory[k] != context[k]]
        merged = {**memory, **context}

        state["context"] = merged
        state["memory_conflicts"] = conflicts
        state.setdefault("flags", {})
        state["flags"]["memory_aligned"] = len(conflicts) == 0
        return state


# ========= Proactive Operators =========

class PredictivePlanner(BaseOperator):
    name = "PredictivePlanner"
    operator_type = "proactive"
    engine = "optimization"

    GOAL_TEMPLATES = {
        "launch": ["research", "design", "build", "test", "ship"],
        "fix": ["reproduce", "diagnose", "patch", "verify"],
        "research": ["gather_sources", "analyze", "summarize"],
    }
    DEFAULT_PLAN = ["research", "execute", "verify"]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Build a concrete step plan for the stated goal
        goal = state.get("goal", "")
        steps = self.GOAL_TEMPLATES.get(goal, self.DEFAULT_PLAN)
        state["plan"] = {"goal": goal or "unspecified", "steps": list(steps)}
        return state


class OpportunityScanner(BaseOperator):
    name = "OpportunityScanner"
    operator_type = "proactive"
    engine = "optimization"

    RULES = [
        ("conversion_rate", lambda v: v < 2.0, "conversion_rate below 2% - review the funnel"),
        ("engagement_rate", lambda v: v > 80.0, "engagement_rate above 80% - double down on this channel"),
        ("error_rate", lambda v: v > 5.0, "error_rate above 5% - investigate failures"),
        ("churn_rate", lambda v: v > 10.0, "churn_rate above 10% - prioritize retention"),
    ]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Scan metrics against known thresholds for actionable opportunities
        metrics = state.get("metrics", {}) or {}
        opportunities = [
            message
            for metric_key, predicate, message in self.RULES
            if metric_key in metrics and predicate(metrics[metric_key])
        ]

        state["opportunities"] = opportunities
        state.setdefault("flags", {})
        state["flags"]["opportunities_found"] = len(opportunities) > 0
        return state


class OptimizationOperator(BaseOperator):
    name = "OptimizationOperator"
    operator_type = "proactive"
    engine = "optimization"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Select the best-scoring candidate, if any were provided
        candidates = state.get("candidates", []) or []
        best = None
        if candidates:
            scored = [c if isinstance(c, dict) else {"value": c, "score": c} for c in candidates]
            best = max(scored, key=lambda c: c.get("score", 0))

        state["best_candidate"] = best
        state.setdefault("flags", {})
        state["flags"]["optimized"] = best is not None
        return state


class AuditCycleOperator(BaseOperator):
    name = "AuditCycleOperator"
    operator_type = "proactive"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Record a real audit entry: a timestamped snapshot of the current flags
        state.setdefault("audit_log", [])
        state["audit_log"].append({
            "event": "audit_cycle",
            "flags_snapshot": dict(state.get("flags", {})),
        })
        return state


class DriftMonitor(BaseOperator):
    name = "DriftMonitor"
    operator_type = "proactive"
    engine = "governance"

    DRIFT_THRESHOLD_PCT = 20.0

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Compare current metrics against a baseline to detect real deviation
        baseline = state.get("baseline_metrics", {}) or {}
        current = state.get("current_metrics", {}) or {}

        deviations = {}
        for key, baseline_value in baseline.items():
            if key not in current or not baseline_value:
                continue
            pct_change = abs(current[key] - baseline_value) / abs(baseline_value) * 100
            if pct_change >= self.DRIFT_THRESHOLD_PCT:
                deviations[key] = round(pct_change, 1)

        state["drift_deviations"] = deviations
        state.setdefault("flags", {})
        state["flags"]["drift_detected"] = len(deviations) > 0
        return state


class LoadBalancer(BaseOperator):
    name = "LoadBalancer"
    operator_type = "proactive"
    engine = "optimization"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Assign work to whichever worker currently has the lowest load
        worker_loads = state.get("worker_loads", {}) or {}
        assigned = min(worker_loads, key=worker_loads.get) if worker_loads else None

        state["assigned_worker"] = assigned
        state.setdefault("flags", {})
        state["flags"]["load_balanced"] = assigned is not None
        return state


class RedundancyOperator(BaseOperator):
    name = "RedundancyOperator"
    operator_type = "proactive"
    engine = "optimization"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Deduplicate items, tracking how much redundancy was actually removed
        items = state.get("items", []) or []
        seen = []
        for item in items:
            key = json.dumps(item, sort_keys=True, default=str) if isinstance(item, (dict, list)) else item
            if key not in seen:
                seen.append(key)

        state["deduplicated_count"] = len(items) - len(seen)
        state.setdefault("flags", {})
        state["flags"]["redundancy_handled"] = True
        return state


class ConsistencyOperator(BaseOperator):
    name = "ConsistencyOperator"
    operator_type = "proactive"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Flag a structural mismatch between this output and the previous pass
        output = state.get("output")
        previous_output = state.get("previous_output")

        consistent = previous_output is None or type(output) is type(previous_output)

        state.setdefault("flags", {})
        state["flags"]["consistent"] = consistent
        return state


class CompressionOperator(BaseOperator):
    name = "CompressionOperator"
    operator_type = "proactive"
    engine = "optimization"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Actually truncate long text output down to a target length
        output = state.get("output")
        target_length = state.get("compression_target_length", 280)

        if isinstance(output, str) and len(output) > target_length:
            words = output[: target_length].rsplit(" ", 1)[0]
            state["output"] = words + "..."
            compressed = True
        else:
            compressed = False

        state.setdefault("flags", {})
        state["flags"]["compressed"] = compressed
        return state


class ExpansionOperator(BaseOperator):
    name = "ExpansionOperator"
    operator_type = "proactive"
    engine = "optimization"

    EXPECTED_SECTIONS = ["summary", "details", "next_steps"]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Fill in any recommended sections missing from a structured output
        output = state.get("output")
        expanded = False
        if isinstance(output, dict):
            for section in self.EXPECTED_SECTIONS:
                if section not in output:
                    output[section] = None
                    expanded = True
            state["output"] = output

        state.setdefault("flags", {})
        state["flags"]["expanded"] = expanded
        return state


# ========= Conditional Operators =========

class DecisionTreeOperator(BaseOperator):
    name = "DecisionTreeOperator"
    operator_type = "conditional"
    engine = "reasoning"

    # (priority, risk_level) -> branch
    TREE = {
        ("critical", "high"): "escalate_immediately",
        ("critical", "low"): "fast_track",
        ("normal", "high"): "review_required",
        ("normal", "low"): "standard_path",
    }

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Choose a concrete branch from priority + risk_level, not priority alone
        priority = state.get("priority", "normal")
        risk_level = state.get("risk_level", "low")
        branch = self.TREE.get((priority, risk_level), "standard_path")

        state.setdefault("routing", {})
        state["routing"]["branch"] = branch
        return state


class PriorityResolver(BaseOperator):
    name = "PriorityResolver"
    operator_type = "conditional"
    engine = "reasoning"

    PRECEDENCE = ["critical", "high", "normal", "low"]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Resolve competing priority candidates by real precedence, not just pass-through
        candidates = state.get("priority_candidates")
        if candidates:
            resolved = min(
                candidates,
                key=lambda p: self.PRECEDENCE.index(p) if p in self.PRECEDENCE else len(self.PRECEDENCE),
            )
        else:
            resolved = state.get("priority", "normal")

        state["priority"] = resolved
        return state


class ResourceAllocator(BaseOperator):
    name = "ResourceAllocator"
    operator_type = "conditional"
    engine = "execution"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Check requested resources against what's actually available
        requested = state.get("requested_resources", {}) or {}
        available = state.get("available_resources", {}) or {}

        shortfall = {
            key: amount - available.get(key, 0)
            for key, amount in requested.items()
            if amount > available.get(key, 0)
        }

        state["resources"] = {"allocated": len(shortfall) == 0, "shortfall": shortfall}
        return state


class ModeSwitchOperator(BaseOperator):
    name = "ModeSwitchOperator"
    operator_type = "conditional"
    engine = "context"

    ALLOWED_MODES = {"default", "focus", "exploration", "safe_mode"}

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Only switch mode if the requested mode is actually valid
        desired_mode = state.get("desired_mode", "default")
        current_mode = state.get("mode", "default")

        if desired_mode in self.ALLOWED_MODES:
            state["mode"] = desired_mode
            state["invalid_mode_requested"] = False
        else:
            state["mode"] = current_mode
            state["invalid_mode_requested"] = desired_mode != "default"
        return state


class ContextRebuilder(BaseOperator):
    name = "ContextRebuilder"
    operator_type = "conditional"
    engine = "context"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Merge partial context fragments into a single rebuilt context
        fragments = state.get("context_fragments", []) or []
        rebuilt: Dict[str, Any] = dict(state.get("context", {}) or {})
        for fragment in fragments:
            if isinstance(fragment, dict):
                rebuilt.update(fragment)

        state["context"] = rebuilt
        return state


class MultiEngineCoordinator(BaseOperator):
    name = "MultiEngineCoordinator"
    operator_type = "conditional"
    engine = "integration"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Determine whether all engines this task needs are actually available
        required = state.get("required_engines", []) or []
        available = set(state.get("available_engines", []) or [])
        missing = [e for e in required if e not in available]

        state["missing_engines"] = missing
        state.setdefault("flags", {})
        state["flags"]["multi_engine"] = len(required) > 1
        state["flags"]["all_engines_available"] = len(missing) == 0
        return state


class DependencyChecker(BaseOperator):
    name = "DependencyChecker"
    operator_type = "conditional"
    engine = "execution"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Check that every declared dependency has actually completed
        dependencies = state.get("dependencies", []) or []
        completed = set(state.get("completed_ids", []) or [])
        unmet = [d for d in dependencies if d not in completed]

        state["unmet_dependencies"] = unmet
        state.setdefault("flags", {})
        state["flags"]["dependencies_ok"] = len(unmet) == 0
        return state


class ValidationOperator(BaseOperator):
    name = "ValidationOperator"
    operator_type = "conditional"
    engine = "execution"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Validate output against a simple required-fields schema, when one is given
        schema = state.get("validation_schema")
        output = state.get("output")

        if schema and isinstance(output, dict):
            required_fields = schema.get("required_fields", [])
            missing = [f for f in required_fields if f not in output]
        else:
            missing = []

        state["validation_errors"] = missing
        state.setdefault("flags", {})
        state["flags"]["validated"] = len(missing) == 0
        return state


class BoundaryExpander(BaseOperator):
    name = "BoundaryExpander"
    operator_type = "conditional"
    engine = "reasoning"

    RELATED_TOPICS = {
        "pricing": ["discounts", "packaging", "competitors"],
        "marketing": ["seo", "content", "advertising"],
        "security": ["compliance", "authentication", "encryption"],
    }

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Widen scope by adding topics related to what's already in it
        scope = list(state.get("scope", []) or [])
        added = []
        for topic in list(scope):
            for related in self.RELATED_TOPICS.get(topic, []):
                if related not in scope:
                    scope.append(related)
                    added.append(related)

        state["scope"] = scope
        state.setdefault("flags", {})
        state["flags"]["scope_expanded"] = len(added) > 0
        return state


class BoundaryCompressor(BaseOperator):
    name = "BoundaryCompressor"
    operator_type = "conditional"
    engine = "reasoning"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Narrow scope down to only the items matching the stated focus keywords
        scope = state.get("scope", []) or []
        focus_keywords = state.get("focus_keywords")

        if focus_keywords:
            narrowed = [s for s in scope if s in focus_keywords]
        else:
            narrowed = scope

        state.setdefault("flags", {})
        state["flags"]["scope_compressed"] = len(narrowed) < len(scope)
        state["scope"] = narrowed
        return state


# ========= Meta Operators =========

class MetaReasoningOperator(BaseOperator):
    name = "MetaReasoningOperator"
    operator_type = "meta"
    engine = "reasoning"

    CONFIDENCE_ESCALATION_THRESHOLD = 40

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Reflect on the chosen reasoning strategy and escalate it if confidence is low
        confidence = state.get("confidence", 100)
        strategy = state.get("reasoning_strategy", "system1")

        if confidence < self.CONFIDENCE_ESCALATION_THRESHOLD and strategy != "system2":
            state["reasoning_strategy"] = "system2"
            escalated = True
        else:
            escalated = False

        state.setdefault("flags", {})
        state["flags"]["meta_reasoned"] = True
        state["flags"]["strategy_escalated"] = escalated
        return state


class CouncilSynthesizer(BaseOperator):
    name = "CouncilSynthesizer"
    operator_type = "meta"
    engine = "integration"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Synthesize the highest-scored candidate output, if candidates were offered
        candidates = state.get("candidate_outputs", []) or []
        if candidates:
            best = max(candidates, key=lambda c: c.get("score", 0) if isinstance(c, dict) else 0)
            state["output"] = best.get("output") if isinstance(best, dict) else best
        else:
            state["output"] = state.get("output", {})
        return state


class OverrideArbiter(BaseOperator):
    name = "OverrideArbiter"
    operator_type = "meta"
    engine = "governance"

    ALLOWED_OVERRIDE_ROLES = {"admin", "owner", "governance_lead"}

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # An override needs both a request and a role actually permitted to make one
        requested = bool(state.get("override_request", False))
        role = state.get("requester_role")
        allowed = requested and role in self.ALLOWED_OVERRIDE_ROLES

        state.setdefault("flags", {})
        state["flags"]["override_allowed"] = allowed
        if requested and not allowed:
            state["override_denied_reason"] = "requester_role not permitted to override"
        return state


class EscalationOperator(BaseOperator):
    name = "EscalationOperator"
    operator_type = "meta"
    engine = "governance"

    SEVERITY_ESCALATION_THRESHOLD = 8

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Escalate on explicit high_risk OR a severity score past the threshold
        high_risk = bool(state.get("high_risk", False))
        severity = state.get("severity", 0)
        escalate = high_risk or severity >= self.SEVERITY_ESCALATION_THRESHOLD

        state.setdefault("flags", {})
        state["flags"]["escalated"] = escalate
        return state


class HarmonizationOperator(BaseOperator):
    name = "HarmonizationOperator"
    operator_type = "meta"
    engine = "integration"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Merge non-conflicting keys across candidate outputs; flag true conflicts
        conflicting = state.get("conflicting_outputs", []) or []
        merged: Dict[str, Any] = {}
        conflicts = []

        for candidate in conflicting:
            if not isinstance(candidate, dict):
                continue
            for key, value in candidate.items():
                if key in merged and merged[key] != value:
                    conflicts.append(key)
                else:
                    merged[key] = value

        if merged or conflicts:
            state["output"] = merged
        else:
            state["output"] = state.get("output", {})
        state["harmonization_conflicts"] = conflicts
        return state


class VersioningOperator(BaseOperator):
    name = "VersioningOperator"
    operator_type = "meta"
    engine = "governance"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Compute a real next semantic version from the change type
        previous_version = state.get("previous_version") or state.get("version", "v1.0.0")
        change_type = state.get("change_type", "patch")

        match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", previous_version)
        if match:
            major, minor, patch = (int(part) for part in match.groups())
            if change_type == "major":
                major, minor, patch = major + 1, 0, 0
            elif change_type == "minor":
                minor, patch = minor + 1, 0
            else:
                patch += 1
            state["version"] = f"v{major}.{minor}.{patch}"
        else:
            state["version"] = previous_version

        return state


class LifecycleOperator(BaseOperator):
    name = "LifecycleOperator"
    operator_type = "meta"
    engine = "governance"

    # (current_stage, event) -> next_stage
    TRANSITIONS = {
        ("draft", "submit"): "review",
        ("review", "approve"): "approved",
        ("review", "reject"): "draft",
        ("approved", "deploy"): "active",
        ("active", "retire"): "retired",
    }

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Advance lifecycle stage only along a valid, defined transition
        current_stage = state.get("lifecycle_stage", "draft")
        event = state.get("lifecycle_event")

        next_stage = self.TRANSITIONS.get((current_stage, event))
        if next_stage:
            state["lifecycle_stage"] = next_stage
            state["lifecycle_transition_valid"] = True
        else:
            state["lifecycle_stage"] = current_stage
            state["lifecycle_transition_valid"] = event is None
        return state


class GovernanceOperator(BaseOperator):
    name = "GovernanceOperator"
    operator_type = "meta"
    engine = "governance"

    RESTRICTED_ACTIONS = {"delete_data", "modify_permissions", "external_publish"}

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # An action only needs governance sign-off if it's restricted and unapproved
        action = state.get("action")
        approved = bool(state.get("approved", False))
        blocked = action in self.RESTRICTED_ACTIONS and not approved

        state.setdefault("flags", {})
        state["flags"]["governed"] = not blocked
        return state


class IntegrationOperator(BaseOperator):
    name = "IntegrationOperator"
    operator_type = "meta"
    engine = "integration"

    SUPPORTED_INTEGRATIONS = {"slack", "email", "webhook", "database"}

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Only mark integrated if the requested target is actually supported
        target = state.get("integration_target")
        supported = target in self.SUPPORTED_INTEGRATIONS

        state["integration_supported"] = supported
        state.setdefault("flags", {})
        state["flags"]["integrated"] = target is None or supported
        return state


class IntegrationOrchestrator(BaseOperator):
    name = "IntegrationOrchestrator"
    operator_type = "meta"
    engine = "integration"

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Final synthesis: roll up what actually happened during this run
        flags = state.get("flags", {}) or {}
        state["final_summary"] = {
            "output": state.get("output"),
            "flags_set": sorted(k for k, v in flags.items() if v),
            "flags_unset": sorted(k for k, v in flags.items() if not v),
            "has_errors": bool(state.get("error") or state.get("escalation_error")),
        }
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


# ========= Product Pipeline: Research -> Design -> Completion -> Audit -> Shipping =========
# Five-stage autonomous product pipeline, one LLM-backed operator per stage.
# Each operator only calls out to a real LLM when
# state["environment_profile"]["external_calls_allowed"] is True (set by
# EnvironmentProfileOperator, per the Tier 1/2/3 guardrails in
# EMPIRE_PROJECT_SPEC.md sec.9); otherwise it returns a deterministic stub of
# the same shape so this chain -- like every other one -- stays testable
# offline with zero external dependencies.

def _external_calls_allowed(state: Dict[str, Any]) -> bool:
    return bool(state.get("environment_profile", {}).get("external_calls_allowed", False))


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", (value or "").strip()) or "untitled"


PIPELINE_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "product_pipeline"


class ResearchDepartmentOperator(BaseOperator):
    name = "ResearchDepartmentOperator"
    operator_type = "reactive"
    engine = "product_pipeline"

    SYSTEM_PROMPT = (
        "You are the Research Department of an autonomous product pipeline. Given a "
        "brand, niche, and topic, produce a structured research dossier as a JSON object "
        "with exactly these keys: target_audience (string), core_problem (string), "
        "market_flaws (array of strings), data_points (array of strings)."
    )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        brand = state.get("brand", "")
        niche = state.get("niche", "")
        topic = state.get("topic", "")

        if _external_calls_allowed(state):
            dossier = call_llm(self.SYSTEM_PROMPT, f"Brand: {brand}\nNiche: {niche}\nTopic: {topic}")
        else:
            dossier = {
                "stub": True,
                "target_audience": f"Audience for {topic or 'this topic'} within {niche or 'this niche'}",
                "core_problem": f"Unsolved core problem for {topic or 'this topic'}",
                "market_flaws": [f"Existing {niche or 'market'} solutions lack depth on {topic or 'this topic'}"],
                "data_points": [f"Placeholder data point for {topic or 'this topic'}"],
            }

        state["research_dossier"] = dossier
        return state


class ProductDesignOperator(BaseOperator):
    name = "ProductDesignOperator"
    operator_type = "reactive"
    engine = "product_pipeline"

    SYSTEM_PROMPT = (
        "You are the Product Design Team. Given a research dossier, produce an "
        "enterprise-grade product blueprint as a JSON object with exactly these keys: "
        "specifications (array of strings), data_models (array of strings), "
        "user_flows (array of strings)."
    )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        dossier = state.get("research_dossier", {})

        if _external_calls_allowed(state):
            blueprint = call_llm(self.SYSTEM_PROMPT, json.dumps(dossier))
        else:
            problem = dossier.get("core_problem", "the core problem")
            blueprint = {
                "stub": True,
                "specifications": [f"Solve: {problem}"],
                "data_models": ["Entity: Product", "Entity: User"],
                "user_flows": ["Discover -> Evaluate -> Purchase -> Use"],
            }

        state["product_blueprint"] = blueprint
        return state


class ProductCompletionOperator(BaseOperator):
    name = "ProductCompletionOperator"
    operator_type = "reactive"
    engine = "product_pipeline"

    SYSTEM_PROMPT = (
        "You are the Product Completion Team. Given a product blueprint, produce the "
        "finished product's components for every platform as a JSON object with "
        "exactly these keys: web (string), mobile (string), api (string), "
        "content (string) -- each the actual drafted material or component "
        "description for that platform."
    )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        blueprint = state.get("product_blueprint", {})

        if _external_calls_allowed(state):
            assets = call_llm(self.SYSTEM_PROMPT, json.dumps(blueprint))
        else:
            assets = {
                "stub": True,
                "web": "Placeholder web component draft",
                "mobile": "Placeholder mobile component draft",
                "api": "Placeholder API contract draft",
                "content": "Placeholder content draft",
            }

        state["product_assets"] = assets
        return state


class PolishAuditOperator(BaseOperator):
    name = "PolishAuditOperator"
    operator_type = "conditional"
    engine = "product_pipeline"

    SYSTEM_PROMPT = (
        "You are the Polish/Audit Team. Given the finished product payload and any "
        "brand-doctrine violations already detected, audit for grammar, spelling, "
        "legal/compliance gaps, accessibility, and real-world usability gaps. Return "
        "a JSON object with exactly these keys: issues (array of strings), "
        "corrected_payload (object -- the product payload with all flagged issues "
        "fixed), compliance_notes (string)."
    )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        assets = state.get("product_assets", {})

        # Real, deterministic brand-doctrine check -- reused rather than
        # re-implemented, and always runs regardless of tier.
        state.setdefault("artifact_version", "1.0.0")
        state["copy_text"] = json.dumps(assets)
        state = BrandDoctrineComplianceOperator().execute(state)

        if _external_calls_allowed(state):
            audit = call_llm(
                self.SYSTEM_PROMPT,
                json.dumps({"product_assets": assets, "brand_violations": state["brand_violations"]}),
            )
        else:
            audit = {
                "stub": True,
                "issues": [] if state["brand_compliant"] else ["Brand doctrine violations detected"],
                "corrected_payload": assets,
                "compliance_notes": "Stub audit -- no live LLM audit performed in this environment tier.",
            }

        audit["brand_compliant"] = state["brand_compliant"]
        audit["brand_violations"] = state["brand_violations"]
        state["audit_report"] = audit
        return state


class ShippingPackagerOperator(BaseOperator):
    name = "ShippingPackagerOperator"
    operator_type = "meta"
    engine = "product_pipeline"

    SYSTEM_PROMPT = (
        "You are the Shipping Team. Given the audited, corrected product payload, "
        "write a clear, numbered, step-by-step deployment/publish guide a solo "
        "operator can follow by hand. Return a JSON object with exactly one key: "
        "instructions (string)."
    )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        brand = state.get("brand", "Brand")
        topic = state.get("topic", "Topic")
        audit_report = state.get("audit_report", {})
        corrected_payload = audit_report.get("corrected_payload", state.get("product_assets", {}))

        if _external_calls_allowed(state):
            shipping = call_llm(self.SYSTEM_PROMPT, json.dumps(corrected_payload))
            instructions = shipping.get("instructions", "")
        else:
            instructions = (
                f"Stub instructions -- no live LLM call performed in this environment tier.\n"
                f"1. Review the generated files for {brand} / {topic}.\n"
                f"2. Re-run this engine with environment=\"production\" to generate real instructions."
            )

        files = {
            f"{brand} - Research - {topic} - v1.txt": json.dumps(state.get("research_dossier", {}), indent=2),
            f"{brand} - Blueprint - {topic} - v1.txt": json.dumps(state.get("product_blueprint", {}), indent=2),
            f"{brand} - Product - {topic} - v1.txt": json.dumps(state.get("product_assets", {}), indent=2),
            f"{brand} - AuditReport - {topic} - v1.txt": json.dumps(audit_report, indent=2),
            f"{brand} - Shipping - {topic} - v1.txt": instructions,
        }

        output_dir = None
        if _external_calls_allowed(state):
            output_dir = PIPELINE_OUTPUT_DIR / f"{_slug(brand)}_{_slug(topic)}"
            output_dir.mkdir(parents=True, exist_ok=True)
            for filename, content in files.items():
                (output_dir / filename).write_text(content, encoding="utf-8")

        state["shipping_package"] = {"files": files, "instructions": instructions}
        state["shipping_output_dir"] = str(output_dir) if output_dir else None
        return state
