# Agentic Design Patterns: Planning

The **Planning** design pattern enables highly autonomous agents to move beyond hard-coded deterministic sequences. Instead of following a fixed script, the agent dynamically generates and executes a custom set of steps to achieve a specific user objective.

## 1. From Deterministic to Autonomous

In traditional workflows, developers define the sequence of LLM calls in advance. In a planning pattern:

- **Phase 1: Plan Generation**: The LLM receives a user request and a set of tool descriptions. It then outputs a structured, step-by-step plan (a "checklist" for the task).
- **Phase 2: Sequential Execution**: The system iterates through the plan. For each step, it provides the LLM with the task description, the current step's instructions, and the cumulative context from previous steps.

## 2. Practical Case Studies

### Retail Inventory Agent

**Request**: "Find round sunglasses under $100 in stock."

![Retail Inventory Database](/doc/assets/retail-inventory-database.png)

1.  **Step 1**: Search product descriptions for "round."
2.  **Step 2**: Cross-reference filtered IDs with inventory database.
3.  **Step 3**: Filter in-stock items by price threshold.
4.  **Final Step**: Synthesize the results into a natural language response.

![Planning example: Retail Inventory Agent](/doc/assets/retail-inventory-agent.png)

### Email Assistant

**Request**: "Reply to Bob, confirm dinner, and archive the thread."

![Planning example: Email Assistant](/doc/assets/email-assistant.png)

1.  **Step 1**: Search for the specific email from "Bob" mentioning "dinner."
2.  **Step 2**: Generate and send a reply using the `send_email` tool.
3.  **Step 3**: Move the thread to the `Archive` folder using the `move_email` tool.

## 3. Current Industry Adoption

- **High Maturity (Coding Agents)**: Planning is the engine behind modern agentic coding assistants. It allows them to break complex software requirements into manageable, sequential implementation steps.
- **Experimental (General Assistants)**: Adoption is growing in general sectors, but remains challenging due to the inherent unpredictability of LLM-generated plans at runtime.

## 4. Key Advantages

- **Flexibility**: Handles an infinite variety of task combinations without requiring specific code for every edge case.
- **Scalability**: New capabilities can be added by simply providing the agent with more tools and updating their descriptions.
- **Contextual Reasoning**: The agent can adjust its strategy mid-execution based on the outputs of earlier steps.

---

_Next Topic: A deep dive into the internal "guts" of plan execution logic._
