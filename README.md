# Agile--

## Монте-Карло: сравнение Scrum и Kanban

Веб-приложение и консольный сценарий для стохастического моделирования гибких процессов: сравниваются метрики **Scrum** и **Kanban** при заданных параметрах команды, спринта, WIP и неопределённости.

Стек: **Python**, **FastAPI**, **uvicorn**, фронтенд — статическая SPA с графиками (Chart.js).

## Требования

- Python 3.10+ (рекомендуется актуальная стабильная версия)
- Зависимости из `requirements.txt` (numpy, pandas, matplotlib, scipy, fastapi, uvicorn)

## Установка

Из корня репозитория:

```bash
python -m venv .venv
```

Активация виртуального окружения:

- **cmd:** `.venv\Scripts\activate.bat`
- **PowerShell:** `.\.venv\Scripts\Activate.ps1` (при отключённых сценариях можно вызывать `.venv\Scripts\python.exe` напрямую)

```bash
pip install -r requirements.txt
```

## Запуск веб-интерфейса

Из корня проекта:

```bash
python -m webapp
```

Или:

```bash
uvicorn webapp.main:app --reload --host 127.0.0.1 --port 8000
```

В браузере откройте: **http://127.0.0.1:8000**

На Windows можно запустить **`start_webapp.bat`** (двойной щелчок или из командной строки).

- Документация API (Swagger): **http://127.0.0.1:8000/docs**
- Проверка: `GET /api/health`
- Расчёт: `POST /api/simulate` (тело запроса — параметры симуляции)

## Консольный прогон с артефактами

Параметры по умолчанию задаются в **`config.py`**. Запуск:

```bash
python run.py
```

В каталоге **`output/`** создаются CSV, PNG, JSON и при наличии шаблона **`web/monte_carlo_agile.html`** — HTML-отчёт с вшитыми данными. Текстовые рекомендации сохраняются в `output/recommendations_ru.txt`.

## Структура проекта (кратко)

| Путь | Назначение |
|------|------------|
| `webapp/` | FastAPI-приложение, раздача статики, API симуляции |
| `monte_carlo.py`, `sim_html_agile.py` | Ядро Монте-Карло и экспорт результатов |
| `config.py` | Параметры по умолчанию для `run.py` |
| `run.py` | Пакетный расчёт и выгрузка файлов в `output/` |
| `visualize.py`, `recommendations.py` | Графики и текст рекомендаций |
| `requirements.txt` | Зависимости Python |
