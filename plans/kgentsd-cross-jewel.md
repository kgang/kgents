# kgentsd Cross-Jewel Integration

> *"kgentsd is the only jewel that can invoke all other jewels."*

**Status**: PLANNING
**Parent**: `plans/kgentsd-crown-jewel.md`
**Focus**: Cross-jewel invocation, pipeline composition, scheduling

---

## The Unique Position of kgentsd

kgentsd occupies a special position in the Crown:

```
                    ┌─────────────┐
                    │   kgentsd   │
                    │ (Level 3)   │
                    └──────┬──────┘
                           │ can invoke all
           ┌───────────────┼───────────────┐
           │       │       │       │       │
           ▼       ▼       ▼       ▼       ▼
        ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
        │Brain│ │Garde│ │Gesta│ │Forge│ │Coal.│
        │     │ │ner  │ │lt   │ │     │ │     │
        └─────┘ └─────┘ └─────┘ └─────┘ └─────┘
           │       │       │       │       │
           ▼       ▼       ▼       ▼       ▼
        ┌─────┐ ┌─────┐
        │Park │ │Domai│
        │     │ │n    │
        └─────┘ └─────┘
```

**Key Insight**: Other jewels can invoke each other, but kgentsd is designed to orchestrate them all. At Level 3, kgentsd can:
- Invoke any jewel's AGENTESE paths
- Chain jewels into pipelines
- Schedule future invocations
- React to cross-jewel events

---

## Invocation Patterns

### Single Jewel Invocation

```python
# Via AGENTESE
await logos.invoke("world.daemon.invoke", observer,
    target="self.memory.capture",
    kwargs={"content": "Insight from daemon observation"}
)

# Direct (Level 3 only)
result = await daemon.invoke_jewel(
    path="self.memory.capture",
    observer=daemon_observer,
    content="Insight from daemon observation"
)
```

### Pipeline Composition

```python
# Chain multiple jewels
pipeline = (
    "world.gestalt.analyze"    # Analyze code
    >> "self.memory.capture"   # Capture findings
    >> "world.forge.document"  # Generate docs
)

result = await daemon.run_pipeline(pipeline, observer, source_file="services/town/")

# Equivalent AGENTESE
await logos.invoke("world.daemon.pipeline", observer,
    steps=[
        {"path": "world.gestalt.analyze", "kwargs": {"source_file": "services/town/"}},
        {"path": "self.memory.capture", "kwargs": {}},  # Uses previous result
        {"path": "world.forge.document", "kwargs": {}},  # Uses previous result
    ]
)
```

### Conditional Pipelines

```python
# Branching based on results
pipeline = Pipeline([
    Step("world.gestalt.analyze", source_file="services/town/"),
    Branch(
        condition=lambda result: result.get("issues", 0) > 0,
        if_true=Step("world.forge.fix", auto_apply=False),
        if_false=Step("self.memory.capture", content="No issues found"),
    ),
])

await daemon.run_pipeline(pipeline, observer)
```

---

## Jewel Integration Map

### Brain (self.memory.*)

kgentsd → Brain for:
- Capturing observations as crystals
- Querying past patterns
- Surfacing relevant memories during analysis

```python
# Capture daemon observation
await daemon.invoke_jewel("self.memory.capture",
    content=f"Detected pattern: {pattern.description}",
    tags=["daemon", "pattern", pattern.category],
)

# Query for similar past observations
similar = await daemon.invoke_jewel("self.memory.surface",
    query=f"patterns in {file_path}",
    limit=5,
)
```

### Gardener (concept.gardener.*)

kgentsd → Gardener for:
- Tracking development sessions
- Managing entropy budget
- Suggesting garden tending

```python
# Start a tending session
await daemon.invoke_jewel("concept.gardener.session.start",
    intent="daemon-triggered maintenance",
    plasticity=0.5,
)

# Record a gesture
await daemon.invoke_jewel("concept.gardener.gesture.record",
    gesture_type="analysis",
    target="services/town/",
    confidence=0.8,
)
```

### Gestalt (world.gestalt.* / world.codebase.*)

kgentsd → Gestalt for:
- Analyzing code structure
- Detecting architectural patterns
- Visualizing system state

```python
# Analyze changed files
analysis = await daemon.invoke_jewel("world.gestalt.analyze",
    files=changed_files,
    include_dependencies=True,
)

# Get visualization data
viz = await daemon.invoke_jewel("world.gestalt.visualize",
    focus="services/daemon/",
    depth=2,
)
```

