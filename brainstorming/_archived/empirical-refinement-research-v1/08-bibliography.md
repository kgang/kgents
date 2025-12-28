# Annotated Bibliography

> *"Standing on the shoulders of giants."*

**Purpose**: Complete reference list for empirical refinement research
**Organization**: By topic area
**Format**: Citation + URL + Relevance annotation

---

## 1. Category Theory & Formal Methods

### 1.1 Operads and Composition

**Flores, Z., Taranto, A., Forman, Y., & Bond, E.** (2024). Formalizing Operads for a Categorical Framework of DSL Composition. *Mathematically Structured Functional Programming (MSFP) 2024*.
- URL: https://msfp-workshop.github.io/msfp2024/
- **Relevance**: First formalization of operads in Coq with significant automation. Direct template for formalizing Experience Quality Operad.
- **Key Contribution**: Proves operads can be formalized without HoTT.

**Spivak, D., et al.** (2024). Polynomial Functors: A Mathematical Theory of Interaction. *arXiv:2312.00990*.
- URL: https://arxiv.org/pdf/2312.00990
- **Relevance**: Theoretical foundation for polynomial functors as models of agents. Validates PolyAgent design.
- **Key Contribution**: Containers/polynomial functors closed under coproducts, products, Day convolution.

**nLab Contributors.** Operad.
- URL: https://ncatlab.org/nlab/show/operad
- **Relevance**: Comprehensive reference for operad theory. Includes algebraic and topological perspectives.

### 1.2 Galois Connections

**Yang, H., et al.** (2015). Modularity in Lattices: A Case Study on the Correspondence Between Top-Down and Bottom-Up Analysis. *SAS 2015*.
- URL: https://www.cs.ox.ac.uk/people/hongseok.yang/paper/sas15.pdf
- **Relevance**: Empirical validation of Galois-based modularity at scale (800K bytecodes). Shows 2-5% precision loss acceptable.
- **Key Contribution**: Proves modularity requirement enables compositional analysis.

**Wikipedia.** Galois Connection.
- URL: https://en.wikipedia.org/wiki/Galois_connection
- **Relevance**: Standard definition and examples of Galois connections.

### 1.3 Lawvere Fixed Points

**Reinhart, T.** (2025). A Survey on Lawvere's Fixed-Point Theorem. *arXiv:2503.13536*.
- URL: https://arxiv.org/abs/2503.13536
- **Relevance**: Comprehensive survey connecting Lawvere to logic, type theory, computation, HoTT. Validates fixed-point claims.
- **Key Contribution**: Shows Lawvere unifies Cantor, Russell, Gödel, Turing, Tarski.

**nLab Contributors.** Lawvere's fixed point theorem.
- URL: https://ncatlab.org/nlab/show/Lawvere's+fixed+point+theorem
- **Relevance**: Mathematical details and proof of Lawvere's theorem.

### 1.4 Formal Verification

**Akintunde, M., et al.** (2024). Formal Verification of Parameterised Neural-symbolic Multi-agent Systems. *IJCAI 2024*.
- URL: https://www.ijcai.org/proceedings/2024/12
- **Relevance**: Shows how to verify multi-agent systems with neural components. Relevant for AI agent verification.
- **Key Contribution**: Abstraction methodology for parameterised multi-agent verification.

---

## 2. Semantic Distance & NLP Metrics

### 2.1 BERTScore

**Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y.** (2019). BERTScore: Evaluating Text Generation with BERT. *ICLR 2020*.
- URL: https://arxiv.org/abs/1904.09675
- **Relevance**: Primary semantic distance metric candidate. r=0.93 correlation with human judgments.
- **Key Contribution**: Token-level similarity using BERT embeddings beats n-gram methods.
- **Limitation**: Vulnerable to adversarial attacks.

### 2.2 NLI-Based Metrics

**Chen, S., et al.** (2023). MENLI: Robust Evaluation Metrics from Natural Language Inference. *TACL*.
- URL: https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00576/116715/MENLI-Robust-Evaluation-Metrics-from-Natural
- **Relevance**: More robust alternative to BERTScore. Recommended for ensemble.
- **Key Contribution**: NLI-based metrics resist adversarial manipulation.

### 2.3 Prompt Compression

**Jiang, H., et al.** (2023). LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models. *EMNLP 2023*.
- URL: https://arxiv.org/abs/2310.05736
- **Relevance**: Shows 20x compression achievable with minimal loss. Validates Galois loss framework.
- **Additional**: LLMLingua-2 (2024) - https://arxiv.org/abs/2403.12968

