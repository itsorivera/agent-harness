
## Managed Runtime: Microsoft Foundry Agent Service

Microsoft Foundry Agent Service is a fully managed service designed to empower developers to securely build, deploy, and scale high-quality AI agents without managing underlying compute and storage resources. It eliminates complex API-level orchestration by offering deployment through the Foundry portal or in code with fewer than 50 lines.

### Agent Classification Topologies

1. **Declarative Agents:** Defined through configuration rather than manual orchestration code.
   * **Prompt-based agents:** A single agent configured with a model, instructions, tools, and prompts (the baseline design pattern).
   * **Workflow agents:** Multi-agent orchestrations configured directly in YAML, coordinating autonomous sub-agents across complex workflows.
2. **Hosted Agents:** Containerized agents developed and deployed in code, fully hosted by the Foundry platform. Provides granular control over custom execution logic while abstracting physical infrastructure.

### Platform Capabilities
* **Automatic Tool Calling:** End-to-end execution loop managed by the runtime (model invocation, tool routing, argument passing, output gathering).
* **Securely Managed Data:** Native state and session persistence powered by the Responses API.
* **Extensive Tool Catalog:** Standardized integrations including Code Interpreter, File Search, Web Search, native Azure platform connectors, and external custom APIs.
* **Flexible Model Selection:** Dynamic binding to optimal models based on latency, reasoning requirements, and cost boundaries.
* **Enterprise-Grade Security:** Keyless authentication architectures, native Content Safety filters, and rigorous data privacy compliance out of the box.
* **Customizable Storage Solutions:** Choice between platform-managed persistence and Bring-Your-Own-Storage (Azure Blob Storage) for enterprise auditability and governance.
* **Observability & Tracing:** Out-of-the-box telemetry tracking internal reasoning loops, tool latency, run status, and debugging data in production.