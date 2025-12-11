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

# Phase 8: Natural Language Adapter
from .adapter import (
    LLM_TRANSLATION_EXAMPLES,
    # Constants
    TRANSLATION_PATTERNS,
    # Adapter
    AgentesAdapter,
    AsyncTranslator,
    LLMProtocol,
    LLMTranslator,
    # Translators
    PatternTranslator,
    TranslationError,
    # Result types
    TranslationResult,
    # Protocols
    Translator,
    build_translation_prompt,
    # Factory functions
    create_adapter,
    create_pattern_translator,
)

# Phase 3: Affordances
from .affordances import (
    ARCHETYPE_AFFORDANCES,
    CONCEPT_AFFORDANCE_SET,
    # Constants
    CORE_ASPECTS,
    SELF_AFFORDANCE_SET,
    STANDARD_ASPECTS,
    TIME_AFFORDANCE_SET,
    VOID_AFFORDANCE_SET,
    WORLD_AFFORDANCE_SET,
    # Matcher
    AffordanceMatcher,
    # Registry
    AffordanceRegistry,
    # DNA
    ArchetypeDNA,
    Aspect,
    # Types
    AspectCategory,
    CapabilityAffordanceMatcher,
    # Context sets
    ContextAffordanceSet,
    StandardAffordanceMatcher,
    # Adapter
    UmweltAdapter,
    create_affordance_registry,
    create_umwelt_adapter,
    get_context_affordance_set,
)

# Phase 2: Context Resolvers
from .contexts import (
    VALID_CONTEXTS,
    CapabilitiesNode,
    # Concept context
    ConceptContextResolver,
    ConceptNode,
    EntropyNode,
    EntropyPool,
    FutureNode,
    GratitudeNode,
    IdentityNode,
    MemoryNode,
    PastNode,
    RandomnessGrant,
    ScheduledAction,
    ScheduleNode,
    # Self context
    SelfContextResolver,
    SerendipityNode,
    StateNode,
    # Time context
    TimeContextResolver,
    TraceNode,
    # Void context
    VoidContextResolver,
    # World context
    WorldContextResolver,
    WorldNode,
    create_concept_node,
    create_concept_resolver,
    # Unified factory
    create_context_resolvers,
    create_entropy_pool,
    create_self_resolver,
    create_time_resolver,
    create_void_resolver,
    create_world_node,
    create_world_resolver,
)
from .exceptions import (
    AffordanceError,
    AgentesError,
    BudgetExhaustedError,
    CompositionViolationError,
    ObserverRequiredError,
    PathNotFoundError,
    PathSyntaxError,
    TastefulnessError,
)

# Phase 6: Integration Layer
from .integration import (
    # G-gent Integration
    AGENTESE_BNF,
    AGENTESE_CONSTRAINTS,
    AGENTESE_EXAMPLES,
    # Membrane Integration
    MEMBRANE_AGENTESE_MAP,
    # Unified Factory
    AgentesIntegrations,
    GgentIntegration,
    LgentIntegration,
    # L-gent Integration
    LgentRegistryProtocol,
    MembraneAgenteseBridge,
    # Umwelt Integration
    UmweltIntegration,
    create_agentese_integrations,
    create_ggent_integration,
    create_lgent_integration,
    create_membrane_bridge,
    create_umwelt_integration,
)

# Phase 4: JIT Compilation
from .jit import (
    JITCompiler,
    JITPromoter,
    # Parser
    ParsedSpec,
    # Promotion
    PromotionResult,
    # Compiler
    SpecCompiler,
    SpecParser,
    compile_spec,
    # Factory functions
    create_jit_compiler,
)

# Phase 5: Composition & Category Laws
from .laws import (
    IDENTITY,
    CategoryLawVerifier,
    Composable,
    Composed,
    Id,
    # Core types
    Identity,
    LawEnforcingComposition,
    # Law verification
    LawVerificationResult,
    SimpleMorphism,
    # Helpers
    compose,
    create_enforcing_composition,
    create_verifier,
    enforce_minimal_output,
    # Minimal output
    is_single_logical_unit,
    morphism,
    pipe,
)
from .logos import ComposedPath, IdentityPath, Logos, create_logos
from .node import (
    AffordanceSet,
    AgentMeta,
    BaseLogosNode,
    BasicRendering,
    BlueprintRendering,
    EconomicRendering,
    JITLogosNode,
    LogosNode,
    PoeticRendering,
    Renderable,
)

# Phase 3: Renderings
from .renderings import (
    AdminRendering,
    DeveloperRendering,
    EntropyRendering,
    EntropyRenderingFactory,
    MemoryRendering,
    MemoryRenderingFactory,
    PhilosopherRendering,
    RenderingFactory,
    ScientificRendering,
    StandardRenderingFactory,
    TemporalRendering,
    TemporalRenderingFactory,
    create_rendering_factory,
    render_for_archetype,
)

# Phase 7: Wire to Logos
from .wiring import (
    WiredLogos,
    create_minimal_wired_logos,
    create_wired_logos,
    wire_existing_logos,
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
