# Capability: Streaming Responses (SSE)

## Overview

This feature enables the agent to send real-time responses to the client using the Server-Sent Events (SSE) protocol. Instead of waiting for the full LLM graph to complete, the system streams tokens as they are generated, significantly improving the perceived latency (Time To First Token).

## Architecture

Following the **Hexagonal Architecture** (Ports and Adapters) principles on my project, the implementation is decoupled into three layers:

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

## Technical Standard: HTTP Server-Sent Events (SSE)

The streaming delivery relies on the **WHATWG Server-Sent Events** specification, a standard for sub-second, unidirectional data push over persistent HTTP connections. Unlike WebSockets, SSE is designed specifically for scenarios where data flows primarily from server to client, making it the optimal choice for LLM token delivery.

### Protocol Characteristics

- **Persistence**: SSE maintains a long-lived HTTP connection using `Keep-Alive`, avoiding the overhead of multiple handshakes.
- **Media Type Control**: The server communicates using `Content-Type: text/event-stream`, which signals the client and intermediate proxies to disable response buffering for immediate data visibility.
- **Event Framing**: Data is delivered in discrete "events" delimited by a double newline (`\n\n`). Each event follows a strict `field: value\n` format.
- **Fault Tolerance**: The protocol includes a native `retry` mechanism. If a connection drops, the client automatically attempts to reconnect, ensuring a robust user experience in unstable network conditions.

### Why SSE is the Industry Choice for AI

1. **Firewall Friendly**: Operates over standard HTTP/HTTPS (Port 80/443), bypassing restrictive corporate firewall rules that often block WebSockets.
2. **Resource Efficiency**: Consumes fewer resources than full-duplex protocols, as it doesn't require a dedicated socket upgrade.
3. **Synergy with JSON Enveloping**: Combining SSE with JSON allows sending usage metrics, citations, or source IDs without polluting the text stream, maintaining high extensibility (Protocol Compliance).

## Infrastructure & Deployment Considerations

Streaming architectures impose specific requirements on the transit layer (Ingress, Proxies, and Load Balancers) to prevent data stalling and connection exhaustion.

### 1. Transit Layer Optimization

- **Proxy Buffering**: Most modern proxies (Nginx, Traefik, HAProxy) buffer responses by default to optimize TCP throughput. This must be disabled for the SSE endpoints for real-time delivery.
  - _K8s Nginx Ingress_: `nginx.ingress.kubernetes.io/proxy-buffering: "off"`
- **Response Compression**: Gzip or Brotli compression should be carefully configured. If the compressor waits for a minimum chunk size before flushing, it will introduce artificial latency.
- **Connection Timeouts**: TCP/Proxy idle timeouts must be increased beyond the maximum expected inference time (e.g., 300s) to prevent premature connection termination.

### 2. HTTP Protocol Tradeoffs: 1.1 vs 2.0

- **HTTP/1.1 (The Browser Bottleneck)**: Browsers limit concurrent persistent connections to 6 per domain. In complex UIs, an SSE stream can exhaust available sockets, blocking other API calls.
- **HTTP/2 (The Scaling Gold Standard)**: Highly recommended for production. Its **Multiplexing** capability allows multiple SSE streams and standard API calls to share a single TCP connection, bypassing the browser's socket limit.

### 3. Client-Specific Challenges

- **Microfrontends (MFE)**: In federated architectures, multiple MFEs might open concurrent streams. HTTP/2 is critical here. Additionally, **CORS** must be explicitly configured to allow the `text/event-stream` handshake across different origins.
- **Desktop Applications**: Desktop clients (Electron, Native) lack browser-enforced connection limits but face frequent network context switches. Implementing a robust `retry` logic within the SSE events is essential for maintaining stream continuity across connection changes.

## Design Decisions

- **Non-Breaking Change**: Streaming was added as an optional capability, preserving the stability of existing one-shot integrations.
- **Type Safety**: The adapter ensures all yielded chunks are converted to strings, preventing common encoding errors with Starlette/FastAPI.
- **Decoupling**: The core agent logic (the Graph) remains unaware of how the data is delivered, adhering to the Single Responsibility Principle.
