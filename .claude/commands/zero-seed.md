Zero Seed Protocol: Ground decisions in axioms, construct witnessed proofs, detect contradictions.

> *"The loss IS the difficulty. The fixed point IS the axiom. The proof IS the decision."*

## Purpose

Zero Seed is the epistemological substrate for agent reasoning. Use it to:
1. Ground decisions in axiomatic foundations (L1-L2)
2. Construct Toulmin proofs with Galois coherence (L3-L4)
3. Detect contradictions via super-additive loss
4. Navigate knowledge graphs toward coherence

## Quick Reference

| Operation | When | Command |
|-----------|------|---------|
| **Ground** | Before major decisions | Check claim against L1-L2 axioms |
| **Prove** | Justifying L3+ changes | Construct Toulmin proof |
| **Contradict** | Two views clash | Compute super-additive loss |
| **Cohere** | Validating argument | Measure Galois loss |
| **Navigate** | Exploring options | Loss-gradient descent |

## Protocol: Grounding Decisions

### Step 1: Identify the Claim

What are you deciding? State it clearly:

```
CLAIM: "Use SSE instead of WebSockets"
```

### Step 2: Ground in Axioms

Check against L1-L2 foundations:

| Level | Foundation | Test |
|-------|------------|------|
| **L1** | Entity, Morphism, Galois Ground | Does this preserve composition? |
| **L2** | Constitution principles | Which principle does this serve? |

```
GROUNDING:
- A2 (Morphism): SSE is simpler composition (unidirectional)
- Composable: Easier to chain with other handlers
- Tasteful: Simpler is better when sufficient
```

### Step 3: Construct Proof (If L3+)

For specification-level claims, provide Toulmin structure:

```
DATA: API needs server-to-client events only
WARRANT: Unidirectional streaming is simpler than bidirectional
CLAIM: Use SSE
BACKING: HTTP/2 makes SSE efficient; WebSockets add connection overhead
QUALIFIER: Definitely (for this use case)
REBUTTALS: Unless bidirectional needed later; Unless connection pooling matters
```

### Step 4: Compute Coherence

Estimate Galois loss (how much meaning survives modularization):

```
COHERENCE ESTIMATE:
- Claim is tight (low warrant_loss)
- Backing is strong (low backing_loss)
- Composition clear (low composition_loss)
- Estimated tier: EMPIRICAL (L < 0.3)
```

### Step 5: Record Decision

```bash
kg decide --fast "Use SSE for real-time updates" \
  --reasoning "Unidirectional sufficient, simpler composition, HTTP/2 efficient" \
  --json
```

## Protocol: Contradiction Detection

When two views conflict:

### Step 1: State Both Views

```
VIEW A (Kent): "Use LangChain for scale"
VIEW B (Claude): "Build kgents kernel for joy"
```

### Step 2: Compute Super-Additive Loss

```
LOSS ANALYSIS:
- L(A) = 0.25 (empirical grounding in resources)
- L(B) = 0.20 (aesthetic grounding in joy)
- L(A + B) = 0.65 (super-additive!)
- Excess = 0.65 - (0.25 + 0.20) = 0.20

VERDICT: Mild contradiction (0.1 < excess < 0.3)
```

### Step 3: Find Synthesis via Ghost Alternatives

Look for the "middle path" that resolves tension:

```
GHOST ALTERNATIVES:
1. "Build minimal kernel, validate, then decide" (L = 0.15)
2. "Use LangChain core, wrap with kgents idioms" (L = 0.30)
3. "Prototype kgents, benchmark against LangChain" (L = 0.22)

SYNTHESIS: Alternative 1 (lowest loss, tests both hypotheses)
```

### Step 4: Record Dialectic

```bash
kg decide --kent "Use LangChain" --kent-reasoning "Scale, resources, production" \
          --claude "Build kgents" --claude-reasoning "Novel contribution, joy-inducing" \
          --synthesis "Build minimal kernel, validate, then decide" \
          --why "Avoids both risks: philosophy without validation AND abandoning untested ideas" \
          --json
```

## Protocol: Proof Validation

For any L3+ node, validate proof quality:

### Coherence Tiers

| Tier | Loss Range | Meaning |
|------|------------|---------|
| **CATEGORICAL** | L < 0.1 | Proof is tight, near-lossless |
| **EMPIRICAL** | L < 0.3 | Well-grounded in evidence |
| **AESTHETIC** | L < 0.5 | Appeals to taste/values |
| **SOMATIC** | L < 0.7 | Intuitive, gut-level |
| **CHAOTIC** | L >= 0.7 | Incoherent, needs revision |

