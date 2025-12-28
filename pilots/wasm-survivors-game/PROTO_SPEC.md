# Hornet Siege: The Colony Always Wins

Status: proto-spec (Enlightened Edition — Market-Informed)

> *"You are the apex predator. You are nature's perfect killing machine. And you will lose."*

---

## Design Philosophy: Principled Differentiation

> *"In a genre of 900+ games, being 'good' is death. Being 'different' is survival."*

This spec is informed by market analysis revealing:
- **900+ survivors-likes** exist; only **1 hit in 2024** (Deep Rock Survivor)
- **Villain games succeed when FUN** (Carrion, Dungeon Keeper), not just thematic
- **THE BALL must be clip-worthy** — streamability is survival
- **Progress velocity matters** — each death must teach, not just punish
- **Dark humor helps** — villain games with personality outperform serious ones

**The Core Bet**: Tragedy + Power Fantasy + Real Biology + Dark Humor = Cult Classic

---

## Lore: The War That Never Ends

**The Truth of Hornets**: Japanese giant hornets (*Vespa mandarinia*) are evolution's perfect raiders. A single hornet can kill 40 bees per minute. Their mandibles slice through chitin like paper. Their venom dissolves flesh. In the wild, a small squad of hornets can massacre 30,000 bees in hours.

**The Truth of Bees**: European honey bees are defenseless against hornets. They die in droves. But Japanese honey bees have evolved the impossible: *collective defense through sacrifice*. When a hornet enters, hundreds of bees form a "hot defensive bee ball"—they surround the invader and vibrate their flight muscles, raising the temperature to 47°C (117°F). The hornet cooks alive. The bees survive (barely). The colony persists.

**The Tragedy You Play**: You are a hornet. You raid to feed your larvae—it's what evolution made you for. The bees defend their civilization—it's what evolution made them for. Neither side is evil. Both are necessary. And in this game, the bees always figure it out.

*You are playing out the tragedy of the invader who was born to conquer but destined to fall.*

**The Meta-Message**: Sometimes the invader IS the monster. Sometimes overwhelming power isn't enough. Sometimes the colony adapts faster than the apex predator can kill.

---

## Personality Tag

*This pilot believes tragedy can be beautiful, that playing the monster teaches empathy, and that sometimes the most honest story is one where you lose. Every upgrade makes you more powerful. Every wave makes the colony smarter. The ending is written. The journey is yours.*

**But also**: The hornet has *attitude*. Dark humor. Swagger before the fall. You're not a sad protagonist—you're a magnificent bastard who knows they're doomed and hunts anyway.

---

## The Seven Contrasts (Emotional Architecture)

> *"Great games oscillate. Flat games flatline."*

The emotional core of Hornet Siege is **violent oscillation** between opposing states. Each contrast is a design law.

### Contrast 1: God of Death ↔ Cornered Prey

| God of Death State | Cornered Prey State |
|-------------------|---------------------|
| Mowing through waves effortlessly | THE BALL is forming, nowhere to run |
| Abilities chaining, combos flowing | Cooldowns empty, health critical |
| "I am unstoppable" | "Oh god oh god oh god" |
| Screen shake, bass drops, XP fountains | Screen tunnels, heartbeat audio, time slows |

**Law GD-1**: Every siege MUST visit both extremes. A run that's all-power or all-panic fails.
**Law GD-2**: The transition should be *sudden*. You don't gradually become prey. You realize it.

### Contrast 2: Speed ↔ Stillness

| Speed | Stillness |
|-------|-----------|
| Combat: 60fps chaos, everything moving | Level-up: World frozen, choices presented |
| Strafing runs through swarms | The moment before THE BALL closes |
| Combo chains, no time to think | Amber memory reflection, all the time |

**Law SS-1**: Combat never pauses except for level-up and death.
**Law SS-2**: Stillness is *earned* through violence. Pause = you killed enough to evolve.

### Contrast 3: Massacre ↔ Respect

| Massacre | Respect |
|----------|---------|
| Early waves: bees scatter like leaves | Late waves: military precision, they KNOW you |
| "These are just bugs" | "These are soldiers defending their home" |
| Kill count climbing | Kill count stops mattering—formations are what count |

