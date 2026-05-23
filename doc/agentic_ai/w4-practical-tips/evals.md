# Practical Tips: Building and Evaluating Agentic Workflows

Developing effective agentic systems is an iterative process. This lecture outlines best practices for moving from an initial prototype to a reliable, production-ready system through disciplined evaluation.

## 1. Prototype-First Development

The most effective way to build an agentic system is to start with a "quick and dirty" prototype.

- **Avoid Over-Theorizing**: Don't spend weeks hypothesizing about potential edge cases.
- **Identify Real Error Modes**: Build a baseline system, run ~20 examples, and manually inspect the outputs to identify where the system actually fails.
- **Focus Effort**: Use these initial observations to prioritize which technical improvements are most necessary.

## 2. Iterative Evaluation (Evals)

Once error modes are identified (e.g., the system consistently extracts the wrong date from an invoice), you should create a small **Evaluation Set (Eval Set)** to track improvements.

- **Initial Scope**: Start small with 10–20 examples.
- **Growth**: Expand the eval set as your system becomes more sophisticated and you encounter more subtle edge cases.
- **Metric Alignment**: If you feel the system is getting better but the eval score isn't moving, iterate on the **evaluation criteria** themselves.

## 3. The 2x2 Evaluation Matrix

Evaluations can be categorized along two axes: the **Evaluation Method** and the **Target Type**.

|                                 | **Objective (Code-Based)**                                                   | **Subjective (LLM-as-a-Judge)**                                                                     |
| :------------------------------ | :--------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- |
| **Per-Example Ground Truth**    | **Example**: Verifying invoice due dates against a manually annotated list.  | **Example**: Checking if an essay mentions 5 specific "gold standard" points unique to each prompt. |
| **No Per-Example Ground Truth** | **Example**: Enforcing a strict 10-word limit across all generated captions. | **Example**: Grading charts against a universal rubric (e.g., "clear axis labels").                 |

![2x2 Evaluation Matrix](/doc/assets/image.png)
__Source:__ [Agentic AI by Andrew Ng](https://learn.deeplearning.ai/courses/agentic-ai)

### 3.1 Objective Evals

Used for tasks with clear, binary, or numerical success criteria.

- **Tools**: Regular expressions, word counters, or exact string matching.
- **Benefit**: Extremely fast and 100% consistent.

### 3.2 Subjective Evals (LLM-as-a-Judge)

Used for tasks where success is qualitative or has high linguistic variability.

- **Tools**: Using a highly capable model (e.g., GPT-4o) to grade the output of a smaller or task-specific agent.
- **Benefit**: Captures nuance and semantic meaning that code-based checks might miss.

## 4. Driving Development with Evals

- **Benchmarking**: Compare your system's performance against that of an **expert human**. This gap identifies the most productive areas for developer focus.
- **Decision Making**: As your evals become more sophisticated, you can rely on them to make data-driven decisions about prompt changes or algorithmic shifts, rather than relying on manual inspection for every change.

---

_Next Topic: Component-level evaluation and identifying the most productive improvements._
