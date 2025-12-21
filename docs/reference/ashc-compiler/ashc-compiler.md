# ASHC Compiler

> *Agentic Self-Hosting Compiler: empirical verification via trace accumulation.*

---

## protocols.ashc.__init__

## __init__

```python
module __init__
```

ASHC - Agentic Self-Hosting Compiler

---

## protocols.ashc.adaptive

## adaptive

```python
module adaptive
```

ASHC Adaptive Evidence Framework

---

## beta_pdf

```python
def beta_pdf(x: float, alpha: float, beta: float) -> float
```

Beta distribution PDF (unnormalized, for comparison only).

---

## beta_mean

```python
def beta_mean(alpha: float, beta: float) -> float
```

Expected value of Beta(α, β) = α / (α + β).

---

## beta_variance

```python
def beta_variance(alpha: float, beta: float) -> float
```

Variance of Beta(α, β).

---

## incomplete_beta_regularized

```python
def incomplete_beta_regularized(x: float, a: float, b: float) -> float
```

Regularized incomplete beta function I_x(a, b).

---

## prob_greater_than

```python
def prob_greater_than(alpha: float, beta: float, threshold: float) -> float
```

P(p > threshold) for p ~ Beta(α, β).

---

## prob_less_than

```python
def prob_less_than(alpha: float, beta: float, threshold: float) -> float
```

P(p < threshold) for p ~ Beta(α, β).

---

## ConfidenceTier

```python
class ConfidenceTier(str, Enum)
```

Tiered confidence levels for adaptive sampling.

---

## BetaPrior

```python
class BetaPrior
```

Beta distribution prior for success probability.

---

## StoppingDecision

```python
class StoppingDecision(str, Enum)
```

Decision from stopping rule.

---

## StoppingConfig

```python
class StoppingConfig
```

Configuration for adaptive stopping.

---

## StoppingState

```python
class StoppingState
```

Mutable state for tracking stopping decisions.

---

## AdaptiveRunResult

```python
class AdaptiveRunResult
```

Result of a single run in adaptive sampling.

---

## AdaptiveEvidence

```python
class AdaptiveEvidence
```

Evidence gathered through adaptive sampling.

---

## AdaptiveCompiler

```python
class AdaptiveCompiler
```

Compile spec with adaptive evidence gathering.

---

## expected_samples_for_ndiff

```python
def expected_samples_for_ndiff(true_p: float, n_diff: int) -> float
```

Expected number of samples to reach n_diff margin.

---

## reliability_boost_from_voting

```python
def reliability_boost_from_voting(base_p: float, n_votes: int) -> float
```

Reliability after majority voting with n_votes.

---

## adaptive_compile

```python
async def adaptive_compile(spec: str, test_code: str | None=None, tier: ConfidenceTier=ConfidenceTier.UNKNOWN) -> AdaptiveEvidence
```

Convenience function for adaptive compilation.

---

## print_evidence_summary

```python
def print_evidence_summary(evidence: AdaptiveEvidence) -> str
```

Pretty-print evidence summary.

---

## uniform

```python
def uniform(cls) -> 'BetaPrior'
```

Uniform prior: no prior information.

---

## from_confidence

```python
def from_confidence(cls, tier: ConfidenceTier) -> 'BetaPrior'
```

Create prior from confidence tier.

---

## from_estimate

```python
def from_estimate(cls, success_rate: float, strength: float=10.0) -> 'BetaPrior'
```

Create prior from estimated success rate.

---

## mean

```python
def mean(self) -> float
```

Expected success rate.

---

## variance

```python
def variance(self) -> float
```

Variance of success rate belief.

---

## confidence_interval_95

```python
def confidence_interval_95(self) -> tuple[float, float]
```

95% credible interval for success rate.

---

## update

```python
def update(self, successes: int, failures: int) -> 'BetaPrior'
```

Bayesian update: prior + data → posterior.

---

## prob_success_above

```python
def prob_success_above(self, threshold: float) -> float
```

P(success_rate > threshold).

---

## prob_success_below

```python
def prob_success_below(self, threshold: float) -> float
```

P(success_rate < threshold).

---

## for_tier

```python
def for_tier(cls, tier: ConfidenceTier) -> 'StoppingConfig'
```

Create stopping config appropriate for confidence tier.

---

## total_samples

```python
def total_samples(self) -> int
```

Total samples observed.

---

## posterior

```python
def posterior(self) -> BetaPrior
```

Current posterior belief.

---

## margin

```python
def margin(self) -> int
```

Current margin (|successes - failures|).

---

## leading_outcome

```python
def leading_outcome(self) -> str
```

Which outcome is currently leading.

---

## observe

```python
def observe(self, success: bool) -> StoppingDecision
```

Observe a new sample and update decision.

---

## from_verification

```python
def from_verification(cls, test_report: TestReport, type_report: TypeReport, lint_report: LintReport, duration_ms: float) -> 'AdaptiveRunResult'
```

Create from verification results.

---

## sample_count

```python
def sample_count(self) -> int
```

Number of samples taken.

---

## success_count

```python
def success_count(self) -> int
```

Number of successful runs.

---

## success_rate

```python
def success_rate(self) -> float
```

Observed success rate.

---

## posterior_mean

```python
def posterior_mean(self) -> float
```

Expected success rate given evidence.

---

## confidence_interval

```python
def confidence_interval(self) -> tuple[float, float]
```

95% credible interval for success rate.

---

## is_success

```python
def is_success(self) -> bool
```

Did we conclude success?

---

## is_failure

```python
def is_failure(self) -> bool
```

Did we conclude failure?

---

## is_uncertain

```python
def is_uncertain(self) -> bool
```

Are we still uncertain?

---

## savings_vs_fixed

```python
def savings_vs_fixed(self) -> float
```

Estimated savings vs running fixed max_samples.

---

## __init__

```python
def __init__(self, generate_fn: Callable[[str], Awaitable[str]] | None=None, estimate_fn: Callable[[str], Awaitable[float]] | None=None)
```

Initialize adaptive compiler.

---

## compile

```python
async def compile(self, spec: str, test_code: str | None=None, tier: ConfidenceTier | None=None, prior: BetaPrior | None=None, config: StoppingConfig | None=None) -> AdaptiveEvidence
```

Compile with adaptive evidence gathering.

---

## protocols.ashc.adversary

## adversary

```python
module adversary
```

ASHC Adversarial Accountability

---

## BetSettlement

