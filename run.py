"""Запуск Монте-Карло (как monte_carlo_agile.html): таблицы, графики, JSON, HTML-отчёт."""

from __future__ import annotations

import json
import os
import sys

import pandas as pd

import config as cfg
from monte_carlo import (
    export_for_web,
    metrics_summary_table,
    results_to_dataframes,
    run_monte_carlo,
    significance_table,
    write_json_export,
)
from recommendations import build_recommendation_text
from visualize import plot_all_charts


def _inject_html_report(
    template_path: str,
    out_html_path: str,
    payload: dict,
) -> None:
    with open(template_path, encoding="utf-8") as f:
        html = f.read()
    data = json.dumps(payload, ensure_ascii=False)
    injection = (
        f"<script>window.__PY_SIM__={data};</script>\n"
        '<script>if(window.__PY_SIM__&&typeof applyPythonExport==="function")'
        "applyPythonExport(window.__PY_SIM__);</script>\n"
    )
    if "</body>" in html:
        html = html.replace("</body>", injection + "</body>", 1)
    else:
        html += injection
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(html)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except OSError:
            pass

    base = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base, "output")
    web_dir = os.path.join(base, "web")
    os.makedirs(out_dir, exist_ok=True)

    p, scrum, kanban = run_monte_carlo()
    df_s, df_k = results_to_dataframes(scrum, kanban)
    df_s.to_csv(os.path.join(out_dir, "monte_carlo_scrum.csv"), index=False)
    df_k.to_csv(os.path.join(out_dir, "monte_carlo_kanban.csv"), index=False)

    summary = metrics_summary_table(scrum, kanban)
    summary.to_csv(os.path.join(out_dir, "comparison_summary.csv"), index=False)

    sig = significance_table(scrum, kanban)
    sig.to_csv(os.path.join(out_dir, "significance_welch.csv"), index=False)

    plot_all_charts(scrum, kanban, out_dir)

    payload = export_for_web(p, scrum, kanban)
    json_path = os.path.join(out_dir, "simulation_data.json")
    write_json_export(json_path, payload)

    template = os.path.join(web_dir, "monte_carlo_agile.html")
    if os.path.isfile(template):
        _inject_html_report(
            template,
            os.path.join(out_dir, "monte_carlo_agile_report.html"),
            payload,
        )

    rec_path = os.path.join(out_dir, "recommendations_ru.txt")
    rec_text = build_recommendation_text(p, scrum, kanban)
    with open(rec_path, "w", encoding="utf-8") as f:
        f.write(rec_text)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 120)
    print("Параметры (config.py, как в HTML-прототипе):")
    print(
        f"  итераций проекта={p.project_duration_iters}, команда={p.team}, σ={p.uncertainty_sigma}, "
        f"спринт={p.sprint_days} дн., velocity={p.base_velocity}, WIP={p.wip_limit}, "
        f"поток={p.flow_tasks_per_day} зад/день, прогонов Монте-Карло={p.monte_carlo_iters}"
    )
    print("\nСводная таблица метрик (фрагмент):")
    print(summary.head(8).to_string(index=False))
    print("\nЗначимость (Welch):")
    print(sig.to_string(index=False))
    print("\nРекомендации (черновик):")
    print(rec_text)
    print(f"\nФайлы: CSV, PNG, {json_path}")
    if os.path.isfile(template):
        print(f"Отчёт с данными Python: {os.path.join(out_dir, 'monte_carlo_agile_report.html')}")


if __name__ == "__main__":
    main()
