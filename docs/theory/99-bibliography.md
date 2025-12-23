# Bibliography

> *"If I have seen further it is by standing on the shoulders of giants."*
> — Isaac Newton

---

## Organization

This bibliography is organized thematically, not alphabetically, to help readers find relevant sources for specific topics.

---

## Category Theory Foundations

### Textbooks

**Mac Lane, S.** (1971). *Categories for the Working Mathematician*. Springer.
- The classic text. Dense but complete. Essential reference for all categorical concepts.

**Awodey, S.** (2010). *Category Theory* (2nd ed.). Oxford University Press.
- More accessible than Mac Lane. Good introduction for mathematically mature readers without category theory background.

**Leinster, T.** (2014). *Basic Category Theory*. Cambridge University Press.
- Concise and clear. Freely available online. Excellent starting point.

**Riehl, E.** (2016). *Category Theory in Context*. Dover.
- Modern treatment with emphasis on universal properties. Good for building intuition.

### Monads

**Moggi, E.** (1991). "Notions of Computation and Monads." *Information and Computation*, 93(1), 55-92.
- The seminal paper connecting monads to computational effects.

**Wadler, P.** (1995). "Monads for Functional Programming." In *Advanced Functional Programming*, Springer.
- Accessible introduction to monads from a programming perspective.

**Manes, E.G.** (1976). *Algebraic Theories*. Springer.
- Mathematical treatment of monads (called "algebraic theories"). For deep understanding.

### Operads

**Loday, J-L. & Vallette, B.** (2012). *Algebraic Operads*. Springer.
- Comprehensive modern treatment. Technical but thorough.

**Leinster, T.** (2004). *Higher Operads, Higher Categories*. Cambridge University Press.
- Accessible introduction to operads with emphasis on higher structure.

**May, J.P.** (1972). *The Geometry of Iterated Loop Spaces*. Springer.
- Original development of operads. Historically important but technical.

### Sheaves and Topoi

**Mac Lane, S. & Moerdijk, I.** (1992). *Sheaves in Geometry and Logic*. Springer.
- The standard reference. Develops sheaves and their role in logic.

**Goldblatt, R.** (1984). *Topoi: The Categorical Analysis of Logic*. North-Holland.
- Accessible treatment focusing on logical aspects of topoi.

**Johnstone, P.T.** (2002). *Sketches of an Elephant: A Topos Theory Compendium*. Oxford University Press.
- Massive and comprehensive. Reference for advanced topics.

---

## Applied Category Theory

**Fong, B. & Spivak, D.I.** (2019). *An Invitation to Applied Category Theory*. Cambridge University Press.
- Accessible introduction to category theory with applications. Highly recommended starting point.

**Spivak, D.I.** (2014). *Category Theory for the Sciences*. MIT Press.
- Applies categorical thinking to modeling. Good for building intuition about applications.

**Coecke, B. & Kissinger, A.** (2017). *Picturing Quantum Processes*. Cambridge University Press.
- Diagrammatic approach to categorical quantum mechanics. Inspirational for visualization.

---

## Type Theory and Proof Theory

### Curry-Howard Correspondence

**Sørensen, M.H. & Urzyczyn, P.** (2006). *Lectures on the Curry-Howard Isomorphism*. Elsevier.
- Comprehensive treatment of the proofs-as-programs correspondence.

**Wadler, P.** (2015). "Propositions as Types." *Communications of the ACM*, 58(12), 75-84.
- Accessible introduction to Curry-Howard. Good starting point.

### Type Theory

**Martin-Löf, P.** (1984). *Intuitionistic Type Theory*. Bibliopolis.
- The foundational text on dependent type theory.

**Univalent Foundations Program** (2013). *Homotopy Type Theory*. Institute for Advanced Study.
- Modern treatment connecting type theory to homotopy theory. Freely available.

### Proof Theory

**Girard, J-Y., Lafont, Y., & Taylor, P.** (1989). *Proofs and Types*. Cambridge University Press.
- Classic introduction to proof theory from a type-theoretic perspective.

**Troelstra, A.S. & Schwichtenberg, H.** (2000). *Basic Proof Theory* (2nd ed.). Cambridge University Press.
- Technical but comprehensive treatment of proof-theoretic methods.

