text = open('web/monte_carlo_agile.html', encoding='utf8').read()

fixes = [
    # KPI card labels in renderKPIs
    ("kpi('leadtime','Lead Time',sLT,kLT,",
     "kpi('leadtime','Время выполнения',sLT,kLT,"),
    ("kpi('predict','Предсказуемость (1/CoV)",
     "kpi('predict','Предсказуемость"),
    # Also check throughput label in KPI
    ("kpi('throughput','Пропускная спос.',",
     "kpi('throughput','Пропускная способность',"),
    ("kpi('throughput','Throughput',",
     "kpi('throughput','Пропускная способность',"),
    # cycle time KPI
    ("kpi('cycletime','Cycle Time',",
     "kpi('cycletime','Цикловое время',"),
    ("kpi('cycletime','Цикловое вр.',",
     "kpi('cycletime','Цикловое время',"),
    # KPI table headers - sigTable
    ("'Lead Time'",
     "'Время выполнения'"),
    # Units
    (" дн.'",
     " дней'"),
    (" зад/ит.'",
     " задач/ит.'"),
]

for old, new in fixes:
    if old in text:
        text = text.replace(old, new)
        print('OK:', old[:50])
    else:
        print('miss:', old[:50])

open('web/monte_carlo_agile.html', 'w', encoding='utf8').write(text)
print('Done.')