**Microsoft Research.** LLMLingua: Innovating LLM efficiency with prompt compression.
- URL: https://www.microsoft.com/en-us/research/blog/llmlingua-innovating-llm-efficiency-with-prompt-compression/
- **Relevance**: Practical guide to prompt compression methodology.

---

## 3. Argumentation Theory

### 3.1 Toulmin in AI

**Verheij, B.** (2009). The Toulmin Argument Model in Artificial Intelligence. In *Argumentation in Artificial Intelligence*. Springer.
- URL: https://link.springer.com/chapter/10.1007/978-0-387-98197-0_11
- **Relevance**: Foundational work on applying Toulmin to AI. Identifies four AI-relevant Toulmin themes.
- **Key Quote**: "Toulmin considers the study of defeasibility an empirical question."

**Khatib, D., et al.** (2024). Critical-Questions-of-Thought: Steering LLM reasoning with Argumentative Querying. *arXiv:2412.15177*.
- URL: https://arxiv.org/html/2412.15177v1
- **Relevance**: Shows critical questions improve LLM reasoning. Direct application for rebuttal generation.
- **Key Contribution**: CQoT methodology for structured reasoning validation.

### 3.2 Conversational Agents

**Wang, S., et al.** (2021). Developing a Conversational Agent's Capability to Identify Structural Wrongness in Arguments Based on Toulmin's Model. *Applied Sciences*.
- URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC8680349/
- **Relevance**: Empirical validation of Toulmin detection (F-score 0.80).
- **Key Contribution**: Proves Toulmin components can be computationally detected.

### 3.3 Trust Enhancement

**Elkins, K., & Chun, J.** (2023). Using Toulmin's Argumentation Model to Enhance Trust in Analytics-Based Advice Giving Systems. *ACM TMIS*.
- URL: https://dl.acm.org/doi/10.1145/3580479
- **Relevance**: Shows Toulmin structure enhances user trust. Validates witness protocol design.
- **Key Contribution**: Three experimental studies validating trust enhancement.

---

## 4. Dialectics & Human-AI Collaboration

### 4.1 Dialectical Reconciliation

**Sklar, E., et al.** (2024). Dialectical Reconciliation via Structured Argumentative Dialogues. *KR 2024*.
- URL: https://arxiv.org/html/2306.14694
- **Relevance**: Framework for resolving inconsistencies through structured dialogue. Validates Kent-AI fusion approach.
- **Key Contribution**: Empirically validated DR-Arg in computational and human experiments.

### 4.2 Mutual Theory of Mind

**Wang, Y., et al.** (2024). Mutual Theory of Mind in Human-AI Collaboration: An Empirical Study with LLM-driven AI Agents. *arXiv:2409.08811*.
- URL: https://arxiv.org/html/2409.08811
- **Relevance**: Framework for mutual understanding in collaboration. Missing from current kgents design.
- **Key Contribution**: MToM framework for human-AI collaboration analysis.

### 4.3 Antagonistic AI

**Sartori, J., & Theodorou, A.** (2024). Fostering effective hybrid human-LLM reasoning and decision making. *Frontiers in AI*.
- URL: https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2024.1464690/full
- **Relevance**: Validates adversarial cooperation (Article II). Confrontational AI promotes critical thinking.
- **Key Contribution**: Counter-narrative to agreeable AI design.

### 4.4 Collaboration Taxonomy

**Westphal, A., & Schaub, T.** (2024). Human-AI collaboration is not very collaborative yet: a taxonomy of interaction patterns. *Frontiers in Computer Science*.
- URL: https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2024.1521066/full
- **Relevance**: Systematic review of collaboration patterns. Identifies gap kgents aims to fill.
- **Key Contribution**: Taxonomy: tool → assistant → partner → lead.

---

## 5. Trust & Reputation

### 5.1 FIRE Model

**Huynh, T., Jennings, N., & Shadbolt, N.** (2006). An integrated trust and reputation model for open multi-agent systems. *Autonomous Agents and Multi-Agent Systems*.
- URL: https://link.springer.com/article/10.1007/s10458-005-6825-4
- **Relevance**: Most comprehensive trust model for MAS. Four sources: interaction, role, witness, certified.
- **Key Contribution**: Validated integration formula with empirical analysis.

### 5.2 Trust Surveys

**Pinyol, I., & Sabater-Mir, J.** (2013). Trust and Reputation Models for Multiagent Systems. *ACM Computing Surveys*.
- URL: https://dl.acm.org/doi/10.1145/2816826
- **Relevance**: Comprehensive survey of trust/reputation models. Context for FIRE adoption.

---

## 6. Sheaf Theory

