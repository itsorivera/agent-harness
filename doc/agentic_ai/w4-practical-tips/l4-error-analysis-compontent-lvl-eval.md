# Practical Tips: Component-Level Evaluations

While End-to-End (E2E) evaluations are critical for measuring overall system performance, they are often too expensive, slow, and noisy for rapid iterative development. **Component-Level Evaluations** allow teams to isolate and optimize specific bottlenecks with high precision.

## 1. The Limitations of E2E Evals

![Limitations of E2E Evals](/doc/assets/limitations-of-e2e-evals.png)
__Source:__ [Agentic AI by Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/)

- **Cost/Latency**: Running a full multi-step agent workflow for every minor change is resource-intensive.
- **Noise**: Randomness in component A (e.g., non-deterministic LLM drafting) can mask significant quality improvements in component B (e.g., a better retrieval logic).
- **Complexity**: Hard to attribute a final failure to a specific internal step without detailed tracing.

## 2. Implementing Component-Level Evals

Isolate a single component (e.g., Web Search) and build a targeted benchmark.

### Case Study: Web Search Optimization

![Case Study: Web Search Optimization](/doc/assets/case-study-web-search-optimization.png)
__Source:__ [Agentic AI by Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/)

Instead of evaluating the final research report, evaluate just the search results:

1.  **Gold Standard Creation**: Have a human expert define a list of "ground truth" authoritative resources for a set of queries.
2.  **Comparison Metrics**: Use Information Retrieval (IR) metrics like **F1 Score** or **Precision@K** to measure the overlap between the agent's search results and the gold standard.
3.  **Hyperparameter Tuning**: Rapidly test variables like:
    - Search providers (Google vs. Bing vs. Tavily).
    - Result count ($K$).
    - Recency filters (date ranges).

## 3. Advantages of the Component Focus

- **Signal Clarity**: Provides a direct feedback loop for the developer working on that specific module.
- **Team Decoupling**: Large projects can assign different teams to optimize different components (e.g., "Search Team" vs. "Drafting Team") with independent, measurable KPIs.
- **Development Velocity**: Component-level tests usually run in seconds, whereas E2E agents might take minutes.

## 4. The Final Verification Loop

Component-level improvement does not always guarantee E2E improvement. Before declaring a task finished:

1.  Optimize the component using targeted evals.
2.  Run a final **End-to-End Eval** to confirm that the component-level gains translate into a better user-facing result.

---

_Next Topic: Techniques for improving isolated component performance._
