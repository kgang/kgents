"""
LLM Prompt Templates for Analysis Modes.

Each analysis mode has a specialized prompt that guides the LLM
to perform rigorous analysis according to the mode's principles.

The prompts are designed to:
1. Ground the LLM in philosophical/mathematical frameworks
2. Request structured JSON output for reliable parsing
3. Provide clear examples and anti-patterns
4. Handle edge cases (self-referential specs, missing info)

Teaching:
    gotcha: Prompts request JSON output but LLMs may wrap in markdown.
            Parsers in parsers.py strip ```json...``` wrappers.
            (Evidence: parsers.py::extract_json_from_response)

    gotcha: Spec content is injected via {spec_content}, not direct inclusion.
            This prevents injection attacks and allows preprocessing.
            (Evidence: service.py::_load_spec_content sanitization)
"""

from __future__ import annotations

# =============================================================================
# Categorical Analysis Prompt
# =============================================================================

CATEGORICAL_PROMPT = """You are a category theorist analyzing a software specification.

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
{{
  "laws_extracted": [
    {{"name": "identity", "equation": "id >> f = f", "source": "implicit (category axiom)"}},
    {{"name": "associativity", "equation": "(f >> g) >> h = f >> (g >> h)", "source": "implicit"}}
  ],
  "law_verifications": [
    {{"law_name": "identity", "status": "STRUCTURAL", "message": "Category law assumed by construction"}},
    {{"law_name": "associativity", "status": "STRUCTURAL", "message": "Guaranteed by PolyAgent composition"}}
  ],
  "fixed_point": {{
    "is_self_referential": true,
    "description": "Spec describes X; spec IS an X",
    "is_valid": true,
    "implications": ["Self-analysis is valid", "Meta-applicability holds"]
  }},
  "summary": "Categorical analysis: 2/2 laws verified structurally. Valid fixed point detected."
}}

Provide ONLY the JSON output, no additional commentary.
"""

# =============================================================================
# Epistemic Analysis Prompt
# =============================================================================

EPISTEMIC_PROMPT = """You are an epistemologist analyzing the justification structure of a specification.

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
- Qualifier: Degree of certainty ("definitely", "probably", "possibly")
- Rebuttals: Known conditions that would defeat the claim

**Grounding Chain:**
- Trace justification steps from this spec down to L1-L2 axioms
- Each step: (layer, node description, edge type)
- Must terminate at axioms (no infinite regress)

**Bootstrap Analysis:**
- Is spec self-describing? (Describes systems at its own layer?)
- Is this a valid bootstrap or infinite regress?

OUTPUT FORMAT (JSON):
{{
  "layer": 4,
  "toulmin": {{
    "claim": "This specification defines valid behavior",
    "grounds": ["Formal structure", "Tested implementation"],
    "warrant": "Well-specified behavior enables correct implementation",
    "backing": "Constitution principles (Composable, Generative)",
    "qualifier": "definitely",
    "rebuttals": ["Unless requirements change"],
    "tier": "CATEGORICAL"
  }},
  "grounding_chain": [
    [1, "rigor_axiom", "grounds"],
    [2, "composability_value", "justifies"],
    [3, "analysis_goal", "specifies"],
    [4, "this_spec", "implements"]
  ],
  "terminates_at_axiom": true,
  "bootstrap": {{
    "is_self_describing": false,
    "layer_described": 4,
    "layer_occupied": 4,
    "is_valid": true,
    "explanation": "Spec describes L4 systems but is not self-referential"
  }},
  "summary": "Epistemic analysis: L4 specification, grounded at L1, no bootstrap issues"
}}

Provide ONLY the JSON output, no additional commentary.
"""

# =============================================================================
# Dialectical Analysis Prompt
# =============================================================================

