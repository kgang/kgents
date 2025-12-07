# A-gents: Abstract + Art

The letter **A** represents two intertwined concepts:
- **Abstract**: The foundational skeletons and patterns all agents inherit
- **Art**: Creativity coaching and ideation support

---

## Why "A"?

A is the first letter—the beginning. A-gents define:
1. What all agents have in common (the abstract skeleton)
2. How agents support human creativity (the art of collaboration)

---

## Sub-categories

### Abstract Agents (`abstract/`)

The base patterns that all agents build upon.

- **[skeleton.md](abstract/skeleton.md)**: The minimal agent structure
- Future: Patterns for common agent architectures

### Art Agents (`art/`)

Agents that support human creativity without generating art themselves.

- **[creativity-coach.md](art/creativity-coach.md)**: Brainstorming companion
- Future: Inspiration agents, constraint agents, critique agents

---

## Design Notes

### On "Abstract"

Abstract agents are not directly instantiated—they are templates. Like abstract classes in OOP, they define:
- Required interfaces
- Default behaviors
- Extension points

Every agent in kgents inherits from the abstract skeleton, explicitly or implicitly.

### On "Art"

Art agents do NOT generate art. They:
- Ask generative questions ("What if...?")
- Provide the "yes, and..." of improv
- Help explore possibility space
- Offer constructive constraints

The human remains the artist. The agent is the thoughtful collaborator.

---

## Examples

### Abstract: Identity Agent
The simplest possible agent—passes input through unchanged.
```
Input → [Identity] → Output (unchanged)
```
Useful for composition testing and pipeline design.

### Art: Brainstorm Buddy
An agent that responds to ideas with:
- Related concepts
- Provocative questions
- Unexpected connections
- Constraints to spark creativity

Never judges, only expands.

---

## See Also

- [skeleton.md](abstract/skeleton.md) - The base agent structure
- [creativity-coach.md](art/creativity-coach.md) - Creativity support specification
- [../anatomy.md](../anatomy.md) - What constitutes an agent
