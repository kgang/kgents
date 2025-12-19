# concept.principles Node

> *Programmatic access to principles through the AGENTESE protocol.*

---

## Core Insight

The principles aren't just documentation—they're **queryable knowledge** that agents can invoke. The `concept.principles` node exposes the stratified principles structure through observer-dependent aspects.

---

## Path Structure

```
concept.principles             # Root node
├── .manifest                  # Stance-aware principle projection
├── .constitution              # The 7 immutable principles
├── .meta                      # Accursed Share, AGENTESE, Personality Space
├── .operational               # Tactical guidance
├── .ad                        # Architectural decisions (parameterized by ID)
├── .check                     # Validate artifact against principles
├── .teach                     # Interactive principle teaching mode
└── .heal                      # Therapeia: diagnose and prescribe
```

---

## Node Registration

```python
@node(
    "concept.principles",
    description="The kgents design principles - queryable, stance-aware",
    aspects=("manifest", "constitution", "meta", "operational", "ad", "check", "teach", "heal"),
    context=AGENTESEContext.CONCEPT,
    dependencies=("principle_loader",),
)
@dataclass
class PrinciplesNode(BaseLogosNode):
    """Node for principle consumption via AGENTESE."""

    _handle: str = "concept.principles"
    _loader: PrincipleLoader = field(default_factory=get_principle_loader)

    @property
    def handle(self) -> str:
        return self._handle
```

---

## Aspects

### manifest (Stance-Aware Projection)

Returns principle slices based on detected or explicit stance.

```python
async def manifest(
    self,
    observer: Umwelt[Any, Any],
    stance: Stance | None = None,
    task: str | None = None,
) -> PrincipleProjection:
    """Project principles appropriate to the observer's stance."""

    # Detect stance from observer context if not explicit
    detected_stance = stance or self._detect_stance(observer)

    slices = STANCE_SLICES[detected_stance]
    if detected_stance == Stance.POIESIS and task:
        slices = slices + self._ad_slices_for_task(task)

    return PrincipleProjection(
        stance=detected_stance,
        slices=slices,
        content=await self._loader.load_slices(slices),
    )
```

**Usage**:
```python
# Auto-detect stance
await logos.invoke("concept.principles.manifest", observer)

# Explicit stance with task context
await logos.invoke("concept.principles.manifest", observer, stance="poiesis", task="adding-agent")
```

### constitution

Returns the 7 core principles.

```python
async def constitution(self, observer: Umwelt[Any, Any]) -> ConstitutionRendering:
    """The immutable seven principles."""
    return ConstitutionRendering(
        content=await self._loader.load("CONSTITUTION.md"),
        principles=THE_SEVEN_PRINCIPLES,  # Parsed structure
    )
```

### meta

Returns meta-principles (Accursed Share, AGENTESE, Personality Space).

```python
async def meta(
    self,
    observer: Umwelt[Any, Any],
    section: str | None = None,
) -> MetaPrincipleRendering:
    """Meta-principles that operate ON the seven."""
    if section:
        return await self._loader.load_section("meta.md", section)
    return await self._loader.load("meta.md")
```

### operational

Returns tactical implementation guidance.

```python
async def operational(self, observer: Umwelt[Any, Any]) -> OperationalRendering:
    """Day-to-day tactical guidance."""
    return await self._loader.load("operational.md")
```

### ad (Parameterized)

Returns specific architectural decisions.

```python
async def ad(
    self,
    observer: Umwelt[Any, Any],
    id: int | None = None,
    category: str | None = None,
) -> ADRendering:
    """Architectural decisions - by ID or category."""
    if id:
        return await self._loader.load_ad(id)
    if category:
        return await self._loader.load_ads_by_category(category)
    return await self._loader.load_ad_index()
```

**Usage**:
```python
await logos.invoke("concept.principles.ad", observer, id=9)  # AD-009 Metaphysical Fullstack
await logos.invoke("concept.principles.ad", observer, category="categorical")  # All categorical ADs
```

### check (Krisis)

Validates an artifact against principles. Returns pass/fail with specific citations.

