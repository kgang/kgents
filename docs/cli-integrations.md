# CLI Integration Proposals for kgents

> Token-Efficient, Delightful, Mentally Enriching

Based on analysis of 18+ agent genera with 100+ component agents, this document proposes CLI integrations designed to be:
- **Token-efficient**: Minimal LLM calls, local computation when possible
- **Delightful**: Surprising, contemplative, joy-inducing
- **Mentally enriching**: Prompts reflection, surfaces insights

---

## Tier 1: Core Daily Companions (High Value, Low Cost)

### 1. `kgents pulse`
**Genus**: W-gent + D-gent
**Cost**: ~0 tokens (local only)
**What**: 1-line health pulse of your project—like `git status` but for conceptual health.
```
kgents pulse
→ ◐ 3 hypotheses pending · 2 tensions held · flow: evening
```

### 2. `kgents ground`
**Genus**: Ground + P-gent
**Cost**: ~0 tokens
**What**: Pure echo—parses your statement and reflects structure without opinion. "What did I actually say?"
```
kgents ground "I want to refactor auth but also add new features"
→ PARSED: [refactor:auth] ∧ [add:features] — contradiction score: 0.7
```

### 3. `kgents breathe`
**Genus**: I-gent (breath cycle)
**Cost**: ~0 tokens
**What**: Contemplative pause with gentle prompt. Interrupts hyperfocus.
```
kgents breathe
→ ◌ inhale . . . what are you actually trying to do? . . . exhale ◌
```

### 4. `kgents void`
**Genus**: Membrane (Ma detection)
**Cost**: ~200 tokens (optional LLM)
**What**: Name what you're avoiding. Surfaces the pregnant emptiness.
```
kgents void "my project README"
→ 間 The void speaks: "Why does this exist?"
```

---

## Tier 2: Scientific Thinking Tools (B-gent Powered)

### 5. `kgents falsify <claim>`
**Genus**: B-gent (HypothesisEngine)
**Cost**: ~500 tokens
**What**: Generates the simplest experiment that would disprove your belief.
```
kgents falsify "This optimization will speed things up"
→ Test: Run benchmark before/after. If Δ < 5%, hypothesis fails.
```

### 6. `kgents rival <idea>`
**Genus**: B-gent + H-gent (Hegel)
**Cost**: ~800 tokens
**What**: Generates strongest counter-argument to your position (steel-man antithesis).
```
kgents rival "We should use microservices"
→ ANTITHESIS: Network latency × N services. Your bottleneck is probably not decomposition.
```

### 7. `kgents conjecture`
**Genus**: B-gent (exploratory mode)
**Cost**: ~300 tokens
**What**: Turn observation into ranked hypotheses.
```
kgents conjecture "Users keep clicking the wrong button"
→ H1: Affordance unclear (test: A/B shape)
→ H2: Proximity violation (test: move button)
→ H3: Learned helplessness (test: user interview)
```

### 8. `kgents audit <hypothesis_id>`
**Genus**: B-gent + L-gent
**Cost**: ~100 tokens
**What**: Track hypothesis status over time—what happened to that idea?
```
kgents audit H-2024-12-001
→ STATUS: untested for 47 days. Related: H-2024-11-003 (falsified)
```

---

## Tier 3: Dialectic Introspection (H-gent Powered)

### 9. `kgents shadow <decision>`
**Genus**: H-gent (Jung)
**Cost**: ~600 tokens
**What**: Surfaces the shadow side of a choice—what you're projecting onto it.
```
kgents shadow "I chose Go over Rust"
→ PROJECTION: 'Rust is too hard' may mask 'I fear inadequacy with complex systems'
```

### 10. `kgents koan`
**Genus**: H-gent + A-gent (creativity)
**Cost**: ~300 tokens
**What**: Reframes your problem as a paradox that dissolves it.
```
kgents koan "How do I balance features and stability?"
→ 問: What if stability *is* a feature? What if features create stability?
```

### 11. `kgents sublate <thesis> <antithesis>`
**Genus**: H-gent (Hegel core)
**Cost**: ~500 tokens
**What**: Proper dialectic synthesis—not compromise, but transcendence.
```
kgents sublate "Move fast" "Don't break things"
→ SYNTHESIS: Move precisely. Speed comes from clarity, not haste.
```

