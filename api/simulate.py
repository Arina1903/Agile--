"""
Vercel Serverless Function: /api/simulate и /api/health
Точка входа для деплоя на Vercel (Python runtime).

Работает как WSGI-совместимый обработчик через Mangum или как
прямой http.server (Vercel поддерживает BaseHTTPRequestHandler).
Используем FastAPI + Mangum для максимальной совместимости.
"""
from __future__ import annotations

import json
import sys
import os

# Добавляем корень проекта в sys.path, чтобы импортировать monte_carlo и co.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from mangum import Mangum
    _HAS_MANGUM = True
except ImportError:
    _HAS_MANGUM = False

# ---------- inline simulation (без импорта всего проекта) ----------

def _randn(rng: np.random.Generator, n: int) -> np.ndarray:
    return rng.standard_normal(n)

def _simulate_scrum(p: dict, rng: np.random.Generator) -> dict:
    N = int(p['iters'])
    dur = int(p['dur'])
    vel = float(p['vel'])
    ovh = float(p['ovh'])
    sig = float(p['sig'])
    spd = float(p['spd'])

    eff = vel * (1 - ovh)
    noise = np.exp(sig * rng.standard_normal((N, dur)) - 0.5 * sig**2)
    tasks_per_iter = eff * noise / 5.0   # ~story points → tasks

    throughput = tasks_per_iter.mean(axis=1)
    cycle_arr   = spd / (tasks_per_iter + 1e-9)
    cycle_time  = cycle_arr.mean(axis=1)
    lead_time   = cycle_time + spd * 0.5   # очередь ≈ полспринта
    completion  = dur * spd + rng.standard_normal(N) * spd * sig
    scr         = (tasks_per_iter >= eff * 0.8).mean(axis=1)
    defects     = np.clip(0.05 + sig * 0.3 + rng.standard_normal(N) * 0.02, 0.01, 0.5)

    return dict(tp=throughput.tolist(), ct=cycle_time.tolist(), lt=lead_time.tolist(),
                cr=scr.tolist(), td=completion.tolist(), def_=defects.tolist())


def _simulate_kanban(p: dict, rng: np.random.Generator) -> dict:
    N = int(p['iters'])
    dur = int(p['dur'])
    wip = int(p['wip'])
    cyc = float(p['cyc'])
    flow = float(p['flow'])
    sig = float(p['sig'])
    spd = float(p['spd'])

    noise = np.exp(sig * rng.standard_normal((N, dur)) - 0.5 * sig**2)
    cycle_time  = (cyc * noise).mean(axis=1)
    throughput  = wip / (cycle_time + 1e-9) * spd
    lead_time   = cycle_time + 1.0 / (flow + 1e-9)
    completion  = dur * spd * (cycle_time / cyc) + rng.standard_normal(N) * sig * spd
    wip_noise   = rng.standard_normal((N, dur))
    wc          = (flow * spd <= wip + wip_noise * sig).mean(axis=1)
    defects     = np.clip(0.03 + sig * 0.2 + rng.standard_normal(N) * 0.015, 0.01, 0.45)

    return dict(tp=throughput.tolist(), ct=cycle_time.tolist(), lt=lead_time.tolist(),
                wc=wc.tolist(), td=completion.tolist(), def_=defects.tolist())


# ---------- FastAPI app ----------

app = FastAPI(title="Monte Carlo Agile — Scrum vs Kanban", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


class SimulateRequest(BaseModel):
    dur:   int   = Field(..., ge=6,   le=24)
    team:  int   = Field(..., ge=3,   le=12)
    sig:   float = Field(..., ge=0.1, le=0.7)
    spd:   float = Field(..., ge=7,   le=31)
    vel:   float = Field(..., ge=1,   le=160)
    ovh:   float = Field(..., ge=0.01, le=1.0)
    wip:   int   = Field(..., ge=1,   le=10)
    cyc:   float = Field(..., ge=1.0, le=8.0)
    flow:  float = Field(..., ge=0.5, le=5.0)
    iters: int   = Field(..., ge=500, le=10_000)
    seed:  int | None = None


@app.get("/api/health")
async def health():
    return {"status": "ok", "runtime": "vercel-serverless"}


@app.post("/api/simulate")
async def simulate(body: SimulateRequest):
    seed = body.seed if body.seed is not None else 42
    p = body.model_dump()

    # Пробуем использовать полноценную Python-модель, если доступна
    try:
        from monte_carlo import export_for_web, params_from_frontend, run_monte_carlo
        params = params_from_frontend(
            dur=p['dur'], team=p['team'], sig=p['sig'], spd=p['spd'],
            vel=p['vel'], ovh=p['ovh'], wip=p['wip'], cyc=p['cyc'],
            flow=p['flow'], iters=p['iters']
        )
        _, scrum, kanban = run_monte_carlo(seed=seed, params=params)
        return export_for_web(params, scrum, kanban)
    except Exception:
        pass

    # Fallback: встроенная лёгкая симуляция
    try:
        rng_s = np.random.default_rng(seed)
        rng_k = np.random.default_rng(seed + 1_000_000)
        s = _simulate_scrum(p, rng_s)
        k = _simulate_kanban(p, rng_k)
        return {
            "params": p,
            "scrum":  {"tp": s['tp'], "ct": s['ct'], "lt": s['lt'],
                       "cr": s['cr'], "td": s['td'], "def": s['def_']},
            "kanban": {"tp": k['tp'], "ct": k['ct'], "lt": k['lt'],
                       "wc": k['wc'], "td": k['td'], "def": k['def_']},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Vercel WSGI handler
if _HAS_MANGUM:
    handler = Mangum(app, lifespan="off")
else:
    # Fallback для локального запуска
    handler = app
