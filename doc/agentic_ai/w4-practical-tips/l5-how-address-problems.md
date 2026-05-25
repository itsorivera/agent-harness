# Practical Tips: Strategies for Addressing Component Failures

Once error analysis identifies a bottleneck, the strategy for improvement depends on the nature of the component. This guide outlines common patterns for optimizing both LLM-driven and traditional software components.

## 1. Improving Non-LLM Components

These include search engines, RAG retrieval systems, or specialized ML models (e.g., speech-to-text, object detection).

- **Hyperparameter Tuning**:
  - _Web Search_: Adjust date ranges, result counts ($K$), or site filters.
  - _RAG Retrieval_: Tune chunk sizes, overlap settings, or vector similarity thresholds.
  - _Traditional ML_: Adjust classification or detection thresholds to balance precision and recall.
- **Provider Replacement**: Frequently swap providers (e.g., switching from a generic search API to a specialized research API) to find the best fit for your specific domain.

## 2. Improving LLM-Based Components

For steps involving text generation or reasoning:

- **Prompt Optimization**:
  - _Detailed Instructions_: Clarify constraints and output formats.
  - _Few-Shot Prompting_: Provide 1–5 concrete examples of desired input/output pairs.
- **Model Switching**: Leverage tools like **AISuite** to benchmark different LLMs.
  - _Heuristic_: Frontier models (e.g., GPT-4, Claude 3.5) excel at complex instruction-following (e.g., PII redaction), while smaller models (e.g., Llama 3-8B) are efficient for simple, factual retrieval.
- **Task Decomposition**: If a step is too complex, break it into a chain of simpler prompts or a **Generation + Reflection** pattern.
- **Fine-Tuning**: A high-effort/high-reward "last resort." Use only for mature applications where you need to squeeze the final 2–5% of performance out of a model and you have a robust dataset.

## 3. Honing Engineering Intuition

Developing high-performing agents requires deep intuition about model capabilities.

- **Instruction Following vs. Factuality**: Understand that a model's ability to "know things" is distinct from its ability to "obey constraints."
- **Continuous Benchmarking**: Regularly test new model releases against a personal set of "vibe-check" queries or component-level evals.
- **Code/Prompt Archaeological Research**: Study prompts used in respected open-source projects or high-quality developer communities to learn advanced structural patterns.

## 4. Prioritizing Quality over Cost

In the early development phase, focus exclusively on output quality. Once the system reaches the desired performance threshold, transition to optimizing for **latency** and **cost**.

---

_Next Topic: Optimizing Cost and Latency in Production Workflows._