### Forge (world.forge.*)

kgentsd → Forge for:
- Generating code fixes
- Creating documentation
- Building new components

```python
# Fix test failure
fix = await daemon.invoke_jewel("world.forge.fix",
    test_id=failing_test.id,
    error=failing_test.error,
    context=analysis,
)

# Generate documentation
docs = await daemon.invoke_jewel("world.forge.document",
    target="services/daemon/",
    style="docstring",
)
```

### Coalition (world.town.coalition.*)

kgentsd → Coalition for:
- Coordinating agent collaboration
- Managing citizen interactions
- Running simulations

```python
# Spawn agents for analysis
coalition = await daemon.invoke_jewel("world.town.coalition.form",
    purpose="analyze-test-failures",
    citizens=["analyst", "fixer", "reviewer"],
)

# Run collaboration
result = await daemon.invoke_jewel("world.town.coalition.collaborate",
    coalition_id=coalition.id,
    task=analysis_task,
)
```

### Park (world.park.*)

kgentsd → Park for:
- Running scenarios
- Testing consent mechanics
- Evaluating agent behaviors

```python
# Run scenario
scenario_result = await daemon.invoke_jewel("world.park.scenario.run",
    scenario="test-failure-response",
    participants=["daemon", "developer"],
)
```

### Domain (world.domain.*)

kgentsd → Domain for:
- Enterprise modeling
- Business logic validation
- Domain-specific analysis

```python
# Validate domain model
validation = await daemon.invoke_jewel("world.domain.validate",
    model="services/domain/models/",
    rules="spec/domain/rules.md",
)
```

---

## Cross-Jewel Event Reactions

kgentsd listens to all jewel events and can react:

```python
class CrossJewelReactor:
    """
    React to events from any jewel.
    """

    @on_event("self.memory.crystal.created")
    async def on_crystal_created(self, event: CrystalCreatedEvent):
        """React to new memory crystal."""
        # Maybe trigger pattern detection
        if event.tags and "pattern" in event.tags:
            await self.analyze_pattern(event.crystal_id)

    @on_event("world.gestalt.analysis.complete")
    async def on_analysis_complete(self, event: AnalysisCompleteEvent):
        """React to code analysis completion."""
        # Store insights
        if event.insights:
            await self.invoke_jewel("self.memory.capture",
                content=f"Analysis of {event.target}: {event.summary}",
                tags=["gestalt", "analysis"],
            )

    @on_event("world.forge.fix.proposed")
    async def on_fix_proposed(self, event: FixProposedEvent):
        """React to proposed fix."""
        # At Level 2, queue for confirmation
        # At Level 3, maybe auto-apply if confidence high
        if self.trust.level >= TrustLevel.AUTONOMOUS and event.confidence > 0.95:
            await self.invoke_jewel("world.forge.fix.apply",
                fix_id=event.fix_id,
            )
```

---

## Pipeline Implementation

```python
@dataclass
class Step:
    """A single step in a pipeline."""
    path: str
    kwargs: dict = field(default_factory=dict)
    transform: Callable[[Any], dict] | None = None  # Transform previous result to kwargs


@dataclass
class Branch:
    """Conditional branch in a pipeline."""
    condition: Callable[[Any], bool]
    if_true: Step | "Pipeline"
    if_false: Step | "Pipeline" | None = None


@dataclass
class Pipeline:
    """Composable pipeline of jewel invocations."""
    steps: list[Step | Branch]

    def __rshift__(self, other: "Step | Pipeline") -> "Pipeline":
        """Compose pipelines with >> operator."""
        if isinstance(other, Step):
            return Pipeline(self.steps + [other])
        elif isinstance(other, Pipeline):
            return Pipeline(self.steps + other.steps)
        raise TypeError(f"Cannot compose with {type(other)}")


class PipelineRunner:
    """Executes pipelines across jewels."""

    def __init__(self, logos: Logos, observer: Observer):
        self.logos = logos
        self.observer = observer

    async def run(self, pipeline: Pipeline, initial_kwargs: dict = None) -> list[Any]:
        """Run pipeline, returning all results."""
        results = []
        current_kwargs = initial_kwargs or {}

        for step in pipeline.steps:
            if isinstance(step, Step):
                # Transform previous result if transformer provided
                if step.transform and results:
                    current_kwargs = step.transform(results[-1])
                else:
                    current_kwargs = {**current_kwargs, **step.kwargs}

                result = await self.logos.invoke(step.path, self.observer, **current_kwargs)
                results.append(result)
                current_kwargs = result if isinstance(result, dict) else {}

            elif isinstance(step, Branch):
                # Evaluate condition on previous result
                condition_result = step.condition(results[-1] if results else None)

                if condition_result:
                    branch_result = await self._run_branch(step.if_true, current_kwargs)
                elif step.if_false:
                    branch_result = await self._run_branch(step.if_false, current_kwargs)
                else:
                    branch_result = None

                if branch_result:
                    results.append(branch_result)
                    current_kwargs = branch_result if isinstance(branch_result, dict) else {}

        return results

    async def _run_branch(self, branch: Step | Pipeline, kwargs: dict) -> Any:
        """Run a branch (single step or sub-pipeline)."""
        if isinstance(branch, Step):
            return await self.logos.invoke(branch.path, self.observer, **{**kwargs, **branch.kwargs})
        elif isinstance(branch, Pipeline):
            return await self.run(branch, kwargs)
```

