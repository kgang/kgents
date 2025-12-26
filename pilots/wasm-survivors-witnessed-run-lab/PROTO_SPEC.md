# Wasm Survivors: Witnessed Run Lab

Status: proto-spec

> *"The run is the proof. The build is the claim. The ghost is the road not taken."*

## Narrative
A chaotic arcade loop becomes a proof engine. Every micro-decision is justified, every run is a trace, every build becomes a crystallized style claim. The system witnesses at the speed of play—fast inputs, faster proofs.

## Personality Tag
*This pilot believes failure is the clearest signal. Chaos is structure when witnessed.*

## Objectives
- Convert moment-to-moment play into a legible trail of justified decisions **without reducing speed or joy**—the loop must feel *faster* because indecision dissolves.
- Make build coherence measurable and visible as an explicit epistemic artifact: playstyle becomes identity, not accident.
- Produce a per-run crystal that reads as a short proof of *why* the run mattered—not a highlight reel, but a claim about who you are as a player.

## Epistemic Commitments
- **Action → Mark → Trace → Crystal** is the non-negotiable spine. Every run writes a proof.
- Marks encode reason, principle weights, and context (combat state, risk level, tempo). Marks *feel* like the system is paying attention.
- Traces are immutable run histories; all summaries must point back to trace segments. The raw footage is sacred.
- Crystals are compressive proofs, not highlights; they justify what was kept, what was dropped, and *why the player made those choices*.
- Galois loss is the coherence metric for build drift. High loss doesn't mean failure—it means the player took risks.
- The ghost graph is the topology of unchosen paths—a persistent reminder that decisions are real because alternatives exist.

## Laws

- **L1 Run Coherence Law**: A run is valid only if every major build shift is marked and justified. Unwitnessed pivots are provisional.
- **L2 Build Drift Law**: If Galois loss exceeds threshold, the system surfaces the drift—never conceals. Drift is data, not shame.
- **L3 Ghost Commitment Law**: Unchosen upgrades are recorded as ghost alternatives. The proof space must include paths not taken.
- **L4 Risk Transparency Law**: High-risk choices must be explicitly marked *before* their effects resolve. Courage is witnessed up front.
- **L5 Proof Compression Law**: A run crystal must reduce trace length while preserving causal rationale. Compression is clarity, not loss.

## Qualitative Assertions

- **QA-1** The game must feel *faster*, not slower, because witnessing reduces indecision. The loop is tight because the system catches up.
- **QA-2** Players should feel their style is *seen*, not judged. The compass is descriptive—a mirror, not a scorecard.
- **QA-3** Failure runs must produce *clearer* crystals than success runs. Defeat reveals more than victory.
- **QA-4** The ghost layer should feel like an alternate timeline, not an error log. Roads not taken are honorable, not regrettable.

## Anti-Success (Failure Modes)

This pilot fails if:

- **Surveillance creep**: The witnessing layer feels heavy—the player notices latency, hesitates before acting, or mutes the system to play freely. Witnessing should be *invisible* at play-speed.
- **Judgment leakage**: The compass or crystal feels punitive ("bad run," "drift too high") instead of descriptive ("aggressive early, defensive late"). The system becomes a critic, not a witness.
- **Highlight theater**: Crystals become "cool moments" reels instead of coherent proofs. The player can't answer "why did I make those choices?"—only "what looked cool."
- **Ghost-as-error**: Unchosen paths feel like mistakes. The UI treats ghosts as "wrong choices" rather than "real alternatives." The decision space collapses.
- **Speed tax**: Any added frame of delay, any input lag, any perceptible slowdown. The arcade loop is sacred.

## kgents Integrations

| Primitive | Role | Chain |
|-----------|------|-------|
| **Witness Mark** | Captures micro-decisions with context | `action → Mark.emit(context, weights)` |
| **Witness Trace** | Immutable run history | `Mark[] → Trace.seal(run_id)` |
| **Witness Crystal** | Compressive proof of run | `Trace → Crystal.compress(rationale)` |
| **ValueCompass** | Visible playstyle constitution | `Crystal.weights → Compass.render()` |
| **Trail** | Run navigation + compression display | `Trace → Trail.navigate(segments)` |
| **Galois Loss** | Drift and coherence signal | `Trace.weights → Galois.loss(style_target)` |
| **Differance Ghost** | Unchosen upgrade graph | `decision_point → Ghost.record(alternatives)` |

**Composition Chain** (single run):
```
InputEvent
  → Mark.emit(risk, tempo, build_state)
  → [on run_end] Trace.seal()
  → Galois.loss(style_target) // drift signal
  → Ghost.record(unchosen_upgrades)
  → Crystal.compress(trace, ghosts)
  → Compass.render(crystal.weights)
  → Trail.display(crystal, trace)
```

## Canary Success Criteria

- A player can explain a run **in under 30 seconds** using only the crystal and the trail.
- A player can name the build's **core proof claim** in one sentence: "I'm an aggressive early-game glass cannon who pivots defensive when RNG punishes."
- The system shows **at least one ghost alternative** per major build pivot—visible but not intrusive.
- The witness layer adds **zero perceptible latency** to the game loop.

## Out of Scope

- Multiplayer balance, long-term meta economy, or matchmaking.
- Leaderboards or competitive ranking systems.
- Replay video export (crystals are semantic, not visual).
