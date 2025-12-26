# Operationalization: Pilots Integration

> *"The pilot IS the validation. The theory IS the spine. The code IS the proof."*

**Theory Source**: All Parts (as validated by pilots)
**Sub-Agent**: a1d46f4
**Status**: Ready for execution (E1, E3 complete)

---

## Current Status (Updated 2025-12-26)

### Foundation Services Complete

| Proposal | Service | Status | Used By |
|----------|---------|--------|---------|
| **E1** | Kleisli Witness Composition | **DONE** | ALL pilots |
| **E3** | Dialectical Fusion Service | **DONE** | disney-portal, rap-coach |
| E5 | Trust Gradient | **EXISTS** | rap-coach (ready to use) |

### Key Files

| Service | Location |
|---------|----------|
| Kleisli Composition | `impl/claude/services/witness/kleisli.py` |
| Dialectical Fusion | `impl/claude/services/dialectic/fusion.py` |
| Trust Gradient | `impl/claude/services/witness/trust/gradient.py` |

---

## Executive Summary

The 5 pilots validate different aspects of the theory. Each pilot proves specific theoretical claims. This document maps theory chapters to pilots and identifies which proposals each pilot validates.

---

## Pilot-Theory Mapping

### Overview

| Pilot | Primary Chapters | Theory Claims Validated | Joy Dimension |
|-------|------------------|------------------------|---------------|
| **trail-to-crystal** | Ch 9, 16, 11 | Constitution as Reward, Witness, Meta-DP | FLOW |
| **wasm-survivors** | Ch 7, 13, 10 | Galois Loss, Heterarchy, Value Agent | FLOW |
| **disney-portal** | Ch 5, 12, 17 | Sheaf Coherence, Multi-Agent, Dialectic | WARMTH |
| **rap-coach** | Ch 7, 16, 17 | Galois Loss, Witness, Dialectic | SURPRISE |
| **sprite-procedural** | Ch 8, 11, 6 | Fixed Points, Meta-DP, Modularization | SURPRISE |

---

## Pilot 1: trail-to-crystal-daily-lab (WEDGE)

### Theory Validation

**Chapters Validated**: 9 (Agent DP), 16 (Witness), 11 (Meta-DP)

| Claim | From Chapter | How Pilot Validates |
|-------|--------------|---------------------|
| Constitution IS reward | Ch 9 | Every action scored against 7 principles |
| Witness traces are first-class | Ch 16 | Mark → Trace → Crystal pipeline |
| Self-improvement is possible | Ch 11 | Daily reflection improves future behavior |

### Proposals Validated

| Proposal | Description | Validation Method | Status |
|----------|-------------|-------------------|--------|
| D1 | BellmanConstitutionalEquation | Actions optimized for constitutional reward | **MAIN REMAINING** |
| **E1** | Kleisli Witness Composition | Marks compose through the day | **DONE** |
| D3 | DriftMonitor | Detect when behavior drifts from intention | Pending |

### E1 Integration (Ready)

The Kleisli composition infrastructure is complete and ready to use:

```python
from services.witness.kleisli import (
    Witnessed,
    kleisli_compose,
    kleisli_chain,
    witnessed_operation,
)

# Daily marks compose via Writer monad
@witnessed_operation(action="morning_intention")
async def set_morning_intention(intention: str) -> str:
    ...

@witnessed_operation(action="end_of_day_reflection")
async def reflect_on_day(marks: list[Mark]) -> Crystal:
    ...

# Compose through the day
pipeline = kleisli_chain(set_morning_intention, execute_actions, reflect_on_day)
```

**Location**: `impl/claude/services/witness/kleisli.py`

### Implementation Requirements

```python
# Core components for trail-to-crystal

class DailyLab:
    """Trail-to-crystal daily lab."""

    def __init__(
        self,
        witness: WitnessService,
        constitution: ConstitutionalEnforcer,
        bellman: BellmanConstitutionalEquation
    ):
        self.witness = witness
        self.constitution = constitution
        self.bellman = bellman

    async def mark_action(
        self,
        action: str,
        intention: str,
        principle_weights: Dict[str, float]
    ) -> Mark:
        """Mark an action with intention."""
        # Score against constitution
        scores = await self.constitution.check(action)

        # Create mark with scores
        mark = await self.witness.mark(
            action=action,
            reasoning=intention,
            metadata={
                "principle_scores": scores.scores,
                "intention": intention
            }
        )

        return mark

    async def end_of_day_crystal(self) -> Crystal:
        """Generate end-of-day crystal."""
        # Get today's trace
        trace = await self.witness.get_trace(today=True)

        # Compress to crystal
        crystal = await self.witness.crystallize(
            trace,
            compression_ratio=0.1,
            preserve_rationale=True
        )

        # Add constitutional summary
        crystal.metadata["constitutional_score"] = self._compute_daily_score(trace)

        return crystal

    def _compute_daily_score(self, trace: Trace) -> float:
        """Compute constitutional score for the day."""
        scores = [m.principle_scores for m in trace.marks if m.principle_scores]
        if not scores:
            return 0.5

        return sum(
            sum(s.values()) / len(s)
            for s in scores
        ) / len(scores)
```

### Exit Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| User explains day via crystal | Kent narrates | < 2 minutes |
| System surfaces honest gap | Gap in crystal | Yes |
| Constitutional score computed | Daily score | Works |
| Marks compose | Kleisli composition | Laws hold |

---

## Pilot 2: wasm-survivors-witnessed-run-lab

### Theory Validation

**Chapters Validated**: 7 (Galois Loss), 13 (Heterarchy), 10 (Value Agent)

| Claim | From Chapter | How Pilot Validates |
|-------|--------------|---------------------|
| Galois Loss predicts failure | Ch 7 | High loss → build drift detected |
| Heterarchy enables contextual leadership | Ch 13 | Different agents lead different game phases |
| Value agents optimize reward | Ch 10 | Build choices maximize survival score |

### Proposals Validated

| Proposal | Description | Validation Method |
|----------|-------------|-------------------|
| G1 | Calibration Pipeline | Game decisions calibrate loss-difficulty |
| G2 | Task Triage Service | Route decisions by loss |
| M2 | HeterarchicalLeadership | Agent leads by competence |

### Implementation Requirements

