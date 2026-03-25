# Logging and Tracing Architecture

This document describes the logging and tracing strategy implemented in the **Agent Harness** application. It focuses on observability, maintainability, and thread-safety in high-concurrency environments.

---

## 1. Overview

The logging system is built on **Structlog**, a powerful logging library for Python that supports structured log formats (JSON or Console-colored output) and flexible context management. 

### Key Objectives
*   **Structured Logging**: Transition from plain-text logs to machine-readable JSON for production.
*   **Request Tracing**: All log entries originating from the same HTTP request share a unique **Correlation ID**.
*   **User Context**: Logs automatically include the `user_id` once the user context is established.
*   **Thread/Async Safety**: Context variables are isolated using `ContextVars` to prevent data leaking between concurrent requests.

---

## 2. Technical Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Logger Factory** | `structlog` | Structured log output and customization. |
| **Context Storage** | `contextvars` | Secure isolation of request-scoped data in async environments. |
| **Middleware** | `fastapi.middleware` | Automated generation and injection of tracing headers. |
| **Tracing IDs** | `uuid4` | Cryptographically strong unique IDs for setiap request. |

---

## 3. Tracing Mechanism

The system uses a **multi-dimensional tracing context**:

### 1. Correlation ID (Request-scoped)
Every request processed by the API is assigned a unique `correlation_id`.
*   **Generation**: Automatically added by the `add_correlation_id` middleware in `src/app.py`.
*   **Propagation**: Carried through all layers (Adapters -> Ports -> Core Logic) implicitly via context.
*   **Response Header**: Returned to the client as `X-Correlation-ID` for frontend/QA debugging.

### 2. User context (User-scoped)
A `user_id` can be bound to the log context to track all actions performed by a specific subject.
*   **Binding**: Performed manually in the Controller layer after extracting it from the request body.

---

## 4. How to Use

### Basic Logging
To logs events within any module, always use the project-wide logger utility:

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

# The correlation_id is injected automatically
logger.info("Initializing process", parameter="example_value")
```

### Binding Additional Context
If you are in a controller or a service and have access to additional metadata (e.g., `user_id` or `session_id`), bind it to the context:

```python
from src.utils.logger import set_context_vars

# Any key-value pair passed here will appear in all subsequent logs for this request
set_context_vars(user_id="12345", module="billing")

# This log will contain: { "event": ..., "correlation_id": "...", "user_id": "12345", "module": "billing" }
logger.warning("Operation failed")
```

---

## 5. Implementation Details

### Context Isolation
We use `structlog.contextvars` to ensure that context data stays within the execution flow of a single `async` task. This is critical for **FastAPI** as it handles many concurrent requests on the same event loop thread.

### Global Middleware
The tracing starts in `src/app.py` via an HTTP Middleware:
1.  Read `X-Correlation-ID` from request headers (if missing, a new one is generated).
2.  Call `set_correlation_id(id)` to save it in `ContextVars`.
3.  Inject the ID into the HTTP Response headers.

### Output Formatting
Configurable via `setup_logger(json_format=True)`.
*   **Production**: Set `json_format=True` to output logs as single-line JSON strings, ideal for ElasticSearch, Datadog, or CloudWatch.
*   **Development**: Set `json_format=False` for colored, human-readable terminal output.

---

## 6. Senior Recommendations for Developers
1.  **Don't pass Correlation IDs as arguments**: The architecture handles this implicitly. Passing the ID through function signatures creates code smell and maintenance overhead.
2.  **Use levels correctly**:
    *   `INFO`: High-level business flow.
    *   `ERROR`: Significant failures including stack traces (`exc_info=True`).
    *   `WARNING`: Recoverable anomalies or slow performance.
    *   `DEBUG`: Highly verbose data for development troubleshooting.
3.  **Include relevant fields**: Instead of `logger.info(f"User {id} logged in")`, use `logger.info("User login", user_id=id)`. Structured data is much easier to query in log management tools.