### 6.1 Data Fusion

**Robinson, M.** (2017). Sheaves are the canonical data structure for sensor integration. *Information Fusion*.
- URL: https://www.sciencedirect.com/science/article/abs/pii/S156625351630207X
- **Relevance**: Foundational paper for sheaf-based data fusion. Defines consistency radius.
- **Key Contribution**: Proves sheaves are CANONICAL for data integration.

**Mansourbeigi, S.** (2018). Sheaf Theory as a Foundation for Heterogeneous Data Fusion. *Utah State University Thesis*.
- URL: https://digitalcommons.usu.edu/etd/7363/
- **Relevance**: Detailed treatment of sheaf-based fusion with examples.

### 6.2 Applications

**Ayzenberg, A., & Magai, G.** (2025). Sheaf theory: from deep geometry to deep learning. *arXiv:2502.15476*.
- URL: https://arxiv.org/pdf/2502.15476
- **Relevance**: Recent overview of sheaf applications in ML. Connects to graph neural networks.

**Tabia, K.** (2020). A Sheaf Theoretical Approach to Uncertainty Quantification of Heterogeneous Geolocation Information. *Sensors*.
- URL: https://www.mdpi.com/1424-8220/20/12/3418
- **Relevance**: Example of sheaf-based uncertainty quantification.

---

## 7. User Experience Metrics

### 7.1 HEART Framework

**Rodden, K., Hutchinson, H., & Fu, X.** (2010). Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications. *CHI 2010*.
- URL: https://dl.acm.org/doi/abs/10.1145/1753326.1753687
- **Relevance**: Google's validated UX framework. Benchmark for Experience Quality Operad.
- **Key Contribution**: HEART: Happiness, Engagement, Adoption, Retention, Task Success.

### 7.2 UEQ

**Laugwitz, B., Held, T., & Schrepp, M.** (2008). Construction and Evaluation of a User Experience Questionnaire. *HCI and Usability*.
- URL: https://link.springer.com/chapter/10.1007/978-3-540-89350-9_6
- **Relevance**: Empirically developed UX questionnaire. Distinguishes pragmatic/hedonic quality.
- **Key Contribution**: 80 bipolar items → validated questionnaire.

### 7.3 Systematic Review

**Ogunyemi, A., & Kapros, E.** (2024). Usability and User Experience Evaluation in Intelligent Environments: A Review and Reappraisal. *IJHCI*.
- URL: https://www.tandfonline.com/doi/full/10.1080/10447318.2024.2394724
- **Relevance**: Comprehensive review of 96 UX evaluation methods. Context for methodology choices.

---

## 8. Applied Category Theory

### 8.1 Conferences

**ACT 2024.** Seventh International Conference on Applied Category Theory.
- URL: https://oxford24.github.io/act_cfp.html
- **Relevance**: Primary venue for category theory applications.

**ACT 2025.** Eighth International Conference on Applied Category Theory.
- URL: University of Florida, June 2-6, 2025
- **Relevance**: Target venue for kgents research contributions.

### 8.2 Research Groups

**Topos Institute.**
- URL: https://topos.institute/blog/
- **Relevance**: Leading applied category theory research. David Spivak's polynomial functor work.

**Azimuth Blog** (John Carlos Baez).
- URL: https://johncarlosbaez.wordpress.com/category/conferences/
- **Relevance**: Commentary on applied category theory developments.

---

## 9. Additional Resources

### 9.1 Formal Concept Analysis

**Wikipedia.** Formal Concept Analysis.
- URL: https://en.wikipedia.org/wiki/Formal_concept_analysis
- **Relevance**: Related to Galois connections. Applications in data mining, knowledge management.

### 9.2 Software Engineering & Category Theory

**Fiadeiro, J.** (2005). Categories for Software Engineering. Springer.
- URL: https://link.springer.com/book/10.1007/b138249
- **Relevance**: Book-length treatment of category theory in software engineering.

---

## Citation Count Summary

| Topic | Papers | Key Paper |
|-------|--------|-----------|
| Category Theory / Formal Methods | 8 | MSFP 2024 (Operads) |
| Semantic Metrics | 5 | BERTScore |
| Argumentation | 4 | CQoT (2024) |
| Dialectics / Collaboration | 5 | MToM (2024) |
| Trust / Reputation | 2 | FIRE Model |
| Sheaf Theory | 4 | Robinson (2017) |
| UX Metrics | 3 | HEART Framework |
| Applied Category Theory | 3 | Topos Institute |

**Total**: 34 references

---

*"If I have seen further, it is by standing on the shoulders of giants." — Isaac Newton*
