# The CLI: Isomorphic Projection of AGENTESE

**Status:** Specification v3.0
**Supersedes:** CLI v2.0
**Date:** 2025-12-17

---

## Epigraph

> *"The CLI is not a separate interface. It is a projection of AGENTESE onto the terminal."*
>
> *"If you register an aspect correctly, the CLI just works."*

---

## Part I: Core Philosophy

### 1.1 The Fundamental Claim

**The CLI is not a protocol. It is a projection functor.**

Every CLI command is a projection of an AGENTESE path. There are no "CLI-specific" behaviors—all behavior derives from the path's aspect metadata. This is not aspirational; it is architectural.

```
CLIProject : (Path, Observer) → Renderable[Terminal]
```

Where:
- `Path` is a valid AGENTESE path (e.g., `self.forest.manifest`)
- `Observer` is the CLI user's umwelt
- `Renderable[Terminal]` is the terminal-appropriate output

### 1.2 What This Guarantees

1. **No orphan handlers**: Every CLI command maps to exactly one AGENTESE path
2. **Automatic UX**: Async wrappers, state loading, confirmation dialogs derive from aspects
3. **Uniform help**: `path.affordances` provides all docstrings
4. **Traceable**: OTEL spans generated uniformly for all invocations
5. **AI-safe**: Registration validates completeness—AI agents cannot misconfigure

### 1.3 The Three Laws of Isomorphic CLI

**Law 1: Paths Are Commands**

Every CLI command IS an AGENTESE path. The CLI surface is a projection, not a mapping.

```bash
# These are identical:
kg self.forest.manifest
kg /forest              # Shortcut expansion
kg forest status        # Legacy expansion

# All resolve to the same AGENTESE invocation
await logos.invoke("self.forest.manifest", cli_observer)
```

**Law 2: Aspects Determine Behavior**

The aspect metadata (category, effects, flags) determines all runtime behavior:
- Sync vs async execution
- State loading requirements
- Confirmation dialogs
- Budget display
- Error handling style

**Law 3: Dimensions Are Explicit**

Every behavioral dimension is named and declared, not scattered as conditionals.

---

## Part II: The Command Dimension Space

### 2.1 The Product Space

CLI commands exist in a 6-dimensional product space:

```
CommandSpace = Execution × Statefulness × Backend × Intent × Seriousness × Interactivity
```

| Dimension | Values | Derived From |
|-----------|--------|--------------|
| **Execution** | `sync`, `async` | AspectCategory |
| **Statefulness** | `stateless`, `stateful` | Effect.READS/WRITES |
| **Backend** | `pure`, `llm`, `external` | Effect.CALLS |
| **Intent** | `functional`, `instructional` | Aspect presence |
| **Seriousness** | `sensitive`, `playful`, `neutral` | Path context + flag |
| **Interactivity** | `oneshot`, `streaming`, `interactive` | Aspect + flags |

### 2.2 Dimension Derivation Rules

#### From AspectCategory

| Category | Execution | Statefulness | Typical Backend |
|----------|-----------|--------------|-----------------|
| `PERCEPTION` | sync | stateless | pure |
| `MUTATION` | async | stateful | varies |
| `GENERATION` | async | stateful | llm |
| `COMPOSITION` | sync | stateless | pure |
| `INTROSPECTION` | sync | stateless | pure |
| `ENTROPY` | sync | stateless | pure |

#### From Effects

| Effect | Dimension Impact |
|--------|-----------------|
| `READS(resource)` | Statefulness → stateful (read) |
| `WRITES(resource)` | Statefulness → stateful (write), requires confirmation if `FORCES` |
| `CALLS(target)` | Backend → llm or external, show budget |
| `CHARGES(amount)` | Show cost warning |
| `FORCES` | Requires explicit consent |
| `AUDITS` | Log decision rationale |

#### Seriousness Derivation

Seriousness is derived from context + explicit flag:

```python
def derive_seriousness(path: str, effects: list[Effect]) -> Seriousness:
    # Sensitive if writes to protected resources
    if any(e.resource in PROTECTED_RESOURCES for e in effects if isinstance(e, Effect.WRITES)):
        return Seriousness.SENSITIVE

    # Playful if from void.* context
    if path.startswith("void."):
        return Seriousness.PLAYFUL

    # Sensitive if forces consent
    if Effect.FORCES in effects:
        return Seriousness.SENSITIVE

    return Seriousness.NEUTRAL
```

### 2.3 The Simplifying Isomorphism (AD-008 Applied)

Just as screen density replaced scattered `isMobile` checks, command dimensions replace scattered behavioral checks:

```python
# Anti-pattern: Scattered conditionals
if is_async_command(name):
    result = await run_async(handler, args)
else:
    result = handler(args)

if requires_state(name):
    state = load_state()

if is_llm_backed(name):
    show_budget_warning()

# Pattern: Dimension-derived behavior
dimensions = derive_dimensions(path)
result = await cli_project(path, observer, dimensions)
```

The dimension derivation is the **single source of truth**. No scattered conditionals remain.

---

## Part III: The CLI Projection Functor

### 3.1 Functor Definition

```python
@dataclass(frozen=True)
class CLIProjection:
    """
    The CLI projection functor.

    Maps (Path, Observer, Dimensions) → Terminal output with
    appropriate async handling, state management, and UX.
    """

    async def project(
        self,
        path: str,
        observer: Observer,
        dimensions: CommandDimensions,
        kwargs: dict[str, Any],
    ) -> TerminalOutput:
        """
        Project an AGENTESE path to terminal output.

        The projection handles:
        1. Async wrapping (if dimensions.execution == async)
        2. State loading (if dimensions.statefulness == stateful)
        3. Budget display (if dimensions.backend == llm)
        4. Confirmation (if dimensions.seriousness == sensitive)
        5. Streaming (if dimensions.interactivity == streaming)
        """
        ...
```

### 3.2 Projection Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLI PROJECTION PIPELINE                              │
│                                                                              │
│   Input: "kg self.forest.manifest --json"                                   │
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │    Parse     │───▶│   Resolve    │───▶│   Derive     │                  │
│   │   (Router)   │    │   (Logos)    │    │ (Dimensions) │                  │
│   └──────────────┘    └──────────────┘    └──────────────┘                  │
│          │                   │                   │                           │
│          ▼                   ▼                   ▼                           │
│   ClassifiedInput      AspectMeta         CommandDimensions                 │
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │   Pre-UX     │───▶│   Invoke     │───▶│  Post-UX     │                  │
│   │ (confirm,    │    │   (Logos)    │    │ (render,     │                  │
│   │  budget)     │    │              │    │  trace)      │                  │
│   └──────────────┘    └──────────────┘    └──────────────┘                  │
│          │                   │                   │                           │
│          ▼                   ▼                   ▼                           │
│   Consent/Budget         Result            TerminalOutput                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Dimension-Driven UX

Each dimension drives specific UX behavior:

#### Execution Dimension

```python
match dimensions.execution:
    case Execution.SYNC:
        result = logos.invoke_sync(path, observer, **kwargs)
    case Execution.ASYNC:
        result = await logos.invoke(path, observer, **kwargs)
```

#### Statefulness Dimension

```python
match dimensions.statefulness:
    case Statefulness.STATELESS:
        pass  # No state management
    case Statefulness.STATEFUL:
        async with state_context(path, observer) as ctx:
            result = await logos.invoke(path, observer, state=ctx, **kwargs)
```

#### Backend Dimension

```python
match dimensions.backend:
    case Backend.PURE:
        pass  # No cost warning
    case Backend.LLM:
        if not quiet_mode:
            emit_budget_indicator(observer.budget)
    case Backend.EXTERNAL:
        if not quiet_mode:
            emit_external_call_warning(dimensions.effects)
```

