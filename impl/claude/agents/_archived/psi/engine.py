"""
Psi-gent v3.0 Morphic Engine.

Six-stage pipeline with backtracking:
RETRIEVE -> PROJECT -> CHALLENGE -> SOLVE -> TRANSLATE -> VERIFY
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable
from uuid import uuid4

from .corpus import MetaphorCorpus, create_standard_corpus
from .learning import (
    AbstractionModel,
    ThompsonSamplingModel,
    cold_start_retrieval,
    extract_features,
    retrieve_with_learning,
)
from .types import (
    ChallengeResult,
    ConceptMapping,
    Distortion,
    EngineConfig,
    Feedback,
    Metaphor,
    MetaphorSolution,
    Operation,
    Outcome,
    Problem,
    Projection,
    SearchState,
    Solution,
)

# =============================================================================
# LLM Interface (Pluggable)
# =============================================================================


LLMCall = Callable[[str, int | None], str]


def _default_llm_call(prompt: str, max_tokens: int | None = None) -> str:
    """Default LLM call - returns placeholder. Override in production."""
    return f"[LLM response to: {prompt[:100]}...]"


# =============================================================================
# Morphic Engine
# =============================================================================


@dataclass
class MetaphorEngine:
    """
    The Morphic Engine: Reasoning by analogy as geometric transformation.

    Six stages:
    1. RETRIEVE: Find candidate metaphors
    2. PROJECT: Map problem into metaphor terms
    3. CHALLENGE: Stress-test the metaphor
    4. SOLVE: Reason within metaphor space
    5. TRANSLATE: Map solution back to problem terms
    6. VERIFY: Measure distortion
    """

    config: EngineConfig = field(default_factory=EngineConfig)
    corpus: MetaphorCorpus = field(default_factory=create_standard_corpus)
    retrieval_model: ThompsonSamplingModel = field(
        default_factory=ThompsonSamplingModel
    )
    abstraction_model: AbstractionModel = field(default_factory=AbstractionModel)

    # LLM interface (injectable)
    llm_call: LLMCall = _default_llm_call

    # Callbacks for integration
    on_stage_complete: Callable[[str, Any], None] | None = None

    # ==========================================================================
    # RETRIEVE Stage
    # ==========================================================================

    def retrieve(
        self,
        problem: Problem,
        limit: int = 5,
        exclude: list[str] | None = None,
        context: str | None = None,
    ) -> list[tuple[Metaphor, float]]:
        """Find candidate metaphors for the problem."""
        exclude = exclude or []
        corpus_list = [m for m in self.corpus if m.id not in exclude]

        if not corpus_list:
            return []

        if self.retrieval_model.is_trained:
            scored = retrieve_with_learning(
                problem, corpus_list, self.retrieval_model, strategy="thompson"
            )
        else:
            scored = cold_start_retrieval(problem, corpus_list)

        # Filter excluded
        scored = [(m, s) for m, s in scored if m.id not in exclude]

        if self.on_stage_complete:
            self.on_stage_complete("retrieve", {"candidates": len(scored)})

        return scored[:limit]

    # ==========================================================================
    # PROJECT Stage
    # ==========================================================================

    def project(
        self,
        problem: Problem,
        metaphor: Metaphor,
        abstraction: float = 0.5,
    ) -> Projection:
        """Map the problem into metaphor terms."""
        # Extract concepts from problem
        concepts = self._extract_concepts(problem)

        # Map concepts to metaphor
        mappings, gaps = self._map_concepts(concepts, metaphor, abstraction)

        # Generate projected description
        mapped_description = self._generate_mapped_description(
            problem, mappings, metaphor
        )

        # Calculate confidence
        if mappings:
            confidence = sum(m.confidence for m in mappings) / len(mappings)
        else:
            confidence = 0.0

        projection = Projection(
            problem=problem,
            metaphor=metaphor,
            mappings=tuple(mappings),
            abstraction=abstraction,
            gaps=tuple(gaps),
            confidence=confidence,
            mapped_description=mapped_description,
        )

        if self.on_stage_complete:
            self.on_stage_complete(
                "project", {"coverage": projection.coverage, "gaps": len(gaps)}
            )

        return projection

    def _extract_concepts(self, problem: Problem) -> list[str]:
        """Extract key concepts from problem description."""
        # Simple extraction: split into words and filter
        # In production, use LLM for semantic extraction
        words = problem.description.lower().replace(".", " ").replace(",", " ").split()
        # Filter common words
        stopwords = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "can",
            "need",
            "to",
            "of",
            "in",
            "for",
            "on",
            "with",
            "at",
            "by",
            "from",
            "as",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "under",
            "again",
            "further",
            "then",
            "once",
            "and",
            "but",
            "or",
            "nor",
            "so",
            "yet",
            "both",
            "either",
            "neither",
            "not",
            "only",
            "own",
            "same",
            "than",
            "too",
            "very",
            "just",
            "it",
            "its",
            "we",
            "they",
            "them",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
        }
        concepts = [w for w in words if w not in stopwords and len(w) > 2]
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for c in concepts:
            if c not in seen:
                seen.add(c)
                unique.append(c)
        return unique[:20]  # Limit to 20 concepts

    def _map_concepts(
        self, concepts: list[str], metaphor: Metaphor, abstraction: float
    ) -> tuple[list[ConceptMapping], list[str]]:
        """Map problem concepts to metaphor concepts."""
        mappings: list[ConceptMapping] = []
        gaps: list[str] = []

        # Build vocabulary from metaphor
        metaphor_vocab = set()
        for word in metaphor.description.lower().split():
            if len(word) > 3:
                metaphor_vocab.add(word)
        for op in metaphor.operations:
            metaphor_vocab.add(op.name.replace("_", " "))
            for word in op.description.lower().split():
                if len(word) > 3:
                    metaphor_vocab.add(word)

        for concept in concepts:
            # Try to find a mapping
            best_match = None
            best_confidence = 0.0

            for vocab_term in metaphor_vocab:
                # Simple similarity: character overlap
                overlap = len(set(concept) & set(vocab_term))
                similarity = overlap / max(len(concept), len(vocab_term))

                # Boost for exact or partial match
                if concept in vocab_term or vocab_term in concept:
                    similarity = max(similarity, 0.7)

                if similarity > best_confidence:
                    best_confidence = similarity
                    best_match = vocab_term

            # Adjust confidence by abstraction level
            # Higher abstraction = more lenient mapping
            threshold = 0.3 * (1 - abstraction) + 0.1

            if best_match and best_confidence > threshold:
                mappings.append(
                    ConceptMapping(
                        source=concept,
                        target=best_match,
                        confidence=min(1.0, best_confidence + abstraction * 0.2),
                        rationale=f"similarity={best_confidence:.2f}",
                    )
                )
            else:
                gaps.append(concept)

        return mappings, gaps

    def _generate_mapped_description(
        self, problem: Problem, mappings: list[ConceptMapping], metaphor: Metaphor
    ) -> str:
        """Generate problem description in metaphor terms."""
        mapping_dict = {m.source: m.target for m in mappings}

        # Simple word replacement
        words = problem.description.split()
        mapped_words = []
        for word in words:
            clean = word.lower().strip(".,!?")
            if clean in mapping_dict:
                mapped_words.append(f"[{mapping_dict[clean]}]")
            else:
                mapped_words.append(word)

        return f"[{metaphor.name}] " + " ".join(mapped_words)

    # ==========================================================================
    # CHALLENGE Stage
    # ==========================================================================

    def challenge(self, projection: Projection) -> ChallengeResult:
        """Stress-test the projection with adversarial cases."""
        results: list[bool] = []
        counterexamples: list[str] = []
        caveats: list[str] = []

        # Challenge 1: Coverage check
        if projection.coverage < 0.5:
            results.append(False)
            counterexamples.append(f"low_coverage: {projection.coverage:.2f}")
        else:
            results.append(True)

        # Challenge 2: Confidence check
        if projection.confidence < 0.4:
            results.append(False)
            counterexamples.append(f"low_confidence: {projection.confidence:.2f}")
        else:
            results.append(True)

        # Challenge 3: Operations applicable
        applicable_ops = self._find_applicable_operations(projection)
        if not applicable_ops:
            results.append(False)
            counterexamples.append("no_applicable_operations")
        else:
            results.append(True)

        # Challenge 4: Gaps are acceptable
        critical_gaps = [
            g for g in projection.gaps if self._is_critical_gap(g, projection)
        ]
        if len(critical_gaps) > len(projection.mappings) // 2:
            results.append(False)
            counterexamples.append(f"critical_gaps: {critical_gaps}")
        else:
            results.append(True)
            if critical_gaps:
                caveats.append(f"minor_gaps: {critical_gaps}")

        passed = sum(results)
        survives = passed >= 3

        challenge_result = ChallengeResult(
            survives=survives,
            challenges_passed=passed,
            challenges_total=len(results),
            counterexamples=tuple(counterexamples),
            caveats=tuple(caveats),
        )

        if self.on_stage_complete:
            self.on_stage_complete(
                "challenge",
                {"survives": survives, "robustness": challenge_result.robustness},
            )

        return challenge_result

    def _find_applicable_operations(self, projection: Projection) -> list[Operation]:
        """Find operations whose preconditions might be satisfied."""
        mapped_targets = {m.target.lower() for m in projection.mappings}
        applicable: list[Operation] = []

        for op in projection.metaphor.operations:
            # Check if any precondition concepts appear in mappings
            precond_words = set()
            for pre in op.preconditions:
                precond_words.update(pre.lower().split())

            if mapped_targets & precond_words:
                applicable.append(op)
            elif not op.preconditions:
                # No preconditions = always applicable
                applicable.append(op)

        return applicable

    def _is_critical_gap(self, gap: str, projection: Projection) -> bool:
        """Check if a gap is critical to solving the problem."""
        # Critical if it appears in constraints
        for constraint in projection.problem.constraints:
            if gap.lower() in constraint.lower():
                return True
        # Critical if it's a key term (appears multiple times)
        count = projection.problem.description.lower().count(gap.lower())
        return count > 2

    # ==========================================================================
    # SOLVE Stage
    # ==========================================================================

    def solve(self, projection: Projection) -> MetaphorSolution:
        """Reason within the metaphor space using its operations."""
        # Find applicable operations
        applicable = self._find_applicable_operations(projection)

        if not applicable:
            # Return minimal solution
            return MetaphorSolution(
                projection=projection,
                reasoning="No applicable operations found.",
                operations_applied=(),
                conclusion="Cannot reason within this metaphor.",
            )

        # Build reasoning chain
        reasoning_parts: list[str] = []
        operations_applied: list[str] = []
        current_state = self._extract_initial_state(projection)

        # Apply up to 3 operations
        for i, op in enumerate(applicable[:3]):
            reasoning, new_state = self._apply_operation(op, current_state, projection)
            reasoning_parts.append(f"Step {i + 1} ({op.name}):\n{reasoning}")
            operations_applied.append(op.name)
            current_state = new_state

        # Synthesize conclusion
        conclusion = self._synthesize_conclusion(
            reasoning_parts, current_state, projection
        )

        metaphor_solution = MetaphorSolution(
            projection=projection,
            reasoning="\n\n".join(reasoning_parts),
            operations_applied=tuple(operations_applied),
            conclusion=conclusion,
        )

        if self.on_stage_complete:
            self.on_stage_complete("solve", {"operations": len(operations_applied)})

        return metaphor_solution

    def _extract_initial_state(self, projection: Projection) -> dict[str, Any]:
        """Extract initial state from projection."""
        return {
            "conditions": [m.target for m in projection.mappings],
            "gaps": list(projection.gaps),
            "problem_domain": projection.problem.domain,
        }

    def _apply_operation(
        self, operation: Operation, state: dict[str, Any], projection: Projection
    ) -> tuple[str, dict[str, Any]]:
        """Apply an operation and return reasoning + new state."""
        # Build reasoning
        reasoning = f"Applying {operation.name}: {operation.description}\n"
        reasoning += f"Preconditions: {operation.preconditions}\n"
        reasoning += f"Effects: {operation.effects}\n"

        # Update state with effects
        new_state = dict(state)
        new_conditions = list(state.get("conditions", []))
        for effect in operation.effects:
            new_conditions.append(effect)
        new_state["conditions"] = new_conditions

        return reasoning, new_state

    def _synthesize_conclusion(
        self, reasoning: list[str], final_state: dict[str, Any], projection: Projection
    ) -> str:
        """Synthesize reasoning into a conclusion."""
        conditions = final_state.get("conditions", [])
        effects = [
            c
            for c in conditions
            if "is known" in c or "increases" in c or "improves" in c
        ]

        if effects:
            return f"In {projection.metaphor.name} terms: {'; '.join(effects[:3])}"
        return f"Analysis complete in {projection.metaphor.name} framework."

    # ==========================================================================
    # TRANSLATE Stage
    # ==========================================================================

    def translate(
        self, metaphor_solution: MetaphorSolution, problem: Problem
    ) -> tuple[str, tuple[str, ...], float]:
        """Translate metaphor solution back to problem terms."""
        projection = metaphor_solution.projection

        # Reverse mappings
        reverse_map = {m.target: m.source for m in projection.mappings}

        # Translate conclusion
        translated = metaphor_solution.conclusion
        for metaphor_term, problem_term in reverse_map.items():
            translated = translated.replace(metaphor_term, problem_term)

        # Extract actions from operations applied
        actions: list[str] = []
        for op_name in metaphor_solution.operations_applied:
            op = next(
                (o for o in projection.metaphor.operations if o.name == op_name), None
            )
            if op:
                # Translate operation description
                action = op.description
                for metaphor_term, problem_term in reverse_map.items():
                    action = action.replace(metaphor_term, problem_term)
                actions.append(action)

        # Calculate confidence
        confidence = projection.confidence * 0.8
        if metaphor_solution.operations_applied:
            confidence += 0.1

        if self.on_stage_complete:
            self.on_stage_complete(
                "translate", {"actions": len(actions), "confidence": confidence}
            )

        return translated, tuple(actions), confidence

    # ==========================================================================
    # VERIFY Stage
    # ==========================================================================

    def verify(self, solution: Solution, problem: Problem) -> tuple[Distortion, bool]:
        """Measure solution quality via distortion analysis."""
        projection = solution.metaphor_solution.projection

        # Structural loss
        structural_loss = 1.0 - projection.coverage

        # Round-trip error (simplified)
        # In production, would re-project and compare
        round_trip_error = len(projection.gaps) / max(
            1, len(projection.mappings) + len(projection.gaps)
        )

        # Prediction failures (simplified)
        # Check if constraints are addressed
        prediction_failures = 0
        for constraint in problem.constraints:
            addressed = any(
                constraint.lower() in action.lower()
                for action in solution.specific_actions
            )
            if not addressed:
                prediction_failures += 1

        distortion = Distortion(
            structural_loss=structural_loss,
            round_trip_error=round_trip_error,
            prediction_failures=prediction_failures,
        )

        verified = distortion.acceptable

        if self.on_stage_complete:
            self.on_stage_complete(
                "verify", {"distortion": distortion.total, "verified": verified}
            )

        return distortion, verified

    # ==========================================================================
    # Main Entry Point
    # ==========================================================================

    def solve_problem(self, problem: Problem) -> Solution:
        """
        Main entry point: solve a problem using metaphorical reasoning.

        Implements the search loop with backtracking.
        """
        state = SearchState(problem)

        while state.iteration < self.config.max_iterations:
            # RETRIEVE
            candidates = self.retrieve(
                problem,
                limit=self.config.max_candidates,
                exclude=state.candidates_tried,
            )

            if not candidates:
                break

            metaphor, score = candidates[0]
            state.candidates_tried.append(metaphor.id)

            # PROJECT
            features = extract_features(problem)
            abstraction = self.abstraction_model.suggest_abstraction(features)
            abstraction = max(
                self.config.min_abstraction,
                min(self.config.max_abstraction, abstraction),
            )

            projection = self.project(problem, metaphor, abstraction)
            state.record_attempt(metaphor.id, projection, "projected")

            # CHALLENGE
            challenge_result = self.challenge(projection)
            if not challenge_result.survives:
                state.record_backtrack(
                    "challenge", str(challenge_result.counterexamples)
                )
                continue

            # SOLVE
            metaphor_solution = self.solve(projection)

            # TRANSLATE
            translated, actions, confidence = self.translate(metaphor_solution, problem)

            # Build solution
            solution = Solution(
                problem=problem,
                metaphor_solution=metaphor_solution,
                translated_answer=translated,
                specific_actions=actions,
                distortion=Distortion(0, 0, 0),  # Placeholder
                trace_id=str(uuid4()),
            )

            # VERIFY
            distortion, verified = self.verify(solution, problem)

            # Update solution with actual distortion
            solution = Solution(
                problem=solution.problem,
                metaphor_solution=solution.metaphor_solution,
                translated_answer=solution.translated_answer,
                specific_actions=solution.specific_actions,
                distortion=distortion,
                trace_id=solution.trace_id,
            )

            state.update_best(solution)

            if verified:
                # Success - record feedback for learning
                if self.config.enable_learning:
                    feedback = Feedback(
                        problem_id=problem.id,
                        problem_features=features,
                        metaphor_id=metaphor.id,
                        abstraction=abstraction,
                        outcome=Outcome.SUCCESS,
                        distortion=distortion.total,
                    )
                    self.retrieval_model.update(feedback)
                    self.abstraction_model.update(feedback)
                return solution

            # Verification failed - decide recovery strategy
            recovery = self._decide_recovery(distortion)
            state.record_backtrack("verify", recovery)

            # Record feedback
            if self.config.enable_learning:
                feedback = Feedback(
                    problem_id=problem.id,
                    problem_features=features,
                    metaphor_id=metaphor.id,
                    abstraction=abstraction,
                    outcome=Outcome.VERIFY_FAILED,
                    distortion=distortion.total,
                )
                self.retrieval_model.update(feedback)

        # Return best solution found, or failure
        if state.best_solution:
            return state.best_solution

        # No solution found - return failure
        return Solution(
            problem=problem,
            metaphor_solution=MetaphorSolution(
                projection=Projection(
                    problem=problem,
                    metaphor=Metaphor(
                        id="null_metaphor",
                        name="None",
                        domain="none",
                        description="No suitable metaphor found",
                        operations=(),
                    ),
                    mappings=(),
                    abstraction=0.5,
                ),
                reasoning="No suitable metaphor found after all attempts.",
                operations_applied=(),
                conclusion="Unable to solve via metaphorical reasoning.",
            ),
            translated_answer="No solution found.",
            specific_actions=(),
            distortion=Distortion(1.0, 1.0, len(problem.constraints)),
            trace_id=str(uuid4()),
        )

    def _decide_recovery(self, distortion: Distortion) -> str:
        """Decide how to recover from verification failure."""
        if distortion.structural_loss > 0.5:
            return "retry_different_metaphor"
        if distortion.round_trip_error > 0.6:
            return "retry_different_abstraction"
        if distortion.prediction_failures > 2:
            return "try_different_metaphor"
        return "retry_different_metaphor"