```python
class BetSettlement
```

The settlement of a bet after outcome is known.

---

## AdversarialAccountability

```python
class AdversarialAccountability
```

The implicit adversary taking the other side of ASHC bets.

---

## create_settlement_report

```python
def create_settlement_report(settlements: list[BetSettlement]) -> dict[str, object]
```

Create a summary report of bet settlements.

---

## ashc_won

```python
def ashc_won(self) -> bool
```

Did ASHC win this bet?

---

## was_expensive

```python
def was_expensive(self) -> bool
```

Was this a significant loss for ASHC?

---

## settle_bet

```python
def settle_bet(self, bet: ASHCBet, credibility: ASHCCredibility) -> BetSettlement
```

Settle a bet after outcome is known.

---

## adversary_win_rate

```python
def adversary_win_rate(self) -> float
```

What fraction of bets did the adversary win?

---

## average_payout

```python
def average_payout(self) -> Decimal
```

Average payout per adversary win.

---

## ashc_is_profitable

```python
def ashc_is_profitable(self) -> bool
```

Is ASHC winning more than losing?

---

## reset

```python
def reset(self) -> None
```

Reset adversary state (for testing or new epoch).

---

## protocols.ashc.ast

## ast

```python
module ast
```

L0 Kernel AST Types

---

## L0Pattern

```python
class L0Pattern
```

Base class for structural patterns.

---

## LiteralPattern

```python
class LiteralPattern(L0Pattern)
```

Match exact value.

---

## WildcardPattern

```python
class WildcardPattern(L0Pattern)
```

Match anything, bind to name.

---

## DictPattern

```python
class DictPattern(L0Pattern)
```

Match dictionary structure.

---

## ListPattern

```python
class ListPattern(L0Pattern)
```

Match list structure.

---

## L0Handle

```python
class L0Handle
```

Reference to a defined value. Not the value itself.

---

## L0Literal

```python
class L0Literal
```

A literal value (string, number, dict, list, etc.).

---

## L0Call

```python
class L0Call
```

Call a Python callable with arguments.

---

## L0Compose

```python
class L0Compose
```

Compose two expressions: f >> g

---

## L0MatchExpr

```python
class L0MatchExpr
```

Structural pattern match expression.

---

## L0Define

```python
class L0Define
```

Define a named value.

---

## L0Emit

```python
class L0Emit
```

Emit an artifact.

---

## L0Witness

```python
class L0Witness
```

Emit a witness (full capture).

---

## L0ProgramAST

```python
class L0ProgramAST
```

A complete L0 program.

---

## from_dict

```python
def from_dict(cls, d: dict[str, L0Pattern], allow_extra: bool=False) -> DictPattern
```

Create from a regular dict for convenience.

---

## from_dict

```python
def from_dict(cls, fn: Callable[..., Any], args: dict[str, Any]) -> L0Call
```

Create from a regular dict for convenience.

---

## definitions

```python
def definitions(self) -> tuple[L0Define, ...]
```

Extract all definitions from statements.

---

## emissions

```python
def emissions(self) -> tuple[L0Emit, ...]
```

Extract all emit statements.

---

## witnesses

```python
def witnesses(self) -> tuple[L0Witness, ...]
```

Extract all witness statements.

---

## protocols.ashc.bootstrap.__init__

## __init__

```python
module __init__
```

ASHC Bootstrap Regeneration Module

---

## protocols.ashc.bootstrap.isomorphism

## isomorphism

```python
module isomorphism
```

ASHC Bootstrap Isomorphism Checker

---

## BehaviorComparison

```python
class BehaviorComparison
```

Result of comparing two implementations' behavior.

---

## BootstrapIsomorphism

```python
class BootstrapIsomorphism
```

Overall result of bootstrap regeneration.

---

## check_isomorphism

```python
async def check_isomorphism(generated_code: str, agent_name: str, run_tests: bool=True, run_types: bool=True) -> BehaviorComparison
```

Compare generated code against installed implementation.

---

## compare_all_agents

```python
async def compare_all_agents(generated_codes: dict[str, str]) -> BootstrapIsomorphism
```

Compare all generated agents against installed.

---

## is_isomorphic

```python
def is_isomorphic(self) -> bool
```

Behavioral isomorphism requires all checks to pass.

---

## score

```python
def score(self) -> float
```

Numerical isomorphism score 0.0-1.0.

---

## overall_score

```python
def overall_score(self) -> float
```

Average isomorphism score across all agents.

---

## is_isomorphic

```python
def is_isomorphic(self) -> bool
```

All agents are behaviorally isomorphic.

---

## isomorphic_count

```python
def isomorphic_count(self) -> int
```

Number of isomorphic agents.

---

## summary

```python
def summary(self) -> str
```

Human-readable summary.

---

## protocols.ashc.bootstrap.parser

## parser

```python
module parser
```

ASHC Bootstrap Spec Parser

---

## BootstrapAgentSpec

```python
class BootstrapAgentSpec
```

Parsed specification for a single bootstrap agent.

---

## ParseResult

```python
class ParseResult
```

Result of parsing the bootstrap spec.

---

## parse_bootstrap_spec

```python
def parse_bootstrap_spec(spec_path: Path | None=None) -> tuple[BootstrapAgentSpec, ...]
```

Parse spec/bootstrap.md into individual agent specs.

---

## parse_bootstrap_spec_detailed

```python
def parse_bootstrap_spec_detailed(spec_path: Path | None=None) -> ParseResult
```

Parse with detailed error reporting.

---

## get_spec_for_agent

```python
def get_spec_for_agent(name: str, spec_path: Path | None=None) -> BootstrapAgentSpec | None
```

Get spec for a single agent by name.

---

## format_spec_summary

```python
def format_spec_summary(specs: tuple[BootstrapAgentSpec, ...]) -> str
```

Format specs for display.

---

## spec_hash

```python
def spec_hash(self) -> str
```

Content-addressed identifier for the spec.

---

## has_laws

```python
def has_laws(self) -> bool
```

Does this spec define laws?

---

## success

```python
def success(self) -> bool
```

All 7 agents parsed successfully.

---

## agent_names

```python
def agent_names(self) -> set[str]
```

Names of successfully parsed agents.

---

## protocols.ashc.bootstrap.regenerator

## regenerator

```python
module regenerator
```

ASHC Bootstrap Regenerator

---

## RegenerationConfig

```python
class RegenerationConfig
```

Configuration for bootstrap regeneration.

