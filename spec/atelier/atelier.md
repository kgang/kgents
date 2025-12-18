---
domain: world
holon: atelier
polynomial:
  positions:
    - gathering
    - creating
    - reviewing
    - exhibiting
    - closed
  transition: workshop_transition
  directions: workshop_directions
operad:
  extends: AGENT_OPERAD
  operations:
    join:
      arity: 1
      signature: "Artisan -> Workshop"
      description: "Artisan joins the workshop"
    contribute:
      arity: 2
      signature: "(Artisan, Workshop) -> Contribution"
      description: "Submit creative contribution to workshop"
    refine:
      arity: 2
      signature: "(Contribution, Artisan) -> RefinedContribution"
      description: "Refine an existing contribution"
    exhibit:
      arity: 1
      signature: "Workshop -> Exhibition"
      description: "Create exhibition from workshop contributions"
    open_exhibition:
      arity: 1
      signature: "Exhibition -> OpenExhibition"
      description: "Open exhibition to public viewing"
    view:
      arity: 2
      signature: "(Observer, Exhibition) -> Experience"
      description: "Observer views exhibition"
    curate:
      arity: 2
      signature: "(Curator, [Contribution]) -> [SelectedContribution]"
      description: "Curator selects contributions for exhibition"
    close:
      arity: 1
      signature: "Workshop -> ClosedWorkshop"
      description: "Close the workshop (terminal operation)"
  laws:
    join_before_contribute: "contribute(a, w) requires joined(a, w)"
    refine_requires_contribution: "refine(c, r) requires exists(c)"
    exhibit_requires_work: "exhibit(w) requires contributions(w) > 0"
    closed_is_terminal: "closed(w) implies no further operations on w"
    refinement_attribution: "refine(c, r).author = c.author"
agentese:
  path: world.atelier
  aspects:
    - manifest
    - workshops
    - workshop.create
    - workshop.join
    - workshop.contribute
    - workshop.refine
    - exhibition.create
    - exhibition.open
    - exhibition.view
---

# Atelier Agent Specification

> *"The workshop is a fishbowl. Spectators observe the creative process."*

The Atelier Crown Jewel models creative workshops where artisans collaborate to produce and exhibit creative works. Inspired by Punchdrunk's immersive theater philosophy.

## Categorical Structure

### Polynomial (WorkshopPolynomial)

Workshops exist in 5 lifecycle phases:

| Position | Description | Valid Transitions |
|----------|-------------|-------------------|
| GATHERING | Setup, artisans joining | -> CREATING (first contribution) |
| CREATING | Active creative work | -> REVIEWING, EXHIBITING |
| REVIEWING | Work being refined | -> CREATING, EXHIBITING |
| EXHIBITING | Exhibition open | -> CLOSED |
| CLOSED | Workshop archived | Terminal |

**Key Property**: CLOSED is terminal. Workshops are ephemeral creative spaces that cannot reopen.

### Operad (ATELIER_OPERAD)

The operad defines the grammar of valid workshop operations:

**Participation**: `join`
**Creation**: `contribute`, `refine`
**Exhibition**: `exhibit`, `open_exhibition`, `view`, `curate`
**Lifecycle**: `close`

**Laws**:
- `join_before_contribute`: Must join before contributing
- `refine_requires_contribution`: Can only refine existing contributions
- `exhibit_requires_work`: Exhibition requires at least one contribution
- `closed_is_terminal`: Closed workshops cannot reopen
- `refinement_attribution`: Refinement preserves original attribution

## AGENTESE Interface

```
world.atelier.manifest          - Workshop service status
world.atelier.workshops         - List workshops
world.atelier.workshop.create   - Create new workshop
world.atelier.workshop.join     - Join workshop as artisan
world.atelier.workshop.contribute - Submit contribution
world.atelier.workshop.refine   - Refine contribution
world.atelier.exhibition.create - Create exhibition
world.atelier.exhibition.open   - Open exhibition to public
world.atelier.exhibition.view   - View exhibition
```

## Implementation

- **Polynomial**: `impl/claude/agents/atelier/polynomial.py`
- **Operad**: `impl/claude/agents/atelier/operad.py`
- **Node**: `impl/claude/services/atelier/node.py`

---

*Canonical spec derived from implementation reflection. Last verified: 2025-12-18*
