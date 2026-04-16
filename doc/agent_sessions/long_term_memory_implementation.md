# Long Term Memory (LTM) Implementation with RedisVL

This document outlines the professional implementation of a **Long-Term Memory (LTM)** system for our AI agent harness, using **RedisVL** as the vector database and following **SOLID** architectural principles.

---

## Architecture Overview

The memory system follows the **Ports & Adapters (Hexagonal Architecture)** pattern to ensure decoupling between the core agent logic and the underlying storage technology (Redis).

### 1. The Port (Core Interface)

In `src/core/ports/ltm_repository_port.py`, we define the `LTMRepositoryPort`. This abstract base class ensures that our agent only knows **what** it can do with memory (store, retrieve, check duplicates) but not **how** it is stored.

### 2. The Redis Adapter (Infrastructure)

The `RedisLTMRepositoryAdapter` in `src/adapter/repository/memory_persistence/LTM/` implements the port using:

- **RedisVL**: To manage vector search indices.
- **RedisJSON**: To store memory objects as structured documents.
- **RediSearch**: To perform hybrid semantic searches (Vector + Metadata filtering).

### 3. Declarative Schema (DDL)

We use a YAML-based definition (`db/memory/redis_ltm_schema.yaml`) to specify the data structure:

- **Fields**: `content` (text), `memory_type` (tag), `user_id` (tag), `created_at` (text).
- **Vector Field**: `embedding` (flat algorithm, 1024 dims - matching AWS Bedrock Titan, cosine distance).

---

## Specialized Agent Tools

The LTM capabilities are exposed to the agent via two main tools located in `src/core/local_tools.py`:

### 📥 `store_memory_tool`

Allows the agent to capture and persist knowledge during a conversation.

- **Features**:
  - **In-line Deduplication**: Before storing, it checks for highly similar existing memories (threshold 0.05 distance) to prevent redundancy.
  - **Auto-Embedding**: Converts text to vectors using the `AWS Bedrock Embedding Adapter`.
  - **Metadata tracking**: Stores the conversation `thread_id` and `user_id` for context tracking.

### 📤 `retrieve_memories_tool`

Allows the agent to search for past knowledge to answer current queries.

- **Features**:
  - **Semantic Vector Search**: Finds memories close in meaning to the user's query.
  - **Hybrid Filtering**: Restricts results to the specific `user_id` and optionally by `memory_type` (Episodic vs Semantic).
  - **Precision Control**: Implements a distance threshold (0.35) to ensure only relevant memories are returned.

---

## Integration & Dependency Injection

To maintain a clean and maintainable codebase, we implemented a **Factory Pattern** to register these tools in the `AgentDependenciesContainer`.

### Why a Factory?

Because the tools depend on the LTM Repository, and the Agent (configured in the Container) depends on the tools, a static import would cause a **Circular Dependency**.

**Solution**:

- The `get_memory_tools(ltm_repo, embedder)` function creates and returns the tools with dependencies already injected via closures.
- The `AgentDependenciesContainer` lazily initializes the Redis connection and injecting it into the factory at runtime.

---

## Key Features Recap

- **Persistence**: Memories survive agent restarts and can be shared across different threads for the same user.
- **Efficiency**: Redis Stack performs sub-millisecond vector similarity searches.
- **Scalability**: The system is designed to handle multiple users with isolated memory spaces via `Tag` filtering.
- **Flexibilidad**: By using Ports & Adapters, we can switch from Redis to Postgres (pgvector) without changing a single line of code in the Agent's tools.

---

## How to Initialize

## To create the underlying Redis index before running the app for the first time:

## Component Configuration & Troubleshooting

### Vector Dimensions Mismatch

A common issue occurs when the embedding model's output doesn't match the Redis index schema.

- **Amazon Titan (Bedrock)**: Produces **1024** dimensions by default.
- **OpenAI (text-embedding-3-small)**: Produces **1536** dimensions.

If you see `Invalid vector length` errors in RedisInsight (Search tab) or zero search results despite having keys, ensure `dims` in `db/memory/redis_ltm_schema.yaml` matches the model being used in `AWSBedrockEmbeddingAdapter`.

### Re-initializing the Index

If you change the schema (e.g., dimensions or algorithm), you **must** drop and recreate the index. The `create_index.py` script handles this using `overwrite=True`.

```powershell
uv run .\db\memory\create_index.py
```