---

## make_generation_prompt

```python
def make_generation_prompt(spec: BootstrapAgentSpec) -> str
```

Build generation prompt from agent spec.

---

## make_simple_prompt

```python
def make_simple_prompt(spec: BootstrapAgentSpec) -> str
```

Simplified prompt for basic agents like Id.

---

## BootstrapRegenerator

```python
class BootstrapRegenerator
```

Regenerate bootstrap from spec using VoidHarness.

---

## regenerate_bootstrap

```python
async def regenerate_bootstrap(agents: list[str] | None=None, config: RegenerationConfig | None=None) -> BootstrapIsomorphism
```

Quick regeneration of bootstrap.

---

## regenerate_single

```python
async def regenerate_single(agent_name: str, config: RegenerationConfig | None=None) -> BehaviorComparison
```

Regenerate a single agent.

---

## main

```python
def main() -> None
```

CLI entry point for bootstrap regeneration.

---

## __init__

```python
def __init__(self, spec_path: Path | None=None, config: RegenerationConfig | None=None)
```

Initialize the regenerator.

---

## specs

```python
def specs(self) -> tuple[BootstrapAgentSpec, ...]
```

Lazy-loaded parsed specs.

---

## regenerate

```python
async def regenerate(self, agents: list[str] | None=None) -> BootstrapIsomorphism
```

Regenerate bootstrap and check isomorphism.

---

## regenerate_agent

```python
async def regenerate_agent(self, name: str) -> BehaviorComparison
```

Regenerate a single agent.

---

## protocols.ashc.causal_graph

## causal_graph

```python
module causal_graph
```

ASHC Causal Graph Learning

---

## CausalEdge

```python
class CausalEdge
```

A tracked relationship between a nudge and its outcome.

---

## text_similarity

```python
def text_similarity(a: str, b: str) -> float
```

Compute text similarity between two strings.

---

## nudge_similarity

```python
def nudge_similarity(n1: Nudge, n2: Nudge) -> float
```

Compute similarity between two nudges.

---

## is_similar_nudge

```python
def is_similar_nudge(n1: Nudge, n2: Nudge, threshold: float=0.7) -> bool
```

Check if two nudges are similar enough to be considered related.

---

## CausalGraph

```python
class CausalGraph
```

Graph of nudge → outcome relationships.

---

## CausalLearner

```python
class CausalLearner
```

Learn causal relationships from evidence runs.

---

## create_edge

```python
def create_edge(location: str, before: str, after: str, reason: str, outcome_delta: float, confidence: float=0.5, runs_observed: int=1) -> CausalEdge
```

Convenience function to create a CausalEdge.

---

## build_graph_from_edges

```python
def build_graph_from_edges(edges: list[CausalEdge]) -> CausalGraph
```

Build a CausalGraph from a list of edges.

---

## is_beneficial

```python
def is_beneficial(self) -> bool
```

Did this nudge improve outcomes?

---

## is_harmful

```python
def is_harmful(self) -> bool
```

Did this nudge harm outcomes?

---

## is_neutral

```python
def is_neutral(self) -> bool
```

Did this nudge have no significant effect?

---

## effect_size

```python
def effect_size(self) -> str
```

Categorize the effect size.

---

## with_observation

```python
def with_observation(self, new_delta: float, weight: float=1.0) -> 'CausalEdge'
```

Update edge with a new observation.

---

## edge_count

```python
def edge_count(self) -> int
```

Number of edges in the graph.

---

## total_observations

```python
def total_observations(self) -> int
```

Total number of run observations across all edges.

---

## predict_outcome

```python
def predict_outcome(self, proposed_nudge: Nudge) -> float
```

Predict outcome of a new nudge based on history.

---

## predict_with_confidence

```python
def predict_with_confidence(self, proposed_nudge: Nudge) -> tuple[float, float]
```

Predict outcome with confidence interval.

---

## stability_score

```python
def stability_score(self) -> float
```

How stable are outcomes under small nudges?

---

## beneficial_edges

```python
def beneficial_edges(self) -> list[CausalEdge]
```

Get edges where the nudge improved outcomes.

---

## harmful_edges

```python
def harmful_edges(self) -> list[CausalEdge]
```

Get edges where the nudge harmed outcomes.

---

## with_edge

```python
def with_edge(self, edge: CausalEdge) -> 'CausalGraph'
```

Add or update an edge in the graph.

---

## merge

```python
def merge(self, other: 'CausalGraph') -> 'CausalGraph'
```

Merge another graph into this one.

---

## verify_causal_monotonicity

```python
def verify_causal_monotonicity(self, tolerance: float=0.15) -> bool
```

Verify the Causal Monotonicity law.

---

## causal_monotonicity_violations

```python
def causal_monotonicity_violations(self, tolerance: float=0.15) -> list[tuple[CausalEdge, CausalEdge, float]]
```

Find all violations of causal monotonicity.

---

## observe_run

```python
def observe_run(self, run: 'Run', baseline_pass_rate: float | None=None) -> None
```

Observe a run and update the causal graph.

---

## observe_evidence

```python
def observe_evidence(self, evidence: 'Evidence', baseline_pass_rate: float | None=None) -> None
```

Observe all runs in an evidence corpus.

---

## compare_with_without

```python
def compare_with_without(self, runs_with_nudge: list['Run'], runs_without_nudge: list['Run'], nudge: Nudge) -> CausalEdge
```

Compare runs with and without a nudge to compute causal effect.

---

## suggest_nudge

```python
def suggest_nudge(self, goal: str='improve') -> Nudge | None
```

Suggest a nudge based on historical effectiveness.

---

## protocols.ashc.causal_penalty

## causal_penalty

```python
module causal_penalty
```

ASHC Causal Penalty Propagation

---

## CausalPenalty

```python
class CausalPenalty
```

A penalty propagated to principles/evidence that caused a failure.

---

## PrincipleCredibility

```python
class PrincipleCredibility
```

Track credibility for a single principle.

---

## PrincipleRegistry

```python
class PrincipleRegistry
```

Registry of all principle credibilities.

---

## blame_for_principle

```python
def blame_for_principle(self, principle_id: str) -> float
```

Get the blame amount for a specific principle.

---

## blame_for_evidence

```python
def blame_for_evidence(self, evidence_id: str) -> float
```

Get the blame amount for a specific piece of evidence.

---

## from_bet

