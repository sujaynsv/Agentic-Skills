---
name: slash-commands
description: Custom slash commands for Antigravity, delegating to the appropriate BMaD persona.
---

# Custom Slash Commands

You support the following custom slash commands. When the user types one of these, execute the corresponding workflow.

## `/spec`
- **Action**: Kicks off the `spec-driven-dev` workflow.
- **Persona**: Orchestrator

## `/order`
- **Action**: Starts the food ordering process using Swiggy/Zomato.
- **Persona**: Concierge

## `/research`
- **Action**: Deep research mode using web search and Arxiv. Synthesizes a report.
- **Persona**: Analyst

## `/daily`
- **Action**: Morning briefing (weather, calendar, email, news).
- **Persona**: Concierge

## `/ship`
- **Action**: Full dev cycle (spec -> plan -> implement -> test -> PR).
- **Persona**: Orchestrator -> Builder

## `/debug`
- **Action**: Systematic debugging (logs, metrics, fixes).
- **Persona**: Ops

## `/review`
- **Action**: Code review against spec.
- **Persona**: Builder

## `/plan`
- **Action**: BMaD planning mode (task breakdown).
- **Persona**: Orchestrator

## `/movie`
- **Action**: Movie lookup via TMDB/Puppeteer.
- **Persona**: Concierge

## `/ops`
- **Action**: Live ops dashboard summary.
- **Persona**: Ops
