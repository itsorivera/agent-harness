# Practical Tips: Error Analysis and Prioritization

In any complex agentic workflow, identifying which component to optimize is as important as the optimization itself. Structured **Error Analysis** is the primary tool for moving from "gut-feeling" development to data-driven prioritization.

![Error Analysis](/doc/assets/error-analysis.png)
__Source: [Agentic AI by Andrew Ng](https://learn.deeplearning.ai/courses/agentic-ai)__

## 1. Traceability and Observability

To effectively analyze errors, you must be able to inspect the internal state of the agent during execution.

![Trace and Span](/doc/assets/trace-and-span.png)
__Source: [Agentic AI by Andrew Ng](https://learn.deeplearning.ai/courses/agentic-ai)__

- **Trace**: The complete set of intermediate outputs for a single run of an agent.
- **Span**: The specific output or behavior of a single step within a workflow (a "span" is a component of a "trace").
- **Habit**: Develop a habit of reading traces regularly to build an intuition for how each component performs under different conditions.

## 2. The Error Analysis Workflow

When a system is underperforming, follow this systematic approach:

1.  **Isolate Failure Cases**: Put aside successful runs and focus exclusively on examples where the final output was unsatisfactory.
2.  **Inspect Spans**: Examine the intermediate outputs (the trace). Compare each component's performance against what a **human expert** would produce given the same input.
3.  **Identify the Root Cause**: Determine which component was the first to fail or produce subpar results.
    - _Note_: Avoid blaming downstream components for poor outputs if they were provided with low-quality inputs from an upstream step.

## 3. Systematic Prioritization (The Spreadsheet Method)

To make prioritization rigorous, track errors across a set of failing examples using a spreadsheet.

### Example Error Tracking Matrix:

![Error Tracking Matrix](/doc/assets/error-tracking-matrix.png)
__Source: [Agentic AI by Andrew Ng](https://learn.deeplearning.ai/courses/agentic-ai)__

| Query                    | Search Terms Status | Search Engine Output      | Selection Logic              | ... |
| :----------------------- | :------------------ | :------------------------ | :--------------------------- | :-- |
| "Black Hole Discoveries" | OK                  | **FAIL** (Too many blogs) | N/A (Bad input)              |     |
| "Seattle Real Estate"    | OK                  | OK                        | **FAIL** (Missed key source) |     |
| **Error Rate**           | **5%**              | **45%**                   | **15%**                      |     |

### Decision Criteria:

Prioritize components based on two factors:

1.  **Frequency**: Which component is responsible for the highest percentage of errors?
2.  **Solvability**: Do you have actionable ideas or alternative tools to improve that specific component?

## 4. Conclusion

![Conclusion](/doc/assets/conclusion.png)
__Source: [Agentic AI by Andrew Ng](https://learn.deeplearning.ai/courses/agentic-ai)__

Error analysis prevents "optimization theater" — spending weeks improving a component that isn't actually the bottleneck of the system. By focusing your technical effort where the data shows the most room for improvement, you drastically increase development velocity and system reliability.

---

_Next Topic: Case studies in advanced error analysis._
