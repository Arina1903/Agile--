"""Графики в стилистике monte_carlo_agile.html (Chart.js → matplotlib)."""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

from sim_html_agile import KanbanMonteCarloResult, ScrumMonteCarloResult, predictability_inverse_cov
from stats_helpers import mean_std, percentile

SC = "#00d4ff"
KC = "#ff6b35"
SD = (0, 212 / 255, 1, 0.13)
KD = (255 / 255, 107 / 255, 53 / 255, 0.13)
BG = "#09090f"
FG = "#e8e8f0"
MUTED = "#6b6b8a"


def _setup_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": "#16161f",
            "axes.edgecolor": "#252535",
            "axes.labelcolor": FG,
            "text.color": FG,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "grid.color": "#252535",
            "grid.alpha": 0.8,
        }
    )


def _pct(a: np.ndarray, p: float) -> float:
    return float(np.percentile(a, p))


def plot_bar_compare_stats(
    s_arr: np.ndarray,
    k_arr: np.ndarray,
    y_label: str,
    out_path: str,
    title: str,
) -> None:
    _setup_style()
    labs = ["P10", "P25", "Медиана", "Среднее", "P75", "P90"]
    sv = [
        _pct(s_arr, 10),
        _pct(s_arr, 25),
        _pct(s_arr, 50),
        float(np.mean(s_arr)),
        _pct(s_arr, 75),
        _pct(s_arr, 90),
    ]
    kv = [
        _pct(k_arr, 10),
        _pct(k_arr, 25),
        _pct(k_arr, 50),
        float(np.mean(k_arr)),
        _pct(k_arr, 75),
        _pct(k_arr, 90),
    ]
    x = np.arange(len(labs))
    w = 0.38
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x - w / 2, sv, width=w, label="Scrum", color=SC, alpha=0.75, edgecolor=SC)
    ax.bar(x + w / 2, kv, width=w, label="Kanban", color=KC, alpha=0.75, edgecolor=KC)
    ax.set_xticks(x)
    ax.set_xticklabels(labs)
    ax.set_ylabel(y_label, color=MUTED)
    ax.set_title(title, color=FG, fontsize=11)
    ax.legend(facecolor="#111118", edgecolor="#252535", labelcolor=FG)
    ax.grid(True, axis="y", alpha=0.4)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, facecolor=BG)
    plt.close()


def plot_distribution_line(
    s_arr: np.ndarray,
    k_arr: np.ndarray,
    bins: int,
    xlabel: str,
    out_path: str,
    title: str,
) -> None:
    _setup_style()
    allv = np.concatenate([s_arr, k_arr])
    mn = _pct(allv, 2)
    mx = _pct(allv, 98)
    step = (mx - mn) / bins if mx > mn else 1.0
    edges = mn + np.arange(bins) * step
    centers = edges + step / 2

    def hist_norm(d: np.ndarray) -> np.ndarray:
        c = np.zeros(bins)
        for v in d:
            b = int(np.clip(np.floor((v - mn) / step), 0, bins - 1))
            c[b] += 1
        return c / max(len(d), 1) * 100.0

    hs, hk = hist_norm(s_arr), hist_norm(k_arr)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.fill_between(centers, hs, alpha=0.35, color=SC, label="Scrum")
    ax.plot(centers, hs, color=SC, linewidth=1.5)
    ax.fill_between(centers, hk, alpha=0.35, color=KC, label="Kanban")
    ax.plot(centers, hk, color=KC, linewidth=1.5)
    ax.set_xlabel(xlabel, color=MUTED)
    ax.set_ylabel("Частота (%)", color=MUTED)
    ax.set_title(title, color=FG, fontsize=11)
    ax.legend(facecolor="#111118", edgecolor="#252535", labelcolor=FG)
    ax.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, facecolor=BG)
    plt.close()


