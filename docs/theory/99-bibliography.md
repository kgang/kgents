# Bibliography

> *"If I have seen further it is by standing on the shoulders of giants."*
> — Isaac Newton

---

## Organization

This bibliography is organized thematically to help readers find relevant sources for specific topics. We've expanded from the original focus on category theory to include dynamic programming, Galois theory, distributed systems, and co-engineering with AI.

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

### Polynomial Functors

**Spivak, D.I.** (2022). "Polynomial Functors: A General Theory of Interaction." *arXiv:2202.00534*.
- Modern treatment with emphasis on interfaces and dynamics. Directly relevant to PolyAgent.

**Kock, J.** (2012). "Polynomial Functors and Polynomial Monads." *Mathematical Proceedings of the Cambridge Philosophical Society*, 154(1), 153-192.
- Mathematical development of polynomial functors.

**Gambino, N. & Kock, J.** (2013). "Polynomial Functors and Polynomial Monads." *Mathematical Proceedings*, 154(1), 153-192.
- Further development with applications.

---

## Galois Theory and Algebra

### Classical Galois Theory

**Artin, E.** (1944). *Galois Theory*. Notre Dame Mathematical Lectures.
- Classic exposition of the connection between field extensions and group theory.

**Stewart, I.** (2015). *Galois Theory* (4th ed.). CRC Press.
- Modern, accessible treatment. Good for building intuition.

**Edwards, H.M.** (1984). *Galois Theory*. Springer.
- Historical approach, tracing Galois's original ideas.

### Galois Connections and Adjunctions

**Davey, B.A. & Priestley, H.A.** (2002). *Introduction to Lattices and Order* (2nd ed.). Cambridge University Press.
- Chapter 7 covers Galois connections. Essential for the lattice-theoretic perspective.

**Melton, A., Schmidt, D.A., & Strecker, G.E.** (1986). "Galois Connections and Computer Science Applications." *LNCS 240*, Springer.
- Applies Galois connections to program analysis. Precedent for our application to prompts.

**Erné, M., Koslowski, J., Melton, A., & Strecker, G.E.** (1993). "A Primer on Galois Connections." *Annals of the New York Academy of Sciences*, 704(1), 103-125.
- Comprehensive survey of Galois connections with applications.

### Abstract Algebra for CS

**Lawvere, F.W. & Schanuel, S.H.** (2009). *Conceptual Mathematics* (2nd ed.). Cambridge University Press.
- Category theory for beginners. Builds intuition before formalism.

**Barr, M. & Wells, C.** (1990). *Category Theory for Computing Science*. Prentice Hall.
- Applies category theory to computer science. Freely available online.

---

## Dynamic Programming and Optimal Control

### Foundations

**Bellman, R.** (1957). *Dynamic Programming*. Princeton University Press.
- The original. Bellman's insight that optimal solutions have optimal substructure.

**Puterman, M.L.** (2014). *Markov Decision Processes: Discrete Stochastic Dynamic Programming*. Wiley.
- Comprehensive treatment of MDPs. The reference for formal DP.

**Bertsekas, D.P.** (2012). *Dynamic Programming and Optimal Control* (4th ed.). Athena Scientific.
- Two-volume comprehensive treatment. Balance of theory and computation.

### Reinforcement Learning