```python
async def check(
    self,
    observer: Umwelt[Any, Any],
    target: str | Agent | Spec,
    principles: list[int] | None = None,  # 1-7, or None for all
) -> CheckResult:
    """Evaluate target against principles."""

    results = []
    for i, question in enumerate(THE_SEVEN_QUESTIONS, 1):
        if principles and i not in principles:
            continue

        judgment = await self._evaluate(target, question)
        results.append(PrincipleCheck(
            principle=i,
            name=PRINCIPLE_NAMES[i],
            question=question,
            passed=judgment.passed,
            citation=judgment.evidence,
            anti_patterns=judgment.matched_anti_patterns,
        ))

    return CheckResult(
        target=str(target),
        passed=all(r.passed for r in results),
        checks=results,
        stance=Stance.KRISIS,
    )
```

**Usage**:
```python
result = await logos.invoke("concept.principles.check", observer, target=my_agent)
if not result.passed:
    for check in result.checks:
        if not check.passed:
            print(f"❌ {check.name}: {check.citation}")
```

### teach (Interactive Mode)

Interactive principle teaching with examples and exercises.

```python
async def teach(
    self,
    observer: Umwelt[Any, Any],
    principle: int | str | None = None,
    depth: Literal["overview", "examples", "exercises"] = "overview",
) -> TeachingContent:
    """Interactive principle learning."""
    ...  # See impl/claude/protocols/agentese/contexts/concept/principles.py
```

### heal (Therapeia)

Given a violation, prescribes the path to restoration.

```python
async def heal(
    self,
    observer: Umwelt[Any, Any],
    violation: int | str,  # Principle number or name
    context: str | None = None,  # What went wrong
) -> HealingPrescription:
    """Diagnose violation and prescribe restoration."""

    principle = self._resolve_principle(violation)
    anti_patterns = await self._loader.load_anti_patterns(principle)
    puppets = await self._loader.load_puppets_for_principle(principle)
    related_ads = await self._loader.load_related_ads(principle)

    return HealingPrescription(
        principle=principle,
        anti_patterns=anti_patterns,
        matched_pattern=self._match_anti_pattern(context, anti_patterns) if context else None,
        puppets=puppets,
        related_ads=related_ads,
        path=[
            "Identify which anti-pattern matches",
            "Find a puppet that makes the solution obvious",
            f"Rebuild using AD-{related_ads[0].id} pattern",
            "Verify with concept.principles.check",
        ],
        stance=Stance.THERAPEIA,
    )
```

**Usage**:
```python
prescription = await logos.invoke(
    "concept.principles.heal",
    observer,
    violation="composable",
    context="Agent can't be combined with other agents"
)
print(prescription.path)  # Step-by-step healing
```

---

## Affordances by Archetype

The node adapts affordances based on observer archetype:

| Archetype | Affordances |
|-----------|-------------|
| `philosopher` | `manifest`, `constitution`, `meta`, `teach`, `heal` |
| `engineer` | `manifest`, `operational`, `ad`, `check` |
| `reviewer` | `manifest`, `constitution`, `check`, `heal` |
| `teacher` | `manifest`, `constitution`, `teach` |
| `debugger` | `manifest`, `check`, `heal`, `ad` |
| `default` | `manifest`, `constitution`, `check` |

---

## Dependencies

```python
# services/providers.py
def get_principle_loader() -> PrincipleLoader:
    return PrincipleLoader(
        base_path=Path("spec/principles"),
        cache=True,  # Principles change rarely
    )

# Container registration
container.register("principle_loader", get_principle_loader, singleton=True)
```

---

## Laws

1. **Stance Coherence**: `manifest(stance=X)` returns exactly `STANCE_SLICES[X]`
2. **Check Completeness**: `check()` always evaluates all seven principles unless filtered
3. **Heal Specificity**: `heal(violation)` always returns at least one prescription path
4. **Constitution Immutability**: `constitution()` returns identical content across all observers

---

## Integration

**Gateway import** (ensures node registers at startup):
```python
# protocols/agentese/gateway.py
def _import_node_modules() -> None:
    from .contexts.concept import principles  # Registers concept.principles
```

**CLI usage**:
```bash
kgents invoke concept.principles.manifest --stance genesis
kgents invoke concept.principles.check --target "self.memory"
kgents invoke concept.principles.heal --violation composable
```

---

## Implementation

```
impl/claude/
├── protocols/agentese/contexts/concept/
│   └── principles.py          # PrinciplesNode implementation
├── services/principles/
│   ├── loader.py              # PrincipleLoader (file loading, caching)
│   ├── stance.py              # Stance detection logic
│   ├── checker.py             # Principle validation logic
│   └── types.py               # PrincipleProjection, CheckResult, etc.
```

---

*"The principles are the water; the node is how you drink."*