**Law MR-1**: Wave 1-3 must feel like slaughter. Wave 8+ must feel like war.
**Law MR-2**: The shift should produce the "they're COORDINATING" moment by wave 3.

### Contrast 4: Hubris ↔ Humility

| Hubris | Humility |
|--------|----------|
| "One more upgrade and I'm invincible" | "I had every upgrade and I still lost" |
| Maxed-out hornet, glowing with power | Same hornet, cooked alive in THE BALL |
| "This run, I'll beat my record" | "The colony always wins. And it should." |

**Law HH-1**: The most powerful-feeling moment should be 30-60s before death.
**Law HH-2**: Death should feel *inevitable in retrospect*, not unfair.

### Contrast 5: Noise ↔ Silence

| Noise | Silence |
|-------|---------|
| Kill sounds, combo pings, pheromone alerts | 2-4 seconds of nothing before THE BALL closes |
| Urgent music escalating | Music drops out, just your wingbeats |
| Screen full of particles | Screen clears—just you and the forming sphere |

**Law NS-1**: THE BALL must be preceded by *ominous silence*.
**Law NS-2**: The loudest moment (death) follows the quietest moment (formation complete).

### Contrast 6: Predator ↔ Prey (Role Reversal)

| Predator | Prey |
|----------|------|
| You choose where to strike | They choose where you can't go |
| Bees flee from your path | Bees herd you toward THE BALL |
| Camera follows your movement | Camera pulls back—you're being surrounded |
| Red threat indicators ON THEM | Red threat indicators ON YOU |

**Law PP-1**: The predator/prey reversal should be *felt*, not just stated.
**Law PP-2**: Visual language must flip. What marked threats becomes what marks YOU.

### Contrast 7: Learning ↔ Knowing

| Learning | Knowing |
|----------|---------|
| Run 1: "What's happening?" | Run 10: "I know exactly how I'll die" |
| Surprised by first formation | Anticipating formation before it forms |
| Reacting to the colony | Predicting the colony (and losing anyway) |

**Law LK-1**: Mastery should be visible. Run 10 looks different than Run 1.
**Law LK-2**: Knowing doesn't save you. The colony knows you're knowing.

---

## Core Pillars

### 1. Predator Movement

> *"You are the fastest thing in this hive. It won't save you."*

You move like a hornet—bursts of terrifying speed, sharp pivots, aerial dominance. The bees can't catch you. They don't need to. They just need to surround you.

**Movement Laws:**
- **M1 Predator Response**: < 16ms input-to-movement. You're a hornet—you move NOW.
- **M2 Never Trapped (Until THE BALL)**: Player can always move. Damage slows but never stops—until the colony coordinates.
- **M3 Speed Superiority**: Base speed outruns any individual bee. Upgrades make you untouchable—individually.
- **M4 Swarm Reads**: Bee formations are telegraphed. Skilled players read the patterns; unskilled players get surrounded.
- **M5 Momentum Feel**: Movement has *weight*. Starting fast, stopping sharp. Not floaty.

### 2. Predator Upgrades

> *"Each upgrade makes you more deadly. None of them make you immortal."*

**Upgrade Design Laws:**
- **U1 Predator Verbs**: Upgrades change *how you kill*, not just *how much*. "Mandibles pierce through multiple bees" > "+10% damage".
- **U2 Raid Identity**: By wave 5, the player should know their hunting style. "I'm playing venom-spray" or "I'm going fear-aura".
- **U3 Synergy Moments**: 2+ upgrades combine for devastating combos. Pheromone Mark + Death Throes = chain panic.
- **U4 Meaningful Choice**: Every level-up presents a real decision. Glass cannon or sustained assault?
- **U5 Visual Transformation**: Upgrades visibly transform you. Wave 10 hornet looks like a war machine compared to wave 1.
- **U6 Swagger Scaling**: More upgrades = more attitude in animations. Confident idle, aggressive attack poses.

**Hornet Upgrade Archetypes**:

| Archetype | Fantasy | Example Upgrades |
|-----------|---------|------------------|
| **Executioner** | Maximum damage per strike | Mandible Crush, Venom Injection, Critical Sting |
| **Survivor** | Outlast the swarm | Exoskeleton, Regeneration, Honey Drain |
| **Skirmisher** | Never stop moving | Wing Burst, Hit-and-Run, Evasion |
| **Terror** | Break their will | Fear Aura, Death Throes, Panic Spray |
| **Assassin** | Precision elimination | Pierce, Marked for Death, Silent Strike |
| **Berserker** | Overwhelming offense | Stinger Volley, Frenzy, Blood Rage |

### 3. The Colony Defense

> *"Every bee is a question. The colony is the answer you can't solve."*

Bees are not HP bags—they're members of a civilization fighting for survival. Individually weak, they become unstoppable through coordination.

**Enemy Design Laws:**
- **E1 Readable Patterns**: Every bee attack is telegraphed. Wing positions, pheromone trails, formation shifts.
- **E2 Learnable Behaviors**: Bee types are consistent. Worker Bees swarm. Guard Bees hold. Scout Bees alert.
- **E3 Distinct Silhouettes**: Know the bee type instantly. Golden workers, red guards, silver scouts.
- **E4 Escalating Coordination**: Early waves are chaos. Late waves are military precision.
- **E5 Fair Deaths**: Every death is attributable. "I died because I let them form THE BALL."
- **E6 Civilization Feel**: Bees should feel like they're *protecting something*, not just attacking.

**Bee Types**:

| Type | Behavior | Teaches | Defensive Formation |
|------|----------|---------|---------------------|
| **Worker Bee** | Swarms toward player | Basic kiting | THE SWARM (overwhelming numbers) |
| **Scout Bee** | Fast, alerts others | Priority targeting | THE HIVEMIND (perfect coordination) |
| **Guard Bee** | Slow, high HP, blocks paths | Prioritization | THE COMB (defensive structure) |
| **Propolis Bee** | Ranged sticky attacks | Projectile dodging | THE PROPOLIS BARRAGE (area denial) |
| **Royal Guard** | Elite defender, complex patterns | Boss mechanics | THE HEAT BALL (the famous defense) |

---

### 4. The Coordination System

> *"Kill them fast, or watch them become a superorganism."*

**Core Rule**: Bees that survive long enough begin coordinating. They spread alarm pheromones, form defensive patterns, and eventually create **Defensive Formations**—coordinated bee structures with capabilities no individual bee could achieve.

| Survival Time | What Happens | Visual |
|---------------|--------------|--------|
| 0-10s | Individual behavior, scattered defense | Normal bee colors |
| 10-15s | **Alarm pheromones spreading**—bees seeking each other | Orange particle trails |
| 15-20s | **Defensive patterns forming**—organized movement | Wing vibrations visible |
| 20s+ | **FORMATION COMPLETE** if 2+ coordinating bees connect | Heat shimmer, bass thrum |

**Coordination Laws:**
- **C1 Predictable Timer**: Players must be able to learn the coordination window
- **C2 Visual Warning**: Coordinating bees are OBVIOUS—pheromone trails, wing vibrations
- **C3 Interruptible**: Killing ANY coordinating bee disrupts nearby bees' formation
- **C4 Escapable**: Formations can be fled from. Powerful but not omniscient.
- **C5 Soloable**: Every formation can be defeated with skill. The skill ceiling is infinite.
- **C6 Dread Buildup**: Coordination visuals should feel like *doom approaching*, not just "enemy spawning"

**Mutant Variants**: Some bees have **Enhanced Coordination** (glowing outline). Enhanced bees that participate in formation-building make the resulting formation **faster and tighter**. Kill enhanced bees first, or the formation will be devastating.

---

### 5. THE HEAT BALL — The Clip-Worthy Moment

> *"When THE BALL forms, streamers should scream. Viewers should clip. This is the signature."*

THE HEAT BALL is not just a formation—it's the **marketing hook**, the **clip moment**, the **thing people tell their friends about**. It must be:

1. **Visually Spectacular**: The most dramatic thing in the game
2. **Audibly Terrifying**: The sound design must make you feel the heat
3. **Mechanically Fair**: You can escape—barely—with perfect play
4. **Emotionally Devastating**: When it closes, you KNOW

