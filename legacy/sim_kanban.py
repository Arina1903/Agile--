"""Упрощённая имитация Kanban: лимит WIP, ежедневная подтяжка задач, FIFO в работе."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass
class KanbanResult:
    completion_days: np.ndarray


def simulate_kanban(
    task_effort_dev_days: np.ndarray,
    team_size: int,
    total_days: int,
    wip_limit: int,
    overhead_fraction: float,
    rng: np.random.Generator,
) -> KanbanResult:
    del rng
    n = len(task_effort_dev_days)
    backlog = deque((i, float(task_effort_dev_days[i])) for i in range(n))
    in_progress: list[list[float]] = []
    completion = np.full(n, np.nan)

    for day in range(total_days):
        while len(in_progress) < wip_limit and backlog:
            tid, rem = backlog.popleft()
            in_progress.append([float(tid), rem])

        capacity = team_size * (1.0 - overhead_fraction)
        while capacity > 0 and in_progress:
            tid, rem = in_progress[0][0], in_progress[0][1]
            if rem <= capacity + 1e-12:
                capacity -= rem
                in_progress.pop(0)
                completion[int(tid)] = float(day)
            else:
                in_progress[0][1] = rem - capacity
                capacity = 0

    return KanbanResult(completion_days=completion)