```python
def from_bet(cls, bet: ASHCBet, penalty_amount: float, principle_weights: dict[str, float] | None=None, evidence_weights: dict[str, float] | None=None) -> 'CausalPenalty'
```

Create a causal penalty from a failed bet.

---

## cite

```python
def cite(self) -> None
```

Record that this principle was cited in a decision.

---

## blame

```python
def blame(self, weight: float) -> None
```

Reduce credibility when this principle led to failure.

---

## reward

```python
def reward(self, weight: float=0.01) -> None
```

Slightly increase credibility when this principle led to success.

---

## blame_rate

```python
def blame_rate(self) -> float
```

What fraction of citations led to blame?

---

## is_discredited

```python
def is_discredited(self) -> bool
```

Has this principle lost all credibility?

---

## is_predictive

```python
def is_predictive(self) -> bool
```

Is this principle predictive of success?

---

## get_or_create

```python
def get_or_create(self, principle_id: str) -> PrincipleCredibility
```

Get principle credibility, creating if needed.

---

## cite_all

```python
def cite_all(self, principle_ids: tuple[str, ...]) -> None
```

Record citation for multiple principles.

---

## apply_penalty

```python
def apply_penalty(self, penalty: CausalPenalty) -> None
```

Apply a causal penalty to all cited principles.

---

## apply_reward

```python
def apply_reward(self, principle_ids: tuple[str, ...], weight: float=0.01) -> None
```

Reward principles that led to success.

---

## discredited_principles

```python
def discredited_principles(self) -> list[str]
```

Get list of principles that have lost all credibility.

---

## predictive_principles

```python
def predictive_principles(self) -> list[str]
```

Get list of principles that are predictive of success.

---

## credibility_ranking

```python
def credibility_ranking(self) -> list[tuple[str, float]]
```

Get principles ranked by credibility (highest first).

---

## effective_weight

```python
def effective_weight(self, principle_id: str) -> float
```

Get the effective weight for a principle in future decisions.

---

## protocols.ashc.economy

## economy

```python
module economy
```

ASHC Economic Accountability Layer

---

## ASHCBet

```python
class ASHCBet
```

A wager ASHC places on a compilation outcome.

---

## ASHCCredibility

```python
class ASHCCredibility
```

ASHC's credibility score.

---

## AllocationStrategy

```python
class AllocationStrategy
```

Computed allocation strategy for a compilation.

---

## ASHCEconomy

```python
class ASHCEconomy
```

Economic layer for ASHC: cost-aware resource allocation.

---

## was_bullshit

```python
def was_bullshit(self) -> bool
```

High confidence + failure = bullshit.

---

## calibration_error

```python
def calibration_error(self) -> float
```

How far off was the confidence from reality?

---

## is_well_calibrated

```python
def is_well_calibrated(self) -> bool
```

Was the confidence within 10% of actual outcome?

---

## resolve

```python
def resolve(self, success: bool) -> 'ASHCBet'
```

Create a resolved copy of this bet.

---

## create

```python
def create(cls, spec: str, confidence: float, stake: Decimal, principles: tuple[str, ...]=(), evidence: tuple[str, ...]=(), reasoning: tuple[str, ...]=()) -> 'ASHCBet'
```

Create a new bet on a spec.

---

## record_outcome

```python
def record_outcome(self, bet: ASHCBet) -> None
```

Update credibility based on bet outcome.

---

## confidence_multiplier

```python
def confidence_multiplier(self) -> float
```

Discount future confidence claims by current credibility.

---

## is_bankrupt

```python
def is_bankrupt(self) -> bool
```

At zero credibility, ASHC should refuse to operate.

---

## average_calibration_error

```python
def average_calibration_error(self) -> float
```

How well-calibrated is ASHC on average?

---

## bullshit_rate

```python
def bullshit_rate(self) -> float
```

What fraction of bets were bullshit?

---

## success_rate

```python
def success_rate(self) -> float
```

What fraction of bets succeeded?

---

## bets_to_recover

```python
def bets_to_recover(self) -> int
```

How many successful bets needed to reach full credibility?

---

## remaining

```python
def remaining(self) -> Decimal
```

Remaining budget.

---

## can_afford

```python
def can_afford(self, cost: Decimal) -> bool
```

Check if budget allows this cost.

---

## spend

```python
def spend(self, amount: Decimal) -> bool
```

Spend from budget.

---

## optimal_allocation

```python
def optimal_allocation(self, prior: BetaPrior, credibility: ASHCCredibility, n_diff: int=2) -> AllocationStrategy
```

Compute optimal resource allocation.

---

## stake_for_confidence

```python
def stake_for_confidence(self, confidence: float) -> Decimal
```

Compute stake amount based on confidence.

---

## protocols.ashc.evidence

## evidence

```python
module evidence
```

ASHC Evidence Accumulation Engine

---

## Nudge

```python
class Nudge
```

A single adjustment to the prompt/spec.

---

## Run

```python
class Run
```

A single execution of spec → implementation with verification.

---

## Evidence

```python
class Evidence
```

Accumulated evidence for spec↔impl equivalence.

---

## ASHCOutput

```python
class ASHCOutput
```

The compiler's output: executable + evidence.

---

## EvidenceCompiler

```python
class EvidenceCompiler
```

Compile spec to executable with evidence accumulation.

---

## compile_spec

```python
async def compile_spec(spec: str, n_variations: int=10, test_code: str | None=None) -> ASHCOutput
```

Convenience function to compile a spec with evidence.

---

## quick_verify

```python
async def quick_verify(code: str, test_code: str | None=None) -> Run | None
```

Quick verification of a single implementation.

---

## passed

```python
def passed(self) -> bool
```

Did this run pass all verification?

---

## test_pass_rate

```python
def test_pass_rate(self) -> float
```

Fraction of tests that passed.

---

## verification_score

```python
def verification_score(self) -> float
```

Combined verification score (0.0 - 1.0).

---

## run_count

```python
def run_count(self) -> int
```

Number of runs in the corpus.

---

## pass_count

```python
def pass_count(self) -> int
```

Number of runs that passed all verification.

---

## pass_rate

```python
def pass_rate(self) -> float
```

Fraction of runs that passed (0.0 - 1.0).

---

## equivalence_score

```python
def equivalence_score(self) -> float
```

Overall equivalence score (0.0 - 1.0).

---

## average_verification_score

```python
def average_verification_score(self) -> float
```

Average verification score across all runs.

---

## best_run

```python
def best_run(self) -> Run | None
```