```python
# Core components for wasm-survivors

class WitnessedRunLab:
    """Wasm-survivors witnessed run lab."""

    def __init__(
        self,
        galois: GaloisLossComputer,
        triage: TaskTriageService,
        leadership: HeterarchicalLeadershipService,
        witness: WitnessService
    ):
        self.galois = galois
        self.triage = triage
        self.leadership = leadership
        self.witness = witness

    async def evaluate_build_choice(
        self,
        current_build: str,
        proposed_upgrade: str
    ) -> dict:
        """Evaluate a build choice using Galois Loss."""
        # Compute loss for the choice
        choice_description = f"Upgrade from {current_build} to {proposed_upgrade}"
        loss = await self.galois.compute(choice_description)

        # Triage the decision
        triage = await self.triage.triage(choice_description)

        # Mark the decision
        await self.witness.mark(
            action="build_choice_evaluated",
            reasoning=f"Galois loss: {loss:.3f}, Triage: {triage.level.value}",
            metadata={
                "current_build": current_build,
                "proposed_upgrade": proposed_upgrade,
                "loss": loss,
                "triage_level": triage.level.value
            }
        )

        return {
            "loss": loss,
            "triage": triage.level.value,
            "recommendation": triage.recommended_strategy
        }

    async def detect_build_drift(
        self,
        run_history: list[dict]
    ) -> dict:
        """Detect if build is drifting from coherent strategy."""
        if len(run_history) < 3:
            return {"drift_detected": False}

        # Compute loss trajectory
        losses = [
            await self.galois.compute(str(h))
            for h in run_history[-5:]
        ]

        # Detect drift: increasing loss trend
        avg_recent = sum(losses[-3:]) / 3
        avg_early = sum(losses[:2]) / 2 if len(losses) > 2 else avg_recent

        drift_detected = avg_recent > avg_early + 0.1

        return {
            "drift_detected": drift_detected,
            "loss_trajectory": losses,
            "avg_recent": avg_recent,
            "avg_early": avg_early
        }

    async def select_phase_leader(
        self,
        game_phase: str,
        agents: list[str]
    ) -> str:
        """Select leader for current game phase."""
        context = LeadershipContext(
            task_domain=game_phase,
            trigger=LeadershipTrigger.NOVEL_SITUATION,
            participating_agents=agents,
            urgency=0.7
        )

        decision = self.leadership.select_leader(context)

        await self.witness.mark(
            action="phase_leader_selected",
            reasoning=decision.reasoning,
            metadata={
                "phase": game_phase,
                "leader": decision.leader_id,
                "score": decision.score
            }
        )

        return decision.leader_id
```

### Exit Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Galois loss API works | 4 endpoints | < 5s latency |
| Drift detection works | 3/3 scenarios | Detected |
| Heterarchical leadership | Leader changes by phase | Yes |
| Run is witnessed | All choices marked | Yes |

---

## Pilot 3: disney-portal-planner

### Theory Validation

**Chapters Validated**: 5 (Sheaf Coherence), 12 (Multi-Agent), 17 (Dialectic)

| Claim | From Chapter | How Pilot Validates |
|-------|--------------|---------------------|
| Sheaves enable local-to-global consistency | Ch 5 | Day plans glue into trip |
| Multi-agent coordination via cocones | Ch 12 | Disagreement resolved constructively |
| Dialectical fusion synthesizes perspectives | Ch 17 | Family preferences merged |

### Proposals Validated

| Proposal | Description | Validation Method | Status |
|----------|-------------|-------------------|--------|
| M1 | MultiAgentSheaf + Cocones | Family members' preferences glue | **Can use E3** |
| C4 | BeliefSheaf | Day plans form consistent beliefs | Pending |
| **E3** | DialecticalFusionService | Conflicting preferences fused | **DONE** |

### E3 Integration (Ready)

The dialectical fusion infrastructure is complete. M1 (MultiAgentSheaf) can build on E3's foundation:

```python
from services.dialectic.fusion import (
    DialecticalFusionService,
    Position,
    Fusion,
    FusionResult,
)

# E3 provides the fusion mechanics; M1 adds multi-agent coordination
service = DialecticalFusionService(llm=my_llm)

# Family member preferences can be modeled as positions
mom_position = Position(
    content="We should go to Fantasyland first",
    reasoning="It's less crowded in the morning",
    confidence=0.8,
    holder="mom",
)

# Fuse conflicting preferences using E3
fusion = await service.propose_fusion(
    topic="First park to visit",
    kent_view=mom_position.content,
    kent_reasoning=mom_position.reasoning,
    claude_view=dad_position.content,
    claude_reasoning=dad_position.reasoning,
)

# fusion.result: CONSENSUS | SYNTHESIS | KENT_PREVAILS | ...
# fusion.synthesis: The merged preference
```

**Location**: `impl/claude/services/dialectic/fusion.py`

**M1 Extension Path**: Build `MultiAgentSheaf` that:
1. Manages N agent positions (not just Kent/Claude)
2. Uses E3's `DialecticalFusionService` for pairwise fusion
3. Constructs cocones from repeated fusion

### Implementation Requirements

```python
# Core components for disney-portal

class DisneyPortalPlanner:
    """Disney portal planner with sheaf coordination."""

    def __init__(
        self,
        sheaf: MultiAgentSheaf,
        fusion: DialecticalFusionService,
        witness: WitnessService
    ):
        self.sheaf = sheaf
        self.fusion = fusion
        self.witness = witness

    async def add_family_member_preference(
        self,
        member_id: str,
        preferences: dict
    ):
        """Add a family member's preferences."""
        self.sheaf.add_belief(AgentBelief(
            agent_id=member_id,
            content=preferences,
            confidence=0.8,
            context=set(preferences.keys()),
            justification=f"{member_id}'s stated preferences"
        ))

    async def plan_day(self, day_date: str) -> dict:
        """Plan a single day, resolving conflicts."""
        # Get all family members' beliefs about this day
        members = list(self.sheaf.beliefs.keys())

        # Check compatibility
        compatible, conflict = self.sheaf.compatible(members)

        if compatible:
            # Beliefs glue cleanly
            glued = self.sheaf.glue(members)
            await self.witness.mark(
                action="day_plan_glued",
                reasoning="Family preferences compatible",
                metadata={"day": day_date, "glued": True}
            )
            return {"plan": glued.content, "method": "glued"}
        else:
            # Need dialectical fusion
            cocone = await self.sheaf.construct_cocone(
                members, conflict, self.llm
            )

            await self.witness.mark(
                action="day_plan_synthesized",
                reasoning=f"Resolved conflict via cocone: {conflict.conflict_type}",
                metadata={
                    "day": day_date,
                    "conflict_type": conflict.conflict_type,
                    "universality": cocone.universality_score
                }
            )

            return {"plan": cocone.synthesis, "method": "cocone"}

    async def explain_tradeoffs(self, plan: dict) -> str:
        """Explain the tradeoffs in the plan."""
        explanation = await self.llm.complete(f"""
Given this Disney trip plan:
{plan}

Explain:
1. What each family member wanted
2. What compromises were made
3. Why this plan balances everyone's joy

Be warm and positive.
""")
        return explanation
```

### Exit Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Sheaf gluing works | Family preferences | Compatible glue |
| Cocone synthesis works | Conflict resolution | Synthesis generated |
| Tradeoff explanation readable | Kent validates | 4/5 readable |
| Constitutional scoring | Per-day score | Works |

---

## Pilot 4: rap-coach-flow-lab

### Theory Validation

**Chapters Validated**: 7 (Galois Loss), 16 (Witness), 17 (Dialectic)