**THE BALL Laws:**

- **TB-1 Encirclement Phase**: Bees form a visible sphere. Gaps exist. You can dash through.
- **TB-2 Constriction Phase**: Sphere tightens. Gaps shrink. Temperature indicator rises.
- **TB-3 Heat Death Phase**: At 47°C, instant death. Screen whites out. Cooking sound.
- **TB-4 The Silence Before**: 2-4 seconds of near-silence before final constriction.
- **TB-5 Camera Pull**: Camera pulls back to show the full sphere. You see yourself surrounded.
- **TB-6 Escape Window**: Skilled players can dash through the final gap. Timing is frame-tight.
- **TB-7 Audio Escalation**: Wing-buzz crescendo → Silence → Single bass note → Death sound

**Visual Sequence**:

```
1. FORMING (10s):     Bees gathering, orange glow, player still fighting
2. SPHERE (5s):       Visible sphere, gaps closing, temperature rising
3. SILENCE (3s):      Audio drops. Just wingbeats. Player realizes.
4. CONSTRICTION (2s): Sphere tightens. One gap remains. Time slows.
5. DEATH (instant):   Gap closes. White flash. Cooking crackle. Done.
```

**The "OH NO" Indicator**: When THE BALL begins forming, a distinct visual + audio cue must trigger that makes experienced players say "oh no" out loud. This is the clip moment.

---

### 6. Colony Intelligence

> *"They're not just defending. They're learning."*

**Collective Memory**: The colony shares information across all active bees.

| Behavior | Description |
|----------|-------------|
| **Pattern Propagation** | If one bee learns your dodge pattern, ALL bees adjust |
| **Sacrifice Awareness** | When one bee dies, others coordinate faster |
| **Formation Priority** | When a Formation exists, loose bees become reinforcements |
| **Death Knowledge** | The colony remembers which tactics killed YOU—uses them more |

**Colony Laws:**
- **H1 Fair Learning**: Colony learns from its successes, not failures. If you escape, they adapt.
- **H2 Reset Between Sieges**: Colony intelligence resets each run. No cross-run punishment.
- **H3 Visible Intelligence**: HUD shows colony coordination level (subtle, not invasive)
- **H4 Counterplay Exists**: Every colony behavior has a counter. Adaptation is a puzzle.
- **H5 Complicity**: The colony learns because you TAUGHT it. Your actions create your doom.

**Visual Language of Coordination**:

| State | Visual | Audio |
|-------|--------|-------|
| Individual | Normal behavior, scattered | Standard buzzing |
| Alarm | Pheromone particles, orange glow | Pitch rises |
| Coordinating | Visible wing vibrations, seeking formation | Harmonic buzz |
| Pre-Formation | Bodies gravitating together, heat shimmer | Deep thrum begins |
| Formation Active | All loose bees gain subtle hive glow | Bass undertone |

---

## Juiciness Laws (Visceral Satisfaction)

> *"Villain games succeed when they're FUN, not just thematic. Carrion won because monster gameplay felt INCREDIBLE."*

### Kill Feedback (The Crunch)

Every kill must feel devastating. This is non-negotiable.

| Element | Requirement | Reference |
|---------|-------------|-----------|
| **Impact Frame** | 2-3 frame freeze on kill | Hades, Vampire Survivors |
| **Chitin Crack** | Distinct sound per bee type | Satisfying crunch |
| **Scatter Physics** | Bodies fly based on attack direction | Carrion, Hotline Miami |
| **XP Burst** | Golden particles + vacuum toward player | Dopamine trigger |
| **Combo Counter** | Visible number, scales with kills/second | Score chasers love this |
| **Screen Shake** | Subtle on normal kills, heavy on multi-kills | < 5px, > 15px |

**Kill Laws:**
- **K1**: Single kill = crunch + scatter + XP
- **K2**: Multi-kill (3+) = bigger crunch + screen shake + combo popup
- **K3**: Massive kill (10+) = bass drop + slowmo + "MASSACRE" text
- **K4**: Every kill sound is pitched slightly randomly (no repetition fatigue)

