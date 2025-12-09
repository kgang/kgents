# H-gent Composition

**How the three traditions compose into introspection pipelines.**

---

## Philosophy

> "The whole is greater than the sum of its parts."
> — Aristotle

Each H-gent tradition (Hegel, Lacan, Jung) provides a different lens on system introspection. Composed together, they reveal insights that no single tradition could surface alone.

---

## The Three Pipelines

### Hegel → Lacan: "Is this synthesis in the Imaginary?"

After dialectic synthesis, check if the result lives in the Imaginary register (idealization) rather than the Symbolic (formal structure) or touching the Real (limits).

```python
class HegelLacanPipeline(Agent[DialecticOutput, LacanResult]):
    """
    Hegel → Lacan composition.

    Question: Is this synthesis in the Imaginary?
    Does it touch the Real or is it purely Symbolic?
    """

    async def invoke(self, dialectic_output: DialecticOutput) -> LacanResult:
        if dialectic_output.synthesis is None:
            # No synthesis - check the tension itself
            return await self._lacan.invoke(LacanInput(
                output=dialectic_output.sublation_notes,
                context={"productive_tension": dialectic_output.productive_tension},
            ))

        return await self._lacan.invoke(LacanInput(
            output=dialectic_output.synthesis,
            context={
                "is_synthesis": True,
                "sublation_notes": dialectic_output.sublation_notes,
            },
        ))
```

**Reveals:**
- Syntheses that are merely aspirational (Imaginary)
- Syntheses that avoid practical limits (far from Real)
- Register slippages in the synthesis

---

### Lacan → Jung: "What shadow does this register structure create?"

After register analysis, ask what the system has exiled to maintain this register position.

```python
class LacanJungPipeline(Agent[LacanResult, JungOutput]):
    """
    Lacan → Jung composition.

    Question: What did we exile to maintain this register structure?
    What shadow is created by the gaps?
    """

    async def invoke(self, lacan_output: LacanResult) -> JungOutput:
        if isinstance(lacan_output, LacanError):
            # Error is Real intrusion - what shadow does error handling create?
            return await self._jung.invoke(JungInput(
                system_self_image="System that encountered unrepresentable error",
                behavioral_patterns=[f"Error: {lacan_output.message}"],
            ))

        # Build self-image from register location
        loc = lacan_output.register_location
        self_image_parts = []
        if loc.symbolic > 0.5:
            self_image_parts.append("structured and formal")
        if loc.imaginary > 0.5:
            self_image_parts.append("idealized and coherent")
        if loc.real_proximity > 0.5:
            self_image_parts.append("touching limits and impossibility")

        return await self._jung.invoke(JungInput(
            system_self_image=f"System that is {', '.join(self_image_parts)}",
            declared_limitations=lacan_output.gaps,
            behavioral_patterns=[s.evidence for s in lacan_output.slippages],
        ))
```

**Reveals:**
- Shadow content created by register structure
- How gaps in representation create exiled content
- Projections arising from slippages

---

### Jung → Hegel: "Can we synthesize persona and shadow?"

After shadow analysis, attempt dialectic between what the system claims to be and what it excludes.

```python
class JungHegelPipeline(Agent[JungOutput, DialecticOutput]):
    """
    Jung → Hegel composition.

    Question: Can we synthesize persona and shadow?
    What's the dialectic between claimed identity and exiled content?
    """

    async def invoke(self, jung_output: JungOutput) -> DialecticOutput:
        if not jung_output.shadow_inventory:
            return DialecticOutput(
                synthesis="Persona fully integrated",
                sublation_notes="No shadow detected to synthesize",
                productive_tension=False,
            )

        # Persona as thesis, shadow as antithesis
        persona_claims = f"Balance score: {jung_output.persona_shadow_balance}"
        shadow_claims = ", ".join(s.content for s in jung_output.shadow_inventory[:3])

        return await self._hegel.invoke(DialecticInput(
            thesis=persona_claims,
            antithesis=shadow_claims,
        ))
```