| Claim | From Chapter | How Pilot Validates |
|-------|--------------|---------------------|
| Galois Loss measures intent/delivery gap | Ch 7 | Take scored for intent alignment |
| Witness captures reasoning traces | Ch 16 | Session trace is immutable |
| Dialectic enables growth | Ch 17 | Feedback synthesizes coach + artist |

### Proposals Validated

| Proposal | Description | Validation Method | Status |
|----------|-------------|-------------------|--------|
| G3 | Loss Decomposition API | Shows WHY take has high loss | Pending |
| **E1** | Kleisli Witness Composition | Takes compose through session | **DONE** |
| E5 | Trust Gradient Dialectic | Coach earns trust over sessions | **EXISTS** |

### E1 + E5 Integration (Ready)

Both foundation services exist and can be used together:

```python
from services.witness.kleisli import Witnessed, witnessed_operation, kleisli_chain
from services.witness.trust.gradient import (
    TrustState,
    TrustLevel,
    can_execute_autonomously,
    Action,
)

# E1: Session takes compose via Kleisli
@witnessed_operation(action="take_recorded")
async def record_take(audio: bytes) -> TakeAnalysis:
    ...

@witnessed_operation(action="feedback_given")
async def provide_feedback(analysis: TakeAnalysis) -> Feedback:
    ...

# Compose session workflow
session_flow = kleisli_chain(record_take, analyze_take, provide_feedback)

# E5: Trust gradient for coach autonomy
trust = TrustState(level=TrustLevel.LEVEL_2, score=0.4)

# Coach can auto-approve routine feedback at trust level 2+
feedback_action = Action(name="suggest_timing_fix", description="", risk_tier=1)
if can_execute_autonomously(trust, feedback_action):
    await give_autonomous_feedback()

# Trust updates based on artist acceptance
trust = trust.update_aligned()  # Artist accepted feedback
```

**Locations**:
- Kleisli: `impl/claude/services/witness/kleisli.py`
- Trust: `impl/claude/services/witness/trust/gradient.py`

**E5 Enhancement Path**: Build `TrustWeightedFusion` that:
1. Uses `TrustState` to weight coach vs artist positions
2. Higher trust = more weight on coach suggestions
3. Trust delta from feedback acceptance/rejection

### Implementation Requirements

```python
# Core components for rap-coach

class RapCoachFlowLab:
    """Rap coach flow lab with witnessed sessions."""

    def __init__(
        self,
        galois: GaloisLossComputer,
        decomposition: LossDecompositionService,
        witness: WitnessService,
        trust: TrustWeightedFusion
    ):
        self.galois = galois
        self.decomposition = decomposition
        self.witness = witness
        self.trust = trust

    async def evaluate_take(
        self,
        intended_style: str,
        actual_take: str
    ) -> dict:
        """Evaluate a take against intended style."""
        # Compute loss (intent/delivery gap)
        description = f"Intended: {intended_style}\nDelivered: {actual_take}"
        loss = await self.galois.compute(description)

        # Decompose loss
        decomposition = await self.decomposition.decompose(description)

        # Mark the take
        mark = await self.witness.mark(
            action="take_evaluated",
            reasoning=decomposition.explanation,
            metadata={
                "loss": loss,
                "structural": decomposition.structural,
                "semantic": decomposition.semantic,
                "ambiguity": decomposition.ambiguity
            }
        )

        return {
            "loss": loss,
            "decomposition": {
                "structural": decomposition.structural,
                "semantic": decomposition.semantic,
                "ambiguity": decomposition.ambiguity
            },
            "explanation": decomposition.explanation,
            "suggestions": decomposition.suggestions,
            "mark_id": mark.id
        }

    async def provide_feedback(
        self,
        take_evaluation: dict,
        artist_reaction: str
    ) -> dict:
        """Provide feedback via dialectical fusion."""
        # Coach's technical view
        coach_view = f"Technical assessment: {take_evaluation['explanation']}"
        coach_reasoning = f"Loss analysis suggests: {take_evaluation['suggestions']}"

        # Artist's emotional view
        artist_view = artist_reaction
        artist_reasoning = "Artist's lived experience of the take"

        # Fuse
        fusion = await self.trust.propose_fusion(
            topic="take_feedback",
            kent_view=artist_view,  # Artist is "Kent" (human agency)
            kent_reasoning=artist_reasoning,
            claude_view=coach_view,  # Coach is "Claude" (AI assistance)
            claude_reasoning=coach_reasoning
        )

        return {
            "feedback": fusion.synthesis.content if fusion.synthesis else fusion.reasoning,
            "fusion_result": fusion.result.value,
            "trust_delta": fusion.trust_delta
        }

    async def session_crystal(self) -> Crystal:
        """Generate session crystal."""
        trace = await self.witness.get_trace(session=True)

        # Compute voice continuity (through-line)
        through_line = await self._compute_through_line(trace)

        crystal = await self.witness.crystallize(
            trace,
            compression_ratio=0.1,
            preserve_rationale=True
        )

        crystal.metadata["through_line"] = through_line
        return crystal

    async def _compute_through_line(self, trace: Trace) -> str:
        """Compute the through-line of the session."""
        # Use LLM to identify consistent elements
        marks_summary = "\n".join([
            f"Take: {m.action} (loss: {m.metadata.get('loss', 'N/A')})"
            for m in trace.marks
        ])

        return await self.llm.complete(f"""
Given these takes from a rap session:
{marks_summary}

What is the through-line? What stayed consistent?
What evolved? What was the artistic journey?
""")
```

### Exit Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Loss decomposition works | WHY shown | Actionable |
| Feedback is dialectical | Fusion occurs | Yes |
| Session crystal generated | Through-line | Readable |
| Courage preserved | High-risk takes | Not penalized |

---

## Pilot 5: sprite-procedural-taste-lab

### Theory Validation

**Chapters Validated**: 8 (Fixed Points), 11 (Meta-DP), 6 (Modularization)

| Claim | From Chapter | How Pilot Validates |
|-------|--------------|---------------------|
| Fixed points yield stable structure | Ch 8 | Style attractors converge |
| Meta-DP enables self-improvement | Ch 11 | Sprite evolution improves |
| Modularization is lossy | Ch 6 | Style loss tracked |

### Proposals Validated

| Proposal | Description | Validation Method |
|----------|-------------|-------------------|
| G4 | Polynomial Extractor | Style spec yields polynomial |
| D5 | SelfImprovementCycle | Sprites improve over epochs |
| G1 | Calibration Pipeline | Style descriptions calibrate loss |

### Implementation Requirements