### Movement Feedback (The Flow)

| Element | Requirement |
|---------|-------------|
| **Dash Whoosh** | Audible wind sound on Wing Burst |
| **Trail Particles** | Subtle motion blur at high speed |
| **Stop Impact** | Tiny dust puff when stopping from dash |
| **Near-Miss** | Audio cue when avoiding attack by < 10px |
| **Cornered Warning** | Heartbeat audio when surrounded |

### Upgrade Feedback (The Power-Up)

| Element | Requirement |
|---------|-------------|
| **Selection Sound** | Satisfying "CHUNK" on ability select |
| **Power Surge** | Brief golden flash on player |
| **Visual Change** | Immediate visible transformation |
| **First Use Highlight** | New ability glows until first use |

---

## Sound Design Laws

> *"Audio is half the juice. A silent Hornet Siege is half a game."*

### Ambient Layers

| Layer | Description | Dynamic |
|-------|-------------|---------|
| **Hive Drone** | Constant low-frequency buzz | Pitch rises with colony coordination |
| **Your Wings** | Player wingbeat, responsive to movement | Faster when dashing |
| **Distant Activity** | Bees you can't see are audible | Directional, warns of spawns |

### Event Sounds

| Event | Sound Profile |
|-------|---------------|
| **Kill** | Chitin crack, pitched by bee type |
| **Combo** | Ascending chime sequence |
| **Level Up** | Evolution "WOMP" + shimmer |
| **Pheromone Alert** | Organic alarm, rises in pitch |
| **Formation Forming** | Deep thrum, building |
| **THE BALL Silence** | All audio drops except wingbeats |
| **Death** | Cooking crackle, white noise fade |

### Music

| Phase | Music Style |
|-------|-------------|
| **Early Waves** | Driving, aggressive, predator energy |
| **Mid Waves** | Tension building, drums intensifying |
| **Late Waves** | Oppressive, inevitable, tragic |
| **Formation Active** | Music distorts, bees are winning |
| **Pre-Death** | Silent except heartbeat |
| **Death Screen** | Somber, beautiful, reflective |

---

## The Hornet's Personality (Dark Humor)

> *"Villain games with personality outperform serious ones. The hornet should have SWAGGER."*

The hornet is not a tragic hero. The hornet is a **magnificent bastard** who knows the score and hunts anyway. Dark humor, not grimdark.

### Voice Lines (Optional, Text-Based OK)

| Trigger | Line Example |
|---------|--------------|
| First kill | "40 per minute. I can do better." |
| Multi-kill | "Evolution made me for this." |
| Level up | "Ah. More ways to die magnificently." |
| Formation spotted | "They're learning. How adorable." |
| THE BALL forming | "Well. Here we go again." |
| Death | "The colony always wins. ...Respect." |

### Visual Personality

| State | Animation |
|-------|-----------|
| Idle (early run) | Alert, aggressive stance |
| Idle (late run) | Confident swagger, surveying kills |
| Idle (low HP) | Still defiant, not cowering |
| Kill | Satisfying snap animation |
| Multi-kill | Brief pause, as if savoring |
| Death | Acceptance, not despair |

**Personality Law**: The hornet never begs, never whines, never seems unfairly treated. The hornet KNOWS what this is and does it anyway. That's the character.

---

## Learning Velocity Mechanics

> *"Progress velocity matters—each death must teach, not just punish."*

### Per-Death Learning

Every death should reveal something. The amber memory system supports this:

| What's Shown | What's Learned |
|--------------|----------------|
| Survival time | "I lasted 30s longer this run" |
| Kill count | "I killed 200 more bees" |
| Formation that killed | "THE BALL got me—need to watch for encirclement" |
| Coordination level at death | "Colony was at 8/10 coordination—they're faster than I thought" |
| "Could have done" hint | "Kill scouts first to delay coordination" |

### Skill Display

| Metric | Visible To Player |
|--------|-------------------|
| Personal best time | Yes, on death screen |
| Personal best kills | Yes, on death screen |
| "New skill unlocked" | No—skill IS the unlock |
| "Formation escaped" count | Yes—shows mastery |

