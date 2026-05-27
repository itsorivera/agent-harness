# Agentic Design Patterns: Creating Planning Workflows

To execute an autonomous plan reliably, the agent's internal reasoning must be translated into a format that downstream code can parse without ambiguity. This stage focuses on the transition from high-level "intent" to structured "execution steps."

## 1. Structured Output Formats

Relying on plain text or Markdown for multi-step plans is error-prone. Modern agentic workflows favor machine-readable schemas:

### JSON (The Industry Standard)

- **Why**: Native compatibility with most programming languages and highly robust LLM generation.
- **Structure**: Typically an array of objects where each object represents a discrete task.
- **Example Schema**:
  ```json
  [
    {
      "step": 1,
      "description": "Retrieve product list for 'round sunglasses'",
      "tool": "get_item_descriptions",
      "arguments": { "query": "round" }
    },
    { "step": 2, ... }
  ]
  ```

### XML

- **Why**: Useful for complex tagging or when the LLM needs clear delimiters to distinguish between reasoning and tool calls.
- **Structure**: Uses specific tags like `<step>`, `<tool>`, and `<args>`.

## 2. Prompting for Structured Plans

To get a reliable plan, the system prompt must be explicit:

1.  **Tool Catalog**: Provide clear descriptions of available functions/tools.
2.  **Schema Enforcement**: Instruct the model to return _only_ the specific format (JSON/XML).
3.  **Ambiguity Reduction**: Define exactly how arguments should be parsed and passed to tools.

## 3. Benefits of Machine-Readable Plans

- **Reliability**: Programmatic parsers can catch formatting errors before execution.
- **Traceability**: Each step in the JSON/XML array can be logged and monitored independently.
- **Interoperability**: The output can be directly passed to execution engines or multi-agent orchestrators.

---

_Next Topic: Using code generation as the ultimate planning language._