```python
# Core components for sprite-procedural

class SpriteProceduralTasteLab:
    """Sprite procedural taste lab with fixed point detection."""

    def __init__(
        self,
        galois: GaloisLossComputer,
        polynomial: PolynomialExtractor,
        improvement: SelfImprovementCycle,
        witness: WitnessService
    ):
        self.galois = galois
        self.polynomial = polynomial
        self.improvement = improvement
        self.witness = witness

    async def initialize_style(self, style_description: str) -> dict:
        """Initialize a style and extract its polynomial structure."""
        # Compute initial loss
        loss = await self.galois.compute(style_description)

        # Check if it's a fixed point
        is_fixed = loss < 0.05

        result = {"style": style_description, "initial_loss": loss, "is_fixed": is_fixed}

        if is_fixed:
            # Extract polynomial structure
            poly = await self.polynomial.extract(style_description)
            result["polynomial"] = poly.to_polyagent_config()

        await self.witness.mark(
            action="style_initialized",
            reasoning=f"Loss: {loss:.3f}, Fixed point: {is_fixed}",
            metadata=result
        )

        return result

    async def evolve_style(
        self,
        current_style: str,
        mutations: list[str]
    ) -> dict:
        """Evolve style through mutations."""
        current_loss = await self.galois.compute(current_style)

        # Evaluate each mutation
        mutation_results = []
        for mutation in mutations:
            new_style = f"{current_style} + {mutation}"
            new_loss = await self.galois.compute(new_style)

            mutation_results.append({
                "mutation": mutation,
                "loss": new_loss,
                "delta": new_loss - current_loss,
                "improves": new_loss < current_loss
            })

        # Select best mutation (lowest loss)
        best = min(mutation_results, key=lambda m: m["loss"])

        await self.witness.mark(
            action="style_evolved",
            reasoning=f"Selected mutation: {best['mutation']} (loss delta: {best['delta']:.3f})",
            metadata={
                "mutations_evaluated": len(mutations),
                "best_mutation": best["mutation"],
                "loss_before": current_loss,
                "loss_after": best["loss"]
            }
        )

        return {
            "evolved_style": f"{current_style} + {best['mutation']}",
            "loss": best["loss"],
            "mutation_applied": best["mutation"],
            "all_mutations": mutation_results
        }

    async def detect_style_attractor(
        self,
        evolution_history: list[dict]
    ) -> dict:
        """Detect if style has reached an attractor (fixed point)."""
        if len(evolution_history) < 5:
            return {"attractor_detected": False}

        # Check if loss has converged
        recent_losses = [h["loss"] for h in evolution_history[-5:]]
        loss_variance = sum(
            (l - sum(recent_losses)/len(recent_losses))**2
            for l in recent_losses
        ) / len(recent_losses)

        # Attractor if variance is low and loss is low
        avg_loss = sum(recent_losses) / len(recent_losses)
        is_attractor = loss_variance < 0.001 and avg_loss < 0.1

        return {
            "attractor_detected": is_attractor,
            "avg_loss": avg_loss,
            "loss_variance": loss_variance,
            "is_fixed_point": avg_loss < 0.05
        }

    async def epoch_crystal(self, epoch: int) -> Crystal:
        """Generate epoch crystal summarizing style evolution."""
        trace = await self.witness.get_trace(epoch=epoch)

        crystal = await self.witness.crystallize(
            trace,
            compression_ratio=0.1,
            preserve_rationale=True
        )

        # Add style evolution summary
        crystal.metadata["style_journey"] = await self._summarize_journey(trace)
        return crystal

    async def _summarize_journey(self, trace: Trace) -> str:
        """Summarize the style evolution journey."""
        return await self.llm.complete(f"""
Given this style evolution trace:
{trace.summary()}

Describe:
1. Where the style started
2. What mutations were tried
3. What the style converged to
4. Why this attractor is stable
""")
```

### Exit Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Fixed point detection | L < 0.05 | Works |
| Style evolution | Loss decreases | Over epochs |
| Attractor convergence | Variance → 0 | Yes |
| Epoch crystal | Journey summarized | Readable |

---

## Pilot Sequencing

```
Week 6: trail-to-crystal (FIRST - WEDGE)
        Validates: D1, E1, D3
        |
Week 7: wasm-survivors OR rap-coach
        Validates: G1-G3, M2 OR G3, E1, E5
        |
Week 8: disney-portal
        Validates: M1, C4, E3
        |
Week 9: sprite-procedural (if time)
        Validates: G4, D5, G1

Week 10: zero-seed-governance + categorical-foundation
         (Additional pilots from execution roadmap)
```

---

## Cross-Pilot Dependencies

```
                        ┌─────────────────────────────────────────────────────────┐
                        │           COMPLETED FOUNDATION (2025-12-26)             │
                        │                                                         │
                        │  E1: Kleisli Witness Composition ──────── ALL PILOTS    │
                        │      services/witness/kleisli.py                        │
                        │                                                         │
                        │  E3: Dialectical Fusion Service ──────── disney, rap    │
                        │      services/dialectic/fusion.py                       │
                        │                                                         │
                        │  E5: Trust Gradient (exists) ─────────── rap-coach      │
                        │      services/witness/trust/gradient.py                 │
                        └─────────────────────────────────────────────────────────┘
                                              │
                                              ▼
trail-to-crystal ─────────────────────────────────────────────────────────────────
    │  E1: ✓ DONE                    │              │              │
    │  D1: MAIN REMAINING            │              │              │
    │                                │              │              │
    ├── WITNESS SPINE (E1) ──────────┼──────────────┼──────────────┤
    │                                │              │              │
    ▼                                ▼              ▼              ▼
wasm-survivors                disney-portal    rap-coach     sprite-lab
    │                              │              │              │
    │ E1: ✓ DONE                   │ E1: ✓ DONE   │ E1: ✓ DONE   │ E1: ✓ DONE
    │ G1-G2: pending               │ E3: ✓ DONE   │ E5: EXISTS   │ G4: pending
    │ M2: pending                  │ M1: uses E3  │ G3: pending  │ D5: pending
    │                              │              │              │
    └── GALOIS LOSS ───────────────┴──────────────┴──────────────┘
                                   │
                          MULTI-AGENT SHEAF (builds on E3)
```

**Key Insights**:
1. **E1 is universal**: Kleisli composition is used by ALL pilots
2. **E3 enables M1**: MultiAgentSheaf can build on DialecticalFusionService
3. **Trust gradient exists**: rap-coach can use gradient.py immediately
4. **D1 is the wedge**: trail-to-crystal's main blocker is BellmanConstitutionalEquation

---

## Pilot Composition Operad (Gap 5 Fix)

> *"The pilot IS the validation. The interface IS AGENTESE. The composition IS morphisms."*

**Problem**: Pilots are isolated towers. No morphism semantics between them. Each pilot validates theory claims in isolation, but there's no defined way for pilots to compose, share state, or chain outputs.

**Solution**: AGENTESE Path as Universal Interface

### Design Decision (Kent 2025-12-26)

- Pilot interface = AGENTESE Path
- Output = AGENTESE node. Input = invoke(). Protocol-native.
- Laws are operad operations; pilots are algebras

This aligns with the Metaphysical Fullstack (AD-009): AGENTESE IS the API.

### The Interface Contract

Every pilot exposes two AGENTESE nodes:

```python
@node("pilots.{pilot_name}.output")
class PilotOutputNode:
    """Universal output interface for pilot composition.

    Returns the pilot's output as a witnessed trace that can be
    consumed by any downstream pilot.
    """

    def __init__(self, pilot: PilotService, witness: WitnessService):
        self.pilot = pilot
        self.witness = witness

    async def invoke(self, observer: Observer) -> WitnessedTrace:
        """Returns the pilot's output as witnessed trace."""
        trace = await self.pilot.get_output_trace()

        # Mark the output emission
        await self.witness.mark(
            action="pilot_output_emitted",
            reasoning=f"Pilot {self.pilot.name} emitting trace for composition",
            metadata={
                "pilot": self.pilot.name,
                "trace_length": len(trace.marks),
                "observer": observer.id
            }
        )

        return trace


@node("pilots.{pilot_name}.input")
class PilotInputNode:
    """Universal input interface for pilot composition.

    Accepts a witnessed trace as input seed, enabling composition
    from upstream pilots.
    """

    def __init__(self, pilot: PilotService, witness: WitnessService):
        self.pilot = pilot
        self.witness = witness

    async def invoke(self, observer: Observer, trace: WitnessedTrace) -> None:
        """Accepts a witnessed trace as input seed."""
        await self.pilot.seed_from_trace(trace)

        # Mark the input reception
        await self.witness.mark(
            action="pilot_input_seeded",
            reasoning=f"Pilot {self.pilot.name} seeded from upstream trace",
            metadata={
                "pilot": self.pilot.name,
                "source_trace_length": len(trace.marks),
                "observer": observer.id
            }
        )
```

### Composition via AGENTESE

```python
# trail-to-crystal outputs crystal
crystal_trace = await logos.invoke("pilots.trail_to_crystal.output", observer)

# sprite-lab accepts crystal as style seed
await logos.invoke("pilots.sprite_lab.input", observer, trace=crystal_trace)

# Composition is just AGENTESE path chaining
composed = await logos.invoke(
    "pilots.trail_to_crystal.output >> pilots.sprite_lab.input",
    observer
)
```

### PILOT_OPERAD Definition

```python
from agents.operad import Operad, Operation, Law

PILOT_OPERAD = Operad(
    name="PilotOperad",

    # Operations define how pilots compose
    operations={
        # Sequential composition: output of A feeds input of B
        "seq": Operation(
            arity=2,
            signature="Pilot × Pilot → Pilot",
            semantics="(A >> B)(x) = B(A(x))"
        ),

        # Parallel composition: both pilots receive same input
        "par": Operation(
            arity=2,
            signature="Pilot × Pilot → Pilot",
            semantics="(A | B)(x) = (A(x), B(x))"
        ),

        # Gated composition: B runs only if predicate P holds
        "gate": Operation(
            arity=2,
            signature="Predicate × Pilot → Pilot",
            semantics="(P ? B)(x) = B(x) if P(x) else id(x)"
        ),
    },

    laws=[
        # Traces accumulate correctly through composition
        Law(
            name="trace_coherence",
            formula="output(A >> B) = output(B).extend(output(A))",
            meaning="Sequential composition extends traces"
        ),

        # Composition is associative
        Law(
            name="associativity",
            formula="(A >> B) >> C = A >> (B >> C)",
            meaning="Grouping doesn't affect result"
        ),

        # Identity pilot exists (passes through unchanged)
        Law(
            name="identity",
            formula="id >> A = A = A >> id",
            meaning="Identity is neutral element"
        ),

        # Parallel composition is symmetric
        Law(
            name="parallel_symmetry",
            formula="A | B = B | A (up to reordering)",
            meaning="Parallel order doesn't matter"
        ),
    ]
)
```

### Pilot Algebras

Each pilot is an algebra for `PILOT_OPERAD`:

```python
from dataclasses import dataclass
from typing import Set


@dataclass
class PilotAlgebra:
    """A pilot as an algebra for the PILOT_OPERAD."""

    pilot: str                           # Pilot name
    input_path: str                      # AGENTESE input path
    output_path: str                     # AGENTESE output path
    laws_satisfied: Set[str]             # LAW_OPERAD laws satisfied
    amendments_grounded: Set[str]        # Zero Seed amendments (A-G)


# Concrete pilot algebras
trail_to_crystal_algebra = PilotAlgebra(
    pilot="trail_to_crystal",
    input_path="pilots.trail_to_crystal.input",
    output_path="pilots.trail_to_crystal.output",
    laws_satisfied={
        "COHERENCE_GATE",      # Output only if witnessed
        "COMPRESSION_HONESTY", # Crystal discloses drops
        "DRIFT_ALERT",         # Constitutional drift surfaced
    },
    amendments_grounded={"A1", "D1", "F1"}
)

wasm_survivors_algebra = PilotAlgebra(
    pilot="wasm_survivors",
    input_path="pilots.wasm_survivors.input",
    output_path="pilots.wasm_survivors.output",
    laws_satisfied={
        "COHERENCE_GATE",
        "DRIFT_ALERT",         # Build drift detected
        "GHOST_PRESERVATION",  # Unchosen builds inspectable
    },
    amendments_grounded={"B1", "G1", "F1"}
)

disney_portal_algebra = PilotAlgebra(
    pilot="disney_portal",
    input_path="pilots.disney_portal.input",
    output_path="pilots.disney_portal.output",
    laws_satisfied={
        "COHERENCE_GATE",
        "COMPRESSION_HONESTY",
        "COURAGE_PRESERVATION", # Bold trip choices protected
    },
    amendments_grounded={"C1", "E3", "F1"}
)

rap_coach_algebra = PilotAlgebra(
    pilot="rap_coach",
    input_path="pilots.rap_coach.input",
    output_path="pilots.rap_coach.output",
    laws_satisfied={
        "COHERENCE_GATE",
        "COURAGE_PRESERVATION", # High-risk takes not penalized
        "COMPRESSION_HONESTY",
    },
    amendments_grounded={"E5", "F1", "G3"}
)

sprite_lab_algebra = PilotAlgebra(
    pilot="sprite_lab",
    input_path="pilots.sprite_lab.input",
    output_path="pilots.sprite_lab.output",
    laws_satisfied={
        "COHERENCE_GATE",
        "COMPRESSION_HONESTY",
        "GHOST_PRESERVATION",  # Unchosen mutations inspectable
    },
    amendments_grounded={"B1", "D5", "G4"}
)
```

### LAW_OPERAD: The Five Pilot Law Schemas

The 5 pilot law schemas from the theory ARE operad operations:

