"""Запуск модели Монте-Карло из monte_carlo_agile.html и сводные таблицы."""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd

import config as cfg
from sim_html_agile import (
    HtmlModelParams,
    KanbanMonteCarloResult,
    ScrumMonteCarloResult,
    simulate_kanban_html,
    simulate_scrum_html,
)


def params_from_config() -> HtmlModelParams:
    return HtmlModelParams(
        project_duration_iters=cfg.PROJECT_DURATION_ITERATIONS,
        team=cfg.TEAM_SIZE,
        uncertainty_sigma=cfg.UNCERTAINTY_SIGMA,
        sprint_days=float(cfg.SPRINT_LENGTH_DAYS),
        base_velocity=float(cfg.BASE_VELOCITY_STORY_POINTS),
        scrum_overhead=cfg.SCRUM_OVERHEAD_FRACTION,
        wip_limit=int(cfg.KANBAN_WIP_LIMIT),
        base_cycle_days=float(cfg.KANBAN_BASE_CYCLE_DAYS),
        flow_tasks_per_day=float(cfg.FLOW_TASKS_PER_DAY),
        monte_carlo_iters=cfg.N_MONTE_CARLO_RUNS,
    )


def params_from_frontend(
    dur: int,
    team: int,
    sig: float,
    spd: float,
    vel: float,
    ovh: float,
    wip: int,
    cyc: float,
    flow: float,
    iters: int,
) -> HtmlModelParams:
    """Параметры из тела запроса веб-приложения (те же поля, что getP() в HTML)."""
    return HtmlModelParams(
        project_duration_iters=int(dur),
        team=int(team),
        uncertainty_sigma=float(sig),
        sprint_days=float(spd),
        base_velocity=float(vel),
        scrum_overhead=float(ovh),
        wip_limit=int(wip),
        base_cycle_days=float(cyc),
        flow_tasks_per_day=float(flow),
        monte_carlo_iters=int(iters),
    )


def run_monte_carlo(
    seed: int = cfg.RANDOM_SEED,
    params: HtmlModelParams | None = None,
) -> tuple[HtmlModelParams, ScrumMonteCarloResult, KanbanMonteCarloResult]:
    p = params or params_from_config()
    rng_s = np.random.default_rng(seed)
    rng_k = np.random.default_rng(seed + 1_000_000)
    scrum = simulate_scrum_html(p, rng_s)
    kanban = simulate_kanban_html(p, rng_k)
    return p, scrum, kanban