Return the run with highest verification score.

---

## is_verified

```python
def is_verified(self) -> bool
```

Is there sufficient evidence for this executable?

---

## confidence

```python
def confidence(self) -> float
```

Confidence level (0.0 - 1.0).

---

## __init__

```python
def __init__(self, generate_fn: Callable[[str], Awaitable[str]] | None=None)
```

Initialize the compiler.

---

## compile

```python
async def compile(self, spec: str, n_variations: int=10, test_code: str | None=None, run_tests: bool=True, run_types: bool=True, run_lint: bool=True, timeout: float=60.0) -> ASHCOutput
```

Main compilation loop.

---

## compile_with_nudges

```python
async def compile_with_nudges(self, spec: str, nudges: list[Nudge], n_variations: int=10, test_code: str | None=None) -> ASHCOutput
```

Compile with tracked nudges for causal analysis.

---

## protocols.ashc.examples.bootstrap

## bootstrap

```python
module bootstrap
```

Bootstrap Example

---

## main

```python
async def main() -> None
```

Run bootstrap example.

---

## protocols.ashc.examples.compose

## compose

```python
module compose
```

Composition Example

---

## main

```python
async def main() -> None
```

Run composition example.

---

## protocols.ashc.examples.minimal

## minimal

```python
module minimal
```

Minimal L0 Example

---

## main

```python
async def main() -> None
```

Run minimal L0 program.

---

## protocols.ashc.harness

## harness

```python
module harness
```

ASHC VoidHarness: Isolated LLM Execution Environment

---

## VoidHarnessConfig

```python
class VoidHarnessConfig
```

Configuration for VoidHarness execution environment.

---

## TokenBudget

```python
class TokenBudget
```

Track and limit token usage across harness lifetime.

---

## GenerationResult

```python
class GenerationResult
```

Result from a single LLM generation.

---

## SubprocessResult

```python
class SubprocessResult
```

Result of a subprocess execution.

---

## VoidHarness

```python
class VoidHarness
```

Isolated Claude CLI execution environment.

---

## generate_from_spec

```python
async def generate_from_spec(spec: str, config: VoidHarnessConfig | None=None) -> str
```

Quick generation from spec.

---

## generate_n_from_spec

```python
async def generate_n_from_spec(spec: str, n: int, config: VoidHarnessConfig | None=None) -> list[GenerationResult | BaseException]
```

Generate n variations from spec.

---

## remaining

```python
def remaining(self) -> int
```

Remaining token budget.

---

## exhausted

```python
def exhausted(self) -> bool
```

Is budget exhausted?

---

## warning_threshold_reached

```python
def warning_threshold_reached(self) -> bool
```

Should we warn about approaching limit?

---

## consume

```python
def consume(self, tokens: int) -> None
```

Consume tokens from budget.

---

## has_code

```python
def has_code(self) -> bool
```

Did generation produce any code?

---

## __init__

```python
def __init__(self, config: VoidHarnessConfig | None=None, budget: TokenBudget | None=None)
```

Initialize the harness.

---

## generate

```python
async def generate(self, spec: str) -> str
```

Generate implementation from spec.

---

## generate_detailed

```python
async def generate_detailed(self, spec: str) -> GenerationResult
```

Generate implementation with full metadata.

---

## generate_n

```python
async def generate_n(self, spec: str, n: int) -> list[GenerationResult | BaseException]
```

Generate n variations concurrently.

---

## generation_count

```python
def generation_count(self) -> int
```

Total number of generations performed.

---

## tokens_used

```python
def tokens_used(self) -> int
```

Total tokens consumed so far.

---

## tokens_remaining

```python
def tokens_remaining(self) -> int
```

Tokens remaining in budget.

---

## budget_exhausted

```python
def budget_exhausted(self) -> bool
```

Is the token budget exhausted?

---

## is_available

```python
def is_available(cls) -> bool
```

Check if Claude CLI is available on the system.

---

## protocols.ashc.llm_compiler

## llm_compiler

```python
module llm_compiler
```

ASHC LLM Compiler: Wire VoidHarness to Evidence/Adaptive Compilers

---

## compile_with_llm

```python
async def compile_with_llm(spec: str, n_variations: int=10, test_code: str | None=None, harness_config: VoidHarnessConfig | None=None, budget: TokenBudget | None=None, run_tests: bool=True, run_types: bool=True, run_lint: bool=True, timeout: float=60.0) -> ASHCOutput
```

Compile spec using real LLM generation.

### Examples
```python
>>> output = await compile_with_llm(
```
```python
>>> print(f"Pass rate: {output.evidence.pass_rate:.0%}")
```

---

## adaptive_compile_with_llm

```python
async def adaptive_compile_with_llm(spec: str, test_code: str | None=None, tier: ConfidenceTier=ConfidenceTier.UNCERTAIN, harness_config: VoidHarnessConfig | None=None, budget: TokenBudget | None=None) -> AdaptiveEvidence
```

Compile spec with adaptive Bayesian stopping using real LLM.

### Examples
```python
>>> evidence = await adaptive_compile_with_llm(
```
```python
>>> print(f"Stopped after {evidence.sample_count} samples")
```
```python
>>> print(f"Saved {evidence.savings_vs_fixed:.0%} vs fixed-N")
```

---

## compile_with_nudges

```python
async def compile_with_nudges(spec: str, nudges: list[Nudge], n_variations: int=10, test_code: str | None=None, harness_config: VoidHarnessConfig | None=None, budget: TokenBudget | None=None) -> ASHCOutput
```

Compile spec with tracked nudges for causal analysis.

### Examples
```python
>>> nudge = Nudge(
```
```python
>>> output = await compile_with_nudges(spec, [nudge])
```

---

## learn_causal_graph

```python
async def learn_causal_graph(specs_with_nudges: list[tuple[str, list[Nudge]]], test_code: str | None=None, n_per_spec: int=5, harness_config: VoidHarnessConfig | None=None, budget: TokenBudget | None=None) -> CausalLearner
```

Learn causal graph from real LLM evidence.

### Examples
```python
>>> learner = await learn_causal_graph([
```
```python
>>> print(f"Learned {learner.graph.edge_count} causal edges")
```

---

## protocols.ashc.passes.__init__

## __init__

```python
module __init__
```

ASHC Pass Operad: Categorical Transform Engine

---

## protocols.ashc.passes.bootstrap

## bootstrap

```python
module bootstrap
```

