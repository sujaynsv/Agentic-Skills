"""
Skills API Gateway
Exposes the Agentic-Skills repo's skill inventory and scorecard endpoint
as a lightweight REST API.
"""

import json
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiohttp

from scorecard_engine import run_scorecard

SKILLS_ROOT = Path(os.getenv("SKILLS_ROOT", "/app/skills"))
SKILLS_INDEX = Path(os.getenv("SKILLS_INDEX", "/app/skills_index.json"))
AV_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
if not AV_KEY:
    raise ValueError("ALPHAVANTAGE_API_KEY environment variable is not set.")

app = FastAPI(
    title="Agentic-Skills API",
    description="REST gateway for the Agentic-Skills repo — list skills, fetch SKILL.md content, run scorecards.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "skills-api"}


@app.get("/skills")
async def list_skills():
    """Return all skills registered in skills_index.json."""
    if not SKILLS_INDEX.exists():
        raise HTTPException(status_code=503, detail="skills_index.json not found")
    with open(SKILLS_INDEX) as f:
        index = json.load(f)
    return {"count": len(index), "skills": index}


@app.get("/skills/{skill_name}")
async def get_skill(skill_name: str):
    """Return the SKILL.md content for a named skill."""
    # Search recursively for the skill directory
    matches = list(SKILLS_ROOT.rglob(f"{skill_name}/SKILL.md"))
    if not matches:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
    content = matches[0].read_text()
    return {"name": skill_name, "path": str(matches[0]), "content": content}


class ScorecardRequest(BaseModel):
    ticker: str


@app.post("/scorecard")
async def scorecard_endpoint(req: ScorecardRequest):
    """Run the 1-min scorecard for a ticker and return structured data."""
    ticker = req.ticker.upper().strip()
    if not ticker:
        raise HTTPException(status_code=400, detail="ticker is required")
    try:
        result = await run_scorecard(ticker, AV_KEY)
        return {"ticker": ticker, "scorecard": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
