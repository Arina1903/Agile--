"""Параметры как в веб-прототипе monte_carlo_agile.html (слайдеры по умолчанию)."""

# Общие
PROJECT_DURATION_ITERATIONS = 12  # «длительность проекта» в единицах внутреннего цикла модели
TEAM_SIZE = 6
UNCERTAINTY_SIGMA = 0.30  # коэффициент неопределённости σ (0.10–0.70 в HTML)

# Scrum
SPRINT_LENGTH_DAYS = 14
BASE_VELOCITY_STORY_POINTS = 42
SCRUM_OVERHEAD_FRACTION = 0.15  # 15% церемоний

# Kanban
KANBAN_WIP_LIMIT = 4
KANBAN_BASE_CYCLE_DAYS = 3.5  # слайдер 35/10
FLOW_TASKS_PER_DAY = 2.2  # слайдер 22/10

# Монте-Карло (число стохастических прогонов)
N_MONTE_CARLO_RUNS = 10_000
RANDOM_SEED = 42