---

## Scheduling

kgentsd can schedule future invocations:

```python
@dataclass
class ScheduledInvocation:
    """A scheduled future invocation."""
    id: str
    path: str
    kwargs: dict
    scheduled_at: datetime
    execute_at: datetime
    repeat: str | None = None  # "hourly", "daily", "weekly", or cron expression
    created_by: str = "daemon"


class Scheduler:
    """Schedules future jewel invocations."""

    def __init__(self, logos: Logos, observer: Observer):
        self.logos = logos
        self.observer = observer
        self._scheduled: dict[str, ScheduledInvocation] = {}
        self._running = False

    async def schedule(
        self,
        path: str,
        execute_at: datetime,
        kwargs: dict = None,
        repeat: str = None,
    ) -> str:
        """Schedule a future invocation."""
        invocation = ScheduledInvocation(
            id=self._generate_id(),
            path=path,
            kwargs=kwargs or {},
            scheduled_at=datetime.now(),
            execute_at=execute_at,
            repeat=repeat,
        )

        self._scheduled[invocation.id] = invocation
        return invocation.id

    async def cancel(self, invocation_id: str):
        """Cancel a scheduled invocation."""
        del self._scheduled[invocation_id]

    async def start(self):
        """Start the scheduler loop."""
        self._running = True

        while self._running:
            now = datetime.now()

            # Find due invocations
            due = [
                inv for inv in self._scheduled.values()
                if inv.execute_at <= now
            ]

            for inv in due:
                try:
                    await self.logos.invoke(inv.path, self.observer, **inv.kwargs)
                except Exception as e:
                    logger.error(f"Scheduled invocation {inv.id} failed: {e}")

                if inv.repeat:
                    # Reschedule
                    inv.execute_at = self._next_execution(inv.execute_at, inv.repeat)
                else:
                    # Remove one-time invocation
                    del self._scheduled[inv.id]

            await asyncio.sleep(1)

    def _next_execution(self, current: datetime, repeat: str) -> datetime:
        """Calculate next execution time."""
        if repeat == "hourly":
            return current + timedelta(hours=1)
        elif repeat == "daily":
            return current + timedelta(days=1)
        elif repeat == "weekly":
            return current + timedelta(weeks=1)
        else:
            # Parse as cron expression
            return self._parse_cron(repeat, current)
```

---

## AGENTESE Interface