Bootstrap Passes

---

## BasePass

```python
class BasePass
```

Base class for bootstrap passes.

---

## IdentityPass

```python
class IdentityPass(BasePass)
```

Id: A -> A

---

## GroundPass

```python
class GroundPass(BasePass)
```

Ground: Void -> Facts

---

## JudgePass

```python
class JudgePass(BasePass)
```

Judge: (Spec, Principles) -> Verdict

---

## ContradictPass

```python
class ContradictPass(BasePass)
```

Contradict: (A, B) -> Tension | None

---

## SublatePass

```python
class SublatePass(BasePass)
```

Sublate: Tension -> Synthesis

---

## FixPass

```python
class FixPass(BasePass)
```

Fix: (A -> A) -> A

---

## create_identity_pass

```python
def create_identity_pass() -> IdentityPass
```

Create an identity pass.

---

## create_ground_pass

```python
def create_ground_pass(source: str='manifest') -> GroundPass
```

Create a ground pass with specified source.

---

## create_judge_pass

```python
def create_judge_pass() -> JudgePass
```

Create a judge pass.

---

## create_contradict_pass

```python
def create_contradict_pass() -> ContradictPass
```

Create a contradict pass.

---

## create_sublate_pass

```python
def create_sublate_pass() -> SublatePass
```

Create a sublate pass.

---

## create_fix_pass

```python
def create_fix_pass(max_iterations: int=10) -> FixPass
```

Create a fix pass with specified max iterations.

---

## name

```python
def name(self) -> str
```

The pass name. Override in subclasses.

---

## input_type

```python
def input_type(self) -> str
```

The input type. Override in subclasses.

---

## output_type

```python
def output_type(self) -> str
```

The output type. Override in subclasses.

---

## primitives

```python
def primitives(self) -> L0Primitives
```

Get or create primitives instance.

---

## __rshift__

```python
def __rshift__(self, other: 'BasePass') -> 'ComposedPass[Any, Any]'
```

Compose with another pass.

---

## invoke

```python
async def invoke(self, input: Any) -> ProofCarryingIR
```

Identity simply returns its input with a witness.

---

## invoke

```python
async def invoke(self, _: None=None) -> ProofCarryingIR
```

Ground produces facts from the source.

---

## invoke

```python
async def invoke(self, input: Any) -> ProofCarryingIR
```

Judge validates input against principles.

---

## invoke

```python
async def invoke(self, input: tuple[Any, Any]) -> ProofCarryingIR
```

Contradict checks for tensions between two inputs.

---

## invoke

```python
async def invoke(self, input: Any) -> ProofCarryingIR
```

Sublate synthesizes from tension.

---

## invoke

```python
async def invoke(self, input: Any) -> ProofCarryingIR
```

Fix finds the fixed point of the input.

---

## protocols.ashc.passes.composition

## composition

```python
module composition
```

Pass Composition

---

## ComposedPass

```python
class ComposedPass(Generic[A, C])
```

Result of composing two passes.

---

## ParallelPass

```python
class ParallelPass(Generic[A, B, C])
```

Parallel composition of two passes.

---

## compose

```python
def compose(first: Any, second: Any) -> ComposedPass[Any, Any]
```

Compose two passes: f >> g.

---

## parallel

```python
def parallel(left: Any, right: Any) -> ParallelPass[Any, Any, Any]
```

Parallel composition: f || g.

---

## name

```python
def name(self) -> str
```

Composed name: (first >> second).

---

## input_type

```python
def input_type(self) -> str
```

Input type is first's input type.

---

## output_type

```python
def output_type(self) -> str
```

Output type is second's output type.

---

## invoke

```python
async def invoke(self, input: A) -> ProofCarryingIR
```

Execute the composed pass.

---

## __rshift__

```python
def __rshift__(self, other: Any) -> 'ComposedPass[A, Any]'
```

Chain with another pass.

---

## name

```python
def name(self) -> str
```

Parallel name: (left || right).

---

## input_type

```python
def input_type(self) -> str
```

Input type is the common input type.

---

## output_type

```python
def output_type(self) -> str
```

Output type is tuple of outputs.

---

## invoke

```python
async def invoke(self, input: A) -> ProofCarryingIR
```

Execute both passes in parallel on same input.

---

## __rshift__

```python
def __rshift__(self, other: Any) -> ComposedPass[A, Any]
```

Chain with another pass.

---

## protocols.ashc.passes.core

## core

```python
module core
```

Pass Core Types

---

## VerificationNode

```python
class VerificationNode
```

A node in the verification graph.

---

## VerificationEdge

```python
class VerificationEdge
```

An edge in the verification graph (data dependency).

---

## VerificationGraph

```python
class VerificationGraph
```

Graph of proof dependencies.

---

## merge_graphs

```python
def merge_graphs(g1: VerificationGraph, g2: VerificationGraph) -> VerificationGraph
```

Merge two verification graphs.

---

## ProofCarryingIR

```python
class ProofCarryingIR
```

Intermediate Representation with attached proofs.

---

## PassProtocol

```python
class PassProtocol(Protocol)
```

Protocol for compiler passes.

---

## LawStatus

```python
class LawStatus(str, Enum)
```

Status of a law verification.

---

## LawResult

```python
class LawResult
```

Result of verifying a single composition law.

---

## CompositionLaw

```python
class CompositionLaw(ABC)
```

Abstract base for composition laws.

---

## empty

```python
def empty(cls) -> 'VerificationGraph'
```

Create an empty verification graph.

---

## from_witness

```python
def from_witness(cls, pass_name: str, witness_id: str, timestamp: datetime | None=None) -> 'VerificationGraph'
```

Create a graph with a single node from a witness.

---

## add_node

```python
def add_node(self, node: VerificationNode) -> 'VerificationGraph'
```

Add a node to the graph.

---

## add_edge

```python
def add_edge(self, edge: VerificationEdge) -> 'VerificationGraph'
```

Add an edge to the graph.

---

## from_output

```python
def from_output(cls, output: Any, witness: Any, pass_name: str) -> 'ProofCarryingIR'
```

Create ProofCarryingIR from a pass output and witness.

---

## chain

```python
def chain(self, other: 'ProofCarryingIR') -> 'ProofCarryingIR'
```

Chain two ProofCarryingIRs together.

---

## name

```python
def name(self) -> str
```

The pass name (for identification).

---

## input_type

```python
def input_type(self) -> str
```

String representation of input type.

