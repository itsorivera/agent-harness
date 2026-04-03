# Issue: Bedrock Converse API Tool Protocol Validation

## Status: Fixed

## Description

When using the **AWS Bedrock Converse API** (via LangChain's `ChatBedrockConverse`), the system encountered a `botocore.errorfactory.ValidationException`. This error prevented the agent from processing new messages in specific conversation threads.

### Error Message

`botocore.errorfactory.ValidationException: An error occurred (ValidationException) when calling the Converse operation: The model returned the following errors: messages.2: tool_use ids were found without tool_result blocks immediately after. Each tool_use block must have a corresponding tool_result block in the next message.`

---

## Root Cause Analysis

### 1. Strict Message Sequencing

The Bedrock Converse API enforces a very strict protocol regarding tool usage:

- If an `AssistantMessage` contains a `tool_use` block, the **immediately following** message in the history must be a `ToolMessage` containing the `tool_result`.
- If a `HumanMessage` is inserted directly after a `tool_use` without an intervening `tool_result`, the API rejects the entire conversation history as invalid.

### 2. Failure Scenarios

In our implementation, this occurred due to:

- **Tool Refactoring**: A tool was renamed (e.g., from `manage_memory` to `store_memory_tool`). Old conversation threads still contained pending calls to the old tool name.
- **Interrupted Execution**: If the server crashed or an unhandled exception occurred within a tool, the graph would stop before generating the `ToolMessage`, leaving the `tool_use` "dangling" in the checkpointer's history.

---

## Solution: "Tool Result Always" Strategy

We refactored the `tool_node` in `src/core/langgraph/nodes.py` to implement a "Preventive Fallback" mechanism.

### Key Implementation Details:

1.  **Global Try/Except**: Every tool execution is wrapped in a try-except block.
2.  **Existence Check**: We explicitly check if the tool exists in our current registry before calling it.
3.  **Mandatory ToolMessage**: Even if a tool fails or is missing, the node **must** return a `ToolMessage` with `status="error"`. This satisfies the Bedrock Converse protocol and prevents the thread from being permanently broken.

### Code Improvement snippet:

```python
try:
    if tool_name not in self.tools_by_name:
        # Generate error message for missing tools
        outputs.append(ToolMessage(content=error_doc, tool_call_id=id, status="error"))
        continue

    # Execute actual tool
    tool_result = await self.tools_by_name[tool_name].ainvoke(args)
    outputs.append(ToolMessage(content=json.dumps(tool_result), tool_call_id=id))
except Exception as e:
    # Always return a ToolMessage even on exceptions
    outputs.append(ToolMessage(content=str(e), tool_call_id=id, status="error"))
```

---

## Impact

- **Increased Resilience**: The system can now recover from tool-level failures without corrupting the conversation history.
- **Graceful Degradation**: If a tool becomes unavailable (e.g., during a refactor), the agent can now explain the error to the user rather than crashing the entire session.
- **Protocol Compliance**: Ensures 100% compatibility with Amazon Bedrock's strict message sequence requirements.

---

## References

- **File**: `src/core/langgraph/nodes.py`
- **Related Issue**: `ValidationException` in `ChatBedrockConverse`
