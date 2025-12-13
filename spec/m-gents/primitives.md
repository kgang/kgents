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

---

## Stigmergic Primitives

### PheromoneAgent

Deposit and sense environmental traces for indirect coordination.

```python
PheromoneAgent: (Concept, Action) → TraceDeposit

class PheromoneAgent(Agent[tuple[Concept, Action], TraceDeposit]):
    """
    Environmental memory via pheromone-like traces.

    Instead of storing memories explicitly, deposit traces
    that influence future behavior through gradients.

    Integration with void.tithe: trace deposit IS the tithe—
    paying forward for future agents.
    """
    field: PheromoneField
    decay_rate: float = 0.1  # Natural forgetting per time unit

    async def invoke(self, input: tuple[Concept, Action]) -> TraceDeposit:
        concept, action = input
        outcome = await self.evaluate_outcome(action)

        # Deposit proportional to outcome quality
        intensity = 1.0 + (outcome.success * 0.5)
        await self.field.deposit(concept, intensity)

        return TraceDeposit(
            concept=concept,
            intensity=intensity,
            decay_rate=self.decay_rate,
            timestamp=now()
        )

    async def follow_gradient(self, position: Concept) -> Concept:
        """Move toward strongest trace (ant algorithm)."""
        neighbors = await self.field.sense(position)
        if not neighbors:
            return await self.explore()  # Bushwhacking
        # Probabilistic selection biased by intensity
        return self.weighted_choice(neighbors)
```

### HiveMindAgent

Collective memory emerging from distributed traces.

```python
HiveMindAgent: Query → CollectiveRecollection

class HiveMindAgent(Agent[Query, CollectiveRecollection]):
    """
    Memory as emergent property of many trace depositors.

    No central store—consensus emerges from accumulated traces.
    Like ant colonies finding shortest paths without planning.
    """
    field: PheromoneField
    participants: list[StigmergicAgent]

    async def invoke(self, query: Query) -> CollectiveRecollection:
        # Multiple agents sense the field
        readings = await asyncio.gather(*[
            agent.sense(query.concept)
            for agent in self.participants
        ])

        # Consensus from convergent readings
        consensus = self.aggregate(readings)

        return CollectiveRecollection(
            query=query,
            consensus=consensus,
            confidence=self.agreement_score(readings),
            trace_count=len([r for r in readings if r])
        )
```

---

## Wittgensteinian Primitives

### LanguageGameAgent

Memory retrieval as playing a language game.

```python
LanguageGameAgent: (Concept, Context) → ValidMoves

class LanguageGameAgent(Agent[tuple[Concept, Context], list[Move]]):
    """
    Memory as knowing-how-to-play.

    From Wittgenstein: meaning is use. A concept's "memory"
    is the set of valid moves one can make with it in context.

    Modeled as polynomial functor: P(y) = Σₛ y^{D(s)}
    - S: positions (states)
    - D(s): directions (valid moves from state s)
    """
    games: dict[str, LanguageGame]  # Known games

    async def invoke(self, input: tuple[Concept, Context]) -> list[Move]:
        concept, context = input

        # Find applicable game
        game = self.find_game(context)
        if not game:
            return []  # Don't know how to play

        # Current position from concept
        position = game.locate(concept)

        # Valid moves from this position
        directions = game.directions(position)

        return [
            Move(
                from_position=position,
                direction=d,
                result=game.apply(position, d),
                grammar_check=game.is_grammatical(position, d)
            )
            for d in directions
        ]

    def find_game(self, context: Context) -> Optional[LanguageGame]:
        """Which language game are we playing?"""
        for name, game in self.games.items():
            if game.matches_context(context):
                return game
        return None
```

### GrammarEvolver

Learn the rules of language games from interaction.

```python
GrammarEvolver: Interaction → GameUpdate

class GrammarEvolver(Agent[Interaction, GameUpdate]):
    """
    Language games evolve through use.

    When novel moves succeed, they become grammatical.
    When moves fail, the game learns new constraints.

    "For a large class of cases... the meaning of a word is its use."
    """
    games: dict[str, LanguageGame]

    async def invoke(self, interaction: Interaction) -> GameUpdate:
        game = self.games.get(interaction.game_name)
        if not game:
            # New game discovered
            game = LanguageGame.bootstrap(interaction)
            self.games[interaction.game_name] = game
            return GameUpdate(action="created", game=game)

        # Observe move and outcome
        move = interaction.move
        outcome = interaction.outcome

        if outcome.success:
            if not game.is_grammatical(move.from_position, move.direction):
                # Successful novel move → expand grammar
                game.add_valid_move(move.from_position, move.direction)
                return GameUpdate(action="expanded", move=move)
        else:
            if game.is_grammatical(move.from_position, move.direction):
                # Failed grammatical move → context matters more
                game.add_context_constraint(move, interaction.context)
                return GameUpdate(action="constrained", move=move)

        return GameUpdate(action="unchanged")
```

