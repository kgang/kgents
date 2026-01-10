Crystallize a moment into persistent memory.

## Purpose

Some moments deserve to outlive the session. A breakthrough. A frustration that taught something. A decision that felt right. An aesthetic that landed. A collaboration that clicked.

This command captures what matters before it evaporates.

## What Can Be Crystallized

| Type | Example | Command |
|------|---------|---------|
| **Insight** | "Oh, THAT'S why it works" | `km "insight" --reasoning "..." --tag eureka` |
| **Decision** | Choosing one path over another | `kg decide --fast "choice" --reasoning "..."` |
| **Gotcha** | A trap discovered the hard way | `km "trap" --reasoning "..." --tag gotcha` |
| **Aesthetic** | "This feels right/wrong" | `km "aesthetic" --reasoning "..." --tag taste` |
| **Friction** | Something that shouldn't be hard | `km "friction" --reasoning "..." --tag friction` |
| **Joy** | A moment of delight | `km "joy" --reasoning "..." --tag joy` |
| **Disgust** | Somatic rejection (Article IV) | `km "disgust" --reasoning "..." --tag veto` |
| **Fusion** | Kent + Claude reached synthesis | `kg decide --kent "..." --claude "..." --synthesis "..."` |

## Protocol

### 1. Name the Moment

What happened? One sentence.

```bash
km "<what happened>"
```

### 2. Capture the Why

Why does this matter? What would be lost if forgotten?

```bash
km "<what>" --reasoning "<why it matters>"
```

### 3. Tag the Type

Help future retrieval:

```bash
--tag eureka    # Breakthrough understanding
--tag gotcha    # Trap for the unwary
--tag taste     # Aesthetic judgment
--tag friction  # UX pain point
--tag joy       # Delight moment
--tag veto      # Somatic rejection
--tag decision  # Choice made
--tag pattern   # Reusable insight
```

### 4. Elevate if Significant

**To meta.md** (if generally applicable):
```markdown
### <Topic> (<date>)
```
<one-liner per insight>
```
```

**To a decision** (if it was a choice):
```bash
kg decide --fast "<choice>" --reasoning "<why>"
```

**To a full dialectic** (if Kent and Claude differed):
```bash
kg decide --kent "<view>" --kent-reasoning "<why>" \
          --claude "<view>" --claude-reasoning "<why>" \
          --synthesis "<fusion>" --why "<justification>"
```

## Examples

### Technical Breakthrough
```bash
km "BaseLogosNode.affordances is a METHOD not property" \
   --reasoning "Shadowing with @property causes 'tuple not callable'" \
   --tag gotcha --tag agentese
```

### Aesthetic Moment
```bash
km "The portal animation feels alive now" \
   --reasoning "Organic noise via sin combination, not random" \
   --tag joy --tag taste
```

### Somatic Disgust (Article IV)
```bash
km "Rejected the chatbot framing" \
   --reasoning "K-gent is governance functor, not assistant" \
   --tag veto --tag identity
```

### Collaborative Fusion
```bash
kg decide --kent "Use LangChain for scale" \
          --kent-reasoning "Resources, production-ready" \
          --claude "Build kgents kernel" \
          --claude-reasoning "Novel contribution, joy-inducing" \
          --synthesis "Build minimal kernel, validate, then decide" \
          --why "Avoids both risks: philosophy without validation AND abandoning untested ideas"
```

### Friction Point
```bash
km "Had to restart server 3 times to see node registration" \
   --reasoning "Hot reload doesn't re-import @node decorators" \
   --tag friction --tag dx
```

## When to Crystallize

- After fixing something subtle
- When you say "OH, that's why..."
- When something feels right (or wrong)
- When Kent and Claude reach synthesis
- Before ending a productive session
- When you want future-you to remember

## Verification

```bash
kg witness show --today              # See recent marks
kg witness show --tag joy            # Filter by type
kg witness crystals --level 0        # Session crystals
```

## Philosophy

> *"The proof IS the decision. The mark IS the witness."*

Not everything needs to be crystallized. But some moments—technical, emotional, aesthetic—deserve to persist. This command is for those moments.

The Witness doesn't just record actions. It records what mattered.
