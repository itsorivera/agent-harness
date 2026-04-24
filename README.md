# Agent Harness: Enterprise-Grade Agent Orchestration & XAI Framework

## 🎯 Engineering Vision

**Agent Harness** is a robust solution designed to bridge the gap between Proof of Concepts (PoC) and production-grade agentic systems. This framework does not just orchestrate language models; it establishes a standard for **Governance, Explainability, and Architectural Rigor**, enabling the deployment of reliable autonomous agents in complex corporate environments.

As a **Senior AI Engineer and Architect**, this project demonstrates my ability to design scalable, decoupled, and auditable systems that resolve the security, latency, and opacity challenges inherent in current agent architectures.

---

## 🏗️ Architectural Blueprint

The system is built upon the principles of **Hexagonal Architecture**, ensuring total **Inversion of Control (IoC)** and strategic decoupling.

### Applied Strategic Principles:

- **Domain Isolation**: The system's core (`src/core`) is infrastructure-agnostic. It has no dependencies on databases, external APIs, or specific AI orchestration frameworks.
- **Contract-Driven Development**: The use of **Ports (interfaces)** ensures that any technical component can be replaced (e.g., swapping LangGraph for a custom solution) without side effects on core business logic.
- **Pluggable Infrastructure**:
  - **Orchestration Engine**: Modular state-based implementation using **LangGraph**.
  - **Polyglot Persistence**: Hybrid storage strategy with **PostgreSQL** for `Short-Term Memory` (State Checkpointing) and **RedisVL** for `Long-Term Memory` (Semantic Search/RAG).
  - **LLM Sovereignty**: Multi-provider abstraction (OpenAI, Anthropic, Bedrock) via adapters that normalize response schemas and manage fallbacks.

---

## 🧠 Explainability (XAI) as a First-Class Citizen

In enterprise environments, the "black box" nature of LLMs is an unacceptable risk. Agent Harness elevates explainability to a top-tier requirement.

- **Forced Structural Reasoning**: Through rigorous Pydantic schemas (`XAIResponse`), the system forces the model to generate a reasoning path (`reasoning`) and a chain of logical steps BEFORE emitting any action.
- **Auditability & QA Pipeline**: Every interaction persists its reasoning metadata alongside the technical response, facilitating post-mortem audits, regulatory compliance, and continuous prompt optimization based on real model "thought" data.

---

## 🛡️ Governance & Human-In-The-Loop (HITL)

I have designed and implemented an advanced **Interceptor Pattern** to manage security in high-impact operations.

- **Granular Interruption Gates**: A specialized guardian node (`hitl_gate`) evaluates every tool call against a set of configurable rules, suspending execution when oversight is required.
- **Interactive Decision Interface**: The framework supports a decision interface where humans can **Approve, Edit (injecting modified arguments on-the-fly)**, or **Reject** the action with direct corrective feedback to the model.
- **Persistent State Resilience**: Integration with checkpoint repositories ensures that the "pause" state is durable, enabling asynchronous approval flows that can span days without losing context.

---

## 📡 Observability and Enterprise Readiness (Day 2 Operations)

The project addresses critical operational challenges in the AI application lifecycle.

- **Distributed Tracing**: Implementation of **Correlation IDs** in the middleware to ensure request traceability from the REST layer to the atomic execution of a tool in the graph.
- **High-Concurrency Streaming**: Use of **Server-Sent Events (SSE)** with JSON enveloping to provide a fluid, reactive user experience for mission-critical applications.
- **Standardized Health Monitoring**: Native integration of health patterns (Liveness/Readiness probes) to facilitate orchestration in Kubernetes clusters.
- **MCP Protocol Readiness**: Engine ready for the **Model Context Protocol**, enabling standardized and secure integration of third-party external tools.

---

## 🛠️ Tech Stack & Rationale

| Component         | Selection          | Architectural Rationale                                                           |
| :---------------- | :----------------- | :-------------------------------------------------------------------------------- |
| **Orchestration** | LangGraph          | Superior capability for modeling cyclic state graphs and native persistence.      |
| **Vector Engine** | RedisVL            | Ultra-low latency semantic indexing and search for dynamic RAG.                   |
| **API Layer**     | FastAPI            | Exceptional asynchronous performance with self-documenting contracts via OpenAPI. |
| **Storage**       | PostgreSQL         | ACID integrity and robustness for managing long-running states and sessions.      |
| **Environment**   | Python 3.11 + `uv` | Reproducible and ultra-fast dependency management, reducing CI/CD times.          |

---

## 📂 System Archetype

```text
src/
├── adapter/          # Infrastructure (Technical implementation details)
│   ├── agent/        # LangGraph Adapter & Graph Strategies
│   ├── memory/       # Persistence Repositories (Postgres/Redis)
│   └── rest/         # External Communication Layer
├── core/             # Domain (Pure Logic and Contracts)
│   ├── ports/        # System Interfaces (Total abstraction)
│   └── tools/        # Agnostic business tool definitions
└── utils/            # Platform Cross-cutting (Logging, Tracing, Metrics)
```

This repository is a manifestation of my **AI Engineering** philosophy: the success of AI depends not just on the model, but on the solidity of the software engineering surrounding it.
