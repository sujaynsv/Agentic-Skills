# Agentic-Skills Workspace

Welcome to the Agentic-Skills repository! This project transforms the Google Antigravity IDE into a fully-autonomous, multi-agent workspace powered by the Model Context Protocol (MCP) and custom BMaD personas.

## Key Features
- **BMaD Orchestration**: Specialized personas (Analyst, Builder, Ops, Concierge) for distinct workflows.
- **Custom Slash Commands**: Fast, intent-driven triggers (e.g., `/spec`, `/order`, `/daily`) that automate complex pipelines.
- **Extensive MCP Integration**: Pre-configured support for 15+ tools including Tavily, GitHub, Exa, Google Calendar, and FileSystem.
- **Custom Food MCP**: A bespoke, Puppeteer-driven Node.js server that fetches real-time data from Swiggy and Zomato.

## Tech Stack
- **Environment**: Google Antigravity IDE
- **Agent Architecture**: BMaD (Builder, Manager/Concierge, Analyst, Designer/Ops)
- **Tooling Standard**: Model Context Protocol (MCP)
- **Custom MCP Backend**: Node.js, Puppeteer, `@modelcontextprotocol/sdk`

## Prerequisites
- **Antigravity IDE**: Installed and configured.
- **Node.js 20+**: Required to run the custom `food-mcp` server.
- **API Keys**: Tavily, Exa, Brave Search, and a GitHub Personal Access Token (PAT).
- **Google Cloud Project**: (Optional) For Gmail and Google Calendar OAuth integration.

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/sujaynsv/Agentic-Skills.git
cd Agentic-Skills
```

### 2. Configure MCP Settings
The environment requires a globally synced `.mcp.json` file. We have provided a secure template.
```bash
# Copy the example file to your active config
cp .mcp.example.json .mcp.json
```
Open `.mcp.json` and replace the placeholder keys (`YOUR_TAVILY_API_KEY_HERE`, etc.) with your actual credentials.

### 3. Setup Custom Food MCP
Our custom Swiggy/Zomato integration requires local Node.js dependencies.
```bash
cd skills/custom-mcps/food-mcp
npm install
```

### 4. Sync Global Configuration
For Antigravity to recognize the custom skills and MCPs, you must link the `.mcp.json` to the global Gemini config directory.
```bash
ln -sf $(pwd)/.mcp.json ~/.gemini/config/mcp.json
```
*Note: Restart your Antigravity IDE after syncing.*

## Architecture

### Directory Structure
```
├── .mcp.example.json            # Safe, template MCP configuration
├── AGENTS.md                    # Core BMaD persona rules and spec-driven mandates
├── README.md                    # This documentation
└── skills/
    ├── custom/                  # Core Agent logic and behaviors
    │   ├── agent-analyst/       # Research and data gathering persona
    │   ├── agent-builder/       # Code generation and file manipulation persona
    │   ├── agent-concierge/     # Life management, food ordering, scheduling persona
    │   ├── agent-ops/           # Debugging, logging, and metrics persona
    │   ├── bmad-orchestrator/   # Routing logic for slash commands
    │   ├── mcp-guide/           # Internal instructions for using MCP tools
    │   ├── slash-commands/      # Definitions for /spec, /order, /daily, etc.
    │   └── spec-driven-dev/     # Enforcement of PRD and Tech Spec workflows
    └── custom-mcps/
        └── food-mcp/            # Custom Node.js MCP Server for Swiggy/Zomato
            ├── index.js         # Main server logic and tool definitions
            ├── package.json     # Node dependencies
            └── .gitignore
```

### Available Slash Commands

- `/spec` : Triggers the Orchestrator to begin Spec-Driven Development.
- `/plan` : Breaks down a spec into actionable tasks.
- `/review` : Strict code review against a pre-approved spec.
- `/order` : Starts the Swiggy/Zomato food ordering flow via the Concierge.
- `/research` : Deep web search and paper analysis (Analyst).
- `/ops` : Live metrics, logging, and debugging.
- `/daily` : Morning briefing (Calendar, Gmail, Weather).
- `/movie` : Movie lookup and recommendations.

### 🌟 Advanced Autonomous God-Mode Commands

We have added 4 high-autonomy "God-Mode" skills designed to make developers invincible during hackathons or deep work:

- `/ship [feature]` : The **Software Factory**. Spawns a 4-stage pipeline (Planner ➡️ Coder ➡️ Tester ➡️ Reviewer). Passes state strictly via a `.pipeline/` folder and refuses to stop until the Reviewer gives a verdict.
- `/fix-build [test command]` : The **Self-Healing Build**. Provide a test command (e.g. `/fix-build npm run test`). The agent runs it, debugs the stack trace, patches the code, and loops infinitely until the build is green.
- `/hunt [issue link]` : The **Bounty Hunter**. Point it at a GitHub issue. It forks the repo, reads the code, writes the feature, adds tests, and autonomously submits a Pull Request.
- `/ghostwrite` : The **Codebase Ghostwriter**. Drop it in a messy codebase. It explores all files, generates Mermaid architecture diagrams, and writes a pristine documentation suite in a new `docs/` folder.
- `/sentinel` : The **Background Sentinel**. Use `/schedule` to run this in the background. It periodically reads your uncommitted `git diff` and drops chat alerts *only* if it detects security flaws, memory leaks, or bad practices.

### Request Lifecycle (Example: `/order`)
1. User types `/order Find me some biryani` in the Antigravity chat.
2. The `bmad-orchestrator` detects the slash command and routes the request to the `agent-concierge` persona.
3. The Concierge parses the intent and identifies that it needs external data.
4. The Concierge calls the `search_swiggy` tool exposed by the local `food-mcp` server over `stdio`.
5. The `food-mcp` (using Node.js and Puppeteer) processes the request and returns structured restaurant data.
6. The Concierge synthesizes the data and presents options to the user.

## Environment Variables

### Required
| Variable | Description |
|---|---|
| `TAVILY_API_KEY` | Required for web search capabilities. |
| `EXA_API_KEY` | Required for deep code/semantic web search. |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Required for repo management and PR creation. |

### Optional
| Variable | Description |
|---|---|
| `BRAVE_API_KEY` | Alternative web search engine. |
| `PROMETHEUS_URL` | Metrics dashboard (defaults to `http://localhost:9090`). |

## Testing Custom Integrations

Since the `food-mcp` supports dynamic location injection, you can test it directly in the IDE by simulating a mobile GPS payload:

```text
/order Find me some biryani on Swiggy. My current GPS coordinates are Latitude: 17.50, Longitude: 78.46
```

The Concierge agent will extract the coordinates, feed them into the `food-mcp`, and return geographically accurate restaurant results.
