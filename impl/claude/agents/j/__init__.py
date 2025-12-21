"""
J-gents: Just-in-Time Agent Intelligence

The letter J represents agents that embody JIT (Just-in-Time) intelligence:
the ability to classify reality, defer computation, compile ephemeral sub-agents,
and collapse safely when stability is threatened.

Philosophy:
> "Determine the nature of reality; compile the mind to match it; collapse to safety."

Core components:
- Promise[T]: Lazy computation with Ground fallback
- Reality: DETERMINISTIC | PROBABILISTIC | CHAOTIC classification
- RealityClassifier: Agent that classifies tasks
- Chaosmonger: AST-based stability analyzer (Phase 2)
- MetaArchitect: JIT agent compiler (Phase 3)
- Sandbox: Safe execution environment (Phase 3)
- JGent: Main coordinator (Phase 4)

See spec/j-gents/ for the full specification.
"""

from .chaosmonger import (
    Chaosmonger,
    StabilityConfig,
    StabilityInput,
    StabilityMetrics,
    StabilityResult,
    analyze_stability,
    check_stability,
    is_stable,
)
from .factory_integration import (
    JITAgentMeta,
    JITAgentWrapper,
    compile_and_instantiate,
    create_agent_from_source,
    get_jit_meta,
    is_jit_agent,
)
from .forge_integration import (
    ForgeTemplate,
    InstantiatedAgent,
    TemplateParameters,
    TemplateRegistry,
    contract_to_template,
    forge_and_instantiate,
    instantiate_template,
)
from .jgent import (
    GeneratedTest,
    JGent,
    JGentConfig,
    JGentInput,
    JGentResult,
    generate_test_for_intent,
    jgent,
    jgent_sync,
)
from .meta_architect import (
    AgentSource,
    ArchitectConstraints,
    ArchitectInput,
    MetaArchitect,
    compile_agent,
    validate_source_safety,
)
from .promise import (
    Promise,
    PromiseMetrics,
    PromiseState,
    child_promise,
    collect_metrics,
    promise,
)
from .reality import (
    ClassificationInput,
    ClassificationOutput,
    Reality,
    RealityClassifier,
    classify,
    classify_intent,
    classify_sync,
)
from .sandbox import (
    SandboxConfig,
    SandboxedNamespace,
    SandboxResult,
    execute_in_sandbox,
    jit_compile_and_execute,
    type_check_source,
    validate_jit_safety,
)

# Shared Entropy Budget (J-gent × B-gent integration)
from .shared_budget import (
    DualEntropyBudget,
    SharedEntropyBudget,
    compute_depth_from_budget,
    create_depth_based_budget,
    create_dual_budget,
)
from .t_integration import (
    FILTER_TEMPLATE,
    JSON_FIELD_EXTRACTOR,
    TEXT_TRANSFORMER,
    JITToolMeta,
    JITToolWrapper as JITTool,
    ToolTemplate,
    compile_tool_from_intent,
    compile_tool_from_template,
    create_tool_from_source,
)

# Target Selection (Foundry Phase 2)
from .target_selector import (
    Target,
    TargetSelectionInput,
    TargetSelectionOutput,
    is_sandbox_required,
    recommend_target_for_code,
    select_target,
    select_target_with_reason,
)

__all__ = [
    # Promise types (Phase 1)
    "Promise",
    "PromiseState",
    "PromiseMetrics",
    # Promise helpers
    "promise",
    "child_promise",
    "collect_metrics",
    # Reality types (Phase 1)
    "Reality",
    "ClassificationInput",
    "ClassificationOutput",
    # Reality agent
    "RealityClassifier",
    # Reality helpers
    "classify",
    "classify_intent",
    "classify_sync",
    # Stability types (Phase 2)
    "StabilityConfig",
    "StabilityInput",
    "StabilityMetrics",
    "StabilityResult",
    # Stability agent (Phase 2)
    "Chaosmonger",
    # Stability helpers (Phase 2)
    "analyze_stability",
    "check_stability",
    "is_stable",
    # MetaArchitect types (Phase 3)
    "ArchitectInput",
    "ArchitectConstraints",
    "AgentSource",
    # MetaArchitect agent (Phase 3)
    "MetaArchitect",
    # MetaArchitect helpers (Phase 3)
    "compile_agent",
    "validate_source_safety",
    # Sandbox types (Phase 3)
    "SandboxConfig",
    "SandboxResult",
    "SandboxedNamespace",
    # Sandbox helpers (Phase 3)
    "execute_in_sandbox",
    "jit_compile_and_execute",
    "type_check_source",
    "validate_jit_safety",
    # JGent types (Phase 4)
    "JGentConfig",
    "JGentInput",
    "JGentResult",
    "GeneratedTest",
    # JGent coordinator (Phase 4)
    "JGent",
    # JGent helpers (Phase 4)
    "jgent",
    "jgent_sync",
    "generate_test_for_intent",
    # F+J Integration types (Cross-Pollination T1.3)
    "ForgeTemplate",
    "TemplateParameters",
    "InstantiatedAgent",
    "TemplateRegistry",
    # F+J Integration helpers (Cross-Pollination T1.3)
    "contract_to_template",
    "instantiate_template",
    "forge_and_instantiate",
    # AgentFactory Integration (Phase 5)
    "JITAgentMeta",
    "JITAgentWrapper",
    # AgentFactory Integration helpers (Phase 5)
    "create_agent_from_source",
    "compile_and_instantiate",
    "get_jit_meta",
    "is_jit_agent",
    # T+J Integration types (Cross-Pollination Phase 7)
    "ToolTemplate",
    "JITToolMeta",
    "JITTool",
    # T+J Integration helpers (Cross-Pollination Phase 7)
    "compile_tool_from_intent",
    "compile_tool_from_template",
    "create_tool_from_source",
    # T+J Common Templates
    "JSON_FIELD_EXTRACTOR",
    "TEXT_TRANSFORMER",
    "FILTER_TEMPLATE",
    # Shared Budget (J-gent × B-gent integration)
    "SharedEntropyBudget",
    "DualEntropyBudget",
    "create_depth_based_budget",
    "compute_depth_from_budget",
    "create_dual_budget",
    # Target Selection (Foundry Phase 2)
    "Target",
    "TargetSelectionInput",
    "TargetSelectionOutput",
    "select_target",
    "select_target_with_reason",
    "is_sandbox_required",
    "recommend_target_for_code",
]