**Sutton, R.S. & Barto, A.G.** (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.
- The standard RL textbook. Freely available online.

**Szepesvári, C.** (2010). *Algorithms for Reinforcement Learning*. Morgan & Claypool.
- Concise, mathematical treatment of RL algorithms.

### DP in AI and Planning

**Russell, S.J. & Norvig, P.** (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
- Chapters on planning, MDPs, and RL. The standard AI textbook.

**Geffner, H. & Bonet, B.** (2013). "A Concise Introduction to Models and Methods for Automated Planning." *Synthesis Lectures on AI and ML*.
- Planning as DP. Connections to agent architectures.

---

## Distributed Systems and Coordination

### Foundations

**Lynch, N.A.** (1996). *Distributed Algorithms*. Morgan Kaufmann.
- The theoretical foundations. Consensus, fault tolerance, impossibility results.

**Tanenbaum, A.S. & Van Steen, M.** (2017). *Distributed Systems* (3rd ed.). Pearson.
- Practical and theoretical. Good overview of the field.

### Consensus and Coordination

**Lamport, L.** (1998). "The Part-Time Parliament." *ACM Transactions on Computer Systems*, 16(2), 133-169.
- The Paxos algorithm. Foundation of modern consensus.

**Fischer, M.J., Lynch, N.A., & Paterson, M.S.** (1985). "Impossibility of Distributed Consensus with One Faulty Process." *JACM*, 32(2), 374-382.
- The FLP impossibility result. Fundamental limit on distributed agreement.

**Brewer, E.** (2012). "CAP Twelve Years Later: How the 'Rules' Have Changed." *IEEE Computer*, 45(2), 23-29.
- The CAP theorem and its implications. Consistency vs. availability.

### Multi-Agent Systems

**Wooldridge, M.** (2009). *An Introduction to MultiAgent Systems* (2nd ed.). Wiley.
- Comprehensive introduction to multi-agent systems.

**Shoham, Y. & Leyton-Brown, K.** (2008). *Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations*. Cambridge University Press.
- Game theory and logic for multi-agent coordination.

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

### Agent Frameworks

**LangChain Team** (2023). "LangChain: Building Applications with LLMs." Documentation and Blog.
- The dominant chain-based framework. Understanding its patterns is essential.

**Richards, T.** (2023). "Auto-GPT: An Autonomous GPT-4 Experiment." GitHub Repository.
- The first widely-used autonomous agent. Pioneered goal-directed loops.

**Moura, J.** (2024). "CrewAI: Framework for Orchestrating Role-Playing AI Agents." GitHub Repository.
- Role-based multi-agent framework. Example of implicit operadic structure.

---

## Applied Category Theory

**Fong, B. & Spivak, D.I.** (2019). *An Invitation to Applied Category Theory*. Cambridge University Press.
- Accessible introduction to category theory with applications. Highly recommended starting point.

**Spivak, D.I.** (2014). *Category Theory for the Sciences*. MIT Press.
- Applies categorical thinking to modeling. Good for building intuition about applications.

**Coecke, B. & Kissinger, A.** (2017). *Picturing Quantum Processes*. Cambridge University Press.
- Diagrammatic approach to categorical quantum mechanics. Inspirational for visualization.

### Categorical Approaches to ML

**Shiebler, D., Gavranović, B., & Wilson, P.** (2021). "Category Theory in Machine Learning." *arXiv:2106.07032*.
- Survey of categorical methods in ML. Good overview.

**Gavranović, B.** (2024). "Fundamental Components of Deep Learning: A Category-Theoretic Approach." PhD Thesis, University of Cambridge.
- Comprehensive categorical treatment of deep learning.

**Cruttwell, G., et al.** (2022). "Categorical Foundations of Gradient-Based Learning." *ESOP*.
- Categorical semantics for automatic differentiation and learning.

**Fong, B., Spivak, D.I., & Tuyéras, R.** (2019). "Backprop as Functor: A Compositional Perspective on Supervised Learning." *LICS*.
- Viewing backpropagation categorically.

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

## Philosophy of Mind and Co-Engineering

### Extended Mind and Embodied Cognition

**Clark, A. & Chalmers, D.** (1998). "The Extended Mind." *Analysis*, 58(1), 7-19.
- Influential paper on cognition extending beyond the brain. Relevant to external reasoning traces.

**Clark, A.** (2008). *Supersizing the Mind: Embodiment, Action, and Cognitive Extension*. Oxford University Press.
- Extended treatment of the extended mind thesis.

### Dialectics and Synthesis

**Hegel, G.W.F.** (1807/1977). *Phenomenology of Spirit*. Oxford University Press.
- The origin of dialectical method. Thesis-antithesis-synthesis.

**Lakoff, G. & Johnson, M.** (1999). *Philosophy in the Flesh*. Basic Books.
- Embodied cognition and its implications for reasoning.

### Human-AI Collaboration

**Dennett, D.C.** (1991). *Consciousness Explained*. Little, Brown.
- Multiple drafts model of consciousness. Relevant to multi-agent perspectives.

**Kahneman, D.** (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
- System 1/System 2 distinction. Relevant to intuitive vs. deliberative reasoning.

---

## Information Theory and Complexity

### Algorithmic Information Theory

**Li, M. & Vitányi, P.** (2008). *An Introduction to Kolmogorov Complexity and Its Applications* (3rd ed.). Springer.
- The standard reference on Kolmogorov complexity.

**Cover, T.M. & Thomas, J.A.** (2006). *Elements of Information Theory* (2nd ed.). Wiley.
- Classic textbook on information theory. Foundation for understanding loss.

### Minimum Description Length

**Grünwald, P.D.** (2007). *The Minimum Description Length Principle*. MIT Press.
- MDL as model selection. Connection to Galois loss as compression metric.

---

## Reading Pathways

### For Category Theory Beginners
1. Leinster (2014) or Fong & Spivak (2019) → 2. Awodey (2010) → 3. Mac Lane (1971) as reference

### For Dynamic Programming Focus
1. Sutton & Barto (2018) → 2. Puterman (2014) → 3. Russell & Norvig (2020) Ch. 17-21

### For Galois Theory
1. Stewart (2015) → 2. Davey & Priestley (2002) Ch. 7 → 3. Melton et al. (1986)

### For LLM Reasoning
1. Wei et al. (2022) → 2. Wang et al. (2022) and Yao et al. (2023) → 3. Olsson et al. (2022)

### For Connecting the Domains
1. Shiebler et al. (2021) for categorical ML → 2. This monograph for the synthesis

---

## How to Read This Literature

**Start accessible, go deep**: Begin with introductory texts, use technical references as needed.

**Read actively**: When we claim that chain-of-thought is Kleisli composition, check the references. Does Moggi's monad framework actually support this interpretation?

**Cross-reference**: The power is in the connections. Bellman's DP + Mac Lane's categories + Spivak's polynomials = our synthesis.

**Contribute**: This bibliography is incomplete. The synthesis of category theory, DP, Galois theory, distributed systems, and AI agents is young. New connections await discovery.

---

*"The bibliography of a good book is a window into a world of learning."*

---

*Previous: [Chapter 20: Open Problems](./20-open-problems.md)*
*Return to: [Table of Contents](./README.md)*
