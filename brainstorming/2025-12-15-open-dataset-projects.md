# Open Dataset-Based Projects for Kgents

> *"The noun is a lie. There is only the rate of change."*

**Date**: 2025-12-15
**Request Context**: Brainstorm 5 open, public, dataset-based projects that could be executed and perennially evolved with kgents. Apply first principles thinking and user journeys.
**Focus Alignment**: Agent Town, holographic metaphor reification, compositional generative UI, joy-inducing experiences

---

## First Principles: Why Open Datasets + Kgents?

### The Core Insight

Kgents' categorical foundation—PolyAgent + Operad + Sheaf—is domain-agnostic. The same three-layer stack that models Agent Town citizens can model scientific discovery, urban dynamics, economic flows, or knowledge evolution. Open datasets provide the **ground truth** that enables agents to:

1. **Manifest** observer-dependent views (AGENTESE `*.manifest`)
2. **Witness** historical evolution (AGENTESE `*.witness`)
3. **Refine** through dialectical interaction (AGENTESE `*.refine`)
4. **Sip/Tithe** from entropy (void.* for serendipity)

### The Perennial Evolution Principle

A truly evolvable project requires:
- **Continuously updated data sources** (not static snapshots)
- **Community-maintained datasets** (crowd wisdom)
- **Multi-modal richness** (text, structure, time series)
- **Compositional depth** (entities + relationships + dynamics)

---

## Project 1: WikiVerse — The Living Knowledge Ecosystem

### Dataset Foundation