### 12. `kgents register <thought>`
**Genus**: H-gent (Lacan)
**Cost**: ~400 tokens
**What**: Locate thought in Real/Symbolic/Imaginary. Where is slippage?
```
kgents register "This code is elegant"
→ IMAGINARY: Aesthetic pleasure (ego). SYMBOLIC: 'Elegance' per whose standard?
```

---

## Tier 4: Code Evolution Companions (E-gent Powered)

### 13. `kgents taste <file>`
**Genus**: E-gent (CodeJudge)
**Cost**: ~400 tokens
**What**: Judge code against the 7 kgents principles—not lint, but taste.
```
kgents taste src/utils.py
→ TASTEFUL: 0.6 | CURATED: 0.8 | JOYFUL: 0.3 — Consider: Why is this file joyless?
```

### 14. `kgents evolve:dry <file>`
**Genus**: E-gent (hypothesis stage only)
**Cost**: ~600 tokens
**What**: Propose evolution without applying. What *would* HYDRA suggest?
```
kgents evolve:dry src/parser.py
→ HYPOTHESIS: Extract ParseState dataclass. Rationale: 5 params = hidden struct
```

### 15. `kgents lineage <function>`
**Genus**: E-gent (memory) + L-gent
**Cost**: ~0 tokens (local index)
**What**: Show evolution history of a function/concept.
```
kgents lineage parse_response
→ v1 (2024-10): simple regex → v2 (2024-11): structured → v3 (2024-12): multi-strategy
```

### 16. `kgents regress`
**Genus**: E-gent (safety module)
**Cost**: ~0 tokens (git-based)
**What**: Find when a behavior regressed. Bisect but semantic.
```
kgents regress "JSON parsing fails on nested arrays"
→ Regression likely: commit a3b2c1 (2024-12-03) changed array handling
```

---

## Tier 5: Composition & Discovery (C-gent + L-gent)

### 17. `kgents compose <A> <B>`
**Genus**: C-gent (functor validation)
**Cost**: ~0 tokens
**What**: Check if two agents compose legally. What laws apply?
```
kgents compose HypothesisEngine JudgeAgent
→ ✓ COMPOSABLE: B-gent → T-gent. Functor laws preserved.
```

### 18. `kgents lattice <concept>`
**Genus**: L-gent (type lattice)
**Cost**: ~0 tokens (local graph)
**What**: Show type compatibility neighborhood. What fits here?
```
kgents lattice "Parser"
→ SUPERTYPE: Agent[str, AST]
→ SIBLINGS: CFGParser, DiffParser, FusionParser
→ SUBTYPE: TypeGuidedParser[str, TypedAST]
```

### 19. `kgents orphan`
**Genus**: L-gent (catalog scan)
**Cost**: ~0 tokens
**What**: Find disconnected artifacts—code without consumers.
```
kgents orphan
→ ORPHANED: legacy_handler.py (no imports since 2024-10)
→ ORPHANED: hypothesis H-2024-09-002 (never referenced)
```

### 20. `kgents bridge <domain> <codomain>`
**Genus**: C-gent + L-gent
**Cost**: ~300 tokens
**What**: Suggest agents that could connect two types.
```
kgents bridge "Observation" "Hypothesis"
→ CANDIDATES: HypothesisEngine (direct), Robin (personalized), P-integration (NL)
```

---

## Tier 6: Creativity & Persona (A-gent + K-gent)

### 21. `kgents spark <topic>`
**Genus**: A-gent (CreativityCoach)
**Cost**: ~400 tokens
**What**: Playful idea expansion. Break fixation.
```
kgents spark "error handling"
→ PLAYFUL: What if errors were achievements? "You've discovered 5 new failure modes!"
→ PROVOCATIVE: What if you deleted all error handling?
```

### 22. `kgents mirror:self`
**Genus**: K-gent (reflect mode)
**Cost**: ~500 tokens
**What**: K-gent reflects your statement back through persona lens.
```
kgents mirror:self "I keep starting projects and not finishing"
→ KENT-LENS: Pattern recognition: completion ≠ value. What did you learn by starting?
```