**Learning Law**: A player on run 10 should be able to articulate what they learned that they didn't know on run 1.

---

## Complicity Mechanics (You Built This Doom)

> *"Loop Hero shows 'build your own doom' works. The player should feel RESPONSIBLE."*

### How You Create Your Death

| Player Action | Colony Response | Complicity |
|---------------|-----------------|------------|
| Kill aggressively | Survivors coordinate faster (sacrifice awareness) | "My aggression taught them" |
| Always dash left | Colony predicts left dashes | "They learned my pattern" |
| Ignore scouts | Formations form faster | "I let them communicate" |
| Focus one area | Other areas build formations | "I created a blind spot" |

### Visible Complicity

- **Colony HUD**: Shows what the colony has learned about YOU
- **Death Screen**: "The colony learned: [your pattern]"
- **Amber Memory**: Records your playstyle, shows how it led to death

**Complicity Law**: The player should feel "I could have prevented this" not "this was random."

---

## Emotional Arc (Refined)

- **E1 Journey Shape**: Sieges traverse POWER → FLOW → CRISIS → TRAGEDY. You feel godlike, then you fall.
- **E2 One More Siege**: The post-death state must invite immediate retry. "Maybe this time..."
- **E3 Defeat Clarity**: Failure runs produce *clearer* feedback than victories. You must know *how* they got you.
- **E4 The Coordination Moment**: Wave 2-3 should deliver the "they're COORDINATING" moment—first formation, first realization that they're a superorganism.
- **E5 Tragic Stakes**: Late waves should feel like a chess match you can't win—you know they know, they know you know, and the ball is forming.
- **E6 Catharsis**: Death should feel like release, not frustration. "They earned it."

---

## Fun Floor

> *"Below this line, the game isn't worth playing. Above it, we iterate."*

### Must-Haves (non-negotiable)

| Category | Requirement |
|----------|-------------|
| **Input** | < 16ms response. Movement feels predatory—*fast*. |
| **Movement** | Player can always move (until THE BALL). No stun-lock. |
| **Kill** | Death = chitin crack + scatter + XP burst. Devastating feedback. |
| **Level-up** | Pause + choice + power surge. Evolution moment. |
| **Death** | Readable cause. "I died because THE BALL formed" in < 2 seconds. |
| **Restart** | < 3 seconds from death to new siege. The colony is always waiting. |
| **Build identity** | By wave 5, player can name their hunting style. |
| **Synergy** | 2+ abilities combine for emergent power. 1+1 > 2 somewhere. |
| **Escalation** | Wave 10 is obviously harder than wave 1. Visually, sonically. |
| **Bee variety** | At least 4 distinct bee types with different behaviors. |
| **Ability variety** | At least 8 abilities that change hunting style. |
| **Coordination visible** | Pheromone timer is ALWAYS readable (visual, not numeric). |
| **Formation telegraphs** | Every Formation attack has long, readable wind-up. |
| **Colony awareness** | HUD shows colony coordination level (subtle indicator). |
| **THE BALL clip-worthy** | First-time viewers should gasp. |

### Player Advocate Tests

