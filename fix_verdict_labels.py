text = open('web/monte_carlo_agile.html', encoding='utf8').read()

replacements = [
    # Scrum card
    ('Cycle Time: <strong style="color:var(--scrum)">${mean(s.ct).toFixed(2)} дн.</strong>',
     'Цикловое время: <strong style="color:var(--scrum)">${mean(s.ct).toFixed(2)} дней</strong>'),
    ('Throughput: <strong style="color:var(--scrum)">${mean(s.tp).toFixed(1)} зад/ит.</strong>',
     'Пропускная способность: <strong style="color:var(--scrum)">${mean(s.tp).toFixed(1)} задач/итерацию</strong>'),
    ('Lead Time: <strong style="color:var(--scrum)">${mean(s.lt).toFixed(2)} дн.</strong>',
     'Время выполнения: <strong style="color:var(--scrum)">${mean(s.lt).toFixed(2)} дней</strong>'),
    # Kanban card
    ('Cycle Time: <strong style="color:var(--kanban)">${mean(k.ct).toFixed(2)} дн.</strong>',
     'Цикловое время: <strong style="color:var(--kanban)">${mean(k.ct).toFixed(2)} дней</strong>'),
    ('Throughput: <strong style="color:var(--kanban)">${mean(k.tp).toFixed(1)} зад/ит.</strong>',
     'Пропускная способность: <strong style="color:var(--kanban)">${mean(k.tp).toFixed(1)} задач/итерацию</strong>'),
    ('Lead Time: <strong style="color:var(--kanban)">${mean(k.lt).toFixed(2)} дн.</strong>',
     'Время выполнения: <strong style="color:var(--kanban)">${mean(k.lt).toFixed(2)} дней</strong>'),
    # Bottom summary
    ('σ=${p.sig.toFixed(2)} | Команда: ${p.team} чел. | Спринт ${p.spd} дн. | WIP ${p.wip} | Поток ${p.flow.toFixed(1)} зад/день | N=${p.iters.toLocaleString()} итераций',
     'Неопределённость σ=${p.sig.toFixed(2)} | Команда: ${p.team} чел. | Длительность спринта: ${p.spd} дней | WIP-лимит: ${p.wip} | Поток задач: ${p.flow.toFixed(1)} задач/день | Итераций: ${p.iters.toLocaleString()}'),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new)
        print(f'OK: {old[:40]}...')
    else:
        print(f'MISS: {old[:40]}...')

open('web/monte_carlo_agile.html', 'w', encoding='utf8').write(text)
print('Done.')