def plot_percentile_profile(
    s_arr: np.ndarray,
    k_arr: np.ndarray,
    out_path: str,
) -> None:
    _setup_style()
    labs = ["P5", "P25", "Медиана", "P75", "P95"]
    sv = [_pct(s_arr, 5), _pct(s_arr, 25), _pct(s_arr, 50), _pct(s_arr, 75), _pct(s_arr, 95)]
    kv = [_pct(k_arr, 5), _pct(k_arr, 25), _pct(k_arr, 50), _pct(k_arr, 75), _pct(k_arr, 95)]
    x = np.arange(len(labs))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, sv, "o-", color=SC, label="Scrum", linewidth=2, markersize=6)
    ax.fill_between(x, sv, alpha=0.2, color=SC)
    ax.plot(x, kv, "o-", color=KC, label="Kanban", linewidth=2, markersize=6)
    ax.fill_between(x, kv, alpha=0.2, color=KC)
    ax.set_xticks(x)
    ax.set_xticklabels(labs)
    ax.set_ylabel("Часы (дни)", color=MUTED)
    ax.set_title("Перцентильный профиль — цикловое время", color=FG, fontsize=11)
    ax.legend(facecolor="#111118", edgecolor="#252535", labelcolor=FG)
    ax.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, facecolor=BG)
    plt.close()


def plot_completion_wip_bars(
    scrum_cr: np.ndarray,
    kanban_wc: np.ndarray,
    out_path: str,
) -> None:
    _setup_style()
    sm, ss = mean_std(scrum_cr)
    km, ks = mean_std(kanban_wc)
    labs = ["Среднее", "−1σ", "+1σ", "P10", "P90"]
    sv = [
        sm * 100,
        (sm - ss) * 100,
        (sm + ss) * 100,
        _pct(scrum_cr, 10) * 100,
        _pct(scrum_cr, 90) * 100,
    ]
    kv = [
        km * 100,
        (km - ks) * 100,
        (km + ks) * 100,
        _pct(kanban_wc, 10) * 100,
        _pct(kanban_wc, 90) * 100,
    ]
    sv = [float(np.clip(v, 0, 110)) for v in sv]
    kv = [float(np.clip(v, 0, 110)) for v in kv]
    x = np.arange(len(labs))
    w = 0.38
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x - w / 2, sv, width=w, label="Scrum: % завершения спринта", color=SC, alpha=0.75)
    ax.bar(x + w / 2, kv, width=w, label="Kanban: WIP-соблюд.", color=KC, alpha=0.75)
    ax.set_xticks(x)
    ax.set_xticklabels(labs)
    ax.set_ylabel("%", color=MUTED)
    ax.set_ylim(0, 110)
    ax.set_title("Завершение спринта / WIP-соблюдение", color=FG, fontsize=11)
    ax.legend(facecolor="#111118", edgecolor="#252535", labelcolor=FG, fontsize=8)
    ax.grid(True, axis="y", alpha=0.4)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, facecolor=BG)
    plt.close()


def _norm(v: float, lo: float, hi: float) -> float:
    return float(np.clip((v - lo) / (hi - lo + 1e-12), 0, 1))


