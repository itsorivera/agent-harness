## Overview & Architectural Tooling Strategy

Microsoft Foundry Agent Service provides flexibility in how you develop agents, with options ranging from visual interfaces to code-centric workflows. Understanding the different development approaches helps you choose the right tools for your scenarios and team preferences.

The platform establishes an underlying abstraction where the agent's logic, models, and tools remain standardized, while developers and architects select the authoring environment (web-based visual design vs. IDE/Git-integrated configuration) that matches the team's operational model.

[](/doc/assets/development-agent-foundry.png)

---

## Development Modalities: Foundry Portal vs. Visual Studio Code

### Foundry Portal Development
The Foundry portal provides a web-based interface for creating and managing AI agents without writing code. This approach is ideal when you want to quickly prototype ideas, collaborate with non-technical stakeholders, or manage agents through a centralized interface.

#### When to Use the Foundry Portal
The portal excels in these scenarios:
* **Quick prototyping:** Rapidly test agent concepts and configurations without setting up development environments.
* **Visual configuration:** Configure agents through intuitive forms and dropdowns rather than code.
* **Centralized management:** View and manage all agents across projects in one place.
* **Team collaboration:** Share agent configurations with stakeholders who prefer visual interfaces.
* **Resource oversight:** Monitor token usage, latency, and evaluation outcomes through dashboards.

The Azure portal provides immediate access to agent creation without installing additional tools. You simply navigate to your Foundry project, select the Agents section, and start building.

---

### Visual Studio Code Development
The Microsoft Foundry extension for Visual Studio Code brings enterprise-grade AI capabilities directly into your development environment. This approach suits developers who prefer working in familiar code editors and want tight integration with their development workflows.

#### Key Capabilities of the VS Code Extension
The extension organizes its features into three main sections:

1. **Resources** — Browse and manage your Foundry project assets directly from VS Code, including:
   * **Deployed models:** View and manage model deployments.
   * **Declarative agents:** View and configure prompt-based and workflow agents.
   * **Hosted agents:** View and manage containerized, code-deployed agents.
   * **Connections:** Manage connections to external services.
   * **Vector stores:** Organize document collections for File Search.

2. **Tools** — Access development and testing capabilities:
   * **Model Catalog:** Browse and deploy models from the catalog.
   * **Model Playground:** Experiment with models directly.
   * **Agent Playgrounds:** Test agents using remote or local playgrounds.
   * **Local Visualizer:** Debug and visualize agent behavior locally.
   * **Deploy Hosted Agents:** Deploy containerized agents to production.

3. **Help and Feedback** — Access documentation and support resources.


#### When to Use Visual Studio Code
The VS Code extension is ideal for:
* **Developer-centric workflows:** Build agents alongside your application code in a single environment.
* **Version control integration:** Track agent configurations in Git alongside your codebase.
* **Rapid iteration:** Make quick changes and test immediately without switching tools.
* **Code-first development:** Edit YAML configurations directly for precise control.
* **Local development:** Work on agent designs offline before deploying to Azure.

The extension installs directly from the Visual Studio Code Marketplace and connects to your existing Foundry projects.

---

## End-to-End Development Lifecycle Workflow

Regardless of your chosen approach, agent development follows a consistent lifecycle pattern across both modalities:


1. **Connect to your Microsoft Foundry project:** Authenticate and bind your environment to the project workspace.
2. **Create an AI agent in the Foundry portal with a descriptive name and purpose:** Initialize the agent entity.
3. **Configure agent instructions defining its behavior and capabilities:** Detail persona and guardrails in the portal or VS Code.
4. **Add tools to extend what the agent can do:** Attach sandboxed runners, search endpoints, or custom logic.
5. **Test the agent using integrated playgrounds:** Validate execution loops against remote or local testbeds.
6. **Iterate on the design based on test results:** Fine-tune prompts, instructions, and tool schemas.
7. **Deploy the agent to production:** Commit and promote configurations or containers to the target environment.
8. **Integrate the agent into your applications:** Consume agent endpoints using generated code or native SDKs.

The Foundry portal and VS Code extension both support this workflow, differing primarily in interface style rather than capabilities.

---

## Azure Infrastructure Architecture & Dependencies

Both development approaches share the same underlying Azure cloud infrastructure.

### Required Azure Resources
To develop agents with Microsoft Foundry Agent Service, you need:
* **Microsoft Foundry project:** Organizes your agents, models, and related assets in one place.
* **Model deployments:** Deployed AI models (such as GPT-4.1 or Claude Sonnet 4.6) that power your agents.

When you create a Microsoft Foundry project, the necessary infrastructure is provisioned automatically. As you add capabilities to your agents, such as File Search or custom tools, the service seamlessly integrates any required supporting services behind the scenes. If you choose to extend the capabilities of your agent even further, for example with Foundry IQ, you may need to deploy some additional Azure services.

### Optional Supporting Azure Services
Depending on your agent's capabilities, you might integrate additional Azure services:
* **Azure AI Search:** For advanced knowledge retrieval when using Foundry IQ or File Search tools.
* **Azure Storage:** For storing and managing files that agents can access.
* **Azure Key Vault:** For securely managing secrets and credentials.
* **Azure Functions:** For custom tool implementations and business logic.

These services integrate with your Foundry project as needed, but aren't required to get started building agents.

---

## Architectural Decision Guide: Choosing the Development Approach

Both the Foundry portal and Visual Studio Code extension provide complete agent development capabilities. Your choice depends on your workflow preferences, team composition, and integration requirements:

| Dimension | Foundry Portal | Visual Studio Code Extension |
|---|---|---|
| **Primary Audience** | Non-technical stakeholders, Product Owners, Rapid Prototypers | Software Engineers, AI Engineers, Enterprise Developers |
| **Configuration Format** | Visual forms, intuitive web dropdowns, graphical UI | Direct YAML configuration files, code-first editing |
| **Source Control (VCS)** | Centralized platform state in Foundry project | Direct Git repository integration alongside application code |
| **Tooling & Setup** | Zero setup; web-browser accessible via Azure | VS Code Marketplace extension installation, connected to Foundry |
| **Playground & Testing** | Cloud-based interactive web playground | Remote playgrounds, Local Playgrounds, and Local Visualizer |
| **Best-Fit Scenarios** | Quick prototyping, centralized asset oversight, stakeholder reviews | App co-development, offline design, CI/CD pipeline commits |

### Hybrid Adoption Pattern
* **Choose the Foundry portal** when you want visual configuration, centralized management, or quick prototyping without local development setup.
* **Choose Visual Studio Code** when you prefer developer-centric workflows, need tight integration with application code, or want version-controlled configuration files.

Many enterprise teams use both approaches concurrently: leveraging the portal for early architectural discovery, rapid prototyping, and business stakeholder feedback, while transitioning to the VS Code extension for granular YAML-level configuration, application integration, automated testing, and production deployment. The flexibility to switch seamlessly between both paths is an essential architectural strength of Microsoft Foundry Agent Service.