- **5-Minute Test**: New player understands controls (30s), gets first kill (5s—you're a predator), feels powerful (wave 1), dies to THE BALL (wave 3-5), retries.
- **Tragedy Test**: Player on run 10 demonstrably plays better—and still loses. The lesson lands.
- **Build Test**: Two players describe their sieges differently. "I went terror build" vs "I went assassin".
- **Death Test**: Player can explain every death. "They formed THE BALL" not "I don't know what happened."
- **Streamer Test**: Someone could entertainingly narrate this. Clear tragedy, readable doom, shareable "THEY GOT ME."
- **Coordination Test**: First-time player has a visible "they're COORDINATING?" moment.
- **Priority Test**: Experienced player can explain coordination priority. "Kill the glowing ones to disrupt formation."
- **Formation Test**: Player can name and describe THE HEAT BALL. "They surround you and cook you."
- **Clip Test**: THE BALL moment is compelling to watch even without context.
- **Humor Test**: Player smiles at least once during a run. The hornet has attitude.

---

## Qualitative Assertions

- **QA-1** Movement should feel *predatory*. You are faster than anything here.
- **QA-2** Abilities should feel like *evolutionary weapons*. Each one makes you more lethal.
- **QA-3** Bees should feel like *a civilization*, not enemies. They're defending their home.
- **QA-4** Death should feel like *inevitability accepted*, not punishment. "They finally got me."
- **QA-5** Sieges should feel like *tragedies*. Each one tells the same story differently.
- **QA-6** Coordination should feel like *doom approaching*. The pheromones are spreading.
- **QA-7** Formations should feel like *the colony awakening*. Not just enemies—a superorganism.
- **QA-8** THE BALL should feel like *the end*. When it forms, you know.
- **QA-9** The hornet should feel like *a character*. Swagger before the fall.
- **QA-10** Kills should feel *satisfying*. Juice is not optional.

---

## Anti-Success (Failure Modes)

This pilot fails if:

**Thematic Failures:**
- **Villain feels heroic**: Player doesn't realize they're the invader. The tragedy is missed.
- **Bees feel like obstacles**: Enemies are HP bags, not a defending civilization. No empathy.
- **Death feels unfair**: "I was robbed" instead of "They outcoordinated me."
- **Power fantasy unearned**: Player feels godlike but doesn't appreciate the tragedy.
- **Coordination feels random**: Bees don't feel like they're learning; just spawning harder.
- **Hornet feels generic**: No personality, no swagger, just a sprite.

**Core Gameplay Failures:**
- **Stat-stick upgrades**: Choices don't change *how* you hunt, only *numbers*.
- **HP sponge bees**: Bees are just health bars, not a coordinating defense.
- **Random death**: Player can't explain why they died.
- **Movement tax**: Input lag, sluggish response. You're a HORNET.
- **Build sameness**: Every siege plays the same.
- **Limp kills**: Kills don't feel satisfying. No crunch, no scatter, no juice.

**Colony Failures:**
- **Invisible coordination**: Player can't tell when bees are forming. Unfair.
- **Unfair Formations**: Attacks aren't telegraphed. Frustration, not tragedy.
- **Colony feels random**: Adaptation doesn't feel personal.
- **No coordination moment**: First formation passes without the "they're WORKING TOGETHER" reaction.
- **Formation spam**: Too many formations too fast. Chaos without clarity.

**Clip Failures:**
- **THE BALL is boring**: Doesn't make viewers react.
- **No clear "oh no" moment**: Tension doesn't build.
- **Death is anticlimactic**: No spectacle, no emotional weight.

---

## Witness Integration (Amber Memory)

> *"Every siege is preserved in amber. The colony remembers, and so do you."*

**During the Siege:**
- **Coordination Tracking**: Every kill, every escape, every formation formed
- **Colony Learning**: Visible indicator of colony coordination level
- **Mutual Recording**: You learn the formations; they learn your patterns

**Amber Memory** (stored in crystal):
- What abilities were chosen, how long survived, what formation killed you
- **Coordination count**: How many formations completed before you fell
- **Colony coordination level**: How smart the colony got during your siege
- **Closest call**: The formation you almost prevented
- Build profile: What hunting style emerged from ability choices
- Unchosen paths: What abilities were offered but not taken
- **What the colony learned**: Your patterns, preserved

**Death Crystallization**:
When killed by a formation, the amber memory shows:
- The formation that killed you (rotating 3D view)
- The bees that formed it (decomposition view)
- How long they survived before coordinating (your failure window)
- What you could have done ("Kill the scouts first next time")

**Witness Principles:**
- **Invisible During Play**: Zero UI during gameplay. No live metrics.
- **Reflection After**: Post-siege amber shows what happened and why.
- **Never Judgmental**: Memories describe ("aggressive early game") not evaluate.
- **Optional Depth**: Casual players ignore it. Analysts dig in.
- **Thematic Synergy**: You're preserved in amber, like the insects you are.

---

## Canary Success Criteria

**Core Gameplay Canaries:**
- **Retry rate > 80%**: After first death, player starts new siege immediately.
- **"One more siege" heard**: Playtester says it unprompted.
- **Build diversity**: 5 distinct viable hunting styles emerge.
- **Death attribution**: Player names cause of death within 2 seconds.
- **Predator mastery**: Experienced players survive 2x longer than beginners.
- **Kill satisfaction**: Player comments on how good kills feel.

**Colony/Coordination Canaries:**
- **Coordination moment**: Every new player has a visible reaction to first formation.
- **Priority learning**: By siege 3, players target coordinating bees first.
- **Formation respect**: Players audibly react to formation completion. "THE BALL IS FORMING."
- **Enhanced awareness**: Experienced players mention enhanced bees. "Kill the glowing ones!"
- **Colony personalization**: Players feel the colony adapting to THEM. "They know I dash left."
- **Complicity recognition**: Players say "I let them form it" not "it just happened."

**Thematic Canaries:**
- **Villain recognition**: Player understands they're the invader within first run.
- **Bee empathy**: Player expresses some sympathy for the bees. "They're just defending their home."
- **Tragedy acceptance**: Player accepts inevitable death as appropriate. "They earned it."
- **Mythology understanding**: Player can explain THE HEAT BALL's real-world basis.
- **Hornet personality**: Player references the hornet's attitude. "That death line is great."

**Streamability Canaries:**
- **Clip moment**: First-time viewer reacts to THE BALL.
- **Quotable phrase**: "THE BALL IS FORMING" becomes recognizable.
- **Shareability**: Player wants to show someone else this game.

---

## Implementation Phases

### Phase 1: Core Survivors Loop (Current)
The base game with hornet theme. Must satisfy Fun Floor before proceeding.
- Movement + kills + juice
- 4 bee types
- 4 abilities
- Basic coordination visual

### Phase 2: THE BALL (Priority 1)
1. Implement THE HEAT BALL with full visual sequence
2. The Silence Before
3. Camera pull effect
4. Cooking death animation
5. **Validate: Is this clip-worthy?**

### Phase 3: Coordination System
1. Implement survival timer on bees
2. Add pheromone visual state
3. Create THE SWARM formation
4. Add coordination trigger and animation

### Phase 4: Full Formation Roster
1. Implement remaining formations
2. Add enhanced bee variant system
3. Create themed coordinated attacks
4. Balance coordination timers

### Phase 5: Personality & Polish
1. Add hornet voice/text lines
2. Implement swagger animations
3. Sound design pass
4. Death screen crystallization

### Phase 6: Witness Integration
1. Merge colony data into amber memory system
2. Add formation death rituals
3. Implement "colony knows you" personalization

---

## Out of Scope

- Complex witness UI during gameplay (amber memories are post-run only)
- Victory condition (the colony always wins)
- Multiplayer balance, long-term meta economy
- Leaderboards or competitive ranking
- Meta-progression unlocks (skill is the progression)
- Cross-run colony memory (colony resets each siege per H2)

---

## The Pitch

> *"A survivors-like where you play the monster. You're a Japanese giant hornet raiding a bee colony—nature's perfect predator against nature's most coordinated defense. Your mandibles can kill 40 bees per minute. It won't be enough.*
>
> *The bees aren't just enemies. They're a civilization. And when they form THE BALL—surrounding you, vibrating, raising the temperature until you cook—you'll understand: sometimes the invader loses. Sometimes the colony prevails.*
>
> *You're not fighting bees. You're fighting a superorganism. And it always wins."*

---

## The Mirror Test

> *"Does this feel like Kent on his best day?"*

**Daring**: You play the villain. You lose. That's the point.
**Bold**: THE HEAT BALL as core mechanic—the real defense, the real tragedy.
**Creative**: A survivors-like where survival isn't the goal—understanding is.
**Opinionated**: The bees ALWAYS win. This is a tragedy you play through.
**Not gaudy**: Every system serves the core truth: the colony adapts faster than you can kill.
**Joyful**: Kills feel INCREDIBLE. The hornet has swagger. Dark humor, not grimdark.

---

*"You are the apex predator. You are evolution's perfect killing machine. You will slaughter thousands. And when they form THE BALL, when the heat rises, when you cook alive surrounded by the civilization you tried to destroy—you'll understand.*

*The colony always wins. And it should."*
