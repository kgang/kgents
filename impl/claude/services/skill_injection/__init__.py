"""
Skill Injection Crown Jewel: JIT Skill Activation for kgents.

The Skill Injection service provides:
- SkillRegistry: Central registry for skills with activation conditions
- ActivationConditionEngine: Evaluates skills against context
- StigmergicMemory: Learning from skill usage traces
- JITInjector: Runtime skill content injection

Philosophy:
    "Skills surface exactly when needed, not before."
    "Context-aware activation based on task patterns."
    "Learn from what worked, forget what didn't."

The Nine Components (J1-J9 from theory-operationalization):
- J1: SkillRegistry - Registry with activation conditions
- J2: Meta-Epistemic Naming - LLM-optimized skill names
- J3: ActivationConditionEngine - Condition evaluation
- J4: StigmergicMemory - Skill usage traces
- J5: SkillComposer - Skill composition (via COMMON_COMPOSITIONS)
- J6: JITInjector - Runtime skill injection
- J7: SkillEvolver - Skill evolution (via StigmergicMemory.suggest_compositions)
- J8: ContextualActivation - Context-aware activation (via engine.select_skills)
- J9: SkillObserver - Skill usage observer (via JITInjector.record_outcome)

AGENTESE Paths:
- self.skill.manifest   - Registry status and statistics
- self.skill.active     - Currently active/injected skills
- self.skill.inject     - Inject skills for a task
- self.skill.evolve     - Trigger skill evolution from usage patterns
- self.skill.search     - Search for skills by keyword
- self.skill.gotchas    - Get gotchas for a task

See: docs/skills/metaphysical-fullstack.md
"""

# Core Types (J2: Meta-Epistemic Naming)
# Activation Engine (J3: ActivationConditionEngine, J8: ContextualActivation)
from .activation_engine import (
    ActivationConditionEngine,
    ActivationConfig,
    ActivationScore,
    get_activation_engine,
    reset_activation_engine,
    set_activation_engine,
)

# Bootstrap
from .bootstrap import (
    bootstrap_skills,
    bootstrap_skills_from_routing,
    categorize_skill,
    extract_activation_conditions,
    load_skill_from_file,
)

# JIT Injector (J6: JITInjector, J9: SkillObserver)
from .jit_injector import (
    InjectionConfig,
    JITInjector,
    SkillContentReader,
    get_jit_injector,
    reset_jit_injector,
    set_jit_injector,
)

# AGENTESE Node
from .node import (
    EvolveResponse,
    GotchasRequest,
    GotchasResponse,
    InjectRendering,
    InjectRequest,
    InjectResponse,
    RecordOutcomeRequest,
    RecordOutcomeResponse,
    SearchRequest,
    SearchResponse,
    SkillManifestRendering,
    SkillManifestResponse,
    SkillNode,
)

# Registry (J1: SkillRegistry)
from .registry import (
    DuplicateSkillError,
    SkillMatch,
    SkillNotFoundError,
    SkillRegistry,
    get_skill_registry,
    reset_skill_registry,
    set_skill_registry,
)

# Stigmergic Memory (J4: StigmergicMemory, J7: SkillEvolver)
from .stigmergic_memory import (
    CompositionStats,
    StigmergicMemory,
    UsageStats,
    compute_context_hash,
    get_stigmergic_memory,
    reset_stigmergic_memory,
    set_stigmergic_memory,
)
from .types import (
    COMMON_COMPOSITIONS,
    ActivationCondition,
    ContextType,
    InjectionResult,
    Skill,
    SkillActivation,
    SkillCategory,
    SkillComposition,
    SkillUsageTrace,
    TaskContext,
    UsageOutcome,
)

__all__ = [
    # Types
    "ActivationCondition",
    "COMMON_COMPOSITIONS",
    "ContextType",
    "InjectionResult",
    "Skill",
    "SkillActivation",
    "SkillCategory",
    "SkillComposition",
    "SkillUsageTrace",
    "TaskContext",
    "UsageOutcome",
    # Registry
    "DuplicateSkillError",
    "SkillMatch",
    "SkillNotFoundError",
    "SkillRegistry",
    "get_skill_registry",
    "reset_skill_registry",
    "set_skill_registry",
    # Activation Engine
    "ActivationConditionEngine",
    "ActivationConfig",
    "ActivationScore",
    "get_activation_engine",
    "reset_activation_engine",
    "set_activation_engine",
    # Stigmergic Memory
    "CompositionStats",
    "StigmergicMemory",
    "UsageStats",
    "compute_context_hash",
    "get_stigmergic_memory",
    "reset_stigmergic_memory",
    "set_stigmergic_memory",
    # JIT Injector
    "InjectionConfig",
    "JITInjector",
    "SkillContentReader",
    "get_jit_injector",
    "reset_jit_injector",
    "set_jit_injector",
    # Bootstrap
    "bootstrap_skills",
    "bootstrap_skills_from_routing",
    "categorize_skill",
    "extract_activation_conditions",
    "load_skill_from_file",
    # Node
    "EvolveResponse",
    "GotchasRequest",
    "GotchasResponse",
    "InjectRendering",
    "InjectRequest",
    "InjectResponse",
    "RecordOutcomeRequest",
    "RecordOutcomeResponse",
    "SearchRequest",
    "SearchResponse",
    "SkillManifestRendering",
    "SkillManifestResponse",
    "SkillNode",
]