### Loss Decomposition

When proof is weak, identify where loss occurs:

```
LOSS DECOMPOSITION:
- data_loss: 0.05 (evidence is solid)
- warrant_loss: 0.25 (reasoning needs tightening)
- claim_loss: 0.03 (conclusion is clear)
- backing_loss: 0.18 (could use more support)
- composition_loss: 0.08 (parts connect well)

TOTAL: 0.59 (AESTHETIC tier)

RECOMMENDATIONS:
1. Strengthen warrant (contributes 0.25)
2. Add more backing (contributes 0.18)
```

## Protocol: Loss-Guided Navigation

When exploring options, follow the gradient:

### Navigation Strategy

```
CURRENT NODE: concept.spec.feature-x (L = 0.45)

EDGES AVAILABLE:
1. JUSTIFIES -> void.value.composability (L = 0.12) BEST
2. SPECIFIES -> world.impl.feature-x-v1 (L = 0.38)
3. CONTRADICTS -> concept.spec.feature-y (L = 0.61)

RECOMMENDATION: Follow edge 1 (steepest descent to coherence)
```

### High-Loss Warnings

When loss exceeds 0.6, flag for attention:

```
WARNING: High-loss node detected
Node: concept.spec.feature-z
Loss: 0.72 (CHAOTIC)

ISSUES:
- Proof doesn't survive modularization
- Warrant-claim linkage is weak
- Multiple implicit assumptions

ACTION REQUIRED: Revise proof or decompose node
```

## Integration with Witness

Zero Seed operations are witnessed:

### Mark Significant Decisions

```bash
km "Grounded feature-x in composability principle" \
   --reasoning "Galois loss 0.12, categorical tier" \
   --tag zero-seed --tag grounding
```

### Record Contradiction Resolutions

```bash
km "Resolved SSE vs WebSocket tension" \
   --reasoning "Super-additive loss 0.20, synthesis: SSE for now, revisit if bidirectional needed" \
   --tag zero-seed --tag contradiction
```

### Track Coherence Over Time

```bash
kg witness show --tag zero-seed --today --json
```

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Ungrounded Claims** | No link to L1-L2 | Always cite axiom or principle |
| **Missing Proofs** | L3+ without Toulmin | Construct DATA-WARRANT-CLAIM |
| **Ignored Contradictions** | Pretending views agree | Compute super-additive loss |
| **Chaotic Proofs** | L > 0.7, no revision | Decompose and strengthen |
| **Loss Ignorance** | No coherence tracking | Always estimate loss tier |

## Example Session

```
USER: Should we cache API responses?

AGENT:
CLAIM: "Implement API response caching"

GROUNDING:
- L1: Morphism preserved (cache is transparent wrapper)
- L2 Composable: Cache composes with any API call
- L2 Generative: Can regenerate from spec if cache clears

PROOF:
- DATA: API latency is 200ms, cache hits 85%
- WARRANT: 85% of requests can avoid 200ms latency
- CLAIM: Caching improves perceived performance
- BACKING: Redis proven at scale; TTL prevents staleness
- QUALIFIER: Probably (depends on hit rate holding)
- REBUTTALS: Unless data changes frequently; Unless memory constrained

COHERENCE: L = 0.18 (EMPIRICAL)

RECORDING DECISION...
$ kg decide --fast "Implement Redis caching for API" \
    --reasoning "85% hit rate, 200ms savings, empirical tier proof"

DONE.
```

## When to Use Zero Seed

- **Always**: Ground major architectural decisions in axioms
- **For L3+**: Construct Toulmin proofs
- **When Views Clash**: Compute contradiction via super-additive loss
- **Before Committing**: Validate proof coherence
- **When Navigating**: Follow loss-gradient toward coherence

## Arguments

If arguments provided, treat as the claim to analyze:

```
/zero-seed "Use GraphQL instead of REST"
```

The agent will:
1. Ground in axioms
2. Construct proof
3. Compute coherence
4. Record decision

## Philosophy

> *"Axioms aren't stipulated, they're discovered as zero-loss fixed points."*

Zero Seed transforms epistemology from philosophy to computation. Decisions have Galois loss. Contradictions have super-additive signals. Proofs have coherence scores. This is rigorous reasoning for agents.