def results_to_dataframes(
    scrum: ScrumMonteCarloResult,
    kanban: KanbanMonteCarloResult,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_s = pd.DataFrame(
        {
            "throughput": scrum.throughput,
            "cycle_time": scrum.cycle_time,
            "lead_time": scrum.lead_time,
            "sprint_completion_rate": scrum.sprint_completion_rate,
            "project_completion_days": scrum.project_completion_days,
            "defects": scrum.defects,
        }
    )
    df_k = pd.DataFrame(
        {
            "throughput": kanban.throughput,
            "cycle_time": kanban.cycle_time,
            "lead_time": kanban.lead_time,
            "wip_compliance": kanban.wip_compliance,
            "project_completion_days": kanban.project_completion_days,
            "defects": kanban.defects,
        }
    )
    return df_s, df_k


def metrics_summary_table(
    scrum: ScrumMonteCarloResult,
    kanban: KanbanMonteCarloResult,
) -> pd.DataFrame:
    """Сводная таблица как «Приложение Б» в HTML (μ, σ, P10–P90)."""
    from stats_helpers import mean_std, percentile

    rows: list[dict[str, Any]] = []
    specs: list[tuple[str, np.ndarray, np.ndarray, bool, bool]] = [
        ("Цикловое время (дни)", scrum.cycle_time, kanban.cycle_time, True, False),
        ("Lead Time (дни)", scrum.lead_time, kanban.lead_time, True, False),
        ("Пропускная способность (задач/ит.)", scrum.throughput, kanban.throughput, False, False),
        (
            "Время завершения проекта (дни)",
            scrum.project_completion_days,
            kanban.project_completion_days,
            True,
            False,
        ),
        ("Уровень дефектов", scrum.defects, kanban.defects, True, True),
        (
            "Завершение спринта / WIP-соблюд.",
            scrum.sprint_completion_rate,
            kanban.wip_compliance,
            False,
            True,
        ),
    ]
    for name, a, b, lower_is_better, as_percent in specs:
        ma, sa = mean_std(a)
        mb, sb = mean_std(b)
        p10a, p90a = percentile(a, 10), percentile(a, 90)
        p10b, p90b = percentile(b, 10), percentile(b, 90)

        def fmt_val(x: float) -> str:
            return f"{x * 100:.1f}%" if as_percent else f"{x:.2f}"

        diff_pct = ((mb - ma) / ma * 100) if abs(ma) > 1e-12 else 0.0
        better = "≈"
        if abs(diff_pct) >= 2.0:
            if lower_is_better:
                better = "Kanban" if mb < ma else "Scrum"
            else:
                better = "Kanban" if mb > ma else "Scrum"
        rows.append(
            {
                "metric": name,
                "scrum_mean": ma,
                "scrum_std": sa,
                "scrum_p10_p90": f"{fmt_val(p10a)}–{fmt_val(p90a)}",
                "kanban_mean": mb,
                "kanban_std": sb,
                "kanban_p10_p90": f"{fmt_val(p10b)}–{fmt_val(p90b)}",
                "delta_pct_k_minus_s": diff_pct,
                "winner": better,
            }
        )
    return pd.DataFrame(rows)


def significance_table(scrum: ScrumMonteCarloResult, kanban: KanbanMonteCarloResult) -> pd.DataFrame:
    from stats_helpers import cohens_d, effect_size_label, welch_ttest_pvalue

    rows = []
    for name, a, b in [
        ("Цикловое время", scrum.cycle_time, kanban.cycle_time),
        ("Lead Time", scrum.lead_time, kanban.lead_time),
        ("Пропускная способность", scrum.throughput, kanban.throughput),
        ("Дефекты", scrum.defects, kanban.defects),
    ]:
        pval = welch_ttest_pvalue(a, b)
        d = cohens_d(a, b)
        rows.append(
            {
                "metric": name,
                "p_value": float(pval),
                "significant_alpha_05": bool(pval < 0.05),
                "cohens_d": float(d),
                "effect": effect_size_label(d),
            }
        )
    return pd.DataFrame(rows)


def export_for_web(
    p: HtmlModelParams,
    scrum: ScrumMonteCarloResult,
    kanban: KanbanMonteCarloResult,
) -> dict[str, Any]:
    """Структура для встраивания в monte_carlo_agile.html (window.__PY_SIM__)."""

    def params_js() -> dict[str, Any]:
        return {
            "dur": p.project_duration_iters,
            "team": p.team,
            "sig": p.uncertainty_sigma,
            "spd": p.sprint_days,
            "vel": p.base_velocity,
            "ovh": p.scrum_overhead,
            "wip": p.wip_limit,
            "cyc": p.base_cycle_days,
            "flow": p.flow_tasks_per_day,
            "iters": p.monte_carlo_iters,
        }

    return {
        "params": params_js(),
        "scrum": {
            "tp": scrum.throughput.tolist(),
            "ct": scrum.cycle_time.tolist(),
            "lt": scrum.lead_time.tolist(),
            "cr": scrum.sprint_completion_rate.tolist(),
            "td": scrum.project_completion_days.tolist(),
            "def": scrum.defects.tolist(),
        },
        "kanban": {
            "tp": kanban.throughput.tolist(),
            "ct": kanban.cycle_time.tolist(),
            "lt": kanban.lead_time.tolist(),
            "wc": kanban.wip_compliance.tolist(),
            "td": kanban.project_completion_days.tolist(),
            "def": kanban.defects.tolist(),
        },
    }


def write_json_export(path: str, payload: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
