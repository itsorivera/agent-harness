# Lecture 3: Tool Calling Syntax and implementation

This lecture focuses on the technical implementation of tool calling within agentic workflows, specifically highlighting the use of **AISuite**, an open-source library designed to unify interactions across multiple LLM providers.

## 1. Core Concept: Tool Request vs. Tool Execution

It is important to clarify that, technically, an LLM does not "call" a tool. Instead, it **requests** that the developer's code executes a specific function with provided arguments. However, in common developer parlance, this is often abbreviated to "the LLM calls the tool."

## 2. The AISuite Library

[AISuite](https://github.com/andrewyng/aisuite) provides a standardized syntax for interacting with various LLMs (GPT-4, Claude, Llama, etc.), closely mirroring the OpenAI API structure.

### Key Syntax Example:

```python
response = client.chat.completions.create(
    model="openai:gpt-4o",
    messages=messages,
    tools=[get_current_time],
    max_turns=5
)
```

## 3. Automatic Schema Generation

One of the most powerful features of AISuite is its ability to automatically describe functions to the LLM.

### Implementation Example:

By simply defining a Python function with a clear docstring, AISuite automatically extracts the metadata:

```python
def get_weather(city: str, unit: str = "celsius"):
    """
    Fetches the current weather for a specified city.

    Args:
        city: The name of the city (e.g., 'London', 'Tokyo').
        unit: The temperature scale to use ('celsius' or 'fahrenheit').
    """
    return f"The weather in {city} is 22 degrees {unit}."
```

- **Docstring Parsing**: The library inspects the function's name, the `Args` section, and the general description to understand its purpose.
- **JSON Schema**: Behind the scenes, AISuite generates the complex JSON structure that LLM providers expect. For the example above, the generated schema would look like this:

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "Fetches the current weather for a specified city.",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {
          "type": "string",
          "description": "The name of the city (e.g., 'London', 'Tokyo')."
        },
        "unit": {
          "type": "string",
          "description": "The temperature scale to use ('celsius' or 'fahrenheit').",
          "default": "celsius"
        }
      },
      "required": ["city"]
    }
  }
}
```

This automation eliminates the need for developers to manually write lengthy prompts or complex JSON structures to define available tools.

## 4. Managing Multi-Turn Interactions

The `max_turns` parameter is a critical safety feature in agentic loops.

- **Definition**: It sets a ceiling on how many times the LLM can request sequential tool calls (e.g., Tool A -> Result -> Tool B -> Result) before the loop is forced to terminate.
- **Best Practice**: A common default is `5`. This prevents potential infinite loops where an LLM might repeatedly call tools without reaching a final answer.

## 5. Unified Execution Loop

Unlike some lower-level APIs where the developer must manually intercept the tool request, execute the function, and feed the result back to the LLM, AISuite handles this entire cycle within the `create` call. It orchestrates the tool execution and provides the final consolidated response.

## 6. The Power of Code Execution

While many tools are task-specific (like getting the current time), the **Code Execution Tool** is uniquely powerful. Giving an LLM the ability to write and execute code provides it with a general-purpose capability to solve complex mathematical problems, manipulate data, and interact with systems in a highly flexible manner.

---

_Next Topic: Specialized Code Execution Tools for LLMs._
