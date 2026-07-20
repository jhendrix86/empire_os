from .input_engine import InputEngine
from .context_engine import ContextEngine
from .reasoning_engine import ReasoningEngine
from .execution_engine import ExecutionEngine
from .governance_engine import GovernanceEngine
from .memory_engine import MemoryEngine
from .optimization_engine import OptimizationEngine
from .integration_engine import IntegrationEngine

# Class 1 -- Core System Engines
from .are_engine import AREEngine
from .cfa_engine import CFAEngine
from .talora_engine import TaloraEngine

# Class 2 -- Identity & Brand Engines
from .audience_graph_engine import AudienceGraphEngine
from .brand_geometry_engine import BrandGeometryEngine
from .brand_enforcement_engine import BrandEnforcementEngine

# Class 3 -- Analytics & Intelligence Engines
from .research_toolkit_engine import ResearchToolkitEngine
from .knowledge_memory_engine import KnowledgeMemoryEngine

# Class 4 -- Automation & Workflow Engines
from .n8n_automation_engine import N8nAutomationEngine
from .module_definition_engine import ModuleDefinitionEngine
from .deployment_spec_engine import DeploymentSpecEngine
from .environment_context_engine import EnvironmentContextEngine

# Class 5 -- Product & Monetization Engines
from .bundle_strategy_engine import BundleStrategyEngine

# Class 6 -- Data & Inventory Engines
from .computer_inventory_engine import ComputerInventoryEngine
from .system_document_engine import SystemDocumentEngine

# Class 7 -- Universe & Expansion Engines
from .maximum_universe_engine import MaximumUniverseEngine
from .evolution_engine import EvolutionEngine
from .multiverse_reconstruction_engine import MultiverseReconstructionEngine

# Class 8 -- Cognitive & Logic Engines
from .logic_motion_engine import LogicMotionEngine

# Class 9 -- Support & Utility Engines
from .ops_runbook_engine import OpsRunbookEngine
from .spec_compliance_engine import SpecComplianceEngine
from .security_governance_engine import SecurityGovernanceEngine
from .testing_validation_engine import TestingValidationEngine

# Class 10 -- Embedded Page Engines
from .are_blueprint_engine import AREBlueprintEngine
from .universe_layout_engine import UniverseLayoutEngine
from .prompt_workflow_engine import PromptWorkflowEngine
from .module_pack_engine import ModulePackEngine
from .research_asset_engine import ResearchAssetEngine

ENGINE_REGISTRY = {
    "input": InputEngine,
    "context": ContextEngine,
    "reasoning": ReasoningEngine,
    "execution": ExecutionEngine,
    "governance": GovernanceEngine,
    "memory": MemoryEngine,
    "optimization": OptimizationEngine,
    "integration": IntegrationEngine,
    "are": AREEngine,
    "cfa": CFAEngine,
    "talora": TaloraEngine,
    "audience_graph": AudienceGraphEngine,
    "brand_geometry": BrandGeometryEngine,
    "brand_enforcement": BrandEnforcementEngine,
    "research_toolkit": ResearchToolkitEngine,
    "knowledge_memory": KnowledgeMemoryEngine,
    "n8n_automation": N8nAutomationEngine,
    "module_definition": ModuleDefinitionEngine,
    "deployment_spec": DeploymentSpecEngine,
    "environment_context": EnvironmentContextEngine,
    "bundle_strategy": BundleStrategyEngine,
    "computer_inventory": ComputerInventoryEngine,
    "system_document": SystemDocumentEngine,
    "maximum_universe": MaximumUniverseEngine,
    "evolution": EvolutionEngine,
    "multiverse_reconstruction": MultiverseReconstructionEngine,
    "logic_motion": LogicMotionEngine,
    "ops_runbook": OpsRunbookEngine,
    "spec_compliance": SpecComplianceEngine,
    "security_governance": SecurityGovernanceEngine,
    "testing_validation": TestingValidationEngine,
    "are_blueprint": AREBlueprintEngine,
    "universe_layout": UniverseLayoutEngine,
    "prompt_workflow": PromptWorkflowEngine,
    "module_pack": ModulePackEngine,
    "research_asset": ResearchAssetEngine,
}