#### Seriousness Dimension

```python
match dimensions.seriousness:
    case Seriousness.SENSITIVE:
        if not force_flag:
            consent = await request_consent(path, dimensions.effects)
            if not consent:
                return Refusal(reason="User declined")
    case Seriousness.PLAYFUL:
        # Errors are gentle, serendipity welcome
        error_style = ErrorStyle.GENTLE
    case Seriousness.NEUTRAL:
        pass
```

#### Interactivity Dimension

```python
match dimensions.interactivity:
    case Interactivity.ONESHOT:
        result = await invoke_once(path, observer, **kwargs)
    case Interactivity.STREAMING:
        async for chunk in invoke_stream(path, observer, **kwargs):
            emit_chunk(chunk)
    case Interactivity.INTERACTIVE:
        await run_repl(path, observer)
```

---

## Part IV: Registration Protocol

### 4.1 The Aspect Decorator (Extended)

Every AGENTESE path that should be CLI-accessible MUST declare full aspect metadata:

```python
@logos.node("self.forest")
class ForestNode:
    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("forest_state")],
        seriousness=Seriousness.NEUTRAL,  # Optional, derived if omitted
        streaming=False,                   # Optional, default False
        help="Display forest status and health metrics",
        examples=[
            "kg self.forest.manifest",
            "kg /forest",
        ],
    )
    async def manifest(self, observer: Observer, **kwargs) -> ForestManifest:
        """Show the current forest state."""
        ...

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[
            Effect.WRITES("forest_state"),
            Effect.CALLS("llm"),
        ],
        seriousness=Seriousness.SENSITIVE,
        help="Prune completed or stale plans from the forest",
    )
    async def prune(self, observer: Observer, plan_ids: list[str]) -> PruneResult:
        """Remove specified plans from the forest."""
        ...
```

### 4.2 Registration Validation

At registration time, the system validates:

```python
def validate_aspect_registration(node_path: str, aspect_meta: AspectMeta) -> list[ValidationError]:
    errors = []

    # 1. Category is required
    if aspect_meta.category is None:
        errors.append(ValidationError(
            f"{node_path}: AspectCategory required for CLI exposure"
        ))

    # 2. Effects must be declared for MUTATION/GENERATION
    if aspect_meta.category in (AspectCategory.MUTATION, AspectCategory.GENERATION):
        if not aspect_meta.effects:
            errors.append(ValidationError(
                f"{node_path}: MUTATION/GENERATION aspects must declare effects"
            ))

    # 3. Help text required
    if not aspect_meta.help:
        errors.append(ValidationError(
            f"{node_path}: Help text required for CLI exposure"
        ))

    # 4. CALLS effect requires budget estimation
    if Effect.CALLS in aspect_meta.effects:
        if aspect_meta.budget_estimate is None:
            errors.append(ValidationError(
                f"{node_path}: LLM-backed aspects must estimate budget"
            ))

    return errors
```

### 4.3 The AI-Safety Guarantee

Because registration validates completeness, AI agents constructing CLI commands cannot:

1. **Create orphan commands** - Every command must map to a registered path
2. **Forget effect declarations** - MUTATION aspects won't register without effects
3. **Skip help text** - Registration requires documentation
4. **Hide LLM costs** - CALLS effects require budget estimates

```python
# AI agent constructing a new command:
# This WILL FAIL at registration if incomplete

@logos.node("world.thing")
class ThingNode:
    @aspect(category=AspectCategory.MUTATION)  # FAILS: no effects
    async def transform(self, observer):
        ...

# Registration error:
# ValidationError: world.thing.transform: MUTATION aspects must declare effects
```

---

## Part V: Instructional Flow (Help System)

### 5.1 Help as Affordances Projection

Help text is not separate documentation—it is the `affordances` aspect projected to terminal:

```bash
kg self.forest.?           # Query affordances
kg self.forest.affordances # Explicit affordances call
kg help self.forest        # Legacy alias
```

