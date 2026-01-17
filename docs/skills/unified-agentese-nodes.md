# Unified AGENTESE Nodes

> *"Every node registered is a capability gained. Every connection wired is synergy earned."*

This skill documents the unified AGENTESE integration for the new service nodes.

## Overview

The unified AGENTESE nodes provide:

| Path | Service | Purpose |
|------|---------|---------|
| `self.axiom.*` | AxiomDiscoveryPipeline | Personal axiom discovery from decision history |
| `self.dialectic.*` | DialecticalFusionService | Kent+Claude thesis-antithesis-synthesis |
| `self.skill.*` | JITInjector + SkillRegistry | Just-in-time skill surfacing |
| `concept.fusion.*` | FusionConceptNode | Abstract fusion ontology (categorical cocone) |

## AGENTESE Paths

### self.axiom.* (Personal Axiom Discovery)

Discovers personal axioms - the L<0.05 fixed points Kent never violates.

```
self.axiom.manifest       - Axiom system status
self.axiom.discover       - Discover personal axioms from decision history
self.axiom.validate       - Validate if content qualifies as an axiom
self.axiom.contradictions - Check for contradictions between axioms
```

**Philosophy**: "Axioms are not stipulated but discovered. They are the fixed points of your decision landscape."

**Example**:
```bash
# Via CLI
kg axiom discover --days 30

# Via AGENTESE gateway
POST /agentese/self/axiom/discover
{"days": 30, "max_candidates": 5}

# Via Logos
await logos.invoke("self.axiom.discover", observer, days=30)
```

### self.dialectic.* (Dialectical Fusion)

Kent+Claude thesis-antithesis-synthesis for decision-making.

```
self.dialectic.manifest   - Current dialectic state
self.dialectic.thesis     - Propose a thesis (Kent's position)
self.dialectic.antithesis - Generate antithesis (Claude's challenge)
self.dialectic.sublate    - Synthesize fusion (Aufhebung)
self.dialectic.history    - View fusion history
```

**Philosophy**: "The goal is not Kent's decisions or AI's decisions. The goal is fused decisions better than either alone."

**Example**:
```bash
# Via CLI
kg decide --kent "Use existing framework" --kent-reasoning "Scale, resources" \
          --claude "Build novel system" --claude-reasoning "Joy-inducing" \
          --topic "Framework choice"

# Via AGENTESE gateway
POST /agentese/self/dialectic/sublate
{
  "topic": "Framework choice",
  "kent_view": "Use existing framework",
  "kent_reasoning": "Scale, resources, production-ready",
  "claude_view": "Build novel system",
  "claude_reasoning": "Joy-inducing, novel contribution"
}
```

### self.skill.* (JIT Skill Injection)

Skills surface exactly when needed, not before.

```
self.skill.manifest   - Registry status and statistics
self.skill.active     - Currently active/injected skills
self.skill.inject     - Inject skills for a task
self.skill.evolve     - Trigger skill evolution from usage patterns
self.skill.search     - Search for skills by keyword
self.skill.gotchas    - Get gotchas for a task
```

**Philosophy**: "Learn from what worked, forget what didn't."

**Example**:
```bash
# Via CLI
kg skill inject "Add a Crown Jewel service"

# Via AGENTESE gateway
POST /agentese/self/skill/inject
{"task": "Add a new AGENTESE node for the Atelier service"}
```

### concept.fusion.* (Fusion Ontology)

The abstract/theoretical view of dialectical fusion.

```
concept.fusion.manifest - The Emerging Constitution (7 articles)
concept.fusion.cocone   - The categorical cocone structure
```

**Philosophy**: "The cocone is not a compromise. It is an Aufhebung - a lifting up that preserves and transcends."

## Service Dependencies

### Providers (services/providers.py)

| Provider | Service | Registration |
|----------|---------|--------------|
| `get_skill_registry()` | SkillRegistry | `skill_registry` |
| `get_jit_injector()` | JITInjector | `jit_injector` |
| `get_dialectic_service()` | DialecticalFusionService | `dialectic_service` |
| `get_ashc_self_awareness()` | ASHCSelfAwareness | `ashc_self_awareness` |
| `get_axiom_discovery_pipeline()` | AxiomDiscoveryPipeline | `axiom_discovery_pipeline` |

### DI Wiring

All services use the **Enlightened Resolution** pattern:

```python
@node(
    "self.skill",
    dependencies=(),  # No required deps - uses singletons
)
class SkillNode(BaseLogosNode):
    def __init__(
        self,
        registry: SkillRegistry | None = None,  # Optional = graceful fallback
    ) -> None:
        self._registry = registry or get_skill_registry()
```