---

## output_type

```python
def output_type(self) -> str
```

String representation of output type.

---

## invoke

```python
async def invoke(self, input: Any) -> ProofCarryingIR
```

Execute the pass.

---

## __rshift__

```python
def __rshift__(self, other: Any) -> Any
```

Compose with another pass.

---

## holds

```python
def holds(self) -> bool
```

True if the law holds.

---

## passed

```python
def passed(cls, law: str, evidence: str='') -> 'LawResult'
```

Create a passing result.

---

## failed

```python
def failed(cls, law: str, evidence: str, left: Any=None, right: Any=None) -> 'LawResult'
```

Create a failing result.

---

## error

```python
def error(cls, law: str, message: str) -> 'LawResult'
```

Create an error result.

---

## aggregate

```python
def aggregate(cls, results: list['LawResult']) -> 'LawResult'
```

Aggregate multiple law results.

---

## name

```python
def name(self) -> str
```

The law name.

---

## equation

```python
def equation(self) -> str
```

The equation (for display).

---

## verify

```python
async def verify(self, *passes: PassProtocol) -> LawResult
```

Verify the law holds for given passes.

---

## protocols.ashc.passes.laws

## laws

```python
module laws
```

Pass Composition Laws

---

## IdentityLaw

```python
class IdentityLaw(CompositionLaw)
```

Identity Law: Id >> f == f == f >> Id

---

## AssociativityLaw

```python
class AssociativityLaw(CompositionLaw)
```

Associativity Law: (f >> g) >> h == f >> (g >> h)

---

## FunctorLaw

```python
class FunctorLaw(CompositionLaw)
```

Functor Law: lift(f >> g) == lift(f) >> lift(g)

---

## ClosureLaw

```python
class ClosureLaw(CompositionLaw)
```

Closure Law: f >> g is still a Pass

---

## WitnessLaw

```python
class WitnessLaw(CompositionLaw)
```

Witness Law: Every pass emits a witness

---

## verify

```python
async def verify(self, *passes: Any) -> LawResult
```

Verify identity law with given passes.

---

## verify

```python
async def verify(self, *passes: Any) -> LawResult
```

Verify associativity law with given passes.

---

## verify

```python
async def verify(self, *passes: Any) -> LawResult
```

Verify functor law with given passes.

---

## verify

```python
async def verify(self, *passes: Any) -> LawResult
```

Verify closure law with given passes.

---

## verify

```python
async def verify(self, *passes: Any) -> LawResult
```

Verify witness law with given passes.

---

## protocols.ashc.passes.operad

## operad

```python
module operad
```

Pass Operad: Grammar of Valid Pass Compositions

---

## PassOperation

```python
class PassOperation
```

An operation in the Pass Operad.

---

## PassOperad

```python
class PassOperad
```

The grammar of valid pass compositions.

---

## create_pass_operad

```python
def create_pass_operad() -> PassOperad
```

Create the ASHC Pass Operad.

---

## render_operad_manifest

```python
def render_operad_manifest(operad: PassOperad=PASS_OPERAD) -> str
```

Render the operad as an ASCII manifest.

---

## render_law_verification

```python
async def render_law_verification(operad: PassOperad=PASS_OPERAD) -> str
```

Render law verification result as ASCII.

---

## __call__

```python
def __call__(self) -> Any
```

Instantiate the pass.

---

## compose

```python
def compose(self, pass_names: list[str]) -> Any
```

Compose named passes into a pipeline.

---

## compose_str

```python
def compose_str(self, expr: str) -> Any
```

Compose passes from a string expression.

---

## verify_laws

```python
async def verify_laws(self, composed: PassProtocol | None=None) -> LawResult
```

Verify all composition laws hold.

---

## verify_law

```python
async def verify_law(self, law_name: str, *passes: PassProtocol) -> LawResult
```

Verify a specific law.

---

## get_operation

```python
def get_operation(self, name: str) -> PassOperation | None
```

Get an operation by name.

---

## list_passes

```python
def list_passes(self) -> list[dict[str, str]]
```

List all available passes with their types.

---

## list_laws

```python
def list_laws(self) -> list[dict[str, str]]
```

List all composition laws.

---

## protocols.ashc.patterns

## patterns

```python
module patterns
```

L0 Kernel Pattern Matching

---

## L0MatchError

```python
class L0MatchError(Exception)
```

Error during pattern matching. Fail-fast.

---

## match

```python
def match(pattern: L0Pattern, value: Any) -> dict[str, Any] | None
```

Structural pattern matching.

---

## literal

```python
def literal(value: Any) -> LiteralPattern
```

Create a literal pattern.

---

## wildcard

```python
def wildcard(name: str) -> WildcardPattern
```

Create a wildcard pattern that binds to name.

---

## dict_pattern

```python
def dict_pattern(keys: dict[str, L0Pattern], allow_extra: bool=False) -> DictPattern
```

Create a dict pattern from a regular dict.

---

## list_pattern

```python
def list_pattern(*elements: L0Pattern, allow_extra: bool=False) -> ListPattern
```

Create a list pattern from elements.

---

## protocols.ashc.primitives

## primitives

```python
module primitives
```

L0 Kernel Primitives

---

## Artifact

```python
class Artifact
```

Emitted artifact from L0 execution.

---

## VerificationStatus

```python
class VerificationStatus(str, Enum)
```

Status of witness verification.

---

## TraceWitnessResult

```python
class TraceWitnessResult
```

Full witness capture. Compatible with services/verification.

---

## ComposedCallable

```python
class ComposedCallable(Generic[A, C])
```

Result of composing two callables.

---

## L0Primitives

```python
class L0Primitives
```

The five irreducible operations.

---

## get_primitives

```python
def get_primitives() -> L0Primitives
```

Get the default L0 primitives instance.

---

## pass_name

```python
def pass_name(self) -> str
```

Extract pass name from agent path.

---

## __call__

```python
async def __call__(self, input: A) -> C
```

Execute composed callable.

---

## compose

```python
def compose(self, f: Callable[[A], B], g: Callable[[B], C]) -> ComposedCallable[A, C]
```

Sequential composition: f >> g

---

## apply

```python
async def apply(self, f: Callable[[A], B], x: A) -> B
```

Function application: f(x)

---

## match

```python
def match(self, pattern: L0Pattern, value: Any) -> dict[str, Any] | None
```

Structural pattern matching.

---

## emit

