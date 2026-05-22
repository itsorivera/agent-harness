# Lecture 5: Model Context Protocol (MCP)

The **Model Context Protocol (MCP)** is an open standard, originally proposed by Anthropic and now widely adopted, designed to provide LLMs with a unified way to access external context and tools.

## 1. The Problem: The $M \times N$ Integration Challenge

Before MCP, every application developer had to write custom wrappers for every tool or data source they wanted to integrate (Slack, Google Drive, GitHub, Postgres, etc.).

- If there are $M$ applications and $N$ tools, the community ends up doing $M \times N$ work.
- **The MCP Solution**: By standardizing the interface, the integration work is reduced to $M + N$. Developers build one MCP server for a tool, and any MCP-compliant client can instantly use it.

## 2. Core Architecture: Clients and Servers

MCP operates on a client-server model:

- **MCP Clients**: These are the AI applications (like cloud desktops or IDEs) that want to consume tools or data.
- **MCP Servers**: These are the "connectors" or wrappers that provide access to specific resources (e.g., a GitHub MCP server, a Slack MCP server).

## 3. Resources vs. Tools

Within the MCP documentation, two primary types of integration are defined:

- **Resources**: Specifically designed for fetching data or providing context to the LLM (e.g., reading a file).
- **Tools**: More general-purpose functions that allow the LLM to take actions in the external world (e.g., creating a pull request or posting a message).

## 4. Practical Example

A common use case involves connecting an AI desktop application (Client) to a GitHub MCP server.

- **Workflow**:
  1. The user asks to "Summarize the README."
  2. The Client requests the file content from the GitHub MCP Server using a `resources` call.
  3. The Server returns the long Markdown text.
  4. The LLM processes this context and generates the summary.
- **Extended Capability**: The same server can provide more complex tools, such as `list_pull_requests`, which the LLM can decide to use to fulfill specific user queries.

## 5. Conclusion: Towards Disciplined Agentic Design

The adoption of standards like MCP marks a shift toward more scalable and modular agentic architectures. This concludes the module on tool use.

_Next Module: Evaluations and Error Analysis — Moving from ad-hoc testing to a disciplined evaluation process._