---

## Active Inference Primitives

### FreeEnergyAgent

Memory retrieval minimizing expected free energy.

```python
FreeEnergyAgent: Observation → Action

class FreeEnergyAgent(Agent[Observation, Action]):
    """
    Memory in service of self-evidencing.

    Under the Free Energy Principle, agents are generative models
    that minimize prediction error. Memory supports:
    1. Better predictions (reduce surprise)
    2. Policy selection (reduce expected future surprise)
    3. Model update (learning)
    """
    generative_model: GenerativeModel  # Beliefs about world
    preferences: Distribution  # Desired states

    async def invoke(self, observation: Observation) -> Action:
        # Update beliefs given observation (perception)
        posterior = await self.infer_hidden_states(observation)

        # Compute expected free energy for each possible action
        policies = self.enumerate_policies()
        G = {}
        for policy in policies:
            G[policy] = await self.expected_free_energy(
                policy,
                posterior,
                self.preferences
            )

        # Select policy minimizing expected free energy
        best_policy = min(policies, key=lambda p: G[p])

        return best_policy.first_action()

    async def expected_free_energy(
        self,
        policy: Policy,
        beliefs: Distribution,
        preferences: Distribution
    ) -> float:
        """
        G = E[log Q(s) - log P(o|s) - log P(s)]

        Balances:
        - Epistemic value (information gain)
        - Pragmatic value (achieving preferred states)
        """
        # Predict states under policy
        predicted_states = await self.predict_under_policy(policy, beliefs)

        # Epistemic: how much would we learn?
        epistemic = self.info_gain(beliefs, predicted_states)

        # Pragmatic: how close to preferences?
        pragmatic = self.kl_divergence(predicted_states, preferences)

        return pragmatic - epistemic  # Lower is better
```

### SurpriseMinimizer

Consolidation driven by prediction error.

```python
SurpriseMinimizer: MemorySet → ConsolidatedMemory

class SurpriseMinimizer(Agent[set[Memory], HolographicMemory]):
    """
    Consolidation as free energy minimization.

    Keep memories that reduce prediction error.
    Compress memories that add only complexity.
    Forget memories that conflict with world model.
    """
    world_model: GenerativeModel

    async def invoke(self, memories: set[Memory]) -> HolographicMemory:
        consolidated = HolographicMemory()

        for memory in memories:
            # How surprising is this memory given our model?
            surprise = await self.compute_surprise(memory)

            # How much does it improve the model?
            improvement = await self.model_improvement(memory)

            if improvement > surprise:
                # Memory reduces overall free energy → keep
                consolidated.store(memory, resolution=1.0)
            elif improvement > 0:
                # Marginal improvement → compress
                consolidated.store(memory, resolution=0.5)
            # else: memory increases free energy → forget

        return consolidated
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

## Cartographic Primitives

### CartographerAgent

See [holographic.md#the-cartography-layer](holographic.md#the-cartography-layer).

```python
CartographerAgent: (ContextVector, Resolution) → HoloMap
```

The Cartographer projects high-dimensional memory space into navigable topology.

**Integrations**:
- L-gent: Provides embedding space (terrain)
- N-gent: Provides SemanticTraces (desire lines)
- B-gent: Constrains resolution via token budget

### PathfinderAgent

```python
PathfinderAgent: Goal → NavigationPlan
```

Navigates via desire lines (historical paths) rather than inventing new routes.

Two modes:
1. **Desire Line Navigation**: Follow historical paths (safe, high confidence)
2. **Bushwhacking**: No history, must explore (risky, low confidence)

### ContextInjector

```python
ContextInjector: (AgentState, Task) → OptimalContext
```

Produces optimal, budget-constrained, foveated context for any turn.

**The answer to**: "What is the most perfect context injection for any given turn?"

---

## Integration Map (Updated)

```
┌─────────────────────────────────────────────────────────────┐
│                      M-gent (Cognitive)                      │
│    RecollectionAgent, ConsolidationAgent, ProspectiveAgent   │
│    CartographerAgent, PathfinderAgent, ContextInjector       │
├─────────────────────────────────────────────────────────────┤
│           ↕ terrain              ↕ traces                    │
│    ┌─────────────┐         ┌─────────────┐                  │
│    │   L-gent    │         │   N-gent    │                  │
│    │ (embeddings)│         │  (history)  │                  │
│    └─────────────┘         └─────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│                      D-gent (Storage)                        │
│    VolatileAgent, PersistentAgent, UnifiedMemory, VectorAgent│
└─────────────────────────────────────────────────────────────┘
```

---

## Bi-Temporal Primitives

### BiTemporalStore

Memory with explicit event-time and knowledge-time separation.

```python
BiTemporalStore: BiTemporalQuery → list[BiTemporalFact]

