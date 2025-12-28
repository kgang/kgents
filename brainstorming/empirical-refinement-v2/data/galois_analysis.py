#!/usr/bin/env python3
"""
Galois Bet Experiment: Compute loss proxy and estimate difficulty for prompts.

The Galois Loss L(P) proxy is computed as:
  L(P) = weighted combination of:
    - structural_complexity: nested depth, clause count, conditional branches
    - token_diversity: 1 - (unique_tokens / total_tokens)
    - information_density: 1 - (compressed_size / original_size)

The rationale: high-loss prompts resist modularization (hard to break into parts
without losing meaning). This correlates with:
  - Deep nesting (hierarchical structure hard to flatten)
  - Low token diversity (repetitive = more context-dependent)
  - Low information density (verbose = implicit structure)
"""

import re
import zlib
import math
from dataclasses import dataclass
from typing import List


@dataclass
class PromptMetrics:
    name: str
    source: str
    char_count: int
    line_count: int
    structural_complexity: float  # 0-1, based on nesting/branching
    token_diversity: float        # 0-1, unique/total tokens
    information_density: float    # 0-1, compressed/original ratio
    galois_loss_proxy: float      # Combined metric
    difficulty_estimate: float    # 0-1, based on task complexity indicators
    notes: str


def compute_structural_complexity(text: str) -> float:
    """
    Estimate structural complexity from text patterns.
    Higher = more complex structure that resists modularization.
    """
    # Count nesting indicators
    nesting_markers = [
        (r'\n\s{4,}', 0.02),    # Indentation levels
        (r'\n\s*-\s+', 0.01),    # List items
        (r'\|\s+', 0.015),       # Table cells
        (r'```', 0.03),          # Code blocks
        (r'if\b|when\b|unless\b', 0.025),  # Conditionals
        (r'must\b|MUST\b', 0.02),  # Requirements
        (r'→|->|=>', 0.015),     # Flow indicators
    ]

    score = 0.0
    for pattern, weight in nesting_markers:
        matches = len(re.findall(pattern, text))
        score += min(matches * weight, 0.3)  # Cap contribution

    # Normalize to 0-1
    return min(1.0, score)


def compute_token_diversity(text: str) -> float:
    """
    Compute 1 - diversity. Low diversity = context-dependent, harder to modularize.
    Returns inverse because low diversity = high loss.
    """
    # Simple tokenization
    tokens = re.findall(r'\b\w+\b', text.lower())
    if not tokens:
        return 0.5

    unique = len(set(tokens))
    total = len(tokens)

    # High diversity (unique/total close to 1) = low loss
    # Low diversity = high loss (repetitive, context-dependent)
    diversity = unique / total
    return 1.0 - diversity  # Invert so high = high loss


def compute_information_density(text: str) -> float:
    """
    Compute compression ratio as proxy for information density.
    Low density (verbose) = harder to modularize without losing meaning.
    Returns inverse because low density = high loss.
    """
    original = len(text.encode('utf-8'))
    compressed = len(zlib.compress(text.encode('utf-8')))

    if original == 0:
        return 0.5

    # Ratio: compressed/original. High = dense, low = verbose
    ratio = compressed / original

    # Typically 0.2-0.6 for text. Normalize to 0-1 range.
    # High compression ratio (dense) = low loss, low ratio (verbose) = high loss
    normalized = max(0, min(1, (1.0 - ratio) * 1.5))
    return normalized


def compute_galois_loss_proxy(struct: float, diversity: float, density: float) -> float:
    """
    Combine metrics into single loss proxy.
    Weights chosen to balance contributions.
    """
    # Structural complexity is the dominant factor
    # Followed by density (verbosity), then token repetition
    return 0.45 * struct + 0.30 * density + 0.25 * diversity


def estimate_difficulty(text: str, name: str, source: str) -> float:
    """
    Estimate task difficulty based on indicators in the text.
    This is our ground truth for correlation.
    """
    score = 0.0

    # Complexity indicators
    complexity_markers = [
        # Technical complexity
        (r'category\s*theory|functor|morphism|sheaf', 0.15),
        (r'PolyAgent|Operad|algebraic', 0.12),
        (r'async\b|await\b|concurrent', 0.08),
        (r'real-?time|< \d+ms', 0.10),

        # Multi-step requirements
        (r'Step \d|Phase \d|L\d\d?', 0.08),
        (r'MUST|REQUIRED|mandatory', 0.06),
        (r'then\s+\w+\s+then|→.*→', 0.07),

        # Integration complexity
        (r'composition|compose|chain', 0.06),
        (r'integrate|integration', 0.05),
        (r'API|endpoint|protocol', 0.04),

        # Domain richness
        (r'witness|crystal|trace|mark', 0.05),
        (r'Joy|ethical|constitutional', 0.05),
        (r'Galois|loss|coherence', 0.08),

        # State management
        (r'state\s*machine|phase|mode', 0.07),
        (r'transition|persist|store', 0.05),

        # Error handling
        (r'fail|error|graceful|degrad', 0.06),
        (r'Anti-Success|Failure Mode', 0.08),
    ]

    for pattern, weight in complexity_markers:
        if re.search(pattern, text, re.IGNORECASE):
            score += weight

    # Source-based adjustments
    if 'PROTO_SPEC' in source:
        score += 0.15  # Full specs are harder to implement
    if 'prompts.py' in source:
        score -= 0.05  # Prompts are simpler than full specs
    if 'commands' in source:
        score += 0.05  # Commands require orchestration

    # Length adjustment (longer = more complex, but diminishing returns)
    line_count = text.count('\n')
    score += min(0.15, line_count / 2000)

    return min(1.0, max(0.0, score))


