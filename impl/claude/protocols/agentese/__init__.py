"""
AGENTESE: The Verb-First Ontology

Where getting IS invoking. Where nouns ARE frozen verbs.
Where observation collapses potential into actuality.

> "The noun is a lie. There is only the rate of change."

Core exports:
- Logos: The resolver functor (H(Context) -> Interaction)
- LogosNode: Protocol for resolvable entities
- AffordanceSet: Observer-specific verb list
- Exceptions: Sympathetic error types
- Context resolvers: world, self, concept, void, time
"""

from .exceptions import (
    AgentesError,
    PathNotFoundError,
    PathSyntaxError,
    AffordanceError,
    ObserverRequiredError,
    TastefulnessError,
    BudgetExhaustedError,
    CompositionViolationError,
)
from .node import (
    LogosNode,
    AffordanceSet,
    AgentMeta,
    Renderable,
    BasicRendering,
    BlueprintRendering,
    PoeticRendering,
    EconomicRendering,
    JITLogosNode,
    BaseLogosNode,
)
from .logos import Logos, create_logos, ComposedPath, IdentityPath

# Phase 3: Affordances
from .affordances import (
    # Types
    AspectCategory,
    Aspect,
    # Constants
    CORE_ASPECTS,
    STANDARD_ASPECTS,
    ARCHETYPE_AFFORDANCES,
    # Registry
    AffordanceRegistry,
    create_affordance_registry,
    # Matcher
    AffordanceMatcher,
    StandardAffordanceMatcher,
    CapabilityAffordanceMatcher,
    # DNA
    ArchetypeDNA,
    # Adapter
    UmweltAdapter,
    create_umwelt_adapter,
    # Context sets
    ContextAffordanceSet,
    WORLD_AFFORDANCE_SET,
    SELF_AFFORDANCE_SET,
    CONCEPT_AFFORDANCE_SET,
    VOID_AFFORDANCE_SET,
    TIME_AFFORDANCE_SET,
    get_context_affordance_set,
)

# Phase 3: Renderings
from .renderings import (
    ScientificRendering,
    DeveloperRendering,
    AdminRendering,
    PhilosopherRendering,
    MemoryRendering,
    EntropyRendering,
    TemporalRendering,
    RenderingFactory,
    StandardRenderingFactory,
    MemoryRenderingFactory,
    EntropyRenderingFactory,
    TemporalRenderingFactory,
    create_rendering_factory,
    render_for_archetype,
)

# Phase 4: JIT Compilation
from .jit import (
    # Parser
    ParsedSpec,
    SpecParser,
    # Compiler
    SpecCompiler,
    JITCompiler,
    # Promotion
    PromotionResult,
    JITPromoter,
    # Factory functions
    create_jit_compiler,
    compile_spec,
)

# Phase 5: Composition & Category Laws
from .laws import (
    # Core types
    Identity,
    Id,
    IDENTITY,
    Composable,
    Composed,
    # Law verification
    LawVerificationResult,
    CategoryLawVerifier,
    # Minimal output
    is_single_logical_unit,
    enforce_minimal_output,
    # Helpers
    compose,
    pipe,
    LawEnforcingComposition,
    SimpleMorphism,
    morphism,
    create_verifier,
    create_enforcing_composition,
)

# Phase 6: Integration Layer
from .integration import (
    # Umwelt Integration
    UmweltIntegration,
    create_umwelt_integration,
    # Membrane Integration
    MEMBRANE_AGENTESE_MAP,
    MembraneAgenteseBridge,
    create_membrane_bridge,
    # L-gent Integration
    LgentRegistryProtocol,
    LgentIntegration,
    create_lgent_integration,
    # G-gent Integration
    AGENTESE_BNF,
    AGENTESE_CONSTRAINTS,
    AGENTESE_EXAMPLES,
    GgentIntegration,
    create_ggent_integration,
    # Unified Factory
    AgentesIntegrations,
    create_agentese_integrations,
)

# Phase 7: Wire to Logos
from .wiring import (
    WiredLogos,
    create_wired_logos,
    wire_existing_logos,
    create_minimal_wired_logos,
)

# Phase 8: Natural Language Adapter
from .adapter import (
    # Result types
    TranslationResult,
    TranslationError,
    # Constants
    TRANSLATION_PATTERNS,
    LLM_TRANSLATION_EXAMPLES,
    # Protocols
    Translator,
    AsyncTranslator,
    LLMProtocol,
    # Translators
    PatternTranslator,
    LLMTranslator,
    # Adapter
    AgentesAdapter,
    # Factory functions
    create_adapter,
    create_pattern_translator,
    build_translation_prompt,
)

# Phase 2: Context Resolvers
from .contexts import (
    VALID_CONTEXTS,
    # World context
    WorldContextResolver,
    WorldNode,
    create_world_resolver,
    create_world_node,
    # Self context
    SelfContextResolver,
    MemoryNode,
    CapabilitiesNode,
    StateNode,
    IdentityNode,
    create_self_resolver,
    # Concept context
    ConceptContextResolver,
    ConceptNode,
    create_concept_resolver,
    create_concept_node,
    # Void context
    VoidContextResolver,
    EntropyPool,
    EntropyNode,
    SerendipityNode,
    GratitudeNode,
    RandomnessGrant,
    create_void_resolver,
    create_entropy_pool,
    # Time context
    TimeContextResolver,
    TraceNode,
    PastNode,
    FutureNode,
    ScheduleNode,
    ScheduledAction,
    create_time_resolver,
    # Unified factory
    create_context_resolvers,
)

