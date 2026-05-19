text = open('web/monte_carlo_agile.html', encoding='utf8').read()

# Map: search by pure ASCII anchors, replace entirely
pairs = [
    ('Cycle Time: <strong style="color:var(--scrum)">${mean(s.ct).toFixed(2)}',
     'Цикловое время: <strong style="color:var(--scrum)">${mean(s.ct).toFixed(2)}'),
    ('Throughput: <strong style="color:var(--scrum)">${mean(s.tp).toFixed(1)}',
     'Пропускная способность: <strong style="color:var(--scrum)">${mean(s.tp).toFixed(1)}'),
    ('Lead Time: <strong style="color:var(--scrum)">${mean(s.lt).toFixed(2)}',
     'Время выполнения: <strong style="color:var(--scrum)">${mean(s.lt).toFixed(2)}'),
    ('Cycle Time: <strong style="color:var(--kanban)">${mean(k.ct).toFixed(2)}',
     'Цикловое время: <strong style="color:var(--kanban)">${mean(k.ct).toFixed(2)}'),
    ('Throughput: <strong style="color:var(--kanban)">${mean(k.tp).toFixed(1)}',
     'Пропускная способность: <strong style="color:var(--kanban)">${mean(k.tp).toFixed(1)}'),
    ('Lead Time: <strong style="color:var(--kanban)">${mean(k.lt).toFixed(2)}',
     'Время выполнения: <strong style="color:var(--kanban)">${mean(k.lt).toFixed(2)}'),
]

for old, new in pairs:
    if old in text:
        text = text.replace(old, new)
        print('OK:', old[:40])
    else:
        print('MISS:', old[:40])

# Fix units: replace дн. -> дней  and зад/ит. -> задач/итерацию
# inside the verdict block (starts after position 47000)
VERDICT_START = text.find('verdict-text')
if VERDICT_START == -1:
    print('WARNING: verdict-text not found')
else:
    before = text[:VERDICT_START]
    after = text[VERDICT_START:]
    after = after.replace('.toFixed(2)} дн.</strong>', '.toFixed(2)} дней</strong>')
    after = after.replace('.toFixed(1)} зад/ит.</strong>', '.toFixed(1)} задач/итерацию</strong>')
    after = after.replace('.toFixed(2)} дн.', '.toFixed(2)} дней')
    text = before + after
    print('Units fixed')

open('web/monte_carlo_agile.html', 'w', encoding='utf8').write(text)

# Verify
t = open('web/monte_carlo_agile.html', encoding='utf8').read()
for term in ['Cycle Time', 'Throughput', 'Lead Time']:
    idx = t.find(term, 47000)
    if idx != -1:
        print(f'STILL in verdict: {repr(t[idx:idx+60])}')
    else:
        print(f'CLEAN: "{term}" removed from verdict')

print('Done.')
