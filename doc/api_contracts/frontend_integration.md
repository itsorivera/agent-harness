# Frontend Integration Guide - Handling Agent Interactivity

## How the Agent Communicates with the UI

The Agent Harness uses an **Event-Driven Pause (Interrupt)** model.

### 1. State Inactivity Detection

Any time the frontend receives a response from the agent, it must check for the presence of the `__interrupt__` key at the root of the response.

```javascript
if (response.data.response?.__interrupt__?.length > 0) {
  // SHOW FORM / MODAL FOR REVIEW
} else {
  // SHOW FINAL AI MESSAGE
}
```

### 2. Identifying Interrupted Tools

The `__interrupt__` object contains a `value` dictionary which includes:

- `action`: The purpose (usually `"review_tools"`).
- `tool_calls`: An array of one or MORE tools requested by the agent.
- `rules`: Allowed user actions (approve, edit, reject).
- `description`: Text to show the user (e.g., "This execution requires approval").

### 3. Display Example (UI Recommendation)

| Data Point                | Frontend Treatment                                                       |
| :------------------------ | :----------------------------------------------------------------------- |
| `tool_calls.name`         | Modal Header (e.g., "Action Required: Place Order")                      |
| `tool_calls.args`         | Form Fields Table. If `"edit"` is allowed, these should be input fields. |
| `rules.allowed_decisions` | Conditional Rendering of "Approve", "Edit", and "Reject" buttons.        |

---

## The Resumption Flow (Step-by-Step)

### Step 1: Detect and Parse

Observe the `id` of each `tool_call`. This ID is required for the response.

### Step 2: User Decision

- **User clicks "Approve"**: Send `type: "approve"`.
- **User clicks "Reject"**: Send `type: "reject"`.
- **User clicks "Edit"**: Map the current form values (which may have been modified by the user) into `edited_args`.

### Step 3: Resume Request

Send a `POST` request to the same endpoint using the SAME `thread_id`.

**Payload to resume:**

```json
{
  "user_id": "current_user",
  "thread_id": "current_thread_id",
  "decisions": [
    {
      "id": "the_tool_call_id",
      "type": "the_user_decision",
      "edited_args": { ...only if user edited... }
    }
  ]
}
```

---

## Best Practices

- **Checkpointers & Persistence**: While the agent is in an `__interrupt__` state, the backend checkpointer preserves the execution stack. The frontend **MUST** provide the correct `thread_id` to resume correctly.
- **Multiple Interrupts**: Although the agent usually asks for one review at a time, it might request several. Ensure your UI can render a list of tool review cards rather than just one.
- **Error Handling**: If the user sends an invalid decision or an ID that doesn't exist, the backend will return an error status. Render these in the modal to guide the user.
