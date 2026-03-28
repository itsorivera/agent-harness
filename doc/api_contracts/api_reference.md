# API Reference - Agent Harness

## Endpoints

### 1. General Agent Query

**URL:** `/api/v1/agents/general/query`  
**Method:** `POST`  
**Description:** Send a query to the general-purpose AI agent.

### 2. Financial Advisor Agent Query

**URL:** `/api/v1/agents/financial-advisor/query`  
**Method:** `POST`  
**Description:** Send a query to the financial advisor agent. This agent has access to market tools and is protected by HITL (Human-In-The-Loop) policies.

---

## Request Contract (`QueryRequest`)

The API follows a polymorphic contract that supports both **New Interactions** and **HITL Resumptions**.

| Field       | Type             | Required | Description                                                                  |
| :---------- | :--------------- | :------- | :--------------------------------------------------------------------------- |
| `question`  | `string`         | No\*     | The user's query in natural language. _Required for new interactions._       |
| `thread_id` | `string`         | Yes      | Unique identifier for the conversation session (UUID recommended).           |
| `user_id`   | `string`         | Yes      | Identifier for the user making the request.                                  |
| `decisions` | `list[Decision]` | No       | List of review decisions for pending tools. _Required for HITL resumptions._ |

### `Decision` Object Structure

| Field         | Type     | Required | Description                                                        |
| :------------ | :------- | :------- | :----------------------------------------------------------------- |
| `id`          | `string` | Yes      | The ID of the tool call being reviewed (found in `__interrupt__`). |
| `type`        | `string` | Yes      | The decision: `"approve"`, `"edit"`, or `"reject"`.                |
| `edited_args` | `dict`   | No       | New arguments if `type` is `"edit"`.                               |
| `message`     | `string` | No       | Optional rejection reason or message for the agent.                |

---

## Response Structure

The agent returns a dictionary representing the finalized state or a pending interrupt.

| Field                     | Description                                                 |
| :------------------------ | :---------------------------------------------------------- |
| `response`                | The internal state of the LangGraph agent.                  |
| `response.messages`       | History of clean AI/Human messages.                         |
| `response.messages_tools` | Full list of messages including tool calls and outputs.     |
| `response.__interrupt__`  | **CRITICAL**: If present, the request is paused for review. |
| `correlation_id`          | Unique ID for tracing the request logs.                     |

---

## Example JSON Payloads

### Start a new Conversation

```json
{
  "question": "Buy 5 shares of NVIDIA",
  "thread_id": "thread_abc123",
  "user_id": "user_789"
}
```

### Resume an Interrupted Thread (Approve)

```json
{
  "thread_id": "thread_abc123",
  "user_id": "user_789",
  "decisions": [
    {
      "id": "tooluse_xyz987",
      "type": "approve"
    }
  ]
}
```

### Resume an Interrupted Thread (Edit)

```json
{
  "thread_id": "thread_abc123",
  "user_id": "user_789",
  "decisions": [
    {
      "id": "tooluse_xyz987",
      "type": "edit",
      "edited_args": {
        "symbol": "NVDA",
        "shares": 2
      }
    }
  ]
}
```

### Resume an Interrupted Thread (Reject)

```json
{
  "thread_id": "thread_abc123",
  "user_id": "user_789",
  "decisions": [
    {
      "id": "tooluse_xyz987",
      "type": "reject",
      "message": "User canceled the order: too expensive at this moment."
    }
  ]
}
```