```python
LAW_OPERAD = Operad(
    name="LawOperad",

    operations={
        # Only emit X if Y is witnessed
        "coherence_gate": LawOp(
            schema="X valid only if Y marked",
            example="Crystal valid only if trace marked",
            universal=True  # ALL pilots must satisfy
        ),

        # Surface when loss exceeds threshold
        "drift_alert": LawOp(
            schema="loss > threshold → surface to user",
            example="Build drift > 0.1 → alert",
            universal=False
        ),

        # Unchosen paths remain inspectable
        "ghost_preservation": LawOp(
            schema="unchosen paths remain inspectable",
            example="Rejected mutations can be reviewed",
            universal=False
        ),

        # High-risk courageous acts are protected
        "courage_preservation": LawOp(
            schema="high-risk acts protected from penalty",
            example="Bold take not penalized in scoring",
            universal=False
        ),

        # Crystal discloses what was dropped
        "compression_honesty": LawOp(
            schema="crystal discloses drops",
            example="Crystal metadata shows compression ratio",
            universal=True  # ALL pilots must satisfy
        ),
    }
)

# Universal guarantee: ALL pilots satisfy COHERENCE_GATE + COMPRESSION_HONESTY
UNIVERSAL_LAWS = {"COHERENCE_GATE", "COMPRESSION_HONESTY"}

def validate_pilot_algebra(algebra: PilotAlgebra) -> bool:
    """Validate that a pilot satisfies universal laws."""
    return UNIVERSAL_LAWS.issubset(algebra.laws_satisfied)
```

### Composition Examples

**Example 1: trail-to-crystal → sprite-lab**

```python
# Daily crystal seeds sprite style
async def trail_to_sprite_composition(observer: Observer):
    """Compose trail-to-crystal output into sprite-lab input."""

    # Get daily crystal from trail-to-crystal
    crystal_trace = await logos.invoke(
        "pilots.trail_to_crystal.output",
        observer
    )

    # Seed sprite-lab with crystal aesthetic
    await logos.invoke(
        "pilots.sprite_lab.input",
        observer,
        trace=crystal_trace
    )

    # Sprite generation is now influenced by daily aesthetic
    sprite = await logos.invoke(
        "pilots.sprite_lab.generate",
        observer,
        style_seed="from_crystal"
    )

    return sprite
```

**Example 2: rap-coach → trail-to-crystal**

```python
# Rap session flows into daily reflection
async def session_to_daily_composition(observer: Observer):
    """Compose rap session into daily lab."""

    # Get session trace
    session_trace = await logos.invoke(
        "pilots.rap_coach.output",
        observer
    )

    # Seed daily lab with session
    await logos.invoke(
        "pilots.trail_to_crystal.input",
        observer,
        trace=session_trace
    )

    # Daily crystal now includes session
    return await logos.invoke(
        "pilots.trail_to_crystal.crystallize",
        observer
    )
```

### Zero Seed Grounding

| Axiom | Application in Composition |
|-------|---------------------------|
| **A2** (Morphism) | Pilots ARE morphisms via AGENTESE paths |
| **Ch. 19** (kgents) | Crown Jewels as categorical instantiation |
| **AGENTESE** | Universal interface for all composition |
| **F1** (Witness) | Composition traces are witnessed |

### Implementation Checklist

| Task | Status | Notes |
|------|--------|-------|
| Define `PilotOutputNode` base class | Pending | In `services/pilots/base.py` |
| Define `PilotInputNode` base class | Pending | In `services/pilots/base.py` |
| Register AGENTESE paths for each pilot | Pending | `@node` decorators |
| Implement `PILOT_OPERAD` | Pending | In `agents/operad/pilot_operad.py` |
| Implement `LAW_OPERAD` | Pending | In `agents/operad/law_operad.py` |
| Property tests for operad laws | Pending | In `tests/property/` |
| Integration test: trail → sprite | Pending | First composition test |

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Pilots have input/output AGENTESE nodes | Path discovery | 5 pilots × 2 paths |
| Composition uses `>>` operator | Path chaining | Works syntactically |
| PILOT_OPERAD defined | Module exists | Laws stated |
| LAW_OPERAD defined | Module exists | 5 schemas |
| Trace coherence law holds | Property test | > 95% pass |
| Universal laws validated | All pilots | 100% satisfy |

---

## Analysis Operad: Pilot Readiness Assessment

> *"Four modes of analysis, rigorously composed."*

Applying the Analysis Operad (Ch 15) to assess pilot readiness:

### Categorical Analysis: Law Validation

| Pilot | Laws Validated | Confidence |
|-------|----------------|------------|
| **trail-to-crystal** | Writer monad laws (E1), Identity/Composition | HIGH (E1 tested) |
| **wasm-survivors** | Galois connection adjointness | MEDIUM (pending G1-G2) |
| **disney-portal** | Sheaf gluing laws, Cocone universality | HIGH (E3 tested) |
| **rap-coach** | Trust polynomial functor laws | MEDIUM (E5 exists) |
| **sprite-procedural** | Fixed point existence (Banach) | LOW (pending) |

### Epistemic Analysis: Theory Validation Confidence

| Pilot | Theory Chapters | Validation Confidence | Risk |
|-------|-----------------|----------------------|------|
| **trail-to-crystal** | 9, 16, 11 | **HIGH** | D1 may require iteration |
| **wasm-survivors** | 7, 13, 10 | MEDIUM | Galois correlation unvalidated |
| **disney-portal** | 5, 12, 17 | **HIGH** | E3 provides strong foundation |
| **rap-coach** | 7, 16, 17 | **HIGH** | E1+E5 nearly complete |
| **sprite-procedural** | 8, 11, 6 | LOW | Most theoretical gaps |

### Dialectical Analysis: Scope Tensions

| Tension | Thesis | Antithesis | Synthesis |
|---------|--------|------------|-----------|
| Pilot scope vs theory scope | Pilots are minimal | Theory is comprehensive | Pilots validate specific claims |
| Implementation speed vs rigor | Ship fast | Verify laws | E1/E3 prove laws can be tested |
| User experience vs theory | Joy first | Correctness first | Constitution balances both |

### Generative Analysis: Theory-to-Pilot Regeneration

Can pilots be regenerated from theory chapters alone?

| Pilot | Primary Chapter | Regeneration Feasibility |
|-------|-----------------|--------------------------|
| **trail-to-crystal** | Ch 16 (Witness) | **HIGH** — Ch 16 defines Mark→Trace→Crystal |
| **wasm-survivors** | Ch 7 (Galois Loss) | MEDIUM — needs domain-specific mapping |
| **disney-portal** | Ch 17 (Dialectic) | **HIGH** — Ch 17 defines fusion |
| **rap-coach** | Ch 17 + Ch 16 | **HIGH** — combines witness + dialectic |
| **sprite-procedural** | Ch 8 (Fixed Points) | LOW — domain-specific interpretation needed |

---

## Zero Seed: Pilot Grounding in Amendments

> *"Trace every pilot back to axioms."*

Each pilot must demonstrate grounding in specific amendments (A-G) from the theoretical framework.

### Amendment Mapping

| Amendment | Description | Pilots Validating |
|-----------|-------------|-------------------|
| **A** | Constitution as Category | ALL (7 principles scored) |
| **B** | Polynomial Agency | wasm-survivors, sprite-lab |
| **C** | Sheaf Coherence | disney-portal |
| **D** | Dynamic Programming | trail-to-crystal (D1), sprite-lab (D5) |
| **E** | Trust Asymmetry | rap-coach (E5) |
| **F** | Witness Protocol | ALL (E1 composition) |
| **G** | Galois Modularization | wasm-survivors, rap-coach, sprite-lab |

### Axiom Validation by Pilot