class BiTemporalStore(Agent[BiTemporalQuery, list[BiTemporalFact]]):
    """
    Two-dimensional temporal memory.

    Every fact has:
    - t_event: when did this happen in the world?
    - t_known: when did the agent learn this?

    Enables:
    - Point-in-time queries: "What did I know at time T?"
    - Retroactive correction: "I now know X was wrong"
    - Belief archaeology: "How has my understanding evolved?"
    """
    facts: list[BiTemporalFact]

    async def invoke(self, query: BiTemporalQuery) -> list[BiTemporalFact]:
        results = []
        for fact in self.facts:
            # Match event time if specified
            if query.as_of_event and fact.t_event > query.as_of_event:
                continue
            # Match knowledge time if specified
            if query.as_of_known and fact.t_known > query.as_of_known:
                continue
            # Skip superseded facts unless we want the full history
            if fact.superseded_by and not query.include_superseded:
                continue
            if query.matches(fact.content):
                results.append(fact)
        return results

    async def correct(self, fact_id: str, new_content: Any, reason: str):
        """Retroactively correct a belief without losing history."""
        old_fact = self.get(fact_id)
        new_fact = BiTemporalFact(
            content=new_content,
            t_event=old_fact.t_event,  # Same event time
            t_known=now(),             # New knowledge time
        )
        old_fact.superseded_by = new_fact.id
        self.facts.append(new_fact)
```

### BeliefArchaeologist

Trace how understanding has evolved over time.

```python
BeliefArchaeologist: Concept → BeliefTimeline

class BeliefArchaeologist(Agent[Concept, BeliefTimeline]):
    """
    Excavate the layers of belief about a concept.

    "What did I believe about X at time T?"
    "When did my understanding change?"
    "What caused the revision?"
    """
    store: BiTemporalStore

    async def invoke(self, concept: Concept) -> BeliefTimeline:
        # Get all versions, including superseded
        all_facts = await self.store.invoke(
            BiTemporalQuery(
                pattern=concept,
                include_superseded=True
            )
        )

        # Build timeline
        timeline = BeliefTimeline(concept=concept)
        for fact in sorted(all_facts, key=lambda f: f.t_known):
            timeline.add_epoch(
                belief=fact.content,
                started=fact.t_known,
                ended=all_facts[fact.superseded_by].t_known if fact.superseded_by else None,
                superseded_by=fact.superseded_by
            )

        return timeline
```

---

## Trace Monoid Primitives

### CausalConeAgent

Navigate the causal structure of memory.

```python
CausalConeAgent: MemoryEvent → CausalCone

class CausalConeAgent(Agent[MemoryEvent, CausalCone]):
    """
    Memory respects causality.

    Given an event, find:
    - Past cone: what caused this?
    - Future cone: what did this cause?
    - Concurrent: what was independent?
    """
    weave: TraceMonoid

    async def invoke(self, event: MemoryEvent) -> CausalCone:
        past = self.weave.ancestors(event)
        future = self.weave.descendants(event)
        concurrent = self.weave.independent_of(event)

        return CausalCone(
            event=event,
            past_cone=past,
            future_cone=future,
            concurrent=concurrent,
            depth=max(len(past), len(future))
        )
```

### KnotAgent

Synchronization barrier for merging memory branches.

```python
KnotAgent: list[MemoryBranch] → MergedMemory

class KnotAgent(Agent[list[MemoryBranch], MergedMemory]):
    """
    A Knot is a synchronization barrier in the Weave.

    When multiple concurrent memory branches need to reconcile:
    1. Identify conflicts
    2. Apply merge strategy
    3. Create unified view

    Like a git merge for memories.
    """

    async def invoke(self, branches: list[MemoryBranch]) -> MergedMemory:
        # Find common ancestor
        common = self.find_common_ancestor(branches)

        # Identify divergences
        divergences = []
        for branch in branches:
            events_since = branch.events_since(common)
            divergences.append(events_since)

        # Detect conflicts (same concept, different content)
        conflicts = self.detect_conflicts(divergences)

        # Resolve
        merged_events = []
        for conflict in conflicts:
            resolution = await self.resolve_conflict(conflict)
            merged_events.append(resolution)

        # Non-conflicting events just union
        for div in divergences:
            for event in div:
                if event not in conflicts:
                    merged_events.append(event)

        return MergedMemory(
            events=merged_events,
            knot_point=now(),
            source_branches=[b.id for b in branches]
        )
```

---

## See Also

- [holographic.md](holographic.md) - Architecture details
- [README.md](README.md) - Philosophy and Four Pillars
- [../anatomy.md](../anatomy.md) - Symbiont and Hypnagogic patterns
