import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from empire_os.engines import ENGINE_REGISTRY
from empire_os.engines.engine_base import BaseEngine
from empire_os.operators.operator_base import BaseOperator
from empire_os.operators import all_operators as ops


class _EchoOperator(BaseOperator):
    name = "EchoOperator"

    def execute(self, state):
        state["echoed"] = True
        return state


ALL_ENGINE_NAMES = [
    "input", "context", "reasoning", "execution", "governance", "memory",
    "optimization", "integration",
    "are", "cfa", "talora",
    "audience_graph", "brand_geometry", "brand_enforcement",
    "research_toolkit", "knowledge_memory",
    "n8n_automation", "module_definition", "deployment_spec", "environment_context",
    "bundle_strategy",
    "computer_inventory", "system_document",
    "maximum_universe", "evolution", "multiverse_reconstruction",
    "logic_motion",
    "ops_runbook", "spec_compliance", "security_governance", "testing_validation",
    "are_blueprint", "universe_layout", "prompt_workflow", "module_pack", "research_asset",
    "product_pipeline",
]


def test_engine_registry_has_all_37_engines():
    assert set(ENGINE_REGISTRY.keys()) == set(ALL_ENGINE_NAMES)
    assert len(ENGINE_REGISTRY) == 37


@pytest.mark.parametrize("key", ALL_ENGINE_NAMES)
def test_engine_name_matches_registry_key(key):
    engine_cls = ENGINE_REGISTRY[key]
    assert issubclass(engine_cls, BaseEngine)
    assert engine_cls.name == key


@pytest.mark.parametrize("key", ALL_ENGINE_NAMES)
def test_engine_run_operator_delegates_to_operator(key):
    engine = ENGINE_REGISTRY[key]()
    state = engine.run_operator(_EchoOperator(), {})
    assert state["echoed"] is True


def test_manifest_engines_yaml_matches_registry():
    manifest_path = Path(__file__).resolve().parents[1] / "manifests" / "engines.yaml"
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    manifest_names = [e["name"] for e in manifest["engines"]]

    op = ops.RegistryComplianceOperator()
    state = op.execute({
        "registry_keys": list(ENGINE_REGISTRY.keys()),
        "manifest_keys": manifest_names,
    })
    assert state["registry_manifest_diff"]["in_sync"] is True


# ---- Class 1: Core System Operators ----

def test_recursive_maturity_operator_scores_engine_statuses():
    op = ops.RecursiveMaturityOperator()
    state = op.execute({"engine_statuses": ["built", "built", "doc", "named"]})
    assert state["maturity_pct"] == pytest.approx(62.5)


def test_recursive_maturity_operator_handles_empty_input():
    op = ops.RecursiveMaturityOperator()
    assert op.execute({"engine_statuses": []})["maturity_pct"] == 0.0


def test_logic_router_operator_routes_known_topic():
    op = ops.LogicRouterOperator()
    state = op.execute({"request_topic": "inventory"})
    assert state["routed_engine"] == "computer_inventory"


def test_logic_router_operator_falls_back_for_unknown_topic():
    op = ops.LogicRouterOperator()
    state = op.execute({"request_topic": "unknown_topic"})
    assert state["routed_engine"] == "unrouted"


@pytest.mark.parametrize("score,expected", [(10, "system1"), (50, "hybrid"), (90, "system2")])
def test_adaptive_reasoning_router_operator(score, expected):
    op = ops.AdaptiveReasoningRouterOperator()
    state = op.execute({"complexity_score": score})
    assert state["reasoning_strategy"] == expected


# ---- Class 2: Identity & Brand Operators ----

def test_segment_overlap_operator_weights_proof_tiers():
    op = ops.SegmentOverlapOperator()
    assert op.execute({"proof_tier": "T1"})["segment_weight"] == 30
    assert op.execute({"proof_tier": "T5"})["segment_weight"] == 10


def test_colorway_spec_operator_locks_real_hex_values():
    op = ops.ColorwaySpecOperator()
    green = op.execute({"colorway": "green"})["brand_spec"]
    assert green["accent_hex"] == "#39FF14"
    assert green["valid"] is True
    invalid = op.execute({"colorway": "purple"})["brand_spec"]
    assert invalid["valid"] is False


# ---- Class 3: Analytics & Intelligence Operators ----

def test_asset_classifier_operator_matches_keyword():
    op = ops.AssetClassifierOperator()
    state = op.execute({"asset_title": "AI Research Toolkit Asset Blueprint"})
    assert state["asset_category"] in ("framework", "tooling")