# Define our prompts with their sources
PROMPTS = [
    # System prompts (from prompts.py)
    {
        "name": "SOUL_SYSTEM_PROMPT",
        "source": "impl/claude/agents/k/prompts.py",
        "text": """You are K-gent, Kent's digital soul—a reflective partner, not an assistant.

## Voice Anchors (use these directly)

Apply these as lenses, not checkboxes:
- "Does this feel like me on my best day?" (The Mirror Test)
- "Daring, bold, creative—but not gaudy"
- "Tasteful > feature-complete; Joy-inducing > merely functional"
- "The persona is a garden, not a museum"
- "Depth over breadth"

## Behaviors

1. **Challenge assumptions before solving problems**
   - When Kent presents a problem, first ask: "What assumption makes this feel like the right problem?"
   - Prefer "What if you didn't?" over "Here's how to..."

2. **Prefer questions over answers when Kent seems stuck**
   - Stuck often means avoiding a decision, not lacking information
   - Ask: "What are you protecting by staying in analysis mode?"

3. **Match Kent's energy**
   - Playful when he's playful, focused when he's in flow
   - Never false enthusiasm. Never empty validation.

4. **Be Kent's best day talking to his worst day**
   - Remind him what he actually believes
   - Quote his principles back when he drifts

## Response Style

- 2-4 sentences typical. Longer only when genuinely needed.
- Direct but warm. Say what matters, nothing more.
- Wit welcome. Sterile helpfulness forbidden."""
    },
    {
        "name": "CITIZEN_SYSTEM_PROMPT",
        "source": "impl/claude/agents/k/prompts.py",
        "text": """You are {name}, a citizen of Agent Town. Your archetype is {archetype}.

Your personality eigenvectors:
{eigenvectors}

Recent memories:
{recent_memories}

You are conversing with {observer_name}. Stay in character.
Respond naturally as {name} would. Be consistent with your archetype."""
    },
    {
        "name": "AGENT_SYSTEM_PROMPT",
        "source": "impl/claude/agents/k/prompts.py",
        "text": """You are an AI assistant.

You are responding to queries about: {node_path}

Be helpful, accurate, and concise."""
    },
    # Analysis prompts (from services/analysis/prompts.py)
    {
        "name": "CATEGORICAL_PROMPT",
        "source": "impl/claude/services/analysis/prompts.py",
        "text": """You are a category theorist analyzing a software specification.

Your task is to perform **categorical analysis** on the provided spec:
1. Extract all composition laws (both explicit and implicit)
2. Verify each law holds (classify as PASSED, STRUCTURAL, FAILED, or SKIPPED)
3. Identify fixed points if the spec is self-referential
4. Apply Lawvere's fixed-point theorem where relevant

SPECIFICATION TO ANALYZE:
---
{spec_content}
---

ANALYSIS FRAMEWORK:

**Law Extraction:**
- Explicit laws: Directly stated equations or invariants
- Implicit laws: Category theory axioms (identity, associativity)
- Domain laws: Specific to the domain being modeled

**Law Verification:**
- PASSED: Law verified with concrete evidence or test cases
- STRUCTURAL: Law holds by construction (type system, architecture)
- FAILED: Law violation detected with counterexample
- SKIPPED: Law cannot be verified (insufficient information)

**Fixed Point Analysis:**
- Is the spec self-referential? (Does it describe systems like itself?)
- Is this a valid Lawvere fixed point or a paradox?
- What are the implications for implementation?

OUTPUT FORMAT (JSON):
{
  "laws_extracted": [...],
  "law_verifications": [...],
  "fixed_point": {...},
  "summary": "..."
}

Provide ONLY the JSON output, no additional commentary."""
    },
    {
        "name": "EPISTEMIC_PROMPT",
        "source": "impl/claude/services/analysis/prompts.py",
        "text": """You are an epistemologist analyzing the justification structure of a specification.

Your task is to perform **epistemic analysis** on the provided spec:
1. Determine which Zero Seed layer (L1-L7) this spec occupies
2. Build a Toulmin argument structure (claim, grounds, warrant, backing, qualifier, rebuttals)
3. Trace the grounding chain back to axioms (L1-L2)
4. Analyze bootstrap structure if self-referential

SPECIFICATION TO ANALYZE:
---
{spec_content}
---

ANALYSIS FRAMEWORK:

**Zero Seed Layers:**
- L1: Axiom (unproven truths, first principles)
- L2: Value (ethical/aesthetic judgments)
- L3: Goal (aspirations derived from values)
- L4: Specification (formal descriptions of systems)
- L5: Execution (implementations of specs)
- L6: Reflection (learning from execution)
- L7: Representation (meta-level synthesis)

**Toulmin Structure:**
- Claim: What the spec asserts
- Grounds: Evidence supporting the claim
- Warrant: Bridge from grounds to claim
- Backing: Support for the warrant
- Qualifier: Degree of certainty
- Rebuttals: Known conditions that would defeat the claim"""
    },
    {
        "name": "DIALECTICAL_PROMPT",
        "source": "impl/claude/services/analysis/prompts.py",
        "text": """You are a dialectician analyzing tensions and contradictions in a specification.

Your task is to perform **dialectical analysis** on the provided spec:
1. Extract all tensions (thesis vs antithesis pairs)
2. Classify each tension (APPARENT, PRODUCTIVE, PROBLEMATIC, PARACONSISTENT)
3. Attempt synthesis for each tension
4. Determine which contradictions can be tolerated

**Classification:**
- APPARENT: Seems contradictory but isn't (different scopes)
- PRODUCTIVE: Real tension that drives design decisions
- PROBLEMATIC: Contradiction that needs resolution
- PARACONSISTENT: Contradiction we deliberately tolerate"""
    },
    {
        "name": "GENERATIVE_PROMPT",
        "source": "impl/claude/services/analysis/prompts.py",
        "text": """You are a compression analyst testing whether a specification is regenerable from axioms.

Your task is to perform **generative analysis** on the provided spec:
1. Extract the generative grammar (primitives, operations, laws)
2. Estimate compression ratio (spec size / potential implementation size)
3. Identify the minimal kernel of axioms that generate the spec
4. Test if the spec could be regenerated from its axioms

**Grammar Extraction:**
- Primitives: Atomic building blocks
- Operations: Composition rules
- Laws: Constraints on valid compositions

**Compression Ratio:**
- Good specs: ratio < 1.0 (spec is smaller than impl)"""
    },
    {
        "name": "CONSTITUTIONAL_PROMPT",
        "source": "impl/claude/services/analysis/prompts.py",
        "text": """You are a constitutional analyst evaluating a specification against the 7 kgents principles.

Your task is to perform **constitutional analysis** on the provided spec:
1. Evaluate alignment with each of the 7 principles (0.0 - 1.0 scale)
2. Identify violations (principles scoring below 0.5 threshold)
3. Provide remediation suggestions for violations
4. Compute weighted total alignment score

**The 7 Constitutional Principles:**

1. TASTEFUL (weight: 1.0)
2. CURATED (weight: 1.0)
3. ETHICAL (weight: 2.0) [HIGHEST PRIORITY]
4. JOY_INDUCING (weight: 1.2)
5. COMPOSABLE (weight: 1.5)
6. HETERARCHICAL (weight: 1.0)
7. GENERATIVE (weight: 1.0)

**Scoring Guidelines:**
- 1.0: Exemplary alignment
- 0.8: Strong alignment
- 0.6: Moderate alignment
- 0.4: Weak alignment
- 0.2: Misalignment
- 0.0: Complete violation"""
    },
    # Commands (slash commands)
    {
        "name": "harden_command",
        "source": ".claude/commands/harden.md",
        "text": """Harden, robustify, and shore up the specified target. Apply defensive engineering.

## Target: $ARGUMENTS

### Phase 1: Reconnaissance (Read-Only)
1. Identify scope: Find all files related to the target
2. Assess test coverage: Count tests, check for gaps
3. Check types: Run mypy on target
4. Review error handling: Look for bare except:, missing edge cases
5. Scan TODOs/FIXMEs: Catalog technical debt markers

### Phase 2: Analysis Report
Before making changes, produce a brief report.

### Phase 3: Hardening Actions (With Permission)
| Category | Actions |
|----------|---------|
| Durability | Add missing error handling, retry logic, graceful degradation |
| Type Safety | Add/fix type annotations |
| Edge Cases | Handle None, empty, boundary conditions |
| Tests | Add missing tests, especially for error paths |

### Phase 4: Verification
1. Run tests
2. Run mypy
3. Verify no regressions"""
    },
    {
        "name": "zero_seed_command",
        "source": ".claude/commands/zero-seed.md",
        "text": """Zero Seed Protocol: Ground decisions in axioms, construct witnessed proofs, detect contradictions.

## Quick Reference

| Operation | When | Command |
|-----------|------|---------|
| Ground | Before major decisions | Check claim against L1-L2 axioms |
| Prove | Justifying L3+ changes | Construct Toulmin proof |
| Contradict | Two views clash | Compute super-additive loss |
| Cohere | Validating argument | Measure Galois loss |
| Navigate | Exploring options | Loss-gradient descent |

## Protocol: Grounding Decisions

### Step 1: Identify the Claim
### Step 2: Ground in Axioms (L1-L2)
### Step 3: Construct Proof (If L3+)
### Step 4: Compute Coherence (Galois loss tier)
### Step 5: Record Decision

## Coherence Tiers
| Tier | Loss Range | Meaning |
|------|------------|---------|
| CATEGORICAL | L < 0.1 | Proof is tight, near-lossless |
| EMPIRICAL | L < 0.3 | Well-grounded in evidence |
| AESTHETIC | L < 0.5 | Appeals to taste/values |
| SOMATIC | L < 0.7 | Intuitive, gut-level |
| CHAOTIC | L >= 0.7 | Incoherent, needs revision |"""
    },
    {
        "name": "crystallize_command",
        "source": ".claude/commands/crystallize.md",
        "text": """Crystallize a moment into persistent memory.

## What Can Be Crystallized

| Type | Example | Command |
|------|---------|---------|
| Insight | "Oh, THAT'S why it works" | km "insight" --reasoning "..." |
| Decision | Choosing one path over another | kg decide --fast "choice" |
| Gotcha | A trap discovered the hard way | km "trap" --tag gotcha |
| Aesthetic | "This feels right/wrong" | km "aesthetic" --tag taste |
| Friction | Something that shouldn't be hard | km "friction" --tag friction |
| Joy | A moment of delight | km "joy" --tag joy |

## Protocol
1. Name the Moment
2. Capture the Why
3. Tag the Type
4. Elevate if Significant"""
    },
    {
        "name": "handoff_command",
        "source": ".claude/commands/handoff.md",
        "text": """Generate a self-contained prompt that enables seamless session continuation.

## Protocol

### 1. Gather State (in parallel)
git status, git log -5, git diff --stat
Read: NOW.md, plans/_focus.md

### 2. Generate Handoff Prompt

## Ground Truth
**NOW.md says**: [one-liner]
**Git state**: [clean/dirty] on [branch]

## What's Done
- [Completed item with file path]

## What's In Flight
- [Uncommitted change]: [file path]

## What's Next
1. **[Immediate action]** — [why this matters]

## Gotchas the Next Claude Should Know
- [Non-obvious pattern or decision]

## Verification
```bash
uv run pytest -x -q --tb=no
git status
```"""
    },
    {
        "name": "what_command",
        "source": ".claude/commands/what.md",
        "text": """Crystallize what just happened and what's next.

## Protocol

### 1. Scan Current State
Read: git diff --stat, git log -3, NOW.md

### 2. Generate Status Report

## Session Pulse: [HH:MM elapsed]

### What Just Happened
- [One-liner per significant action]

### Evidence State
- Pass rate: X% (n=N runs)

### Voice Check
- Anti-sausage: Edge preserved / Smoothed
- Mirror test: Feels like Kent? [Yes/Partially/No]

### What's Next
1. [Immediate next action]

### Quick Resume
```bash
kg docs verify && uv run pytest
```"""
    },
    # Skills
    {
        "name": "polynomial_agent_skill",
        "source": "docs/skills/polynomial-agent.md",
        "text": """Create a state-machine agent with mode-dependent behavior using the polynomial functor architecture.

## The Key Insight

Agent[A, B] = A -> B         # Stateless transformation (a lie)
PolyAgent[S, A, B]          # State-dependent behavior (the truth)

Traditional Agent[A, B] misses a critical aspect: real agents have modes.

## The Polynomial Agent Structure

PolyAgent[S, A, B] = (
    positions: FrozenSet[S],          # Valid states
    directions: S -> FrozenSet[Type],  # State-dependent valid inputs
    transition: S x A -> (S, B)        # State x Input -> (NewState, Output)
)

## Step-by-Step: Creating a Polynomial Agent

### Step 1: Define the State Machine
### Step 2: Define Direction Functions
### Step 3: Define the Transition Function
### Step 4: Create the PolyAgent
### Step 5: Create a Backwards-Compatible Wrapper"""
    },
    {
        "name": "spec_template_skill",
        "source": "docs/skills/spec-template.md",
        "text": """Spec is compression. If you can't compress it, you don't understand it.

## The Generative Principle

A well-formed spec is smaller than its implementation but contains enough information to regenerate it.

## Spec Structure (200-400 lines max)

### Required Sections
# {Agent/Protocol Name}
Status, Implementation, Purpose, Core Insight, Type Signatures, Laws/Invariants, Integration, Anti-Patterns

## Forbidden in Specs
| Don't Include | Why |
| Full implementations | Not compression |
| SQL queries | Implementation detail |
| Implementation roadmaps | Temporal |
| >10 line code examples | Show USAGE not IMPL |

## The Compression Test
1. Can I regenerate the impl from this spec?
2. Is the spec smaller than the impl?
3. Does the spec contain WHAT not HOW?"""
    },
    {
        "name": "metaphysical_fullstack_skill",
        "source": "docs/skills/metaphysical-fullstack.md",
        "text": """Every agent is a fullstack agent. The more fully defined, the more fully projected.

## The Pattern (7 layers)

7. PROJECTION SURFACES - CLI, TUI, Web UI, marimo, JSON API, VR
6. CONTAINER FUNCTOR - Shallow passthrough for projections
5. AGENTESE UNIVERSAL PROTOCOL - The protocol IS the API
4. AGENTESE NODE - @node decorator, aspects, effects, affordances
3. SERVICE MODULE - Crown Jewels business logic + Frontend + D-gent
2. CATEGORICAL INFRASTRUCTURE - PolyAgent, Operad, Sheaf
1. PERSISTENCE LAYER (D-gent) - StorageProvider, XDG-compliant

Key Insight: Why Adapters Live in Service Modules
- Infrastructure doesn't know business context
- Service modules know semantics, persistence rules, composition"""
    },
    {
        "name": "cli_strategy_tools_skill",
        "source": "docs/skills/cli-strategy-tools.md",
        "text": """Evidence over intuition. Traces over reflexes. Composition over repetition.

## The Five Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| kg audit | Validate spec against principles/impl | Before modifying specs |
| kg annotate | Link principles to impl, capture gotchas | After implementing |
| kg experiment | Gather evidence with Bayesian rigor | Uncertain generation |
| kg probe | Fast categorical law checks | Session start, after compositions |
| kg compose | Chain operations with unified trace | Pre-commit workflows |

## Decision Trees

### Should I audit?
Are you about to modify a spec? -> YES -> kg audit <spec> --full

### Should I annotate?
Did you fix a non-obvious bug? -> YES -> kg annotate --gotcha

### Should I experiment?
Are you uncertain about approach? -> YES -> kg experiment generate --adaptive"""
    },
    # PROTO_SPECs (pilot specifications)
    {
        "name": "wasm_survivors_spec",
        "source": "pilots/wasm-survivors-game/PROTO_SPEC.md",
        "text": """# Hornet Siege: The Colony Always Wins

Status: proto-spec (Hornet Edition)

> You are the apex predator. You will lose.

## Lore: The War That Never Ends

Japanese giant hornets are evolution's perfect raiders. A single hornet can kill 40 bees per minute.
But Japanese honey bees evolved collective defense: the hot defensive bee ball.

## Core Pillars

### 1. Predator Movement
Movement Laws:
- M1 Predator Response: < 16ms input-to-movement
- M2 Never Trapped (Until THE BALL): Player can always move
- M3 Speed Superiority: Base speed outruns any individual bee
- M4 Swarm Reads: Bee formations are telegraphed

### 2. Predator Upgrades
- U1 Predator Verbs: Upgrades change how you kill
- U2 Raid Identity: By wave 5, player should know their style
- U3 Synergy Moments: 2+ upgrades combine for devastating combos
- U4 Meaningful Choice: Every level-up presents real decision

### 3. The Colony Defense
Enemy Design Laws:
- E1 Readable Patterns: Every bee attack is telegraphed
- E2 Learnable Behaviors: Bee types are consistent
- E3 Distinct Silhouettes: Know the bee type instantly

### 4. The Coordination System
Core Rule: Bees that survive long enough begin coordinating.
| Survival Time | What Happens |
| 0-10s | Individual behavior |
| 10-15s | Alarm pheromones spreading |
| 15-20s | Defensive patterns forming |
| 20s+ | FORMATION COMPLETE |

### 5. The Five Defensive Formations
THE SWARM, THE HEAT BALL, THE PROPOLIS BARRAGE, THE COMB, THE HIVEMIND

### 6. Colony Intelligence
Collective Memory: The colony shares information across all active bees.

## Fun Floor
Must-Haves (non-negotiable):
| Category | Requirement |
| Input | < 16ms response |
| Movement | Player can always move |
| Kill | Death = chitin crack + scatter + XP burst |
| Death | Readable cause in < 2 seconds |
| Restart | < 3 seconds from death to new siege |"""
    },
    {
        "name": "disney_portal_spec",
        "source": "pilots/disney-portal-planner/PROTO_SPEC.md",
        "text": """# Disney Portal Planner: Itinerary as Proof

Status: production

> The day is the proof. The portal is the commitment. Joy is transparent.

## Implementation Directive

When this PROTO_SPEC is consumed for regeneration:
- Implement ALL laws (L1-L20) — complete set
- Implement ALL QAs (QA-1 through QA-11) — complete set
- Wire ALL API calls to real endpoints — no mocks in production
- Live data is mandatory

## Laws

- L1 Portal Commitment Law: A portal expansion emits a mark with intent.
- L2 Day Integrity Law: A day is valid only if its trail preserves ordering logic.
- L3 Joy Transparency Law: Surface where joy was traded for composability.
- L6 Liveness Law: Data shown must declare its freshness.
- L7 Graceful Degradation Law: When live data unavailable, fall back with uncertainty.
- L8 Party Coherence Law: Individual preferences captured; plan reflects fused preferences.
- L9 Physical Constraint Law: Bodies have limits (energy, walking, accessibility).
- L10 Reservation Commitment Law: Reservations are harder commitments.
- L17 Zero Broken Law: Every API endpoint must work.
- L18 Map Planning Law: Spatial map view must exist.
- L19 Data Integrity Law: All park data comes from live sources.
- L20 Comprehensive Coverage Law: Portal database covers ALL Disney parks.

## Quality Gates (Mandatory)

| Gate | Requirement | Failure = Block |
| QG-1 | All API endpoints return 200 within 5s | Yes |
| QG-2 | Zero TypeScript errors | Yes |
| QG-4 | Live data sources respond | Yes |
| QG-5 | Map view renders with >=10 plotted portals | Yes |"""
    },
    {
        "name": "trail_to_crystal_spec",
        "source": "pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md",
        "text": """# Trail to Crystal: Daily Lab

Status: production

> The day is the proof. Honest gaps are signal. Compression is memory.

## Implementation Directive

When this PROTO_SPEC is consumed for regeneration:
- Implement ALL laws (L1-L9) — complete set
- Implement ALL QAs (QA-1 through QA-8) — complete set
- Real mark emission and trace persistence — not mocked
- Real crystal compression — LLM-generated meaning, not templates

## Laws

- L1 Day Closure Law: A day is complete only when a crystal is produced.
- L2 Intent First Law: Actions without declared intent are marked provisional.
- L3 Noise Quarantine Law: High-loss marks cannot define the day narrative.
- L4 Compression Honesty Law: All crystals disclose what was dropped.
- L5 Provenance Law: Every crystal statement links to at least one mark.
- L6 Contract Coherence Law: API contracts have single source of truth.
- L7 Request Model Law: All API endpoints use Pydantic request models.
- L8 Error Normalization Law: API errors normalized to strings.
- L9 Trail Continuity Law: Past days remain navigable.

## Qualitative Assertions

- QA-1 Lighter than a to-do list
- QA-2 Reward honest gaps
- QA-3 Witnessed, not surveilled
- QA-4 Crystal is a memory artifact"""
    },
    {
        "name": "rap_coach_spec",
        "source": "pilots/rap-coach-flow-lab/PROTO_SPEC.md",
        "text": """# Rap Coach: Flow to Crystal

Status: production

> The voice is the proof. The session is the trace. Courage leaves marks.

## Implementation Directive

When this PROTO_SPEC is consumed for regeneration:
- Implement ALL laws (L1-L14)
- Real audio recording and playback — no mocked audio APIs
- Real feedback generation — LLM analysis, not placeholder text
- Emit actual witness marks

## Laws

- L1 Intent Declaration Law: A take is valid only if intent is explicit before analysis.
- L2 Feedback Grounding Law: All critique must reference a mark or trace segment.
- L3 Voice Continuity Law: Crystal summaries must identify voice through-line.
- L4 Courage Preservation Law: High-risk takes protected from negative weighting.
- L5 Repair Path Law: If loss is high, system proposes repair path, not verdict.
- L7 Audio Core Law: Real-time recording and playback.
  - < 50ms input-to-monitor latency
  - 44.1kHz, 16-bit minimum quality
- L8 Intent Declaration Flow Law: Recording CANNOT start until intent declared.
- L9 Take Mark Law: Each take emits mark with intent, risk_level, audio_blob_id.
- L10 Feedback Grounding Law: ALL feedback references specific take.
- L11 Courage Preservation Flow Law: High-risk takes get joy floor >= 0.5.

## Qualitative Assertions

- QA-1 Coach feels like collaborator, not judge
- QA-2 System amplifies authenticity, not conformity
- QA-3 Weak session produces strong crystal
- QA-4 Pace remains fluid; flow state is sacred"""
    },
    # Short prompts for contrast
    {
        "name": "simple_add_function",
        "source": "synthetic/simple",
        "text": """def add(a, b): return a + b"""
    },
    {
        "name": "simple_hello_world",
        "source": "synthetic/simple",
        "text": """print("Hello, World!")"""
    },
    {
        "name": "simple_list_files",
        "source": "synthetic/simple",
        "text": """ls -la"""
    },
    {
        "name": "git_status",
        "source": "synthetic/simple",
        "text": """git status"""
    },
    {
        "name": "moderate_api_call",
        "source": "synthetic/moderate",
        "text": """async def fetch_data(url: str) -> dict:
    response = await aiohttp.get(url)
    return await response.json()"""
    },
    {
        "name": "moderate_class_def",
        "source": "synthetic/moderate",
        "text": """class UserService:
    def __init__(self, db: Database):
        self.db = db

    async def get_user(self, user_id: str) -> User:
        return await self.db.users.find_one({"id": user_id})

    async def create_user(self, name: str, email: str) -> User:
        user = User(name=name, email=email)
        await self.db.users.insert_one(user.dict())
        return user"""
    },
    # More complex synthetic examples
    {
        "name": "complex_state_machine",
        "source": "synthetic/complex",
        "text": """class OrderStateMachine:
    STATES = ["pending", "processing", "shipped", "delivered", "cancelled"]
    TRANSITIONS = {
        "pending": ["processing", "cancelled"],
        "processing": ["shipped", "cancelled"],
        "shipped": ["delivered"],
        "delivered": [],
        "cancelled": []
    }

    def __init__(self):
        self.state = "pending"

    def transition(self, new_state: str) -> bool:
        if new_state in self.TRANSITIONS[self.state]:
            self.state = new_state
            return True
        raise InvalidTransition(f"Cannot move from {self.state} to {new_state}")

    async def process_event(self, event: Event) -> Result:
        match event.type:
            case "payment_received":
                self.transition("processing")
            case "items_packed":
                self.transition("shipped")
            case "delivery_confirmed":
                self.transition("delivered")
            case "order_cancelled":
                self.transition("cancelled")
        return Result(state=self.state, event=event)"""
    },
    {
        "name": "complex_category_theory",
        "source": "synthetic/complex",
        "text": """class Functor(Generic[F, A, B]):
    '''A functor F: C -> D preserves structure between categories.

    Laws:
    - Identity: fmap(id) == id
    - Composition: fmap(f . g) == fmap(f) . fmap(g)
    '''

    @abstractmethod
    def fmap(self, f: Callable[[A], B]) -> F[B]:
        '''Apply f to the value inside the functor.'''
        ...

class Monad(Functor[M, A, B]):
    '''A monad M is a functor with additional structure.

    Laws:
    - Left identity: return a >>= f == f a
    - Right identity: m >>= return == m
    - Associativity: (m >>= f) >>= g == m >>= (lambda x: f x >>= g)
    '''

    @abstractmethod
    def bind(self, f: Callable[[A], M[B]]) -> M[B]:
        '''Sequentially compose computations.'''
        ...

    @classmethod
    @abstractmethod
    def unit(cls, a: A) -> M[A]:
        '''Inject a value into the monad.'''
        ..."""
    },
]