**[Wikidata](https://www.wikidata.org/)** — The world's largest open knowledge graph with 119M+ entities, 1.65B statements, continuously updated by 24,000+ volunteers monthly.

**[Wikidata Embedding Project](https://www.wikidata.org/wiki/Wikidata:Embedding_Project)** (October 2025) — Vector embeddings of the entire knowledge graph, supporting 100+ languages via Jina AI models, stored in DataStax Astra DB.

### The Vision

A multi-agent ecosystem where specialized citizen-agents embody different domains of human knowledge. Each agent maintains a "garden" of concepts, and interactions between agents create emergent cross-domain insights.

### Categorical Mapping

| Layer | WikiVerse Implementation |
|-------|-------------------------|
| **PolyAgent** | `KnowledgePolynomial` — Positions: {EXPLORING, TEACHING, DEBATING, SYNTHESIZING, ARCHIVING} |
| **Operad** | `EPISTEMIC_OPERAD` — Operations: cite, contradict, synthesize, specialize, generalize |
| **Sheaf** | `ConceptCoherence` — Gluing agent-local knowledge into consistent global ontology |

### User Journeys

#### Journey 1: The Curious Student
```
User: "I want to understand how climate change relates to ancient civilizations"

System Flow:
1. WikiVerse spawns ClimateAgent (climatology garden) and HistoryAgent (ancient history garden)
2. Both agents navigate their Wikidata neighborhoods via vector similarity
3. EPISTEMIC_OPERAD.synthesize composes their local views
4. Sheaf gluing produces coherent narrative with citation links
5. User receives: "The 4.2 kiloyear event (drought ~2200 BCE) contributed to the collapse of
   the Akkadian Empire, Egyptian Old Kingdom, and Indus Valley Civilization. Sources: [Q...]"

AGENTESE Path: world.climate.manifest(student_umwelt) >> concept.history.lens >> void.synthesis.sip
```

#### Journey 2: The Fact-Checker
```
User: "Verify: Einstein was born in Germany"

System Flow:
1. FactCheckAgent queries Wikidata for Q937 (Einstein)
2. Retrieves birthplace: Q3806 (Ulm) → part of Q183 (Germany) at time of birth
3. But also: Ulm was part of Kingdom of Württemberg (Q152750) in 1879
4. Agent presents nuanced verification with temporal context
5. Response: "Partially true. Einstein was born in Ulm, which was part of the German Empire
   (Kingdom of Württemberg) in 1879. Modern Germany (Federal Republic) was established 1949."

AGENTESE Path: concept.einstein.witness >> time.1879.manifest >> self.truth.refine
```

#### Journey 3: The Knowledge Gardener
```
User: "Help me explore connections in my field (quantum computing)"

System Flow:
1. QuantumAgent pulls Wikidata items tagged Q2526 (quantum computing)
2. Identifies entity neighborhoods via embedding similarity
3. Finds surprising connections: quantum computing ↔ bird navigation (quantum coherence in biology)
4. User can "plant" new connections, which agent proposes as Wikidata edits
5. Community validation creates positive feedback loop

AGENTESE Path: concept.quantum.manifest(expert_umwelt) >> void.serendipity.sip >> world.wikidata.define
```

### Perennial Evolution

- **Data freshness**: Wikidata updates continuously; agents re-index periodically
- **Emergent expertise**: Agents specialize based on usage patterns (AD-006 polynomial states)
- **Cross-lingual expansion**: Embedding project adds new languages quarterly
- **Community co-evolution**: User corrections improve both agent behavior and Wikidata itself

### Joy-Inducing Elements

- Knowledge "constellations" visualized as Agent Town neighborhoods
- Agents develop personality traits based on their knowledge domains
- "Accursed Share" exploration budget for unexpected connections
- Achievement system for contributing verified knowledge back to Wikidata

---

## Project 2: MetroMind — Urban Intelligence Collective

### Dataset Foundation

**[OpenStreetMap](https://www.openstreetmap.org/)** — Global crowdsourced geographic data, updated continuously by 10M+ contributors.

**[Urbanity Network Dataset](https://www.nature.com/articles/s41597-023-02578-1)** — Comprehensive spatial network data for 50 major cities across 29 countries.

**[Unified Traffic Dataset for 20 U.S. Cities](https://www.nature.com/articles/s41597-024-03149-8)** — City-scale traffic flow, speed, and density data.

**[UrbanBus Dataset](https://academic.oup.com/iti/article/doi/10.1093/iti/liae019/7917135)** — 727M automatic fare collection transactions for bus ridership analysis.

### The Vision

A "digital twin" multi-agent system where citizen-agents represent different urban stakeholders (commuter, planner, business owner, cyclist). Their interactions simulate and predict urban dynamics, enabling participatory city planning.

### Categorical Mapping

| Layer | MetroMind Implementation |
|-------|--------------------------|
| **PolyAgent** | `StakeholderPolynomial` — Positions: {COMMUTING, RESIDING, WORKING, RECREATING, PLANNING} |
| **Operad** | `MOBILITY_OPERAD` — Operations: route, transfer, congest, disperse, develop |
| **Sheaf** | `TrafficCoherence` — Gluing individual trips into network-wide flow patterns |

### User Journeys

#### Journey 1: The City Planner
```
User: "What happens if we add a bike lane on Main Street?"

System Flow:
1. MetroMind spawns 1000 CommutterAgents with varied home/work locations (from OSM)
2. Current routing: 40% drive Main St, 30% transit, 30% other
3. Simulation: Bike lane reduces Main St car capacity by 15%
4. Agent society evolves: Some drivers switch to bikes, others reroute
5. Emergent: New coffee shop traffic pattern identified (business opportunity)
6. Visualization: Before/after traffic flow heatmaps + stakeholder satisfaction metrics

AGENTESE Path: world.mainstreet.refine(planner_umwelt) >> time.future.manifest >> concept.equity.lens
```

#### Journey 2: The Daily Commuter
```
User: "Optimize my commute for next week (I care about reliability > speed)"

System Flow:
1. PersonalMobilityAgent analyzes user's historical patterns
2. Queries real-time traffic + weather + event data
3. Simulates 100 possible weeks using Monte Carlo
4. Considers other commuters' likely responses (game theory via Town operad)
5. Recommends: "Tuesday: Leave 7:15 (event downtown); Friday: WFH (predicted rain delay)"

AGENTESE Path: self.mobility.manifest >> time.nextweek.witness >> void.reliability.sip
```

#### Journey 3: The Neighborhood Advocate
```
User: "Our neighborhood needs better transit. Generate evidence for city council."

System Flow:
1. EquityAgent pulls demographic data + current transit coverage
2. Identifies "transit desert" patterns via network analysis
3. Computes accessibility scores (jobs reachable within 45min)
4. Generates compelling narrative with visualizations
5. Drafts petition with data-backed arguments

AGENTESE Path: world.neighborhood.witness >> concept.equity.manifest >> self.advocacy.define
```

### Perennial Evolution

- **OSM updates**: Community contributions flow continuously
- **Seasonal patterns**: Model evolves with school schedules, weather patterns
- **Infrastructure changes**: New construction auto-incorporated from permits data
- **Behavioral drift**: Agent models update based on observed vs predicted patterns

### Joy-Inducing Elements

- "Mayor for a Day" simulation mode where users can experiment with policy changes
- Neighborhood agents develop distinct personalities (the "quiet suburb" vs "bustling downtown")
- Gamified civic engagement: earn badges for improving data quality
- Time travel: see how your city looked/moved in past decades

---

## Project 3: MoleculeGarden — Collaborative Scientific Discovery

### Dataset Foundation

**[Open Molecules 2025 (OMol25)](https://newscenter.lbl.gov/2025/05/14/computational-chemistry-unlocked-a-record-breaking-dataset-to-train-ai-models-has-launched/)** — Meta + Berkeley Lab's 100M+ molecular simulations, consuming 6 billion compute hours.

**[PubChem 2025](https://academic.oup.com/nar/article/53/D1/D1516/7903365)** — NIH's comprehensive chemical database with compound/bioassay/pathway data.

**[Universal Model for Atoms (UMA)](https://www.webpronews.com/meta-unveils-groundbreaking-open-molecules-2025-a-quantum-leap-in-ai-driven-scientific-research/)** — AI models that perform chemistry calculations 10,000x faster than traditional methods.

### The Vision

A multi-agent scientific research platform where specialized agents represent different scientific disciplines. They collaborate on hypothesis generation, experimental design, and cross-domain discovery—democratizing access to computational chemistry.

### Categorical Mapping

| Layer | MoleculeGarden Implementation |
|-------|-------------------------------|
| **PolyAgent** | `ResearcherPolynomial` — Positions: {HYPOTHESIZING, DESIGNING, SIMULATING, ANALYZING, PUBLISHING} |
| **Operad** | `DISCOVERY_OPERAD` — Operations: propose, test, refute, replicate, synthesize |
| **Sheaf** | `TheoreticalCoherence` — Gluing local findings into globally consistent scientific models |

### User Journeys

#### Journey 1: The Drug Discovery Startup
```
User: "Find candidates for a novel antibiotic targeting [specific bacterial protein]"

System Flow:
1. TargetAgent pulls protein structure from PDB, identifies binding sites
2. ChemistryAgent queries PubChem for known binders of similar proteins
3. SimulationAgent uses UMA to predict binding affinities for 10,000 candidates
4. SafetyAgent cross-references toxicity databases
5. Results: "3 promising candidates identified. Candidate A: high affinity, moderate toxicity.
   Candidate B: moderate affinity, low toxicity, novel scaffold. Candidate C: [PATENTED - caution]"

AGENTESE Path: concept.protein.manifest(researcher_umwelt) >> world.pubchem.lens >> void.novelty.sip
```

#### Journey 2: The Materials Science Researcher
```
User: "Design a material with high thermal conductivity but low electrical conductivity"

System Flow:
1. PropertyAgent defines target constraints mathematically
2. StructureAgent explores OMol25 for materials with similar properties
3. GenerativeAgent proposes novel atomic arrangements using AI
4. ValidationAgent simulates properties using UMA
5. LiteratureAgent checks novelty against existing patents/papers
6. Output: "Proposed: Modified boron nitride structure. Predicted thermal: 350 W/mK, electrical: 10^-15 S/cm.
   No prior art found. Suggested synthesis route: [CVD process from precursors X, Y]"

AGENTESE Path: concept.material.define >> world.omol25.manifest >> self.hypothesis.refine
```

#### Journey 3: The Chemistry Student
```
User: "Help me understand why water has unusual properties"

System Flow:
1. TeacherAgent identifies user's knowledge level from interaction history
2. Pulls relevant molecular simulations from OMol25
3. Generates interactive visualizations of hydrogen bonding
4. Creates "thought experiments": "What if oxygen was less electronegative?"
5. Simulates hypothetical water-like molecules to show contrast
6. Socratic dialogue: "Given what you've seen, why do you think ice floats?"

AGENTESE Path: concept.water.manifest(student_umwelt) >> time.simulation.witness >> self.understanding.refine
```

### Perennial Evolution

- **New simulations**: OMol25 continues expanding; agents incorporate new data
- **Literature integration**: PubChem updates with new papers weekly
- **Model improvements**: UMA updates improve prediction accuracy
- **Discovery feedback**: Real-world experimental validation improves agent models

### Joy-Inducing Elements

- "Molecular Zoo" where users can adopt and nurture interesting molecules
- Collaborative discovery boards where humans + agents co-create hypotheses
- "Accursed Share" exploration: random molecular walks that occasionally find gold
- Achievement system: "First to simulate [novel compound class]"

---

## Project 4: EconWeb — Economic Dynamics Simulator

### Dataset Foundation

**[FRED (Federal Reserve Economic Data)](https://fred.stlouisfed.org/)** — 841,000 economic time series from 118 sources.

**[World Bank Open Data](https://data.worldbank.org/)** — Global development indicators, continuously updated.

**[FinMultiTime Dataset](https://arxiv.org/html/2506.05019v1)** — 112.6GB multimodal financial data: news, tables, charts, prices for 5,105 stocks (2009-2025).

**[IMF Data Portal](https://www.imf.org/en/data)** — Macroeconomic and financial data for 190+ countries.

### The Vision

A heterarchical economic simulation where agents represent economic actors (households, firms, central banks, traders) whose interactions produce emergent market dynamics. Users can explore counterfactual scenarios and develop economic intuition through play.

### Categorical Mapping

| Layer | EconWeb Implementation |
|-------|------------------------|
| **PolyAgent** | `EconomicActorPolynomial` — Positions: {PRODUCING, CONSUMING, INVESTING, TRADING, REGULATING} |
| **Operad** | `MARKET_OPERAD` — Operations: buy, sell, borrow, lend, tax, subsidize |
| **Sheaf** | `EquilibriumCoherence` — Gluing local transactions into global market prices |

### User Journeys

#### Journey 1: The Policy Analyst
```
User: "What happens if the Fed raises rates 50bp while inflation is at 4%?"

System Flow:
1. PolicyAgent sets scenario parameters from current FRED data
2. Spawns 10,000 HouseholdAgents with varying income/debt profiles
3. FirmAgents adjust hiring/investment based on cost of capital
4. BankAgents modify lending standards
5. Simulation runs 24 simulated months, with agent interactions
6. Results: "Unemployment rises 0.8% over 18 months. Housing prices fall 12%.
   Inflation reaches 2.5% by month 20. Distributional impact: [visualization]"

AGENTESE Path: concept.policy.manifest(analyst_umwelt) >> time.future.simulate >> self.impact.witness
```

#### Journey 2: The Individual Investor
```
User: "How should I rebalance my portfolio given current market conditions?"

System Flow:
1. PortfolioAgent analyzes current holdings
2. MacroAgent synthesizes FRED + IMF + news sentiment from FinMultiTime
3. RiskAgent simulates 1000 market scenarios using historical patterns
4. StrategyAgent considers user's stated risk tolerance + time horizon
5. BehavioralAgent accounts for common investor biases
6. Recommendation: "Reduce tech exposure 5% (concentration risk). Add 3% international bonds
   (diversification). Keep 10% cash (opportunity reserve). Rationale: [detailed]"

AGENTESE Path: self.portfolio.manifest >> world.markets.witness >> void.uncertainty.sip
```

#### Journey 3: The Economics Student
```
User: "Help me understand the 2008 financial crisis through simulation"

System Flow:
1. HistoricalAgent loads 2005-2009 FRED data as initial conditions
2. Creates simplified banking system with 100 BankAgents
3. Student can adjust: leverage ratios, risk models, regulatory oversight
4. Simulation reveals cascade dynamics as conditions deteriorate
5. Interactive: "What if banks had 20% capital requirements instead of 3%?"
6. Counterfactual comparison shows alternate history

AGENTESE Path: time.2008.witness >> concept.leverage.refine >> self.understanding.manifest
```

### Perennial Evolution

- **Real-time integration**: FRED updates daily; agents incorporate new data
- **Multi-year backtesting**: Historical simulations improve model fidelity
- **Regime detection**: Agents learn to identify economic phase transitions
- **Policy laboratory**: Central banks could use for scenario planning (B2B opportunity)

### Joy-Inducing Elements

- "Time traveler" mode: experience historical economic events from different perspectives
- Trading game where users compete against agent strategies
- "Butterfly effect" visualizations showing how small changes cascade
- Economic "weather reports" with personality (optimistic bull vs worried bear)

---

## Project 5: ArXivMind — Scientific Literature Intelligence

### Dataset Foundation

**[arXiv](https://arxiv.org/)** — 2.5M+ scientific papers, growing daily, open access.

**[Semantic Scholar API](https://www.semanticscholar.org/)** — Citation graphs, influence scores, paper embeddings.

**[OpenAlex](https://openalex.org/)** — Open catalog of scholarly papers, authors, institutions.

**Research from [LLM-based Scientific Agents Survey](https://arxiv.org/html/2503.24047v1)** — Methodologies for AI-driven scientific discovery.

### The Vision

A research assistant ecosystem where agents specialize in different scientific domains, help researchers navigate literature, identify gaps, and generate novel research directions. The "holographic metaphor reification" principle manifests as agents that embody entire research fields.

### Categorical Mapping

| Layer | ArXivMind Implementation |
|-------|--------------------------|
| **PolyAgent** | `ScholarPolynomial` — Positions: {SURVEYING, CRITIQUING, CONNECTING, PROPOSING, WRITING} |
| **Operad** | `RESEARCH_OPERAD` — Operations: cite, build_upon, challenge, synthesize, replicate |
| **Sheaf** | `LiteratureCoherence` — Gluing local paper readings into coherent field understanding |

### User Journeys

#### Journey 1: The PhD Student
```
User: "I'm starting research on [topic]. Create a literature map."

System Flow:
1. DomainAgent queries arXiv/Semantic Scholar for relevant papers (last 5 years)
2. CitationAgent builds influence graph (who cites whom)
3. ClusterAgent identifies research subcommunities via embedding similarity
4. GapAgent finds underexplored intersections between clusters
5. TrendAgent identifies rising vs declining topics
6. Output: Interactive map with:
   - Core papers (must read)
   - Methodological schools (approaches)
   - Open questions (opportunities)
   - Key researchers (potential collaborators)

AGENTESE Path: concept.field.manifest(novice_umwelt) >> world.arxiv.lens >> self.understanding.define
```

#### Journey 2: The Research Lab PI
```
User: "Monitor my field and alert me to important developments"

System Flow:
1. SentinelAgent establishes baseline from user's publication history
2. Daily: Scans new arXiv submissions for relevance
3. Filters: Novel methods > incremental improvements
4. Summarizes: Key findings in 2-3 sentences
5. Contextualizes: "This contradicts your 2023 paper because..."
6. Weekly digest with priority rankings

AGENTESE Path: time.daily.manifest >> world.arxiv.witness >> self.research.refine
```

#### Journey 3: The Cross-Disciplinary Innovator
```
User: "Find connections between [field A] and [field B] that nobody has explored"

System Flow:
1. Spawns FieldAAgent and FieldBAgent (specialized in each domain)
2. Agents independently build concept embeddings of their fields
3. BridgeAgent finds concept pairs with high embedding similarity but low citation overlap
4. NoveltyAgent verifies no existing papers at intersection
5. IdeaAgent generates 5 potential research directions
6. Output: "Intersection discovered: [Concept X] from cryptography maps structurally to
   [Concept Y] in neuroscience. No papers found. Proposed research question: [...]"

AGENTESE Path: concept.fieldA.manifest >> concept.fieldB.manifest >> void.novelty.sip >> self.hypothesis.define
```

### Perennial Evolution

- **Daily growth**: arXiv adds ~1000 papers/day; agents continuously index
- **Citation dynamics**: Influence scores update as papers get cited
- **Field drift**: Agent specializations evolve with research trends
- **Collective intelligence**: Cross-user patterns identify emerging hot topics

### Joy-Inducing Elements

- "Research genealogy" visualizations showing intellectual lineage
- Agent debates: Watch two field-agents argue about competing paradigms
- "Serendipity mode": Accursed Share exploration of random paper connections
- Collaborative writing: Co-author papers with specialized agents

---

## Cross-Project Synergies

The five projects share the kgents categorical foundation and can interoperate:

| Integration | Example |
|-------------|---------|
| WikiVerse + ArXivMind | Scientific papers linked to Wikidata entities for fact-grounding |
| MetroMind + EconWeb | Urban development simulations with economic impact analysis |
| MoleculeGarden + ArXivMind | Auto-literature review for any chemical compound |
| WikiVerse + MetroMind | Geographic entities enriched with encyclopedic context |
| EconWeb + MoleculeGarden | Supply chain modeling for new materials |

### The Meta-Pattern

All five projects instantiate the same structure:

```python
PROJECT = {
    "polynomial": DomainPolynomial,      # State machine for domain entities
    "operad": DOMAIN_OPERAD,             # Composition grammar
    "sheaf": DomainCoherence,            # Local → Global consistency
    "data": [OpenDataset1, ...],         # Continuously updated sources
    "agents": [SpecializedAgent1, ...],  # Domain-embodying citizens
}
```

This is AD-006 (Unified Categorical Foundation) applied at portfolio scale.

---

## Implementation Priority

Based on `_focus.md` alignment:

| Project | Focus Alignment | Effort | Impact | Priority |
|---------|-----------------|--------|--------|----------|
| **WikiVerse** | Holographic metaphor reification, knowledge | Medium | High | 1 |
| **ArXivMind** | Builder's Workshop (researchers as builders) | Medium | High | 2 |
| **MetroMind** | Agent Town expansion, visual UI | High | Very High | 3 |
| **MoleculeGarden** | B-gent scientific discovery, democratization | High | Very High | 4 |
| **EconWeb** | Revenue opportunity (B2B), emergent dynamics | Medium | High | 5 |

**Recommended Start**: WikiVerse (leverages existing Wikidata Embedding Project infrastructure) as proof-of-concept for the categorical pattern, then expand to ArXivMind for B2B research tool potential.

---

## Sources

### Wikidata & Knowledge Graphs
- [Wikidata Embedding Project](https://www.wikidata.org/wiki/Wikidata:Embedding_Project)
- [Wikidata and AI: Simplified Access](https://diff.wikimedia.org/2024/09/23/wikidata-and-artificial-intelligence-simplified-access-to-open-data-for-open-source-projects/)
- [LLM-Empowered Knowledge Graph Construction Survey](https://arxiv.org/html/2510.20345v1)

### Urban & Transportation
- [Unified Traffic Dataset for 20 U.S. Cities](https://www.nature.com/articles/s41597-024-03149-8)
- [Urbanity Global Network Dataset](https://www.nature.com/articles/s41597-023-02578-1)
- [CitySim: LLM-Driven Urban Simulation](https://arxiv.org/html/2506.21805v1)
- [Awesome Urban Datasets (GitHub)](https://github.com/urban-toolkit/awesome-urban-datasets)

### Scientific Discovery
- [Open Molecules 2025 (Berkeley Lab)](https://newscenter.lbl.gov/2025/05/14/computational-chemistry-unlocked-a-record-breaking-dataset-to-train-ai-models-has-launched/)
- [PubChem 2025 Update](https://academic.oup.com/nar/article/53/D1/D1516/7903365)
- [LLM-based Scientific Agents Survey](https://arxiv.org/html/2503.24047v1)

### Economic & Financial
- [FRED Economic Data](https://fred.stlouisfed.org/)
- [FinMultiTime Dataset](https://arxiv.org/html/2506.05019v1)
- [IMF Data Portal](https://www.imf.org/en/data)

### Multi-Agent Systems
- [OASIS: One Million Agent Simulations](https://www.analyticsvidhya.com/blog/2025/02/open-source-datasets-for-generative-and-agentic-ai/)
- [Multi-Agent Collaboration Survey](https://arxiv.org/html/2501.06322v1)

---

*"Plans are worthless, but planning is everything." — Eisenhower*
