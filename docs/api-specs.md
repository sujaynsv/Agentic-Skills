# API and Workflow Specifications

This document outlines the core workflows and interfaces required to run the `Agentic-Skills` pipelines.

## MCP Configuration (`.mcp.json`)
Model Context Protocols are global APIs that agents use to interact with the real world. 
- **Google Workspace**: `j3k0/mcp-google-workspace`
- **Google Calendar**: `@cocal/google-calendar-mcp`
- **Food Delivery**: Custom Node.js/Puppeteer script in `skills/custom-mcps/food-mcp/`

## The `.pipeline` State Folder
The Software Factory (`/ship`) uses a strict file-based state machine. The agents expect these files to exist and be passed sequentially:

### 1. `.pipeline/specs.md`
- **Writer**: Planner Persona
- **Reader**: Coder, Tester, Reviewer
- **Format**: Markdown with technical specifications, architecture decisions, and edge case definitions.

### 2. `.pipeline/changes.md`
- **Writer**: Coder Persona
- **Reader**: Tester, Reviewer
- **Format**: Markdown summary of files modified, logic implemented, and any deviations from the spec.

## Trigger Commands
All skills are invoked via slash commands defined in `skills/custom/slash-commands/SKILL.md`.

| Command | Persona | Input Required |
|---------|---------|----------------|
| `/ship` | `software-factory` | Feature request description |
| `/fix-build` | `self-healing-build` | Terminal test command |
| `/hunt` | `bounty-hunter` | GitHub Issue URL / Number |
| `/ghostwrite`| `ghostwriter` | None |
| `/sentinel` | `background-sentinel` | None |
| `/order` | `agent-concierge` | Natural language food request |
