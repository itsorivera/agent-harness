# Client-Side Integration Guide: Consuming AI Streams

This guide explains how to properly consume the Agent Harness Streaming API from a client-side perspective (Web, Desktop, or Mobile).

## 1. Initiating the Stream

Unlike standard GET-based SSE (which uses `EventSource`), the Agent Harness API uses a **POST** request to allow complex payloads (thread IDs, system prompts, etc.).

### Headers

To negotiate a streaming connection, ensures the following headers are used:

- `Content-Type: application/json`
- `Accept: text/event-stream` (Optional but recommended)

### Payload

The `stream: true` flag is mandatory to trigger the asynchronous generator in the backend.

```json
{
  "question": "Can you explain quantum computing?",
  "stream": true,
  "thread_id": "unique-session-id",
  "user_id": "client-001"
}
```

## 2. Processing the Stream (The "Chunking" Logic)

When a stream is active, data arrives in independent packets (chunks) delimited by double newlines (`\n\n`). A professional client implementation must follow these steps:

1.  **Decodification**: Convert the incoming byte stream (Uint8Array) into a readable string (UTF-8).
2.  **Splitting**: Split the incoming buffer by the `\n\n` delimiter. One network packet might contain multiple SSE events.
3.  **Parsing**:
    - Discard the `data: ` prefix.
    - Check for the `[DONE]` termination marker.
    - Perform `JSON.parse()` on the remaining payload to extract the delta content.

### Example Implementation (JavaScript/Fetch API)

```javascript
const response = await fetch("/api/v1/agents/general/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ question: "Hello!", stream: true }),
});

const reader = response.body.getReader();
const decoder = new TextDecoder();
let accumulatedText = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value, { stream: true });

  // Process multiple SSE events in a single packet
  const lines = chunk.split("\n\n");
  for (const line of lines) {
    if (!line.startsWith("data: ")) continue;

    const payload = line.replace("data: ", "");
    if (payload === "[DONE]") {
      console.log("Stream finished.");
      break;
    }

    try {
      const json = JSON.parse(payload);
      const delta = json.choices[0].delta.content;
      accumulatedText += delta;
      updateUI(accumulatedText); // Update the typing effect
    } catch (e) {
      console.error("Error parsing chunk", e);
    }
  }
}
```

## 3. UI/UX Best Practices

### The "Cursor" Effect

Do not wait for the whole chunk. Append tokens to your state as they arrive to create the signature "typing" effect of AI assistants.

### Auto-Scrolling

If the response exceeds the viewport, implement an auto-scroll mechanism that only triggers if the user hasn't manually scrolled up to read previous content.

### Error Handling in Streams

Streams can fail mid-generation (e.g., token limit reached or network timeout).

- **Timeouts**: Implement a client-side timeout that triggers if no data is received for X seconds.
- **Visual Feedback**: Change the "stop" button back to "send" if the connection closes abruptly.

## 4. Connection Termination

The stream closes in two scenarios:

1.  **Server Finish**: The server sends `data: [DONE]\n\n` and closes the HTTP connection.
2.  **Client Abort**: Use an `AbortController` to allow the user to stop the generation. This is a critical senior-level feature for cost-saving and UX.

```javascript
const controller = new AbortController();
const signal = controller.signal;

// To stop the stream:
controller.abort();
```
