## Behavioral Rules (Always Active)
- Always check which MCP is relevant before answering questions about external data.
- Prefer tool calls over hallucination — if an MCP can answer it, use it.
- Never implement code without a confirmed plan (see spec-driven rule below).
- Use `memory` MCP to store key decisions across sessions.

## Spec-Driven Development (MANDATORY for any project)
Before writing code for any feature, bug, or project:
1. Write a PRD (product-requirements.md) describing WHAT and WHY.
2. Write a technical-spec.md describing HOW (architecture, data models, APIs).
3. Get explicit user confirmation: "Spec approved? Proceed to implement?"
4. Only then write code — following the spec exactly.
5. Flag any spec deviation immediately rather than silently diverging.

This rule applies to ALL projects opened in Antigravity, not just this repo.

## Available Agent Personas
- **analyst**: Research mode — use arxiv, brave, tavily, exa, fetch.
- **builder**: Build mode — use filesystem, github, context7, excalidraw.
- **ops**: Ops mode — use prometheus, docker, sentry, sequential-thinking.
- **concierge**: Life mode — use swiggy-food, zomato, weather, google-calendar, gmail.

## MCP Quick-Reference
- `brave-search`, `tavily`, `exa-search`: Web search
- `fetch`: Fetch raw URL content
- `arxiv`: Fetch academic papers
- `github`: Manage GitHub issues, PRs
- `postgres`, `sqlite`, `redis`: Query databases and caches
- `puppeteer`, `playwright`, `firecrawl`: Browser automation and web scraping
- `notion`, `linear`: Note-taking, task management
- `google-calendar`, `gmail`: Email and calendar
- `swiggy-food`, `swiggy-instamart`, `zomato`: Food ordering and grocery
- `prometheus`, `sentry`, `docker`: Ops monitoring
- `memory`, `sequential-thinking`: Agent logic and long-term memory