**Pilot 1: trail-to-crystal**
- **A1**: Constitutional scoring of daily actions
- **D1**: Bellman equation optimizes for constitutional reward
- **F1**: Marks compose via Kleisli (E1 DONE)

**Pilot 2: wasm-survivors**
- **B1**: Polynomial state machine for game phases
- **G1**: Galois loss predicts build drift
- **F1**: All decisions witnessed

**Pilot 3: disney-portal**
- **C1**: Sheaf gluing for family preferences
- **E3**: Dialectical fusion for conflicts (DONE)
- **F1**: Trip planning witnessed

**Pilot 4: rap-coach**
- **E5**: Trust gradient for coach autonomy
- **F1**: Session composition via E1 (DONE)
- **G3**: Loss decomposition for feedback

**Pilot 5: sprite-procedural**
- **B1**: Polynomial functor for style evolution
- **D5**: Self-improvement cycle
- **G4**: Fixed points as style attractors

### Axiom Witness Requirement

Every pilot MUST:
1. **Trace to Amendment**: Link implementation to specific amendment (A-G)
2. **Witness Axiom Application**: Create marks when axioms are applied
3. **Validate Laws**: Property tests for categorical laws
4. **Report Coverage**: Which axioms are tested vs assumed

---

## Success Metrics (Cross-Pilot)

| Metric | Source | Target |
|--------|--------|--------|
| First pilot ships | trail-to-crystal | Week 6 |
| Three pilots demo-ready | Any combination | Week 8 |
| Galois correlation validated | wasm + rap-coach | r > 0.5 |
| Sheaf gluing works | disney-portal | Consensus formed |
| Fixed points detected | sprite-lab | L < 0.05 converges |
| **E1 coverage** | ALL pilots | 100% (ACHIEVED) |
| **E3 coverage** | disney, rap | 100% (ACHIEVED) |
| Amendment grounding | ALL pilots | Traced to A-G |

---

## Axiom Witness Protocol: Self-Aware Discovery (Invention)

> *"Axioms are not stipulated but discovered. They are the fixed points of your decision landscape."*

**Problem**: Zero Seed axioms are stipulated in docs, not discovered from evidence.

**Solution**: Witness marks capture axiom instantiation; crystals surface candidates quietly.

**Design Decision (Kent)**:
- Axiom candidates accumulate **QUIETLY** (no active notifications)
- Surface in daily crystal as part of reflection
- System is **self-aware by construction**
- Users need **onboarding to proficiency**

### The Discovery Mechanism

**Definition**: An axiom candidate is a proposition with Galois loss < 0.05 (fixed point).

The core data structure extends the existing `DiscoveredAxiom` from `services/zero_seed/axiom_discovery.py`:

```python
@dataclass
class AxiomCandidate:
    """A proposition that might be an axiom.

    Extends the existing DiscoveredAxiom pattern from axiom_discovery.py
    with amendment tracking and evidence counting.

    Location: services/zero_seed/axiom_discovery.py (extension)
    """
    proposition: str
    amendment: str  # Which amendment (A-G) it relates to
    galois_loss: float  # < 0.05 = strong candidate
    evidence_count: int  # How many times instantiated
    first_seen: datetime
    source_mark_ids: tuple[str, ...]  # Marks that evidence this axiom

    @property
    def is_strong_candidate(self) -> bool:
        """True if loss is low AND we have enough evidence."""
        return self.galois_loss < 0.05 and self.evidence_count >= 3

    @property
    def status_symbol(self) -> str:
        """Visual indicator for crystal display."""
        if self.is_strong_candidate:
            return "✓ STRONG"
        elif self.galois_loss < 0.10:
            return "○ emerging"
        else:
            return "· potential"
```

### Witness Mark for Axiom Instantiation

When pilots instantiate axioms in practice, they create witness marks:

```python
async def mark_axiom_instantiation(
    witness: WitnessService,
    amendment: str,
    instance: str,
    galois_loss: float,
    context: str = "",
) -> Mark:
    """Mark when an axiom is instantiated in practice.

    This creates an observable trace of axiom application.
    The accumulator silently collects these for crystal surfacing.

    Args:
        witness: The witness service
        amendment: Which amendment (A-G) was instantiated
        instance: Description of how it was instantiated
        galois_loss: Measured Galois loss for this instantiation
        context: Additional context (optional)

    Returns:
        The created mark

    Example:
        await mark_axiom_instantiation(
            witness=self.witness,
            amendment="A",  # Constitution as Category
            instance="trail-to-crystal constitutional scoring",
            galois_loss=0.03
        )
    """
    return await witness.mark(
        action="axiom_instantiated",
        reasoning=f"Amendment {amendment} instantiated via {instance}",
        principles=["generative"],  # Axioms ground the generative principle
        metadata={
            "amendment": amendment,
            "instance": instance,
            "galois_loss": galois_loss,
            "is_axiom_candidate": galois_loss < 0.05,
            "context": context,
        }
    )

# Usage in trail-to-crystal pilot
async def _score_action_constitutionally(self, action: str) -> dict:
    """Score an action against constitution (validates Amendment A)."""
    scores = await self.constitution.check(action)

    # This IS an axiom instantiation - mark it silently
    if scores.weighted_total > 0.8:
        await mark_axiom_instantiation(
            witness=self.witness,
            amendment="A",  # Constitution as Category
            instance="action constitutional scoring",
            galois_loss=0.03,  # High-quality score = low loss
            context=f"Action: {action[:50]}..."
        )

    return scores
```

### Quiet Accumulation + Crystal Surfacing

**Quiet Phase**: Axiom marks accumulate silently in the witness store. No notifications, no interruptions.

```python
class AxiomAccumulator:
    """Silently accumulates axiom evidence from witness marks.

    This runs in the background, observing marks without
    notifying the user. Evidence surfaces only in crystals.

    Philosophy: "Quiet observation, thoughtful surfacing."

    Location: services/zero_seed/axiom_accumulator.py (new)
    """

    def __init__(self, mark_store: MarkStore):
        self._store = mark_store
        self._candidates: dict[str, AxiomCandidate] = {}

    async def accumulate(self, mark: Mark) -> None:
        """Add mark to axiom evidence if relevant.

        Called automatically when marks are created.
        No user-facing effects - purely observational.
        """
        if not mark.metadata.get("is_axiom_candidate"):
            return

        amendment = mark.metadata.get("amendment", "?")
        proposition = mark.metadata.get("instance", "")
        loss = mark.metadata.get("galois_loss", 1.0)

        key = f"{amendment}:{proposition}"

        if key in self._candidates:
            # Update existing candidate
            existing = self._candidates[key]
            # Running average of loss
            new_count = existing.evidence_count + 1
            new_loss = (
                (existing.galois_loss * existing.evidence_count + loss)
                / new_count
            )
            self._candidates[key] = AxiomCandidate(
                proposition=existing.proposition,
                amendment=amendment,
                galois_loss=new_loss,
                evidence_count=new_count,
                first_seen=existing.first_seen,
                source_mark_ids=existing.source_mark_ids + (str(mark.id),),
            )
        else:
            # New candidate
            self._candidates[key] = AxiomCandidate(
                proposition=proposition,
                amendment=amendment,
                galois_loss=loss,
                evidence_count=1,
                first_seen=mark.timestamp,
                source_mark_ids=(str(mark.id),),
            )

    async def get_candidates(self) -> list[AxiomCandidate]:
        """Get all current axiom candidates, sorted by strength."""
        return sorted(
            self._candidates.values(),
            key=lambda c: (not c.is_strong_candidate, c.galois_loss),
        )

    async def get_strong_candidates(self) -> list[AxiomCandidate]:
        """Get only strong axiom candidates (L < 0.05, n >= 3)."""
        return [c for c in self._candidates.values() if c.is_strong_candidate]
```

