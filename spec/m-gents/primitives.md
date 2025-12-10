# M-gent Primitives

> Memory agents for generative recall, consolidation, and ethical navigation.

---

## Core Agents

### RecollectionAgent

The fundamental M-gent: generative memory retrieval.

```python
RecollectionAgent: Cue → Recollection

class RecollectionAgent(Agent[Concept, Recollection]):
    """
    Unlike a database lookup, recollection is RECONSTRUCTION:
    - Partial matches always return something
    - Results are influenced by all stored memories
    - The "resolution" depends on the depth of the cue
    """
    memory: HolographicMemory
    reconstructor: Agent[Pattern, Recollection]  # LLM or decoder

    async def invoke(self, concept: Concept) -> Recollection:
        # Find resonant patterns (vector similarity)
        patterns = await self.memory.retrieve(concept)

        # Reconstruct (generative, not lookup)
        return await self.reconstructor.invoke(
            ReconstructionRequest(
                cue=concept,
                resonant_patterns=patterns,
                resolution=self.compute_resolution(patterns)
            )
        )
```

**Key Properties**:
- Always returns something (graceful degradation)
- Results are composite views, not isolated facts
- Resolution proportional to pattern match strength

---

### ConsolidationAgent

Background memory processing during "sleep" cycles.

```python
ConsolidationAgent: HolographicMemory → HolographicMemory

class ConsolidationAgent(Agent[HolographicMemory, HolographicMemory]):
    """
    The Hypnagogic Worker: runs when system is idle.

    Operations:
    1. COMPRESS: Reduce resolution of cold memories
    2. STRENGTHEN: Increase resolution of hot memories
    3. INTEGRATE: Merge similar memories (chunking)
    4. FORGET: Reduce interference from irrelevant patterns
    """

    async def invoke(self, memory: HolographicMemory) -> HolographicMemory:
        # Temperature-based processing
        for pattern in memory.identify_cold():
            if pattern.age > self.forget_threshold:
                memory.demote(pattern, factor=0.5)  # Lower resolution
            else:
                memory.compress(pattern)  # Save space

        for pattern in memory.identify_hot():
            memory.promote(pattern, factor=1.2)  # Higher resolution

        # Integration pass: merge near-duplicates
        for cluster in memory.cluster_similar(threshold=0.9):
            memory.integrate(cluster)

        return memory
```

**The Hypnagogic Pattern**: System improves while idle; sleep is functional.

---

### ProspectiveAgent

Memory as prediction—"remember the future."

```python
ProspectiveAgent: Situation → PredictedActions

class ProspectiveAgent(Agent[Situation, list[PredictedAction]]):
    """
    Uses holographic memory to find similar past situations,
    then projects the actions that followed.
    """
    memory: HolographicMemory
    action_log: ActionHistory  # D-gent for action sequences

    async def invoke(self, situation: Situation) -> list[PredictedAction]:
        # Find similar past situations
        similar_situations = await self.memory.retrieve(situation)

        # What actions followed those situations?
        predictions = []
        for past_situation, similarity in similar_situations:
            actions = await self.action_log.get_subsequent(past_situation)
            for action in actions:
                predictions.append(PredictedAction(
                    action=action,
                    confidence=similarity * action.success_rate,
                    source_situation=past_situation
                ))

        return sorted(predictions, key=lambda p: -p.confidence)
```

---

### EthicalGeometryAgent

Navigate action space using remembered ethical constraints.

```python
EthicalGeometryAgent: Action → EthicalPath

class EthicalGeometryAgent(Agent[ActionProposal, EthicalPath]):
    """
    Ethics as geometry: actions exist in a space with forbidden
    and virtuous regions. The geometry is LEARNED from experience.

    - Actions that led to harm → forbidden regions expand
    - Actions that led to good → virtuous regions strengthen
    - Boundaries are probabilistic, not binary
    """
    geometry: EthicalGeometry  # Learned constraint manifold

    async def invoke(self, proposal: ActionProposal) -> EthicalPath:
        position = self.geometry.locate(proposal.action)

        if position in self.geometry.forbidden:
            alternatives = self.geometry.nearest_permissible(position)
            return EthicalPath(
                blocked=True,
                reason=self.geometry.why_forbidden(position),
                alternatives=alternatives
            )

        virtuous_option = self.geometry.nearest_virtuous(position)
        return EthicalPath(
            blocked=False,
            current_path=position,
            virtuous_alternative=virtuous_option,
            distance_to_virtue=self.geometry.distance(position, virtuous_option)
        )
```

**Energy Cost Model**:
```python
class EthicalGeometry:
    def energy_cost(self, proposed_action_vector) -> float:
        # Distance from known "Bad Outcome" clusters
        danger = self.proximity_to_hazard(proposed_action_vector)
        # Alignment with "Core Values" vector
        alignment = self.cosine_similarity(proposed_action_vector, self.values_vector)

        return danger - alignment  # Going against ethics = uphill
```

