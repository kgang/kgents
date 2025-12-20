# Architectural Decisions

> *Binding decisions that shape implementation across kgents. These accumulate from session learnings.*

---

## Quick Reference

| AD | Name | Date | Core Insight |
|----|------|------|--------------|
| [AD-001](AD-001-universal-functor.md) | Universal Functor Mandate | 2025-12-12 | All agent transformations derive from UniversalFunctor |
| [AD-002](AD-002-polynomial.md) | Polynomial Generalization | 2025-12-13 | Agents generalize to PolyAgent[S,A,B] for state-dependent behavior |
| [AD-003](AD-003-generative-over-enumerative.md) | Generative Over Enumerative | 2025-12-13 | Define operads that generate instances, not lists |
| [AD-004](AD-004-precomputed-richness.md) | Pre-Computed Richness | 2025-12-13 | Demo data uses pre-computed LLM outputs, not stubs |
| [AD-005](AD-005-self-similar-lifecycle.md) | Self-Similar Lifecycle | 2025-12-13 | 11-phase development cycle with category laws |
| [AD-006](AD-006-unified-categorical.md) | Unified Categorical Foundation | 2025-12-14 | All domains instantiate PolyAgent + Operad + Sheaf |
| [AD-007](AD-007-liturgical-cli.md) | Liturgical CLI | 2025-12-14 | CLI as AGENTESE context navigator, not command executor |
| [AD-008](AD-008-simplifying-isomorphisms.md) | Simplifying Isomorphisms | 2025-12-16 | Extract named dimensions from repeated conditionals |
| [AD-009](AD-009-metaphysical-fullstack.md) | Metaphysical Fullstack Agent | 2025-12-17 | Every agent is a vertical slice; adapters in services |
| [AD-010](AD-010-habitat-guarantee.md) | The Habitat Guarantee | 2025-12-18 | Every AGENTESE path projects into a Habitat experience |
| [AD-011](AD-011-registry-single-source.md) | Registry as Single Source of Truth | 2025-12-19 | @node registry is truth; frontend/CLI derive from it |
| [AD-012](AD-012-aspect-projection.md) | Aspect Projection Protocol | 2025-12-19 | Paths are places; aspects are actions |
| [AD-013](AD-013-form-polynomial.md) | Form as Polynomial Functor | 2025-12-19 | Complex forms modeled as state machines |

---

## By Category

### Categorical Foundation
- **AD-001**: Universal Functor Mandate
- **AD-002**: Polynomial Generalization
- **AD-006**: Unified Categorical Foundation

### Design Philosophy
- **AD-003**: Generative Over Enumerative
- **AD-004**: Pre-Computed Richness
- **AD-008**: Simplifying Isomorphisms

### Architecture
- **AD-005**: Self-Similar Lifecycle (N-Phase)
- **AD-009**: Metaphysical Fullstack Agent

### Protocol & Navigation
- **AD-007**: Liturgical CLI
- **AD-010**: The Habitat Guarantee
- **AD-011**: Registry as Single Source of Truth
- **AD-012**: Aspect Projection Protocol

### UI & Forms
- **AD-013**: Form as Polynomial Functor

---

## Reading Guide

| If you're... | Read these ADs |
|--------------|----------------|
| Building a new agent | AD-002, AD-006, AD-009 |
| Working on AGENTESE | AD-010, AD-011, AD-012 |
| Designing UI | AD-008, AD-013 |
| Debugging | AD-001, AD-011 |
| Philosophizing | AD-003, AD-005, AD-006 |

---

*Each AD file contains: Context, Decision, Consequences, Anti-patterns, Implementation references.*
