# Agentic Workflow Architecture: Core Design Patterns

This document outlines the four fundamental software design patterns utilized in architecting Agentic AI systems. These patterns serve as the core structural templates for assembling individual intelligence operations into autonomous and resilient execution pipelines.

![Agentic design patterns](/doc/assets/agentic_design_patterns.png)
_Source: [Agentic AI by Andrew Ng - DeepLearning.AI](https://www.deeplearning.ai/courses/agentic-ai/)_

## 1. Reflection (Self-Correction Loops)

Reflection is the architectural pattern of utilizing a Large Language Model to iteratively evaluate and optimize its own outputs before returning a final payload.

- **Implementation:** The initial generated payload (e.g., source code or text) is routed into a secondary evaluation prompt. The model is instructed to critique the output against strict rubrics (efficiency, edge cases, standard compliance). The resulting critique is then fed back to the model as context to generate structural revisions.
- **Environmental Grounding:** This pattern is frequently augmented by integrating external state feedback. For instance, executing generated code against a unit test sandbox and injecting the resulting stack traces directly into the reflection context vector.
- **Engineering Characteristics:** It provides a highly efficient performance optimization loop without the overhead of model fine-tuning.

## 2. Tool Use (Function Calling)

Tool Use expands the operational capabilities of an agent beyond language processing, allowing it to dynamically interact with and mutate external environments.

- **Implementation:** The model is structurally exposed to an array of defined functional schemas (e.g., OpenAPI specs). Upon reasoning, the model constructs executable payloads (such as JSON representations of API calls).
- **Use Cases:** Routing complex mathematical requests to an isolated Python execution environment, dynamically executing database queries, or invoking web search APIs to mitigate knowledge cut-off hallucinations.

## 3. Planning (Dynamic Graph Orchestration)

Planning is the system's ability to autonomously construct the Directed Acyclic Graph (DAG) of operations required to resolve a highly abstract user request.

- **Implementation:** Rather than engineers hardcoding a static execution logic, the model operates as a high-level orchestrator. It breaks the objective into a logical sequence of discrete operations, selecting the appropriate models or tools in real-time. (e.g., sequencing a pose-estimation model, followed by an image generation model, and concluding with a Text-to-Speech API).
- **Engineering Characteristics:** While planning architectures unlock immense general-purpose flexibility and can solve combinatorial edge cases, they are considered experimental. They suffer from high state drift and are significantly harder to securely constrain.

## 4. Multi-Agent Collaboration

This pattern adopts principles similar to a microservices architecture. It abandons monolithic, high-context prompts in favor of fragmented, inter-communicative agent personas.

- **Implementation:** A complex process is mapped into a multi-node system where each node is an LLM explicitly configured with a narrow persona (e.g., a pipeline separated into "Researcher", "Writer", and "Editor" agents). These nodes interact collaboratively or adversarially via passed states.
- **Engineering Characteristics:** Foundational frameworks like ChatDev utilize this to emulate enterprise workflows (Programmers, QA Testers, Managers). Splitting the global cognitive load across distinct specialized boundaries significantly reduces out-of-bounds generation, yielding superior empirical results for intricate tasks.

---

## Key Takeaway

Architecting advanced Agentic AI systems requires moving beyond static, single-turn prompts. Production-level agent architecture is defined by the structural integration of Reflection, Tool Use, Planning, and Multi-Agent Collaboration to build dynamic, self-correcting, and highly segmented logic graphs.
