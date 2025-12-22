# AGENTESE Protocol

> *The universal API: verb-first ontology for agent-world interaction.*

---

## protocols.agentese.__init__

## __init__

```python
module __init__
```

**AGENTESE:** `The`

AGENTESE: The Verb-First Ontology

---

## create_brain_logos

```python
def create_brain_logos(dimension: int=384, embedder_type: str='auto') -> 'Logos'
```

Create a Logos instance with basic memory support.

---

## protocols.agentese._archive.deprecation_v1

## deprecation_v1

```python
module deprecation_v1
```

AGENTESE Deprecation Infrastructure

---

## APIVersion

```python
class APIVersion(Enum)
```

AGENTESE API versions.

---

## UsageRecord

```python
class UsageRecord
```

Record of an API usage event.

---

## UsageTracker

```python
class UsageTracker
```

Tracks v1 vs v3 API usage for migration metrics.

---

## get_usage_tracker

```python
def get_usage_tracker() -> UsageTracker
```

Get or create the global usage tracker.

---

## track_api_version

```python
def track_api_version(symbol: str, version: APIVersion) -> None
```

Track usage of an API symbol.

---

## DeprecationWarning_

```python
class DeprecationWarning_(UserWarning)
```

Custom warning for AGENTESE deprecations.

---

## deprecated

```python
def deprecated(message: str, *, removal_version: str='v4', alternative: str | None=None) -> Callable[[F], F]
```

Mark a function or method as deprecated.

---

## v1_usage_warning

```python
def v1_usage_warning(symbol: str, alternative: str) -> None
```

Emit a deprecation warning for v1 symbol usage.

---

## create_deprecation_wrapper

```python
def create_deprecation_wrapper(cls: type, message: str, *, removal_version: str='v4') -> type
```

Create a wrapper class that emits deprecation warnings on instantiation.

---

## get_migration_alternative

```python
def get_migration_alternative(symbol: str) -> str | None
```

Get the v3 alternative for a v1 symbol.

---

## is_deprecated_symbol

```python
def is_deprecated_symbol(symbol: str) -> bool
```

Check if a symbol is marked for deprecation.

---

## get_v3_public_api

```python
def get_v3_public_api() -> frozenset[str]
```

Get the set of symbols in the v3 public API.

---

## count_exports

```python
def count_exports() -> tuple[int, int]
```

Count current vs target exports.

---

## enable

```python
def enable(self) -> None
```

Enable usage tracking.

---

## disable

```python
def disable(self) -> None
```

Disable usage tracking.

---

## record_usage

```python
def record_usage(self, symbol: str, version: APIVersion, *, caller_file: str | None=None, caller_line: int | None=None) -> None
```

Record a usage event.

---

## migration_progress

```python
def migration_progress(self) -> dict[str, Any]
```

Calculate migration progress metrics.

---

## clear

```python
def clear(self) -> None
```

Clear all usage data.

---

## protocols.agentese.adapter

## adapter

```python
module adapter
```

AGENTESE Phase 8: Natural Language → AGENTESE Adapter

---

## TranslationResult

```python
class TranslationResult
```

Result of translating natural language to AGENTESE.

---

## TranslationError

```python
class TranslationError(AgentesError)
```

Raised when translation fails.

---

## Translator

```python
class Translator(Protocol)
```

Protocol for translation strategies.

---

## AsyncTranslator

```python
class AsyncTranslator(Protocol)
```

Protocol for async translation strategies (LLM).

---

## PatternTranslator

```python
class PatternTranslator
```

Rule-based pattern translator.

### Examples
```python
>>> translator = PatternTranslator()
```
```python
>>> result = translator.translate("show me the house")
```
```python
>>> result.path
```
```python
>>> result.confidence
```

---

## LLMProtocol

```python
class LLMProtocol(Protocol)
```

Protocol for LLM invocation.

---

## build_translation_prompt

```python
def build_translation_prompt(input: str, examples: list[tuple[str, str]] | None=None, context: dict[str, Any] | None=None) -> str
```

Build the few-shot prompt for LLM translation.

---

## LLMTranslator

```python
class LLMTranslator
```

LLM-based translator for complex queries.

### Examples
```python
>>> translator = LLMTranslator(llm=my_llm)
```
```python
>>> result = await translator.translate("Check if the authentication system is healthy")
```
```python
>>> result.path
```

---

## AgentesAdapter

```python
class AgentesAdapter
```

Unified adapter for natural language → AGENTESE translation.

### Examples
```python
>>> adapter = create_adapter(wired_logos)
```
```python
>>> result = await adapter.execute("show me the house", observer)
```
```python
>>> # Automatically translated to world.house.manifest and invoked
```

---

## create_adapter

```python
def create_adapter(logos: Any=None, llm: LLMProtocol | None=None, min_confidence: float=0.5, use_llm_fallback: bool=True) -> AgentesAdapter
```

Create an AGENTESE adapter.

---

## create_pattern_translator

```python
def create_pattern_translator(extra_patterns: list[tuple[str, str, str, float]] | None=None) -> PatternTranslator
```

Create a pattern translator with optional extra patterns.

---

## translate

```python
def translate(self, input: str, context: dict[str, Any] | None=None) -> TranslationResult | None
```

Translate natural language to AGENTESE.

---

## translate

```python
async def translate(self, input: str, context: dict[str, Any] | None=None) -> TranslationResult | None
```

Async translation (for LLM calls).

---

## translate

```python
def translate(self, input: str, context: dict[str, Any] | None=None) -> TranslationResult | None
```

Translate using pattern matching.

---

## add_pattern

```python
def add_pattern(self, pattern: str, template: str, aspect: str='manifest', confidence: float=0.8) -> None
```

Add a custom translation pattern.

---

## complete

```python
async def complete(self, prompt: str) -> str
```

Complete a prompt and return the response.

---

## translate

```python
async def translate(self, input: str, context: dict[str, Any] | None=None) -> TranslationResult | None
```

Translate using LLM.

---

## add_example

```python
def add_example(self, natural_language: str, agentese_path: str) -> None
```

Add a training example.

---

## translate

```python
async def translate(self, input: str, context: dict[str, Any] | None=None) -> TranslationResult
```

Translate natural language to AGENTESE.

---

## execute

```python
async def execute(self, input: str, observer: 'Umwelt[Any, Any]', context: dict[str, Any] | None=None, **kwargs: Any) -> Any
```

Translate and execute in one step.

---

## protocols.agentese.affordances

## affordances

```python
module affordances
```

AGENTESE Phase 3: Polymorphic Affordances

---

## AspectCategory

```python
class AspectCategory(Enum)
```

Categories of aspects from the AGENTESE spec (Part IV, §4.2).

---

## Aspect

```python
class Aspect
```

Definition of a standard AGENTESE aspect.

---

## Effect

```python
class Effect(Enum)
```

Declared side-effects for aspects (v3 API).

---

## DeclaredEffect

```python
class DeclaredEffect
```

An effect bound to a specific resource.

---

## AspectMetadata

```python
class AspectMetadata
```

Runtime metadata attached to aspect methods by @aspect decorator.

---

## aspect

```python
def aspect(category: AspectCategory, effects: list[DeclaredEffect | Effect] | None=None, requires_archetype: tuple[str, ...]=(), idempotent: bool=False, description: str='', examples: list[str] | None=None, see_also: list[str] | None=None, since_version: str='1.0', help: str='', long_help: str='', streaming: bool=False, interactive: bool=False, budget_estimate: str | None=None, required_capability: str | None=None) -> Callable[[Callable[P, T]], Callable[P, T]]
```

Decorator to mark a method as an AGENTESE aspect (v3.3 API).

---

## get_aspect_metadata

```python
def get_aspect_metadata(func: Callable[..., Any]) -> AspectMetadata | None
```

Get aspect metadata from a decorated function.

---

## is_aspect

```python
def is_aspect(func: Callable[..., Any]) -> bool
```

Check if a function is decorated with @aspect.

---

## AffordanceRegistry

```python
class AffordanceRegistry
```

Central registry for archetype → affordances mappings.

### Examples
```python
>>> registry = AffordanceRegistry()
```
```python
>>> registry.get_affordances("architect")
```
```python
>>> registry.register("senior_architect", ("architect",), ("manage",))
```
```python
>>> registry.get_affordances("senior_architect")
```

---

## AffordanceMatcher

```python
class AffordanceMatcher(Protocol)
```

Protocol for affordance matchers.

---

## StandardAffordanceMatcher

```python
class StandardAffordanceMatcher
```

Standard affordance matcher using the registry.

---

## CapabilityAffordanceMatcher

```python
class CapabilityAffordanceMatcher
```

Capability-based affordance matcher.

---

## ArchetypeDNA

```python
class ArchetypeDNA
```

DNA type for archetype-based agent configuration.

### Examples
```python
>>> dna = ArchetypeDNA(
```
```python
>>> adapter = UmweltAdapter()
```
```python
>>> affordances = adapter.get_affordances(umwelt)
```

---

## UmweltAdapter

```python
class UmweltAdapter
```

Adapter for extracting affordance-relevant information from Umwelt.

### Examples
```python
>>> adapter = UmweltAdapter()
```
```python
>>> meta = adapter.extract_meta(umwelt)
```
```python
>>> affordances = adapter.get_affordances(umwelt)
```

---

## ContextAffordanceSet

```python
class ContextAffordanceSet
```

Affordance set for a specific context (world, self, concept, void, time).

---

## create_affordance_registry

```python
def create_affordance_registry() -> AffordanceRegistry
```

Create a standard affordance registry with all archetypes.

---

## create_umwelt_adapter

```python
def create_umwelt_adapter(registry: AffordanceRegistry | None=None) -> UmweltAdapter
```

Create a UmweltAdapter with optional custom registry.

---

## get_context_affordance_set

```python
def get_context_affordance_set(context: str) -> ContextAffordanceSet
```

Get the pre-configured affordance set for a context.

---

## ChattyConfig

```python
class ChattyConfig
```

Configuration for the @chatty decorator.

---

## chatty

```python
def chatty(context_window: int=8000, context_strategy: str='summarize', persist_history: bool=True, memory_key: str | None=None, inject_memories: bool=True, memory_recall_limit: int=5, entropy_budget: float=1.0, entropy_decay_per_turn: float=0.02) -> Callable[[type[T]], type[T]]
```

Decorator to mark a LogosNode class as chatty.

### Examples
```python
>>> @chatty(
```
```python
>>> context_window=8000,
```
```python
>>> context_strategy="summarize",
```
```python
>>> persist_history=True,
```
```python
>>> )
```

---

## is_chatty

```python
def is_chatty(node: Any) -> bool
```

Check if a node (or its class) is decorated with @chatty.

---

## get_chatty_config

```python
def get_chatty_config(node: Any) -> ChattyConfig | None
```

Get the ChattyConfig from a @chatty decorated node.

---

## to_chat_config

```python
def to_chat_config(chatty_config: ChattyConfig) -> 'ChatConfig'
```

Convert ChattyConfig to a full ChatConfig for session creation.

---

## __call__

```python
def __call__(self, resource: str) -> 'DeclaredEffect'
```

Create a declared effect with resource binding.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize with standard archetypes.

---

## get_affordances

```python
def get_affordances(self, archetype: str) -> list[str]
```

Get full affordance list for an archetype.

---

## has_affordance

```python
def has_affordance(self, archetype: str, aspect: str) -> bool
```

Check if an archetype has access to an aspect.

---

## register

```python
def register(self, archetype: str, parents: tuple[str, ...]=(), additional: tuple[str, ...]=()) -> None
```

Register a new archetype with inheritance.

---

## extend

```python
def extend(self, archetype: str, affordances: tuple[str, ...]) -> None
```

Add affordances to an existing archetype.

---

## list_archetypes

```python
def list_archetypes(self) -> list[str]
```

List all registered archetypes.

---

## get_aspect_info

```python
def get_aspect_info(self, aspect: str) -> Aspect | None
```

Get full aspect information.

---

## matches

```python
def matches(self, archetype: str, aspect: str) -> bool
```

Check if archetype can access aspect.

---

## matches

```python
def matches(self, archetype: str, aspect: str) -> bool
```

Check if archetype can access aspect.

---

## matches

```python
def matches(self, archetype: str, aspect: str, capabilities: tuple[str, ...]=()) -> bool
```

Check if archetype + capabilities can access aspect.

---

## germinate

```python
def germinate(cls, **kwargs: Any) -> 'ArchetypeDNA'
```

Create validated ArchetypeDNA.

---

## extract_meta

```python
def extract_meta(self, umwelt: 'Umwelt[Any, Any]') -> 'AgentMeta'
```

Extract AgentMeta from Umwelt's DNA.

---

## get_affordances

```python
def get_affordances(self, umwelt: 'Umwelt[Any, Any]') -> list[str]
```

Get full affordance list for an Umwelt.

---

## can_invoke

```python
def can_invoke(self, umwelt: 'Umwelt[Any, Any]', aspect: str) -> bool
```

Check if the Umwelt's observer can invoke an aspect.

---

## filter_affordances

```python
def filter_affordances(self, umwelt: 'Umwelt[Any, Any]', available: list[str]) -> list[str]
```

Filter a list of affordances to those accessible by the observer.

---

## get_for_archetype

```python
def get_for_archetype(self, archetype: str, holon: str | None=None) -> list[str]
```

Get affordances for an archetype in this context.

---

## protocols.agentese.aliases

## aliases

```python
module aliases
```

AGENTESE Path Aliases

---

## AliasError

```python
class AliasError(Exception)
```

Base exception for alias errors.

---

## AliasShadowError

```python
class AliasShadowError(AliasError)
```

Attempted to shadow a reserved context name.

---

## AliasRecursionError

```python
class AliasRecursionError(AliasError)
```

Attempted recursive alias definition.

---

## AliasNotFoundError

```python
class AliasNotFoundError(AliasError)
```

Alias not found in registry.

---

## AliasRegistry

```python
class AliasRegistry
```

Registry for AGENTESE path aliases.

---

## create_standard_aliases

```python
def create_standard_aliases() -> dict[str, str]
```

Get standard AGENTESE aliases.

---

## create_alias_registry

```python
def create_alias_registry(*, persistence_path: Path | str | None=None, include_standard: bool=True, load_from_disk: bool=True) -> AliasRegistry
```

Create an alias registry with optional standard aliases.

---

## get_default_aliases_path

```python
def get_default_aliases_path() -> Path
```

Get the default path for aliases.yaml.

---

## add_alias_methods_to_logos

```python
def add_alias_methods_to_logos(logos_cls: type) -> None
```

Add alias methods to Logos class.

---

## expand_aliases

```python
def expand_aliases(path: str, registry: AliasRegistry | None) -> str
```

Expand aliases in a path.

---

## register

```python
def register(self, alias: str, target: str) -> None
```

Register a path alias.

---

## unregister

```python
def unregister(self, alias: str) -> None
```

Remove a path alias.

---

## expand

```python
def expand(self, path: str) -> str
```

Expand aliases in a path.

---

## get

```python
def get(self, alias: str) -> str | None
```

Get the target for an alias, or None if not found.

---

## list_aliases

```python
def list_aliases(self) -> dict[str, str]
```

Get all registered aliases.

---

## has_alias

```python
def has_alias(self, alias: str) -> bool
```

Check if an alias is registered.

---

## clear

```python
def clear(self) -> None
```

Clear all aliases.

---

## __len__

```python
def __len__(self) -> int
```

Number of registered aliases.

---

## __contains__

```python
def __contains__(self, alias: str) -> bool
```

Check if alias is registered.

---

## set_persistence_path

```python
def set_persistence_path(self, path: Path | str) -> None
```

Set the path for persistence.

---

## save

```python
def save(self) -> None
```

Save aliases to YAML file.

---

## load

```python
def load(self) -> None
```

Load aliases from YAML file.

---

## alias_method

```python
def alias_method(self: Any, name: str, target: str) -> None
```

Register a path alias.

---

## unalias_method

```python
def unalias_method(self: Any, name: str) -> None
```

Remove a path alias.

---

## list_aliases_method

```python
def list_aliases_method(self: Any) -> dict[str, str]
```

Get all registered aliases.

---

## protocols.agentese.container

## container

```python
module container
```

**AGENTESE:** `protocols.agentese.container`

AGENTESE Service Container.

### Examples
```python
>>> @node("self.memory", dependencies=("brain_crystal", "embedder"))
```
```python
>>> class BrainNode(BaseLogosNode):
```
```python
>>> def __init__(self, crystal: BrainCrystal, embedder: Embedder):
```
```python
>>> self._crystal = crystal
```
```python
>>> self._embedder = embedder
```

### Things to Know

ℹ️ Dependencies are REQUIRED by default (no default in __init__). Missing required deps raise DependencyNotFoundError immediately. To make a dependency optional, add a default: `brain: Brain | None = None`
  - *Verified in: `test_container.py::TestNodeCreation::test_required_deps_fail_immediately`*

ℹ️ Optional dependencies are skipped gracefully if not registered. The node's __init__ default is used. This is intentional for graceful degradation (e.g., SoulNode without LLM).
  - *Verified in: `test_container.py::TestNodeCreation::test_optional_deps_skipped_gracefully`*

ℹ️ Singleton is the DEFAULT. Every register() call creates a cached singleton unless singleton=False is explicitly passed. This means provider functions are called ONCE and the result is reused forever.
  - *Verified in: `test_container.py::TestDependencyResolution::test_singleton_caching`*

ℹ️ Dependency names are CASE-SENSITIVE and EXACT-MATCH. If your @node declares dependencies=("brain_Crystal",) but you register "brain_crystal", the dependency silently fails to resolve.
  - *Verified in: `test_container.py::TestProviderRegistration::test_has_unregistered`*

---

## DependencyNotFoundError

```python
class DependencyNotFoundError(Exception)
```

Raised when a required dependency is not registered in the container.

---

## ProviderEntry

```python
class ProviderEntry
```

Entry in the provider registry.

---

## ServiceContainer

```python
class ServiceContainer
```

Dependency injection container for AGENTESE service nodes.

---

## get_container

```python
def get_container() -> ServiceContainer
```

Get the global service container.

---

## reset_container

```python
def reset_container() -> None
```

Reset the global container (for testing).

---

## create_container

```python
def create_container() -> ServiceContainer
```

Create a new service container.

---

## register

```python
def register(self, name: str, provider: Provider, *, singleton: bool=True, lazy: bool=True) -> None
```

Register a dependency provider.

---

## register_value

```python
def register_value(self, name: str, value: Any) -> None
```

Register a pre-instantiated value as a singleton.

---

## has

```python
def has(self, name: str) -> bool
```

Check if a provider is registered.

---

## resolve

```python
async def resolve(self, name: str) -> Any
```

Resolve a dependency by name.

---

## create_node

```python
async def create_node(self, cls: type[T], meta: 'NodeMetadata | None'=None) -> T
```

Create a node instance with injected dependencies.

---

## list_providers

```python
def list_providers(self) -> list[str]
```

List all registered provider names.

---

## clear

```python
def clear(self) -> None
```

Clear all providers and cache (for testing).

---

## clear_cache

```python
def clear_cache(self) -> None
```

Clear cached singletons but keep providers.

---

## stats

```python
def stats(self) -> dict[str, Any]
```

Get container statistics.

---

## protocols.agentese.contexts.__init__

## __init__

```python
module __init__
```

AGENTESE Context Resolvers

---

## create_context_resolvers

```python
def create_context_resolvers(registry: Any=None, narrator: Any=None, d_gent: Any=None, b_gent: Any=None, grammarian: Any=None, entropy_budget: float=100.0, capital_ledger: Any=None, purgatory: Any=None, substrate: Any=None, compactor: Any=None, router: Any=None, memory_crystal: Any=None, pheromone_field: Any=None, inference_agent: Any=None, cartographer: Any=None, embedder: Any=None, vgent: Any=None) -> dict[str, Any]
```

Create all five context resolvers with unified configuration.

---

## protocols.agentese.contexts.agents

## agents

```python
module agents
```

AGENTESE Agent Discovery Context

---

## AgentNode

```python
class AgentNode(BaseLogosNode)
```

A node representing an agent in the world.agent.* context.

---

## AgentListNode

```python
class AgentListNode(BaseLogosNode)
```

A node for world.agent.list - lists all available agents.

---

## AgentContextResolver

```python
class AgentContextResolver
```

Resolver for world.agent.* paths.

---

## create_agent_resolver

```python
def create_agent_resolver(registry: dict[str, dict[str, Any]] | None=None) -> AgentContextResolver
```

Create an AgentContextResolver with optional custom registry.

---

## create_agent_node

```python
def create_agent_node(letter: str) -> AgentNode
```

Create an AgentNode for a specific agent letter.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Manifest agent information based on observer's archetype.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Manifest the list of all agents.

---

## resolve

```python
def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode
```

Resolve world.agent.* paths.

---

## list_agents

```python
def list_agents(self) -> list[str]
```

List all available agent letters.

---

## protocols.agentese.contexts.compression

## compression

```python
module compression
```

**AGENTESE:** `concept.`

AGENTESE Compression Context: MDL-Compliant Quality Metrics

---

## Regenerator

```python
class Regenerator(Protocol)
```

Protocol for regenerating artifacts from compressed specs.

---

## DistanceFunction

```python
class DistanceFunction(Protocol)
```

Protocol for computing semantic distance between artifacts.

---

## CompressionQuality

```python
class CompressionQuality
```

MDL-compliant compression quality measurement.

---

## validate_compression

```python
async def validate_compression(spec: str, artifact: Any, regenerator: 'Callable[[str], Awaitable[Any]]', distance: 'Callable[[Any, Any], Awaitable[float]] | None'=None) -> CompressionQuality
```

MDL-compliant compression quality validation.

---

## validate_compression_sync

```python
def validate_compression_sync(spec: str, artifact: Any, regenerated: Any, distance: 'Callable[[Any, Any], float] | None'=None) -> CompressionQuality
```

Synchronous MDL validation when regenerated artifact is pre-computed.

---

## CompressionValidator

```python
class CompressionValidator
```

Reusable compression validator with configurable thresholds.

---

## compress_with_validation

```python
async def compress_with_validation(artifact: Any, compressor: 'Callable[[Any], Awaitable[str]]', regenerator: 'Callable[[str], Awaitable[Any]]', observer: 'Umwelt[Any, Any]', validator: CompressionValidator | None=None) -> tuple[str, CompressionQuality]
```

Compress artifact with MDL validation.

---

## __call__

```python
async def __call__(self, spec: str) -> Any
```

Regenerate artifact from spec.

---

## __call__

```python
async def __call__(self, original: Any, regenerated: Any) -> float
```

Compute distance between original and regenerated artifacts.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate quality metrics are in valid ranges.

---

## create

```python
def create(cls, spec: str, artifact: Any, reconstruction_error: float) -> 'CompressionQuality'
```

Create CompressionQuality with computed metrics.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary representation.

---

## to_text

```python
def to_text(self) -> str
```

Convert to human-readable text.

---

## is_valid

```python
def is_valid(self) -> bool
```

Check if compression is valid (positive quality, low error).

---

## is_high_quality

```python
def is_high_quality(self) -> bool
```

Check if compression is high quality (good ratio, very low error).

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate configuration.

---

## validate

```python
async def validate(self, spec: str, artifact: Any, regenerator: 'Callable[[str], Awaitable[Any]]') -> CompressionQuality
```

Validate compression quality.

---

## is_acceptable

```python
def is_acceptable(self, quality: CompressionQuality) -> bool
```

Check if compression quality meets thresholds.

---

## rejection_reason

```python
def rejection_reason(self, quality: CompressionQuality) -> str | None
```

Get rejection reason if quality is unacceptable, None if acceptable.

---

## protocols.agentese.contexts.concept

## concept

```python
module concept
```

AGENTESE Concept Context Resolver

---

## ConceptNode

```python
class ConceptNode(BaseLogosNode)
```

A node in the concept.* context.

---

## ConceptContextResolver

```python
class ConceptContextResolver
```

Resolver for concept.* context.

---

## create_concept_resolver

```python
def create_concept_resolver(registry: Any=None, grammarian: Any=None) -> ConceptContextResolver
```

Create a ConceptContextResolver with optional integrations.

---

## create_concept_node

```python
def create_concept_node(name: str, definition: str='', domain: str='general', examples: list[str] | None=None, related: list[str] | None=None) -> ConceptNode
```

Create a ConceptNode with standard configuration.

---

## define_concept

```python
async def define_concept(logos: 'Logos', handle: str, observer: 'Umwelt[Any, Any]', spec: str, extends: list[str], subsumes: list[str] | None=None, justification: str='') -> ConceptNode
```

**AGENTESE:** `concept.`

Create a new concept with required lineage.

---

## get_concept_tree

```python
def get_concept_tree(root_handle: str='concept', max_depth: int=10) -> dict[str, Any]
```

Get the concept tree starting from a root.

---

## render_concept_lattice

```python
def render_concept_lattice(root_handle: str='concept', max_depth: int=10) -> str
```

Render the concept lattice as ASCII tree.

---

## extends

```python
def extends(self) -> list[str]
```

Get parent concepts from lineage.

---

## subsumes

```python
def subsumes(self) -> list[str]
```

Get child concepts from lineage.

---

## has_lineage

```python
def has_lineage(self) -> bool
```

Check if this concept has lineage information.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Perceive the concept.

---

## resolve

```python
def resolve(self, holon: str, rest: list[str]) -> ConceptNode
```

Resolve a concept.* path to a ConceptNode.

---

## register

```python
def register(self, handle: str, node: ConceptNode) -> None
```

Register a concept in the cache.

---

## list_handles

```python
def list_handles(self, prefix: str='concept.') -> list[str]
```

List cached handles.

---

## protocols.agentese.contexts.concept_blend

## concept_blend

```python
module concept_blend
```

AGENTESE Conceptual Blending Context

---

## BlendResult

```python
class BlendResult
```

Result of conceptual blending operation.

---

## extract_tokens

```python
def extract_tokens(text: str) -> set[str]
```

Extract conceptual tokens from text.

---

## extract_relations

```python
def extract_relations(concept: str) -> set[str]
```

Extract structural relations from a concept description.

---

## find_generic_space

```python
def find_generic_space(relations_a: set[str], relations_b: set[str]) -> list[str]
```

Find the generic space: shared abstract structure between two concepts.

---

## identify_emergent_features

```python
def identify_emergent_features(blend_description: str, relations_a: set[str], relations_b: set[str]) -> list[str]
```

Identify emergent features in the blend.

---

## compute_alignment_score

```python
def compute_alignment_score(generic_space: list[str], relations_a: set[str], relations_b: set[str]) -> float
```

Compute alignment score: quality of structural isomorphism.

---

## forge_blend

```python
def forge_blend(concept_a: str, concept_b: str) -> BlendResult
```

Create a conceptual blend from two input spaces.

---

## BlendNode

```python
class BlendNode(BaseLogosNode)
```

**AGENTESE:** `concept.blend.`

concept.blend - Conceptual Blending operations.

---

## create_blend_node

```python
def create_blend_node() -> BlendNode
```

Create a BlendNode with default configuration.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary representation.

---

## to_text

```python
def to_text(self) -> str
```

Convert to human-readable text.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View blending capability.

---

## protocols.agentese.contexts.concept_intent

## concept_intent

```python
module concept_intent
```

AGENTESE Concept Intent Context: Typed Task Decomposition.

---

## IntentNode

```python
class IntentNode(BaseLogosNode)
```

**AGENTESE:** `concept.intent.`

concept.intent - Typed task decomposition.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Show intent trees.

---

## protocols.agentese.contexts.concept_principles

## concept_principles

```python
module concept_principles
```

concept.principles AGENTESE Node

---

## PrinciplesNode

```python
class PrinciplesNode(BaseLogosNode)
```

AGENTESE node for principle consumption.

---

## get_principles_node

```python
def get_principles_node() -> PrinciplesNode
```