**Reveals:**
- Whether persona and shadow can be integrated
- Productive tensions between identity and exclusions
- Paths to wholeness

---

## Full Introspection Pipeline

Compose all three for complete analysis:

```python
class FullIntrospection(Agent[IntrospectionInput, IntrospectionOutput]):
    """
    Complete H-gent introspection pipeline.

    Flow:
    1. Hegel: Dialectic synthesis
    2. Lacan: Register analysis of synthesis
    3. Jung: Shadow analysis of register structure
    4. Meta-synthesis: Integration across all perspectives
    """

    async def invoke(self, input: IntrospectionInput) -> IntrospectionOutput:
        # Step 1: Dialectic
        dialectic = await self._hegel.invoke(DialecticInput(
            thesis=input.thesis,
            antithesis=input.antithesis,
            context=input.context,
        ))

        # Step 2: Register analysis
        register = await self._lacan.invoke(LacanInput(
            output=dialectic.synthesis or dialectic.sublation_notes,
            context=input.context,
        ))

        # Step 3: Shadow analysis
        if isinstance(register, LacanError):
            shadow = await self._jung.invoke(JungInput(
                system_self_image="System that generated unanalyzable output",
                behavioral_patterns=[register.message],
            ))
        else:
            shadow = await self._jung.invoke(JungInput(
                system_self_image="System after dialectic synthesis",
                declared_limitations=register.gaps,
                behavioral_patterns=[s.evidence for s in register.slippages],
            ))

        # Step 4: Meta-synthesis
        meta_notes = self._synthesize_perspectives(dialectic, register, shadow)

        return IntrospectionOutput(
            dialectic=dialectic,
            register_analysis=register,
            shadow_analysis=shadow,
            meta_notes=meta_notes,
        )
```

### IntrospectionOutput

```python
@dataclass
class IntrospectionInput:
    """Input for full introspection."""
    thesis: Any
    antithesis: Any | None = None
    context: dict[str, Any] | None = None

@dataclass
class IntrospectionOutput:
    """Complete introspection analysis."""
    dialectic: DialecticOutput        # Hegel's synthesis
    register_analysis: LacanResult    # Where synthesis lives
    shadow_analysis: JungOutput       # What synthesis excludes
    meta_notes: str                   # Integration across perspectives
```

---

## Meta-Synthesis Logic

The `meta_notes` field synthesizes insights from all three perspectives:

```python
def _synthesize_perspectives(
    self,
    dialectic: DialecticOutput,
    register: LacanResult,
    shadow: JungOutput,
) -> str:
    notes = []

    # Dialectic insight
    if dialectic.productive_tension:
        notes.append(f"Hegel: Tension held productive - {dialectic.sublation_notes}")
    else:
        notes.append(f"Hegel: Synthesis achieved - {dialectic.sublation_notes}")

    # Register insight
    if isinstance(register, LacanError):
        notes.append(f"Lacan: Real intrusion - {register.message}")
    else:
        dominant = "Symbolic" if register.register_location.symbolic > 0.5 else \
                   "Imaginary" if register.register_location.imaginary > 0.5 else \
                   "Real-proximate"
        notes.append(f"Lacan: Output primarily in {dominant} register")
        if register.slippages:
            notes.append(f"  Warning: {len(register.slippages)} register slippage(s)")

    # Shadow insight
    if shadow.shadow_inventory:
        notes.append(f"Jung: {len(shadow.shadow_inventory)} shadow content(s)")
        notes.append(f"  Persona-shadow balance: {shadow.persona_shadow_balance:.2f}")
    if shadow.projections:
        notes.append(f"  Warning: {len(shadow.projections)} projection(s)")

    # Integration recommendation
    notes.append("\nIntegration: " + _integration_recommendation(dialectic, register, shadow))

    return "\n".join(notes)
```

### Integration Recommendations

