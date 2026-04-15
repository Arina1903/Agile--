"""Текстовые выводы по логике вкладки «Рекомендации» в monte_carlo_agile.html."""

from __future__ import annotations

import numpy as np

from sim_html_agile import HtmlModelParams, KanbanMonteCarloResult, ScrumMonteCarloResult, predictability_inverse_cov


def build_recommendation_text(
    p: HtmlModelParams,
    scrum: ScrumMonteCarloResult,
    kanban: KanbanMonteCarloResult,
) -> str:
    sp = predictability_inverse_cov(scrum.throughput)
    kp = predictability_inverse_cov(kanban.throughput)
    m_s_ct = float(np.mean(scrum.cycle_time))
    m_k_ct = float(np.mean(kanban.cycle_time))
    m_s_tp = float(np.mean(scrum.throughput))
    m_k_tp = float(np.mean(kanban.throughput))

    sw = sum(
        [
            m_s_ct < m_k_ct,
            sp > kp,
            m_s_tp > m_k_tp,
        ]
    )
    kw = sum(
        [
            m_k_ct < m_s_ct,
            kp > sp,
            m_k_tp > m_s_tp,
        ]
    )
    if sw > kw:
        win = "Scrum"
    elif kw > sw:
        win = "Kanban"
    else:
        win = "Равнозначны (по упрощённым критериям)"

    lines: list[str] = []
    if p.uncertainty_sigma > 0.4:
        lines.append(
            f"При σ={p.uncertainty_sigma:.2f} (выше порога 0.35) Scrum испытывает больше давления "
            f"неопределённости; разумно рассмотреть Scrumban или сокращение спринта "
            f"до {max(7, int(p.sprint_days - 7))} дней."
        )
    else:
        lines.append(
            f"При σ={p.uncertainty_sigma:.2f} Scrum остаётся предсказуемым; среднее cycle time = {m_s_ct:.1f} дн.; "
            f"длина спринта {p.sprint_days:.0f} дней согласуется с параметрами модели."
        )

    if p.flow_tasks_per_day > 3:
        lines.append(
            f"Поток {p.flow_tasks_per_day:.1f} задач/день хорошо согласуется с Kanban; "
            f"рекомендуемый WIP около {round(p.team * 0.75)}."
        )
    else:
        lines.append(
            f"При потоке {p.flow_tasks_per_day:.1f} задач/день преимущества Kanban по модели слабее; "
            f"throughput Kanban = {m_k_tp:.1f} зад/ит."
        )

    if p.wip_limit > p.team:
        lines.append(f"Текущий WIP={p.wip_limit} выше размера команды ({p.team}); по закону Литтла имеет смысл снизить WIP.")
    else:
        lines.append(f"WIP={p.wip_limit} при команде {p.team} чел. выглядит в допустимом диапазоне (ориентир team×0.75–1.0).")

    lines.append("")
    lines.append(
        f"Итог симуляции ({p.monte_carlo_iters} прогонов): рекомендуется: {win}. "
        f"Scrum: cycle time {m_s_ct:.2f} дн., throughput {m_s_tp:.1f} зад/ит., предсказуемость {sp:.2f}. "
        f"Kanban: cycle time {m_k_ct:.2f} дн., throughput {m_k_tp:.1f} зад/ит., предсказуемость {kp:.2f}."
    )
    lines.append("")
    lines.append(
        "Выводы привязаны к упрощённой стохастической модели из веб-прототипа; в тексте ВКР укажите допущения и при необходимости калибровку по Jira."
    )

    return "\n".join(lines)
