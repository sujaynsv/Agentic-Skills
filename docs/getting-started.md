# Getting Started with Agentic-Skills

This repository is designed to give your Google Antigravity IDE "God-Mode" autonomy. 

## Prerequisites
1. **Google Antigravity IDE**: Ensure you are using the latest version with Gemini 1.5 Pro or similar models configured.
2. **Git & GitHub CLI**: Required for the `/hunt` and `/ship` workflows.
3. **Puppeteer**: Required for the custom Swiggy/Zomato food MCP.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sujaynsv/Agentic-Skills.git
   cd Agentic-Skills
   ```

2. **Configure IDE Roots**:
   The IDE automatically discovers customizations in the `skills/` directory if this repository is mapped to your Workspace Customizations Root (`.agents/`) or if you edit the global config in `~/.gemini/config/`. 

3. **Install MCP Dependencies**:
   If you want to use the food delivery MCP, navigate to the MCP folder and install dependencies:
   ```bash
   cd skills/custom-mcps/food-mcp
   npm install
   ```

## Usage

Simply open the Antigravity chat in this repository (or any repository linked to these skills) and type a slash command.

**Example 1: Fixing a broken build**
```text
/fix-build npm run test
```

**Example 2: Shipping a feature autonomously**
```text
/ship Add rate limiting to the authentication endpoint
```

**Example 3: Generating documentation (like this one!)**
```text
/ghostwrite
```