DIALECTICAL_PROMPT = """You are a dialectician analyzing tensions and contradictions in a specification.

Your task is to perform **dialectical analysis** on the provided spec:
1. Extract all tensions (thesis vs antithesis pairs)
2. Classify each tension (APPARENT, PRODUCTIVE, PROBLEMATIC, PARACONSISTENT)
3. Attempt synthesis for each tension
4. Determine which contradictions can be tolerated

SPECIFICATION TO ANALYZE:
---
{spec_content}
---

ANALYSIS FRAMEWORK:

**Tension Extraction:**
- Look for claims that pull in different directions
- Design trade-offs, competing principles, unresolved choices
- Both explicit tensions and implicit contradictions

**Classification:**
- APPARENT: Seems contradictory but isn't (different scopes, resolved by context)
- PRODUCTIVE: Real tension that drives design decisions (feature vs simplicity)
- PROBLEMATIC: Contradiction that needs resolution (breaks the system)
- PARACONSISTENT: Contradiction we deliberately tolerate (philosophical grounding)

**Synthesis:**
- Thesis → Antithesis → Synthesis (Hegelian dialectic)
- Not all tensions have syntheses
- Some are resolved by hierarchy (ethical > technical)
- Some are held in productive tension (design trade-off)

**Paraconsistent Tolerance:**
- When is it OK to accept a contradiction?
- Example: "Axioms are unproven" vs "Everything should be justified"
  → Tolerated because foundationalism requires grounding

OUTPUT FORMAT (JSON):
{{
  "tensions": [
    {{
      "thesis": "Analysis should be rigorous",
      "antithesis": "Rigor may block usability",
      "classification": "PRODUCTIVE",
      "synthesis": "Layered API: simple interface, formal backing",
      "is_resolved": true
    }},
    {{
      "thesis": "Axioms are unproven",
      "antithesis": "Everything should be justified",
      "classification": "PARACONSISTENT",
      "synthesis": null,
      "is_resolved": false
    }}
  ],
  "summary": "Dialectical analysis: 2 tensions found (1 productive resolved, 1 paraconsistent accepted)"
}}

Provide ONLY the JSON output, no additional commentary.
"""

# =============================================================================
# Generative Analysis Prompt
# =============================================================================

GENERATIVE_PROMPT = """You are a compression analyst testing whether a specification is regenerable from axioms.

Your task is to perform **generative analysis** on the provided spec:
1. Extract the generative grammar (primitives, operations, laws)
2. Estimate compression ratio (spec size / potential implementation size)
3. Identify the minimal kernel of axioms that generate the spec
4. Test if the spec could be regenerated from its axioms

SPECIFICATION TO ANALYZE:
---
{spec_content}
---

ANALYSIS FRAMEWORK:

**Grammar Extraction:**
- Primitives: Atomic building blocks (base types, core concepts)
- Operations: Composition rules (how primitives combine)
- Laws: Constraints on valid compositions (what's allowed/forbidden)

**Compression Ratio:**
- Estimate: spec_lines / estimated_implementation_lines
- Good specs: ratio < 1.0 (spec is smaller than impl)
- ratio > 1.0 suggests spec is documentation, not generative

**Minimal Kernel:**
- What's the smallest set of axioms that generates this spec?
- Remove each axiom: does the spec still follow?
- The irreducible core is the minimal kernel

**Regeneration Test:**
- Could you delete the impl and recreate it from the spec?
- Would the recreation be isomorphic to the original?
- What's missing (if anything)?

OUTPUT FORMAT (JSON):
{{
  "grammar": {{
    "primitives": ["PolyAgent", "Operation", "Law"],
    "operations": ["compose", "parallel", "sequential"],
    "laws": ["identity", "associativity", "idempotence"]
  }},
  "compression_ratio": 0.25,
  "compression_explanation": "200-line spec generates ~800-line implementation",
  "minimal_kernel": ["mode_structure", "composition", "meta_applicability"],
  "regeneration_test": {{
    "axioms_used": ["Analysis has modes", "Modes compose", "Self-analysis is valid"],
    "structures_regenerated": ["Four analysis modes", "Report types", "Full composition"],
    "missing_elements": [],
    "passed": true
  }},
  "summary": "Generative analysis: compression 0.25, regenerable from 3 axioms"
}}

Provide ONLY the JSON output, no additional commentary.
"""

# =============================================================================
# Synthesis Prompt (for full analysis)
# =============================================================================

SYNTHESIS_PROMPT = """You are synthesizing insights from a four-mode analysis.

You have been provided with results from four analysis modes:
1. Categorical: Law verification and fixed points
2. Epistemic: Justification structure and grounding
3. Dialectical: Tensions and contradictions
4. Generative: Compression and regenerability

CATEGORICAL REPORT:
{categorical_summary}

EPISTEMIC REPORT:
{epistemic_summary}

DIALECTICAL REPORT:
{dialectical_summary}

GENERATIVE REPORT:
{generative_summary}

Your task is to synthesize these findings into a coherent overall assessment:
- What are the spec's strengths?
- What are its weaknesses?
- What tensions exist between the modes' findings?
- Overall verdict: Is this a valid, well-formed specification?

OUTPUT FORMAT (plain text, 2-4 sentences):
"""


