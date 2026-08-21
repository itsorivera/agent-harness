# Taxonomy of Agentic Systems Architecture

This document outlines the conceptual framework for understanding the different layers involved in building and deploying Artificial Intelligence Agents. Distinguishing between these layers is critical for architectural clarity, security, and scalability.

## Key Concepts

### 1. Abstraction vs. Execution
The distinction between **Agent Frameworks** and **Agent Runtimes** lies in the difference between design and movement. Frameworks provide the structural components (prompts, tool definitions), while Runtimes manage the lifecycle of the process (loops, error recovery, and human-in-the-loop interactions).

### 2. The Contract vs. The Capability
A common point of confusion is the interaction with external environments. 
*   **The Framework (Level 1)** defines the **Contract**: It describes to the LLM what a tool does and what parameters it requires.
*   **The Harness (Level 3)** provides the **Capability**: It manages the actual infrastructure, API keys, and secure environments (sandboxes) required to execute the requested action.

### 3. Statefulness and Durability
Modern agentic systems require the ability to persist over time. **Agent Runtimes** ensure that an agent can pause its execution to wait for a human approval or a long-running process without losing its internal state or memory of the task.

### 4. Orchestration Layers
**No-Code/Low-Code** platforms act as a high-level abstraction layer. While they simplify the user experience, they internally orchestrate the underlying Frameworks, Runtimes, and Harnesses.

---

## Taxonomy of Agentic Systems Architecture and Abstraction

| Layer / Level | Technical Denomination | Primary Responsibility | Real-World Implementation Example (Audit Agent) |
| :--- | :--- | :--- | :--- |
| **Level 0: No-Code / Low-Code** | **Interface Abstraction Layer (Visual Orchestration)** | Democratization and speed. Defines business logic without writing code. | A finance manager uses **Zapier Central** to connect email to Excel, dragging a line so that "every time a receipt arrives, the amount is extracted." |
| **Level 1: Frameworks** | **Model Composition and Abstraction Layer** | Defining the structure and the communication "contract" with the LLM. | A developer uses **LangChain** to define the *Schema* (technical description) of a tool called `query_database`, teaching the model which parameters to request. |
| **Level 2: Runtimes** | **State and Lifecycle Management Layer** | Defining dynamic behavior: Loops, memory, pauses, and persistence. | **LangGraph** is used to create a flow where, if the LLM decides a bill is suspicious, the system **saves the state**, generates a ticket, and **pauses** until a human clicks "Approve." |
| **Level 3: Harnesses** | **Infrastructure and Operational Capabilities Layer** | Defining the physical/digital environment: execution, permissions, and protocols. | The agent uses an **MCP (Model Context Protocol) server** acting as a "secure tunnel" to physically access the corporate SQL database and download PDF files from a private server. |

---

## Summary of Relationships

*   **Frameworks** are the **Architectural Blueprints**.
*   **Runtimes** are the **Logistical Engine**.
*   **Harnesses** are the **Mechanical Tools and Environment**.
*   **No-Code** is the **User Dashboard** that wraps all the above.