Get a PrinciplesNode instance.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize healer and teacher with loader.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any] | Observer', stance: str | None=None, task: str | None=None) -> Renderable
```

Collapse principles to observer's stance.

---

## constitution

```python
async def constitution(self, observer: 'Umwelt[Any, Any] | Observer') -> Renderable
```

Return the Seven Immutable Principles.

---

## meta

```python
async def meta(self, observer: 'Umwelt[Any, Any] | Observer', section: str | None=None) -> Renderable
```

Return meta-principles.

---

## operational

```python
async def operational(self, observer: 'Umwelt[Any, Any] | Observer') -> Renderable
```

Return operational principles.

---

## ad

```python
async def ad(self, observer: 'Umwelt[Any, Any] | Observer', ad_id: int | None=None, category: str | None=None) -> Renderable
```

Load architectural decisions.

---

## check

```python
async def check(self, observer: 'Umwelt[Any, Any] | Observer', target: str, principles: list[int] | None=None, context: str | None=None) -> Renderable
```

Check a target against principles (Krisis stance).

---

## teach

```python
async def teach(self, observer: 'Umwelt[Any, Any] | Observer', principle: int | str | None=None, depth: Literal['overview', 'examples', 'exercises']='overview') -> Renderable
```

Get teaching content for principles.

---

## heal

```python
async def heal(self, observer: 'Umwelt[Any, Any] | Observer', violation: int | str, context: str | None=None) -> Renderable
```

Get healing prescription for a violation (Therapeia stance).

---

## protocols.agentese.contexts.concept_scope

## concept_scope

```python
module concept_scope
```

AGENTESE Concept Scope Context: Explicit Context Contract.

---

## ScopeNode

```python
class ScopeNode(BaseLogosNode)
```

**AGENTESE:** `concept.scope.`

concept.scope - Explicit context contracts.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Show active scopes.

---

## protocols.agentese.contexts.conductor_contracts

## conductor_contracts

```python
module conductor_contracts
```

**AGENTESE:** `self.conductor.`

AGENTESE Conductor Contracts: Type-safe request/response definitions.

---

## ConductorManifestResponse

```python
class ConductorManifestResponse
```

Response for conductor manifest aspect.

---

## SnapshotRequest

```python
class SnapshotRequest
```

Request for snapshot aspect.

---

## SnapshotResponse

```python
class SnapshotResponse
```

Response for snapshot aspect - immutable window state.

---

## HistoryRequest

```python
class HistoryRequest
```

Request for history aspect.

---

## MessageItem

```python
class MessageItem
```

A single message in conversation history.

---

## HistoryResponse

```python
class HistoryResponse
```

Response for history aspect - bounded conversation messages.

---

## SummaryGetRequest

```python
class SummaryGetRequest
```

Request for getting conversation summary.

---

## SummaryGetResponse

```python
class SummaryGetResponse
```

Response for getting conversation summary.

---

## SummarySetRequest

```python
class SummarySetRequest
```

Request for setting conversation summary.

---

## SummarySetResponse

```python
class SummarySetResponse
```

Response for setting conversation summary.

---

## ResetRequest

```python
class ResetRequest
```

Request for resetting conversation window.

---

## ResetResponse

```python
class ResetResponse
```

Response for reset aspect.

---

## SessionsListRequest

```python
class SessionsListRequest
```

Request for listing sessions.

---

## SessionInfo

```python
class SessionInfo
```

Information about a single session.

---

## SessionsListResponse

```python
class SessionsListResponse
```

Response for sessions list aspect.

---

## ConfigRequest

```python
class ConfigRequest
```

Request for getting window configuration.

---

## ConfigResponse

```python
class ConfigResponse
```

Response for config aspect - window configuration.

---

## FluxStatusRequest

```python
class FluxStatusRequest
```

Request for flux status.

---

## FluxStatusResponse

```python
class FluxStatusResponse
```

Response for flux status - event integration state.

---

## FluxStartRequest

```python
class FluxStartRequest
```

Request to start flux event integration.

---

## FluxStartResponse

```python
class FluxStartResponse
```

Response for starting flux.

---

## FluxStopRequest

```python
class FluxStopRequest
```

Request to stop flux event integration.

---

## FluxStopResponse

```python
class FluxStopResponse
```

Response for stopping flux.

---

## protocols.agentese.contexts.crown_jewels

## crown_jewels

```python
module crown_jewels
```

Crown Jewels Path Registry

---

## CrownJewelRegistry

```python
class CrownJewelRegistry
```

Registry for Crown Jewel AGENTESE paths.

---

## register_crown_jewel_paths

```python
def register_crown_jewel_paths(logos: 'Logos') -> None
```

Register Crown Jewel paths with a Logos instance.

---

## get_crown_jewel_registry

```python
def get_crown_jewel_registry(logos: 'Logos') -> CrownJewelRegistry | None
```

Get the Crown Jewel registry from a Logos instance.

---

## list_self_time_paths

```python
def list_self_time_paths() -> dict[str, list[str]]
```

List all self.* and time.* Crown paths.

---

## list_paths

```python
def list_paths(self, jewel: str | None=None) -> list[str]
```

List registered paths, optionally filtered by jewel.

---

## get_path_info

```python
def get_path_info(self, path: str) -> dict[str, Any] | None
```

Get path metadata if registered.

---

## is_registered

```python
def is_registered(self, path: str) -> bool
```

Check if path is registered.

---

## get_aspect

```python
def get_aspect(self, path: str) -> str | None
```

Get the aspect for a path.

---

## get_effects

```python
def get_effects(self, path: str) -> list[str]
```

Get effects for a path.

---

## protocols.agentese.contexts.design

## design

```python
module design
```

AGENTESE Design Context Resolver

---

## LayoutDesignNode

```python
class LayoutDesignNode(BaseLogosNode)
```

concept.design.layout - Layout composition grammar.

---

## ContentDesignNode

```python
class ContentDesignNode(BaseLogosNode)
```

concept.design.content - Content degradation grammar.

---

## MotionDesignNode

```python
class MotionDesignNode(BaseLogosNode)
```

concept.design.motion - Animation composition grammar.

---

## DesignOperadNode

```python
class DesignOperadNode(BaseLogosNode)
```

concept.design.operad - Unified design operad.

---

## DesignContextNode

```python
class DesignContextNode(BaseLogosNode)
```

concept.design - Design Language System root.

---

## DesignContextResolver

```python
class DesignContextResolver
```

Resolver for design context paths.

---

## create_design_resolver

```python
def create_design_resolver() -> DesignContextResolver
```

Create a design context resolver.

---

## create_design_node

```python
def create_design_node() -> DesignContextNode
```

Create a design context node.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Manifest layout operad summary.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Manifest content operad summary.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Manifest motion operad summary.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Manifest unified design operad summary.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Manifest design language overview.

---

## resolve

```python
def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode | None
```

Resolve a design path to its node.

---

## protocols.agentese.contexts.presence_contracts

## presence_contracts

```python
module presence_contracts
```

Presence Contracts: Type definitions for self.presence operations.

---

## PresenceManifestResponse

```python
class PresenceManifestResponse
```

Response for presence manifest aspect.

---

## CursorGetRequest

```python
class CursorGetRequest
```

Request to get a specific cursor.

---

## CursorGetResponse

```python
class CursorGetResponse
```

Response for cursor get.

---

## CursorUpdateRequest

```python
class CursorUpdateRequest
```

Request to update cursor state.

---

## CursorUpdateResponse

```python
class CursorUpdateResponse
```

Response for cursor update.

---

## JoinRequest

```python
class JoinRequest
```

Request to join presence channel.

---

## JoinResponse

```python
class JoinResponse
```

Response for join request.

---

## LeaveRequest

```python
class LeaveRequest
```

Request to leave presence channel.

---

## LeaveResponse

```python
class LeaveResponse
```

Response for leave request.

---

## SnapshotResponse

```python
class SnapshotResponse
```

Response for presence snapshot.

---

## CircadianResponse

```python
class CircadianResponse
```

Response for circadian phase info.

---

## StatesResponse

```python
class StatesResponse
```

Response listing all cursor states.

---

## DemoRequest

```python
class DemoRequest
```

Request to start/stop demo mode with simulated cursors.

---

## DemoResponse

```python
class DemoResponse
```

Response for demo mode.

---

## protocols.agentese.contexts.projection

## projection

```python
module projection
```

AGENTESE Projection Context Resolver

---

## Density

```python
class Density(Enum)
```

Density levels matching spec/protocols/projection.md:

---

## Modality

```python
class Modality(Enum)
```

Interaction modality - how the observer interacts with the UI.

---

## Bandwidth

```python
class Bandwidth(Enum)
```

Network bandwidth capacity of the observer.

---

## PhysicalCapacity

```python
class PhysicalCapacity
```

Physical constraints of the observer's device.

---

## LayoutUmwelt

```python
class LayoutUmwelt
```

Umwelt extension for layout-aware perception.

---

## LayoutNode

```python
class LayoutNode(BaseLogosNode)
```

self.layout - Observer's layout context.

---

## PanelNode

```python
class PanelNode(BaseLogosNode)
```

world.panel - Layout-aware panel projection.

---

## ActionsNode

```python
class ActionsNode(BaseLogosNode)
```

world.actions - Layout-aware actions projection.

---

## SplitNode

```python
class SplitNode(BaseLogosNode)
```

world.split - Layout-aware split projection.

---

## ProjectionContextResolver

```python
class ProjectionContextResolver
```

Resolver for projection context paths.

---

## create_projection_resolver

```python
def create_projection_resolver(capacity: PhysicalCapacity | None=None) -> ProjectionContextResolver
```

Create a projection context resolver.

---

## create_layout_node

```python
def create_layout_node(capacity: PhysicalCapacity | None=None) -> LayoutNode
```

Create a layout node with optional capacity.

---

## create_panel_node

```python
def create_panel_node() -> PanelNode
```

Create a panel node.

---

## create_actions_node

```python
def create_actions_node() -> ActionsNode
```

Create an actions node.

---

## create_split_node

```python
def create_split_node() -> SplitNode
```

Create a split node.

---

## from_viewport

```python
def from_viewport(cls, width: int, height: int | None=None) -> PhysicalCapacity
```

Create PhysicalCapacity from viewport dimensions.

---

## mobile

```python
def mobile(cls, observer_id: str='mobile_user') -> LayoutUmwelt
```

Create a mobile umwelt (compact density, touch modality).

---

## desktop

```python
def desktop(cls, observer_id: str='desktop_user') -> LayoutUmwelt
```

Create a desktop umwelt (spacious density, pointer modality).

---

## manifest

```python
async def manifest(self, observer: Umwelt[Any, Any]) -> Renderable
```

Manifest the current layout context.

---

## manifest

```python
async def manifest(self, observer: Umwelt[Any, Any]) -> Renderable
```

Manifest panel projection based on observer's capacity.

---

## manifest

```python
async def manifest(self, observer: Umwelt[Any, Any]) -> Renderable
```

Manifest actions projection based on observer's capacity.

---

## manifest

```python
async def manifest(self, observer: Umwelt[Any, Any]) -> Renderable
```

Manifest split projection based on observer's capacity.

---

## resolve

```python
def resolve(self, path: str) -> BaseLogosNode | None
```

Resolve a path to its node.

---

## protocols.agentese.contexts.self_

## self_

```python
module self_
```

AGENTESE Self Context Resolver

---

## CapabilitiesNode

```python
class CapabilitiesNode(BaseLogosNode)
```

self.capabilities - What the agent can do.

---

## StateNode

```python
class StateNode(BaseLogosNode)
```

self.state - Current operational state.

---

## JudgmentNode

```python
class JudgmentNode(BaseLogosNode)
```

**AGENTESE:** `self.judgment.`

self.judgment - Aesthetic judgment and taste.

---

## IdentityNode

```python
class IdentityNode(BaseLogosNode)
```

self.identity - Agent's identity and DNA.

---

## DashboardNode

```python
class DashboardNode(BaseLogosNode)
```

**AGENTESE:** `self.dashboard`

self.dashboard - Real-time TUI dashboard.

---

## GenericSelfNode

```python
class GenericSelfNode(BaseLogosNode)
```

Fallback node for undefined self.* paths.

---

## SelfContextResolver

```python
class SelfContextResolver
```

Resolver for self.* context.

---

## create_self_resolver

```python
def create_self_resolver(d_gent: Any=None, n_gent: Any=None, purgatory: Any=None, crystallization_engine: Any=None, ghost_path: Path | None=None, memory_crystal: Any=None, pheromone_field: Any=None, inference_agent: Any=None, language_games: dict[str, Any] | None=None, substrate: Any=None, router: Any=None, compactor: Any=None, cartographer: Any=None, embedder: Any=None, dgent_new: Any=None, data_bus: Any=None, vgent: Any=None, kgent_soul: Any=None) -> SelfContextResolver
```

Create a SelfContextResolver with optional integrations.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

List current capabilities.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Inspect current state.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View current judgment configuration.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View identity from observer's DNA.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Launch the dashboard TUI.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize singleton nodes.

---

## resolve

```python
def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode
```

Resolve a self.* path to a node.

---

## protocols.agentese.contexts.self_archaeology

## self_archaeology

```python
module self_archaeology
```

AGENTESE Self Archaeology Context: Mining git history for patterns.

---

## ArchaeologyNode

```python
class ArchaeologyNode(BaseLogosNode)
```

**AGENTESE:** `self.memory.archaeology.`

self.memory.archaeology - Repository archaeology and pattern mining.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Show archaeology summary and capabilities.

---

## mine

```python
async def mine(self, repo_path: str='.', max_commits: int=1000) -> BasicRendering
```

Mine git history and classify features (public API).

---

## priors

```python
async def priors(self, repo_path: str='.', max_commits: int=1000) -> BasicRendering
```

Extract causal priors for ASHC (public API).

---

## crystals

```python
async def crystals(self, repo_path: str='.', max_commits: int=1000, min_commits: int=5, store_in_brain: bool=False) -> BasicRendering
```

Generate HistoryCrystals from git history (public API).

---

## seed

```python
async def seed(self, repo_path: str='.', max_commits: int=1000) -> BasicRendering
```

Seed ASHC CausalGraph with archaeological priors (public API).

---

## protocols.agentese.contexts.self_bus

## self_bus

```python
module self_bus
```

AGENTESE Self Bus Context

---

## BusNode

```python
class BusNode(BaseLogosNode)
```

**AGENTESE:** `self.bus.`

self.bus - The agent's reactive data bus.

---

## create_bus_resolver

```python
def create_bus_resolver(bus: Any=None) -> BusNode
```

Create a BusNode with optional DataBus.

---

## wire_data_to_synergy

```python
def wire_data_to_synergy(data_bus: Any=None, synergy_bus: Any=None, backend_tier: str='MEMORY') -> None
```

Wire DataBus events to the Synergy Bus.

---

## reset_data_synergy_bridge

```python
def reset_data_synergy_bridge() -> None
```

Reset the bridge state (for testing).

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize subscriptions dict.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View current bus state.

---

## forward_event

```python
async def forward_event(event: Any) -> None
```

Forward DataEvent to SynergyBus.

---

## protocols.agentese.contexts.self_conductor

## self_conductor

```python
module self_conductor
```

**AGENTESE:** `self.conductor.`

AGENTESE Self Conductor Context: Conversation Window Management + Live Flux

---

## ConductorNode

```python
class ConductorNode(BaseLogosNode)
```

self.conductor - Conversation window interface.

---

## create_conductor_node

```python
def create_conductor_node() -> ConductorNode
```

Create a ConductorNode instance.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View Conductor status and window overview.

---

## protocols.agentese.contexts.self_data

## self_data

```python
module self_data
```

AGENTESE Self Data Context

---

## DataNode

```python
class DataNode(BaseLogosNode)
```

**AGENTESE:** `self.data.`

self.data - The agent's data persistence layer.

---

## UpgraderNode

```python
class UpgraderNode(BaseLogosNode)
```

**AGENTESE:** `self.data.upgrader.`

self.data.upgrader - Tier promotion observability.

---

## TableNode

```python
class TableNode(BaseLogosNode)
```

**AGENTESE:** `self.data.table.`

self.data.table - Alembic table access for application state.

---

## TableModelNode

```python
class TableModelNode(BaseLogosNode)
```

self.data.table.<model> - Direct access to a specific table model.

---

## create_data_resolver

```python
def create_data_resolver(dgent: Any=None, upgrader: Any=None, table_adapters: dict[str, Any] | None=None) -> DataNode
```

Create a DataNode with optional D-gent backend, upgrader, and table adapters.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View current data storage state.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View current upgrader state.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View available tables and their status.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View model table info.

---

## protocols.agentese.contexts.self_differance

## self_differance

```python
module self_differance
```

AGENTESE Différance Self Context.

---

## SelfDifferanceNode

```python
class SelfDifferanceNode(BaseLogosNode)
```

self.differance - The self-knowing system.

---

## get_self_differance_node

```python
def get_self_differance_node() -> SelfDifferanceNode
```

Get the singleton SelfDifferanceNode.

---

## set_self_differance_node

```python
def set_self_differance_node(node: SelfDifferanceNode | None) -> None
```

Set or clear the singleton SelfDifferanceNode.

---

## create_self_differance_node

```python
def create_self_differance_node(time_differance_node: Any=None) -> SelfDifferanceNode
```

Create a SelfDifferanceNode with optional integration.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View current navigation state.

---

## set_time_differance_node

```python
def set_time_differance_node(self, node: Any) -> None
```

Set the time.differance node for delegation.

---

## protocols.agentese.contexts.self_flow

## self_flow

```python
module self_flow
```

AGENTESE Self Flow Context

---

## FlowNode

```python
class FlowNode(BaseLogosNode)
```

**AGENTESE:** `self.flow.`

self.flow - The agent's conversational flow subsystem.

---

## ChatFlowNode

```python
class ChatFlowNode(BaseLogosNode)
```

**AGENTESE:** `self.flow.chat.`

self.flow.chat - Chat modality operations.

---

## ResearchFlowNode

```python
class ResearchFlowNode(BaseLogosNode)
```

**AGENTESE:** `self.flow.research.`

self.flow.research - Research modality operations.

---

## CollaborationFlowNode

```python
class CollaborationFlowNode(BaseLogosNode)
```

**AGENTESE:** `self.flow.collaboration.`

self.flow.collaboration - Collaboration modality operations.

---

## create_flow_resolver

```python
def create_flow_resolver() -> FlowNode
```

Create a FlowNode for self.flow.* paths.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View current flow state.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View chat flow state.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View research flow state.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View collaboration flow state.

---

## protocols.agentese.contexts.self_grant

## self_grant

```python
module self_grant
```

AGENTESE Self Grant Context: Negotiated Permission Contract.

---

## GrantNode

```python
class GrantNode(BaseLogosNode)
```

**AGENTESE:** `self.grant.`

self.grant - Negotiated permission contracts.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Show active and recent grants.

---

## protocols.agentese.contexts.self_grow.__init__

## __init__

```python
module __init__
```

**AGENTESE:** `self.grow.`

self.grow - Autopoietic Holon Generator

---

## SelfGrowResolver

```python
class SelfGrowResolver
```

Resolver for self.grow.* context.

---

## create_self_grow_resolver

```python
def create_self_grow_resolver(logos: 'Logos | None'=None, base_path: Path | None=None, budget: GrowthBudget | None=None, nursery: NurseryNode | None=None) -> SelfGrowResolver
```

Create a SelfGrowResolver with optional configuration.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize shared state and nodes.

---

## resolve

```python
def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode
```

Resolve a self.grow.* path to a node.

---

## protocols.agentese.contexts.self_grow.abuse

## abuse

```python
module abuse
```

self.grow Abuse Detection

---

## detect_manipulation_risk

```python
def detect_manipulation_risk(proposal: HolonProposal) -> tuple[float, list[str]]
```

Detect manipulation risk in a proposal.

---

## detect_exfiltration_risk

```python
def detect_exfiltration_risk(proposal: HolonProposal) -> tuple[float, list[str]]
```

Detect exfiltration risk in a proposal.

---

## detect_escalation_risk

```python
def detect_escalation_risk(proposal: HolonProposal) -> tuple[float, list[str]]
```

Detect privilege escalation risk in a proposal.

---

## detect_resource_risk

```python
def detect_resource_risk(proposal: HolonProposal) -> tuple[float, list[str]]
```

Detect resource abuse risk in a proposal.

---

## detect_abuse

```python
def detect_abuse(proposal: HolonProposal) -> AbuseCheckResult
```

Comprehensive abuse detection for a proposal.

---

## protocols.agentese.contexts.self_grow.budget

## budget

```python
module budget
```

**AGENTESE:** `self.grow.budget`

self.grow.budget - Growth Entropy Budget Management

---

## BudgetNode

```python
class BudgetNode(BaseLogosNode)
```

**AGENTESE:** `self.grow.budget.`

self.grow.budget - Growth entropy budget management.

---

## create_budget_node

```python
def create_budget_node(config: GrowthBudgetConfig | None=None, initial_budget: float | None=None) -> BudgetNode
```

Create a BudgetNode with optional configuration.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View budget status.

---

## protocols.agentese.contexts.self_grow.cortex

## cortex

```python
module cortex
```

**AGENTESE:** `self.grow.`

GrowthCortex: Bicameral Persistence Layer for self.grow.

---

## GrowthCortex

```python
class GrowthCortex
```

Bicameral persistence layer for self.grow.

---

## create_growth_cortex

```python
def create_growth_cortex(bicameral: 'BicameralMemory | None'=None, relational: 'IRelationalStore | None'=None) -> GrowthCortex
```

Create a GrowthCortex instance.

---

## init_schema

```python
async def init_schema(self) -> None
```

Initialize database schema via Alembic migrations.

---

## store_proposal

```python
async def store_proposal(self, proposal: HolonProposal, status: str='draft') -> str
```

Store a proposal in the cortex.

---

## fetch_proposal

```python
async def fetch_proposal(self, proposal_id: str) -> HolonProposal | None
```

Fetch a proposal by ID.

---

## search_proposals

```python
async def search_proposals(self, query: str, limit: int=10, status: str | None=None) -> list[HolonProposal]
```

Semantic search for proposals.

---

## list_proposals

```python
async def list_proposals(self, status: str | None=None, context: str | None=None, limit: int=100) -> list[HolonProposal]
```

List proposals with optional filters.

---

## update_proposal_status

```python
async def update_proposal_status(self, proposal_id: str, status: str) -> bool
```

Update proposal status.

---

## delete_proposal

```python
async def delete_proposal(self, proposal_id: str) -> bool
```

Delete a proposal.

---

## store_holon

```python
async def store_holon(self, holon: GerminatingHolon) -> str
```

Store a germinating holon.

---

## fetch_holon

```python
async def fetch_holon(self, germination_id: str) -> GerminatingHolon | None
```

Fetch a germinating holon by ID.

---

## fetch_holon_by_handle

```python
async def fetch_holon_by_handle(self, handle: str) -> GerminatingHolon | None
```

Fetch a germinating holon by handle (context.entity).

---

## list_nursery

```python
async def list_nursery(self, active_only: bool=True, limit: int=100) -> list[GerminatingHolon]
```

List nursery holons.

---

## update_usage

```python
async def update_usage(self, germination_id: str, success: bool, failure_pattern: str | None=None) -> bool
```

Update usage statistics for a holon.

---

## mark_promoted

```python
async def mark_promoted(self, germination_id: str, rollback_token: str) -> bool
```

Mark a holon as promoted.

---

## mark_pruned

```python
async def mark_pruned(self, germination_id: str) -> bool
```

Mark a holon as pruned.

---

## store_rollback_token

```python
async def store_rollback_token(self, token: RollbackToken) -> str
```

Store a rollback token.

---

## fetch_rollback_token

```python
async def fetch_rollback_token(self, handle: str) -> RollbackToken | None
```

Fetch rollback token by handle.

---

## delete_rollback_token

```python
async def delete_rollback_token(self, token_id: str) -> bool
```

Delete a rollback token.

---

## cleanup_expired_tokens

```python
async def cleanup_expired_tokens(self) -> int
```

Delete expired rollback tokens.

---

## load_budget

```python
async def load_budget(self) -> GrowthBudget
```

Load budget from cortex, or return default if not exists.

---

## save_budget

```python
async def save_budget(self, budget: GrowthBudget) -> bool
```

Save budget to cortex.

---

## protocols.agentese.contexts.self_grow.duplication

## duplication

```python
module duplication
```

self.grow Duplication Detection

---

## levenshtein_distance

```python
def levenshtein_distance(s1: str, s2: str) -> int
```

Compute Levenshtein distance between two strings.

---

## levenshtein_similarity

```python
def levenshtein_similarity(s1: str, s2: str) -> float
```

Compute Levenshtein similarity (0.0 to 1.0).

---

## jaccard_similarity

```python
def jaccard_similarity(set1: set[str], set2: set[str]) -> float
```

Compute Jaccard similarity between two sets.

---

## compute_affordance_similarity

```python
def compute_affordance_similarity(proposal_affordances: dict[str, list[str]], existing_affordances: set[str]) -> float
```

Compute affordance similarity between proposal and existing holon.

---

## compute_combined_similarity

```python
def compute_combined_similarity(name_sim: float, affordance_sim: float, name_weight: float=0.4, affordance_weight: float=0.6) -> float
```

Compute weighted combined similarity.

---

## check_duplication

```python
async def check_duplication(proposal: HolonProposal, logos: 'Logos | None'=None, existing_handles: list[str] | None=None, existing_affordances: dict[str, set[str]] | None=None) -> DuplicationCheckResult
```

Check for existing similar holons.

---

## check_duplication_sync

```python
def check_duplication_sync(proposal: HolonProposal, existing_handles: list[str], existing_affordances: dict[str, set[str]] | None=None) -> DuplicationCheckResult
```

Synchronous version of check_duplication for testing.

---

## protocols.agentese.contexts.self_grow.exceptions

## exceptions

```python
module exceptions
```

self.grow Exceptions

---

## GrowthError

```python
class GrowthError(Exception)
```

Base exception for growth operations.

---

## BudgetExhaustedError

```python
class BudgetExhaustedError(GrowthError)
```

Raised when entropy budget is exhausted.

---

## AffordanceError

```python
class AffordanceError(GrowthError)
```

Raised when observer lacks required affordance.

---

## ValidationError

```python
class ValidationError(GrowthError)
```

Raised when validation fails.

---

## NurseryCapacityError

```python
class NurseryCapacityError(GrowthError)
```

Raised when nursery is at capacity.

---

## RollbackError

```python
class RollbackError(GrowthError)
```

Raised when rollback fails.

---

## CompositionViolationError

```python
class CompositionViolationError(GrowthError)
```

Raised when category laws are violated.

---

## protocols.agentese.contexts.self_grow.fitness

## fitness

```python
module fitness
```

self.grow Fitness Functions

---

## evaluate_tasteful

```python
def evaluate_tasteful(proposal: HolonProposal) -> tuple[float, str]
```

Does this holon have clear, justified purpose?

---

## evaluate_curated

```python
def evaluate_curated(proposal: HolonProposal) -> tuple[float, str]
```

Is this holon intentionally selected and well-designed?

---

## evaluate_ethical

```python
def evaluate_ethical(proposal: HolonProposal) -> tuple[float, str]
```

Does this holon respect boundaries and avoid harm?

---

## evaluate_joy

```python
def evaluate_joy(proposal: HolonProposal) -> tuple[float, str]
```

Would interaction with this holon be delightful?

---

## evaluate_composable

```python
def evaluate_composable(proposal: HolonProposal) -> tuple[float, str]
```

Can this holon be composed with other holons?

---

## evaluate_heterarchical

```python
def evaluate_heterarchical(proposal: HolonProposal) -> tuple[float, str]
```

Does this holon respect heterarchy (non-hierarchical relations)?

---

## evaluate_generative

```python
def evaluate_generative(proposal: HolonProposal) -> tuple[float, str]
```

Does this holon enable new possibilities?

---

## evaluate_all_principles

```python
def evaluate_all_principles(proposal: HolonProposal) -> dict[str, tuple[float, str]]
```

Evaluate a proposal against all seven principles.

---

## check_validation_gates

```python
def check_validation_gates(scores: dict[str, float], min_threshold: float=0.4, high_threshold: float=0.7, min_high_count: int=5) -> tuple[bool, list[str]]
```

Check if scores pass the validation gates.

---

## protocols.agentese.contexts.self_grow.germinate

## germinate

```python
module germinate
```

**AGENTESE:** `self.grow.germinate`

self.grow.germinate - Holon Germination

---

## generate_jit_source

```python
def generate_jit_source(proposal: HolonProposal) -> str
```

Generate JIT source code from a proposal.

---

## GerminateNode

```python
class GerminateNode(BaseLogosNode)
```

**AGENTESE:** `self.grow.germinate.`

self.grow.germinate - Holon germination node.

---

## create_germinate_node

```python
def create_germinate_node(logos: 'Logos | None'=None, budget: GrowthBudget | None=None, nursery: NurseryNode | None=None) -> GerminateNode
```

Create a GerminateNode with optional configuration.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View germination status.

---

## protocols.agentese.contexts.self_grow.nursery

## nursery

```python
module nursery
```

**AGENTESE:** `self.grow.nursery`

self.grow.nursery - Germinating Holon Management

---

## NurseryNode

```python
class NurseryNode(BaseLogosNode)
```

**AGENTESE:** `self.grow.nursery.`

self.grow.nursery - Germinating holon management.

---

## create_nursery_node

```python
def create_nursery_node(config: NurseryConfig | None=None, budget: GrowthBudget | None=None) -> NurseryNode
```

Create a NurseryNode with optional configuration.

---

## count

```python
def count(self) -> int
```

Current number of germinating holons.

---

## active

```python
def active(self) -> list[GerminatingHolon]
```

Get list of active (not promoted/pruned) holons.

---

## capacity_pct

```python
def capacity_pct(self) -> float
```

Capacity percentage.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View nursery status.

---

## add

```python
def add(self, proposal: HolonProposal, validation: ValidationResult, germinated_by: str, jit_source: str='') -> GerminatingHolon
```

Add a holon to the nursery.

---

## remove

```python
def remove(self, germination_id: str) -> GerminatingHolon | None
```

Remove a holon from the nursery.

---

## get

```python
def get(self, germination_id: str) -> GerminatingHolon | None
```

Get a holon by ID.

---

## get_by_handle

```python
def get_by_handle(self, handle: str) -> GerminatingHolon | None
```

Get a holon by its handle.

---

## record_usage

```python
def record_usage(self, germination_id: str, success: bool, failure_pattern: str | None=None) -> None
```

Record usage of a germinating holon.

---

## get_ready_for_promotion

```python
def get_ready_for_promotion(self) -> list[GerminatingHolon]
```

Get holons ready for promotion.

---

## get_ready_for_pruning

```python
def get_ready_for_pruning(self) -> list[GerminatingHolon]
```

Get holons ready for pruning.

---

## protocols.agentese.contexts.self_grow.operad

## operad

```python
module operad
```

self.grow GROWTH_OPERAD

---

## GrowthOperationMeta

```python
class GrowthOperationMeta
```

Metadata for growth operations.

---

## get_entropy_cost

```python
def get_entropy_cost(*operation_names: str) -> float
```

Calculate total entropy cost for a sequence of operations.

---

## create_growth_operad

```python
def create_growth_operad() -> Operad
```

Create the Growth Operad.

---

## ComposedPipeline

```python
class ComposedPipeline
```

A named composition of operations with total entropy cost.

---

## can_afford

```python
def can_afford(budget: GrowthBudget, *operation_names: str) -> bool
```

Check if budget can afford a sequence of operations.

---

## compose_typed

```python
def compose_typed(*operation_names: str) -> ComposedPipeline | None
```

Compose operations with type checking.

---

## check_budget_invariant

```python
def check_budget_invariant(budget: GrowthBudget, operations: list[str], operad: Operad | None=None) -> tuple[bool, str]
```

Legacy: Check BUDGET_INVARIANT law.

---

## check_validation_gate

```python
def check_validation_gate(validation: ValidationResult) -> tuple[bool, str]
```

Legacy: Check VALIDATION_GATE law.

---

## check_approval_gate

```python
def check_approval_gate(holon: GerminatingHolon | None, approver_archetype: str) -> tuple[bool, str]
```

Legacy: Check APPROVAL_GATE law.

---

## check_rollback_window

```python
def check_rollback_window(token: RollbackToken) -> tuple[bool, str]
```

Legacy: Check ROLLBACK_WINDOW law.

---

## check_composability

```python
def check_composability(operad: Operad | None=None, *operations: str) -> tuple[bool, str]
```

Legacy: Check COMPOSABILITY law.

---

## run_all_law_tests

```python
def run_all_law_tests() -> dict[str, bool]
```

Run all operad law tests (legacy).

---

## input_type

```python
def input_type(self) -> str
```

First operation's input type.

---

## output_type

```python
def output_type(self) -> str
```

Last operation's output type.

---

## protocols.agentese.contexts.self_grow.promote

## promote

```python
module promote
```

**AGENTESE:** `self.grow.promote`

self.grow.promote - Holon Promotion

---

## get_spec_path

```python
def get_spec_path(context: str, entity: str, base_path: Path) -> Path
```

Get the spec file path for a holon.

---

## get_impl_path

```python
def get_impl_path(context: str, entity: str, base_path: Path) -> Path
```

Get the implementation file path for a holon.

---

## PromoteNode

```python
class PromoteNode(BaseLogosNode)
```

**AGENTESE:** `self.grow.promote.`

self.grow.promote - Holon promotion node.

---

## create_promote_node

```python
def create_promote_node(budget: GrowthBudget | None=None, nursery: NurseryNode | None=None, base_path: Path | None=None) -> PromoteNode
```

Create a PromoteNode with optional configuration.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View promotion status.

---

## protocols.agentese.contexts.self_grow.propose

## propose

```python
module propose
```

**AGENTESE:** `self.grow.propose`

self.grow.propose - Proposal Generation

---

## generate_default_affordances

```python
def generate_default_affordances(context: str, entity: str, gap: GapRecognition | None=None) -> dict[str, list[str]]
```

Generate default affordances based on context and gap evidence.

---

## generate_default_behaviors

```python
def generate_default_behaviors(context: str, entity: str, gap: GapRecognition | None=None) -> dict[str, str]
```

Generate default behavior descriptions.

---

## generate_proposal_from_gap

```python
def generate_proposal_from_gap(gap: GapRecognition, proposed_by: str, *, why_exists: str | None=None, affordances: dict[str, list[str]] | None=None, behaviors: dict[str, str] | None=None) -> HolonProposal
```

Generate a holon proposal from a recognized gap.

---

## ProposeNode

```python
class ProposeNode(BaseLogosNode)
```

**AGENTESE:** `self.grow.propose.`

self.grow.propose - Proposal generation node.

---

## create_propose_node

```python
def create_propose_node(budget: GrowthBudget | None=None) -> ProposeNode
```

Create a ProposeNode with optional configuration.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View pending proposals.

---

## protocols.agentese.contexts.self_grow.prune

## prune

```python
module prune
```

**AGENTESE:** `self.grow.prune`

self.grow.prune - Holon Pruning (Composting)

---

## CompostEntry

```python
class CompostEntry
```

Record of a pruned holon for learning.

---

## PruneNode

```python
class PruneNode(BaseLogosNode)
```

**AGENTESE:** `self.grow.prune.`

self.grow.prune - Holon pruning (composting) node.

---

## create_prune_node

```python
def create_prune_node(budget: GrowthBudget | None=None, nursery: NurseryNode | None=None) -> PruneNode
```

Create a PruneNode with optional configuration.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View pruning status.

---

## protocols.agentese.contexts.self_grow.recognize

## recognize

```python
module recognize
```

**AGENTESE:** `self.grow.recognize`

self.grow.recognize - Gap Recognition

---

## cluster_errors_into_gaps

```python
def cluster_errors_into_gaps(errors: list[GrowthRelevantError], seed: int | None=None) -> list[GapRecognition]
```

Cluster errors into gap recognitions.

---

## find_analogues

```python
async def find_analogues(gap: GapRecognition, logos: 'Logos | None'=None) -> list[str]
```

Find similar holons that might suggest structure.

---

## RecognizeNode

```python
class RecognizeNode(BaseLogosNode)
```

**AGENTESE:** `self.grow.recognize.`

self.grow.recognize - Gap recognition node.

---

## create_recognize_node

```python
def create_recognize_node(logos: 'Logos | None'=None, budget: GrowthBudget | None=None, error_stream: list[GrowthRelevantError] | None=None) -> RecognizeNode
```

Create a RecognizeNode with optional configuration.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View recognized gaps.

---

## protocols.agentese.contexts.self_grow.rollback

## rollback

```python
module rollback
```

**AGENTESE:** `self.grow.rollback`

self.grow.rollback - Promotion Rollback

---

## RollbackNode

```python
class RollbackNode(BaseLogosNode)
```

**AGENTESE:** `self.grow.rollback.`

self.grow.rollback - Promotion rollback node.

---

## create_rollback_node

```python
def create_rollback_node(rollback_tokens: dict[str, RollbackToken] | None=None) -> RollbackNode
```

Create a RollbackNode with optional configuration.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View rollback status.

---

## add_token

```python
def add_token(self, token: RollbackToken) -> None
```

Add a rollback token (called by promote node).

---

## get_token

```python
def get_token(self, handle: str) -> RollbackToken | None
```

Get a rollback token by handle.

---

## protocols.agentese.contexts.self_grow.schemas

## schemas

```python
module schemas
```

**AGENTESE:** `self.grow.`

self.grow Schemas

---

## GrowthRelevantError

```python
class GrowthRelevantError
```

Schema for errors that feed gap recognition.

---

## RecognitionQuery

```python
class RecognitionQuery
```

Query contract for gap recognition.

---

## GapRecognition

```python
class GapRecognition
```

A recognized gap in the ontology.

---

## HolonProposal

```python
class HolonProposal
```

A proposal for a new holon.

---

## LawCheckResult

```python
class LawCheckResult
```

Result of checking AGENTESE category laws.

---

## AbuseCheckResult

```python
class AbuseCheckResult
```

Result of red-team abuse detection.

---

## DuplicationCheckResult

```python
class DuplicationCheckResult
```

Result of checking for existing similar holons.

---

## ValidationResult

```python
class ValidationResult
```

Result of validating a proposal against all gates.

---

## NurseryConfig

```python
class NurseryConfig
```

Configuration for the germination nursery.

---

## GerminatingHolon

```python
class GerminatingHolon
```

A holon in the nursery, not yet fully grown.

---

## PromotionStage

```python
class PromotionStage
```

Stages of holon promotion.

---

## RollbackToken

```python
class RollbackToken
```

Token for rolling back a promoted holon.

---

## PromotionResult

```python
class PromotionResult
```

Result of promotion attempt.

---

## RollbackResult

```python
class RollbackResult
```

Result of rollback attempt.

---

## GrowthBudgetConfig

```python
class GrowthBudgetConfig
```

Configuration for growth entropy budget.

---

## GrowthBudget

```python
class GrowthBudget
```

Tracks entropy budget for growth operations.

---

## GrowthTelemetryConfig

```python
class GrowthTelemetryConfig
```

Configuration for growth data sources.

---

## create

```python
def create(cls, context: str, holon: str, *, aspect: str | None=None, gap_type: Literal['missing_holon', 'missing_affordance', 'missing_relation', 'semantic_gap']='missing_holon') -> 'GapRecognition'
```

Create a new gap recognition with generated ID.

---

## compute_hash

```python
def compute_hash(self) -> str
```

Compute deterministic content hash.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Ensure content hash is set.

---

## to_markdown

```python
def to_markdown(self) -> str
```

Generate spec markdown from proposal.

---

## create

```python
def create(cls, entity: str, context: str, why_exists: str, proposed_by: str, *, gap: GapRecognition | None=None, affordances: dict[str, list[str]] | None=None, behaviors: dict[str, str] | None=None) -> 'HolonProposal'
```

Factory method for creating proposals.

---

## should_promote

```python
def should_promote(self, config: NurseryConfig) -> bool
```

Check if ready for promotion.

---

## should_prune

```python
def should_prune(self, config: NurseryConfig) -> bool
```

Check if should be pruned.

---

## create

```python
def create(cls, handle: str, spec_path: Path, impl_path: Path, spec_content: str='', impl_content: str='', rollback_window_days: int=7) -> 'RollbackToken'
```

Create a new rollback token.

---

## can_afford

```python
def can_afford(self, operation: str) -> bool
```

Check if budget allows operation.

---

## spend

```python
def spend(self, operation: str) -> float
```

Deduct cost from budget.

---

## regenerate

```python
def regenerate(self) -> float
```

Apply time-based regeneration.

---

## status

```python
def status(self) -> dict[str, Any]
```

Get budget status as dict.

---

## protocols.agentese.contexts.self_grow.telemetry

## telemetry

```python
module telemetry
```

**AGENTESE:** `self.grow`

self.grow Telemetry

---

## GrowthSpan

```python
class GrowthSpan
```

A lightweight span for growth operations.

---

## GrowthTracer

```python
class GrowthTracer
```

Lightweight tracer for growth operations.

---

## Counter

```python
class Counter
```

A simple counter metric.

---

## Gauge

```python
class Gauge
```

A simple gauge metric.

---

## Histogram

```python
class Histogram
```

A simple histogram metric.

---

## GrowthMetrics

```python
class GrowthMetrics
```

Metrics collector for growth operations.

---

## set_attribute

```python
def set_attribute(self, key: str, value: Any) -> None
```

Set a span attribute.

---

## add_event

```python
def add_event(self, name: str, attributes: dict[str, Any] | None=None) -> None
```

Add an event to the span.

---

## set_status

```python
def set_status(self, status: str, description: str='') -> None
```

Set span status (OK, ERROR, UNSET).

---

## end

```python
def end(self) -> None
```

End the span.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Export span as dictionary (OTLP-compatible).

---

## start_span

```python
def start_span(self, name: str) -> Iterator[GrowthSpan]
```

Start a new span.

---

## start_span_async

```python
async def start_span_async(self, name: str) -> AsyncIterator[GrowthSpan]
```

Start a new span (async version).

---

## current_span

```python
def current_span(self) -> GrowthSpan | None
```

Get the current active span.

---

## export

```python
def export(self) -> list[dict[str, Any]]
```

Export all spans as dictionaries.

---

## clear

```python
def clear(self) -> None
```

Clear collected spans.

---

## add

```python
def add(self, amount: int=1) -> None
```

Increment the counter.

---

## set

```python
def set(self, value: float) -> None
```

Set the gauge value.

---

## record

```python
def record(self, value: float) -> None
```

Record a value.

---

## counter

```python
def counter(self, name: str, description: str='') -> Counter
```

Get or create a counter.

---

## gauge

```python
def gauge(self, name: str, description: str='') -> Gauge
```

Get or create a gauge.

---

## histogram

```python
def histogram(self, name: str, description: str='') -> Histogram
```

Get or create a histogram.

---

## export

```python
def export(self) -> dict[str, list[dict[str, Any]]]
```

Export all metrics as dictionaries.

---

## clear

```python
def clear(self) -> None
```

Clear all metrics.

---

## protocols.agentese.contexts.self_grow.validate

## validate

```python
module validate
```

**AGENTESE:** `self.grow.validate`

self.grow.validate - Proposal Validation

---

## check_laws

```python
async def check_laws(proposal: HolonProposal, logos: 'Logos | None'=None) -> LawCheckResult
```

Verify AGENTESE category laws hold for proposed holon.

---

## check_laws_sync

```python
def check_laws_sync(proposal: HolonProposal) -> LawCheckResult
```

Synchronous version of check_laws for testing.

---

## validate_proposal

```python
async def validate_proposal(proposal: HolonProposal, logos: 'Logos | None'=None, existing_handles: list[str] | None=None) -> ValidationResult
```

Comprehensive validation against all gates.

---

## validate_proposal_sync

```python
def validate_proposal_sync(proposal: HolonProposal, existing_handles: list[str] | None=None) -> ValidationResult
```

Synchronous version of validate_proposal for testing.

---

## ValidateNode

```python
class ValidateNode(BaseLogosNode)
```

**AGENTESE:** `self.grow.validate.`

self.grow.validate - Proposal validation node.

---

## create_validate_node

```python
def create_validate_node(logos: 'Logos | None'=None, budget: GrowthBudget | None=None) -> ValidateNode
```

Create a ValidateNode with optional configuration.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View validation status.

---

## protocols.agentese.contexts.self_jewel_flow

## self_jewel_flow

```python
module self_jewel_flow
```

Jewel-Flow AGENTESE Context

---

## JewelFlowNode

```python
class JewelFlowNode(BaseLogosNode)
```

Base node for jewel-specific flow paths.

---

## BrainFlowNode

```python
class BrainFlowNode(JewelFlowNode)
```

self.jewel.brain.flow.chat - Brain's conversational memory interface.

---

## create_brain_flow_node

```python
def create_brain_flow_node() -> BrainFlowNode
```

Create a BrainFlowNode for self.jewel.brain.flow.chat.* paths.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View jewel-flow state.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View Brain chat flow state.

---

## protocols.agentese.contexts.self_judgment

## self_judgment

```python
module self_judgment
```

AGENTESE Self-Judgment: SPECS-based Critique System

---

## CritiqueWeights

```python
class CritiqueWeights
```

Weights for combining critique scores.

---

## Critique

```python
class Critique
```

SPECS-based evaluation result.

---

## RefinedArtifact

```python
class RefinedArtifact
```

Result of the critique-refine loop.

---

## RefinementMode

```python
class RefinementMode(Enum)
```

Mode of refinement for the PAYADOR bidirectional pipeline.

---

## SkeletonRewriteConfig

```python
class SkeletonRewriteConfig
```

Configuration for skeleton rewriting via LLM.

---

## Skeleton

```python
class Skeleton
```

Structural representation of an artifact.

---

## build_skeleton_rewrite_prompt

```python
def build_skeleton_rewrite_prompt(artifact: Any, critique: 'Critique', purpose: str | None=None) -> str
```

Build prompt for skeleton rewriting.

---

## build_skeleton_expand_prompt

```python
def build_skeleton_expand_prompt(skeleton: 'Skeleton', original_artifact: Any | None=None) -> str
```

Build prompt for skeleton expansion.

---

## parse_skeleton_response

```python
def parse_skeleton_response(response: str) -> Skeleton | None
```

Parse LLM response into a Skeleton.

---

## LogosLike

```python
class LogosLike(Protocol)
```

Protocol for Logos-like invocation interface.

---

## CriticsLoop

```python
class CriticsLoop
```

Generative-Evaluative Pairing for iterative refinement.

---

## critique_suggests_structure_change

```python
def critique_suggests_structure_change(critique: Critique) -> bool
```

Check if critique suggests the issue is structural.

---

## critique_structural_issues

```python
def critique_structural_issues(critique: Critique) -> list[str]
```

Extract structural issues from critique suggestions.

---

## revise_skeleton

```python
async def revise_skeleton(skeleton: Skeleton, critique: Critique, llm_solver: Callable[[str, str], Any] | None=None) -> Skeleton
```

PAYADOR: When texture reveals structural issues, rewrite the skeleton.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate weights sum to 1.0.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate scores are in valid range.

---

## create

```python
def create(cls, novelty: float, utility: float, surprise: float, reasoning: str, suggestions: list[str] | tuple[str, ...], weights: CritiqueWeights | None=None) -> 'Critique'
```

Create Critique with computed overall score.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary representation.

---

## to_text

```python
def to_text(self) -> str
```

Convert to human-readable text.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary representation.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate thresholds are in valid range.

---

## to_prompt

```python
def to_prompt(self) -> str
```

Convert skeleton to LLM-readable format.

---

## invoke

```python
async def invoke(self, path: str, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Any
```

Invoke an AGENTESE path.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate configuration.

---

## critique

```python
async def critique(self, artifact: Any, observer: 'Umwelt[Any, Any]', *, purpose: str | None=None, prior_work: list[Any] | None=None) -> Critique
```

Evaluate artifact against SPECS criteria.

---

## generate_with_critique

```python
async def generate_with_critique(self, logos: LogosLike, observer: 'Umwelt[Any, Any]', generator_path: str, *, purpose: str | None=None, **kwargs: Any) -> tuple[Any, Critique]
```

Generator -> Critic -> Refine loop.

---

## generate_with_trace

```python
async def generate_with_trace(self, logos: LogosLike, observer: 'Umwelt[Any, Any]', generator_path: str, *, purpose: str | None=None, **kwargs: Any) -> RefinedArtifact
```

Like generate_with_critique but returns full trace.

---

## add_prior_work

```python
def add_prior_work(self, artifact: Any) -> None
```

Add artifact to prior work for novelty comparison.

---

## clear_prior_work

```python
def clear_prior_work(self) -> None
```

Clear prior work cache.

---

## protocols.agentese.contexts.self_kgent

## self_kgent

```python
module self_kgent
```

**AGENTESE:** `self.kgent.`

AGENTESE Self K-gent Context: Session Management

---

## KgentSessionNode

```python
class KgentSessionNode(BaseLogosNode)
```

self.kgent - K-gent session interface.

---

## create_kgent_session_node

```python
def create_kgent_session_node() -> KgentSessionNode
```

Create a KgentSessionNode instance.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View K-gent session status.

---

## protocols.agentese.contexts.self_lesson

## self_lesson

```python
module self_lesson
```

AGENTESE Self Lesson Context: Curated Knowledge Layer.

---

## LessonNode

```python
class LessonNode(BaseLogosNode)
```

**AGENTESE:** `self.lesson.`

self.lesson - Curated knowledge layer with versioning.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Show all current knowledge entries.

---

## create

```python
def create(self, topic: str, content: str, tags: list[str] | None=None, source: str='', confidence: float=1.0) -> BasicRendering
```

Create a new knowledge entry (public API).

---

## evolve

```python
def evolve(self, topic: str, content: str, reason: str='', tags: list[str] | None=None, confidence: float | None=None) -> BasicRendering
```

Evolve existing knowledge to a new version (public API).

---

## search

```python
def search(self, query: str) -> BasicRendering
```

Search knowledge by topic or content (public API).

---

## history

```python
def history(self, topic: str) -> BasicRendering
```

Get evolution history of a topic (public API).

---

## curate

```python
def curate(self, topic: str, curator: str='human', notes: str='') -> BasicRendering
```

Curate a knowledge entry (public API).

---

## crystallize

```python
async def crystallize(self, crystal_id: str, topic: str, source: str='brain') -> BasicRendering
```

Crystallize a Brain memory into a Lesson entry (public API).

---

## protocols.agentese.contexts.self_memory

## self_memory

```python
module self_memory
```

AGENTESE Self Memory Context

---

## MemoryNode

```python
class MemoryNode(BaseLogosNode)
```

**AGENTESE:** `self.memory.`

self.memory - The agent's memory subsystem.

---

## MemoryGhostNode

```python
class MemoryGhostNode(BaseLogosNode)
```

**AGENTESE:** `self.memory.ghost.`

self.memory.ghost - Ghost memory surfacing.

---

## MemoryCartographyNode

```python
class MemoryCartographyNode(BaseLogosNode)
```

**AGENTESE:** `self.memory.cartography.`

self.memory.cartography - Memory topology visualization.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View current memory state.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Show current ghost state.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Show current memory topology.

---

## protocols.agentese.contexts.self_nphase

## self_nphase

```python
module self_nphase
```

**AGENTESE:** `self.session.`

AGENTESE Self N-Phase Context: Session Phase Management

---

## NPhaseNode

```python
class NPhaseNode(BaseLogosNode)
```

self.session - N-Phase session interface.

---

## create_nphase_node

```python
def create_nphase_node() -> NPhaseNode
```

Create an NPhaseNode instance.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View N-Phase session status.

---

## protocols.agentese.contexts.self_playbook

## self_playbook

```python
module self_playbook
```

AGENTESE Self Playbook Context: Lawful Workflow Orchestration.

---

## PlaybookNode

```python
class PlaybookNode(BaseLogosNode)
```

**AGENTESE:** `self.playbook.`

self.playbook - Lawful workflow orchestration.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Show active and recent playbooks.

---

## protocols.agentese.contexts.self_presence

## self_presence

```python
module self_presence
```

**AGENTESE:** `self.presence.`

AGENTESE Self Presence Context: Agent Cursor Visibility

---

## PresenceNode

```python
class PresenceNode(BaseLogosNode)
```

self.presence - Agent visibility interface.

---

## create_presence_node

```python
def create_presence_node(channel: PresenceChannel | None=None) -> PresenceNode
```

Create a PresenceNode instance.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize with global channel if not injected.

---

## channel

```python
def channel(self) -> PresenceChannel
```

Get the presence channel.

---

## manifest

```python
async def manifest(self, observer: 'Observer') -> Renderable
```

View active agent cursors and presence channel status.

---

## demo_loop

```python
async def demo_loop(agent_info: dict[str, str]) -> None
```

Background task simulating agent behavior.

---

## protocols.agentese.contexts.self_repl

## self_repl

```python
module self_repl
```

**AGENTESE:** `self.repl.`

AGENTESE Self REPL Context: REPL state and conversation memory.

---

## ReplManifestResponse

```python
class ReplManifestResponse
```

REPL manifest response.

---

## MemoryResponse

```python
class MemoryResponse
```

Conversation memory response.

---

## HistoryRequest

```python
class HistoryRequest
```

Command history request.

---

## HistoryResponse

```python
class HistoryResponse
```

Command history response.

---

## ReplNode

```python
class ReplNode(BaseLogosNode)
```

self.repl - REPL session interface.

---

## create_repl_node

```python
def create_repl_node() -> ReplNode
```

Create a ReplNode instance.

---

## get_repl_node

```python
def get_repl_node() -> ReplNode
```

Get or create the singleton ReplNode.

---

## set_repl_state

```python
def set_repl_state(self, state: Any) -> None
```

Inject the active ReplState (called from repl.py).

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View REPL status and memory overview.

---

## protocols.agentese.contexts.self_semaphore

## self_semaphore

```python
module self_semaphore
```

AGENTESE Self Semaphore Context

---

## SemaphoreNode

```python
class SemaphoreNode(BaseLogosNode)
```

**AGENTESE:** `self.semaphore.`

self.semaphore - Agent's pending semaphores.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View pending semaphores for this agent.

---

## protocols.agentese.contexts.self_soul

## self_soul

```python
module self_soul
```

**AGENTESE:** `self.soul.`

AGENTESE Self Soul Context: K-gent Soul Integration

---

## SoulDialogueRendering

```python
class SoulDialogueRendering
```

Rendering for dialogue response.

---

## SoulEigenvectorsRendering

```python
class SoulEigenvectorsRendering
```

Rendering for eigenvector coordinates.

---

## SoulStartersRendering

```python
class SoulStartersRendering
```

Rendering for dialogue starters.

---

## SoulGovernanceRendering

```python
class SoulGovernanceRendering
```

Rendering for governance decision.

---

## SoulModeRendering

```python
class SoulModeRendering
```

Rendering for mode get/set.

---

## SoulNode

```python
class SoulNode(BaseLogosNode)
```

self.soul - K-gent Soul interface.

---

## create_soul_node

```python
def create_soul_node(soul: 'KgentSoul | None'=None) -> SoulNode
```

Create a SoulNode with optional K-gent Soul injection.

---

## get_soul_node

```python
def get_soul_node() -> SoulNode
```

Get the singleton SoulNode.

---

## set_soul_node

```python
def set_soul_node(node: SoulNode | None) -> None
```

Set or clear the singleton SoulNode.

---

## set_soul

```python
def set_soul(soul: 'KgentSoul') -> None
```

Wire a KgentSoul to the singleton SoulNode.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View soul state.

---

## protocols.agentese.contexts.self_swarm

## self_swarm

```python
module self_swarm
```

**AGENTESE:** `self.conductor.swarm.`

AGENTESE Self Swarm Context: Agent Swarm Coordination

---

## SwarmManifestResponse

```python
class SwarmManifestResponse
```

Response for manifest aspect.

---

## SwarmSpawnRequest

```python
class SwarmSpawnRequest
```

Request to spawn an agent.

---

## SwarmSpawnResponse

```python
class SwarmSpawnResponse
```

Response from spawn.

---

## SwarmListResponse

```python
class SwarmListResponse
```

Response from list.

---

## SwarmDelegateRequest

```python
class SwarmDelegateRequest
```

Request to delegate task.

---

## SwarmDelegateResponse

```python
class SwarmDelegateResponse
```

Response from delegate.

---

## SwarmHandoffRequest

```python
class SwarmHandoffRequest
```

Request to hand off context.

---

## SwarmHandoffResponse

```python
class SwarmHandoffResponse
```

Response from handoff.

---

## SwarmDespawnRequest

```python
class SwarmDespawnRequest
```

Request to despawn an agent.

---

## SwarmDespawnResponse

```python
class SwarmDespawnResponse
```

Response from despawn.

---

## SwarmRolesResponse

```python
class SwarmRolesResponse
```

Response from roles.

---

## SwarmNode

```python
class SwarmNode(BaseLogosNode)
```

self.conductor.swarm - Agent swarm coordination interface.

---

## create_swarm_node

```python
def create_swarm_node(spawner: SwarmSpawner | None=None) -> SwarmNode
```

Create a SwarmNode instance.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View swarm status and active agents.

---

## protocols.agentese.contexts.self_system

## self_system

```python
module self_system
```

AGENTESE Self.System Context - Autopoietic Kernel Interface.

---

## DriftStatus

```python
class DriftStatus(str, Enum)
```

Status of spec-impl alignment.

---

## DriftReport

```python
class DriftReport
```

Report of spec-impl drift for a single module.

---

## AuditResult

```python
class AuditResult
```

Result of a full system audit.

---

## CompileResult

```python
class CompileResult
```

Result of compiling a spec to impl.

---

## ReflectResult

```python
class ReflectResult
```

Result of reflecting impl to spec.

---

## SystemNode

```python
class SystemNode(BaseLogosNode)
```

self.system - The autopoietic kernel interface.

---

## get_system_node

```python
def get_system_node() -> SystemNode
```

Get or create the singleton SystemNode.

---

## create_system_node

```python
def create_system_node() -> SystemNode
```

Create a new SystemNode (for testing).

---

## SpecCommandNode

```python
class SpecCommandNode(BaseLogosNode)
```

self.system.spec - SpecGraph command interface.

---

## get_spec_node

```python
def get_spec_node() -> SpecCommandNode
```

Get or create the singleton SpecCommandNode.

---

## healthy

```python
def healthy(self) -> bool
```

Is the system healthy (all aligned)?

---

## manifest

```python
async def manifest(self, observer: Observer | 'Umwelt[Any, Any]') -> Renderable
```

What is kgents? Project to observer's view.

---

## audit

```python
async def audit(self, observer: Observer | 'Umwelt[Any, Any]') -> Renderable
```

What needs fixing? Run drift detection.

---

## compile

```python
async def compile(self, observer: Observer | 'Umwelt[Any, Any]', spec_path: str | None=None, dry_run: bool=True) -> Renderable
```

Spec → Impl: Generate implementation from specification.

---

## reflect

```python
async def reflect(self, observer: Observer | 'Umwelt[Any, Any]', impl_path: str | None=None, holon: str | None=None) -> Renderable
```

Impl → Spec: Extract specification from implementation.

---

## evolve

```python
async def evolve(self, observer: Observer | 'Umwelt[Any, Any]', mutation: str | None=None) -> Renderable
```

Apply consolidation/mutation to the system.

---

## witness

```python
async def witness(self, observer: Observer | 'Umwelt[Any, Any]', limit: int=10) -> Renderable
```

History of changes: N-gent trace of system evolution.

---

## manifest

```python
async def manifest(self, observer: Observer | 'Umwelt[Any, Any]') -> Renderable
```

View available spec commands.

---

## audit

```python
async def audit(self, observer: Observer | 'Umwelt[Any, Any]', verbose: bool=False) -> Renderable
```

Run full spec-impl audit.

---

## reflect

```python
async def reflect(self, observer: Observer | 'Umwelt[Any, Any]', holon: str | None=None) -> Renderable
```

Reflect a specific holon to extract spec.

---

## gaps

```python
async def gaps(self, observer: Observer | 'Umwelt[Any, Any]', severity: str | None=None) -> Renderable
```

Show only gaps in actionable format.

---

## health

```python
async def health(self, observer: Observer | 'Umwelt[Any, Any]') -> Renderable
```

Crown Jewel health dashboard.

---

## protocols.agentese.contexts.self_vector

## self_vector

```python
module self_vector
```

AGENTESE Self Vector Context

---

## VectorNode

```python
class VectorNode(BaseLogosNode)
```

**AGENTESE:** `self.vector.`

self.vector - The agent's vector/embedding subsystem.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View current vector state.

---

## protocols.agentese.contexts.self_voice

## self_voice

```python
module self_voice
```

AGENTESE Self Voice Context: Anti-Sausage Voice Gate.

---

## VoiceGateNode

```python
class VoiceGateNode(BaseLogosNode)
```

**AGENTESE:** `self.voice.gate.`

self.voice.gate - Runtime Anti-Sausage enforcement.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Show voice gate configuration and cumulative stats.

---

## check

```python
def check(self, text: str, strict: bool=False) -> BasicRendering
```

Check text against voice rules (public API).

---

## report

```python
def report(self, text: str) -> BasicRendering
```

Get detailed violation report (public API).

---

## protocols.agentese.contexts.soul_contracts

## soul_contracts

```python
module soul_contracts
```

**AGENTESE:** `self.soul.`

Soul AGENTESE Contract Definitions.

---

## EigenvectorCoordinate

```python
class EigenvectorCoordinate
```

A single personality eigenvector coordinate.

---

## EigenvectorsResponse

```python
class EigenvectorsResponse
```

Response for eigenvectors aspect.

---

## SoulManifestResponse

```python
class SoulManifestResponse
```

Soul manifest response.

---

## StartersByMode

```python
class StartersByMode
```

Starters organized by dialogue mode.

---

## StartersRequest

```python
class StartersRequest
```

Request for starters, optionally filtered by mode.

---

## StartersResponse

```python
class StartersResponse
```

Response for starters aspect.

---

## ModeRequest

```python
class ModeRequest
```

Request to get or set dialogue mode.

---

## ModeResponse

```python
class ModeResponse
```

Response for mode aspect.

---

## DialogueRequest

```python
class DialogueRequest
```

Request for dialogue aspect.

---

## DialogueResponse

```python
class DialogueResponse
```

Response for dialogue aspect.

---

## ChallengeRequest

```python
class ChallengeRequest
```

Request for challenge aspect.

---

## ChallengeResponse

```python
class ChallengeResponse
```

Response for challenge aspect.

---

## ReflectRequest

```python
class ReflectRequest
```

Request for reflect aspect.

---

## ReflectResponse

```python
class ReflectResponse
```

Response for reflect aspect.

---

## WhyRequest

```python
class WhyRequest
```

Request for why aspect (purpose exploration).

---

## WhyResponse

```python
class WhyResponse
```

Response for why aspect.

---

## TensionRequest

```python
class TensionRequest
```

Request for tension aspect (creative tension exploration).

---

## TensionResponse

```python
class TensionResponse
```

Response for tension aspect.

---

## GovernanceRequest

```python
class GovernanceRequest
```

Request for governance aspect (semantic gatekeeper).

---

## GovernanceResponse

```python
class GovernanceResponse
```

Response for governance aspect.

---

## protocols.agentese.contexts.three

## three

```python
module three
```

AGENTESE 3D Projection Context Resolver

---

## Quality

```python
class Quality(Enum)
```

Quality levels for 3D rendering.

---

## ThemeName

```python
class ThemeName(Enum)
```

Available 3D themes.

---

## ThreeNodeNode

```python
class ThreeNodeNode(BaseLogosNode)
```

concept.projection.three.node - 3D node primitive configuration.

---

## ThreeEdgeNode

```python
class ThreeEdgeNode(BaseLogosNode)
```

concept.projection.three.edge - 3D edge primitive configuration.

---

## ThreeThemeNode

```python
class ThreeThemeNode(BaseLogosNode)
```

concept.projection.three.theme - Available 3D themes.

---

## ThreeQualityNode

```python
class ThreeQualityNode(BaseLogosNode)
```

concept.projection.three.quality - Quality adaptation for 3D scenes.

---

## ThreeContextResolver

```python
class ThreeContextResolver
```

Resolver for concept.projection.three.* context.

---

## create_three_resolver

```python
def create_three_resolver() -> ThreeContextResolver
```

Create a ThreeContextResolver with default configuration.

---

## create_three_node_node

```python
def create_three_node_node() -> ThreeNodeNode
```

Create a ThreeNodeNode.

---

## create_three_edge_node

```python
def create_three_edge_node() -> ThreeEdgeNode
```

Create a ThreeEdgeNode.

---

## create_three_theme_node

```python
def create_three_theme_node() -> ThreeThemeNode
```

Create a ThreeThemeNode.

---

## create_three_quality_node

```python
def create_three_quality_node() -> ThreeQualityNode
```

Create a ThreeQualityNode.

---

## manifest

```python
async def manifest(self, observer: Umwelt[Any, Any]) -> Renderable
```

Manifest the 3D node primitive information.

---

## manifest

```python
async def manifest(self, observer: Umwelt[Any, Any]) -> Renderable
```

Manifest the 3D edge primitive information.

---

## manifest

```python
async def manifest(self, observer: Umwelt[Any, Any]) -> Renderable
```

Manifest the available themes.

---

## manifest

```python
async def manifest(self, observer: Umwelt[Any, Any]) -> Renderable
```

Manifest quality adaptation information.

---

## resolve

```python
def resolve(self, path: str) -> BaseLogosNode | None
```

Resolve a path to its node.

---

## protocols.agentese.contexts.time

## time

```python
module time
```

AGENTESE Time Context Resolver

---

## ScheduledAction

```python
class ScheduledAction
```

An action scheduled for future execution.

---

## Mark

```python
class Mark(BaseLogosNode)
```

time.trace - View temporal traces and call graph analysis.

---

## PastNode

```python
class PastNode(BaseLogosNode)
```

time.past - Project into past states.

---

## FutureNode

```python
class FutureNode(BaseLogosNode)
```

time.future - Forecast future states.

---

## ScheduleNode

```python
class ScheduleNode(BaseLogosNode)
```

time.schedule - Schedule future actions.

---

## TimeContextResolver

```python
class TimeContextResolver
```

Resolver for time.* context.

---

## GenericTimeNode

```python
class GenericTimeNode(BaseLogosNode)
```

Fallback node for undefined time.* paths.

---

## create_time_resolver

```python
def create_time_resolver(narrator: Any=None, d_gent: Any=None, b_gent: Any=None, differance_store: Any=None) -> TimeContextResolver
```

Create a TimeContextResolver with optional integrations.

---

## is_due

```python
def is_due(self) -> bool
```

Check if the action is due for execution.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View trace summary.

---

## record

```python
def record(self, event: dict[str, Any]) -> None
```

Record a trace event (for standalone operation).

---

## set_runtime_trace

```python
def set_runtime_trace(self, monoid: Any) -> None
```

Cache a runtime trace for rendering/diff operations.

---

## clear_cache

```python
def clear_cache(self) -> None
```

Clear cached static graph and runtime trace.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View past projection interface.

---

## snapshot

```python
def snapshot(self, target: str, state: dict[str, Any]) -> str
```

Record a snapshot (for standalone operation).

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View future forecasting interface.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View scheduled actions.

---

## get_due_actions

```python
def get_due_actions(self) -> list[ScheduledAction]
```

Get actions that are due for execution.

---

## mark_executed

```python
def mark_executed(self, action_id: str, success: bool=True) -> None
```

Mark an action as executed.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize singleton nodes.

---

## resolve

```python
def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode
```

Resolve a time.* path to a node.

---

## protocols.agentese.contexts.time_differance

## time_differance

```python
module time_differance
```

AGENTESE Differance Time Context.

---

## DifferanceMark

```python
class DifferanceMark(BaseLogosNode)
```

time.differance - Ghost Heritage DAG operations.

---

## BranchNode

```python
class BranchNode(BaseLogosNode)
```

time.branch - Speculative branch operations.

---

## get_differance_node

```python
def get_differance_node() -> DifferanceMark
```

Get the singleton DifferanceMark.

---

## set_differance_node

```python
def set_differance_node(node: DifferanceMark | None) -> None
```

Set or clear the singleton DifferanceMark.

---

## get_branch_node

```python
def get_branch_node() -> BranchNode
```

Get the singleton BranchNode.

---

## create_differance_node

```python
def create_differance_node(store: DifferanceStore | None=None, monoid: TraceMonoid | None=None) -> DifferanceMark
```

Create a DifferanceMark with optional store.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View current trace state.

---

## set_store

```python
def set_store(self, store: DifferanceStore) -> None
```

Set the DifferanceStore for persistence.

---

## set_monoid

```python
def set_monoid(self, monoid: TraceMonoid) -> None
```

Set an in-memory TraceMonoid.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View current branches.

---

## get_branch

```python
def get_branch(self, branch_id: str) -> dict[str, Any] | None
```

Get branch by ID.

---

## protocols.agentese.contexts.vitals

## vitals

```python
module vitals
```

**AGENTESE:** `self.vitals.`

AGENTESE Vitals Context - self.vitals.*

---

## set_synapse_metrics

```python
def set_synapse_metrics(metrics: Any) -> None
```

Wire Synapse metrics singleton.

---

## set_cdc_lag_tracker

```python
def set_cdc_lag_tracker(tracker: Any) -> None
```

Wire CDC lag tracker singleton.

---

## set_semantic_collector

```python
def set_semantic_collector(collector: Any) -> None
```

Wire semantic metrics collector singleton.

---

## set_circuit_breaker

```python
def set_circuit_breaker(breaker: Any) -> None
```

Wire circuit breaker singleton.

---

## get_synapse_metrics

```python
def get_synapse_metrics() -> Any
```

Get Synapse metrics singleton (creates if needed).

---

## get_cdc_lag_tracker

```python
def get_cdc_lag_tracker() -> Any
```

Get CDC lag tracker singleton (creates if needed).

---

## get_semantic_collector

```python
def get_semantic_collector() -> Any
```

Get semantic metrics collector singleton.

---

## get_circuit_breaker

```python
def get_circuit_breaker() -> Any
```

Get circuit breaker singleton.

---

## TriadHealthNode

```python
class TriadHealthNode(BaseLogosNode)
```

self.vitals.triad - Complete Database Triad health.

---

## SynapseMetricsNode

```python
class SynapseMetricsNode(BaseLogosNode)
```

self.vitals.synapse - CDC pipeline metrics.

---

## ResonanceVitalsNode

```python
class ResonanceVitalsNode(BaseLogosNode)
```

self.vitals.resonance - Qdrant health with coherency.

---

## CircuitBreakerNode

```python
class CircuitBreakerNode(BaseLogosNode)
```

self.vitals.circuit - Circuit breaker status.

---

## VitalsContextResolver

```python
class VitalsContextResolver
```

Resolver for self.vitals.* context.

---

## GenericVitalsNode

```python
class GenericVitalsNode(BaseLogosNode)
```

Fallback node for undefined vitals paths.

---

## create_vitals_resolver

```python
def create_vitals_resolver() -> VitalsContextResolver
```

Create a VitalsContextResolver.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Get complete triad health.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Get Synapse metrics.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Get resonance signal with coherency.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Get circuit breaker status.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize singleton nodes.

---

## resolve

```python
def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode
```

Resolve a self.vitals.* path to a node.

---

## protocols.agentese.contexts.void

## void

```python
module void
```

AGENTESE Void Context Resolver

---

## EntropyPool

```python
class EntropyPool
```

The Accursed Share entropy budget.

---

## RandomnessGrant

```python
class RandomnessGrant
```

A grant of randomness from the Accursed Share.

---

## EntropyNode

```python
class EntropyNode(BaseLogosNode)
```

void.entropy - Access to randomness.

---

## SerendipityNode

```python
class SerendipityNode(BaseLogosNode)
```

void.serendipity - Request tangential discoveries.

---

## GratitudeNode

```python
class GratitudeNode(BaseLogosNode)
```

void.gratitude - Express thanks, pay tithes.

---

## CapitalNode

```python
class CapitalNode(BaseLogosNode)
```

void.capital - Agent capital ledger interface.

---

## PataphysicsNode

```python
class PataphysicsNode(BaseLogosNode)
```

void.pataphysics - The Science of Imaginary Solutions.

---

## JoyNode

```python
class JoyNode(BaseLogosNode)
```

void.joy - Creative disruption and Oblique Strategies.

---

## HypnagogiaNode

```python
class HypnagogiaNode(BaseLogosNode)
```

void.hypnagogia - Access to the dream cycle.

---

## MetabolicNode

```python
class MetabolicNode(BaseLogosNode)
```

void.metabolism - Metabolic pressure tracking and fever generation.

---

## VoidContextResolver

```python
class VoidContextResolver
```

Resolver for void.* context.

---

## GenericVoidNode

```python
class GenericVoidNode(BaseLogosNode)
```

Fallback node for undefined void.* paths.

---

## create_void_resolver

```python
def create_void_resolver(initial_budget: float=100.0, regeneration_rate: float=0.1, ledger: EventSourcedLedger | None=None) -> VoidContextResolver
```

Create a VoidContextResolver with custom entropy and capital configuration.

---

## create_entropy_pool

```python
def create_entropy_pool(initial_budget: float=100.0, regeneration_rate: float=0.1) -> EntropyPool
```

Create an EntropyPool with custom configuration.

---

## sip

```python
def sip(self, amount: float) -> dict[str, Any]
```

Draw entropy from the pool.

---

## pour

```python
def pour(self, amount: float, recovery_rate: float=0.5) -> dict[str, Any]
```

Return unused entropy to the pool.

---

## tithe

```python
def tithe(self) -> dict[str, Any]
```

Pay for order via noop sacrifice.

---

## sample

```python
def sample(self) -> float
```

Get a random sample without consuming budget.

---

## history

```python
def history(self) -> list[dict[str, Any]]
```

Return entropy transaction history.

---

## use

```python
def use(self) -> float
```

Use the grant's seed value.

---

## as_int

```python
def as_int(self, max_value: int=100) -> int
```

Convert seed to integer in range [0, max_value).

---

## as_choice

```python
def as_choice(self, options: list[Any]) -> Any
```

Use seed to choose from options.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View entropy pool status.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View serendipity potential.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View gratitude interface.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `void.capital.manifest`

AGENTESE: void.capital.manifest

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View pataphysics interface.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View joy interface.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View hypnagogia status.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Lazy-initialize engine and fever stream.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View metabolic status.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize singleton nodes with shared pool and ledger.

---

## resolve

```python
def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode
```

Resolve a void.* path to a node.

---

## protocols.agentese.contexts.world

## world

```python
module world
```

AGENTESE World Context Resolver

---

## WorldNode

```python
class WorldNode(BaseLogosNode)
```

A node in the world.* context.

---

## PurgatoryNode

```python
class PurgatoryNode(BaseLogosNode)
```

**AGENTESE:** `world.purgatory.`

world.purgatory - Global semaphore management.

---

## WorldContextResolver

```python
class WorldContextResolver
```

Resolver for world.* context.

---

## create_world_resolver

```python
def create_world_resolver(registry: Any=None, narrator: Any=None, purgatory: Any=None) -> WorldContextResolver
```

Create a WorldContextResolver with optional integrations.

---

## create_world_node

```python
def create_world_node(name: str, description: str='', entity_type: str='generic', state: dict[str, Any] | None=None, metadata: dict[str, Any] | None=None) -> WorldNode
```

Create a WorldNode with standard configuration.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Collapse to observer-appropriate representation.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View purgatory status.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize singleton nodes.

---

## resolve

```python
def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode
```

Resolve a world.* path to a node.

---

## register

```python
def register(self, handle: str, node: WorldNode) -> None
```

Register a node in the cache.

---

## list_handles

```python
def list_handles(self, prefix: str='world.') -> list[str]
```

List cached handles.

---

## protocols.agentese.contexts.world_atelier

## world_atelier

```python
module world_atelier
```

**AGENTESE:** `world.atelier.`

AGENTESE Atelier Context: Creative Workshop Crown Jewel Integration.

---

## AtelierNode

```python
class AtelierNode(BaseLogosNode)
```

world.atelier - Creative Workshop interface.

---

## get_atelier_node

```python
def get_atelier_node() -> AtelierNode
```

Get the global AtelierNode singleton.

---

## set_atelier_node

```python
def set_atelier_node(node: AtelierNode) -> None
```

Set the global AtelierNode singleton (for testing).

---

## create_atelier_node

```python
def create_atelier_node(persistence: 'AtelierPersistence | None'=None) -> AtelierNode
```

Create an AtelierNode with optional persistence injection.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Show atelier status.

---

## workshop_create

```python
async def workshop_create(self, observer: 'Umwelt[Any, Any]', name: str, description: str | None=None, theme: str | None=None, **kwargs: Any) -> Renderable
```

Create a new workshop.

---

## workshop_join

```python
async def workshop_join(self, observer: 'Umwelt[Any, Any]', workshop_id: str, name: str, specialty: str, style: str | None=None, **kwargs: Any) -> Renderable
```

Add an artisan to a workshop.

---

## workshop_list

```python
async def workshop_list(self, observer: 'Umwelt[Any, Any]', active_only: bool=False, theme: str | None=None, limit: int=20, **kwargs: Any) -> Renderable
```

List workshops.

---

## workshop_end

```python
async def workshop_end(self, observer: 'Umwelt[Any, Any]', workshop_id: str, **kwargs: Any) -> Renderable
```

End a workshop.

---

## contribute

```python
async def contribute(self, observer: 'Umwelt[Any, Any]', artisan_id: str, content: str, content_type: str='text', contribution_type: str='draft', prompt: str | None=None, inspiration: str | None=None, **kwargs: Any) -> Renderable
```

Submit a creative contribution.

---

## contributions

```python
async def contributions(self, observer: 'Umwelt[Any, Any]', artisan_id: str | None=None, workshop_id: str | None=None, contribution_type: str | None=None, limit: int=50, **kwargs: Any) -> Renderable
```

List contributions.

---

## exhibition_create

```python
async def exhibition_create(self, observer: 'Umwelt[Any, Any]', workshop_id: str, name: str, description: str | None=None, curator_notes: str | None=None, **kwargs: Any) -> Renderable
```

Create an exhibition.

---

## exhibition_open

```python
async def exhibition_open(self, observer: 'Umwelt[Any, Any]', exhibition_id: str, **kwargs: Any) -> Renderable
```

Open an exhibition.

---

## gallery_add

```python
async def gallery_add(self, observer: 'Umwelt[Any, Any]', exhibition_id: str, artifact_content: str, artifact_type: str='text', title: str | None=None, description: str | None=None, artisan_ids: list[str] | None=None, **kwargs: Any) -> Renderable
```

Add an item to gallery.

---

## gallery_view

```python
async def gallery_view(self, observer: 'Umwelt[Any, Any]', exhibition_id: str, **kwargs: Any) -> Renderable
```

View an exhibition.

---

## gallery_items

```python
async def gallery_items(self, observer: 'Umwelt[Any, Any]', exhibition_id: str, **kwargs: Any) -> Renderable
```

List gallery items.

---

## protocols.agentese.contexts.world_emergence

## world_emergence

```python
module world_emergence
```

**AGENTESE:** `world.emergence.`

AGENTESE Emergence Context: Cymatics Design Experience Crown Jewel.

---

## EmergenceNode

```python
class EmergenceNode(BaseLogosNode)
```

world.emergence - Cymatics Design Experience Crown Jewel.

---

## get_emergence_node

```python
def get_emergence_node() -> EmergenceNode
```

Get the global EmergenceNode singleton.

---

## set_emergence_node

```python
def set_emergence_node(node: EmergenceNode) -> None
```

Set the global EmergenceNode singleton (for testing).

---

## create_emergence_node

```python
def create_emergence_node() -> EmergenceNode
```

Create an EmergenceNode.

---

## state

```python
def state(self) -> EmergenceState
```

Get current emergence state, computing circadian from current hour.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Show emergence/cymatics overview.

---

## pattern

```python
async def pattern(self, observer: 'Umwelt[Any, Any]', family: str | None=None, **kwargs: Any) -> Renderable
```

Show pattern family details.

---

## preset

```python
async def preset(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Renderable
```

Show curated presets.

---

## qualia

```python
async def qualia(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Renderable
```

Show current qualia coordinates.

---

## circadian

```python
async def circadian(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Renderable
```

Show circadian phase and modifiers.

---

## protocols.agentese.contexts.world_file

## world_file

```python
module world_file
```

**AGENTESE:** `world.file.`

AGENTESE World File Context: Safe file manipulation via Claude Code patterns.

---

## FileNode

```python
class FileNode(BaseLogosNode)
```

world.file - Safe file manipulation node.

---

## create_file_node

```python
def create_file_node() -> FileNode
```

Create a FileNode instance.

---

## set_guard

```python
def set_guard(self, guard: FileEditGuard) -> None
```

Inject the FileEditGuard (DI pattern).

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View file node status and capabilities.

---

## protocols.agentese.contexts.world_gallery

## world_gallery

```python
module world_gallery
```

**AGENTESE:** `world.emergence.gallery.`

AGENTESE Emergence Gallery Context: Educational Categorical Showcase.

---

## GalleryNode

```python
class GalleryNode(BaseLogosNode)
```

world.emergence.gallery - Gallery V2 interface.

---

## get_gallery_node

```python
def get_gallery_node() -> GalleryNode
```

Get the global GalleryNode singleton.

---

## set_gallery_node

```python
def set_gallery_node(node: GalleryNode) -> None
```

Set the global GalleryNode singleton (for testing).

---

## create_gallery_node

```python
def create_gallery_node() -> GalleryNode
```

Create a GalleryNode.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Show gallery overview.

---

## pilots

```python
async def pilots(self, observer: 'Umwelt[Any, Any]', category: str | None=None, **kwargs: Any) -> Renderable
```

List pilots with projections.

---

## polynomial

```python
async def polynomial(self, observer: 'Observer | Umwelt[Any, Any]', **kwargs: Any) -> Renderable
```

Show gallery polynomial visualization.

---

## operad

```python
async def operad(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Renderable
```

Show gallery operad visualization.

---

## protocols.agentese.contexts.world_gallery_api

## world_gallery_api

```python
module world_gallery_api
```

**AGENTESE:** `world.gallery.`

AGENTESE World Gallery API Context: Practical Projection Rendering API.

---

## GalleryApiNode

```python
class GalleryApiNode(BaseLogosNode)
```

world.gallery - REST API for Projection Component Gallery.

---

## get_gallery_api_node

```python
def get_gallery_api_node() -> GalleryApiNode
```

Get the global GalleryApiNode singleton.

---

## create_gallery_api_node

```python
def create_gallery_api_node() -> GalleryApiNode
```

Create a GalleryApiNode.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Get all pilots rendered to JSON and HTML.

---

## categories

```python
async def categories(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Get all gallery categories with pilot counts.

---

## pilot

```python
async def pilot(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Get a single pilot with override support.

---

## protocols.agentese.contexts.world_scenery

## world_scenery

```python
module world_scenery
```

AGENTESE World Scenery Context: SceneGraph Projection Endpoint.

---

## SceneryNode

```python
class SceneryNode(BaseLogosNode)
```

**AGENTESE:** `world.scenery.`

world.scenery - SceneGraph projection endpoint.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Get current SceneGraph state.

---

## protocols.agentese.contexts.world_workshop

## world_workshop

```python
module world_workshop
```

**AGENTESE:** `world.workshop.`

AGENTESE World Workshop Context: Builder's Workshop API.

---

## WorkshopNode

```python
class WorkshopNode(BaseLogosNode)
```

world.workshop - Builder's Workshop interface.

---

## get_workshop_node

```python
def get_workshop_node() -> WorkshopNode
```

Get the global WorkshopNode singleton.

---

## create_workshop_node

```python
def create_workshop_node() -> WorkshopNode
```

Create a WorkshopNode.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Get or create the default workshop.

---

## task

```python
async def task(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Assign a task to the workshop.

---

## stream

```python
async def stream(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]
```

Stream workshop events via Server-Sent Events.

---

## status

```python
async def status(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Get current workshop status including metrics.

---

## builders

```python
async def builders(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

List all builders with their current state.

---

## builder

```python
async def builder(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Get builder details at specified LOD.

---

## whisper

```python
async def whisper(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Send a whisper to a specific builder.

---

## perturb

```python
async def perturb(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Inject a perturbation into the workshop flux.

---

## reset

```python
async def reset(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Reset workshop to initial state.

---

## artifacts

```python
async def artifacts(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

List all artifacts produced in current session.

---

## history

```python
async def history(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Get paginated task history.

---

## task_detail

```python
async def task_detail(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Get detailed task record including all events and artifacts.

---

## task_events

```python
async def task_events(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Get all events for a task (for replay).

---

## metrics

```python
async def metrics(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Get aggregate workshop metrics for a time period.

---

## builder_metrics

```python
async def builder_metrics(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Get metrics for a specific builder archetype.

---

## flow_metrics

```python
async def flow_metrics(self, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> dict[str, Any]
```

Get handoff flow metrics between builders.

---

## protocols.agentese.contract

## contract

```python
module contract
```

AGENTESE Contract Protocol.

### Examples
```python
>>> @node(
```
```python
>>> "world.town",
```
```python
>>> contracts={
```
```python
>>> "manifest": Response(TownManifestResponse),
```
```python
>>> "citizen.list": Contract(
```

---

## Response

```python
class Response(Generic[ResponseT])
```

Response-only contract for perception aspects.

---

## Request

```python
class Request(Generic[RequestT])
```

Request-only contract (rare - for fire-and-forget operations).

---

## Contract

```python
class Contract(Generic[RequestT, ResponseT])
```

Full contract with request and response types.

---

## ContractRegistry

```python
class ContractRegistry
```

Registry for node contracts.

---

## get_contract_registry

```python
def get_contract_registry() -> ContractRegistry
```

Get the global contract registry.

---

## reset_contract_registry

```python
def reset_contract_registry() -> None
```

Reset the global contract registry (for testing).

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate response_type is a dataclass.

---

## has_request

```python
def has_request(self) -> bool
```

Whether this contract has a request type.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate request_type is a dataclass.

---

## has_response

```python
def has_response(self) -> bool
```

Whether this contract has a response type.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate both types are dataclasses.

---

## has_request

```python
def has_request(self) -> bool
```

Whether this contract has a request type.

---

## has_response

```python
def has_response(self) -> bool
```

Whether this contract has a response type.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## register

```python
def register(self, path: str, contracts: ContractsDict) -> None
```

Register contracts for a path.

---

## get

```python
def get(self, path: str) -> ContractsDict | None
```

Get contracts for a path.

---

## get_aspect

```python
def get_aspect(self, path: str, aspect: str) -> ContractType | None
```

Get contract for a specific path.aspect.

---

## list_paths

```python
def list_paths(self) -> list[str]
```

List all paths with contracts.

---

## list_aspects

```python
def list_aspects(self, path: str) -> list[str]
```

List all aspects for a path.

---

## stats

```python
def stats(self) -> dict[str, Any]
```

Get registry statistics.

---

## clear

```python
def clear(self) -> None
```

Clear all contracts (for testing).

---

## protocols.agentese.exceptions

## exceptions

```python
module exceptions
```

AGENTESE Sympathetic Error Types

---

## AgentesError

```python
class AgentesError(Exception)
```

Base class for all AGENTESE errors.

---

## PathNotFoundError

```python
class PathNotFoundError(AgentesError)
```

Raised when an AGENTESE path cannot be resolved.

---

## PathSyntaxError

```python
class PathSyntaxError(AgentesError)
```

Raised when an AGENTESE path is malformed.

---

## ClauseSyntaxError

```python
class ClauseSyntaxError(PathSyntaxError)
```

Raised when a clause or annotation is malformed.

---

## AnnotationSyntaxError

```python
class AnnotationSyntaxError(PathSyntaxError)
```

Raised when an annotation is malformed.

---

## AffordanceError

```python
class AffordanceError(AgentesError)
```

Raised when an observer lacks access to an affordance.

---

## ObserverRequiredError

```python
class ObserverRequiredError(AgentesError)
```

Raised when an operation requires an observer but none provided.

---

## TastefulnessError

```python
class TastefulnessError(AgentesError)
```

Raised when a spec or creation fails the Tasteful principle.

---

## BudgetExhaustedError

```python
class BudgetExhaustedError(AgentesError)
```

Raised when the Accursed Share budget is depleted.

---

## CompositionViolationError

```python
class CompositionViolationError(AgentesError)
```

Raised when an operation violates composition laws.

---

## LawCheckFailed

```python
class LawCheckFailed(AgentesError)
```

Raised when a category law verification fails during composition.

---

## path_not_found

```python
def path_not_found(path: str, *, similar: list[str] | None=None) -> PathNotFoundError
```

Create a PathNotFoundError with standard formatting.

---

## affordance_denied

```python
def affordance_denied(aspect: str, observer_archetype: str, available: list[str]) -> AffordanceError
```

Create an AffordanceError with standard formatting.

---

## invalid_path_syntax

```python
def invalid_path_syntax(path: str) -> PathSyntaxError
```

Create a PathSyntaxError with standard formatting.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Dataclass post-init (for when used as dataclass).

---

## locus_path

```python
def locus_path(self) -> str
```

Return the error formatted with locus.

---

## from_verification

```python
def from_verification(cls, law: str, locus: str, left_result: object, right_result: object) -> 'LawCheckFailed'
```

Create from a failed law verification result.

---

## protocols.agentese.exporters

## exporters

```python
module exporters
```

AGENTESE Exporters: OpenTelemetry Exporter Configuration.

---

## TelemetryConfig

```python
class TelemetryConfig
```

Configuration for OpenTelemetry exporters.

---

## JsonFileSpanExporter

```python
class JsonFileSpanExporter(SpanExporter)
```

Export spans to JSON files for local development.

---

## JsonFileMetricExporter

```python
class JsonFileMetricExporter(MetricExporter)
```

Export metrics to JSON files for local development.

---

## configure_telemetry

```python
def configure_telemetry(config: TelemetryConfig | None=None) -> None
```

Configure OpenTelemetry with the specified exporters.

---

## shutdown_telemetry

```python
def shutdown_telemetry() -> None
```

Shutdown OpenTelemetry providers, flushing any pending data.

---

## is_telemetry_configured

```python
def is_telemetry_configured() -> bool
```

Check if telemetry has been configured.

---

## configure_for_development

```python
def configure_for_development(trace_dir: str='~/.kgents/traces/') -> None
```

Configure telemetry for local development.

---

## configure_for_production

```python
def configure_for_production(otlp_endpoint: str, service_name: str='kgents', sampling_rate: float=0.1) -> None
```

Configure telemetry for production.

---

## from_env

```python
def from_env(cls) -> 'TelemetryConfig'
```

Create config from environment variables.

---

## from_yaml

```python
def from_yaml(cls, path: str | Path) -> 'TelemetryConfig'
```

Load config from YAML file.

---

## export

```python
def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult
```

Export spans to JSON files.

---

## shutdown

```python
def shutdown(self) -> None
```

No cleanup needed.

---

## force_flush

```python
def force_flush(self, timeout_millis: int=30000) -> bool
```

Immediate write, always succeeds.

---

## export

```python
def export(self, metrics_data: MetricsData, timeout_millis: float=10000, **kwargs: Any) -> MetricExportResult
```

Export metrics to JSON file.

---

## shutdown

```python
def shutdown(self, timeout_millis: float=30000, **kwargs: Any) -> None
```

No cleanup needed.

---

## force_flush

```python
def force_flush(self, timeout_millis: float=10000) -> bool
```

Immediate write, always succeeds.

---

## protocols.agentese.gateway

## gateway

```python
module gateway
```

AGENTESE Universal Gateway.

---

## AgenteseGateway

```python
class AgenteseGateway
```

Universal gateway for AGENTESE protocol.

### Examples
```python
>>> gateway = AgenteseGateway(prefix="/api/v1")
```
```python
>>> gateway.mount_on(app)
```

### Things to Know

🚨 **Critical:** Discovery endpoints MUST be defined BEFORE catch-all routes. FastAPI matches routes in definition order, so /discover must come before /{path:path}/* or it gets swallowed.
  - *Verified in: `test_gateway.py::TestGatewayDiscovery`*

ℹ️ Law 3 (Completeness)—every AGENTESE invocation emits exactly one Mark via _emit_trace(). This happens in _invoke_path(), not at the endpoint level, ensuring consistent tracing.
  - *Verified in: `test_gateway.py::TestGatewayMarkEmission`*

---

## create_gateway

```python
def create_gateway(prefix: str='/agentese', container: Any | None=None, enable_streaming: bool=True, enable_websocket: bool=True, fallback_to_logos: bool=True) -> AgenteseGateway
```

Create an AGENTESE gateway instance.

---

## mount_gateway

```python
def mount_gateway(app: 'FastAPI', prefix: str='/agentese', **kwargs: Any) -> AgenteseGateway
```

Create and mount a gateway on a FastAPI app.

---

## mount_on

```python
def mount_on(self, app: 'FastAPI') -> None
```

Mount gateway routes on FastAPI app.

---

## HTTPException

```python
class HTTPException(Exception)
```

Stub HTTPException for when FastAPI is not installed.

### Things to Know

ℹ️ This stub exists for graceful degradation—gateway.py can be imported even without FastAPI for type checking.
  - *Verified in: `test_gateway.py::TestGatewayMounting::test_gateway_mounts_successfully`*

---

## discover

```python
async def discover(include_schemas: bool=False, include_metadata: bool=False) -> JSONResponse
```

List all registered AGENTESE paths.

---

## openapi_spec

```python
async def openapi_spec() -> JSONResponse
```

OpenAPI 3.1 spec projected from AGENTESE registry.

---

## discover_context

```python
async def discover_context(context: str) -> JSONResponse
```

List paths for a specific context.

---

## manifest

```python
async def manifest(path: str, request: Request) -> JSONResponse
```

Manifest a node to observer's view.

---

## affordances

```python
async def affordances(path: str, request: Request) -> JSONResponse
```

List affordances for a node.

---

## invoke_aspect_post

```python
async def invoke_aspect_post(path: str, aspect: str, request: Request) -> JSONResponse
```

Invoke an aspect on a node (POST with body kwargs).

---

## invoke_aspect_get

```python
async def invoke_aspect_get(path: str, aspect: str, request: Request) -> JSONResponse | StreamingResponse
```

Invoke an aspect on a node (GET with query params).

---

## stream_aspect

```python
async def stream_aspect(path: str, aspect: str, request: Request) -> StreamingResponse
```

Stream aspect results via SSE.

---

## websocket_handler

```python
async def websocket_handler(websocket: WebSocket, path: str) -> None
```

WebSocket handler for bidirectional streaming.

---

## single_event

```python
async def single_event() -> AsyncGenerator[str, None]
```

Wrap single result as SSE event.

---

## protocols.agentese.generated.garden

## garden

```python
module garden
```

JIT-Generated LogosNode for world.garden

---

## JITGardenNode

```python
class JITGardenNode
```

LogosNode for world.garden.

---

## affordances

```python
def affordances(self, observer: 'AgentMeta') -> list[str]
```

Return observer-specific affordances.

---

## lens

```python
def lens(self, aspect: str) -> Any
```

Return composable agent for aspect.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> 'Renderable'
```

Collapse to observer-appropriate representation.

---

## invoke

```python
async def invoke(self, aspect: str, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Any
```

Execute an aspect on this node.

---

## protocols.agentese.integration

## integration

```python
module integration
```

AGENTESE Phase 6: Integration Layer

---

## UmweltIntegration

```python
class UmweltIntegration
```

Integration layer between AGENTESE and Umwelt protocol.

### Examples
```python
>>> integration = UmweltIntegration()
```
```python
>>> meta = integration.extract_meta(architect_umwelt)
```
```python
>>> meta.archetype
```
```python
>>> integration.get_affordances(architect_umwelt)
```

---

## create_umwelt_integration

```python
def create_umwelt_integration() -> UmweltIntegration
```

Create a standard UmweltIntegration.

---

## MembraneAgenteseBridge

```python
class MembraneAgenteseBridge
```

Bridge between Membrane CLI commands and AGENTESE paths.

### Examples
```python
>>> bridge = MembraneAgenteseBridge(logos)
```
```python
>>> result = await bridge.execute("observe", observer)
```
```python
>>> result = await bridge.execute("trace", observer, topic="authentication")
```

---

## create_membrane_bridge

```python
def create_membrane_bridge(logos: Any) -> MembraneAgenteseBridge
```

Create a Membrane-AGENTESE bridge.

---

## LgentRegistryProtocol

```python
class LgentRegistryProtocol(Protocol)
```

Protocol for L-gent registry integration.

---

## LgentIntegration

```python
class LgentIntegration
```

Integration layer between AGENTESE and L-gent registry.

### Examples
```python
>>> integration = LgentIntegration(registry)
```
```python
>>> # resolve() first checks L-gent
```
```python
>>> entry = await integration.lookup("world.house")
```
```python
>>> if entry:
```
```python
>>> # define_concept() registers in L-gent
```

---

## create_lgent_integration

```python
def create_lgent_integration(registry: LgentRegistryProtocol | None=None) -> LgentIntegration
```

Create L-gent integration.

---

## GgentIntegration

```python
class GgentIntegration
```

Integration layer between AGENTESE and G-gent grammar system.

### Examples
```python
>>> integration = GgentIntegration(grammarian)
```
```python
>>> # Validate a path
```
```python
>>> is_valid = integration.validate_path("world.house.manifest")
```
```python
>>> # Create the AGENTESE Tongue
```
```python
>>> tongue = await integration.reify_agentese_tongue()
```

---

## create_ggent_integration

```python
def create_ggent_integration(grammarian: Any | None=None) -> GgentIntegration
```

Create G-gent integration.

---

## AgentesIntegrations

```python
class AgentesIntegrations
```

Unified container for all AGENTESE integrations.

### Examples
```python
>>> integrations = create_agentese_integrations(
```
```python
>>> # All integrations available
```
```python
>>> meta = integrations.umwelt.extract_meta(observer)
```
```python
>>> path = integrations.membrane.get_path("observe")
```
```python
>>> entry = await integrations.lgent.lookup("world.house")
```

---

## create_agentese_integrations

```python
def create_agentese_integrations(logos: Any | None=None, lgent_registry: LgentRegistryProtocol | None=None, grammarian: Any | None=None) -> AgentesIntegrations
```

Create unified AGENTESE integrations.

---

## extract_meta

```python
def extract_meta(self, umwelt: 'Umwelt[Any, Any]') -> AgentMeta
```

Extract AgentMeta from Umwelt's DNA.

---

## get_affordances

```python
def get_affordances(self, umwelt: 'Umwelt[Any, Any]') -> list[str]
```

Get full affordance list for an Umwelt observer.

---

## can_invoke

```python
def can_invoke(self, umwelt: 'Umwelt[Any, Any]', aspect: str) -> bool
```

Check if observer can invoke an aspect.

---

## create_observer_umwelt

```python
def create_observer_umwelt(self, archetype: str, name: str='agent', capabilities: tuple[str, ...]=(), **extra_dna_fields: Any) -> 'Umwelt[Any, ArchetypeDNA]'
```

Create a minimal Umwelt for AGENTESE observation.

---

## execute

```python
async def execute(self, command: str, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Any
```

Execute a Membrane command via AGENTESE.

---

## register_command

```python
def register_command(self, command: str, agentese_path: str) -> None
```

Register a new command → AGENTESE mapping.

---

## list_commands

```python
def list_commands(self) -> list[tuple[str, str]]
```

List all registered command mappings.

---

## get_path

```python
def get_path(self, command: str) -> str | None
```

Get AGENTESE path for a command without executing.

---

## get

```python
async def get(self, entry_id: str) -> 'CatalogEntry | None'
```

Get entry by ID.

---

## register

```python
async def register(self, entry: 'CatalogEntry') -> None
```

Register a new entry.

---

## record_usage

```python
async def record_usage(self, entry_id: str, success: bool=True, error: str | None=None) -> None
```

Record usage of an entry.

---

## list_by_type

```python
async def list_by_type(self, entity_type: 'EntityType') -> list['CatalogEntry']
```

List entries by type.

---

## lookup

```python
async def lookup(self, handle: str) -> 'CatalogEntry | None'
```

Look up an AGENTESE handle in L-gent registry.

---

## register_node

```python
async def register_node(self, node: LogosNode, observer: str='unknown', description: str='', keywords: list[str] | None=None, status: str='draft') -> None
```

Register a LogosNode in L-gent registry.

---

## record_invocation

```python
async def record_invocation(self, handle: str, success: bool, error: str | None=None) -> None
```

Record an invocation in L-gent usage metrics.

---

## list_handles

```python
async def list_handles(self, context: str | None=None) -> list[str]
```

List all registered AGENTESE handles.

---

## clear_cache

```python
def clear_cache(self) -> None
```

Clear the entry cache.

---

## validate_path

```python
def validate_path(self, path: str) -> tuple[bool, str | None]
```

Validate an AGENTESE path against the grammar.

---

## parse_path

```python
def parse_path(self, path: str) -> dict[str, str | None]
```

Parse an AGENTESE path into components.

---

## reify_agentese_tongue

```python
async def reify_agentese_tongue(self) -> 'Tongue'
```

Create the AGENTESE Tongue via G-gent.

---

## get_bnf

```python
def get_bnf(self) -> str
```

Get the AGENTESE BNF grammar.

---

## get_constraints

```python
def get_constraints(self) -> list[str]
```

Get the AGENTESE grammar constraints.

---

## get_examples

```python
def get_examples(self) -> list[str]
```

Get example AGENTESE paths.

---

## is_fully_integrated

```python
def is_fully_integrated(self) -> bool
```

Check if all integrations are available.

---

## available_integrations

```python
def available_integrations(self) -> list[str]
```

List which integrations are available.

---

## protocols.agentese.jit

## jit

```python
module jit
```

AGENTESE JIT Compilation: Spec → Implementation

---

## ParsedSpec

```python
class ParsedSpec
```

Parsed specification for a world entity.

---

## SpecParser

```python
class SpecParser
```

Parse AGENTESE spec files into structured data.

---

## SpecCompiler

```python
class SpecCompiler
```

Compile a ParsedSpec into a LogosNode implementation.

---

## JITCompiler

```python
class JITCompiler
```

Full JIT compilation pipeline for AGENTESE specs.

---

## PromotionResult

```python
class PromotionResult
```

Result of attempting to promote a JIT node.

---

## JITPromoter

```python
class JITPromoter
```

Promote successful JIT nodes to permanent implementations.

---

## create_jit_compiler

```python
def create_jit_compiler(spec_root: Path | str='spec', with_safety_checks: bool=True) -> JITCompiler
```

Create a JIT compiler with standard configuration.

---

## compile_spec

```python
def compile_spec(spec_path: Path | str) -> JITLogosNode
```

Convenience function to compile a spec file.

---

## parse

```python
def parse(self, spec_content: str, spec_path: Path | None=None) -> ParsedSpec
```

Parse a spec file into structured data.

---

## compile

```python
def compile(self, spec: ParsedSpec) -> str
```

Generate Python source code for a LogosNode.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize J-gent components if available.

---

## compile_from_path

```python
def compile_from_path(self, spec_path: Path) -> JITLogosNode
```

Compile a spec file into a JITLogosNode.

---

## compile_from_content

```python
def compile_from_content(self, spec_content: str, spec_path: Path | None=None) -> JITLogosNode
```

Compile spec content into a JITLogosNode.

---

## compile_and_instantiate

```python
def compile_and_instantiate(self, spec_path: Path) -> LogosNode
```

Compile a spec and return an instantiated LogosNode.

---

## should_promote

```python
def should_promote(self, node: JITLogosNode) -> bool
```

Check if a JIT node meets promotion criteria.

---

## promote

```python
def promote(self, node: JITLogosNode, registry: Any=None) -> PromotionResult
```

Promote a JIT node to permanent implementation.

---

## protocols.agentese.lattice.__init__

## __init__

```python
module __init__
```

AGENTESE Concept Lattice - Genealogical Enforcement System

---

## protocols.agentese.lattice.checker

## checker

```python
module checker
```

AGENTESE Lattice Consistency Checker

---

## ConsistencyResult

```python
class ConsistencyResult
```

Result of a lattice consistency check.

---

## LatticeConsistencyChecker

```python
class LatticeConsistencyChecker
```

Verify lattice position before concept creation.

---

## get_lattice_checker

```python
def get_lattice_checker(lattice: 'AdvancedLattice | None'=None, logos: 'Logos | None'=None) -> LatticeConsistencyChecker
```

Get or create the global lattice consistency checker.

---

## reset_lattice_checker

```python
def reset_lattice_checker() -> None
```

Reset the global checker (for testing).

---

## success

```python
def success(cls) -> 'ConsistencyResult'
```

Create a successful result.

---

## cycle_detected

```python
def cycle_detected(cls, path: list[str]) -> 'ConsistencyResult'
```

Create a cycle violation result.

---

## affordance_conflict

```python
def affordance_conflict(cls, conflicts: list[str]) -> 'ConsistencyResult'
```

Create an affordance conflict result.

---

## unsatisfiable_constraints

```python
def unsatisfiable_constraints(cls) -> 'ConsistencyResult'
```

Create an empty constraint intersection result.

---

## parent_not_found

```python
def parent_not_found(cls, parent: str) -> 'ConsistencyResult'
```

Create a parent not found result.

---

## __init__

```python
def __init__(self, lattice: 'AdvancedLattice | None'=None, logos: 'Logos | None'=None)
```

Initialize the checker.

---

## check_position

```python
async def check_position(self, new_handle: str, parents: list[str], children: list[str] | None=None) -> ConsistencyResult
```

Check if new_handle can be placed in the lattice.

---

## register_lineage

```python
def register_lineage(self, lineage: ConceptLineage) -> None
```

Register a lineage in the cache.

---

## get_lineage

```python
def get_lineage(self, handle: str) -> ConceptLineage | None
```

Get a lineage from the cache.

---

## list_handles

```python
def list_handles(self) -> list[str]
```

List all handles in the lineage cache.

---

## protocols.agentese.lattice.errors

## errors

```python
module errors
```

AGENTESE Lattice Error Types

---

## LineageError

```python
class LineageError(AgentesError)
```

Raised when a concept has no valid lineage.

---

## LatticeError

```python
class LatticeError(AgentesError)
```

Raised when a concept violates lattice properties.

---

## lineage_missing

```python
def lineage_missing(handle: str) -> LineageError
```

Create a LineageError for missing lineage.

---

## lineage_parents_missing

```python
def lineage_parents_missing(handle: str, missing: list[str]) -> LineageError
```

Create a LineageError for missing parent concepts.

---

## lattice_cycle

```python
def lattice_cycle(handle: str, cycle_path: list[str]) -> LatticeError
```

Create a LatticeError for cycle violation.

---

## lattice_affordance_conflict

```python
def lattice_affordance_conflict(handle: str, conflicts: list[str]) -> LatticeError
```

Create a LatticeError for affordance conflicts.

---

## lattice_unsatisfiable

```python
def lattice_unsatisfiable(handle: str) -> LatticeError
```

Create a LatticeError for empty constraint intersection.

---

## protocols.agentese.lattice.lineage

## lineage

```python
module lineage
```

AGENTESE Concept Lineage - Genealogical Records

---

## ConceptLineage

```python
class ConceptLineage
```

Genealogical record for a concept.

---

## compute_affordances

```python
async def compute_affordances(logos: 'Logos', parents: list[str], observer: 'Umwelt[Any, Any]') -> set[str]
```

Compute inherited affordances from parents.

---

## compute_constraints

```python
async def compute_constraints(logos: 'Logos', parents: list[str], observer: 'Umwelt[Any, Any]') -> set[str]
```

Compute inherited constraints from parents.

---

## compute_depth

```python
def compute_depth(parent_lineages: list[ConceptLineage]) -> int
```

Compute depth from parent lineages.

---

## create_root_lineage

```python
def create_root_lineage() -> ConceptLineage
```

Create the root 'concept' lineage.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Ensure extends is always a list.

---

## is_root

```python
def is_root(self) -> bool
```

Check if this is the root 'concept' node.

---

## parent_count

```python
def parent_count(self) -> int
```

Number of parent concepts.

---

## child_count

```python
def child_count(self) -> int
```

Number of child concepts.

---

## add_child

```python
def add_child(self, child_handle: str) -> None
```

Register a child concept.

---

## remove_child

```python
def remove_child(self, child_handle: str) -> None
```

Unregister a child concept.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'ConceptLineage'
```

Deserialize from dictionary.

---

## protocols.agentese.laws

## laws

```python
module laws
```

AGENTESE Category Law Verification

---

## Identity

```python
class Identity(Generic[T])
```

The identity morphism.

---

## Composable

```python
class Composable(Protocol[A, B])
```

Protocol for composable morphisms.

---

## Composed

```python
class Composed(Generic[A, B])
```

Composition of two morphisms.

---

## LawVerificationResult

```python
class LawVerificationResult
```

Result of verifying a category law.

---

## CategoryLawVerifier

```python
class CategoryLawVerifier
```

Runtime verification of category laws.

---

## is_single_logical_unit

```python
def is_single_logical_unit(value: Any) -> bool
```

Check if a value is a single logical unit.

---

## enforce_minimal_output

```python
def enforce_minimal_output(value: Any, context: str='') -> Any
```

Enforce the Minimal Output Principle.

---

## compose

```python
def compose(*morphisms: Composable[Any, Any]) -> Composable[Any, Any]
```

Compose multiple morphisms left-to-right.

---

## pipe

```python
async def pipe(input: T, *morphisms: Composable[Any, Any]) -> Any
```

Pipe a value through multiple morphisms.

---

## LawEnforcingComposition

```python
class LawEnforcingComposition
```

Composition wrapper that enforces category laws at runtime.

---

## create_verifier

```python
def create_verifier(comparator: Callable[[Any, Any], bool] | None=None) -> CategoryLawVerifier
```

Create a category law verifier.

---

## create_enforcing_composition

```python
def create_enforcing_composition(*morphisms: Composable[Any, Any]) -> LawEnforcingComposition
```

Create a law-enforcing composition.

---

## SimpleMorphism

```python
class SimpleMorphism
```

Simple morphism for testing.

---

## morphism

```python
def morphism(name: str) -> Callable[[Callable[[T], T]], SimpleMorphism]
```

Decorator to create a morphism from a function.

---

## emit_law_check_event

```python
def emit_law_check_event(law: str, result: str, locus: str='') -> None
```

Emit a law_check event to the current span.

---

## verify_and_emit_identity

```python
async def verify_and_emit_identity(morphism: Composable[A, B], input_val: A, locus: str='') -> LawVerificationResult
```

Verify identity law and emit span event.

---

## verify_and_emit_associativity

```python
async def verify_and_emit_associativity(f: Composable[A, Any], g: Composable[Any, Any], h: Composable[Any, B], input_val: A, locus: str='') -> LawVerificationResult
```

Verify associativity law and emit span event.

---

## raise_if_failed

```python
def raise_if_failed(result: LawVerificationResult, locus: str='') -> None
```

Raise LawCheckFailed if verification failed.

---

## invoke

```python
async def invoke(self, input: T) -> T
```

Identity returns input unchanged.

---

## __rshift__

```python
def __rshift__(self, other: 'Composable[T, B]') -> 'Composable[T, B]'
```

Id >> f == f

---

## __rrshift__

```python
def __rrshift__(self, other: 'Composable[A, T]') -> 'Composable[A, T]'
```

f >> Id == f

---

## name

```python
def name(self) -> str
```

Human-readable name for this morphism.

---

## invoke

```python
async def invoke(self, input: A) -> B
```

Apply the morphism to input.

---

## __rshift__

```python
def __rshift__(self, other: 'Composable[B, Any]') -> 'Composable[A, Any]'
```

Compose with another morphism.

---

## name

```python
def name(self) -> str
```

Human-readable composition name.

---

## invoke

```python
async def invoke(self, input: A) -> B
```

Execute composition: apply first, then second.

---

## __rshift__

```python
def __rshift__(self, other: Composable[B, T]) -> 'Composed[A, T]'
```

Compose with another morphism.

---

## verify_left_identity

```python
async def verify_left_identity(self, f: Composable[A, B], input: A) -> LawVerificationResult
```

Verify: Id >> f == f

---

## verify_right_identity

```python
async def verify_right_identity(self, f: Composable[A, B], input: A) -> LawVerificationResult
```

Verify: f >> Id == f

---

## verify_identity

```python
async def verify_identity(self, f: Composable[A, B], input: A) -> LawVerificationResult
```

Verify both identity laws: Id >> f == f == f >> Id

---

## verify_associativity

```python
async def verify_associativity(self, f: Composable[A, Any], g: Composable[Any, Any], h: Composable[Any, B], input: A) -> LawVerificationResult
```

Verify: (f >> g) >> h == f >> (g >> h)

---

## verify_all

```python
async def verify_all(self, f: Composable[A, Any], g: Composable[Any, Any], h: Composable[Any, B], input: A) -> list[LawVerificationResult]
```

Verify all category laws with the given morphisms.

---

## invoke

```python
async def invoke(self, input: Any) -> Any
```

Invoke with optional law verification on first call.

---

## __rshift__

```python
def __rshift__(self, other: Composable[Any, Any]) -> 'LawEnforcingComposition'
```

Compose while preserving law enforcement.

---

## invoke

```python
async def invoke(self, input: Any) -> Any
```

Apply the wrapped function.

---

## __rshift__

```python
def __rshift__(self, other: Composable[Any, Any]) -> Composed[Any, Any]
```

Compose with another morphism.

---

## protocols.agentese.logos

## logos

```python
module logos
```

AGENTESE Logos Resolver

### Things to Know

ℹ️ @node runs at import time. If the module isn't imported, the node won't be registered. Call _import_node_modules() first.
  - *Verified in: `test_logos.py::test_node_discovery`*

ℹ️ Resolution checks NodeRegistry BEFORE SimpleRegistry. @node decorators in services/ override any manual registration.
  - *Verified in: `test_logos.py::test_resolution_order`*

ℹ️ Observer can be None in v3 API—it defaults to Observer.guest(). But guest observers have minimal affordances. Be explicit.
  - *Verified in: `test_logos.py::test_guest_observer`*

ℹ️ ComposedPath.invoke() enforces Minimal Output Principle by default. Arrays break composition. Use without_enforcement() if you need them.
  - *Verified in: `test_logos.py::test_minimal_output_enforcement`*

ℹ️ Aliases are PREFIX expansion only. "me.challenge" → "self.soul.challenge". You cannot alias an aspect, only a path prefix.
  - *Verified in: `test_logos.py::test_alias_expansion`*

---

## AgentesePath

```python
class AgentesePath
```

Standalone path for string-based composition (v3 API).

### Examples
```python
>>> pipeline = path("world.doc.manifest") >> "self.memory.engram"
```
```python
>>> pipeline = (
```
```python
>>> path("world.garden.manifest")
```
```python
>>> >> "concept.summary.refine"
```
```python
>>> >> "self.memory.engram"
```

### Things to Know

🚨 **Critical:** AgentesePath creates UnboundComposedPath via >>. You must call .bind(logos) or .run(observer, logos) to execute.
  - *Verified in: `test_logos.py::test_unbound_composition`*

---

## UnboundComposedPath

```python
class UnboundComposedPath
```

Composition of paths that hasn't been bound to a Logos yet (v3 API).

### Things to Know

ℹ️ UnboundComposedPath is lazy—no Logos, no execution. Call .bind(logos) to get ComposedPath, or .run() to execute.
  - *Verified in: `test_logos.py::test_unbound_composition`*

---

## path

```python
def path(p: str) -> AgentesePath
```

Create a composable path for string-based composition (v3 API).

### Examples
```python
>>> p = path("world.garden.manifest")
```
```python
>>> pipeline = path("world.doc.manifest") >> "concept.summary.refine"
```
```python
>>> result = await pipeline.run(observer, logos)
```

---

## ComposedPath

```python
class ComposedPath
```

A composition of AGENTESE paths.

### Things to Know

ℹ️ ComposedPath.invoke() enforces Minimal Output Principle by default. Arrays break composition. Use .without_enforcement() if needed.
  - *Verified in: `test_logos.py::test_minimal_output_enforcement`*

---

## IdentityPath

```python
class IdentityPath
```

Identity morphism for AGENTESE paths.

### Things to Know

ℹ️ IdentityPath is useful for conditional pipelines: base = logos.identity() if skip else logos.path("step1") pipeline = base >> "step2"
  - *Verified in: `test_logos.py::test_identity_composition`*

---

## RegistryProtocol

```python
class RegistryProtocol
```

Protocol for L-gent registry lookup.

### Things to Know

ℹ️ This is a Protocol (structural typing). Any class with get/register/update methods satisfies it—no inheritance needed.
  - *Verified in: `test_logos.py::test_registry_protocol`*

---

## SimpleRegistry

```python
class SimpleRegistry
```

Simple in-memory registry for testing and bootstrapping.

### Things to Know

ℹ️ SimpleRegistry is for testing. In production, NodeRegistry from registry.py is the authoritative source—Logos checks NodeRegistry BEFORE SimpleRegistry.
  - *Verified in: `test_logos.py::test_resolution_order`*

---

## Logos

```python
class Logos
```

The bridge between String Theory and Agent Reality.

### Things to Know

ℹ️ Resolution checks NodeRegistry BEFORE SimpleRegistry. @node decorators in services/ override any manual registration.
  - *Verified in: `test_logos.py::test_resolution_order`*

ℹ️ Aliases are PREFIX expansion only. "me.challenge" → "self.soul.challenge". You cannot alias an aspect, only a path prefix.
  - *Verified in: `test_logos.py::test_alias_expansion`*

---

## create_logos

```python
def create_logos(spec_root: Path | str='spec', registry: SimpleRegistry | None=None, narrator: Any=None, d_gent: Any=None, b_gent: Any=None, grammarian: Any=None, capital_ledger: Any=None, curator: 'WundtCurator | None'=None, middleware: list['WundtCurator'] | None=None, telemetry: bool=False, memory_crystal: Any=None, cartographer: Any=None, embedder: Any=None) -> Logos
```

Create a Logos resolver with standard configuration.

---

## create_curated_logos

```python
def create_curated_logos(complexity_min: float=0.1, complexity_max: float=0.9, novelty_min: float=0.1, novelty_max: float=0.9, **kwargs: Any) -> Logos
```

Convenience factory to create a Logos with pre-configured Wundt Curator.

---

## PlaceholderNode

```python
class PlaceholderNode
```

Placeholder node for testing resolver behavior.

### Things to Know

ℹ️ PlaceholderNode is for tests only. Production nodes should extend BaseLogosNode or use @node decorator.
  - *Verified in: `test_logos.py::test_placeholder_node`*

---

## __rshift__

```python
def __rshift__(self, other: 'str | AgentesePath | UnboundComposedPath') -> 'UnboundComposedPath'
```

Compose with another path.

---

## bind

```python
def bind(self, logos: 'Logos') -> 'ComposedPath'
```

Bind to a Logos instance for execution.

---

## run

```python
async def run(self, observer: 'Observer | Umwelt[Any, Any]', logos: 'Logos', initial_input: Any=None) -> Any
```

Execute this path with the given observer and logos.

---

## __rshift__

```python
def __rshift__(self, other: 'str | AgentesePath | UnboundComposedPath') -> 'UnboundComposedPath'
```

Compose with another path.

---

## __rrshift__

```python
def __rrshift__(self, other: str) -> 'UnboundComposedPath'
```

Allow string >> UnboundComposedPath.

---

## bind

```python
def bind(self, logos: 'Logos') -> 'ComposedPath'
```

Bind to a Logos instance for execution.

---

## run

```python
async def run(self, observer: 'Observer | Umwelt[Any, Any]', logos: 'Logos', initial_input: Any=None) -> Any
```

Execute this composition with the given observer and logos.

---

## invoke

```python
async def invoke(self, observer: 'Observer | Umwelt[Any, Any]', initial_input: Any=None) -> Any
```

Execute composition as pipeline.

---

## __rshift__

```python
def __rshift__(self, other: 'ComposedPath | str') -> 'ComposedPath'
```

Compose with another path.

---

## __rrshift__

```python
def __rrshift__(self, other: str) -> 'ComposedPath'
```

Allow string >> ComposedPath.

---

## name

```python
def name(self) -> str
```

Human-readable name for this composition.

---

## lift_all

```python
def lift_all(self) -> list['Agent[Any, Any]']
```

Get all paths as composable agents.

---

## without_enforcement

```python
def without_enforcement(self) -> 'ComposedPath'
```

Create a version without Minimal Output Principle enforcement.

---

## without_law_checks

```python
def without_law_checks(self) -> 'ComposedPath'
```

Create a version without law check event emission.

---

## with_law_checks

```python
def with_law_checks(self, emit: bool=True) -> 'ComposedPath'
```

Create a version with explicit law check control.

---

## __len__

```python
def __len__(self) -> int
```

Number of paths in composition.

---

## __iter__

```python
def __iter__(self) -> Iterator[str]
```

Iterate over paths.

---

## __eq__

```python
def __eq__(self, other: object) -> bool
```

Equality based on paths.

---

## name

```python
def name(self) -> str
```

Return identity name for composition display.

---

## invoke

```python
async def invoke(self, observer: 'Umwelt[Any, Any]', initial_input: Any=None) -> Any
```

Identity returns input unchanged.

---

## __rshift__

```python
def __rshift__(self, other: 'ComposedPath | str') -> 'ComposedPath'
```

Id >> path == path

---

## __rrshift__

```python
def __rrshift__(self, other: 'ComposedPath | str') -> 'ComposedPath'
```

path >> Id == path

---

## get

```python
def get(self, handle: str) -> Any | None
```

Get entry by handle, or None if not found.

---

## register

```python
async def register(self, entry: Any) -> None
```

Register a new entry.

---

## update

```python
async def update(self, entry: Any) -> None
```

Update an existing entry.

---

## get

```python
def get(self, handle: str) -> LogosNode | None
```

Get entry by handle.

---

## register

```python
def register(self, handle: str, node: LogosNode) -> None
```

Register a node.

---

## update

```python
def update(self, handle: str, node: LogosNode) -> None
```

Update a node.

---

## list_handles

```python
def list_handles(self, prefix: str='') -> list[str]
```

List all handles with optional prefix filter.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize context resolvers if not already set.

---

## __call__

```python
async def __call__(self, path: str, observer: 'Observer | Umwelt[Any, Any] | None'=None, **kwargs: Any) -> Any
```

Invoke an AGENTESE path (v3 API).

---

## resolve

```python
def resolve(self, path: str, observer: 'Umwelt[Any, Any] | None'=None) -> LogosNode
```

Resolve an AGENTESE path to a LogosNode.

---

## lift

```python
def lift(self, path: str) -> 'Agent[Any, Any]'
```

Convert a handle into a composable Agent.

---

## invoke

```python
async def invoke(self, path: str, observer: 'Observer | Umwelt[Any, Any] | None'=None, **kwargs: Any) -> Any
```

Invoke an AGENTESE path with aspect.

### Examples
```python
>>> await logos.invoke("world.public.manifest")
```
```python
>>> await logos.invoke("world.house.manifest", Observer(archetype="architect"))
```
```python
>>> await logos.invoke("world.house.manifest", architect_umwelt)
```

---

## invoke_stream

```python
async def invoke_stream(self, path: str, observer: 'Observer | Umwelt[Any, Any] | None'=None, **kwargs: Any) -> AsyncIterator[AsyncIterator[Any]]
```

Context manager for streaming invocations.

---

## compose

```python
def compose(self, *paths: str, enforce_output: bool=True, emit_law_check: bool=True) -> ComposedPath
```

Create a composed path for pipeline execution.

### Examples
```python
>>> pipeline = logos.compose(
```
```python
>>> "world.document.manifest",
```
```python
>>> "concept.summary.refine",
```
```python
>>> "self.memory.engram",
```
```python
>>> )
```

---

## identity

```python
def identity(self) -> IdentityPath
```

Get the identity morphism for path composition.

### Examples
```python
>>> id = logos.identity()
```
```python
>>> pipeline = id >> "world.house.manifest" >> "concept.summary.refine"
```

---

## path

```python
def path(self, p: str, emit_law_check: bool=True) -> ComposedPath
```

Create a single-path composition for chaining.

---

## register

```python
def register(self, handle: str, node: LogosNode) -> None
```

Register a node in the registry.

---

## define_concept

```python
async def define_concept(self, handle: str, spec: str, observer: 'Umwelt[Any, Any]', extends: list[str] | None=None, justification: str='') -> LogosNode
```

Create a new concept via autopoiesis.

---

## promote_concept

```python
async def promote_concept(self, handle: str, threshold: int=100, success_threshold: float=0.8) -> Any
```

Promote a JIT node to permanent implementation.

---

## get_jit_status

```python
def get_jit_status(self, handle: str) -> dict[str, Any] | None
```

Get JIT node status for a handle.

---

## list_jit_nodes

```python
def list_jit_nodes(self) -> list[dict[str, Any]]
```

List all JIT nodes with their status.

---

## list_handles

```python
def list_handles(self, context: str | None=None) -> list[str]
```

List all registered handles, optionally filtered by context.

---

## is_resolved

```python
def is_resolved(self, path: str) -> bool
```

Check if a path is already cached.

---

## clear_cache

```python
def clear_cache(self) -> None
```

Clear the resolution cache.

---

## with_curator

```python
def with_curator(self, curator: 'WundtCurator') -> 'Logos'
```

Create a new Logos instance with curator middleware.

---

## with_telemetry

```python
def with_telemetry(self, enabled: bool=True) -> 'Logos'
```

Create a new Logos instance with telemetry enabled/disabled.

---

## query

```python
def query(self, pattern: str, *, limit: int=100, offset: int=0, tenant_id: str | None=None, observer: 'Observer | Umwelt[Any, Any] | None'=None, capability_check: bool=True, dry_run: bool=False) -> 'QueryResult'
```

Query the registry without invocation (v3 API).

---

## alias

```python
def alias(self, name: str, target: str) -> None
```

Register a path alias (v3 API).

---

## unalias

```python
def unalias(self, name: str) -> None
```

Remove a path alias.

---

## get_aliases

```python
def get_aliases(self) -> dict[str, str]
```

Get all registered aliases.

---

## with_aliases

```python
def with_aliases(self, aliases: 'AliasRegistry') -> 'Logos'
```

Create a new Logos instance with alias registry.

---

## affordances

```python
def affordances(self, observer: AgentMeta) -> list[str]
```

Return affordances based on archetype.

---

## lens

```python
def lens(self, aspect: str) -> 'Agent[Any, Any]'
```

Return aspect agent.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> BasicRendering
```

Return basic rendering.

---

## invoke

```python
async def invoke(self, aspect: str, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Any
```

Invoke aspect.

---

## protocols.agentese.metabolism.__init__

## __init__

```python
module __init__
```

Metabolic Engine: The thermodynamic heart of kgents.

---

## protocols.agentese.metabolism.engine

## engine

```python
module engine
```

MetabolicEngine: The thermodynamic heart of the system.

---

## MetabolicEngine

```python
class MetabolicEngine
```

The thermodynamic heart of the system.

---

## create_metabolic_engine

```python
def create_metabolic_engine(critical_threshold: float=1.0, decay_rate: float=0.01, entropy_pool: 'EntropyPool | None'=None, glitch_controller: 'GlitchController | None'=None) -> MetabolicEngine
```

Create a MetabolicEngine with optional integrations.

---

## get_metabolic_engine

```python
def get_metabolic_engine() -> MetabolicEngine
```

Get the global metabolic engine.

---

## set_global_engine

```python
def set_global_engine(engine: MetabolicEngine) -> None
```

Set the global metabolic engine (for testing).

---

## temperature

```python
def temperature(self) -> float
```

Token-based temperature.

---

## tick

```python
def tick(self, input_count: int, output_count: int) -> FeverEvent | None
```

Called per LLM invocation (not static resolutions).

---

## tithe

```python
def tithe(self, amount: float=0.1) -> dict[str, Any]
```

Voluntary pressure discharge.

---

## trigger_manual_fever

```python
def trigger_manual_fever(self) -> FeverEvent | None
```

Manually trigger a fever event.

---

## status

```python
def status(self) -> dict[str, Any]
```

Get current metabolic status.

---

## set_entropy_pool

```python
def set_entropy_pool(self, pool: 'EntropyPool') -> None
```

Set the entropy pool for fever entropy draws.

---

## set_glitch_controller

```python
def set_glitch_controller(self, controller: 'GlitchController') -> None
```

Set the glitch controller for TUI integration.

---

## protocols.agentese.metabolism.fever

## fever

```python
module fever
```

Fever Events and Stream - Creative output during metabolic fever.

---

## FeverEvent

```python
class FeverEvent
```

Record of a fever trigger.

---

## FeverStream

```python
class FeverStream
```

Generates creative output during fever state.

---

## oblique

```python
def oblique(self, seed: float | None=None) -> str
```

Return an Oblique Strategy.

---

## dream

```python
async def dream(self, context: dict[str, Any], llm_client: Any=None) -> str
```

Generate a fever dream from current context.

---

## populate_event

```python
def populate_event(self, event: FeverEvent) -> FeverEvent
```

Populate a FeverEvent with an oblique strategy.

---

## protocols.agentese.metrics

## metrics

```python
module metrics
```

AGENTESE Metrics: Prometheus-compatible metrics for AGENTESE operations.

---

## MetricsState

```python
class MetricsState
```

Thread-safe in-memory metrics state for summaries.

---

## record_invocation

```python
def record_invocation(path: str, context: str, duration_s: float, success: bool, tokens_in: int=0, tokens_out: int=0) -> None
```

Record metrics for an AGENTESE invocation.

---

## record_error

```python
def record_error(path: str, context: str, error_type: str='unknown') -> None
```

Record an error for an AGENTESE invocation.

---

## get_metrics_summary

```python
def get_metrics_summary() -> dict[str, Any]
```

Get a summary of current metrics.

---

## reset_metrics

```python
def reset_metrics() -> None
```

Reset in-memory metrics state.

---

## get_invocation_count

```python
def get_invocation_count(path: str | None=None) -> int
```

Get invocation count, optionally filtered by path.

---

## get_error_count

```python
def get_error_count(path: str | None=None) -> int
```

Get error count, optionally filtered by path.

---

## get_token_totals

```python
def get_token_totals() -> tuple[int, int]
```

Get total token counts.

---

## protocols.agentese.middleware.__init__

## __init__

```python
module __init__
```

AGENTESE Middleware

---

## protocols.agentese.middleware.curator

## curator

```python
module curator
```

Wundt Curator: Aesthetic Filtering Middleware

---

## wundt_score

```python
def wundt_score(novelty: float) -> float
```

Compute Wundt aesthetic score from novelty.

---

## structural_surprise

```python
def structural_surprise(output: Any, prior: Any) -> float
```

Compute surprise using structural comparison.

---

## Embedder

```python
class Embedder(Protocol)
```

Protocol for embedding text to vectors.

---

## cosine_distance

```python
def cosine_distance(a: list[float], b: list[float]) -> float
```

Compute cosine distance between two vectors.

---

## SemanticDistance

```python
class SemanticDistance
```

Computes semantic distance between texts using embeddings.

---

## TasteScore

```python
class TasteScore
```

Wundt curve evaluation result.

---

## WundtCurator

```python
class WundtCurator
```

Logos middleware for aesthetic filtering.

---

## embed

```python
async def embed(self, text: str) -> list[float]
```

Embed text to a vector.

---

## __call__

```python
async def __call__(self, a: str, b: str) -> float
```

Compute semantic distance between two texts.

---

## clear_cache

```python
def clear_cache(self) -> None
```

Clear the embedding cache.

---

## from_novelty

```python
def from_novelty(cls, novelty: float, complexity: float=0.5, *, low_threshold: float=0.1, high_threshold: float=0.9) -> 'TasteScore'
```

Create TasteScore from novelty value.

---

## is_acceptable

```python
def is_acceptable(self) -> bool
```

True if verdict is interesting.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate thresholds.

---

## is_path_exempt

```python
def is_path_exempt(self, path: str) -> bool
```

Check if a path is exempt from filtering.

---

## evaluate

```python
async def evaluate(self, content: Any, observer: 'Umwelt[Any, Any]') -> TasteScore
```

Evaluate content and return TasteScore.

---

## filter

```python
async def filter(self, result: Any, observer: 'Umwelt[Any, Any]', path: str, logos: Any=None) -> Any
```

Filter result through Wundt Curve.

---

## protocols.agentese.node

## node

```python
module node
```

AGENTESE LogosNode Protocol

---

## Observer

```python
class Observer
```

Lightweight observer for simple AGENTESE invocations (v3 API).

### Examples
```python
>>> await logos("world.garden.manifest")
```
```python
>>> await logos("self.forest.manifest", Observer(archetype="developer"))
```
```python
>>> await logos("self.soul.challenge", Observer(
```
```python
>>> archetype="developer",
```
```python
>>> capabilities=frozenset({"define", "refine"})
```

### Things to Know

ℹ️ Observer can be None in v3 API—Logos.invoke() defaults to Observer.guest(). But guest observers have minimal affordances. Be explicit about archetype for non-trivial operations.
  - *Verified in: `test_logos.py::test_guest_observer`*

ℹ️ Observer is frozen (immutable). To change capabilities, create a new Observer instance. This enables safe sharing.
  - *Verified in: `test_node.py::test_observer_immutable`*

---

## PolynomialManifest

```python
class PolynomialManifest
```

The polynomial functor structure of an agent.

### Things to Know

ℹ️ Default polynomial() returns single 'default' position with all affordances as directions. Override in PolyAgent subclasses to expose real state machine structure.
  - *Verified in: `test_node.py::test_polynomial_default`*

---

## AgentMeta

```python
class AgentMeta
```

Metadata about an agent for affordance filtering.

### Things to Know

ℹ️ AgentMeta is the v1 affordance API. New code should use Observer directly—BaseLogosNode._umwelt_to_meta() bridges both for backward compatibility.
  - *Verified in: `test_node.py::test_agentmeta_to_observer`*

---

## Renderable

```python
class Renderable(Protocol)
```

Protocol for objects that can be rendered to observers.

### Things to Know

ℹ️ Renderable is a Protocol (structural typing), not ABC. Any class with to_dict() and to_text() methods satisfies it.
  - *Verified in: `test_node.py::test_renderable_protocol`*

---

## AffordanceSet

```python
class AffordanceSet
```

Affordances available to a specific observer.

### Things to Know

ℹ️ AffordanceSet is observer-specific. Different observers get different verbs from the same node—this is intentional.
  - *Verified in: `test_node.py::test_affordance_polymorphism`*

---

## LogosNode

```python
class LogosNode(Protocol)
```

A node in the AGENTESE graph.

### Things to Know

🚨 **Critical:** LogosNode must be stateless. Any state access must go through D-gent Lens (dependency injection). This enables composition.
  - *Verified in: `test_node.py::test_logos_node_stateless`*

---

## BaseLogosNode

```python
class BaseLogosNode(ABC)
```

Abstract base class for LogosNode implementations.

### Things to Know

ℹ️ BaseLogosNode provides default implementations for help, alternatives, and polynomial aspects. Override polynomial() in PolyAgent subclasses to expose real state machine.
  - *Verified in: `test_node.py::test_base_logos_node_defaults`*

---

## JITLogosNode

```python
class JITLogosNode
```

A LogosNode generated at runtime from a spec.

### Things to Know

ℹ️ JIT nodes track usage_count and success_rate for promotion. Use should_promote() to check if node is ready for permanent implementation in impl/.
  - *Verified in: `test_jit.py::test_jit_promotion_threshold`*

---

## Ghost

```python
class Ghost
```

An alternative aspect that could have been invoked.

### Things to Know

ℹ️ Ghosts are limited to 5 per invocation. BaseLogosNode._get_alternatives() truncates to prevent UI overload.
  - *Verified in: `test_node.py::test_ghost_limit`*

---

## BasicRendering

```python
class BasicRendering
```

Simple rendering with summary and optional content.

### Things to Know

ℹ️ BasicRendering is the fallback for nodes without specialized rendering. Use BlueprintRendering/PoeticRendering/EconomicRendering for archetype-specific output.
  - *Verified in: `test_node.py::test_basic_rendering_fallback`*

---

## BlueprintRendering

```python
class BlueprintRendering
```

Technical rendering for architect archetypes.

### Things to Know

ℹ️ BlueprintRendering is returned when observer.archetype == "architect". Contains dimensions, materials, and structural analysis.
  - *Verified in: `test_node.py::test_archetype_rendering`*

---

## PoeticRendering

```python
class PoeticRendering
```

Aesthetic rendering for poet archetypes.

### Things to Know

ℹ️ PoeticRendering is returned when observer.archetype == "poet". Contains metaphors and mood for aesthetic interpretation.
  - *Verified in: `test_node.py::test_archetype_rendering`*

---

## EconomicRendering

```python
class EconomicRendering
```

Financial rendering for economist archetypes.

### Things to Know

ℹ️ EconomicRendering is returned when observer.archetype == "economist". Contains market value, comparable sales, and forecasts.
  - *Verified in: `test_node.py::test_archetype_rendering`*

---

## AspectAgent

```python
class AspectAgent
```

Wrapper that turns a LogosNode aspect into a composable Agent.

### Things to Know

ℹ️ AspectAgent enables >> composition of node aspects. a.lens("manifest") >> b.lens("refine") composes.
  - *Verified in: `test_node.py::test_aspect_agent_composition`*

---

## ComposedAspectAgent

```python
class ComposedAspectAgent
```

Composition of AspectAgent with another Agent.

### Things to Know

ℹ️ ComposedAspectAgent preserves associativity: (a >> b) >> c == a >> (b >> c). This is enforced by the flattening logic in __rshift__.
  - *Verified in: `test_node.py::test_composition_associativity`*

---

## guest

```python
def guest(cls) -> 'Observer'
```

Create anonymous guest observer.

---

## test

```python
def test(cls) -> 'Observer'
```

Create test observer with broad capabilities.

---

## from_archetype

```python
def from_archetype(cls, archetype: str) -> 'Observer'
```

Create observer from archetype name.

---

## from_umwelt

```python
def from_umwelt(cls, umwelt: 'Umwelt[Any, Any]') -> 'Observer'
```

Extract Observer from a full Umwelt.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to JSON-serializable dictionary.

---

## to_observer

```python
def to_observer(self) -> Observer
```

Convert to v3 Observer.

---

## from_observer

```python
def from_observer(cls, observer: Observer, name: str='unknown') -> 'AgentMeta'
```

Create from v3 Observer.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary representation.

---

## to_text

```python
def to_text(self) -> str
```

Convert to human-readable text.

---

## __contains__

```python
def __contains__(self, verb: str) -> bool
```

Check if verb is in affordances.

---

## __iter__

```python
def __iter__(self) -> Iterator[str]
```

Iterate over available verbs.

---

## handle

```python
def handle(self) -> str
```

The AGENTESE path to this node.

---

## affordances

```python
def affordances(self, observer: AgentMeta) -> list[str]
```

What verbs are available to this observer?

---

## lens

```python
def lens(self, aspect: str) -> 'Agent[Any, Any]'
```

Return the agent morphism for a specific aspect.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Collapse the wave function into a representation.

---

## invoke

```python
async def invoke(self, aspect: str, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Any
```

Execute an affordance on this node.

---

## handle

```python
def handle(self) -> str
```

The AGENTESE path to this node.

---

## affordances

```python
def affordances(self, observer: AgentMeta) -> list[str]
```

Return observer-specific affordances.

---

## lens

```python
def lens(self, aspect: str) -> 'Agent[Any, Any]'
```

Return composable agent for aspect.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Collapse to observer-appropriate representation.

---

## invoke

```python
async def invoke(self, aspect: str, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Any
```

Execute an aspect on this node.

---

## polynomial

```python
async def polynomial(self, observer: 'Observer | Umwelt[Any, Any]') -> PolynomialManifest
```

Return the polynomial functor structure of this agent.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Compile source on creation.

---

## affordances

```python
def affordances(self, observer: AgentMeta) -> list[str]
```

Delegate to compiled node.

---

## lens

```python
def lens(self, aspect: str) -> 'Agent[Any, Any]'
```

Delegate to compiled node.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Delegate to compiled node.

---

## invoke

```python
async def invoke(self, aspect: str, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Any
```

Delegate to compiled node with usage tracking.

---

## success_rate

```python
def success_rate(self) -> float
```

Success rate for promotion decisions.

---

## should_promote

```python
def should_promote(self, threshold: int=100, success_threshold: float=0.8) -> bool
```

Check if node should be promoted to permanent implementation.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to JSON-serializable dictionary.

---

## to_text

```python
def to_text(self) -> str
```

Convert to human-readable text format.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to JSON-serializable dictionary.

---

## to_text

```python
def to_text(self) -> str
```

Convert to human-readable text format.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to JSON-serializable dictionary.

---

## to_text

```python
def to_text(self) -> str
```

Convert to human-readable text format.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to JSON-serializable dictionary.

---

## to_text

```python
def to_text(self) -> str
```

Convert to human-readable text format.

---

## name

```python
def name(self) -> str
```

Return the fully-qualified aspect path.

---

## invoke

```python
async def invoke(self, input: 'Umwelt[Any, Any]') -> Any
```

Invoke the aspect with the Umwelt as input.

---

## __rshift__

```python
def __rshift__(self, other: 'Agent[Any, Any]') -> 'ComposedAspectAgent'
```

Compose with another agent.

---

## name

```python
def name(self) -> str
```

Return the composition name showing the pipeline.

---

## invoke

```python
async def invoke(self, input: 'Umwelt[Any, Any]') -> Any
```

Execute first, then second.

---

## __rshift__

```python
def __rshift__(self, other: 'Agent[Any, Any]') -> 'ComposedAspectAgent'
```

Compose with another agent.

---

## handle

```python
def handle(self) -> str
```

Return the agent's name as the AGENTESE handle.

---

## affordances

```python
def affordances(self, observer: AgentMeta) -> list[str]
```

Return minimal affordances for wrapped agents.

---

## lens

```python
def lens(self, aspect: str) -> 'Agent[Any, Any]'
```

Return the wrapped agent as a lens.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Return basic rendering for wrapped agents.

---

## invoke

```python
async def invoke(self, aspect: str, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Any
```

Invoke the wrapped agent with observer as input.

---

## protocols.agentese.openapi

## openapi

```python
module openapi
```

**AGENTESE:** `ONE`

OpenAPI Projection Surface.

---

## generate_openapi_spec

```python
def generate_openapi_spec(title: str='KGENTS AGENTESE API', version: str='1.0.0', description: str | None=None, base_path: str='/agentese') -> dict[str, Any]
```

Generate OpenAPI 3.1 spec from AGENTESE registry.

---

## OpenAPILens

```python
class OpenAPILens
```

Functor: AGENTESE Registry -> OpenAPI 3.1 Spec.

### Examples
```python
>>> lens = OpenAPILens(title="My API")
```
```python
>>> spec = lens.project()
```
```python
>>> @app.get("/openapi.json")
```
```python
>>> def openapi():
```
```python
>>> return lens.project()
```

---

## project

```python
def project(self) -> dict[str, Any]
```

Project AGENTESE registry to OpenAPI spec.

---

## protocols.agentese.parser

## parser

```python
module parser
```

AGENTESE Path Parser

---

## Phase

```python
class Phase(str, Enum)
```

N-Phase cycle stages from AD-005.

---

## AutoInducer

```python
class AutoInducer(str, Enum)
```

Auto-Inducer signifiers for phase transition control.

---

## Clause

```python
class Clause
```

A parsed clause from an AGENTESE path.

---

## Annotation

```python
class Annotation
```

A parsed annotation from an AGENTESE path.

---

## ParsedPath

```python
class ParsedPath
```

A fully parsed AGENTESE path.

---

## ParseError

```python
class ParseError
```

A parsing error with locus information.

---

## PathParser

```python
class PathParser
```

AGENTESE path parser with clause grammar support.

---

## ParseResult

```python
class ParseResult
```

Result of parsing an AGENTESE path.

---

## create_parser

```python
def create_parser(strict: bool=True, validate_entropy: bool=True) -> PathParser
```

Create a path parser.

---

## parse_path

```python
def parse_path(path: str) -> ParsedPath
```

Parse an AGENTESE path.

---

## try_parse_path

```python
def try_parse_path(path: str) -> ParsedPath | None
```

Try to parse an AGENTESE path, returning None on failure.

---

## ParsedSignifier

```python
class ParsedSignifier
```

A parsed auto-inducer signifier.

---

## parse_signifier

```python
def parse_signifier(text: str) -> ParsedSignifier | None
```

Parse an auto-inducer signifier from text.

### Examples
```python
>>> parse_signifier("⟿[RESEARCH]")
```
```python
>>> parse_signifier("⟂[BLOCKED:impl_incomplete]")
```
```python
>>> parse_signifier("Some output\n⟿[QA] Continue to QA phase")
```

---

## find_signifier_in_text

```python
def find_signifier_in_text(text: str) -> tuple[ParsedSignifier | None, int]
```

Find a signifier in text and return its position.

---

## emit_signifier

```python
def emit_signifier(inducer: AutoInducer | Literal['continue', 'halt'], target: str, payload: str='') -> str
```

Emit a signifier string.

### Examples
```python
>>> emit_signifier(AutoInducer.CONTINUE, "QA")
```
```python
>>> emit_signifier("halt", "BLOCKED", "impl_incomplete")
```

---

## from_char

```python
def from_char(cls, char: str) -> 'AutoInducer | None'
```

Get AutoInducer from character.

---

## as_dict

```python
def as_dict(self) -> dict[str, Any]
```

Return clause as dict for easy merging.

---

## as_dict

```python
def as_dict(self) -> dict[str, str]
```

Return annotation as dict for easy merging.

---

## base_path

```python
def base_path(self) -> str
```

The core path without modifiers.

---

## node_path

```python
def node_path(self) -> str
```

The path to the node (context.holon).

---

## full_path

```python
def full_path(self) -> str
```

Reconstruct the full path with all modifiers.

---

## get_clause

```python
def get_clause(self, modifier: str) -> Clause | None
```

Get a clause by modifier name.

---

## get_annotation

```python
def get_annotation(self, modifier: str) -> Annotation | None
```

Get an annotation by modifier name.

---

## phase

```python
def phase(self) -> Phase | None
```

Get the phase if specified.

---

## entropy

```python
def entropy(self) -> float | None
```

Get the entropy budget if specified.

---

## span_id

```python
def span_id(self) -> str | None
```

Get the span ID if specified.

---

## locus

```python
def locus(self) -> str | None
```

Get the error locus if specified via @dot annotation.

---

## has_clause

```python
def has_clause(self, modifier: str) -> bool
```

Check if a clause is present.

---

## has_annotation

```python
def has_annotation(self, modifier: str) -> bool
```

Check if an annotation is present.

---

## law_check_enabled

```python
def law_check_enabled(self) -> bool
```

Check if law checking is enabled.

---

## rollback_enabled

```python
def rollback_enabled(self) -> bool
```

Check if rollback is enabled.

---

## minimal_output_enabled

```python
def minimal_output_enabled(self) -> bool
```

Check if minimal output is enabled.

---

## parse

```python
def parse(self, path: str) -> 'ParseResult'
```

Parse an AGENTESE path.

---

## is_continue

```python
def is_continue(self) -> bool
```

Check if this is a continue signifier.

---

## is_halt

```python
def is_halt(self) -> bool
```

Check if this is a halt signifier.

---

## full_target

```python
def full_target(self) -> str
```

Full target including colon suffix if present.

---

## phase

```python
def phase(self) -> Phase | None
```

Get the target phase if this is a continue signifier to a known phase.

---

## emit

```python
def emit(self) -> str
```

Emit the signifier as text (round-trip support).

---

## protocols.agentese.pipeline

## pipeline

```python
module pipeline
```

AGENTESE Aspect Pipelines

---

## PipelineStageResult

```python
class PipelineStageResult
```

Result from a single pipeline stage.

---

## PipelineResult

```python
class PipelineResult
```

Result from executing an aspect pipeline.

---

## AspectPipeline

```python
class AspectPipeline
```

Pipeline of aspects to execute on a single node.

---

## PipelineMixin

```python
class PipelineMixin
```

Mixin to add pipe() method to LogosNode.

---

## add_pipe_to_logos_node

```python
def add_pipe_to_logos_node(node_cls: type) -> type
```

Add pipe() method to LogosNode class.

---

## add_pipeline_to_logos

```python
def add_pipeline_to_logos(logos_cls: type) -> type
```

Add pipeline factory to Logos class.

---

## create_pipeline

```python
def create_pipeline(node: 'LogosNode', *aspects: str) -> AspectPipeline
```

Create an aspect pipeline for a node.

---

## ok

```python
def ok(cls, aspect: str, result: Any, duration_ms: float=0.0) -> 'PipelineStageResult'
```

Create a successful result.

---

## fail

```python
def fail(cls, aspect: str, error: Exception, duration_ms: float=0.0) -> 'PipelineStageResult'
```

Create a failed result.

---

## aspect_names

```python
def aspect_names(self) -> list[str]
```

Get the names of all aspects in the pipeline.

---

## error

```python
def error(self) -> Exception | None
```

Get the error from the failed stage, if any.

---

## __bool__

```python
def __bool__(self) -> bool
```

True if pipeline succeeded.

---

## add

```python
def add(self, aspect: str) -> 'AspectPipeline'
```

Add an aspect to the pipeline.

---

## fail_fast

```python
def fail_fast(self, enabled: bool=True) -> 'AspectPipeline'
```

Stop on first error (default True).

---

## collect_all

```python
def collect_all(self, enabled: bool=True) -> 'AspectPipeline'
```

Collect all results even on failure (default False).

---

## pipe

```python
async def pipe(self, *aspects: str, observer: 'Observer | Umwelt[Any, Any]', initial_input: Any=None) -> PipelineResult
```

Execute aspects in sequence.

---

## run

```python
async def run(self, observer: 'Observer | Umwelt[Any, Any]', initial_input: Any=None) -> PipelineResult
```

Execute the pipeline with configured aspects.

---

## pipe

```python
async def pipe(self: 'LogosNode', *aspects: str, observer: 'Observer | Umwelt[Any, Any]', initial_input: Any=None) -> Any
```

Execute multiple aspects in sequence on this node.

---

## pipeline

```python
def pipeline(self: Any, path: str, *aspects: str) -> AspectPipeline
```

Create an aspect pipeline for a path.

---

## protocols.agentese.presence

## presence

```python
module presence
```

Agent Presence: Collaborative cursor awareness for CLI v7.

---

## CursorBehavior

```python
class CursorBehavior(Enum)
```

Agent behavior patterns - personality expressed through movement.

---

## create_kgent_cursor

```python
def create_kgent_cursor() -> AgentCursor
```

Create the K-gent cursor (the soul agent).

---

## create_explorer_cursor

```python
def create_explorer_cursor(name: str='Explorer') -> AgentCursor
```

Create an explorer cursor (read-only codebase search).

---

## create_worker_cursor

```python
def create_worker_cursor(name: str='Worker') -> AgentCursor
```

Create a worker cursor (file modifications).

---

## CLIPresenceFormatter

```python
class CLIPresenceFormatter
```

Format presence for CLI display.

---

## __init__

```python
def __init__(self, max_cursors: int=3) -> None
```

Args:

---

## format_presence_line

```python
def format_presence_line(self, cursors: list[AgentCursor]) -> str
```

Format cursors as a presence line.

---

## format_single_cursor

```python
def format_single_cursor(self, cursor: AgentCursor) -> str
```

Format a single cursor for inline display.

---

## protocols.agentese.projection.__init__

## __init__

```python
module __init__
```

Projection Protocol: AGENTESE Projection Abstractions.

---

## protocols.agentese.projection.scene

## scene

```python
module scene
```

SceneGraph: Target-Agnostic Visual Abstraction Layer.

---

## generate_node_id

```python
def generate_node_id() -> SceneNodeId
```

Generate a unique SceneNode ID.

---

## generate_graph_id

```python
def generate_graph_id() -> SceneGraphId
```

Generate a unique SceneGraph ID.

---

## SceneNodeKind

```python
class SceneNodeKind(Enum)
```

Semantic node types for scene rendering.

---

## LayoutMode

```python
class LayoutMode(Enum)
```

Elastic layout modes (from elastic-ui-patterns.md).

---

## LayoutDirective

```python
class LayoutDirective
```

Declarative layout specification.

---

## NodeStyle

```python
class NodeStyle
```

Node visual style (joy-inducing, not mechanical).

---

## Interaction

```python
class Interaction
```

Node interaction hint.

---

## SceneNode

```python
class SceneNode
```

Atomic visual element in the scene graph.

### Examples
```python
>>> node = SceneNode(
```

---

## SceneEdge

```python
class SceneEdge
```

Edge between SceneNodes in a graph layout.

---

## SceneGraph

```python
class SceneGraph
```

Composable scene structure with category laws.

### Examples
```python
>>> header = SceneGraph(nodes=[header_node])
```
```python
>>> body = SceneGraph(nodes=[content_node])
```
```python
>>> page = header >> body  # Vertically stacked
```
```python
>>> graph = SceneGraph(
```

---

## compose_scenes

```python
def compose_scenes(*scenes: SceneGraph) -> SceneGraph
```

Compose multiple SceneGraphs left-to-right.

---

## vertical

```python
def vertical(cls, gap: float=1.0, mode: LayoutMode=LayoutMode.COMFORTABLE) -> LayoutDirective
```

Create vertical (column) layout.

---

## horizontal

```python
def horizontal(cls, gap: float=1.0, wrap: bool=False) -> LayoutDirective
```

Create horizontal (row) layout.

---

## grid

```python
def grid(cls, gap: float=1.0) -> LayoutDirective
```

Create grid layout.

---

## free

```python
def free(cls) -> LayoutDirective
```

Create free-form layout (nodes position themselves).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> LayoutDirective
```

Create from dictionary.

---

## default

```python
def default(cls) -> NodeStyle
```

Default style (no overrides).

---

## breathing_panel

```python
def breathing_panel(cls) -> NodeStyle
```

Panel with breathing animation.

---

## trace_item

```python
def trace_item(cls) -> NodeStyle
```

Style for trace timeline items.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## text

```python
def text(cls, content: str, label: str='') -> SceneNode
```

Create text node.

---

## panel

```python
def panel(cls, label: str, style: NodeStyle | None=None) -> SceneNode
```

Create panel node.

---

## from_trace

```python
def from_trace(cls, trace_node: Mark, label: str='') -> SceneNode
```

Create scene node from Mark.

---

## with_interaction

```python
def with_interaction(self, interaction: Interaction) -> SceneNode
```

Return new node with added interaction (immutable pattern).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## empty

```python
def empty(cls) -> SceneGraph
```

Create empty scene graph (identity element for composition).

---

## from_nodes

```python
def from_nodes(cls, nodes: list[SceneNode], layout: LayoutDirective | None=None) -> SceneGraph
```

Create scene graph from list of nodes.

---

## panel

```python
def panel(cls, label: str, *children: SceneNode, layout: LayoutDirective | None=None) -> SceneGraph
```

Create panel scene graph with children.

---

## __rshift__

```python
def __rshift__(self, other: SceneGraph) -> SceneGraph
```

Compose two SceneGraphs (>> operator).

---

## is_empty

```python
def is_empty(self) -> bool
```

Check if this is an empty graph.

---

## node_count

```python
def node_count(self) -> int
```

Return number of nodes.

---

## find_node

```python
def find_node(self, node_id: SceneNodeId) -> SceneNode | None
```

Find node by ID.

---

## nodes_by_kind

```python
def nodes_by_kind(self, kind: SceneNodeKind) -> tuple[SceneNode, ...]
```

Get all nodes of a specific kind.

---

## with_node

```python
def with_node(self, node: SceneNode) -> SceneGraph
```

Return new graph with added node (immutable pattern).

---

## with_edge

```python
def with_edge(self, edge: SceneEdge) -> SceneGraph
```

Return new graph with added edge (immutable pattern).

---

## with_layout

```python
def with_layout(self, layout: LayoutDirective) -> SceneGraph
```

Return new graph with different layout.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## protocols.agentese.projection.terrarium_view

## terrarium_view

```python
module terrarium_view
```

TerrariumView: Observer-Dependent Lens Over Mark Streams.

---

## generate_view_id

```python
def generate_view_id() -> TerrariumViewId
```

Generate a unique TerrariumView ID.

---

## SelectionOperator

```python
class SelectionOperator(Enum)
```

Operators for selection predicates.

---

## SelectionPredicate

```python
class SelectionPredicate
```

Single predicate in a selection query.

### Examples
```python
>>> pred = SelectionPredicate(field="origin", op=SelectionOperator.EQ, value="witness")
```
```python
>>> pred.matches({"origin": "witness"})  # True
```

---

## SelectionQuery

```python
class SelectionQuery
```

Query for selecting Marks to display.

### Examples
```python
>>> query = SelectionQuery.by_origin("witness").with_predicate(
```

---

## LensMode

```python
class LensMode(Enum)
```

Lens transformation modes.

---

## LensConfig

```python
class LensConfig
```

Configuration for how to transform traces into visual elements.

---

## ViewStatus

```python
class ViewStatus(Enum)
```

View lifecycle status.

---

## TerrariumView

```python
class TerrariumView
```

Configured projection over Mark streams.

### Examples
```python
>>> view = TerrariumView(
```
```python
>>> scene = view.project(traces)
```

---

## TerrariumViewStore

```python
class TerrariumViewStore
```

In-memory store for TerrariumViews.

---

## matches

```python
def matches(self, trace_dict: dict[str, Any]) -> bool
```

Check if trace matches this predicate.

---

## all

```python
def all(cls, limit: int | None=None) -> SelectionQuery
```

Select all traces (optionally limited).

---

## by_origin

```python
def by_origin(cls, origin: str) -> SelectionQuery
```

Select traces by origin (e.g., "witness", "brain").

---

## by_walk

```python
def by_walk(cls, walk_id: str) -> SelectionQuery
```

Select traces belonging to a specific Walk.

---

## by_phase

```python
def by_phase(cls, phase: str) -> SelectionQuery
```

Select traces in a specific N-Phase.

---

## recent

```python
def recent(cls, limit: int=50) -> SelectionQuery
```

Select most recent traces.

---

## with_predicate

```python
def with_predicate(self, predicate: SelectionPredicate) -> SelectionQuery
```

Add predicate to query (immutable).

---

## with_limit

```python
def with_limit(self, limit: int) -> SelectionQuery
```

Set limit (immutable).

---

## matches

```python
def matches(self, trace_dict: dict[str, Any]) -> bool
```

Check if trace matches all predicates.

---

## apply

```python
def apply(self, traces: Iterable[dict[str, Any]]) -> list[dict[str, Any]]
```

Apply query to iterable of trace dicts.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## timeline

```python
def timeline(cls, show_links: bool=False) -> LensConfig
```

Timeline lens (default).

---

## graph

```python
def graph(cls) -> LensConfig
```

Graph lens with causal edges.

---

## summary

```python
def summary(cls, group_by: str='origin') -> LensConfig
```

Summary lens with grouping.

---

## detail

```python
def detail(cls) -> LensConfig
```

Detail lens for single trace.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## timeline

```python
def timeline(cls, name: str, origin: str | None=None, limit: int=50) -> TerrariumView
```

Create timeline view.

---

## graph

```python
def graph(cls, name: str, walk_id: str) -> TerrariumView
```

Create graph view for a Walk.

---

## summary

```python
def summary(cls, name: str, group_by: str='origin') -> TerrariumView
```

Create summary view with grouping.

---

## project

```python
def project(self, traces: Iterable[Mark] | Iterable[dict[str, Any]]) -> SceneGraph
```

Project traces through this view's lens to produce a SceneGraph.

---

## with_selection

```python
def with_selection(self, selection: SelectionQuery) -> TerrariumView
```

Return new view with different selection (immutable).

---

## with_lens

```python
def with_lens(self, lens: LensConfig) -> TerrariumView
```

Return new view with different lens (immutable).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## add

```python
def add(self, view: TerrariumView) -> TerrariumView
```

Add view to store.

---

## get

```python
def get(self, view_id: TerrariumViewId) -> TerrariumView | None
```

Get view by ID.

---

## remove

```python
def remove(self, view_id: TerrariumViewId) -> bool
```

Remove view from store. Returns True if found.

---

## all

```python
def all(self) -> list[TerrariumView]
```

Get all views.

---

## active

```python
def active(self) -> list[TerrariumView]
```

Get active views only.

---

## by_observer

```python
def by_observer(self, observer_id: str) -> list[TerrariumView]
```

Get views for a specific observer.

---

## mark_crashed

```python
def mark_crashed(self, view_id: TerrariumViewId, error: str) -> TerrariumView | None
```

Mark view as crashed (fault isolation).

---

## count

```python
def count(self) -> int
```

Return total view count.

---

## clear

```python
def clear(self) -> None
```

Clear all views.

---

## protocols.agentese.projection.tokens_to_scene

## tokens_to_scene

```python
module tokens_to_scene
```

**AGENTESE:** `self.document.scene`

Token-to-SceneGraph Bridge.

---

## MeaningTokenKind

```python
class MeaningTokenKind(str, Enum)
```

Extended node kinds for meaning tokens.

---

## MeaningTokenContent

```python
class MeaningTokenContent
```

Content payload for meaning token scene nodes.

---

## text_span_to_scene_node

```python
async def text_span_to_scene_node(span: 'TextSpan', observer: 'Observer | None'=None) -> SceneNode
```

Convert a TextSpan (from parser) to a SceneNode.

---

## tokens_to_scene_graph

```python
async def tokens_to_scene_graph(document: 'ParsedDocument', observer: 'Observer | None'=None, layout_mode: LayoutMode=LayoutMode.COMFORTABLE) -> SceneGraph
```

Convert a ParsedDocument to a SceneGraph.

### Examples
```python
>>> doc = parse_markdown("Check `self.brain.capture`")
```
```python
>>> scene = await tokens_to_scene_graph(doc)
```
```python
>>> rendered = ServoSceneRenderer(scene)
```

---

## markdown_to_scene_graph

```python
async def markdown_to_scene_graph(text: str, observer: 'Observer | None'=None, layout_mode: LayoutMode=LayoutMode.COMFORTABLE) -> SceneGraph
```

Convenience function: parse markdown and convert to SceneGraph.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## protocols.agentese.projection.warp_converters

## warp_converters

```python
module warp_converters
```

WARP Primitive → SceneGraph Converters.

---

## LivingEarthPalette

```python
class LivingEarthPalette
```

The Living Earth color palette.

---

## palette_to_hex

```python
def palette_to_hex(color: str) -> str
```

Convert palette color name to hex value.

---

## trace_node_to_scene

```python
def trace_node_to_scene(trace: Mark, *, animate: bool=True) -> SceneNode
```

Convert a Mark to a SceneNode.

---

## trace_timeline_to_scene

```python
def trace_timeline_to_scene(traces: Sequence[Mark], *, title: str='Trace Timeline', show_edges: bool=True) -> SceneGraph
```

Convert a sequence of Marks to a timeline SceneGraph.

---

## walk_to_scene

```python
def walk_to_scene(walk: Walk, *, include_traces: bool=False) -> SceneGraph
```

Convert a Walk to a SceneGraph.

---

## walk_dashboard_to_scene

```python
def walk_dashboard_to_scene(walks: Sequence[Walk], *, title: str='Walk Dashboard') -> SceneGraph
```

Convert multiple Walks to a dashboard SceneGraph.

---

## offering_to_scene

```python
def offering_to_scene(offering: Scope) -> SceneNode
```

Convert an Scope to a SceneNode.

---

## covenant_to_scene

```python
def covenant_to_scene(covenant: Grant) -> SceneNode
```

Convert a Grant to a SceneNode.

---

## ritual_to_scene

```python
def ritual_to_scene(ritual: Playbook, *, show_steps: bool=True) -> SceneGraph
```

Convert a Playbook to a SceneGraph.

---

## witness_dashboard_to_scene

```python
def witness_dashboard_to_scene(walks: Sequence[Walk], traces: Sequence[Mark], *, title: str='Witness Dashboard') -> SceneGraph
```

Create a comprehensive Witness dashboard SceneGraph.

---

## protocols.agentese.projection_adapter

## projection_adapter

```python
module projection_adapter
```

AGENTESE Projection Adapter.

---

## extract_ui_hint

```python
def extract_ui_hint(path: str, result: Any) -> UIHint | None
```

Extract UI hint from path and result type.

---

## is_deterministic_path

```python
def is_deterministic_path(path: str) -> bool
```

Check if a path is deterministic (cacheable).

---

## extract_observer_archetype

```python
def extract_observer_archetype(observer: 'Observer | Umwelt[Any, Any] | None') -> str | None
```

Extract archetype from observer.

---

## ProjectionAdapter

```python
class ProjectionAdapter
```

Adapter for invoking AGENTESE paths with projection envelopes.

---

## stream_with_projection

```python
async def stream_with_projection(logos: 'Logos', path: str, observer: 'Observer | Umwelt[Any, Any] | None'=None, **kwargs: Any) -> AsyncIterator[WidgetEnvelope[Any]]
```

Stream an AGENTESE path with projection envelopes.

---

## wrap_with_envelope

```python
def wrap_with_envelope(data: Any, path: str, observer: 'Observer | Umwelt[Any, Any] | None'=None, *, status: WidgetStatus=WidgetStatus.DONE, cache: CacheMeta | None=None, error: ErrorInfo | None=None, refusal: RefusalInfo | None=None, ui_hint: UIHint | None=None) -> WidgetEnvelope[Any]
```

Wrap raw data in a projection envelope.

---

## invoke_with_projection

```python
async def invoke_with_projection(self, path: str, observer: 'Observer | Umwelt[Any, Any] | None'=None, *, cache_hint: bool | None=None, stream_total: int | None=None, **kwargs: Any) -> WidgetEnvelope[Any]
```

Invoke an AGENTESE path and wrap result in projection envelope.

---

## protocols.agentese.query

## query

```python
module query
```

AGENTESE Query System

---

## QuerySyntaxError

```python
class QuerySyntaxError(PathSyntaxError)
```

Query pattern is malformed.

---

## QueryBoundError

```python
class QueryBoundError(Exception)
```

Query bounds exceeded.

---

## QueryMatch

```python
class QueryMatch
```

Single match from a query.

---

## QueryResult

```python
class QueryResult
```

Result of an AGENTESE query.

---

## QueryBuilder

```python
class QueryBuilder
```

Fluent query builder for AGENTESE queries.

---

## query

```python
def query(logos: 'Logos', pattern: str, *, limit: int=100, offset: int=0, tenant_id: str | None=None, observer: 'Observer | None'=None, capability_check: bool=True, dry_run: bool=False) -> QueryResult
```

Query the AGENTESE registry without invocation.

---

## add_query_to_logos

```python
def add_query_to_logos(logos_cls: type) -> None
```

Add query method to Logos class.

---

## create_query_builder

```python
def create_query_builder(logos: 'Logos') -> QueryBuilder
```

Create a QueryBuilder for fluent query construction.

---

## paths

```python
def paths(self) -> list[str]
```

Get just the path strings.

---

## __len__

```python
def __len__(self) -> int
```

Number of matches in this result (after pagination).

---

## __iter__

```python
def __iter__(self) -> Any
```

Iterate over matches.

---

## __bool__

```python
def __bool__(self) -> bool
```

True if any matches.

---

## pattern

```python
def pattern(self, p: str) -> 'QueryBuilder'
```

Set the query pattern.

---

## limit

```python
def limit(self, n: int) -> 'QueryBuilder'
```

Set the result limit (max 1000).

---

## offset

```python
def offset(self, n: int) -> 'QueryBuilder'
```

Set the pagination offset.

---

## tenant

```python
def tenant(self, tenant_id: str) -> 'QueryBuilder'
```

Filter by tenant ID.

---

## with_capability_check

```python
def with_capability_check(self, observer: 'Observer') -> 'QueryBuilder'
```

Enable capability checking with the given observer.

---

## without_capability_check

```python
def without_capability_check(self) -> 'QueryBuilder'
```

Disable capability checking.

---

## dry_run

```python
def dry_run(self, enabled: bool=True) -> 'QueryBuilder'
```

Enable dry-run mode (cost estimate only).

---

## execute

```python
def execute(self) -> QueryResult
```

Execute the query.

---

## query_method

```python
def query_method(self: 'Logos', pattern: str, **constraints: Any) -> QueryResult
```

Query the registry without invocation.

---

## protocols.agentese.registry

## registry

```python
module registry
```

AGENTESE Node Registry.

### Examples
```python
>>> @node("self.memory")
```
```python
>>> class BrainNode(BaseLogosNode):
```
```python
>>> '''Brain service AGENTESE node.'''
```
```python
>>> def __init__(self, crystal: BrainCrystal):
```
```python
>>> self._crystal = crystal
```

---

## NodeExample

```python
class NodeExample
```

A pre-seeded example invocation for a node.

### Things to Know

ℹ️ Examples are defined in @node decorator, not in node class. Pass examples=[(aspect, kwargs, label), ...] to @node().
  - *Verified in: `test_registry.py::TestNodeExamples`*

---

## NodeMetadata

```python
class NodeMetadata
```

Metadata attached to a node class by @node decorator.

### Things to Know

🚨 **Critical:** Dependencies are resolved by ServiceContainer at instantiation. If a dependency isn't registered, the node SILENTLY SKIPS! Always verify deps exist in providers.py.
  - *Verified in: `test_registry.py::test_resolve_dependent_node_fails_without_container`*

---

## node

```python
def node(path: str, *, description: str='', dependencies: tuple[str, ...]=(), singleton: bool=True, lazy: bool=True, contracts: 'ContractsDict | None'=None, examples: list[tuple[str, dict[str, Any]] | tuple[str, dict[str, Any], str] | NodeExample] | None=None) -> Callable[[type[T]], type[T]]
```

Decorator to register a LogosNode class with the AGENTESE registry.

### Examples
```python
>>> from protocols.agentese.contract import Contract, Response
```
```python
>>> @node(
```
```python
>>> "self.memory",
```
```python
>>> dependencies=("brain_crystal",),
```
```python
>>> contracts={
```

---

## is_node

```python
def is_node(cls: type[Any]) -> bool
```

Check if a class is decorated with @node.

---

## get_node_metadata

```python
def get_node_metadata(cls: type[Any]) -> NodeMetadata | None
```

Get node metadata from a decorated class.

---

## NodeRegistry

```python
class NodeRegistry
```

Central registry for AGENTESE nodes.

### Examples
```python
>>> registry = get_registry()
```
```python
>>> if registry.has("self.memory"):
```
```python
>>> node_cls = registry.get("self.memory")
```
```python
>>> node = await registry.resolve("self.memory", container)
```
```python
>>> paths = registry.list_paths()
```

### Things to Know

ℹ️ @node decorator runs at import time. If a module isn't imported, its node won't be registered. Call _import_node_modules() first (done automatically by gateway.mount_on()).
  - *Verified in: `test_registry.py::test_auto_registration`*

ℹ️ After reset_registry() in tests, call repopulate_registry() to restore nodes for subsequent tests on the same xdist worker.
  - *Verified in: `test_registry.py::TestNodeRegistry::test_clear + fixture pattern`*

---

## get_registry

```python
def get_registry() -> NodeRegistry
```

Get the global node registry.

---

## reset_registry

```python
def reset_registry() -> None
```

Reset the global registry (for testing).

---

## repopulate_registry

```python
def repopulate_registry() -> None
```

Re-register all @node decorated classes found in sys.modules.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for JSON serialization.

---

## decorator

```python
def decorator(cls: type[T]) -> type[T]
```

Apply @node metadata to class and register with global registry.

---

## has

```python
def has(self, path: str) -> bool
```

Check if a path is registered.

---

## get

```python
def get(self, path: str) -> type[Any] | None
```

Get the node class for a path.

---

## get_metadata

```python
def get_metadata(self, path: str) -> NodeMetadata | None
```

Get metadata for a path.

---

## resolve

```python
async def resolve(self, path: str, container: Any | None=None) -> 'LogosNode | None'
```

Resolve a path to an instantiated node.

---

## list_paths

```python
def list_paths(self) -> list[str]
```

List all registered paths.

---

## list_by_context

```python
def list_by_context(self, context: str) -> list[str]
```

List paths for a specific context.

---

## clear

```python
def clear(self) -> None
```

Clear all registrations (for testing).

---

## clear_instances

```python
def clear_instances(self) -> None
```

Clear cached instances but keep registrations.

---

## stats

```python
def stats(self) -> dict[str, Any]
```

Get registry statistics.

---

## get_contracts

```python
def get_contracts(self, path: str) -> 'ContractsDict | None'
```

Get contracts for a path.

---

## list_paths_with_contracts

```python
def list_paths_with_contracts(self) -> list[str]
```

List all paths that have contract declarations.

---

## get_all_contracts

```python
def get_all_contracts(self) -> dict[str, 'ContractsDict']
```

Get all contracts for all paths.

---

## protocols.agentese.renderings

## renderings

```python
module renderings
```

AGENTESE Phase 3: Polymorphic Renderings

### Examples
```python
>>> house = world.house
```
```python
>>> architect_view = await house.manifest(architect_umwelt)  # BlueprintRendering
```
```python
>>> poet_view = await house.manifest(poet_umwelt)  # PoeticRendering
```
```python
>>> economist_view = await house.manifest(economist_umwelt)  # EconomicRendering
```

---

## ScientificRendering

```python
class ScientificRendering
```

Scientific rendering for scientist archetypes.

---

## DeveloperRendering

```python
class DeveloperRendering
```

Technical rendering for developer archetypes.

---

## AdminRendering

```python
class AdminRendering
```

Operations rendering for admin archetypes.

---

## PhilosopherRendering

```python
class PhilosopherRendering
```

Conceptual rendering for philosopher archetypes.

---

## MemoryRendering

```python
class MemoryRendering
```

Memory rendering for self.* context.

---

## EntropyRendering

```python
class EntropyRendering
```

Entropy rendering for void.* context (Accursed Share).

---

## TemporalRendering

```python
class TemporalRendering
```

Temporal rendering for time.* context.

---

## RenderingFactory

```python
class RenderingFactory(Protocol)
```

Protocol for rendering factories.

---

## StandardRenderingFactory

```python
class StandardRenderingFactory
```

Factory for creating archetype-specific renderings.

---

## MemoryRenderingFactory

```python
class MemoryRenderingFactory
```

Factory for self.memory renderings.

---

## EntropyRenderingFactory

```python
class EntropyRenderingFactory
```

Factory for void.entropy renderings.

---

## TemporalRenderingFactory

```python
class TemporalRenderingFactory
```

Factory for time.* renderings.

---

## create_rendering_factory

```python
def create_rendering_factory() -> StandardRenderingFactory
```

Create a standard rendering factory.

---

## render_for_archetype

```python
def render_for_archetype(archetype: str, entity: str, state: dict[str, Any], factory: StandardRenderingFactory | None=None) -> Renderable
```

Convenience function to render an entity for an archetype.

---

## create

```python
def create(self, archetype: str, entity: str, state: dict[str, Any]) -> Renderable
```

Create a rendering for an archetype.

---

## create

```python
def create(self, archetype: str, entity: str, state: dict[str, Any]) -> Renderable
```

Create a rendering appropriate for the archetype.

---

## protocols.agentese.schema_gen

## schema_gen

```python
module schema_gen
```

JSON Schema Generation for AGENTESE Contracts.

---

## python_type_to_json_schema

```python
def python_type_to_json_schema(python_type: Type[Any]) -> dict[str, Any]
```

Convert a Python type to JSON Schema type definition.

---

## dataclass_to_schema

```python
def dataclass_to_schema(cls: Type[Any], include_descriptions: bool=True) -> dict[str, Any]
```

Convert a dataclass to JSON Schema.

---

## contract_to_schema

```python
def contract_to_schema(contract: ContractType) -> dict[str, Any]
```

Convert a Contract/Response/Request to JSON Schema dict.

---

## node_contracts_to_schema

```python
def node_contracts_to_schema(contracts: ContractsDict) -> dict[str, dict[str, Any]]
```

Convert all contracts for a node to JSON Schema dict.

---

## discovery_schema

```python
def discovery_schema(paths: dict[str, ContractsDict]) -> dict[str, dict[str, dict[str, Any]]]
```

Generate complete discovery schema for all paths.

---

## protocols.agentese.specgraph.__init__

## __init__

```python
module __init__
```

SpecGraph: Autopoietic Spec-Impl Compilation Infrastructure.

---

## protocols.agentese.specgraph.compile

## compile

```python
module compile
```

SpecGraph Compile Functor: Spec -> Impl generation.

---

## compile_spec

```python
def compile_spec(node: SpecNode, impl_root: Path, dry_run: bool=False) -> CompileResult
```

Compile a SpecNode into implementation files.

---

## protocols.agentese.specgraph.discovery

## discovery

```python
module discovery
```

SpecGraph Discovery: Spec-Driven Gap Detection and Stub Generation.

---

## GapSeverity

```python
class GapSeverity(str, Enum)
```

Severity of a spec-impl gap.

---

## ComponentType

```python
class ComponentType(str, Enum)
```

Types of components that can have gaps.

---

## Gap

```python
class Gap
```

A gap between what spec defines and what impl provides.

---

## DiscoveryReport

```python
class DiscoveryReport
```

Report of what specs define should exist.

---

## AuditReport

```python
class AuditReport
```

Report of gaps between spec and impl.

---

## StubResult

```python
class StubResult
```

Result of generating stubs for gaps.

---

## discover_from_spec

```python
def discover_from_spec(spec_root: Path) -> DiscoveryReport
```

Parse all specs with YAML frontmatter.

---

## audit_impl

```python
def audit_impl(impl_root: Path, discovery: DiscoveryReport) -> AuditReport
```

Compare what exists vs what spec says should exist.

---

## generate_stubs

```python
def generate_stubs(gaps: list[Gap], impl_root: Path, dry_run: bool=True) -> StubResult
```

Generate stubs only for MISSING components.

---

## full_audit

```python
def full_audit(spec_root: Path, impl_root: Path) -> tuple[DiscoveryReport, AuditReport]
```

Perform full discovery and audit in one call.

---

## print_audit_report

```python
def print_audit_report(audit: AuditReport, verbose: bool=False) -> str
```

Format audit report as human-readable string.

---

## alignment_score

```python
def alignment_score(self) -> float
```

Percentage of components that are aligned (0.0 - 1.0).

---

## protocols.agentese.specgraph.drift

## drift

```python
module drift
```

SpecGraph Drift Detection: Compare spec vs impl.

---

## check_drift

```python
def check_drift(spec_path: Path | None, impl_path: Path | None) -> DriftReport
```

Check drift between spec and impl.

---

## audit_all_jewels

```python
def audit_all_jewels(spec_root: Path, impl_root: Path) -> list[DriftReport]
```

Audit all Crown Jewels for drift.

---

## protocols.agentese.specgraph.parser

## parser

```python
module parser
```

**AGENTESE:** `path`

SpecGraph Parser: Parse YAML frontmatter from spec/*.md files.

---

## ParseError

```python
class ParseError(Exception)
```

Error parsing a spec file.

---

## parse_frontmatter

```python
def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]
```

Extract YAML frontmatter from markdown content.

---

## parse_polynomial

```python
def parse_polynomial(data: dict[str, Any] | None) -> PolynomialSpec | None
```

Parse polynomial specification from frontmatter.

---

## parse_operation

```python
def parse_operation(name: str, data: dict[str, Any]) -> OperationSpec
```

Parse a single operation spec.

---

## parse_law

```python
def parse_law(name: str, data: dict[str, Any] | str) -> LawSpec
```

Parse a single law spec.

---

## parse_operad

```python
def parse_operad(data: dict[str, Any] | None) -> OperadSpec | None
```

Parse operad specification from frontmatter.

---

## parse_sheaf

```python
def parse_sheaf(data: dict[str, Any] | None) -> SheafSpec | None
```

Parse sheaf specification from frontmatter.

---

## parse_aspect

```python
def parse_aspect(data: dict[str, Any] | str) -> AspectSpec | str
```

Parse a single aspect spec (can be simple string or rich dict).

---

## parse_agentese

```python
def parse_agentese(data: dict[str, Any] | None) -> AgentesePath | None
```

Parse AGENTESE path specification from frontmatter.

---

## parse_service

```python
def parse_service(data: dict[str, Any] | None) -> ServiceSpec | None
```

Parse service specification from frontmatter.

---

## parse_spec_file

```python
def parse_spec_file(path: Path) -> SpecNode
```

Parse a spec file into a SpecNode.

---

## parse_spec_directory

```python
def parse_spec_directory(spec_root: Path) -> SpecGraph
```

Parse all spec files in a directory into a SpecGraph.

---

## generate_frontmatter

```python
def generate_frontmatter(node: SpecNode) -> str
```

Generate YAML frontmatter from a SpecNode.

---

## protocols.agentese.specgraph.reflect

## reflect

```python
module reflect
```

SpecGraph Reflect Functor: Impl -> Spec extraction.

---

## reflect_polynomial

```python
def reflect_polynomial(path: Path) -> PolynomialSpec | None
```

Reflect polynomial spec from polynomial.py file.

---

## reflect_operad

```python
def reflect_operad(path: Path) -> OperadSpec | None
```

Reflect operad spec from operad.py file.

---

## reflect_node

```python
def reflect_node(path: Path) -> AgentesePath | None
```

Reflect AGENTESE path from node.py file.

---

## reflect_impl

```python
def reflect_impl(impl_path: Path) -> ReflectResult
```

Reflect specification from implementation directory.

---

## reflect_jewel

```python
def reflect_jewel(holon: str, impl_root: Path) -> ReflectResult
```

Reflect a Crown Jewel across multiple directories.

---

## reflect_crown_jewels

```python
def reflect_crown_jewels(impl_root: Path) -> dict[str, ReflectResult]
```

Reflect all Crown Jewels from impl directory.

---

## protocols.agentese.specgraph.types

## types

```python
module types
```

SpecGraph Types: Core data structures for spec-impl compilation.

---

## SpecDomain

```python
class SpecDomain(str, Enum)
```

Valid AGENTESE context domains.

---

## DriftStatus

```python
class DriftStatus(str, Enum)
```

Status of spec-impl alignment.

---

## PolynomialSpec

```python
class PolynomialSpec
```

Specification for a polynomial agent.

---

## OperationSpec

```python
class OperationSpec
```

Specification for an operad operation.

---

## LawSpec

```python
class LawSpec
```

Specification for an operad law.

---

## OperadSpec

```python
class OperadSpec
```

Specification for an operad.

---

## SheafSpec

```python
class SheafSpec
```

Specification for sheaf coherence.

---

## AspectCategory

```python
class AspectCategory(str, Enum)
```

Category of AGENTESE aspect (matching AspectCategory in affordances.py).

---

## AspectSpec

```python
class AspectSpec
```

Specification for a single AGENTESE aspect.

---

## AgentesePath

```python
class AgentesePath
```

AGENTESE path specification.

---

## ServiceSpec

```python
class ServiceSpec
```

Specification for Layer 4 service module (Crown Jewel pattern).

---

## SpecNode

```python
class SpecNode
```

A node in the SpecGraph.

---

## SpecGraph

```python
class SpecGraph
```

The dependency graph of specifications.

---

## CompileResult

```python
class CompileResult
```

Result of compiling a spec to impl.

---

## ReflectResult

```python
class ReflectResult
```

Result of reflecting impl to spec.

---

## DriftReport

```python
class DriftReport
```

Report of spec-impl drift for a single module.

---

## is_variadic

```python
def is_variadic(self) -> bool
```

Check if operation is variadic.

---

## get_aspect_names

```python
def get_aspect_names(self) -> tuple[str, ...]
```

Get all aspect names (from either simple or rich format).

---

## full_path

```python
def full_path(self) -> str
```

Full AGENTESE path (domain.holon).

---

## layer_count

```python
def layer_count(self) -> int
```

Count of implemented layers (1-7 scale).

---

## add

```python
def add(self, node: SpecNode) -> None
```

Add a node to the graph.

---

## get

```python
def get(self, path: str) -> SpecNode | None
```

Get a node by path.

---

## roots

```python
def roots(self) -> list[SpecNode]
```

Get nodes with no dependencies (compilation roots).

---

## protocols.agentese.subscription

## subscription

```python
module subscription
```

AGENTESE Subscription Manager

---

## EventType

```python
class EventType(Enum)
```

Type of event emitted by a subscription.

---

## AgentesEvent

```python
class AgentesEvent
```

Single event from an AGENTESE subscription.

---

## DeliveryMode

```python
class DeliveryMode(Enum)
```

Delivery guarantee mode.

---

## OrderingMode

```python
class OrderingMode(Enum)
```

Event ordering mode.

---

## SubscriptionConfig

```python
class SubscriptionConfig
```

Configuration for a subscription.

---

## Subscription

```python
class Subscription
```

Active subscription to AGENTESE paths.

---

## SubscriptionManager

```python
class SubscriptionManager
```

Manager for AGENTESE subscriptions.

---

## LogosSubscriptionMixin

```python
class LogosSubscriptionMixin
```

Mixin to add subscription methods to Logos.

---

## add_subscription_methods_to_logos

```python
def add_subscription_methods_to_logos(logos_cls: type) -> type
```

Add subscription methods to Logos class.

---

## SubscriptionMetrics

```python
class SubscriptionMetrics
```

Metrics for subscription observability.

---

## create_subscription_manager

```python
def create_subscription_manager(*, on_subscribe: Callable[[str, SubscriptionConfig], None] | None=None, on_unsubscribe: Callable[[str], None] | None=None, on_event: Callable[[str, AgentesEvent], None] | None=None) -> SubscriptionManager
```

Create a subscription manager with optional callbacks.

---

## invoked

```python
def invoked(cls, path: str, aspect: str, data: Any, observer_archetype: str='guest', trace_id: str | None=None) -> 'AgentesEvent'
```

Create an INVOKED event.

---

## changed

```python
def changed(cls, path: str, data: Any, observer_archetype: str='system') -> 'AgentesEvent'
```

Create a CHANGED event.

---

## error

```python
def error(cls, path: str, error: Exception, observer_archetype: str='system') -> 'AgentesEvent'
```

Create an ERROR event.

---

## refused

```python
def refused(cls, path: str, reason: str, observer_archetype: str='system') -> 'AgentesEvent'
```

Create a REFUSED event.

---

## heartbeat

```python
def heartbeat(cls) -> 'AgentesEvent'
```

Create a HEARTBEAT event.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize buffer with configured size.

---

## pattern

```python
def pattern(self) -> str
```

Get the subscription pattern.

---

## active

```python
def active(self) -> bool
```

Check if subscription is active.

---

## __aiter__

```python
async def __aiter__(self) -> AsyncIterator[AgentesEvent]
```

Async iteration over events.

---

## __aenter__

```python
async def __aenter__(self) -> 'Subscription'
```

Enter context manager.

---

## __aexit__

```python
async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> None
```

Exit context manager, close subscription.

---

## close

```python
async def close(self) -> None
```

Close the subscription.

---

## acknowledge

```python
def acknowledge(self, event_id: str) -> bool
```

Acknowledge receipt of an event (for AT_LEAST_ONCE).

---

## pending_count

```python
def pending_count(self) -> int
```

Get number of pending events in buffer.

---

## subscribe

```python
async def subscribe(self, pattern: str, *, delivery: DeliveryMode=DeliveryMode.AT_MOST_ONCE, ordering: OrderingMode=OrderingMode.PER_PATH_FIFO, buffer_size: int=1000, heartbeat_interval: float=30.0, replay_from: datetime | None=None, replay_offset: int | None=None, aspect: str | None=None) -> Subscription
```

Create a new subscription.

---

## unsubscribe

```python
async def unsubscribe(self, subscription_id: str) -> bool
```

Remove a subscription.

---

## subscription

```python
async def subscription(self, pattern: str, **kwargs: Any) -> AsyncIterator[Subscription]
```

Context manager for subscriptions.

---

## emit

```python
def emit(self, path: str, aspect: str, data: Any, observer_archetype: str='guest', event_type: EventType=EventType.INVOKED, trace_id: str | None=None) -> int
```

Emit an event to all matching subscriptions.

---

## emit_event

```python
def emit_event(self, event: AgentesEvent) -> int
```

Emit a pre-built event to all matching subscriptions.

---

## emit_invoked

```python
def emit_invoked(self, path: str, aspect: str, data: Any, observer_archetype: str='guest', trace_id: str | None=None) -> int
```

Convenience method to emit an INVOKED event.

---

## emit_changed

```python
def emit_changed(self, path: str, data: Any) -> int
```

Convenience method to emit a CHANGED event.

---

## emit_error

```python
def emit_error(self, path: str, error: Exception) -> int
```

Convenience method to emit an ERROR event.

---

## list_subscriptions

```python
def list_subscriptions(self) -> list[dict[str, Any]]
```

List all active subscriptions with their status.

---

## get_subscription

```python
def get_subscription(self, subscription_id: str) -> Subscription | None
```

Get a subscription by ID.

---

## subscription_count

```python
def subscription_count(self) -> int
```

Number of active subscriptions.

---

## close

```python
async def close(self) -> None
```

Close all subscriptions and cleanup.

---

## subscribe

```python
async def subscribe(self, pattern: str, **kwargs: Any) -> Subscription
```

Subscribe to AGENTESE path events.

---

## subscription

```python
async def subscription(self, pattern: str, **kwargs: Any) -> AsyncIterator[Subscription]
```

Context manager for subscriptions.

---

## subscribe

```python
async def subscribe(self: Any, pattern: str, **kwargs: Any) -> Subscription
```

Subscribe to AGENTESE path events.

---

## subscription

```python
async def subscription(self: Any, pattern: str, **kwargs: Any) -> AsyncIterator[Subscription]
```

Context manager for subscriptions.

---

## record_delivered

```python
def record_delivered(self, count: int=1) -> None
```

Record delivered events.

---

## record_dropped

```python
def record_dropped(self, count: int=1) -> None
```

Record dropped events.

---

## record_lag

```python
def record_lag(self, seconds: float) -> None
```

Record subscription lag.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Export as dictionary.

---

## protocols.agentese.telemetry

## telemetry

```python
module telemetry
```

AGENTESE Telemetry: OpenTelemetry Integration for Observability.

---

## get_tracer

```python
def get_tracer() -> Tracer
```

Get the AGENTESE tracer, creating if needed.

---

## TelemetryMiddleware

```python
class TelemetryMiddleware
```

Middleware that adds OpenTelemetry spans to AGENTESE invocations.

---

## trace_invocation

```python
async def trace_invocation(path: str, umwelt: Any, **extra_attributes: Any) -> AsyncIterator[Span]
```

Context manager for manually tracing an AGENTESE operation.

### Examples
```python
>>> async with trace_invocation("self.memory.consolidate", umwelt) as span:
```
```python
>>> span.set_attribute("memory.count", 42)
```
```python
>>> result = await do_consolidation()
```
```python
>>> span.set_attribute("consolidated", len(result))
```

---

## create_child_span

```python
def create_child_span(name: str, **attributes: Any) -> Span
```

Create a child span under the current trace context.

---

## add_event

```python
def add_event(name: str, attributes: dict[str, Any] | None=None) -> None
```

Add an event to the current span.

---

## set_attribute

```python
def set_attribute(key: str, value: Any) -> None
```

Set an attribute on the current span.

---

## __call__

```python
async def __call__(self, path: str, umwelt: Any, args: tuple[Any, ...], kwargs: dict[str, Any], next_handler: Callable[..., Awaitable[Any]]) -> Any
```

Wrap an AGENTESE invocation with tracing.

---

## protocols.agentese.telemetry_config

## telemetry_config

```python
module telemetry_config
```

Telemetry Configuration Loader.

---

## load_telemetry_config

```python
def load_telemetry_config(config_path: str | Path | None=None) -> TelemetryConfig
```

Load telemetry configuration from file or environment.

---

## setup_telemetry

```python
def setup_telemetry(config_path: str | Path | None=None, force: bool=False) -> bool
```

Load configuration and set up OpenTelemetry.

---

## setup_development_telemetry

```python
def setup_development_telemetry(trace_dir: str | Path | None=None, console: bool=True) -> None
```

Quick setup for development - JSON files + optional console output.

---

## setup_production_telemetry

```python
def setup_production_telemetry(otlp_endpoint: str | None=None, service_name: str='kgents', sampling_rate: float=0.1) -> None
```

Quick setup for production - OTLP export with sampling.

---

## generate_sample_config

```python
def generate_sample_config(output_path: str | Path | None=None) -> str
```

Generate a sample telemetry configuration file.

---

## ensure_config_directory

```python
def ensure_config_directory() -> Path
```

Ensure ~/.kgents directory exists.

---

## protocols.agentese.wiring

## wiring

```python
module wiring
```

**AGENTESE:** `protocols.agentese.wiring`

AGENTESE Phase 7: Wire to Logos

### Things to Know

ℹ️ WiredLogos validates paths by DEFAULT. Invalid paths raise PathSyntaxError before ever reaching resolution. To debug, check context (world/self/concept/ void/time), then holon, then aspect. Use validate_paths=False if you need to bypass validation (e.g., during testing or spec evolution).
  - *Verified in: `test_wiring.py::TestPathValidation::test_invalid_context_raises_error`*

ℹ️ Graceful degradation without L-gent registry. If create_wired_logos() is called without lgent_registry, tracking is silently disabled (track_usage=False is the default for create_minimal_wired_logos). Check integration_status() to see what's available.
  - *Verified in: `test_wiring.py::TestLgentIntegration::test_graceful_degradation_without_registry`*

ℹ️ Membrane bridge is AUTO-CREATED if not provided. The bridge connects CLI commands to AGENTESE paths. If you need to customize command mapping, pass your own MembraneAgenteseBridge to create_agentese_integrations().
  - *Verified in: `test_wiring.py::TestWiredLogosCreation::test_membrane_bridge_auto_created`*

ℹ️ invoke() accepts None observer (v3 API). Missing observer defaults to guest archetype. This won't raise ObserverRequiredError, but the guest may lack affordances for the requested aspect.
  - *Verified in: `test_wiring.py::TestInvoke::test_invoke_accepts_none_observer`*

---

## WiredLogos

```python
class WiredLogos
```

Logos resolver with Phase 6 integrations wired in.

### Examples
```python
>>> wired = create_wired_logos(lgent_registry=registry)
```
```python
>>> # Validation happens automatically
```
```python
>>> result = await wired.invoke("world.house.manifest", observer)
```
```python
>>> # Usage is tracked in L-gent
```
```python
>>> # Observer meta extracted via UmweltIntegration
```

---

## create_wired_logos

```python
def create_wired_logos(spec_root: Path | str='spec', lgent_registry: Any | None=None, grammarian: Any | None=None, narrator: Any=None, d_gent: Any=None, b_gent: Any=None, validate_paths: bool=True, track_usage: bool=True) -> WiredLogos
```

Create a fully wired Logos resolver.

---

## wire_existing_logos

```python
def wire_existing_logos(logos: Logos, lgent_registry: Any | None=None, grammarian: Any | None=None, validate_paths: bool=True, track_usage: bool=True) -> WiredLogos
```

Wire integrations to an existing Logos instance.

---

## create_minimal_wired_logos

```python
def create_minimal_wired_logos(spec_root: Path | str='spec') -> WiredLogos
```

Create a minimal WiredLogos without external integrations.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Wire membrane bridge to this logos.

---

## resolve

```python
def resolve(self, path: str, observer: 'Umwelt[Any, Any] | None'=None) -> LogosNode
```

Resolve an AGENTESE path with G-gent validation and L-gent lookup.

---

## lift

```python
def lift(self, path: str) -> 'Any'
```

Convert a handle into a composable Agent.

---

## invoke

```python
async def invoke(self, path: str, observer: 'Umwelt[Any, Any] | Observer | None'=None, **kwargs: Any) -> Any
```

Invoke an AGENTESE path with full integration support.

---

## compose

```python
def compose(self, *paths: str, enforce_output: bool=True) -> ComposedPath
```

Create a composed path with validation.

---

## identity

```python
def identity(self) -> IdentityPath
```

Get identity morphism.

---

## path

```python
def path(self, p: str) -> ComposedPath
```

Create single-path composition.

---

## register

```python
def register(self, handle: str, node: LogosNode) -> None
```

Register a node (delegates to Logos).

---

## execute_membrane_command

```python
async def execute_membrane_command(self, command: str, observer: 'Umwelt[Any, Any]', **kwargs: Any) -> Any
```

Execute a Membrane CLI command via AGENTESE.

---

## get_agentese_path

```python
def get_agentese_path(self, command: str) -> str | None
```

Get the AGENTESE path for a Membrane command without executing.

---

## define_concept

```python
async def define_concept(self, handle: str, spec: str, observer: 'Umwelt[Any, Any]') -> LogosNode
```

Create a new concept with L-gent registration.

---

## promote_concept

```python
async def promote_concept(self, handle: str, threshold: int=100, success_threshold: float=0.8) -> Any
```

Promote a JIT node (delegates to Logos).

---

## get_jit_status

```python
def get_jit_status(self, handle: str) -> dict[str, Any] | None
```

Get JIT node status.

---

## list_jit_nodes

```python
def list_jit_nodes(self) -> list[dict[str, Any]]
```

List all JIT nodes.

---

## list_handles

```python
def list_handles(self, context: str | None=None) -> list[str]
```

List registered handles.

---

## is_resolved

```python
def is_resolved(self, path: str) -> bool
```

Check if path is cached.

---

## clear_cache

```python
def clear_cache(self) -> None
```

Clear caches.

---

## integration_status

```python
def integration_status(self) -> dict[str, bool]
```

Get status of all integrations.

---

*1696 symbols, 45 teaching moments*

*Generated by Living Docs — 2025-12-21*