All three produce:

```
self.forest.*

Aspects:
  manifest     [PERCEPTION]  Display forest status and health metrics
  prune        [MUTATION]    Prune completed or stale plans (requires confirmation)
  plant        [GENERATION]  Plant a new plan in the forest
  witness      [PERCEPTION]  Show forest history

Effects:
  manifest:  reads(forest_state)
  prune:     writes(forest_state), calls(llm)
  plant:     writes(forest_state), calls(llm), charges(tokens)

Examples:
  kg self.forest.manifest
  kg self.forest.prune --plan-id abc123
  kg /forest
```

### 5.2 Docstring Extraction

The `help` field in aspects feeds the help system:

```python
@aspect(
    category=AspectCategory.MUTATION,
    effects=[Effect.WRITES("forest"), Effect.CALLS("llm")],
    help="Prune completed or stale plans from the forest",
    long_help="""
    Removes plans that are either:
    - Marked as complete (100% progress)
    - Stale (no updates in configured timeout)
    - Explicitly specified by --plan-id

    This operation requires confirmation unless --force is passed.
    """,
    examples=[
        ("Prune all complete plans", "kg self.forest.prune --complete"),
        ("Prune specific plan", "kg self.forest.prune --plan-id abc123"),
        ("Force prune without confirmation", "kg self.forest.prune --complete --force"),
    ],
)
async def prune(self, observer: Observer, **kwargs) -> PruneResult:
    ...
```

### 5.3 Context-Sensitive Help

Help adapts to observer capabilities:

```python
def project_help(path: str, observer: Observer) -> str:
    affordances = logos.query(f"?{path}.*")

    # Filter to what this observer can access
    accessible = [a for a in affordances if observer.can_access(a)]

    # Render with observer-appropriate detail level
    if observer.archetype == "novice":
        return render_simple_help(accessible)
    else:
        return render_full_help(accessible)
```

---

## Part VI: Error Projection

### 6.1 Sympathetic Errors

Errors are projected with dimension-appropriate sympathy:

```python
def project_error(
    error: AgentError,
    dimensions: CommandDimensions,
) -> TerminalOutput:
    match dimensions.seriousness:
        case Seriousness.PLAYFUL:
            # Gentle, encouraging
            return f"Hmm, that didn't quite work: {error.message}\n\nMaybe try: {error.suggested_action}"
        case Seriousness.SENSITIVE:
            # Serious, precise
            return f"Error [{error.code}]: {error.message}\n\nRecovery: {error.suggested_action}\nTrace: {error.trace_id}"
        case Seriousness.NEUTRAL:
            return f"Error: {error.message}\n\nTry: {error.suggested_action}"
```

### 6.2 Error Categories to Exit Codes

```python
ERROR_TO_EXIT: dict[ErrorCategory, int] = {
    ErrorCategory.INVALID_INPUT: 1,
    ErrorCategory.UNAUTHORIZED: 2,
    ErrorCategory.FORBIDDEN: 3,
    ErrorCategory.NOT_FOUND: 4,
    ErrorCategory.CONFLICT: 5,
    ErrorCategory.QUOTA_EXCEEDED: 6,
    ErrorCategory.TIMEOUT: 7,
    ErrorCategory.UNAVAILABLE: 8,
    ErrorCategory.INTERNAL: 9,
}
```

---

## Part VII: The Hollow Shell (Preserved from v2)

### 7.1 Lazy Loading

The CLI loads in <50ms through lazy resolution. Commands are registered as module paths, not imports:

```python
COMMAND_REGISTRY = {
    "self.forest.manifest": "agents.forest:ForestNode.manifest",
    "self.soul.dialogue": "agents.k.soul:SoulNode.dialogue",
    # ...
}

def resolve_handler(path: str) -> Callable:
    """Import only the invoked path's module."""
    if path not in COMMAND_REGISTRY:
        raise PathNotFoundError(path)

    module_path, method_path = COMMAND_REGISTRY[path].rsplit(":", 1)
    module = importlib.import_module(module_path)
    return rgetattr(module, method_path)
```