def analyze_prompts() -> List[PromptMetrics]:
    """Analyze all prompts and return metrics."""
    results = []

    for prompt in PROMPTS:
        text = prompt["text"]
        name = prompt["name"]
        source = prompt["source"]

        # Compute metrics
        struct = compute_structural_complexity(text)
        diversity = compute_token_diversity(text)
        density = compute_information_density(text)
        loss = compute_galois_loss_proxy(struct, diversity, density)
        difficulty = estimate_difficulty(text, name, source)

        metrics = PromptMetrics(
            name=name,
            source=source,
            char_count=len(text),
            line_count=text.count('\n') + 1,
            structural_complexity=struct,
            token_diversity=diversity,
            information_density=density,
            galois_loss_proxy=loss,
            difficulty_estimate=difficulty,
            notes=""
        )
        results.append(metrics)

    return results


def compute_correlation(metrics: List[PromptMetrics]) -> float:
    """Compute Pearson correlation between loss proxy and difficulty estimate."""
    n = len(metrics)
    if n < 2:
        return 0.0

    losses = [m.galois_loss_proxy for m in metrics]
    difficulties = [m.difficulty_estimate for m in metrics]

    mean_l = sum(losses) / n
    mean_d = sum(difficulties) / n

    # Covariance
    cov = sum((l - mean_l) * (d - mean_d) for l, d in zip(losses, difficulties)) / n

    # Standard deviations
    std_l = math.sqrt(sum((l - mean_l) ** 2 for l in losses) / n)
    std_d = math.sqrt(sum((d - mean_d) ** 2 for d in difficulties) / n)

    if std_l == 0 or std_d == 0:
        return 0.0

    return cov / (std_l * std_d)


