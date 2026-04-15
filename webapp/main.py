"""
Веб-приложение: FastAPI + статическая SPA (Chart.js).
Запуск из корня проекта: uvicorn webapp.main:app --reload --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from monte_carlo import export_for_web, params_from_frontend, run_monte_carlo
from .schemas import SimulateRequest

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Monte Carlo Agile — Scrum vs Kanban", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/simulate")
async def simulate(body: SimulateRequest) -> dict:
    p = params_from_frontend(
        dur=body.dur,
        team=body.team,
        sig=body.sig,
        spd=body.spd,
        vel=body.vel,
        ovh=body.ovh,
        wip=body.wip,
        cyc=body.cyc,
        flow=body.flow,
        iters=body.iters,
    )
    seed = body.seed if body.seed is not None else 42

    loop = asyncio.get_event_loop()

    def _run():
        return run_monte_carlo(seed=seed, params=p)

    try:
        _, scrum, kanban = await loop.run_in_executor(None, _run)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return export_for_web(p, scrum, kanban)


if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