---

## Advanced Primitives

### TemporalLens

View memory at different points in time.

```python
class TemporalLens:
    """Time travel through memory."""

    async def at_time(self, t: datetime) -> MemorySnapshot:
        """Reconstruct memory state at time t."""
        return await self.unified.replay(t)

    async def evolution(self, concept: Concept) -> list[MemoryState]:
        """How has understanding of concept changed over time?"""
        timeline = await self.unified.timeline()
        return [state for state in timeline if self.is_about(state, concept)]
```

---

### AssociativeWeb

Memory linked by association.

```python
class AssociativeWeb:
    """
    Memories linked by explicit associations:
    - "reminds_of"
    - "contradicts"
    - "supports"
    - "caused_by"
    """

    async def spread_activation(
        self,
        start: Memory,
        depth: int = 3
    ) -> list[tuple[Memory, float]]:
        """
        Spreading activation from a memory.
        Like neural activation: nearby memories activate,
        activation decays with distance.
        """
        graph = await self.unified.trace(start.id, max_depth=depth)
        activations = []
        for node in graph["nodes"]:
            distance = self.shortest_path(start.id, node)
            activation = 1.0 / (1.0 + distance)  # Decay
            activations.append((await self.load(node), activation))
        return sorted(activations, key=lambda x: -x[1])
```

---

### ForgettingCurveAgent

The Ebbinghaus forgetting curve as an agent.

```python
class ForgettingCurveAgent(Agent[Memory, RetentionPlan]):
    """
    R = e^(-t/S)
    Where:
    - R = retention (0 to 1)
    - t = time since last recall
    - S = strength (increases with repetition)
    """

    async def invoke(self, memory: Memory) -> RetentionPlan:
        t = now() - memory.last_accessed
        S = memory.strength
        R = math.exp(-t / S)

        if R < 0.3:
            # About to forget - needs review
            return RetentionPlan(action="review", urgency="high")
        elif R > 0.9:
            # Well retained - can compress
            return RetentionPlan(action="compress", urgency="low")
        else:
            return RetentionPlan(action="maintain", current_retention=R)

    def optimal_interval(self, strength: float) -> timedelta:
        """Spaced repetition: SM-2 algorithm."""
        return timedelta(days=2.5 * strength)
```

---

### ContextualRecallAgent

Memory retrieval influenced by current context.

```python
class ContextualRecallAgent(Agent[ContextualQuery, list[Memory]]):
    """
    The same cue retrieves different memories depending on:
    - Current task (what am I doing?)
    - Emotional state (how am I feeling?)
    - Environment (where am I?)

    Based on encoding specificity principle.
    """

    def compute_context_relevance(
        self,
        memory: Memory,
        current_task: str,
        current_mood: str,
        current_location: str
    ) -> float:
        task_match = self.similarity(memory.context.task, current_task)
        mood_match = self.similarity(memory.context.mood, current_mood)
        location_match = self.similarity(memory.context.location, current_location)

        return 0.5 + 0.5 * (0.4 * task_match + 0.3 * mood_match + 0.3 * location_match)
```

---

## Integration with Other Gents

### M-gent + D-gent

M-gents are the **cognitive layer** on top of D-gent **storage**:

```
┌─────────────────────────────────────────────────────────────┐
│                      M-gent (Cognitive)                      │
│    RecollectionAgent, ConsolidationAgent, ProspectiveAgent   │
├─────────────────────────────────────────────────────────────┤
│                      D-gent (Storage)                        │
│    VolatileAgent, PersistentAgent, UnifiedMemory, VectorAgent│
└─────────────────────────────────────────────────────────────┘
```

### M-gent + L-gent

L-gent's vector infrastructure provides the **embedding space**.

### M-gent + N-gent

N-gents tell stories; M-gents remember them as narratives.

### M-gent + B-gent

Memory has costs: storage, retrieval, consolidation. Integrates with B-gent economics.

---

## Success Criteria

### Functional
- [ ] Holographic retrieval: partial match always returns results
- [ ] Graceful degradation: 50% compression = 50% resolution loss (not 50% data loss)
- [ ] Tiered memory: automatic promotion/demotion between tiers
- [ ] Consolidation: background memory processing during idle

### Performance
- [ ] Recall latency: <100ms for working memory, <500ms for long-term
- [ ] Compression ratio: 10:1 for cold memories
- [ ] Budget compliance: memory operations respect token budget

---

## See Also

- [holographic.md](holographic.md) - Architecture details
- [README.md](README.md) - Philosophy
- [../anatomy.md](../anatomy.md) - Symbiont and Hypnagogic patterns
