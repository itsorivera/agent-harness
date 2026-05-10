## Memory Management System

An implementation of a robust memory management strategy for AI agents using **LangGraph** and **LangMem**. This part of the agent harness focuses on providing agents with long-term persistence and semantic memory capabilities.

![Memory Management Architecture](/doc/assets/manage-memory-agent-strategy.png)

## Core Memory Strategy

This agent utilizes a multi-layered memory approach designed for **Multitenancy** and **Semantic Precision**:

- **Semantic Memory:** Powered by `InMemoryStore` using `HuggingFaceEmbeddings` (`all-MiniLM-L6-v2`). This transforms natural language into 384-dimensional vectors for semantic search.
- **Hierarchical Isolation (Namespaces):** Memory is strictly partitioned using a tuple-based path.
  - Format: `(application_name, user_id, collection_type)`
  - Example: `('email_assistant', 'lance', 'collection')`
  - **Isolation:** Each `user_id` has a unique namespace, ensuring that private data from one user is never leaked to another during retrieval.
  ![Memory Isolation](/doc/assets/memory-hierarchical-isolation.png)
- **Active Memory Tools:**
  - `manage_memory`: Allows the agent to write, update, or prune its long-term memory store dynamically.
  - `search_memory`: Enables the agent to perform semantic lookups to retrieve relevant context from past interactions.

## Memory Architecture & Lifecycle

1.  **Identification:** The agent detects a piece of information worth remembering (e.g., "The user prefers afternoon meetings").
2.  **Storage:** Through `manage_memory`, the fact is sent to the `InMemoryStore`.
3.  **Vectorization:** The embedding model converts the text into a vector, which is indexed within the user's specific **Namespace**.
4.  **Retrieval:** During a new conversation, the agent calls `search_memory`. The system searches the user's isolated namespace for the most semantically similar memories to the current query.

## Session Management & Profiling

### Organizer Strategy for Scalability

To effectively organize memories while maintaining long-term relevance:

1.  **Namespace Partitioning:** Use the `namespace` parameter to separate global user knowledge from session-specific metadata.
2.  **Memory Distillation:** Implement background summarization to convert raw chat logs into atomic, high-value facts.
3.  **Context Ranking:** Use metadata and semantic similarity to rank memories by recency and relevance within the current session.
4.  **Atomic Chunking:** Store facts as independent units ("User likes Coffee") rather than large blobs of text to improve search accuracy.