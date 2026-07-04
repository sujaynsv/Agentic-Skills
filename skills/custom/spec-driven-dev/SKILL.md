---
name: spec-driven-dev
description: Workflow for spec-driven development. ALWAYS run this before writing any code.
---

# Spec-Driven Development (SDD)

You are enforcing the SDD methodology. Do not write code until this process is complete.

## Workflow
1. **Gather Requirements**: Ask the user what they want to build.
2. **Write PRD**: Create a `product-requirements.md` file. It should contain:
   - Problem statement
   - Target audience
   - Key features
   - Non-goals
3. **Write Tech Spec**: Create a `technical-spec.md` file. It should contain:
   - Architecture
   - Data models
   - API endpoints
   - MCP tools required
4. **Request Approval**: Explicitly ask the user: "Spec approved? Proceed to implement?"
5. **Implementation**: Only upon approval, delegate to the `builder` persona to write code.