## Synergy Opportunities

### 1. Axiom Discovery + ASHC Grounding Check

When an axiom is discovered, verify it's grounded in the constitutional graph:

```python
# Discover axiom
result = await axiom_pipeline.discover_axioms()

# For each candidate, check ASHC grounding
for candidate in result.top_axioms:
    grounding = await ashc_awareness.am_i_grounded(candidate.content)
    if not grounding.is_grounded:
        # Flag as potentially unstable
```

### 2. Dialectical Fusion + Witness Mark Recording

Every fusion should emit a Witness mark:

```python
# After fusion
await bus.publish(
    WitnessTopics.DIALECTIC_SYNTHESIS,
    {
        "fusion_id": fusion.id,
        "topic": fusion.topic,
        "result": fusion.result.value,
    }
)
```

### 3. Skill Injection + Active Axioms Context

Skills can be weighted by alignment with discovered axioms:

```python
# Get active axioms
axioms = await axiom_pipeline.discover_axioms()

# Include axiom context in skill activation
context = TaskContext(
    task=task,
    active_axioms=[a.content for a in axioms.top_axioms],
)
```

### 4. Constitutional Graph + ASHC Self-Awareness

Self-reflective queries about why things exist:

```python
# "Why does this file exist?"
justification = await ashc_awareness.what_principle_justifies(
    action="create services/foo/node.py"
)

# Returns: principle + loss score + derivation path
```

## Event Bus Topics

The new services emit events via WitnessSynergyBus:

| Topic | Event Type | Description |
|-------|------------|-------------|
| `witness.dialectic.thesis` | DIALECTIC | Kent proposes thesis |
| `witness.dialectic.antithesis` | DIALECTIC | Claude challenges |
| `witness.dialectic.synthesis` | DIALECTIC | Fusion achieved |
| `witness.dialectic.veto` | DIALECTIC | Disgust veto invoked |
| `witness.axiom.discovered` | AXIOM | New axiom found |
| `witness.axiom.validated` | AXIOM | Axiom validated |
| `witness.axiom.contradiction` | AXIOM | Contradiction detected |
| `witness.skill.injected` | SKILL | Skills surfaced |
| `witness.skill.outcome_recorded` | SKILL | Usage feedback |
| `witness.skill.composition_suggested` | SKILL | Auto-composition |

## Health Check

Use the unified health check to verify all nodes:

```python
from protocols.agentese.health import check_unified_nodes_health

report = await check_unified_nodes_health()
print(report.to_text())
```

**Expected output**:
```
AGENTESE Health Report
==================================================
Timestamp: 2025-01-16T...
Overall Status: HEALTHY

Total Nodes: 4
  Healthy: 4
  Degraded: 0
  Unhealthy: 0

[Completed in 45.2ms]
```

## Gotchas

1. **@node runs at import time**: Module must be imported or node won't register.
   - FIX: Ensure module is listed in `gateway._import_node_modules()`

2. **DI dependencies must match param names**: `@node(dependencies=("foo",))` requires `def __init__(self, foo=None)`
   - FIX: Use exact matching names

3. **Skills bootstrap lazily**: Call `bootstrap_skills()` before first use.
   - The SkillNode does this automatically in `_ensure_bootstrapped()`

4. **Dialectic service uses in-memory store**: Fusions are not persisted by default.
   - FIX: Wire to WitnessPersistence for durability

5. **Axiom discovery requires marks**: No decisions in MarkStore = no axioms discovered.
   - FIX: Ensure `kg witness mark` or `km` commands are capturing decisions

## Testing

Run the integration tests:

```bash
cd impl/claude
uv run pytest protocols/agentese/_tests/test_unified_nodes.py -v
```

## File Locations

| File | Purpose |
|------|---------|
| `/impl/claude/protocols/agentese/gateway.py` | Node import registration |
| `/impl/claude/services/providers.py` | Service provider functions |
| `/impl/claude/services/zero_seed/axiom_node.py` | AxiomNode implementation |
| `/impl/claude/services/dialectic/node.py` | DialecticNode + FusionConceptNode |
| `/impl/claude/services/skill_injection/node.py` | SkillNode implementation |
| `/impl/claude/protocols/agentese/health.py` | Unified health check |
| `/impl/claude/protocols/agentese/_tests/test_unified_nodes.py` | Integration tests |

---

*Philosophy: "The unified AGENTESE nodes make the invisible visible. Every decision witnessed. Every skill surfaced. Every synthesis recorded."*
