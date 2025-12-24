"""
Composition via Bellman equation.

Placeholder for future implementation.

The vision: When composing agents f >> g, the combined value function is:

V_{f >> g}(s) = max_a [R_f(s,a) + γ * V_g(f(s,a))]

This gives us:
- Immediate reward from f's action
- Future reward from g's optimal continuation
- Compositional value: the whole is the sum of discounted parts
"""

# TODO: Implement Bellman composition
# - bellman_compose(agent_f, agent_g, gamma=0.9) -> composed_agent
# - value_function_composition(V_f, V_g, transition) -> V_composed
# - optimal_policy_composition(π_f, π_g) -> π_composed