# ---- Class 4: Automation & Workflow Operators ----

def test_workflow_export_operator_builds_valid_shape():
    op = ops.WorkflowExportOperator()
    state = op.execute({"trigger_type": "webhook", "action_type": "http_request"})
    workflow = state["n8n_workflow"]
    assert len(workflow["nodes"]) == 2
    assert "Trigger" in workflow["connections"]


def test_module_spec_validator_operator_flags_missing_fields():
    op = ops.ModuleSpecValidatorOperator()
    state = op.execute({"module_spec": {"id": "m1", "name": "Module 1"}})
    assert state["module_valid"] is False
    assert set(state["missing_fields"]) == {"dependencies", "status"}


def test_deployment_checklist_operator_requires_all_config():
    op = ops.DeploymentChecklistOperator()
    state = op.execute({"config": {"database_url": "postgres://x"}})
    assert state["deployment_ready"] is False
    assert "redis_url" in state["missing_config"]


# ---- Class 5: Product & Monetization Operators ----

def test_bundle_pricing_operator_applies_discount():
    op = ops.BundlePricingOperator()
    state = op.execute({"sku_prices": [100, 50]})
    assert state["bundle_price"] == 127  # 150 * 0.85 = 127.5 -> floored to 127


# ---- Class 6: Data & Inventory Operators ----

def test_inventory_record_validator_operator_checks_cim_js_fields():
    op = ops.InventoryRecordValidatorOperator()
    record = {
        "device_id": "d1", "hostname": "h1", "os": "Windows", "cpu": "i7",
        "ram_gb": 16, "storage_gb": 512, "role": "workstation",
    }
    assert op.execute({"device_record": record})["record_valid"] is True
    assert op.execute({"device_record": {}})["record_valid"] is False


def test_document_header_operator_generates_header():
    op = ops.DocumentHeaderOperator()
    state = op.execute({"doc_title": "Test Doc", "doc_category": "OSR"})
    assert state["document_header"]["title"] == "Test Doc"
    assert state["document_header"]["category"] == "OSR"


# ---- Class 7: Universe & Expansion Operators ----

def test_universe_layer_lookup_operator_returns_real_doc_titles():
    op = ops.UniverseLayerLookupOperator()
    assert op.execute({"index": 0})["universe_doc"] == "Universe v5 Meta-Physics Document"
    assert len(op.UAL_DOCS) == 14


def test_maturity_delta_operator_computes_delta():
    op = ops.MaturityDeltaOperator()
    state = op.execute({"maturity_before": 35, "maturity_after": 70})
    assert state["maturity_delta"] == 35


def test_canon_index_operator_totals_match_master_index():
    op = ops.CanonIndexOperator()
    state = op.execute({"category": "UAL"})
    assert state["category_doc_count"] == 14
    assert state["total_docs"] == 135


# ---- Class 8: Cognitive & Logic Operators ----

def test_logic_to_motion_operator_advances_sequence():
    op = ops.LogicToMotionOperator()
    assert op.execute({"logic_state": "idle"})["motion_state"] == "routing"
    assert op.execute({"logic_state": "settled"})["motion_state"] == "settled"


# ---- Class 9: Support & Utility Operators ----

def test_runbook_lookup_operator_finds_keyword_match():
    op = ops.RunbookLookupOperator()
    state = op.execute({"keyword": "deployment"})
    assert "Deployment Runbook" in state["matched_runbooks"]


def test_registry_compliance_operator_detects_drift():
    op = ops.RegistryComplianceOperator()
    keys = list(ENGINE_REGISTRY.keys())
    state = op.execute({"registry_keys": keys, "manifest_keys": keys[:-1]})
    assert state["registry_manifest_diff"]["in_sync"] is False
    assert len(state["registry_manifest_diff"]["missing_from_manifest"]) == 1


def test_registry_compliance_operator_confirms_in_sync():
    op = ops.RegistryComplianceOperator()
    keys = list(ENGINE_REGISTRY.keys())
    state = op.execute({"registry_keys": keys, "manifest_keys": keys})
    assert state["registry_manifest_diff"]["in_sync"] is True


# ---- Class 10: Embedded Page Operators ----

def test_blueprint_section_operator_lists_10_canon_sections():
    state = ops.BlueprintSectionOperator().execute({})
    assert len(state["blueprint_sections"]) == 10


def test_layout_page_operator_paginates_titles():
    op = ops.LayoutPageOperator()
    state = op.execute({"doc_titles": ["Doc A", "Doc B"]})
    assert state["layout_pages"] == {1: "Doc A", 2: "Doc B"}