### 7.2 Shortcut and Legacy Expansion

For backwards compatibility and convenience:

```python
SHORTCUTS = {
    "/forest": "self.forest.manifest",
    "/soul": "self.soul.dialogue",
    "/brain": "self.memory.manifest",
    "/town": "world.town.manifest",
    "/surprise": "void.entropy.sip",
}

LEGACY_COMMANDS = {
    ("forest", "status"): "self.forest.manifest",
    ("forest", "prune"): "self.forest.prune",
    ("soul", "challenge"): "self.soul.challenge",
    # ...
}
```

Expansion happens at the router layer, before dimension derivation.

---

## Part VIII: Observability

### 8.1 Uniform Tracing

Every CLI invocation generates an OTEL span:

```python
span.set_attributes({
    "agentese.path": path,
    "agentese.category": dimensions.category.value,
    "agentese.execution": dimensions.execution.value,
    "agentese.statefulness": dimensions.statefulness.value,
    "agentese.backend": dimensions.backend.value,
    "agentese.seriousness": dimensions.seriousness.value,
    "cli.input_type": classified.input_type,
    "cli.original": classified.original,
})
```

### 8.2 Metrics

```python
# Counters
agentese_cli_invocations_total{path, category, execution, status}
agentese_cli_errors_total{path, error_category}

# Histograms
agentese_cli_duration_seconds{path, category}

# Gauges
agentese_cli_active_streams{path}
```

### 8.3 The --trace Flag

```bash
kg self.forest.manifest --trace

# Output includes:
# ...normal output...
#
# Trace: abc123def456
# Duration: 42ms
# Dimensions: PERCEPTION/sync/stateful/pure/neutral/oneshot
```

---

## Part IX: Implementation Contract

### 9.1 What The CLI Must Do

1. **Derive all behavior from aspects** - No hardcoded behavioral conditionals
2. **Validate registrations** - Reject incomplete aspect metadata
3. **Project uniformly** - Same functor for all paths
4. **Trace everything** - OTEL spans for every invocation
5. **Fail sympathetically** - Dimension-appropriate error messages

### 9.2 What The CLI Must Not Do

1. **Bypass Logos** - All invocations go through `logos.invoke()`
2. **Scatter conditionals** - Dimensions are the single source of truth
3. **Hide information** - Effects, costs, traces are visible
4. **Break composition** - `path >> path` works uniformly
5. **Require manual wiring** - Aspects auto-derive CLI behavior

---

## Part X: Migration Path

### 10.1 From Current Handlers

Current handlers (44 files in `impl/claude/protocols/cli/handlers/`) migrate in waves:

| Wave | Handlers | Pattern |
|------|----------|---------|
| 1 | Crown Jewels (brain, soul, town, atelier) | Full aspect metadata |
| 2 | Forest Protocol (forest, grow, tend) | Already AGENTESE-native |
| 3 | Joy Commands (challenge, oblique, surprise) | Add seriousness=playful |
| 4 | Soul Extensions (why, tension, flinch) | Add effects declarations |
| 5 | Query/Subscribe (query, subscribe, daemon) | Add streaming support |
| 6 | New Paths (nphase, approve, tether) | New node registration |

### 10.2 Migration Checklist Per Handler

```markdown
- [ ] Identify AGENTESE path (from COMMAND_TO_PATH or create new)
- [ ] Add @aspect decorator with:
  - [ ] category (required)
  - [ ] effects (required for MUTATION/GENERATION)
  - [ ] seriousness (optional, derived if omitted)
  - [ ] help (required)
  - [ ] examples (recommended)
- [ ] Remove handler-specific async wrappers (use dimension-derived)
- [ ] Remove handler-specific state loading (use dimension-derived)
- [ ] Remove handler-specific confirmation dialogs (use dimension-derived)
- [ ] Add to shortcut registry if warranted
- [ ] Add to legacy registry for backwards compatibility
- [ ] Verify with: kg <path> --dry-run
```

