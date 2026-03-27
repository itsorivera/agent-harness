# Running and Debugging Strategies for Agent Harness

This document outlines the two complementary methods for running and debugging the agent harness project. Each approach serves a distinct purpose in the development lifecycle.

---

## 1. Custom FastAPI Server (Implementation & Deployment)

**Entry Point:** `run.py` (which launches `src/app.py`)
**Typical Port:** `8000`

### Purpose
This is the primary application server. It is used for production-like environments, integration testing with other backends/frontends, and handling custom business logic.

### Key Features
*   **Custom API Structure:** Exposes domain-specific endpoints (e.g., `/api/v1/agents/general/query`).
*   **Dependency Injection:** Manages the lifecycle of LLM providers, checkpointers, and tools using the custom `AgentDependenciesContainter`.
*   **Production Readiness:** Includes custom middlewares for:
    *   **CORS:** Allowing cross-origin requests from web clients.
    *   **Observability:** Generating and propagating `correlation_id` and tracking metrics.
    *   **Error Handling:** Standardized JSON responses for exceptions.

### How to Run
```powershell
uv run .\run.py
```

---

## 2. LangGraph Development Server (Debugging & Observability)

**Entry Point:** `langgraph.json` (which uses `src/main_graph.py` as a factory)
**Typical Port:** `8100` (or `8000` if the custom API is not running)

### Purpose
This server is designed exclusively for developer experience and advanced observability. It implements the standard **LangGraph Server API**.

### Key Features
*   **Visual Debugging:** Enables the use of [LangGraph Studio](https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/) and the [AgentChat Vercel UI](https://agentchat.vercel.app/).
*   **Graph Visualization:** Provides a real-time graphical view of state transitions and node execution.
*   **State Inspection:** Allows deep inspection of the message history and internal state variables of any thread without manual logging.
*   **Time Travel:** Supports re-running specific nodes with edited state data to test "what-if" scenarios.

### Configuration
Requires a `langgraph.json` file in the root directory pointing to a compiled graph factory:
```json
{
  "graphs": {
    "agent": "src/main_graph.py:get_agent"
  }
}
```

### Prerequisites
To use the `langgraph dev` command locally without Docker, you must install the `langgraph-cli` with the `inmem` component (which provides the required `langgraph-api`).

```powershell
uv add "langgraph-cli[inmem]"
```

### How to Run
Use `uv run` to ensure the command is executed within the project's virtual environment:

```powershell
uv run langgraph dev --port 8100
```

---

## 3. Comparison Summary

| Feature | Custom FastAPI (`run.py`) | LangGraph Dev Server |
| :--- | :--- | :--- |
| **Primary Use Case** | Product Integration / Deployment | Developer Debugging / Monitoring |
| **API Format** | Custom REST (v1/api/...) | Standard LangGraph Protocol |
| **Client Support** | Custom Frontends / Third-party APIs | LangGraph Studio / Vercel Web UI |
| **Observability** | Log-based (Correlation IDs) | Visual (Graph Nodes & State) |
| **Custom Logic** | Auth, Metrics, Advanced Routing | Graph execution only |

---

## 4. Recommended Workflow: The "Dual-View" Setup

During active development, it is highly recommended to run both servers simultaneously on different ports:

1.  **Terminal 1:** Run `uv run .\run.py` on port `8000`. Use this for your actual frontend or API testing (e.g., Postman).
2.  **Terminal 2:** Run `uv run langgraph dev --port 8100` on port `8100`. Use this with the [Vercel Web UI](https://agentchat.vercel.app/?apiUrl=http://localhost:8100&assistantId=agent) for real-time inspection of the graph logic.

By doing this, you can build your application with full control over the API while having "X-ray vision" into the agent's brain when things get complex.
