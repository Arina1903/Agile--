"""Упрощённая имитация Scrum: спринты фиксированной длины, FIFO-бэклог, перенос остатка."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass
class ScrumResult:
    completion_days: np.ndarray  # индекс дня завершения (0-based); nan — не завершено


def simulate_scrum(
    task_effort_dev_days: np.ndarray,
    team_size: int,
    sprint_days: int,
    total_days: int,
    overhead_fraction: float,
    rng: np.random.Generator,
) -> ScrumResult:
    del rng  # резерв под случайный порядок / переговоры в спринте
    n = len(task_effort_dev_days)
    backlog = deque((i, float(task_effort_dev_days[i])) for i in range(n))
    completion = np.full(n, np.nan)
    t = 0
    while t < total_days and backlog:
        sprint_end = min(t + sprint_days, total_days)
        capacity_dev_days = team_size * (sprint_end - t) * (1.0 - overhead_fraction)
        while backlog and capacity_dev_days > 0:
            tid, rem = backlog[0]
            if rem <= capacity_dev_days + 1e-12:
                capacity_dev_days -= rem
                backlog.popleft()
                completion[tid] = float(sprint_end - 1)
            else:
                backlog[0] = (tid, rem - capacity_dev_days)
                capacity_dev_days = 0
        t = sprint_end
    return ScrumResult(completion_days=completion)
