"""
Загрузка обезличенной выгрузки задач для калибровки распределений.

Ожидаемые столбцы (любой из вариантов имён):
- оценка: 'Story Points', 'story_points', 'points'
- или длительность: 'time_spent_hours', 'timespent', 'Hours'

Если столбцов нет — вернёт None (используйте синтетику из config).
"""

from __future__ import annotations

import os
from typing import Optional

import numpy as np
import pandas as pd


def _pick_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    lower = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name.lower() in lower:
            return lower[name.lower()]
    for c in df.columns:
        cl = c.lower().replace(" ", "_")
        for name in candidates:
            if cl == name.lower().replace(" ", "_"):
                return c
    return None


def load_efforts_from_jira_csv(path: str) -> Optional[np.ndarray]:
    if not os.path.isfile(path):
        return None
    df = pd.read_csv(path)
    col = _pick_column(df, ["Story Points", "story_points", "points", "estimate"])
    if col is None:
        col = _pick_column(df, ["time_spent_hours", "timespent", "hours", "Time Spent"])
    if col is None:
        return None
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if s.empty:
        return None
    arr = s.to_numpy(dtype=float)
    return arr[arr > 0]


def summarize_distribution(values: np.ndarray) -> tuple[float, float]:
    """Подбор mean_log, sigma_log для lognormal по выборке (метод моментов на логарифме)."""
    v = np.log(np.clip(values, 1e-6, None))
    return float(np.mean(v)), float(np.std(v))