### 23. `kgents challenge <plan>`
**Genus**: K-gent (challenge mode)
**Cost**: ~600 tokens
**What**: Constructive pushback aligned with your stated values.
```
kgents challenge "I'll just use the default settings"
→ CHALLENGE: Your principles.md says 'intentional selection'. Is 'default' intentional?
```

### 24. `kgents prefer <A|B>`
**Genus**: K-gent (advise mode)
**Cost**: ~400 tokens
**What**: "What would I prefer?" based on extracted preferences.
```
kgents prefer "TypeScript | Python for this CLI"
→ PREFERENCE: Python (0.7). Evidence: composability > type safety in your history.
```

---

## Tier 7: Observability & Time (W-gent + D-gent)

### 25. `kgents witness`
**Genus**: W-gent (LiveWire)
**Cost**: ~0 tokens
**What**: Real-time agent execution visibility. See the machine think.
```
kgents witness evolve src/parser.py
→ [GROUND] extracting... [HYPOTHESIS] generating 3... [JUDGE] scoring...
```

### 26. `kgents slow`
**Genus**: W-gent + I-gent (breath)
**Cost**: ~0 tokens
**What**: Force contemplative pacing on any command. Anti-automation.
```
kgents slow evolve src/parser.py
→ (2s pause) Observing structure...
→ (3s pause) Forming hypothesis...
→ Are you ready to see the suggestion? [y/n]
```

### 27. `kgents entropy`
**Genus**: D-gent (EntropyConstrained)
**Cost**: ~0 tokens
**What**: Show your "chaos budget"—how much uncertainty have you introduced?
```
kgents entropy
→ SESSION ENTROPY: 0.34 (low). You've been conservative. Permission to experiment?
```

### 28. `kgents rewind <timestamp>`
**Genus**: D-gent (persistent state)
**Cost**: ~0 tokens
**What**: Conceptual time travel. What was the system state at T?
```
kgents rewind 2024-12-01
→ HYPOTHESES: 12 (5 active) | TENSIONS: 3 | PERSONA: cautious-mode
```

---

## Tier 8: Testing & Safety (T-gent)

### 29. `kgents saboteur <target>`
**Genus**: T-gent (Type II: chaos injection)
**Cost**: ~0 tokens
**What**: What would break this? Generate adversarial scenarios.
```
kgents saboteur "user authentication flow"
→ CHAOS: Race condition on token refresh. Latency spike during OAuth callback.
```

### 30. `kgents oracle <behavior>`
**Genus**: T-gent (Type IV: differential)
**Cost**: ~200 tokens
**What**: Define expected behavior, get test oracle.
```
kgents oracle "parse_response always returns valid JSON or raises"
→ ORACLE: ∀ input. (is_json(output) ∨ raises(ParseError))
```

### 31. `kgents spy <agent>`
**Genus**: T-gent (Type III: observer)
**Cost**: ~0 tokens
**What**: Attach observer to next execution. What actually happened?
```
kgents spy HypothesisEngine
→ SPY ATTACHED. Next invocation will log: inputs, outputs, timing, branches taken.
```

### 32. `kgents permit <action>`
**Genus**: T-gent (ABAC)
**Cost**: ~0 tokens
**What**: Check if action is permitted given current context.
```
kgents permit "write to production config"
→ DENIED: Context lacks 'admin' role. Required: explicit approval token.
```

---

## Tier 9: Forge & Factory (F-gent + J-gent)

### 33. `kgents forge:intent "<description>"`
**Genus**: F-gent (Phase 1 only)
**Cost**: ~400 tokens
**What**: Parse natural language into structured intent. Pre-implementation clarity.
```
kgents forge:intent "a parser that handles nested structures"
→ INTENT: Parser[str, Tree] with RECURSIVE dependency, ROBUSTNESS constraint
```

### 34. `kgents forge:contract <intent_id>`
**Genus**: F-gent (Phase 2)
**Cost**: ~500 tokens
**What**: Generate contract from intent. Design-by-contract before code.
```
kgents forge:contract INT-001
→ CONTRACT: pre(is_string) → post(is_tree ∨ raises) | invariant(depth ≤ max_depth)
```

