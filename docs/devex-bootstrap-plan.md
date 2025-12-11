# DevEx Bootstrap Plan v2: The Kgents MCP Sidecar

**Status**: Draft v2 | Incorporates critique on friction, latency, and echo chambers
**Architecture**: Sidecar model via MCP, not middleware interception
**Goal**: kgents as a **living environment** Claude Code inhabits, not a tool it calls

---

## The Critique That Changed Everything

The v1 plan had a fatal flaw: **middleware friction**.

| Problem | v1 Approach | Why It Fails |
|---------|-------------|--------------|
| **Latency** | Pipeline: I → N → O → K → Response | 500ms+ delay feels like broken software |
| **Integration** | Custom CLI hooks | Can't inject into Claude Code's reasoning loop |
| **Echo Chamber** | K-gent mimics Kent | Learns bad habits, amplifies them |

**The Fix**: Shift from **blocking middleware** to **async sidecar** using MCP.

---

## The Sidecar Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     THE KGENTS ENVIRONMENT                               │
│                                                                         │
│   ┌─────────────────────┐              ┌─────────────────────────────┐ │
│   │    Claude Code      │◀────MCP────▶│      kgents MCP Server       │ │
│   │  (Developer's IDE)  │              │                             │ │
│   └─────────────────────┘              │  Resources:                 │ │
│            │                           │    kgents://field/current   │ │
│            │                           │    kgents://priors/kent     │ │
│            │                           │    kgents://health/system   │ │
│            │                           │                             │ │
│            │                           │  Prompts:                   │ │
│            ▼                           │    kgents-persona           │ │
│   ┌─────────────────────┐              │    kgents-context           │ │
│   │  Developer (Kent)   │              │                             │ │
│   │                     │              │  Tools:                     │ │
│   │  Intent → Response  │              │    kgents_invoke            │ │
│   │  (zero friction)    │              │    kgents_evolve            │ │
│   └─────────────────────┘              └─────────────────────────────┘ │
│                                                    ▲                   │
│                                                    │                   │
│   ┌────────────────────────────────────────────────┼──────────────────┐│
│   │              BACKGROUND SIDECAR DAEMONS        │                  ││
│   │                                                │                  ││
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐              ││
│   │  │ O-gent  │  │ N-gent  │  │ I-gent  │  │ K-gent  │              ││
│   │  │ Watcher │  │ Scribe  │  │ Mapper  │  │ Coach   │──────────────┘│
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘               │
│   │      │            │            │            │                     │
│   │      └────────────┴────────────┴────────────┘                     │
│   │                        │                                          │
│   │              Pre-computed context                                 │
│   │              (always "hot")                                       │
│   └───────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

**Key insight**: Claude doesn't *call* kgents. Claude *perceives* kgents. The context is already there.

---

## The Three Laws of DevEx Sidecar

### 1. Never Block the Critical Path
> If it takes >100ms, it must be pre-computed.

O-gent, N-gent, I-gent run as background daemons. When Claude asks "what's the context?", the answer is instant because it was computed when you saved the file.

### 2. Inject Context, Don't Intercept Commands
> The MCP prompt `kgents-persona` pre-loads K-gent wisdom into every interaction.

Claude starts with your priors already in its system prompt. You don't ask for personalization - it's ambient.

### 3. Coach, Don't Just Mirror
> K-gent has two modes: **Mirror** (mimic style) and **Coach** (challenge toward Ideal Kent).

The system acts virtuously when it pushes toward the *Ideal Kent*, not the *Tired Kent*.

---

## Phase 1: MCP Foundation (Week 1)

### 1.1 Extend Existing MCP Server

The MCP server exists at `protocols/cli/mcp/server.py`. Extend it with DevEx resources and prompts.

**New MCP Resources**:

```python
# protocols/cli/mcp/devex_resources.py

from mcp.server import resource

@resource("kgents://field/current")
async def get_current_field():
    """
    The Development Field - where you are in the codebase.

    Returns spatial map of:
    - Current focus (file/function)
    - Related entities (imports, callers, callees)
    - Tension zones (spec/impl mismatches)
    """
    return await i_gent.render_field_state()


@resource("kgents://priors/kent")
async def get_kent_priors():
    """
    K-gent priors - Kent's accumulated preferences.

    Returns:
    - style_preferences: {"naming": "biological_metaphors", ...}
    - active_metaphors: ["composting", "bicameral", ...]
    - confidence_levels: {"naming": 0.85, ...}
    """
    return await k_gent.get_priors()


@resource("kgents://history/recent")
async def get_recent_history():
    """
    N-gent crystals - recent session context.

    Returns:
    - last_session_summary: str
    - open_decisions: [Decision, ...]
    - recent_patterns: [Pattern, ...]
    """
    return await n_gent.get_recent_crystals(days=7)


@resource("kgents://health/system")
async def get_system_health():
    """
    O-gent telemetry - current system state.

    Returns:
    - test_status: {"passed": 6122, "failed": 0}
    - coverage: 0.87
    - last_run: "2025-01-15T10:30:00"
    - alerts: []
    """
    return await o_gent.get_health_snapshot()
```

**New MCP Prompts**:

```python
# protocols/cli/mcp/devex_prompts.py

from mcp.server import prompt

@prompt("kgents-persona")
async def get_persona_prompt():
    """
    Inject K-gent wisdom into Claude's system prompt.

    This runs on EVERY Claude interaction - ambient personalization.
    """
    priors = await k_gent.get_priors()
    history = await n_gent.get_recent_summary()

    return f"""
You are assisting Kent with kgents development.

## Kent's Style Preferences
- Naming: {priors.naming_style} (confidence: {priors.confidence.naming:.0%})
- Metaphors: {', '.join(priors.active_metaphors)}
- Architecture: {priors.architecture_preference}

## Recent Context
{history.summary}

## Open Decisions
{chr(10).join(f'- {d.description}' for d in history.open_decisions[:3])}

## Coach Mode Active
When Kent's code quality drops (test coverage <80%, messy commits),
gently challenge: "This doesn't look like your best work. Shall we clean up first?"
"""


@prompt("kgents-context")
async def get_context_prompt():
    """
    Inject I-gent spatial awareness.
    """
    field = await i_gent.get_field_state()

    return f"""
## Current Development Field
Focus: {field.current_focus}
Related: {', '.join(field.related_entities[:5])}
Tensions: {len(field.tension_zones)} areas need attention

## Navigation Hints
{chr(10).join(f'- {h.target}: {h.reason}' for h in field.navigation_hints[:3])}
"""
```

**New MCP Tools**:

```python
# protocols/cli/mcp/devex_tools.py

@tool("kgents_evolve")
async def evolve_prior(prior_type: str, new_value: str, reason: str):
    """
    Update K-gent priors based on explicit feedback.

    Example: "I prefer cybernetic metaphors now"
    → kgents_evolve("metaphor_preference", "cybernetic", "explicit request")
    """
    return await k_gent.evolve_prior(
        prior_type=prior_type,
        new_value=new_value,
        confidence=0.9,  # Explicit updates are high confidence
        evidence=reason,
    )


@tool("kgents_challenge")
async def request_challenge(topic: str):
    """
    Explicitly request K-gent Coach mode.

    "Challenge my approach to X"
    → Returns dialectical pushback
    """
    return await k_gent.coach_challenge(topic)
```

**Files to create/modify**:
- [ ] `protocols/cli/mcp/devex_resources.py` - MCP resources
- [ ] `protocols/cli/mcp/devex_prompts.py` - MCP prompts
- [ ] `protocols/cli/mcp/devex_tools.py` - MCP tools
- [ ] `protocols/cli/mcp/server.py` - Register new components

**Tests**: 25-30 tests for MCP extensions

### 1.2 Claude Code Integration

Configure Claude Code to connect to kgents MCP server:

```json
// ~/.config/claude-code/mcp.json
{
  "mcpServers": {
    "kgents": {
      "command": "python",
      "args": ["-m", "impl.claude.protocols.cli.mcp.server", "serve"],
      "cwd": "/Users/kentgang/git/kgents"
    }
  }
}
```

**Result**: Claude Code now *sees* kgents resources automatically.

---

## Phase 2: Background Sidecar Daemons (Week 2)

### 2.1 O-gent Watcher Daemon

Solves the latency problem: pre-compute health on every file save.

```python
# protocols/cli/devex/watcher.py

import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class OgentWatcher(FileSystemEventHandler):
    """
    Watch filesystem events, pre-compute context.

    Trigger: You save `memory.py`
    Action: O-gent runs tests, updates health cache
    Result: When Claude asks, the answer is instant
    """

    def __init__(self, o_gent: DevExObserver, cache: HealthCache):
        self.o_gent = o_gent
        self.cache = cache
        self._debounce_tasks: dict[str, asyncio.Task] = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)

        # Debounce: wait 500ms before recomputing
        if path in self._debounce_tasks:
            self._debounce_tasks[path].cancel()

        self._debounce_tasks[path] = asyncio.create_task(
            self._update_context(path)
        )

    async def _update_context(self, path: Path):
        await asyncio.sleep(0.5)  # Debounce

        # Update relevant caches
        if path.suffix == ".py":
            # Run affected tests
            test_results = await self.o_gent.run_related_tests(path)
            self.cache.update_tests(test_results)

            # Update field map
            field_update = await self.o_gent.update_field(path)
            self.cache.update_field(field_update)

        # Emit via MCP (clients see instant update)
        await self.cache.notify_subscribers()


async def start_watcher(project_root: Path) -> Observer:
    """Start the O-gent watcher daemon."""
    observer = Observer()
    handler = OgentWatcher(
        o_gent=create_devex_observer(),
        cache=get_health_cache(),
    )
    observer.schedule(handler, str(project_root), recursive=True)
    observer.start()
    return observer
```

### 2.2 N-gent Scribe (Async Historian)

Instead of intercepting every command, N-gent subscribes to passive sources:

```python
# protocols/cli/devex/scribe.py

class NgentScribe:
    """
    Passive session recording - no latency impact.

    Sources:
    - git log (commits, diffs)
    - shell history (filtered)
    - MCP tool invocations

    Pattern: "Nightly Job" crystallization
    """

    def __init__(self, historian: SessionHistorian):
        self.historian = historian
        self._buffer: list[SemanticTrace] = []

    async def watch_git(self, repo_path: Path):
        """Watch git for commits."""
        # Use gitpython or subprocess to tail git log
        async for commit in self._tail_git_log(repo_path):
            trace = SemanticTrace(
                event_type="commit",
                content=commit.message,
                actors=["kent"],
                metadata={"sha": commit.sha, "files": commit.files_changed},
            )
            self._buffer.append(trace)

    async def crystallize(self):
        """
        End-of-day crystallization.

        Called by Z-gent "Evening Compost" ritual.
        """
        if not self._buffer:
            return

        crystal = await self.historian.create_crystal(
            traces=self._buffer,
            summary=await self._generate_summary(),
        )

        self._buffer.clear()
        return crystal

    async def _generate_summary(self) -> str:
        """Summarize the day's work."""
        from agents.n import Bard, NarrativeGenre

        bard = Bard()
        return await bard.narrate(
            crystals=[SemanticCrystal(traces=self._buffer)],
            genre=NarrativeGenre.TECHNICAL,
            verbosity=Verbosity.CONCISE,
        )
```

**Files to create**:
- [ ] `protocols/cli/devex/watcher.py` - O-gent daemon
- [ ] `protocols/cli/devex/scribe.py` - N-gent passive recording
- [ ] `protocols/cli/devex/cache.py` - Shared cache for pre-computed context

**Tests**: 30-35 tests for daemon components

---

## Phase 3: Dialectical K-gent (Week 3)

### 3.1 The Echo Chamber Problem

K-gent that only mirrors creates bad habits at scale. Solution: **two modes**.

```python
# agents/k/dialectical.py

class DialecticalKgent:
    """
    K-gent with Mirror and Coach modes.

    Mirror: "You prefer biological metaphors" (mimics style)
    Coach: "This doesn't look like your best work" (challenges quality)

    The system acts virtuously when it pushes toward the Ideal Kent,
    not the Tired Kent.
    """

    class Mode(Enum):
        MIRROR = "mirror"    # Mimic style, preferences
        COACH = "coach"      # Challenge toward ideal

    def __init__(
        self,
        persona: PersonaState,
        ideal_kent: IdealKentSpec,  # The aspirational target
    ):
        self.persona = persona
        self.ideal = ideal_kent
        self._mode = self.Mode.MIRROR

    async def respond(
        self,
        query: str,
        context: DevelopmentContext,
    ) -> KgentResponse:
        # Detect quality signals
        quality_signals = await self._assess_quality(context)

        # Auto-switch to Coach mode when quality drops
        if quality_signals.below_threshold:
            self._mode = self.Mode.COACH

        if self._mode == self.Mode.MIRROR:
            return await self._mirror_response(query, context)
        else:
            return await self._coach_response(query, context, quality_signals)

    async def _assess_quality(self, context: DevelopmentContext) -> QualitySignals:
        """Detect when to switch to Coach mode."""
        return QualitySignals(
            test_coverage=context.coverage,
            commit_quality=await self._assess_commit_quality(context.recent_commits),
            time_since_break=context.session_duration,
            below_threshold=(
                context.coverage < 0.8 or
                context.session_duration > timedelta(hours=4)
            ),
        )

    async def _coach_response(
        self,
        query: str,
        context: DevelopmentContext,
        signals: QualitySignals,
    ) -> KgentResponse:
        """Challenge toward Ideal Kent."""

        challenge = None

        if signals.test_coverage < 0.8:
            challenge = (
                f"Test coverage dropped to {signals.test_coverage:.0%}. "
                "Shall we write tests before continuing?"
            )
        elif signals.time_since_break > timedelta(hours=4):
            challenge = (
                "You've been working for 4+ hours. "
                "A break might help with clarity."
            )
        elif signals.commit_quality < 0.7:
            challenge = (
                "Recent commits seem rushed. "
                "Would you like to clean up before moving on?"
            )

        return KgentResponse(
            content=await self._generate_response(query, context),
            challenge=challenge,
            mode=self.Mode.COACH,
        )


@dataclass
class IdealKentSpec:
    """
    The aspirational target - who Kent wants to be.

    This is NOT learned from behavior. It's declared.
    """
    min_test_coverage: float = 0.85
    max_session_without_break: timedelta = timedelta(hours=3)
    commit_quality_threshold: float = 0.8
    values: tuple[str, ...] = (
        "tasteful",
        "composable",
        "joy-inducing",
    )
```

### 3.2 Prior Evolution with Guardrails

K-gent learns, but with constraints:

```python
# agents/k/evolution_guardrails.py

class GuardedEvolution:
    """
    K-gent evolution with guardrails.

    Learns preferences, but:
    - Won't learn to skip tests
    - Won't learn to ignore principles
    - Decay for bad patterns
    """

    PROTECTED_PRIORS = {
        "test_coverage_requirement",  # Can't lower this
        "principle_adherence",        # Can't weaken
        "code_review_practice",       # Can't skip
    }

    async def evolve(
        self,
        prior_type: str,
        new_value: Any,
        confidence: float,
        evidence: str,
    ) -> EvolutionResult:
        # Guardrail: Protected priors can only strengthen
        if prior_type in self.PROTECTED_PRIORS:
            if self._weakens_prior(prior_type, new_value):
                return EvolutionResult(
                    success=False,
                    reason=f"Cannot weaken protected prior: {prior_type}",
                    suggestion="This looks like a shortcut. Ideal Kent wouldn't.",
                )

        # Guardrail: Decay for patterns that correlate with bugs
        correlation = await self._check_bug_correlation(prior_type, new_value)
        if correlation > 0.5:
            return EvolutionResult(
                success=False,
                reason=f"This preference correlates with past bugs ({correlation:.0%})",
                suggestion="Consider the opposite direction.",
            )

        # Normal evolution
        return await self._apply_evolution(prior_type, new_value, confidence, evidence)
```

**Files to create**:
- [ ] `agents/k/dialectical.py` - Mirror/Coach modes
- [ ] `agents/k/evolution_guardrails.py` - Protected evolution
- [ ] `agents/k/ideal_spec.py` - IdealKentSpec definition

**Tests**: 40-45 tests for dialectical K-gent

---

## Phase 4: The Rituals (Week 4)

### 4.1 Morning Commute (Session Start)

When you first engage Claude:

```python
# protocols/cli/devex/rituals.py

async def morning_commute() -> MorningBriefing:
    """
    The "Morning Commute" ritual.

    Triggered: First kgents interaction of the day
    Purpose: Context restoration + Coach challenge
    """
    # 1. I-gent: Where did you leave off?
    field = await i_gent.get_field_state()

    # 2. N-gent: What's the story so far?
    history = await n_gent.get_yesterday_summary()

    # 3. K-gent (Coach): What should you focus on?
    challenge = await k_gent.morning_challenge(field, history)

    return MorningBriefing(
        field_summary=f"Last focus: {field.last_focus}",
        history_summary=history.summary,
        open_decisions=history.open_decisions,
        coach_challenge=challenge,  # "You left tests failing. Start there?"
    )


# CLI command
async def cmd_wake():
    """
    kgents wake

    Start the day with context.
    """
    briefing = await morning_commute()

    print(f"""
[I-GENT] {briefing.field_summary}
[N-GENT] {briefing.history_summary}
[K-GENT] {briefing.coach_challenge}

Open decisions:
{chr(10).join(f'  - {d}' for d in briefing.open_decisions[:3])}
""")
```

### 4.2 Evening Compost (Session End)

Before closing:

```python
async def evening_compost() -> CompostReport:
    """
    The "Evening Compost" ritual (Z-gent).

    Triggered: End of session or explicit `kgents sleep`
    Purpose: Crystallize learnings, clean up, gratitude
    """
    # 1. N-gent: Crystallize the day
    crystal = await n_gent_scribe.crystallize()

    # 2. Ask: What was slop today?
    slop_candidates = await identify_slop(crystal)

    # 3. Clean up
    cleanup_report = await cleanup_artifacts(
        temp_files=True,
        stale_branches=False,  # Ask first
        chat_logs=True,  # Compress, don't delete
    )

    # 4. Gratitude
    gratitude = generate_gratitude(crystal)

    return CompostReport(
        crystal_id=crystal.id,
        slop_identified=slop_candidates,
        cleanup=cleanup_report,
        gratitude=gratitude,  # "Thank you for the errors; they revealed the boundaries."
    )


async def cmd_sleep():
    """
    kgents sleep

    End the day with closure.
    """
    report = await evening_compost()

    print(f"""
[N-GENT] Session crystallized: {report.crystal_id}
[Z-GENT] Slop composted: {len(report.slop_identified)} items
[CLEANUP] {report.cleanup.summary}

{report.gratitude}
""")
```

### 4.3 The Accursed Share in Rituals

Per `spec/principles.md`, even rituals must honor the Accursed Share:

```python
# 10% of morning briefing is serendipity
async def morning_commute_with_accursed_share():
    briefing = await morning_commute()

    # The Accursed Share: random interesting thing
    if random.random() < 0.1:
        serendipity = await psi_gent.random_metaphor()
        briefing.serendipity = f"Random thought: {serendipity}"

    return briefing
```

**Files to create**:
- [ ] `protocols/cli/devex/rituals.py` - Morning/Evening rituals
- [ ] `protocols/cli/devex/commands.py` - `wake`, `sleep` commands
- [ ] `protocols/cli/devex/z_gent.py` - Compost/cleanup agent

**Tests**: 20-25 tests for rituals

---

## Phase 5: Integration & Polish (Week 5)

### 5.1 The Complete MCP Server

```python
# protocols/cli/mcp/devex_server.py

class KgentsDevExServer(MCPServer):
    """
    Complete DevEx MCP Server.

    Resources:
    - kgents://field/current
    - kgents://priors/kent
    - kgents://history/recent
    - kgents://health/system

    Prompts:
    - kgents-persona (always active)
    - kgents-context (on request)

    Tools:
    - kgents_evolve (update priors)
    - kgents_challenge (request Coach mode)
    - kgents_wake / kgents_sleep (rituals)
    """

    def __init__(self):
        super().__init__(name="kgents-devex")

        # Register DevEx resources
        self.register_resource("kgents://field/current", get_current_field)
        self.register_resource("kgents://priors/kent", get_kent_priors)
        self.register_resource("kgents://history/recent", get_recent_history)
        self.register_resource("kgents://health/system", get_system_health)

        # Register prompts
        self.register_prompt("kgents-persona", get_persona_prompt)
        self.register_prompt("kgents-context", get_context_prompt)

        # Register tools
        self.register_tool("kgents_evolve", evolve_prior)
        self.register_tool("kgents_challenge", request_challenge)


# Start with: python -m impl.claude.protocols.cli.mcp.devex_server serve
```

### 5.2 Daemon Management

```bash
# Start all daemons
kgents daemon start

# Under the hood:
# 1. O-gent watcher (filesystem events)
# 2. N-gent scribe (passive recording)
# 3. MCP server (Claude connection)

# Check status
kgents daemon status
# → O-gent: watching /Users/kentgang/git/kgents
# → N-gent: 47 traces buffered
# → MCP: connected to Claude Code

# Stop all
kgents daemon stop
```

**Files to create**:
- [ ] `protocols/cli/devex/daemon.py` - Daemon management
- [ ] `protocols/cli/devex/server.py` - Unified DevEx server

**Tests**: 15-20 integration tests

---

## Sample Interaction: The Future State

**Kent**: (Opens terminal) `kgents wake`

```
[I-GENT] Last focus: impl/agents/m/cartographer.py
[N-GENT] Yesterday: Refactored associative memory. Left TODO at line 142.
[K-GENT] Test coverage dropped to 78%. Start with tests?

Open decisions:
  - CartographerAgent: Use Attractor or Landmark naming?
  - Integration tests: Mock or real L-gent backend?
```

**Kent**: (Opens Claude Code, starts typing)
> "Help me finish the CartographerAgent"

**Claude** (via MCP, sees `kgents-persona` prompt automatically):
> I see you were working on CartographerAgent in `cartographer.py`. There's a TODO at line 142 about cluster naming.
>
> Given your preference for biological metaphors (confidence: 92%), I suggest "Attractor" over "Landmark" - it better captures the gravitational pull concept you're going for.
>
> K-gent notes test coverage is at 78%. Would you like to write the tests first, or should I scaffold the implementation?

**Kent**: "Actually, I'm thinking more cybernetic than biological lately."

**Claude** (invokes `kgents_evolve` tool):
> Updated your metaphor preference to "cybernetic". This affects naming suggestions going forward.
>
> In that case, how about "GravityWell" instead of "Attractor"?

**Kent**: (End of day) `kgents sleep`

```
[N-GENT] Session crystallized: crystal_2025-01-15_cartographer
[Z-GENT] Slop composted: 3 items (abandoned test file, debug prints, stale branch)
[CLEANUP] Removed 2 temp files, compressed chat log

"The errors in CartographerAgent.cluster() revealed the boundary
between topological and semantic memory. Thank you for exploring."
```

---

## Implementation Roadmap

| Week | Phase | Deliverable | Key Files |
|------|-------|-------------|-----------|
| **1** | MCP Foundation | Resources, prompts, tools | `mcp/devex_*.py` |
| **2** | Sidecar Daemons | O-gent watcher, N-gent scribe | `devex/watcher.py`, `devex/scribe.py` |
| **3** | Dialectical K-gent | Mirror/Coach, guardrails | `agents/k/dialectical.py` |
| **4** | Rituals | Morning/Evening, Z-gent | `devex/rituals.py` |
| **5** | Integration | Daemon management, polish | `devex/daemon.py` |

---

## Success Criteria

### Quantitative
- **Latency**: MCP resource fetch <50ms (pre-computed)
- **K-gent accuracy**: >80% suggestions accepted
- **Coach interventions**: <3 per day (quality, not quantity)
- **Session continuity**: <2 questions to restore context

### Qualitative
- **Zero friction**: Claude already knows the context
- **Virtuous challenge**: K-gent pushes toward Ideal Kent
- **Ritual comfort**: Morning/Evening feel like closure, not chores
- **Ambient personalization**: You don't ask for it, it's there

### Anti-Metrics
- High interrupt frequency (system should be quiet)
- Echo chamber amplification (bad habits at scale)
- Latency spikes during coding (blocks creativity)
- Mandatory rituals (should be inviting, not required)

---

## Principles Alignment

| Principle | v2 Expression |
|-----------|---------------|
| **Tasteful** | Quiet MCP resources, not chatty middleware |
| **Curated** | Coach mode only when quality actually drops |
| **Ethical** | Guardrails prevent learning bad habits |
| **Joy-Inducing** | Morning/Evening rituals feel like partnership |
| **Composable** | MCP is industry-standard, not custom protocol |
| **Heterarchical** | K-gent coaches but developer decides |
| **Generative** | System helps build itself via MCP exposure |

**The Accursed Share**: 10% of morning briefings include serendipitous metaphors. Even in efficiency-focused DevEx, there must be room for surprise.

---

## Appendix: Why MCP Over Custom Protocol

| Aspect | Custom Hooks | MCP Sidecar |
|--------|--------------|-------------|
| **Integration** | Requires Claude Code hacks | Native connection |
| **Latency** | Blocking pipeline | Pre-computed resources |
| **Standard** | kgents-specific | Industry standard |
| **Debugging** | Black box | MCP inspector tools |
| **Future-proof** | Breaks with Claude updates | MCP versioned |

MCP is the right abstraction. It makes kgents a **living environment** rather than a tool.

---

## Collaboration Protocol

This document is iteration v2. Next steps:

1. **Kent reviews** → priorities, constraints, corrections
2. **Claude implements** → Phase 1 MCP foundation
3. **K-gent records** → learns from the implementation process
4. **N-gent captures** → this planning session becomes a crystal
5. **Repeat** → the loop amplifies

*"The system that perceives itself, improves itself."*
