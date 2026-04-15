"""Метрики эффективности и сопоставимости для сравнения методологий."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class MetricSummary:
    mean_lead_time: float
    median_lead_time: float
    p80_lead_time: float
    p90_lead_time: float
    throughput_per_day: float
    completed_fraction: float
    std_lead_time: float


def summarize_lead_times(
    completion_days: np.ndarray,
    horizon_days: float,
    arrival_day: float = 0.0,
) -> MetricSummary:
    done = np.isfinite(completion_days)
    if not np.any(done):
        return MetricSummary(
            mean_lead_time=float("nan"),
            median_lead_time=float("nan"),
            p80_lead_time=float("nan"),
            p90_lead_time=float("nan"),
            throughput_per_day=0.0,
            completed_fraction=0.0,
            std_lead_time=float("nan"),
        )
    lead = completion_days[done] - arrival_day
    lead = np.maximum(lead, 0.0)
    n_done = int(np.sum(done))
    return MetricSummary(
        mean_lead_time=float(np.mean(lead)),
        median_lead_time=float(np.median(lead)),
        p80_lead_time=float(np.percentile(lead, 80)),
        p90_lead_time=float(np.percentile(lead, 90)),
        throughput_per_day=n_done / max(horizon_days, 1e-9),
        completed_fraction=n_done / max(len(completion_days), 1),
        std_lead_time=float(np.std(lead)),
    )


def compare_variability(s1: MetricSummary, s2: MetricSummary) -> float | None:
    """Отношение стандартных отклонений (меньше — предсказуемее относительно другого)."""
    if not (np.isfinite(s1.std_lead_time) and np.isfinite(s2.std_lead_time)):
        return None
    if s2.std_lead_time < 1e-12:
        return None
    return s1.std_lead_time / s2.std_lead_time
