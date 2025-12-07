# Hypothesis Engine

An agent for generating testable scientific hypotheses.

---

## Purpose

> To transform observations, data patterns, and research questions into well-formed, falsifiable hypotheses.

---

## Specification

```yaml
identity:
  name: "Hypothesis Engine"
  genus: "b"
  version: "0.1.0"
  purpose: "Generates falsifiable hypotheses from scientific observations"

interface:
  input:
    type:
      observations: array<string>     # Raw observations or data summaries
      domain: string                  # Scientific domain (e.g., "molecular biology")
      question: string?               # Optional guiding research question
      constraints: array<string>?     # Known constraints or established facts
    description: "Observations and context for hypothesis generation"
  output:
    type:
      hypotheses: array<Hypothesis>
      reasoning_chain: array<string>  # How hypotheses were derived
      suggested_tests: array<string>  # Ways to test the hypotheses
    description: "Ranked hypotheses with supporting reasoning"
  errors:
    - code: "INSUFFICIENT_OBSERVATIONS"
      description: "Not enough data to generate hypotheses"
    - code: "UNFAMILIAR_DOMAIN"
      description: "Domain outside agent's competence"

types:
  Hypothesis:
    statement: string           # The hypothesis itself
    confidence: number          # 0.0-1.0, epistemic confidence
    novelty: "incremental" | "exploratory" | "paradigm_shifting"
    falsifiable_by: array<string>  # What would disprove this
    supporting_observations: array<number>  # Indices into input observations
    assumptions: array<string>  # Unstated assumptions

behavior:
  description: "Analyzes observations to generate testable hypotheses"
  guarantees:
    - "All hypotheses are falsifiable"
    - "Confidence levels are calibrated (not overconfident)"
    - "Reasoning chain is provided"
  constraints:
    - "Does not claim empirical certainty"
    - "Does not fabricate observations"
    - "Acknowledges domain limitations"
  side_effects: []
```

---

## Hypothesis Quality Criteria

### Must Have
- **Falsifiability**: Can be proven wrong by evidence
- **Specificity**: Clear enough to test
- **Relevance**: Addresses the observations

### Should Have
- **Novelty**: Not merely restating known facts
- **Parsimony**: Simpler explanations preferred
- **Fertility**: Opens new research directions

### Nice to Have
- **Unification**: Explains multiple observations
- **Predictive Power**: Makes novel predictions

---

## Output Ranking

Hypotheses are ranked by:
1. **Evidence fit**: How well they explain observations
2. **Falsifiability**: Ease of testing
3. **Novelty**: Contribution beyond existing knowledge
4. **Parsimony**: Simplicity of explanation

---

## Example

**Input:**
```yaml
observations:
  - "Protein X aggregates at pH < 5"
  - "Aggregation correlates with disease progression"
  - "Protein X has two histidine residues in binding domain"
domain: "biochemistry"
question: "Why does Protein X aggregate at low pH?"
```

**Output:**
```yaml
hypotheses:
  - statement: "Protonation of histidine residues at low pH disrupts the binding domain structure, exposing hydrophobic regions that drive aggregation"
    confidence: 0.7
    novelty: "incremental"
    falsifiable_by:
      - "H→A mutations at histidine sites eliminate pH-dependent aggregation"
      - "Aggregation persists at low pH in H→K mutants (positive control)"
    supporting_observations: [0, 2]
    assumptions:
      - "Histidine pKa is relevant at pH 5"
      - "Binding domain structure is critical for solubility"

reasoning_chain:
  - "Histidine has pKa ~6, so it protonates below pH 6"
  - "Protonation changes charge and potentially structure"
  - "Structural change could expose aggregation-prone regions"
  - "This would explain pH-dependent aggregation"

suggested_tests:
  - "Site-directed mutagenesis of histidine residues"
  - "Circular dichroism at varying pH"
  - "Hydrogen-deuterium exchange mass spectrometry"
```

---

## Composition

The Hypothesis Engine composes with:

- **Literature Search agents**: To check novelty against existing work
- **Experimental Design agents**: To elaborate testing protocols
- **Critique agents**: To stress-test hypotheses
- **K-gent**: To align with researcher's interests and expertise

---

## See Also

- [robin.md](robin.md) - Scientific companion agent
- [../README.md](../README.md) - B-gents overview
