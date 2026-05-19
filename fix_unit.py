text = open('web/monte_carlo_agile.html', encoding='utf8').read()

old_str = 'задач/итерацию'
new_str = 'задач в итерацию'

if old_str in text:
    text = text.replace(old_str, new_str)
    print(f'OK: replaced "{old_str}" with "{new_str}"')
else:
    print(f'MISS: could not find "{old_str}"')

open('web/monte_carlo_agile.html', 'w', encoding='utf8').write(text)
print('Done.')