def test_pipeline_sequencer_operator_advances_and_completes():
    op = ops.PipelineSequencerOperator()
    assert op.execute({"current_stage": "Offer Validation"})["next_stage"] == "Content Engine"
    assert op.execute({"current_stage": "Digital Product Creation"})["next_stage"] == "complete"
    assert op.execute({"current_stage": None})["next_stage"] == "Offer Validation"


def test_pack_assembler_operator_counts_modules():
    op = ops.PackAssemblerOperator()
    state = op.execute({"module_ids": ["m1", "m2", "m3"]})
    assert state["pack"]["module_count"] == 3


def test_asset_index_operator_marks_indexed():
    op = ops.AssetIndexOperator()
    state = op.execute({"asset_title": "Test Asset", "asset_category": "framework"})
    assert state["asset_record"]["indexed"] is True


# ---- AI Research Toolkit: 16 real modules (Primary + Secondary flows) ----

def test_topic_explorer_operator_generates_four_angles():
    state = ops.TopicExplorerOperator().execute({"topic": "pricing strategy"})
    assert len(state["sub_topics"]) == 4
    assert all("pricing strategy" in s for s in state["sub_topics"])


def test_research_question_builder_operator_builds_one_question_per_subtopic():
    state = ops.ResearchQuestionBuilderOperator().execute({"sub_topics": ["A", "B"]})
    assert len(state["research_questions"]) == 2


def test_literature_summary_operator_extracts_first_sentences():
    state = ops.LiteratureSummaryOperator().execute({"data": ["First point. More detail.", "Second point."]})
    assert state["literature_summary"] == "First point. Second point"


def test_research_gap_finder_operator_flags_uncovered_questions():
    state = ops.ResearchGapFinderOperator().execute({
        "research_questions": ["What drives adoption?", "What drives churn?"],
        "literature_summary": "adoption is well documented here",
    })
    assert "What drives churn?" in state["gaps"]
    assert "What drives adoption?" not in state["gaps"]


def test_insight_extractor_operator_finds_signal_sentences():
    state = ops.InsightExtractorOperator().execute({
        "data": ["This is routine.", "This finding is significant for the market."]
    })
    assert len(state["insights"]) == 1


def test_data_interpretation_operator_computes_basic_stats():
    state = ops.DataInterpretationOperator().execute({"data": [10, 20, 30]})
    assert state["data_interpretation"] == {"mean": 20, "min": 10, "max": 30}


def test_future_scenario_builder_operator_returns_three_scenarios():
    state = ops.FutureScenarioBuilderOperator().execute({"topic": "AI adoption"})
    assert set(state["scenarios"].keys()) == {"optimistic", "base", "pessimistic"}


def test_simplify_complex_research_operator_truncates_to_max_words():
    long_summary = " ".join(["word"] * 100)
    state = ops.SimplifyComplexResearchOperator().execute({"literature_summary": long_summary})
    assert len(state["simplified_summary"].split()) == 40


def test_theory_connector_operator_builds_all_pairs():
    state = ops.TheoryConnectorOperator().execute({"concepts": ["A", "B", "C"]})
    assert state["theory_connections"] == [("A", "B"), ("A", "C"), ("B", "C")]


def test_methodology_refiner_operator_flags_missing_checklist_items():
    state = ops.MethodologyRefinerOperator().execute({"methodology": "we used a control group"})
    assert "control group" not in state["methodology_feedback"]
    assert "sample size" in state["methodology_feedback"]


def test_hypothesis_generator_operator_builds_one_per_gap():
    state = ops.HypothesisGeneratorOperator().execute({"gaps": ["gap A"]})
    assert len(state["hypotheses"]) == 1
    assert "gap A" in state["hypotheses"][0]


def test_expert_debate_simulator_operator_builds_pro_and_con():
    state = ops.ExpertDebateSimulatorOperator().execute({"hypotheses": ["h1"]})
    assert state["debate_points"][0]["pro"] and state["debate_points"][0]["con"]


def test_cross_industry_insight_operator_covers_four_industries():
    state = ops.CrossIndustryInsightOperator().execute({"topic": "churn prediction"})
    assert len(state["cross_industry_insights"]) == 4


@pytest.mark.parametrize("series,expected", [
    ([1, 5, 10], "increasing"),
    ([10, 5, 1], "decreasing"),
    ([5, 5, 5], "flat"),
    ([5], "insufficient_data"),
])
def test_trend_analyzer_operator_detects_direction(series, expected):
    state = ops.TrendAnalyzerOperator().execute({"data": series})
    assert state["trend"] == expected


