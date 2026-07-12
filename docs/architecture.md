# Agentic-Skills Architecture

The `Agentic-Skills` repository is structured around a central **Orchestrator Pattern**. The IDE invokes the main configuration which reads `skills_index.json` to load custom skills, rules, and MCPs (Model Context Protocols).

## Directory Structure
- `AGENTS.md`: Global behavioral rules and constraints.
- `.mcp.json`: Global configuration for Model Context Protocol servers.
- `skills_index.json`: Manages the registration and discovery of all skills in this repository.
- `skills/`: The core directory containing isolated agent logic.
  - `skills/custom/`: Custom agent roles (Personas) and workflows.
  - `skills/custom-mcps/`: Custom built MCP servers (e.g., `food-mcp`).

## Core Architecture Diagram

```mermaid
graph TD
    A[Antigravity IDE] -->|Slash Commands| B(BMaD Orchestrator)
    
    B -->|`/research`| C[Analyst Persona]
    B -->|`/plan`, `/review`| D[Builder Persona]
    B -->|`/debug`, `/ops`| E[Ops Persona]
    B -->|`/daily`, `/order`| F[Concierge Persona]
    
    B -->|`/ship`| G[Software Factory]
    B -->|`/fix-build`| H[Self-Healing Build]
    B -->|`/hunt`| I[Bounty Hunter]
    B -->|`/ghostwrite`| J[Ghostwriter]
    B -->|`/sentinel`| K[Background Sentinel]
    
    F -.-> L((Swiggy / Zomato MCP))
    F -.-> M((Gmail / Calendar MCP))
```

## The Software Factory Pipeline

The `/ship` command initiates a highly strict closed-loop pipeline for feature delivery:

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant Planner
    participant Coder
    participant Tester
    participant Reviewer
    
    User->>Orchestrator: `/ship "Add pagination"`
    Orchestrator->>Planner: Initialize `.pipeline/` folder
    Planner-->>Coder: Writes `.pipeline/specs.md`
    Coder-->>Tester: Writes code and `.pipeline/changes.md`
    Tester-->>Reviewer: Writes automated tests
    Reviewer->>User: Runs `git diff`, outputs `[VERDICT: APPROVED]`
```