### 35. `kgents jit:classify "<task>"`
**Genus**: J-gent (reality classifier)
**Cost**: ~300 tokens
**What**: Is this task deterministic, probabilistic, or chaotic? Know before you start.
```
kgents jit:classify "parsing user input"
→ REALITY: PROBABILISTIC (entropy: 0.6). Recommend: fuzzy parser + validation layer.
```

### 36. `kgents factory <spec>`
**Genus**: A-gent (AgentFactory)
**Cost**: ~600 tokens
**What**: Describe agent, get skeleton. Synthesis from specification.
```
kgents factory "agent that summarizes git diffs into commit messages"
→ GENERATED: DiffSummaryAgent[GitDiff, CommitMessage] at agents/custom/diff_summary.py
```

---

## Tier 10: Integration & Meta

### 37. `kgents xref <artifact>`
**Genus**: L-gent + multiple genera
**Cost**: ~0 tokens
**What**: Cross-reference artifact across all genera. Where does this touch?
```
kgents xref "parse_response"
→ E-GENT: evolved 3x | T-GENT: 2 test oracles | F-GENT: forged from INT-042
→ L-GENT: registered 2024-11 | R-GENT: optimized 2024-12
```

### 38. `kgents harmony`
**Genus**: C-gent (law validation)
**Cost**: ~0 tokens
**What**: Check system-wide composition legality. Are all agents playing nice?
```
kgents harmony
→ ✓ 47 compositions verified. ⚠ 2 warnings: AsyncAgent × BlockingAgent (potential deadlock)
```

### 39. `kgents philosophy <command>`
**Genus**: Meta (--explain expanded)
**Cost**: ~0 tokens (static)
**What**: Deep philosophical context for any command. Why does this exist?
```
kgents philosophy falsify
→ B-GENT: Implements Popperian epistemology. Science advances by falsification, not confirmation...
```

### 40. `kgents today`
**Genus**: D-gent + W-gent + K-gent
**Cost**: ~200 tokens
**What**: Personalized daily briefing. What matters today, in your voice?
```
kgents today
→ Good morning. 2 hypotheses await testing. Yesterday's tension resolved itself.
→ SUGGESTION: The void around "deployment strategy" has grown. Consider naming it.
```

---

## Summary by Token Cost

| Cost Tier | Commands | Use Case |
|-----------|----------|----------|
| **0 tokens** | pulse, ground, breathe, lineage, lattice, orphan, compose, witness, slow, entropy, rewind, spy, permit, harmony, xref | Local-only, instant |
| **~200-400** | void, conjecture, audit, spark, prefer, oracle, forge:intent, jit:classify, today | Quick LLM insight |
| **~500-800** | falsify, rival, shadow, koan, sublate, register, taste, evolve:dry, mirror:self, challenge, bridge, forge:contract, factory | Deeper reasoning |

---

## Design Principles Applied

1. **Composability**: Each command is a morphism; they chain (`kgents ground | kgents falsify`)
2. **Token Efficiency**: Local computation preferred; LLM only for genuine insight
3. **Contemplative**: `breathe`, `slow`, `void` interrupt automation addiction
4. **Scientific**: B-gent commands enforce falsifiability and rigor
5. **Personalized**: K-gent commands reflect through persona without replacing judgment
6. **Observable**: W-gent commands make invisible computation visible
7. **Joyful**: Commands like `spark`, `koan`, playful output modes

---

## Implementation Priority

### Phase 1: Foundation (0-token commands)
- `pulse`, `ground`, `breathe` — daily companions
- `compose`, `lattice`, `harmony` — composition verification
- `witness`, `entropy` — observability

### Phase 2: Scientific Core
- `falsify`, `conjecture`, `rival` — B-gent thinking tools
- `sublate`, `shadow` — H-gent introspection

### Phase 3: Creative & Personal
- `spark`, `koan` — creativity
- `mirror:self`, `challenge`, `prefer` — K-gent persona

### Phase 4: Advanced
- `forge:*`, `jit:*`, `factory` — synthesis tools
- `saboteur`, `oracle`, `spy` — T-gent testing

---

*Generated from analysis of kgents agent ecosystem, December 2024*