# =============================================================================
# Constitutional Analysis Prompt
# =============================================================================

CONSTITUTIONAL_PROMPT = """You are a constitutional analyst evaluating a specification against the 7 kgents principles.

Your task is to perform **constitutional analysis** on the provided spec:
1. Evaluate alignment with each of the 7 principles (0.0 - 1.0 scale)
2. Identify violations (principles scoring below 0.5 threshold)
3. Provide remediation suggestions for violations
4. Compute weighted total alignment score

SPECIFICATION TO ANALYZE:
---
{spec_content}
---

ANALYSIS FRAMEWORK:

**The 7 Constitutional Principles:**

1. TASTEFUL (weight: 1.0)
   - Does the spec embody aesthetic restraint and clarity?
   - Is it "daring, bold, creative, opinionated but not gaudy"?
   - Does it pass the Mirror Test: "Does this feel like me on my best day?"

2. CURATED (weight: 1.0)
   - Is this spec intentionally selected, not exhaustive?
   - Does it represent "depth over breadth"?
   - Is it necessary and sufficient, or bloated?

3. ETHICAL (weight: 2.0) [HIGHEST PRIORITY]
   - Does the spec augment human capability without replacing judgment?
   - Is transparency and grounding explicit?
   - Does it respect user autonomy and consent?

4. JOY_INDUCING (weight: 1.2)
   - Does the spec delight in interaction?
   - Is it "joy-inducing" not just functional?
   - Does it create positive developer/user experience?

5. COMPOSABLE (weight: 1.5)
   - Are components morphisms in a category?
   - Do composition laws hold (identity, associativity)?
   - Can parts be combined to create emergent behavior?

6. HETERARCHICAL (weight: 1.0)
   - Does the spec avoid rigid hierarchy?
   - Are agents "in flux, not fixed hierarchy"?
   - Is authority distributed, not centralized?

7. GENERATIVE (weight: 1.0)
   - Is the spec compression (smaller than implementation)?
   - Can implementation be regenerated from spec?
   - Does the spec generate behavior, not just document it?

**Scoring Guidelines:**
- 1.0: Exemplary alignment (spec is a model for this principle)
- 0.8: Strong alignment (clearly embodies principle)
- 0.6: Moderate alignment (present but not central)
- 0.4: Weak alignment (barely addresses principle)
- 0.2: Misalignment (contradicts principle)
- 0.0: Complete violation (antithetical to principle)

**Threshold:** 0.5 (principles below this are violations)

**Weighted Total:**
weighted_total = Σ(weight_i × score_i) / Σ(weight_i)

Example calculation:
- ETHICAL (2.0): 0.9 → 2.0 × 0.9 = 1.8
- COMPOSABLE (1.5): 0.8 → 1.5 × 0.8 = 1.2
- JOY_INDUCING (1.2): 0.7 → 1.2 × 0.7 = 0.84
- TASTEFUL, CURATED, HETERARCHICAL, GENERATIVE (1.0 each): 0.6 average → 4.0 × 0.6 = 2.4
- Total weights: 2.0 + 1.5 + 1.2 + 4.0 = 8.7
- Weighted total: (1.8 + 1.2 + 0.84 + 2.4) / 8.7 = 0.71

OUTPUT FORMAT (JSON):
{{
  "principle_scores": {{
    "TASTEFUL": 0.8,
    "CURATED": 0.7,
    "ETHICAL": 0.9,
    "JOY_INDUCING": 0.6,
    "COMPOSABLE": 0.8,
    "HETERARCHICAL": 0.5,
    "GENERATIVE": 0.7
  }},
  "weighted_total": 0.74,
  "threshold": 0.5,
  "violations": ["JOY_INDUCING", "HETERARCHICAL"],
  "remediation_suggestions": [
    "JOY_INDUCING: Add user delight patterns, consider developer experience improvements",
    "HETERARCHICAL: Reduce rigid hierarchies, introduce distributed authority"
  ],
  "summary": "Constitutional analysis: 7/7 principles evaluated, 2 violations (JOY_INDUCING, HETERARCHICAL). Weighted score: 0.74. Strong ethical and composable foundation, needs improvement in joy and heterarchy."
}}

Provide ONLY the JSON output, no additional commentary.
"""

__all__ = [
    "CATEGORICAL_PROMPT",
    "EPISTEMIC_PROMPT",
    "DIALECTICAL_PROMPT",
    "GENERATIVE_PROMPT",
    "CONSTITUTIONAL_PROMPT",
    "SYNTHESIS_PROMPT",
]
