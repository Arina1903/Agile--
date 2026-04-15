"""
Модель Монте-Карло из веб-прототипа monte_carlo_agile.html (simScrum / simKanban).
Стохастические метрики по итерациям для сравнения Scrum и Kanban.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _randn(rng: np.random.Generator, size: int | tuple[int, ...] | None = None) -> np.ndarray:
    return rng.standard_normal(size)


def _rand_ln(rng: np.random.Generator, mu: float, sigma: float, size: int) -> np.ndarray:
    return np.exp(mu + sigma * rng.standard_normal(size))


def _rand_poisson(rng: np.random.Generator, lam: float, size: int) -> np.ndarray:
    """Эквивалент цикла Кнута из JS для каждого элемента (векторизовано через numpy)."""
    return rng.poisson(lam, size=size)


def _clamp(arr: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return np.clip(arr, lo, hi)


@dataclass
class ScrumMonteCarloResult:
    throughput: np.ndarray  # задач/итерацию
    cycle_time: np.ndarray  # дни
    lead_time: np.ndarray
    sprint_completion_rate: np.ndarray  # cr
    project_completion_days: np.ndarray
    defects: np.ndarray


@dataclass
class KanbanMonteCarloResult:
    throughput: np.ndarray
    cycle_time: np.ndarray
    lead_time: np.ndarray
    wip_compliance: np.ndarray  # wc
    project_completion_days: np.ndarray
    defects: np.ndarray


@dataclass
class HtmlModelParams:
    """Параметры как в getP() HTML: dur, team, sig, spd, vel, ovh, wip, cyc, flow, iters."""

    project_duration_iters: int  # dur
    team: int
    uncertainty_sigma: float  # sig 0..0.7
    sprint_days: float  # spd
    base_velocity: float  # vel story points
    scrum_overhead: float  # ovh 0..1
    wip_limit: int
    base_cycle_days: float  # cyc (3.5)
    flow_tasks_per_day: float  # flow (2.2)
    monte_carlo_iters: int


def simulate_scrum_html(p: HtmlModelParams, rng: np.random.Generator) -> ScrumMonteCarloResult:
    iters = p.monte_carlo_iters
    dur = p.project_duration_iters
    tp = np.zeros(iters)
    ct = np.zeros(iters)
    lt = np.zeros(iters)
    cr = np.zeros(iters)
    td = np.zeros(iters)
    defects = np.zeros(iters)

    for i in range(iters):
        tot_t = 0.0
        tot_c = 0.0
        tot_cr = 0.0
        for _ in range(dur):
            vel = _clamp(
                _rand_ln(rng, np.log(p.base_velocity), p.uncertainty_sigma, 1),
                p.base_velocity * 0.3,
                p.base_velocity * 2.2,
            )[0]
            ovh = _clamp(
                p.scrum_overhead * (1.0 + 0.3 * _randn(rng, 1)),
                0.0,
                1.0,
            )[0]
            tasks = max(1, int(np.round(vel / 5.0 * (1.0 - ovh))))
            planned = int(np.round(p.base_velocity / 5.0 * (1.0 + 0.1 * _randn(rng, 1))[0]))
            planned = max(1, planned)
            tot_cr += min(tasks, planned) / planned
            for _t in range(tasks):
                tot_c += _clamp(
                    _rand_ln(rng, np.log(p.sprint_days * 0.35), p.uncertainty_sigma * 0.8, 1),
                    0.5,
                    p.sprint_days,
                )[0]
            tot_t += tasks
        ac = tot_c / max(1.0, tot_t)
        tp[i] = tot_t / dur
        ct[i] = ac
        lt[i] = ac + p.sprint_days * (0.5 + 0.3 * np.abs(_randn(rng, 1))[0])
        cr[i] = tot_cr / dur
        td[i] = dur * p.sprint_days * (1.0 + p.uncertainty_sigma * 0.3 * np.abs(_randn(rng, 1))[0])
        defects[i] = _clamp(
            0.08 + p.uncertainty_sigma * 0.2 + 0.02 * _randn(rng, 1),
            0.02,
            0.35,
        )[0]

    return ScrumMonteCarloResult(
        throughput=tp,
        cycle_time=ct,
        lead_time=lt,
        sprint_completion_rate=cr,
        project_completion_days=td,
        defects=defects,
    )


def simulate_kanban_html(p: HtmlModelParams, rng: np.random.Generator) -> KanbanMonteCarloResult:
    iters = p.monte_carlo_iters
    dur = p.project_duration_iters
    tp = np.zeros(iters)
    ct = np.zeros(iters)
    lt = np.zeros(iters)
    wc = np.zeros(iters)
    td = np.zeros(iters)
    defects = np.zeros(iters)

    for i in range(iters):
        tot_t = 0.0
        tot_c = 0.0
        tot_wv = 0.0
        for _ in range(dur):
            arr = _rand_poisson(rng, p.flow_tasks_per_day * p.sprint_days, 1)[0]
            in_sys = _clamp(
                np.array([float(arr)], dtype=float),
                0.0,
                float(p.wip_limit * 3),
            )[0]
            wv = max(0.0, in_sys - p.wip_limit) / max(1.0, in_sys)
            tot_wv += wv
            e_wip = min(in_sys, p.wip_limit + np.abs(_randn(rng, 1))[0])
            tasks = int(np.round(e_wip * 2.0))
            cyc = max(0.5, p.base_cycle_days)
            for _t in range(tasks):
                tot_c += _clamp(
                    _rand_ln(rng, np.log(cyc), p.uncertainty_sigma * 0.9, 1),
                    0.3,
                    15.0,
                )[0]
            tot_t += tasks
        ac = tot_c / max(1.0, tot_t)
        tp[i] = tot_t / dur
        ct[i] = ac
        lt[i] = ac * (1.4 + 0.3 * np.abs(_randn(rng, 1))[0])
        wc[i] = 1.0 - tot_wv / dur
        td[i] = dur * p.sprint_days * (1.0 + p.uncertainty_sigma * 0.2 * np.abs(_randn(rng, 1))[0])
        defects[i] = _clamp(
            0.06 + p.uncertainty_sigma * 0.15 + 0.02 * _randn(rng, 1),
            0.01,
            0.30,
        )[0]

    return KanbanMonteCarloResult(
        throughput=tp,
        cycle_time=ct,
        lead_time=lt,
        wip_compliance=wc,
        project_completion_days=td,
        defects=defects,
    )


def predictability_inverse_cov(x: np.ndarray) -> float:
    """Как в HTML: 1 / (std/mean + 0.01)."""
    m = float(np.mean(x))
    s = float(np.std(x, ddof=0))
    return 1.0 / (s / m + 0.01)
