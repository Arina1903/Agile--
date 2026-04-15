"""Описательная статистика, Welch t-test, Cohen's d."""

from __future__ import annotations

import numpy as np

try:
    from scipy import stats as scipy_stats

    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False


def mean_std(a: np.ndarray) -> tuple[float, float]:
    return float(np.mean(a)), float(np.std(a, ddof=0))


def percentile(a: np.ndarray, p: float) -> float:
    return float(np.percentile(a, p))


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    ma, mb = np.mean(a), np.mean(b)
    sa, sb = np.std(a, ddof=0), np.std(b, ddof=0)
    sp = np.sqrt((sa**2 + sb**2) / 2.0)
    return abs(ma - mb) / (sp + 1e-15)


def welch_ttest_pvalue(a: np.ndarray, b: np.ndarray) -> float:
    if _HAS_SCIPY:
        r = scipy_stats.ttest_ind(a, b, equal_var=False)
        return float(r.pvalue)
    # Аппроксимация без scipy (двусторонний t)
    ma, mb = np.mean(a), np.mean(b)
    sa, sb = np.std(a, ddof=1), np.std(b, ddof=1)
    na, nb = len(a), len(b)
    se = np.sqrt(sa**2 / na + sb**2 / nb)
    if se < 1e-15:
        return 1.0
    t = abs(ma - mb) / se
    # грубая двусторонняя оценка для больших n
    if t > 3.5:
        return 0.0005
    if t > 2.5:
        return 0.005
    if t > 1.96:
        return 0.04
    return 0.5


def effect_size_label(d: float) -> str:
    ad = abs(d)
    if ad < 0.2:
        return "малый"
    if ad < 0.5:
        return "средний"
    if ad < 0.8:
        return "большой"
    return "очень большой"