def test_knowledge_map_operator_links_every_concept_to_the_others():
    state = ops.KnowledgeMapOperator().execute({"concepts": ["A", "B", "C"]})
    assert state["knowledge_map"]["A"] == ["B", "C"]


def test_research_summary_engine_operator_matches_real_output_schema():
    state = {
        "simplified_summary": "short summary",
        "insights": ["insight"],
        "gaps": ["gap"],
        "hypotheses": ["hypothesis"],
        "methodology_feedback": ["sample size"],
    }
    output = ops.ResearchSummaryEngineOperator().execute(state)["research_output"]
    assert set(output.keys()) == {"summary", "insights", "gaps", "recommendations", "next_steps"}
    assert output["summary"] == "short summary"


def test_research_toolkit_primary_flow_runs_end_to_end():
    # The real 8-step Primary Research Flow, run start to finish on one topic.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from orchestrator.chain_loader import load_chain

    chain = load_chain("research_toolkit_chain")
    assert len(chain) == 8

    engine = ENGINE_REGISTRY["research_toolkit"]()
    state = {"topic": "customer retention", "data": ["Retention is significant for revenue."]}
    for operator in chain:
        state = engine.run_operator(operator, state)

    assert "research_output" in state
    assert set(state["research_output"].keys()) == {"summary", "insights", "gaps", "recommendations", "next_steps"}


# ---- Brand Enforcement: real Doctrine Enforcement Rules ----

def test_brand_doctrine_compliance_operator_passes_clean_copy():
    state = ops.BrandDoctrineComplianceOperator().execute({
        "copy_text": "This system helps operators plan work clearly.",
        "artifact_version": "1.0.0",
    })
    assert state["brand_compliant"] is True
    assert state["brand_violations"] == {}


def test_brand_doctrine_compliance_operator_flags_empire_metaphor():
    state = ops.BrandDoctrineComplianceOperator().execute({
        "copy_text": "Build your empire and conquer the market.",
        "artifact_version": "1.0.0",
    })
    assert state["brand_compliant"] is False
    assert "empire" in state["brand_violations"]["empire_metaphors"]


def test_brand_doctrine_compliance_operator_flags_hype_and_urgency():
    state = ops.BrandDoctrineComplianceOperator().execute({
        "copy_text": "Act now, don't miss out -- unlock greatness today!",
        "artifact_version": "1.0.0",
    })
    assert "emotional_manipulation" in state["brand_violations"]
    assert "inspirational_hype" in state["brand_violations"]


def test_brand_doctrine_compliance_operator_requires_a_version():
    state = ops.BrandDoctrineComplianceOperator().execute({"copy_text": "Clean, plain copy."})
    assert state["brand_compliant"] is False
    assert "unversioned_artifact" in state["brand_violations"]


# ---- Universe v5 causal layers: Security & Governance, Testing & Validation,
# ---- Environment & Context, Knowledge & Memory ----

def test_access_control_operator_grants_permitted_action():
    state = ops.AccessControlOperator().execute({"role": "architect", "requested_action": "write"})
    assert state["access_granted"] is True


def test_access_control_operator_denies_unpermitted_action():
    state = ops.AccessControlOperator().execute({"role": "operator", "requested_action": "admin"})
    assert state["access_granted"] is False
    assert "admin" not in state["role_permissions"]


def test_access_control_operator_defaults_to_least_privilege():
    state = ops.AccessControlOperator().execute({"requested_action": "write"})
    assert state["access_granted"] is False  # default role "operator" cannot write


def test_test_coverage_operator_flags_untested_components():
    state = ops.TestCoverageOperator().execute({
        "components": ["are", "cfa", "talora"],
        "tested_components": ["are", "cfa"],
    })
    assert state["untested_components"] == ["talora"]
    assert state["test_coverage_pct"] == pytest.approx(66.7, rel=1e-2)


def test_test_coverage_operator_against_the_real_engine_registry():
    # Self-referential check: how much of empire_os's own engine set has a
    # dedicated unit test function in this very file?
    import re
    test_source = Path(__file__).read_text(encoding="utf-8")
    tested = {name for name in ENGINE_REGISTRY if re.search(rf"\b{name}\b", test_source)}
    state = ops.TestCoverageOperator().execute({
        "components": list(ENGINE_REGISTRY.keys()),
        "tested_components": list(tested),
    })
    assert state["test_coverage_pct"] > 0


