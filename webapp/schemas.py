"""Схемы API для веб-приложения."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SimulateRequest(BaseModel):
    dur: int = Field(..., ge=6, le=24, description="Длительность проекта (итераций)")
    team: int = Field(..., ge=3, le=12)
    sig: float = Field(..., ge=0.1, le=0.7, description="σ неопределённости")
    spd: float = Field(..., ge=7, le=31, description="Длина спринта, дней")
    vel: float = Field(..., ge=1, le=160, description="Базовая velocity (story points)")
    ovh: float = Field(..., ge=0.01, le=1.0, description="Накладные расходы церемоний, доля")
    wip: int = Field(..., ge=1, le=10)
    cyc: float = Field(..., ge=1.0, le=8.0, description="Базовый цикл задачи, дни")
    flow: float = Field(..., ge=0.5, le=5.0, description="Интенсивность потока, задач/день")
    iters: int = Field(..., ge=500, le=20_000, description="Число прогонов Монте-Карло")
    seed: int | None = Field(None, description="Seed RNG для воспроизводимости")