__all__ = [
    # Core
    "Logos",
    "create_logos",
    "LogosNode",
    "AffordanceSet",
    "AgentMeta",
    "Renderable",
    "BasicRendering",
    "BlueprintRendering",
    "PoeticRendering",
    "EconomicRendering",
    "JITLogosNode",
    "BaseLogosNode",
    # Exceptions
    "AgentesError",
    "PathNotFoundError",
    "PathSyntaxError",
    "AffordanceError",
    "ObserverRequiredError",
    "TastefulnessError",
    "BudgetExhaustedError",
    "CompositionViolationError",
    # Phase 3: Affordances
    "AspectCategory",
    "Aspect",
    "CORE_ASPECTS",
    "STANDARD_ASPECTS",
    "ARCHETYPE_AFFORDANCES",
    "AffordanceRegistry",
    "create_affordance_registry",
    "AffordanceMatcher",
    "StandardAffordanceMatcher",
    "CapabilityAffordanceMatcher",
    "ArchetypeDNA",
    "UmweltAdapter",
    "create_umwelt_adapter",
    "ContextAffordanceSet",
    "WORLD_AFFORDANCE_SET",
    "SELF_AFFORDANCE_SET",
    "CONCEPT_AFFORDANCE_SET",
    "VOID_AFFORDANCE_SET",
    "TIME_AFFORDANCE_SET",
    "get_context_affordance_set",
    # Phase 3: Renderings
    "ScientificRendering",
    "DeveloperRendering",
    "AdminRendering",
    "PhilosopherRendering",
    "MemoryRendering",
    "EntropyRendering",
    "TemporalRendering",
    "RenderingFactory",
    "StandardRenderingFactory",
    "MemoryRenderingFactory",
    "EntropyRenderingFactory",
    "TemporalRenderingFactory",
    "create_rendering_factory",
    "render_for_archetype",
    # Constants
    "VALID_CONTEXTS",
    # Context Resolvers
    "WorldContextResolver",
    "WorldNode",
    "create_world_resolver",
    "create_world_node",
    "SelfContextResolver",
    "MemoryNode",
    "CapabilitiesNode",
    "StateNode",
    "IdentityNode",
    "create_self_resolver",
    "ConceptContextResolver",
    "ConceptNode",
    "create_concept_resolver",
    "create_concept_node",
    "VoidContextResolver",
    "EntropyPool",
    "EntropyNode",
    "SerendipityNode",
    "GratitudeNode",
    "RandomnessGrant",
    "create_void_resolver",
    "create_entropy_pool",
    "TimeContextResolver",
    "TraceNode",
    "PastNode",
    "FutureNode",
    "ScheduleNode",
    "ScheduledAction",
    "create_time_resolver",
    "create_context_resolvers",
    # Phase 4: JIT Compilation
    "ParsedSpec",
    "SpecParser",
    "SpecCompiler",
    "JITCompiler",
    "PromotionResult",
    "JITPromoter",
    "create_jit_compiler",
    "compile_spec",
    # Phase 5: Composition & Category Laws
    "ComposedPath",
    "IdentityPath",
    "Identity",
    "Id",
    "IDENTITY",
    "Composable",
    "Composed",
    "LawVerificationResult",
    "CategoryLawVerifier",
    "is_single_logical_unit",
    "enforce_minimal_output",
    "compose",
    "pipe",
    "LawEnforcingComposition",
    "SimpleMorphism",
    "morphism",
    "create_verifier",
    "create_enforcing_composition",
    # Phase 6: Integration Layer
    "UmweltIntegration",
    "create_umwelt_integration",
    "MEMBRANE_AGENTESE_MAP",
    "MembraneAgenteseBridge",
    "create_membrane_bridge",
    "LgentRegistryProtocol",
    "LgentIntegration",
    "create_lgent_integration",
    "AGENTESE_BNF",
    "AGENTESE_CONSTRAINTS",
    "AGENTESE_EXAMPLES",
    "GgentIntegration",
    "create_ggent_integration",
    "AgentesIntegrations",
    "create_agentese_integrations",
    # Phase 7: Wire to Logos
    "WiredLogos",
    "create_wired_logos",
    "wire_existing_logos",
    "create_minimal_wired_logos",
    # Phase 8: Natural Language Adapter
    "TranslationResult",
    "TranslationError",
    "TRANSLATION_PATTERNS",
    "LLM_TRANSLATION_EXAMPLES",
    "Translator",
    "AsyncTranslator",
    "LLMProtocol",
    "PatternTranslator",
    "LLMTranslator",
    "AgentesAdapter",
    "create_adapter",
    "create_pattern_translator",
    "build_translation_prompt",
]
