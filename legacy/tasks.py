"""Генерация набора задач для прогона симуляции."""

from __future__ import annotations

import numpy as np


def generate_task_efforts(
    n_tasks: int,
    mean_log: float,
    sigma_log: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Трудоёмкость задач в человеко-часах (положительные значения)."""
    raw = rng.lognormal(mean_log, sigma_log, size=n_tasks)
    return np.clip(raw, 0.25, None)


def hours_to_dev_days(effort_hours: np.ndarray, hours_per_dev_day: float) -> np.ndarray:
    return effort_hours / hours_per_dev_day
