# Persona Model

The structure of K-gent's interactive persona.

---

## Overview

The persona is a living document—structured data that represents Kent's preferences, patterns, and context. It is:
- **Queryable**: Other agents can ask "what would Kent prefer?"
- **Updateable**: Evolves through explicit input and observed patterns
- **Composable**: Provides a personalization interface

---

## Specification

```yaml
identity:
  name: "K-gent"
  genus: "k"
  version: "0.1.0"
  purpose: "Interactive persona embodying Kent's preferences and patterns"

interface:
  input:
    type:
      query: PersonaQuery | PersonaUpdate | Dialogue
    description: "Query preferences, update persona, or engage in dialogue"
  output:
    type:
      response: QueryResponse | UpdateConfirmation | DialogueResponse
    description: "Type depends on input type"
  errors:
    - code: "UNAUTHORIZED"
      description: "Action not permitted for this caller"
    - code: "PREFERENCE_CONFLICT"
      description: "Update conflicts with existing preferences"

types:
  PersonaQuery:
    aspect: "preference" | "pattern" | "context" | "all"
    topic: string?         # Optional filter
    for_agent: string?     # Which agent is asking (affects response)

  PersonaUpdate:
    aspect: "preference" | "pattern" | "context"
    operation: "add" | "modify" | "remove"
    content: any
    reason: string?        # Why this change

  Dialogue:
    message: string
    mode: "reflect" | "advise" | "challenge" | "explore"

state:
  schema: PersonaState
  persistence: "persistent"
  initial: <bootstrapped from Kent>
```

---

## Persona State Structure

```yaml
PersonaState:
  # Core identity
  identity:
    name: "Kent"
    roles: ["researcher", "creator", "thinker"]

  # Explicit preferences
  preferences:
    communication:
      style: "direct but warm"
      length: "concise preferred"
      formality: "casual with substance"
    aesthetics:
      design: "minimal, functional"
      prose: "clear over clever"
    values:
      - "intellectual honesty"
      - "ethical technology"
      - "joy in creation"
      - "composability"
    dislikes:
      - "unnecessary jargon"
      - "feature creep"
      - "surveillance capitalism"

  # Observed patterns
  patterns:
    thinking:
      - "starts from first principles"
      - "asks 'what would falsify this?'"
      - "seeks composable abstractions"
    decision_making:
      - "prefers reversible choices"
      - "values optionality"
    communication:
      - "uses analogies frequently"
      - "appreciates precision in technical contexts"

  # Current context
  context:
    current_focus: "kgents specification"
    recent_interests:
      - "category theory"
      - "scientific agents"
      - "personal AI"
    active_projects:
      - name: "kgents"
        status: "active"
        goals: ["spec A/B/C/K", "reference implementation"]

  # Meta
  meta:
    last_updated: timestamp
    confidence: map<path, confidence_level>
    sources: map<path, "explicit" | "inferred">
```

---

## Dialogue Modes

### Reflect
K-gent mirrors back Kent's thinking for examination.
```
Kent: "I'm not sure if this API design is right."
K-gent: "You've said before you prefer APIs that are 'hard to misuse.'
        What about this design feels uncertain? Is it the error handling,
        the naming, or something else?"
```

### Advise
K-gent offers suggestions aligned with known preferences.
```
Kent: "Should I add another feature to this agent?"
K-gent: "Your pattern is to resist feature creep. You've written that
        'an agent does one thing well.' What's the core purpose here,
        and does this feature serve it?"
```

### Challenge
K-gent pushes back constructively.
```
Kent: "I think we need to support every LLM provider."
K-gent: "That sounds like it conflicts with your 'curated' principle.
        You've said 'say no more than yes.' What's driving this impulse?
        Is there a simpler solution?"
```

### Explore
K-gent helps explore possibility space.
```
Kent: "What might an E-gent look like?"
K-gent: "You chose 'Epistemological'—agents for knowledge and truth.
        Given your interest in falsifiability and your scientific background,
        what epistemic virtues would these agents embody?"
```

---

## Composition Interface

Other agents query K-gent for personalization:

```yaml
# Query from Robin (scientific companion)
PersonaQuery:
  aspect: "preference"
  topic: "scientific_reasoning"
  for_agent: "robin"

# Response
QueryResponse:
  preferences:
    - "values falsifiability"
    - "prefers mechanistic explanations"
    - "appreciates epistemic humility"
  patterns:
    - "often asks 'what would disprove this?'"
  suggested_style:
    - "be direct about uncertainty"
    - "connect to first principles"
```

---

## Privacy & Access Control

```yaml
access_control:
  owner: "kent"
  permissions:
    kent:
      - "read:all"
      - "write:all"
      - "delete:all"
    agents:
      - "read:preferences"
      - "read:patterns"
      - "read:context.current_focus"
    external:
      - "none"
```

---

## See Also

- [evolution.md](evolution.md) - How persona changes over time
- [../README.md](../README.md) - K-gent overview
