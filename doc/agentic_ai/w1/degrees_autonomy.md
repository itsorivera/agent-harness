# Agentic Workflow Architecture: Degrees of Autonomy

This document formalizes the operational spectrum of autonomy within AI systems based strictly on the lecture material.

## 1. The Agentic Spectrum

The term "agentic" is most usefully applied as a continuous architectural adjective rather than a binary categorization. In classical Artificial Intelligence (GOFAI) and Reinforcement Learning, the term "agent" possesses a strict mathematical definition. As formally established in **[_Artificial Intelligence: A Modern Approach_ (Russell & Norvig)](http://aima.cs.berkeley.edu/)** through the framework of _rational agents_—and practically implemented in reinforcement learning texts like **[_Reinforcement Learning: An Introduction_ (Sutton & Barto)](http://incompleteideas.net/book/the-book-2nd.html)** via **[Markov Decision Processes (MDP)](https://en.wikipedia.org/wiki/Markov_decision_process)**—an agent is an autonomous entity that perceives discrete environmental states and calculates actions to systematically maximize a specific performance measure or objective reward function.

With the advent of Generative AI, the engineering community engaged in counterproductive taxonomic debates: because chaining LLM prompts rarely constitutes execution within a strict Markovian environment with a formal reward mechanism, classical AI engineers rejected labeling these generative scripts as "true agents." To circumvent this semantic gatekeeping and re-focus on practical software production, the framework transitions to the adjective _agentic_. Acknowledging that modern LLM autonomy is not a binary switch, systems are instead architected and evaluated across a continuous operational capability spectrum.

## 2. Less Autonomous Architectures

Function on predetermined, linear sequences of steps entirely defined by the engineer in advance.

![Low-Autonomy Architectures](/doc/assets/low_autonomy_architectures.png)
_Source: [Agentic AI by Andrew Ng - DeepLearning.AI](https://www.deeplearning.ai/courses/agentic-ai/)_

- **Implementation Mechanics:** The execution pipeline is hardcoded. The Large Language Model (LLM) is used simply for semantic inference within that static sequence.
- **Operational Example:** An essay generator where the workflow is statically executed as: _Prompt $\rightarrow$ LLM generates search terms $\rightarrow$ Hardcoded web search execution $\rightarrow$ Hardcoded page fetch $\rightarrow$ LLM writes the essay._
- **Engineering Characteristics:** Autonomy is confined entirely to the specific text the LLM generates. These pipelines provide high reliability and currently drive massive business value across the industry today.

## 3. Semi-Autonomous Architectures

Occupying the middle of the spectrum, these implementations permit the LLM to make certain defined decisions. The agent can conditionally choose when to execute tools, but the available tools and their integration boundaries are predefined and constrained by the system architect.

## 4. Highly Autonomous Architectures

Highly autonomous systems delegate substantial execution logic directly to the LLM, trusting it to act as the core runtime orchestrator. This dynamic architectural loop is heavily grounded in the seminal **[ReAct (Reasoning and Acting) Framework](https://arxiv.org/abs/2210.03629)**, which formalized how language models can iteratively combine internal reasoning chains with active environmental tool extraction.

![High-Autonomy Architectures](/doc/assets/high_autonomy_architectures.png)
_Source: [Agentic AI by Andrew Ng - DeepLearning.AI](https://www.deeplearning.ai/courses/agentic-ai/)_

- **Implementation Mechanics:** By implementing a ReAct-style loop, the LLM independently determines the Directed Acyclic Graph (DAG) sequence, dynamically deciding which external tools or sources to integrate and when.
- **Operational Example:** Given the same essay prompt, the LLM autonomously decides whether to search the standard web, news sources, or the arXiv repository. The model decides how many pages to fetch, determines if a retrieved PDF necessitates calling a PDF-to-text converter, iterates through self-reflection (retrieving more data if necessary), or even writes entirely new functions to execute.
- **Engineering Characteristics:** Enables highly flexible solutions for varying contexts. However, they remain highly experimental, inherently unpredictable, difficult to control, and are currently the subject of intense active research.

## 5. Workflow Diagram Notation

When mapping agentic workflow topologies in this course, the following visual notation is adopted:

- **Red Nodes (User Input):** Indicate the initial prompt, input document, or user query triggering the workflow.
- **Gray Nodes (LLM Calls):** Indicate reasoning, planning, or generation steps handled specifically by a Large Language Model.
- **Green Nodes (Software Execution):** Indicate deterministic actions executed by external software, such as invoking a web search API or executing fetch code.

---

## Key Takeaway

Architectural design requires selecting the appropriate degree of autonomy. While less autonomous, highly deterministic pipelines provide the control and immediate business value required by the industry today, highly autonomous workflows offer flexible orchestration but are still constrained by their unpredictability and remain an active area of research.
