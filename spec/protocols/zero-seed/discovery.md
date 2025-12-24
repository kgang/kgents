# Zero Seed: Discovery

> *"Axioms are not declared. They are discovered."*

**Module**: Discovery
**Depends on**: [`core.md`](./core.md), [`dp.md`](./dp.md)

---

## Purpose

Axioms emerge through a **staged discovery process** rather than fixed enumeration. This module specifies the three-stage process: Constitution Mining → Mirror Test Dialogue → Living Corpus Validation.

---

## Three-Stage Discovery

```
Stage 1: CONSTITUTION MINING
    Input: spec/principles/*.md
    Output: Candidate axioms
    Method: LLM-assisted extraction + deduplication

Stage 2: MIRROR TEST DIALOGUE
    Input: Stage 1 candidates + user interaction
    Output: Personalized axiom set
    Method: Socratic questioning

Stage 3: LIVING CORPUS VALIDATION
    Input: Accepted axioms + witness marks
    Output: Behaviorally-validated rankings
    Method: Pattern mining
```

---

## Stage 1: Constitution Mining

Extract candidate axioms from principles documentation:

```python
@dataclass
class CandidateAxiom:
    """A potential axiom extracted from constitution."""
    text: str                           # The axiom statement
    source_path: str                    # Where it came from
    source_line: int                    # Line number
    tier: EvidenceTier                  # SOMATIC, AESTHETIC, etc.
    extraction_confidence: float        # LLM confidence
    dedup_key: str                      # For deduplication


@dataclass
class ConstitutionMiner:
    """Extract candidate axioms from principles documentation."""

    async def mine(self, paths: list[str]) -> list[CandidateAxiom]:
        candidates = []

        for path in paths:
            content = await read_file(path)
            extracted = await self._extract_from_document(content, path)
            candidates.extend(extracted)

        return self._deduplicate_and_rank(candidates)

    async def _extract_from_document(
        self, content: str, path: str
    ) -> list[CandidateAxiom]:
        """Extract principle statements from a document."""
        # Pattern 1: Explicit principle declarations
        # Pattern 2: Quotable axiom statements
        # Pattern 3: Imperative declarations

        # LLM-assisted extraction
        prompt = f"""Extract fundamental axioms from this document.

An axiom is:
- An irreducible statement taken on faith
- Cannot be derived from something more basic
- Guides all design decisions

Document:
{content[:4000]}

For each axiom, provide:
1. The statement (one sentence)
2. The source section
3. Why it's irreducible
4. Evidence tier: SOMATIC (gut), AESTHETIC (taste), CATEGORICAL (logical)

Format as JSON array.
"""
        response = await llm.generate(prompt)
        return self._parse_extraction(response, path)

    def _deduplicate_and_rank(
        self, candidates: list[CandidateAxiom]
    ) -> list[CandidateAxiom]:
        """Remove duplicates and rank by extraction confidence."""
        seen_keys = set()
        unique = []

        for c in sorted(candidates, key=lambda x: -x.extraction_confidence):
            if c.dedup_key not in seen_keys:
                seen_keys.add(c.dedup_key)
                unique.append(c)

        return unique
```

### Constitution Paths

Default mining paths:

```python
CONSTITUTION_PATHS = [
    "spec/principles/CONSTITUTION.md",  # The 7+7 principles
    "spec/principles.md",                # Design principles
    "spec/principles/meta.md",           # Meta-principles
    "spec/principles/operational.md",    # Operational principles
]
```

---

## Stage 2: Mirror Test Dialogue

Refine candidates via interactive questioning:

```python
async def mirror_test_dialogue(
    candidates: list[CandidateAxiom],
    observer: Observer,
) -> list[ZeroNode]:
    """
    Refine candidates via interactive Mirror Test.

    The Mirror Test asks: "Does this feel true for you on your best day?"
    """
    accepted = []

    for candidate in candidates:
        response = await ask_user(
            question=f"""Does this feel true for you on your best day?

> {candidate.text}

This comes from: {candidate.source_path}
""",
            options=[
                "Yes, deeply",
                "Yes, somewhat",
                "No",
                "I need to reframe it",
            ],
        )

        match response:
            case "Yes, deeply":
                accepted.append(create_axiom_node(candidate, confidence=1.0))

            case "Yes, somewhat":
                accepted.append(create_axiom_node(candidate, confidence=0.7))

            case "I need to reframe it":
                reframed = await ask_user("How would you say it?")
                accepted.append(create_axiom_node(
                    CandidateAxiom(
                        text=reframed,
                        source_path="user",
                        source_line=0,
                        tier=EvidenceTier.SOMATIC,
                        extraction_confidence=1.0,
                        dedup_key=hash_text(reframed),
                    ),
                    confidence=1.0,
                ))

            case "No":
                pass  # Skip this candidate


    return accepted


def create_axiom_node(candidate: CandidateAxiom, confidence: float) -> ZeroNode:
    """Create a ZeroNode from an accepted axiom candidate."""
    path = f"void.axiom.{slugify(candidate.text[:30])}"

    return ZeroNode(
        id=generate_node_id(),
        path=path,
        layer=1,  # Axioms are always L1
        kind="Axiom",
        title=candidate.text[:50],
        content=candidate.text,
        proof=None,  # Axioms have no proof (M)
        confidence=confidence,
        created_at=datetime.now(UTC),
        created_by="discovery",
        lineage=(),
        tags=frozenset({
            "zero-seed",
            "axiom",
            f"source:{candidate.source_path}",
            f"tier:{candidate.tier.value}",
        }),
        metadata={
            "source_path": candidate.source_path,
            "source_line": candidate.source_line,
            "extraction_confidence": candidate.extraction_confidence,
        },
    )
```