def plot_radar(
    scrum: ScrumMonteCarloResult,
    kanban: KanbanMonteCarloResult,
    out_path: str,
) -> None:
    _setup_style()
    sm, km = np.mean(scrum.throughput), np.mean(kanban.throughput)
    sct, kct = np.mean(scrum.cycle_time), np.mean(kanban.cycle_time)
    slt, klt = np.mean(scrum.lead_time), np.mean(kanban.lead_time)
    sdf, kdf = np.mean(scrum.defects), np.mean(kanban.defects)
    scr, kwc = np.mean(scrum.sprint_completion_rate), np.mean(kanban.wip_compliance)
    sp = predictability_inverse_cov(scrum.throughput)
    kp = predictability_inverse_cov(kanban.throughput)
    mx_tp = max(sm, km) * 1.2
    mx_ct = max(sct, kct) * 1.2
    mx_lt = max(slt, klt) * 1.2
    mx_p = max(sp, kp) * 1.2

    labels = [
        "Пропускная\nспособность",
        "Цикловое время (↓)",
        "Lead Time (↓)",
        "Дефекты (↓)",
        "Спринт / WIP",
        "Предсказуемость",
    ]
    sv = [
        _norm(sm, 0, mx_tp) * 10,
        (1 - _norm(sct, 0, mx_ct)) * 10,
        (1 - _norm(slt, 0, mx_lt)) * 10,
        (1 - _norm(sdf, 0, 0.35)) * 10,
        _norm(scr, 0, 1) * 10,
        _norm(sp, 0, mx_p) * 10,
    ]
    kv = [
        _norm(km, 0, mx_tp) * 10,
        (1 - _norm(kct, 0, mx_ct)) * 10,
        (1 - _norm(klt, 0, mx_lt)) * 10,
        (1 - _norm(kdf, 0, 0.35)) * 10,
        _norm(kwc, 0, 1) * 10,
        _norm(kp, 0, mx_p) * 10,
    ]
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False) + np.pi / 2
    sv = np.array(sv + [sv[0]])
    kv = np.array(kv + [kv[0]])
    angles = np.concatenate([angles, [angles[0]]])

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection="polar"))
    ax.plot(angles, sv, "o-", color=SC, label="Scrum", linewidth=2)
    ax.fill(angles, sv, alpha=0.15, color=SC)
    ax.plot(angles, kv, "o-", color=KC, label="Kanban", linewidth=2)
    ax.fill(angles, kv, alpha=0.15, color=KC)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8, color=MUTED)
    ax.set_title("Интегральная оценка (радар)", color=FG, fontsize=11, pad=16)
    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.08), facecolor="#111118", labelcolor=FG)
    plt.subplots_adjust(top=0.88, left=0.12, right=0.88)
    plt.savefig(out_path, dpi=150, facecolor=BG)
    plt.close()


def plot_all_charts(
    scrum: ScrumMonteCarloResult,
    kanban: KanbanMonteCarloResult,
    out_dir: str,
    prefix: str = "mc",
) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    paths: list[str] = []
    for fn, s_arr, k_arr, ylab, ttl in [
        ("throughput", scrum.throughput, kanban.throughput, "Задач/итерацию", "Пропускная способность"),
        ("cycle", scrum.cycle_time, kanban.cycle_time, "Дней", "Цикловое время"),
        ("lead", scrum.lead_time, kanban.lead_time, "Дней", "Lead Time"),
        ("completion", scrum.project_completion_days, kanban.project_completion_days, "Дней", "Прогноз завершения проекта"),
    ]:
        p = os.path.join(out_dir, f"{prefix}_bar_{fn}.png")
        plot_bar_compare_stats(s_arr, k_arr, ylab, p, ttl)
        paths.append(p)
    p1 = os.path.join(out_dir, f"{prefix}_dist_cycle.png")
    plot_distribution_line(
        scrum.cycle_time,
        kanban.cycle_time,
        30,
        "Цикловое время (дни)",
        p1,
        "Распределение цикловых времён",
    )
    paths.append(p1)
    p2 = os.path.join(out_dir, f"{prefix}_dist_tp.png")
    plot_distribution_line(
        scrum.throughput,
        kanban.throughput,
        30,
        "Пропускная способность (зад/ит.)",
        p2,
        "Распределение пропускной способности",
    )
    paths.append(p2)
    p3 = os.path.join(out_dir, f"{prefix}_ci_cycle.png")
    plot_percentile_profile(scrum.cycle_time, kanban.cycle_time, p3)
    paths.append(p3)
    p4 = os.path.join(out_dir, f"{prefix}_completion_wip.png")
    plot_completion_wip_bars(scrum.sprint_completion_rate, kanban.wip_compliance, p4)
    paths.append(p4)
    p5 = os.path.join(out_dir, f"{prefix}_radar.png")
    plot_radar(scrum, kanban, p5)
    paths.append(p5)
    return paths