```python
@node("world.daemon")
class DaemonNode:
    """AGENTESE node for daemon cross-jewel operations."""

    @aspect(category=AspectCategory.MUTATION, effects=[Effect.INVOKES("*")])
    async def invoke(
        self,
        observer: Observer,
        target: str,
        kwargs: dict = None,
    ) -> dict:
        """
        Invoke any jewel path.

        Requires Level 3 trust for mutation paths.
        Read-only paths available at all levels.
        """
        if not self.trust.can_invoke(target):
            raise PermissionError(f"Cannot invoke {target} at trust level {self.trust.level}")

        result = await self.logos.invoke(target, observer, **(kwargs or {}))
        return {"path": target, "result": result}

    @aspect(category=AspectCategory.MUTATION, effects=[Effect.INVOKES("*")])
    async def pipeline(
        self,
        observer: Observer,
        steps: list[dict],
    ) -> dict:
        """
        Run a pipeline of jewel invocations.

        Each step: {"path": str, "kwargs": dict}
        Results from previous steps available as context.
        """
        pipeline = Pipeline([
            Step(path=s["path"], kwargs=s.get("kwargs", {}))
            for s in steps
        ])

        runner = PipelineRunner(self.logos, observer)
        results = await runner.run(pipeline)

        return {"steps": len(steps), "results": results}

    @aspect(category=AspectCategory.MUTATION, effects=[Effect.SCHEDULES("*")])
    async def schedule(
        self,
        observer: Observer,
        path: str,
        execute_at: str,  # ISO datetime
        kwargs: dict = None,
        repeat: str = None,
    ) -> dict:
        """
        Schedule a future jewel invocation.

        execute_at: ISO datetime string
        repeat: "hourly", "daily", "weekly", or cron expression
        """
        invocation_id = await self.scheduler.schedule(
            path=path,
            execute_at=datetime.fromisoformat(execute_at),
            kwargs=kwargs,
            repeat=repeat,
        )

        return {
            "scheduled": True,
            "invocation_id": invocation_id,
            "path": path,
            "execute_at": execute_at,
            "repeat": repeat,
        }
```

---

## Common Daemon Workflows

### Test Failure Response

```python
# Daemon detects test failure
async def on_test_failed(self, event: TestFailed):
    """Respond to test failure."""

    # 1. Analyze the failure
    analysis = await self.invoke_jewel("world.gestalt.analyze",
        file=event.file,
        focus="test-failure",
        error=event.error,
    )

    # 2. Check for similar past failures
    similar = await self.invoke_jewel("self.memory.surface",
        query=f"test failure in {event.file}",
        limit=3,
    )

    # 3. Attempt fix (Level 3) or suggest (Level 2)
    if self.trust.level >= TrustLevel.AUTONOMOUS:
        fix = await self.invoke_jewel("world.forge.fix",
            test_id=event.test_id,
            error=event.error,
            analysis=analysis,
            similar_failures=similar,
        )

        if fix.confidence > 0.9:
            await self.invoke_jewel("world.forge.apply",
                fix_id=fix.id,
            )
    else:
        # Suggest fix for human review
        await self.suggest(
            action=FixAction(test_id=event.test_id, fix=fix),
            rationale=f"Based on analysis and {len(similar)} similar past failures",
        )
```

### Code Change Response

```python
# Daemon detects code change
async def on_file_modified(self, event: FileModified):
    """Respond to code modification."""

    # 1. Run relevant tests
    test_results = await self.invoke_jewel("world.gestalt.test",
        files=[event.path],
        mode="affected",  # Only tests affected by this file
    )

    # 2. If tests pass, analyze for documentation needs
    if test_results.all_passed:
        doc_analysis = await self.invoke_jewel("world.gestalt.analyze",
            file=event.path,
            focus="documentation",
        )

        if doc_analysis.documentation_gaps:
            # Generate documentation
            docs = await self.invoke_jewel("world.forge.document",
                target=event.path,
                gaps=doc_analysis.documentation_gaps,
            )

            # Capture insight
            await self.invoke_jewel("self.memory.capture",
                content=f"Updated documentation for {event.path}",
                tags=["documentation", "daemon"],
            )
```

---

## Implementation Checklist

### Week 4 Deliverables

- [ ] `services/daemon/invoke.py` — Single jewel invocation
- [ ] `services/daemon/pipeline.py` — Pipeline composition
- [ ] `services/daemon/schedule.py` — Future scheduling
- [ ] `services/daemon/workflows/test_failure.py` — Test failure workflow
- [ ] `services/daemon/workflows/code_change.py` — Code change workflow
- [ ] `services/daemon/workflows/pr_review.py` — PR review workflow
- [ ] `services/daemon/node.py` — AGENTESE node (update with invoke/pipeline/schedule)
- [ ] `services/daemon/_tests/test_invoke.py` — Invocation tests
- [ ] `services/daemon/_tests/test_pipeline.py` — Pipeline tests
- [ ] `services/daemon/_tests/test_schedule.py` — Scheduling tests

---

*"The daemon is the conductor; the jewels are the orchestra."*