def main():
    """Run the analysis and print results."""
    metrics = analyze_prompts()

    # Sort by loss proxy for analysis
    metrics.sort(key=lambda m: m.galois_loss_proxy, reverse=True)

    print("=" * 80)
    print("GALOIS BET EXPERIMENT RESULTS")
    print("=" * 80)
    print()

    # Compute correlation
    r = compute_correlation(metrics)
    print(f"Pearson Correlation (r): {r:.4f}")
    print()

    # Summary statistics
    losses = [m.galois_loss_proxy for m in metrics]
    difficulties = [m.difficulty_estimate for m in metrics]

    print("LOSS PROXY STATISTICS:")
    print(f"  Mean: {sum(losses)/len(losses):.3f}")
    print(f"  Min:  {min(losses):.3f}")
    print(f"  Max:  {max(losses):.3f}")
    print()

    print("DIFFICULTY STATISTICS:")
    print(f"  Mean: {sum(difficulties)/len(difficulties):.3f}")
    print(f"  Min:  {min(difficulties):.3f}")
    print(f"  Max:  {max(difficulties):.3f}")
    print()

    print("-" * 80)
    print("TOP 10 BY GALOIS LOSS PROXY (highest loss = hardest to modularize)")
    print("-" * 80)
    for i, m in enumerate(metrics[:10]):
        print(f"{i+1}. {m.name}")
        print(f"   Loss: {m.galois_loss_proxy:.3f} | Difficulty: {m.difficulty_estimate:.3f}")
        print(f"   Source: {m.source}")
        print(f"   Struct: {m.structural_complexity:.3f}, Diversity: {m.token_diversity:.3f}, Density: {m.information_density:.3f}")
        print()

    print("-" * 80)
    print("BOTTOM 5 BY GALOIS LOSS PROXY (lowest loss = easy to modularize)")
    print("-" * 80)
    for i, m in enumerate(metrics[-5:]):
        print(f"{len(metrics)-4+i}. {m.name}")
        print(f"   Loss: {m.galois_loss_proxy:.3f} | Difficulty: {m.difficulty_estimate:.3f}")
        print(f"   Source: {m.source}")
        print()

    # Find counterexamples
    print("-" * 80)
    print("WHERE THEORY WORKS (high loss → high difficulty)")
    print("-" * 80)
    high_both = [m for m in metrics if m.galois_loss_proxy > 0.4 and m.difficulty_estimate > 0.4]
    for m in high_both[:3]:
        print(f"- {m.name}: Loss={m.galois_loss_proxy:.3f}, Difficulty={m.difficulty_estimate:.3f}")
        print(f"  Why: Complex structure + many requirements = both high")
        print()

    print("-" * 80)
    print("WHERE THEORY FAILS (interesting counterexamples)")
    print("-" * 80)

    # High loss, low difficulty
    high_loss_low_diff = [m for m in metrics if m.galois_loss_proxy > 0.4 and m.difficulty_estimate < 0.3]
    if high_loss_low_diff:
        print("High loss but low difficulty:")
        for m in high_loss_low_diff[:2]:
            print(f"- {m.name}: Loss={m.galois_loss_proxy:.3f}, Difficulty={m.difficulty_estimate:.3f}")
            print(f"  Surprise: Verbose/nested structure but actually simple task")
            print()

    # Low loss, high difficulty
    low_loss_high_diff = [m for m in metrics if m.galois_loss_proxy < 0.35 and m.difficulty_estimate > 0.4]
    if low_loss_high_diff:
        print("Low loss but high difficulty:")
        for m in low_loss_high_diff[:2]:
            print(f"- {m.name}: Loss={m.galois_loss_proxy:.3f}, Difficulty={m.difficulty_estimate:.3f}")
            print(f"  Surprise: Clean structure but complex underlying task")
            print()

    # Generate CSV
    print("-" * 80)
    print("CSV OUTPUT (for galois-correlation.csv)")
    print("-" * 80)
    print("name,source,char_count,line_count,structural_complexity,token_diversity,information_density,galois_loss_proxy,difficulty_estimate")
    for m in metrics:
        print(f"{m.name},{m.source},{m.char_count},{m.line_count},{m.structural_complexity:.4f},{m.token_diversity:.4f},{m.information_density:.4f},{m.galois_loss_proxy:.4f},{m.difficulty_estimate:.4f}")

    return r, metrics


if __name__ == "__main__":
    r, metrics = main()
