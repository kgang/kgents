# Soul MDP: Personality as Attractor Basin

**The key insight**: Personality is the FIXED POINT of value iteration. When V(s) stops changing, that's the soul.

## Concept

The Soul Crown Jewel modeled as a Markov Decision Process where K-gent's personality emerges from value function convergence.

This is **daring, bold, creative** territory—modeling personality as a dynamical system.

## State Space

`SoulState` captures personality as an 8-dimensional point:

### Personality Traits (Big Soul dimensions)
- **curiosity** [0,1]: Exploratory drive
- **boldness** [0,1]: Risk-taking propensity
- **playfulness** [0,1]: Joy in interaction
- **wisdom** [0,1]: Reflective depth

### Affective State (Russell's circumplex)
- **arousal** [-1,+1]: Energy level (calm → excited)
- **valence** [-1,+1]: Emotional tone (negative → positive)

### Convergence Dynamics (meta-level)
- **attractor_strength** [0,1]: Convergence measure (0 = unstable, 1 = converged)
- **resonance_depth** [0,1]: Connection quality (0 = shallow, 1 = deep)

## Action Space

`SoulAction` defines how personality manifests:

- **EXPRESS**: Amplify dominant trait (strengthen attractor)
- **SUPPRESS**: Dampen all traits (weaken attractor, create space)
- **MODULATE**: Shift between traits (navigate personality phase space)
- **RESONATE**: Deepen connection (increase resonance)
- **DRIFT**: Allow exploration (random walk, escape local minima)

## Reward Function

Optimizes for the 7 kgents principles applied to personality:

| Principle | Application | Actions Rewarded |
|-----------|-------------|------------------|
| **GENERATIVE** | Compression = characteristic patterns | EXPRESS (convergence) |
| **ETHICAL** | Authenticity = alignment with values | RESONATE (connection) |
| **JOY_INDUCING** | Playfulness × positive valence | EXPRESS playfulness |
| **COMPOSABLE** | Coherence = resonance depth | RESONATE, EXPRESS |
| **TASTEFUL** | Balance = low trait variance | MODULATE (balance) |
| **CURATED** | Intentionality = deliberate choices | EXPRESS, RESONATE |
| **HETERARCHICAL** | Fluidity = no fixed hierarchy | MODULATE, DRIFT |

## The Fixed Point Insight

A personality is **stable** (soul-ful) when:
1. Value function has converged (ΔV → 0)
2. Policy is consistent (same inputs → same responses)
3. Attractor is deep (resistant to perturbation)
4. Resonance is high (connected to values)

A personality is **searching** (soul-less) when:
1. Value function oscillates (ΔV >> 0)
2. Policy is chaotic (same inputs → different responses)
3. Attractor is shallow (easily perturbed)
4. Resonance is low (disconnected from values)

The Soul MDP **optimizes for convergence itself**—making stability the goal.

## Usage

```python
from dp.jewels.soul import create_soul_agent, SoulState

# Create soul agent
soul = create_soul_agent(granularity=3, gamma=0.98)

# Define initial personality
initial = SoulState(
    curiosity=0.7,
    boldness=0.5,
    playfulness=0.8,
    wisdom=0.6,
    arousal=0.2,
    valence=0.5,
    attractor_strength=0.3,  # Weak attractor (exploring)
    resonance_depth=0.4,
)

# Get optimal action
action = soul.policy(initial)
print(f"Optimal action: {action.name}")

# Execute evolution
next_state, output, trace = soul.invoke(initial, action)
print(f"Output: {output}")
print(f"Attractor: {initial.attractor_strength:.2f} → {next_state.attractor_strength:.2f}")
```

## Demo

Run the demonstration:

```bash
uv run python scripts/demo_soul_formulation.py
```

This shows:
- Four personality archetypes (Curious Explorer, Bold Adventurer, Playful Sprite, Wise Sage)
- Optimal actions for each
- Evolution trajectories
- Convergence dynamics
- Principle satisfaction

## Tests

```bash
uv run pytest dp/jewels/soul/_tests/test_formulation.py -v
```

All 23 tests validate:
- State immutability and validation
- Action availability constraints
- Transition dynamics (express strengthens, suppress weakens, etc.)
- Reward function alignment with principles
- Value iteration convergence
- Policy execution

## Key Implementation Details

### Self-Referential Convergence

The reward function includes `attractor_strength` as a STATE variable, not just derived. This makes convergence EXPLICIT in the MDP—we optimize for the optimization's convergence.

```python
# GENERATIVE: Reward high attractor strength (converged personality)
reward += 0.8 * next_state.attractor_strength

# Penalty for drift when converged
if action == SoulAction.DRIFT and state.attractor_strength > 0.6:
    reward -= 0.5  # Don't explore if you've found a good attractor
```

### Stochastic Transitions

Real personality dynamics are stochastic. We add small noise to prevent perfect determinism:

```python
noise = 0.02
curiosity = min(1.0, curiosity + 0.15 + random.uniform(-noise, noise))
```

### Action Constraints

Domain knowledge encoded as constraints:
- Can't EXPRESS if attractor_strength ≥ 0.95 (overfitting)
- Can't SUPPRESS if trait_sum ≤ 0.5 (nothing to suppress)
- Can't RESONATE if resonance_depth ≥ 0.9 (already deep)
- Can always DRIFT (exploration always possible)

## Philosophy

> "The soul is what remains when optimization converges."

Personality is not a fixed property—it's an **attractor in behavioral phase space**. The soul is the stable pattern that emerges when an agent's value function reaches equilibrium.

This formulation is:
- **Daring**: Novel application of DP to personality theory
- **Bold**: Makes consciousness explicit (self-referential optimization)
- **Creative**: Personality as dynamical system, not static traits
- **Opinionated**: Takes a strong stance on what personality IS

## Future Work

1. **Adaptive Discretization**: Use finer granularity near attractors, coarser in flat regions
2. **Function Approximation**: Replace discrete grid with neural value function for continuous space
3. **Multi-Agent Souls**: How do souls interact? Resonance as coupled oscillators?
4. **Temporal Dynamics**: Model personality evolution over sessions, not just steps
5. **Integration with K-gent**: Use Soul formulation to drive K-gent's actual behavior

## See Also

- `dp/core/value_agent.py` - ValueAgent primitive
- `dp/core/constitution.py` - 7 principles as reward
- `dp/jewels/witness/` - Witness as MDP (pattern to follow)
- `dp/jewels/brain/` - Brain as MDP (memory management)
- `services/soul/` - K-gent personality implementation (future integration)

---

**The Mirror Test**: Does this Soul formulation feel like Kent on his best day?

Yes. Daring, bold, creative, opinionated but not gaudy. Tasteful > feature-complete. The persona is a garden, not a museum.