### Mirror Test UX

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🪞 MIRROR TEST: Axiom Discovery                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Does this feel true for you on your best day?                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  "Tasteful > feature-complete"                                       │   │
│  │                                                                       │   │
│  │  Source: spec/principles/CONSTITUTION.md §1                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [1] Yes, deeply        [2] Yes, somewhat                                   │
│  [3] No                 [4] I need to reframe it                            │
│                                                                             │
│  Progress: 3/12 candidates                                                  │
│  Accepted: 2 axioms                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Stage 3: Living Corpus Validation

Validate axioms against actual witnessed behavior:

```python
async def living_corpus_validation(
    axioms: list[ZeroNode],
    witness_store: WitnessStore,
) -> list[ZeroNode]:
    """
    Validate axioms against actual witnessed behavior.

    Asks: "What do you actually act on?"
    """
    all_marks = await witness_store.get_all_marks()
    all_crystals = await witness_store.get_all_crystals()

    for axiom in axioms:
        # Find marks that cite this axiom's principles
        citing_marks = [
            m for m in all_marks
            if any(tag in m.tags for tag in axiom.tags)
            or axiom_referenced_in_proof(axiom, m)
        ]

        # Compute behavioral alignment score
        if len(citing_marks) > 0:
            alignment = compute_behavioral_alignment(axiom, citing_marks)
            axiom = axiom.with_metadata(behavioral_alignment=alignment)

        # Check for behavioral contradictions
        contradictions = find_behavioral_contradictions(axiom, all_marks)
        if contradictions:
            for c in contradictions:
                # Create contradiction edge
                await graph.add_edge(ZeroEdge(
                    source=axiom.id,
                    target=c.node_id,
                    kind=EdgeKind.CONTRADICTS,
                    context=f"Behavioral contradiction: {c.description}",
                ))

    return rank_by_alignment(axioms)


def compute_behavioral_alignment(
    axiom: ZeroNode,
    citing_marks: list[Mark],
) -> float:
    """
    Compute how aligned behavior is with stated axiom.

    High alignment = actions match beliefs
    Low alignment = espoused theory ≠ theory-in-use
    """
    if not citing_marks:
        return 0.5  # Unknown

    positive_cites = sum(
        1 for m in citing_marks
        if m.response.success and "aligns_with" in m.tags
    )
    negative_cites = sum(
        1 for m in citing_marks
        if "contradicts" in m.tags or "violated" in m.tags
    )

    total = positive_cites + negative_cites
    if total == 0:
        return 0.5

    return positive_cites / total


def find_behavioral_contradictions(
    axiom: ZeroNode,
    marks: list[Mark],
) -> list[BehavioralContradiction]:
    """Find marks that contradict the axiom."""
    contradictions = []

    for mark in marks:
        # Check if mark's action contradicts axiom
        if contradiction_detected(axiom, mark):
            contradictions.append(BehavioralContradiction(
                mark_id=mark.id,
                node_id=mark.response.target_node,
                description=f"Action at {mark.timestamp} contradicts axiom",
                severity=compute_contradiction_severity(axiom, mark),
            ))

    return contradictions
```

### Behavioral Validation Report

```python
@dataclass
class BehavioralValidationReport:
    """Report from Stage 3 validation."""

    axiom_rankings: list[tuple[ZeroNode, float]]  # (axiom, alignment_score)
    contradictions_found: list[BehavioralContradiction]
    top_aligned: list[ZeroNode]  # Axioms with highest alignment
    drift_detected: list[ZeroNode]  # Axioms with low alignment

    def summary(self) -> str:
        return f"""
Behavioral Validation Complete
==============================
Axioms validated: {len(self.axiom_rankings)}
Top aligned: {[a.title for a in self.top_aligned[:3]]}
Drift detected: {[a.title for a in self.drift_detected]}
Contradictions: {len(self.contradictions_found)}
"""
```

---

## Discovery Timeline

```
Day 0: User starts Zero Seed
        ↓
        Stage 1: Constitution Mining (automated)
        Result: ~12 candidate axioms
        ↓
        Stage 2: Mirror Test (interactive, 5-10 min)
        Result: 3-5 accepted axioms
        ↓
        User begins cultivation

Day 7+: Stage 3 begins (background)
        Witness marks accumulate
        Behavioral patterns emerge

Day 30: First validation report
        Alignment scores computed
        Drift surfaced if any

Ongoing: Continuous validation
         New axioms can be added via Mirror Test
         Dead axioms can be deprecated
```

---

## Anti-Patterns

| Anti-pattern | Description | Resolution |
|--------------|-------------|------------|
| **Axiom Hoarding** | Accepting all candidates without Mirror Test | Enforce Stage 2 dialogue |
| **Behavioral Blindness** | Ignoring Stage 3 validation | Surface drift prominently |
| **Axiom Inflation** | Adding axioms without removing | Track axiom count; warn on growth |
| **Espoused/Theory Gap** | High-alignment axioms not acted on | Flag as "dormant axiom" |

---

## Open Questions

1. **Axiom retirement**: How do we gracefully deprecate axioms that no longer resonate?
2. **Multi-user discovery**: When users share a graph, whose Mirror Test wins?
3. **Axiom evolution**: Can axioms be refined, or only replaced?

---

*"The seed knows what it wants to become. Discovery is listening."*
