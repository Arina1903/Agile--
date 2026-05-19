text = open('web/monte_carlo_agile.html', encoding='utf8').read()

old = (
    'Итог по метрикам:</strong> Цикловое время у Kanban ${d_ct_pct > 0 ? \'выше\' : \'ниже\'} на ${Math.abs(d_ct_pct)}%, пропускная способность ${d_tp_pct > 0 ? \'выше\' : \'ниже\'} на ${Math.abs(d_tp_pct)}% относительно Scrum.<br>\n'
    '  Голосование по метрикам: Scrum побеждает по <strong>${sw}</strong> из 3, Kanban — по <strong>${kw}</strong> из 3.<br>\n'
    '  <span style="color:var(--muted);">Параметры: σ=${p.sig.toFixed(2)} | Команда ${p.team} чел. | Спринт ${p.spd} дн. | WIP ${p.wip} | Поток ${p.flow.toFixed(1)} зад/день | N=${p.iters.toLocaleString()} итераций</span>\n'
    '</div>`;\n'
)

new = (
    'Итог по метрикам:</strong><br>\n'
    '  Цикловое время у Kanban ${d_ct_pct > 0 ? \'выше\' : \'ниже\'} на <strong>${Math.abs(d_ct_pct)}%</strong> относительно Scrum.<br>\n'
    '  Пропускная способность у Kanban ${d_tp_pct > 0 ? \'выше\' : \'ниже\'} на <strong>${Math.abs(d_tp_pct)}%</strong> относительно Scrum.<br><br>\n'
    '  Голосование по трём ключевым метрикам: Scrum побеждает по <strong>${sw}</strong> из 3 показателей, Kanban — по <strong>${kw}</strong> из 3 показателей.<br><br>\n'
    '  <span style="color:var(--muted);">\n'
    '    Параметры запуска:<br>\n'
    '    &nbsp;&nbsp;— Коэффициент неопределённости: <strong>${p.sig.toFixed(2)}</strong><br>\n'
    '    &nbsp;&nbsp;— Размер команды: <strong>${p.team} человек</strong><br>\n'
    '    &nbsp;&nbsp;— Длительность спринта: <strong>${p.spd} дней</strong><br>\n'
    '    &nbsp;&nbsp;— WIP-лимит (Kanban): <strong>${p.wip} задачи</strong><br>\n'
    '    &nbsp;&nbsp;— Интенсивность потока: <strong>${p.flow.toFixed(1)} задач в день</strong><br>\n'
    '    &nbsp;&nbsp;— Количество итераций Монте-Карло: <strong>${p.iters.toLocaleString()}</strong>\n'
    '  </span>\n'
    '</div>`;\n'
)

if old in text:
    text = text.replace(old, new)
    print('OK: summary block replaced')
else:
    print('MISS - trying line by line search...')
    # Debug: print actual chars at that area
    import sys; sys.stdout.reconfigure(encoding='utf-8')
    idx = text.find('Голосование по метрикам')
    print(repr(text[idx-200:idx+300]))

open('web/monte_carlo_agile.html', 'w', encoding='utf8').write(text)
print('Done.')