---

## Machine Learning and LLMs

### Transformer Architecture

**Vaswani, A., et al.** (2017). "Attention Is All You Need." *NeurIPS*.
- The original transformer paper. Essential reading.

**Elhage, N., et al.** (2021). "A Mathematical Framework for Transformer Circuits." *Anthropic*.
- Develops the residual stream interpretation and mathematical tools for mechanistic analysis.

### Chain-of-Thought and Reasoning Strategies

**Wei, J., et al.** (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *NeurIPS*.
- The paper that launched CoT. Essential for understanding the phenomenon.

**Wang, X., et al.** (2022). "Self-Consistency Improves Chain of Thought Reasoning in Language Models." *ICLR 2023*.
- Introduces self-consistency decoding. Important for the sheaf interpretation.

**Yao, S., et al.** (2023). "Tree of Thoughts: Deliberate Problem Solving with Large Language Models." *NeurIPS*.
- Introduces ToT. Essential for operadic interpretation.

**Besta, M., et al.** (2023). "Graph of Thoughts: Solving Elaborate Problems with Large Language Models." *arXiv:2308.09687*.
- Extends ToT to graphs. Important for understanding operadic equations.

**Yao, S., et al.** (2022). "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR 2023*.
- Introduces ReAct. Important for state monad interpretation.

**Shinn, N., et al.** (2023). "Reflexion: Language Agents with Verbal Reinforcement Learning." *NeurIPS*.
- Introduces Reflexion. Shows learning without gradient updates.

### Mechanistic Interpretability

**Olsson, C., et al.** (2022). "In-context Learning and Induction Heads." *Anthropic*.
- Identifies the induction head circuit. Key mechanistic finding.

**Elhage, N., et al.** (2022). "Toy Models of Superposition." *Anthropic*.
- Explains how models store more features than dimensions. Essential for understanding capacity.

**Wang, K., et al.** (2022). "Interpretability in the Wild: A Circuit for Indirect Object Identification in GPT-2 Small." *ICLR 2023*.
- Detailed circuit analysis. Methodological exemplar.

**Conmy, A., et al.** (2023). "Towards Automated Circuit Discovery for Mechanistic Interpretability." *NeurIPS*.
- Automated methods for finding circuits. Important for scalability.

### Process Reward Models

**Lightman, H., et al.** (2023). "Let's Verify Step by Step." *arXiv:2305.20050*.
- Introduces process supervision. Important for step-level verification.

### Reasoning Evaluation

**Turpin, M., et al.** (2023). "Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting." *NeurIPS*.
- Shows CoT can be post-hoc rationalization. Important caveat.

**Kadavath, S., et al.** (2022). "Language Models (Mostly) Know What They Know." *arXiv:2207.05221*.
- Studies model self-knowledge and calibration.

### State of the Art (2024)

**Anthropic** (2024). "Claude 3 Technical Report."
- Details on current frontier models.

**OpenAI** (2024). "GPT-4 Technical Report."
- Details on GPT-4 architecture and capabilities.

**DeepMind** (2024). "AlphaProof and AlphaGeometry."
- Neurosymbolic systems for mathematical reasoning. Important milestone.

---

## Neurosymbolic AI

**Garcez, A., et al.** (2019). "Neural-Symbolic Computing: An Effective Methodology for Principled Integration of Machine Learning and Reasoning." *arXiv:1905.06088*.
- Survey of neurosymbolic approaches.

**Nye, M., et al.** (2021). "Show Your Work: Scratchpads for Intermediate Computation with Language Models." *arXiv:2112.00114*.
- Training models to produce intermediate computation. Important for symbolic structure.

**Jiang, A., et al.** (2022). "Draft, Sketch, and Prove: Guiding Formal Theorem Provers with Informal Proofs." *ICLR 2023*.
- Hybrid approach to theorem proving.

---

## Categorical Approaches to ML

**Shiebler, D., Gavranović, B., & Wilson, P.** (2021). "Category Theory in Machine Learning." *arXiv:2106.07032*.
- Survey of categorical methods in ML. Good overview.

**Gavranović, B.** (2024). "Fundamental Components of Deep Learning: A Category-Theoretic Approach." PhD Thesis, University of Cambridge.
- Comprehensive categorical treatment of deep learning.

**Cruttwell, G., et al.** (2022). "Categorical Foundations of Gradient-Based Learning." *ESOP*.
- Categorical semantics for automatic differentiation and learning.

**Fong, B., Spivak, D.I., & Tuyéras, R.** (2019). "Backprop as Functor: A Compositional Perspective on Supervised Learning." *LICS*.
- Viewing backpropagation categorically.

---

## Philosophy of Mind and Reasoning

**Clark, A. & Chalmers, D.** (1998). "The Extended Mind." *Analysis*, 58(1), 7-19.
- Influential paper on cognition extending beyond the brain. Relevant to external reasoning traces.

**Dennett, D.C.** (1991). *Consciousness Explained*. Little, Brown.
- Multiple drafts model of consciousness. Relevant to multi-agent perspectives.

**Kahneman, D.** (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
- System 1/System 2 distinction. Relevant to intuitive vs. deliberative reasoning.

---

## Logic and Formal Methods

**Gentzen, G.** (1935). "Investigations into Logical Deduction." In *The Collected Papers of Gerhard Gentzen*, North-Holland.
- Origin of natural deduction and sequent calculus. Foundational.

**Prawitz, D.** (1965). *Natural Deduction: A Proof-Theoretical Study*. Almqvist & Wiksell.
- Comprehensive treatment of natural deduction.

**Barendregt, H.** (1984). *The Lambda Calculus: Its Syntax and Semantics*. North-Holland.
- Definitive reference on lambda calculus.

---

## Polynomial Functors

**Kock, J.** (2012). "Polynomial Functors and Polynomial Monads." *Mathematical Proceedings of the Cambridge Philosophical Society*, 154(1), 153-192.
- Mathematical development of polynomial functors.

**Gambino, N. & Kock, J.** (2013). "Polynomial Functors and Polynomial Monads." *Mathematical Proceedings of the Cambridge Philosophical Society*, 154(1), 153-192.
- Further development with applications.

**Spivak, D.I.** (2022). "Polynomial Functors: A General Theory of Interaction." *arXiv:2202.00534*.
- Modern treatment with emphasis on interfaces and dynamics. Relevant to PolyAgent.

---

## Further Reading by Topic

### If you want to understand monads deeply:
1. Wadler (1995) - accessible introduction
2. Moggi (1991) - the theoretical foundation
3. Mac Lane, Chapter VI - categorical perspective

### If you want to understand operads:
1. Leinster (2004), Chapters 1-2 - accessible introduction
2. Loday & Vallette (2012), Chapters 1-5 - full treatment
3. May (1972) - historical origin

### If you want to understand sheaves:
1. Mac Lane & Moerdijk (1992), Chapters I-II - standard introduction
2. Goldblatt (1984), Chapters 1-4 - logical perspective
3. Johnstone (2002) - comprehensive reference

### If you want to understand LLM reasoning:
1. Wei et al. (2022) - CoT introduction
2. Wang et al. (2022) - Self-consistency
3. Yao et al. (2023) - ToT
4. Olsson et al. (2022) - Mechanistic understanding

### If you want to explore categorical ML:
1. Fong & Spivak (2019) - Applied category theory
2. Shiebler et al. (2021) - ML-specific survey
3. Gavranović (2024) - Deep treatment

---

## How to Read This Literature

**For beginners in category theory**:
Start with Leinster (2014) or Fong & Spivak (2019). Move to Awodey (2010). Use Mac Lane (1971) as reference.

**For beginners in LLM reasoning**:
Start with Wei et al. (2022). Read Wang et al. (2022) and Yao et al. (2023). Then explore mechanistic interpretability via Olsson et al. (2022).

**For connecting the domains**:
Read Shiebler et al. (2021) for existing categorical approaches to ML. This monograph attempts to extend that work to reasoning specifically.

---

*"The bibliography of a good book is a window into a world of learning."*

---

*Previous: [Chapter 9: Open Problems and Conjectures](./09-open-problems.md)*
*Return to: [Table of Contents](./README.md)*
