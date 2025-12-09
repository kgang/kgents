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
    SandboxResult,
    SandboxedNamespace,
    execute_in_sandbox,
    jit_compile_and_execute,
    type_check_source,
    validate_jit_safety,
)
from .forge_integration import (
    ForgeTemplate,
    TemplateParameters,
    InstantiatedAgent,
    TemplateRegistry,
    contract_to_template,
    instantiate_template,
    forge_and_instantiate,
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
]
