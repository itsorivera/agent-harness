# Agentic Design Patterns: Planning with Code Execution

While JSON-based plans are effective for simple workflows, complex reasoning and data manipulation often benefit from **Code as Action**. In this pattern, the LLM generates executable code (typically Python) that serves as both the plan and the execution mechanism.

## 1. The Bottleneck of Atomic Tools

When building agents with traditional tools (e.g., `filter_rows`, `get_median`), developers often run into "tool sprawl."

![The bottleneck of atomic tools](/doc/assets/atomic-tools.png)
_Source: [Agentic AI by Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/)_

- **Brittleness**: New user queries often require new, specialized tools.
- **Inefficiency**: Complex logic requires a massive chain of tool calls, increasing latency and probability of failure.

## 2. Code as the Ultimate Planning Language

By allowing an LLM to write code (using libraries like `pandas`, `numpy`, or `scipy`), the agent gains access to thousands of pre-existing, well-documented functions.

![Code as the Ultimate Planning Language](/doc/assets/code-as-action.png)
_Source: [Agentic AI by Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/)_

### Advantages of Code Execution:

- **Rich Expression**: A single Python script can encapsulate loading, cleaning, transforming, and visualizing data.

![Superior Performance](/doc/assets/superior-performance.png)
_Source: [Agentic AI by Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/)_

- **Superior Performance**: Research (e.g., Xinyao Wang et al.) demonstrates that **Code as Action** consistently outperforms JSON-based or text-based planning in reasoning accuracy.
- **LLM Proficiency**: Models are trained on vast amounts of documentation and code, making them naturally adept at utilizing standard libraries to solve novel problems.

## 3. Implementation Workflow

1.  **Prompt**: "Identify the user query and return Python code to solve it, delimited by `<python>` tags."
2.  **Plan Embedding**: The code comments and structure represent the agent's internal plan.
3.  **Safe execution**: The generated code **must** be executed in a secure environment (e.g., a sandbox, Docker container, or services like E2B) to prevent security risks.

## 4. Current State and Challenges

- **Mature Sector**: Agentic coding assistants use this pattern to build, test, and refactor software.
- **Trade-off (Control vs. Autonomy)**: While code gives the agent more power to solve unforeseen edge cases, it reduces the developer's ability to predict the exact execution path at runtime.

---

_Next Topic: Collaborative reasoning with Multi-Agent Systems._
