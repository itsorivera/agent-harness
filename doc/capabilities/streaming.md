# Capability: Streaming Responses (SSE)

## Overview

This feature enables the agent to send real-time responses to the client using the Server-Sent Events (SSE) protocol. Instead of waiting for the full LLM graph to complete, the system streams tokens as they are generated, significantly improving the perceived latency (Time To First Token).

## Architecture

Following the **Hexagonal Architecture** (Ports and Adapters) principles, the implementation is decoupled into three layers:

### 1. Core Port (`AgentPort`)

The `AgentPort` interface was extended with the `stream_message` method. This defines the contract that any agent must implement to support real-time data flow.

```python
@abstractmethod
async def stream_message(self, ...) -> AsyncIterator[str]:
    pass
```

### 2. Infrastructure Adapter (`LanggraphAgentAdapter`)

The LangGraph adapter implements the streaming logic using the `.astream()` method.

- **Protocol Compliance**: It transforms raw LLM chunks into the standard SSE format (`data: <content>\n\n`).
- **Provider Abstraction**: It includes specialized logic to extract text from multi-modal or list-based content blocks common in enterprise providers like AWS Bedrock / Anthropic Claude.

### 3. Application Layer (REST API)

The FastAPI controller manages the delivery mechanism:

- **Schema**: Added `stream: bool = False` to the `QueryRequest` model.
- **Response**: Uses `StreamingResponse` with `media_type="text/event-stream"`.

## Usage Details

### Request Format

Clients can toggle streaming by setting the `stream` flag in the JSON body:

```json
{
  "question": "What is the current market trend?",
  "thread_id": "conv-001",
  "user_id": "user-fausto",
  "stream": true
}
```

### Response Format

The server follows the industry standard (OpenAI-compatible) SSE format:

```text
data: {"choices": [{"delta": {"content": "The", "role": "assistant"}, "index": 0}], "object": "chat.completion.chunk"}
data: {"choices": [{"delta": {"content": " current", "role": "assistant"}, "index": 0}], "object": "chat.completion.chunk"}
...
data: [DONE]
```

## Why SSE?

- **Lightweight**: Uses standard HTTP without the overhead of WebSockets.
- **Easy Integration**: Supported natively by browsers and most AI SDKs (Vercel AI SDK, LangChain.js).
- **Directionality**: Perfect for AI assistants where data flows primarily from server to client.

## Design Decisions

- **Non-Breaking Change**: Streaming was added as an optional capability, preserving the stability of existing one-shot integrations.
- **Type Safety**: The adapter ensures all yielded chunks are converted to strings, preventing common encoding errors with Starlette/FastAPI.
- **Decoupling**: The core agent logic (the Graph) remains unaware of how the data is delivered, adhering to the Single Responsibility Principle.