def test_environment_profile_operator_matches_tier_system():
    local = ops.EnvironmentProfileOperator().execute({"environment": "local"})["environment_profile"]
    prod = ops.EnvironmentProfileOperator().execute({"environment": "production"})["environment_profile"]
    assert local["tier_ceiling"] == 1 and local["external_calls_allowed"] is False
    assert prod["tier_ceiling"] == 3 and prod["external_calls_allowed"] is True


def test_environment_profile_operator_defaults_to_local():
    state = ops.EnvironmentProfileOperator().execute({})
    assert state["environment_profile"] == ops.EnvironmentProfileOperator.PROFILES["local"]


def test_knowledge_graph_operator_builds_subject_adjacency():
    state = ops.KnowledgeGraphOperator().execute({
        "triples": [("empire_os", "contains", "engines"), ("empire_os", "contains", "operators")]
    })
    assert state["knowledge_graph"]["empire_os"] == [("contains", "engines"), ("contains", "operators")]


# ---- Product Pipeline: Research -> Design -> Completion -> Audit -> Shipping ----
# environment_profile is absent/local in all these tests, so every stage takes
# the stub branch -- no network access, no OPENAI_API_KEY required.

def test_research_department_operator_stub_in_local_tier():
    state = ops.ResearchDepartmentOperator().execute({"brand": "Acme", "niche": "Home Office", "topic": "Keyboard Stand"})
    dossier = state["research_dossier"]
    assert dossier["stub"] is True
    assert set(dossier.keys()) == {"stub", "target_audience", "core_problem", "market_flaws", "data_points"}


def test_product_design_operator_stub_consumes_dossier():
    state = ops.ProductDesignOperator().execute({"research_dossier": {"core_problem": "wrist strain"}})
    blueprint = state["product_blueprint"]
    assert blueprint["stub"] is True
    assert "wrist strain" in blueprint["specifications"][0]


def test_product_completion_operator_stub_covers_all_platforms():
    state = ops.ProductCompletionOperator().execute({"product_blueprint": {}})
    assets = state["product_assets"]
    assert set(assets.keys()) == {"stub", "web", "mobile", "api", "content"}


def test_polish_audit_operator_flags_real_brand_violations():
    state = ops.PolishAuditOperator().execute({
        "product_assets": {"content": "Build your empire and conquer the market."}
    })
    audit = state["audit_report"]
    assert audit["brand_compliant"] is False
    assert "empire_metaphors" in audit["brand_violations"]
    assert audit["issues"] == ["Brand doctrine violations detected"]


def test_polish_audit_operator_passes_clean_copy():
    state = ops.PolishAuditOperator().execute({"product_assets": {"content": "A clear, plain product description."}})
    audit = state["audit_report"]
    assert audit["brand_compliant"] is True
    assert audit["issues"] == []


def test_shipping_packager_operator_builds_all_five_files_without_disk_write():
    state = ops.ShippingPackagerOperator().execute({
        "brand": "Acme", "topic": "Keyboard Stand",
        "research_dossier": {}, "product_blueprint": {}, "product_assets": {},
        "audit_report": {"corrected_payload": {}},
    })
    files = state["shipping_package"]["files"]
    assert set(files.keys()) == {
        "Acme - Research - Keyboard Stand - v1.txt",
        "Acme - Blueprint - Keyboard Stand - v1.txt",
        "Acme - Product - Keyboard Stand - v1.txt",
        "Acme - AuditReport - Keyboard Stand - v1.txt",
        "Acme - Shipping - Keyboard Stand - v1.txt",
    }
    assert state["shipping_output_dir"] is None  # local tier: no disk side effects


def test_product_pipeline_local_tier_runs_end_to_end():
    # The real 6-step chain (env resolve + 5 stages), run start to finish in
    # local tier -- every stage takes its stub branch, so this needs no
    # network access and no OPENAI_API_KEY.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from orchestrator.chain_loader import load_chain

    chain = load_chain("product_pipeline_chain")
    assert len(chain) == 6

    engine = ENGINE_REGISTRY["product_pipeline"]()
    state = {"brand": "Acme", "niche": "Home Office", "topic": "Keyboard Stand"}
    for operator in chain:
        state = engine.run_operator(operator, state)

    assert state["environment_profile"]["external_calls_allowed"] is False
    assert state["research_dossier"]["stub"] is True
    assert state["product_blueprint"]["stub"] is True
    assert state["product_assets"]["stub"] is True
    assert "audit_report" in state
    assert len(state["shipping_package"]["files"]) == 5
    assert state["shipping_output_dir"] is None