```python
def _integration_recommendation(dialectic, register, shadow) -> str:
    if dialectic.productive_tension:
        return "Hold dialectic tension while integrating shadow content gradually."

    if isinstance(register, LacanError):
        return "Address Real intrusion before continuing synthesis."

    if register.slippages:
        if shadow.persona_shadow_balance < 0.3:
            return "High slippage + low shadow integration - risk of instability."
        return "Address register slippages to stabilize synthesis."

    if shadow.persona_shadow_balance < 0.5:
        return "Synthesis stable but shadow underintegrated. Focus on integration."

    return "System showing good integration across all dimensions."
```

---

## Collective Shadow Analysis

Beyond individual agent shadow, examine system-level shadow:

```python
@dataclass
class CollectiveShadowInput:
    """Input for system-level shadow analysis."""
    system_description: str       # Overall system self-description
    agent_personas: list[str]     # Individual agent self-images
    emergent_behaviors: list[str] # Behaviors from composition

class CollectiveShadowAgent(Agent[CollectiveShadowInput, CollectiveShadow]):
    """
    System-level shadow analysis.

    Examines shadow that emerges from agent composition—
    content that no individual agent owns but the system excludes.
    """

    async def invoke(self, input: CollectiveShadowInput) -> CollectiveShadow:
        # Build shadow from system description
        shadow_inventory = build_shadow_inventory(...)

        # Detect emergent shadow - what appears only in composition
        emergent_shadow = []
        for behavior in input.emergent_behaviors:
            if not any(persona in behavior for persona in input.agent_personas):
                emergent_shadow.append(f"Emergent: {behavior}")

        # System-level projections
        projections = detect_system_projections(input)

        return CollectiveShadow(
            collective_persona=input.system_description,
            shadow_inventory=shadow_inventory,
            system_level_projections=projections,
            emergent_shadow_content=emergent_shadow,
        )
```

**Key insight**: Composition creates shadow that no individual component owns. The collective shadow is not the sum of individual shadows—it's emergent.

---

## Composition as Morphisms

Each pipeline is a morphism in the agent category:

```
HegelLacanPipeline:  DialecticOutput → LacanResult
LacanJungPipeline:   LacanResult → JungOutput
JungHegelPipeline:   JungOutput → DialecticOutput
FullIntrospection:   IntrospectionInput → IntrospectionOutput
```

These compose via the standard `>>` operator:

```python
# Sequential composition
hegel_lacan = hegel >> lacan_pipeline
lacan_jung = lacan >> jung_pipeline

# Full pipeline via composition
full = hegel >> lacan >> jung >> meta_synthesis
```

---

## Convenience Factories

```python
def hegel_to_lacan() -> HegelLacanPipeline:
    """Create Hegel → Lacan pipeline."""
    return HegelLacanPipeline()

def lacan_to_jung() -> LacanJungPipeline:
    """Create Lacan → Jung pipeline."""
    return LacanJungPipeline()

def jung_to_hegel() -> JungHegelPipeline:
    """Create Jung → Hegel pipeline."""
    return JungHegelPipeline()

def full_introspection() -> FullIntrospection:
    """Create full H-gent introspection pipeline."""
    return FullIntrospection()

def collective_shadow() -> CollectiveShadowAgent:
    """Create collective shadow agent."""
    return CollectiveShadowAgent()
```

---

## When to Use Each Pipeline

| Pipeline | Use When |
|----------|----------|
| `hegel_to_lacan` | Need to check if synthesis is merely aspirational |
| `lacan_to_jung` | Register analysis reveals gaps to explore |
| `jung_to_hegel` | Shadow content needs integration with persona |
| `full_introspection` | Complete system self-examination |
| `collective_shadow` | Multi-agent system audit |

---

## See Also

- [README.md](README.md) — H-gent overview
- [hegel.md](hegel.md) — Dialectical synthesis
- [lacan.md](lacan.md) — Register analysis
- [jung.md](jung.md) — Shadow integration
- [contradiction.md](contradiction.md) — Tension detection
- [sublation.md](sublation.md) — Tension resolution

---

*"Each tradition sees what the others miss. Together, they see the whole."*
