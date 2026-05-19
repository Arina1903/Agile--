text = open('web/monte_carlo_agile.html', encoding='utf8').read()

# Replace by unique anchors around the English labels (no Cyrillic in search keys)
# Scrum card
text = text.replace(
    'Cycle Time: <strong style="color:var(--scrum)">${mean(s.ct).toFixed(2)}',
    '\u0426\u0438\u043a\u043b\u043e\u0432\u043e\u0435 \u0432\u0440\u0435\u043c\u044f: <strong style="color:var(--scrum)">${mean(s.ct).toFixed(2)}'
)
text = text.replace(
    'Throughput: <strong style="color:var(--scrum)">${mean(s.tp).toFixed(1)}',
    '\u041f\u0440\u043e\u043f\u0443\u0441\u043a\u043d\u0430\u044f \u0441\u043f\u043e\u0441\u043e\u0431\u043d\u043e\u0441\u0442\u044c: <strong style="color:var(--scrum)">${mean(s.tp).toFixed(1)}'
)
text = text.replace(
    'Lead Time: <strong style="color:var(--scrum)">${mean(s.lt).toFixed(2)}',
    '\u0412\u0440\u0435\u043c\u044f \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f: <strong style="color:var(--scrum)">${mean(s.lt).toFixed(2)}'
)
# Kanban card
text = text.replace(
    'Cycle Time: <strong style="color:var(--kanban)">${mean(k.ct).toFixed(2)}',
    '\u0426\u0438\u043a\u043b\u043e\u0432\u043e\u0435 \u0432\u0440\u0435\u043c\u044f: <strong style="color:var(--kanban)">${mean(k.ct).toFixed(2)}'
)
text = text.replace(
    'Throughput: <strong style="color:var(--kanban)">${mean(k.tp).toFixed(1)}',
    '\u041f\u0440\u043e\u043f\u0443\u0441\u043a\u043d\u0430\u044f \u0441\u043f\u043e\u0441\u043e\u0431\u043d\u043e\u0441\u0442\u044c: <strong style="color:var(--kanban)">${mean(k.tp).toFixed(1)}'
)
text = text.replace(
    'Lead Time: <strong style="color:var(--kanban)">${mean(k.lt).toFixed(2)}',
    '\u0412\u0440\u0435\u043c\u044f \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f: <strong style="color:var(--kanban)">${mean(k.lt).toFixed(2)}'
)

# Fix abbreviations in units:  дн. -> дней,  зад/ит. -> задач/итерацию
# in the verdict block only (between the two cards)
# We target the unit strings that follow the metric values
import re
# дн.</strong> -> дней</strong>  inside the verdict
text = re.sub(r'(\$\{mean\([sk]\.[clp][tla]\)\.toFixed\(2\)\}) \u0434\u043d\.\u003c/strong\u003e',
              r'\1 \u0434\u043d\u0435\u0439\u003c/strong\u003e', text)
# зад/ит.</strong> -> задач/итерацию</strong>
text = re.sub(r'(\$\{mean\([sk]\.tp\)\.toFixed\(1\)\}) \u0437\u0430\u0434/\u0438\u0442\.\u003c/strong\u003e',
              r'\1 \u0437\u0430\u0434\u0430\u0447/\u0438\u0442\u0435\u0440\u0430\u0446\u0438\u044e\u003c/strong\u003e', text)

open('web/monte_carlo_agile.html', 'w', encoding='utf8').write(text)
print('Done')

# Verify
text2 = open('web/monte_carlo_agile.html', encoding='utf8').read()
for term in ['Cycle Time', 'Throughput', 'Lead Time']:
    count = text2.count(term)
    # only in card positions 47000+
    idx = text2.find(term, 47000)
    if idx != -1:
        print(f'STILL FOUND at {idx}: {repr(text2[idx:idx+80])}')
    else:
        print(f'CLEAN: {term} not found in verdict area')