**Crystal Surfacing**: Daily crystal includes axiom discovery section.

```python
@dataclass
class DailyCrystalWithAxioms(DailyCrystal):
    """Extended daily crystal with axiom discoveries.

    Extends the existing DailyCrystal from daily_lab.py
    to include axiom discovery surfacing.

    Location: services/witness/daily_lab.py (extension)
    """
    axiom_discoveries: list[AxiomCandidate] = field(default_factory=list)
    onboarding_phase: int = 1  # 1 = verbose, 2 = condensed

    def _format_axiom_section(self) -> str:
        """Format axiom discoveries for crystal.

        Adapts based on onboarding phase:
        - Phase 1 (Week 1-2): Verbose with explanation
        - Phase 2 (Week 3+): Condensed format
        """
        if not self.axiom_discoveries:
            return ""

        if self.onboarding_phase == 1:
            return self._format_verbose()
        else:
            return self._format_condensed()

    def _format_verbose(self) -> str:
        """Verbose format for new users (Phase 1)."""
        lines = [
            "## Axiom Discoveries",
            "",
            "*What are these? kgents discovers foundational truths through use.*",
            "*When a pattern shows Galois loss < 0.05, it's nearly 'round-trip stable' —*",
            "*meaning the LLM understands it so well that restructure → reconstitute*",
            "*produces the same result. These are axiom candidates.*",
            "",
        ]

        for candidate in self.axiom_discoveries:
            lines.append(
                f"- [{candidate.status_symbol}] {candidate.amendment}: "
                f"\"{candidate.proposition}\" "
                f"(L={candidate.galois_loss:.3f}, n={candidate.evidence_count})"
            )

            # Add explanation for strong candidates
            if candidate.is_strong_candidate:
                lines.append(
                    f"  *→ This is becoming axiomatic for your workflow.*"
                )

        return "\n".join(lines)

    def _format_condensed(self) -> str:
        """Condensed format for proficient users (Phase 2)."""
        parts = []
        for c in self.axiom_discoveries:
            symbol = "✓" if c.is_strong_candidate else "○"
            parts.append(f"{c.amendment} (L={c.galois_loss:.2f} {symbol})")

        return f"Axioms: {', '.join(parts)}"
```

### User Onboarding for Axiom Awareness

The system teaches users about axioms through use, not documentation.

**Phase 1 (Week 1-2)**: System explains axiom candidates in crystal with full context.

```
## Axiom Discoveries

*What are these? kgents discovers foundational truths through use.*
*When a pattern shows Galois loss < 0.05, it's nearly 'round-trip stable' —*
*meaning the LLM understands it so well that restructure → reconstitute*
*produces the same result. These are axiom candidates.*

- [✓ STRONG] A: "Constitution scores are meaningful" (L=0.03, n=7)
  *→ This is becoming axiomatic for your workflow.*
- [○ emerging] E: "Trust gradient guides autonomy" (L=0.08, n=2)
```

**Phase 2 (Week 3+)**: Condensed format, assumes understanding.

```
Axioms: A (L=0.03 ✓), E (L=0.08 ○)
```

### Integration with Existing Infrastructure

**Existing Services Used**:
- `services/zero_seed/axiom_discovery.py` → `DiscoveredAxiom`, `AxiomDiscoveryService`
- `services/zero_seed/galois/galois_loss.py` → `GaloisLossComputer`
- `services/zero_seed/galois/fixed_point.py` → `detect_fixed_point`
- `services/witness/daily_lab.py` → `DailyCrystal`, `DailyCrystallizer`
- `services/witness/crystal.py` → `Crystal`, `ConstitutionalCrystalMeta`

**New Components**:
- `AxiomCandidate` → Extension of `DiscoveredAxiom` with amendment tracking
- `AxiomAccumulator` → Background accumulation from witness marks
- `mark_axiom_instantiation()` → Convenience function for pilots
- `DailyCrystalWithAxioms` → Extended crystal with axiom surfacing

### Zero Seed Grounding

| Component | Theory Source | Validation |
|-----------|---------------|------------|
| Fixed points as axioms | Ch. 8 (Polynomial Bootstrap) | L < 0.05 threshold |
| Witness marks | Ch. 16 / A4 (Witness) | Marks capture evidence |
| Crystal surfacing | Ch. 16 (Witness) | Reflection mechanism |
| Quiet accumulation | Kent's design decision | Non-intrusive discovery |
| Onboarding phases | Kent's design decision | Progressive revelation |

### Amendment Traceability

Each axiom candidate traces to a specific amendment:

| Amendment | What It Validates | Example Instance |
|-----------|-------------------|------------------|
| **A** | Constitution as Category | Constitutional scoring is meaningful |
| **B** | Polynomial Agency | State machines capture agent behavior |
| **C** | Sheaf Coherence | Local preferences glue to global plan |
| **D** | Dynamic Programming | Bellman equation optimizes decisions |
| **E** | Trust Asymmetry | Trust gradient guides autonomy |
| **F** | Witness Protocol | Marks compose via Kleisli |
| **G** | Galois Modularization | Loss predicts comprehension drift |

### Benefits

1. **Self-aware by construction** — System knows its own foundations through observation
2. **Evidence-based axioms** — Not stipulated, discovered from actual use
3. **Non-intrusive** — Quiet accumulation, crystal surfacing (Kent's design)
4. **Onboarding path** — Users learn what axioms mean through progressive revelation
5. **Traceable to theory** — Every axiom links to specific amendments (A-G)

### Exit Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| AxiomCandidate dataclass defined | Code exists | Specified |
| Witness mark for axiom instantiation | Function exists | Specified |
| Quiet accumulator implemented | AxiomAccumulator class | Specified |
| Crystal integration | axiom_discoveries in crystal | Specified |
| Onboarding phases | Phase 1 → Phase 2 transition | After 2 weeks |
| Amendment traceability | Each candidate links to A-G | 100% traced |

---

**Document Metadata**
- **Lines**: ~1200
- **Pilots**: 5
- **Theory Chapters**: All
- **Foundation Services**: E1 (DONE), E3 (DONE), E5 (EXISTS)
- **Axiom Witness Protocol**: Invention (specified)
- **Status**: Ready for execution with solid foundation