---

## Part XI: Success Metrics

| Metric | Target |
|--------|--------|
| Handlers with full aspect metadata | 100% |
| Behavioral conditionals in handlers | 0 |
| Dimension derivation coverage | 100% |
| Help text coverage | 100% |
| OTEL trace coverage | 100% |
| AI registration validation | All paths pass |
| Startup time | <50ms |

---

## Part XII: Anti-Patterns

### What We Reject

1. **Handler-specific async wrappers** - Use dimension-derived execution
2. **Scattered `is_sensitive()` checks** - Use seriousness dimension
3. **Manual budget warnings** - Use backend dimension + CALLS effect
4. **Hardcoded confirmation dialogs** - Use FORCES effect
5. **Separate help system** - Use affordances projection
6. **Handler bypass of Logos** - All paths through `logos.invoke()`

### The Isomorphism Test

> If two paths have the same dimensions, they MUST have identical CLI behavior (modulo content).

Violations indicate scattered conditionals that should be eliminated.

---

## Appendix A: Dimension Reference

### A.1 Execution

| Value | Meaning | Derived When |
|-------|---------|--------------|
| `sync` | Blocking call | PERCEPTION, COMPOSITION, INTROSPECTION, ENTROPY |
| `async` | Non-blocking | MUTATION, GENERATION, or Effect.CALLS present |

### A.2 Statefulness

| Value | Meaning | Derived When |
|-------|---------|--------------|
| `stateless` | No state context | No READS/WRITES effects |
| `stateful` | Load/save state | READS or WRITES effects present |

### A.3 Backend

| Value | Meaning | Derived When |
|-------|---------|--------------|
| `pure` | No external calls | No CALLS effect |
| `llm` | LLM call | Effect.CALLS("llm") |
| `external` | External API | Effect.CALLS("api") or similar |

### A.4 Seriousness

| Value | Meaning | Derived When |
|-------|---------|--------------|
| `sensitive` | Errors loud, confirmation required | FORCES effect, protected resources |
| `playful` | Errors gentle, serendipity welcome | void.* context |
| `neutral` | Standard behavior | Default |

### A.5 Interactivity

| Value | Meaning | Derived When |
|-------|---------|--------------|
| `oneshot` | Single invocation | Default |
| `streaming` | Continuous output | streaming=True in aspect |
| `interactive` | REPL mode | interactive=True in aspect |

---

## Appendix B: Standard Dimensions by Path

| Path Pattern | Execution | Statefulness | Backend | Seriousness | Interactivity |
|--------------|-----------|--------------|---------|-------------|---------------|
| `self.*.manifest` | sync | stateful | pure | neutral | oneshot |
| `self.soul.*` | async | stateful | llm | neutral | oneshot |
| `self.soul.chat.*` | async | stateful | llm | neutral | **interactive** |
| `self.memory.*` | async | stateful | varies | neutral | oneshot |
| `world.town.*` | async | stateful | llm | playful | oneshot |
| `world.town.citizen.*.chat.*` | async | stateful | llm | playful | **interactive** |
| `concept.*.refine` | async | stateless | llm | neutral | oneshot |
| `void.*` | sync | stateless | pure | playful | oneshot |
| `time.trace.*` | sync | stateful | pure | neutral | oneshot |

### B.1 Interactive Mode

Paths with `Interactivity.INTERACTIVE` trigger REPL mode in CLI:

```bash
# These enter interactive chat mode:
kg self.soul.chat
kg world.town.citizen.elara.chat

# Bypass with one-shot flag:
kg self.soul.chat --message "Quick question"
```

See `spec/protocols/chat.md` for full chat protocol specification.

---

*"The CLI that understands its dimensions needs no configuration. The projection is automatic."*

*Last updated: 2025-12-17*