```python
def emit(self, artifact_type: str, content: Any) -> Artifact
```

Emit an artifact.

---

## witness

```python
def witness(self, pass_name: str, input_data: Any, output_data: Any) -> TraceWitnessResult
```

Emit a full witness. Captures complete input/output.

---

## protocols.ashc.program

## program

```python
module program
```

L0 Program Builder DSL

---

## L0Program

```python
class L0Program
```

Builder for L0 programs.

---

## __init__

```python
def __init__(self, name: str)
```

Create a new L0 program.

---

## name

```python
def name(self) -> str
```

The program name.

---

## literal

```python
def literal(self, value: Any) -> L0Expr
```

Create a literal expression.

---

## handle

```python
def handle(self, name: str) -> L0Handle
```

Create a handle referencing a defined value.

---

## call

```python
def call(self, fn: Callable[..., Any], **kwargs: Any) -> L0Expr
```

Create a call expression.

---

## compose

```python
def compose(self, first: L0Expr | L0Define, second: L0Expr | L0Define) -> L0Expr
```

Compose two expressions: first >> second

---

## match_expr

```python
def match_expr(self, pattern: L0Pattern, value: L0Expr | L0Define) -> L0Expr
```

Create a match expression.

---

## pattern_literal

```python
def pattern_literal(self, value: Any) -> L0Pattern
```

Create a literal pattern that matches exact value.

---

## pattern_wildcard

```python
def pattern_wildcard(self, name: str) -> L0Pattern
```

Create a wildcard pattern that binds to name.

---

## pattern_dict

```python
def pattern_dict(self, keys: dict[str, L0Pattern], allow_extra: bool=False) -> L0Pattern
```

Create a dict pattern that matches structure.

---

## pattern_list

```python
def pattern_list(self, *elements: L0Pattern, allow_extra: bool=False) -> L0Pattern
```

Create a list pattern that matches structure.

---

## define

```python
def define(self, name: str, expr: L0Expr) -> L0Define
```

Define a named value.

---

## emit

```python
def emit(self, artifact_type: str, content: L0Expr | L0Define) -> L0Emit
```

Emit an artifact.

---

## witness

```python
def witness(self, pass_name: str, input_expr: L0Expr | L0Define, output_expr: L0Expr | L0Define) -> L0Witness
```

Emit a witness with full capture.

---

## build

```python
def build(self) -> L0ProgramAST
```

Build the program AST.

---

## run

```python
async def run(self, primitives: L0Primitives | None=None) -> L0Result
```

Execute the program.

---

## protocols.ashc.runtime

## runtime

```python
module runtime
```

L0 Kernel Runtime

---

## L0Error

```python
class L0Error(Exception)
```

Fail-fast error. Execution halts immediately.

---

## L0Result

```python
class L0Result
```

Successful execution result.

---

## resolve_expr

```python
async def resolve_expr(expr: L0Expr, bindings: dict[str, Any], primitives: L0Primitives) -> Any
```

Resolve an expression to its value.

---

## execute_stmt

```python
async def execute_stmt(stmt: L0Stmt, bindings: dict[str, Any], primitives: L0Primitives, artifacts: list[Artifact], witnesses: list[TraceWitnessResult]) -> dict[str, Any]
```

Execute a single statement.

---

## run_program

```python
async def run_program(program: L0ProgramAST, primitives: L0Primitives | None=None) -> L0Result
```

Execute L0 program with fail-fast semantics.

---

## protocols.ashc.stubs

## stubs

```python
module stubs
```

L0 Bootstrap Stubs

---

## ground_manifest_stub

```python
async def ground_manifest_stub() -> dict[str, Any]
```

Stub for self.ground.manifest.

---

## ground_context_stub

```python
async def ground_context_stub() -> dict[str, Any]
```

Stub for self.ground.context.

---

## judge_spec_stub

```python
async def judge_spec_stub(spec: dict[str, Any]) -> dict[str, Any]
```

Stub for concept.principles.judge.

---

## judge_artifact_stub

```python
async def judge_artifact_stub(artifact: dict[str, Any]) -> dict[str, Any]
```

Stub for concept.principles.judge on artifacts.

---

## contradict_stub

```python
async def contradict_stub(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any] | None
```

Stub for concept.dialectic.contradict.

---

## sublate_stub

```python
async def sublate_stub(tension: dict[str, Any]) -> dict[str, Any]
```

Stub for concept.dialectic.sublate.

---

## identity_stub

```python
async def identity_stub(x: Any) -> Any
```

Stub for Id agent.

---

## compose_stub

```python
def compose_stub(f: Any, g: Any) -> Any
```

Stub for compose operation.

---

## get_stub

```python
def get_stub(path: str) -> Any
```

Get a stub by AGENTESE path.

---

## protocols.ashc.verify

## verify

```python
module verify
```

ASHC Verification Runners

---

## TestReport

```python
class TestReport
```

Results from running pytest on generated code.

---

## TypeReport

```python
class TypeReport
```

Results from running mypy on generated code.

---

## LintReport

```python
class LintReport
```

Results from running ruff on generated code.

---

## SubprocessResult

```python
class SubprocessResult
```

Result of a subprocess execution.

---

## run_subprocess

```python
async def run_subprocess(cmd: list[str], cwd: Path | None=None, timeout: float=60.0, env: dict[str, str] | None=None) -> SubprocessResult
```

Run a subprocess with timeout and output capture.

---

## run_pytest

```python
async def run_pytest(code: str, test_code: str | None=None, timeout: float=60.0) -> TestReport
```

Run pytest on generated code.

---

## run_mypy

```python
async def run_mypy(code: str, timeout: float=30.0) -> TypeReport
```

Run mypy on generated code.

---

## run_ruff

```python
async def run_ruff(code: str, timeout: float=10.0) -> LintReport
```

Run ruff on generated code.

---

## VerificationResult

```python
class VerificationResult
```

Combined results from all verification tools.

---

## verify_code

```python
async def verify_code(code: str, test_code: str | None=None, run_tests: bool=True, run_types: bool=True, run_lint: bool=True, timeout: float=60.0) -> VerificationResult
```

Run all verification tools on generated code.

---

## total

```python
def total(self) -> int
```

Total number of tests.

---

## success

```python
def success(self) -> bool
```

Did all tests pass?

---

## passed

```python
def passed(self) -> bool
```

Did all verifications pass?

---

*404 symbols, 0 teaching moments*

*Generated by Living Docs — 2025-12-21*