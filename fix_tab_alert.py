text = open('web/monte_carlo_agile.html', encoding='utf8').read()

old = '''function switchTab(n){
  if (n !== 'simulation' && !simulationHasRun) {
    alert('Пожалуйста, сначала запустите симуляцию (нажмите кнопку "ЗАПУСТИТЬ СИМУЛЯЦИЮ"), чтобы увидеть результаты.');
    return;
  }'''

new = '''function switchTab(n){'''

if old in text:
    text = text.replace(old, new)
    print('OK: alert block removed')
else:
    # Try to find by partial match and replace the whole guard block
    import re
    text, n = re.subn(
        r"function switchTab\(n\)\{\s*if \(n !== 'simulation' && !simulationHasRun\) \{.*?return;\s*\}",
        "function switchTab(n){",
        text, flags=re.DOTALL
    )
    print(f'Regex replacements: {n}')

open('web/monte_carlo_agile.html', 'w', encoding='utf8').write(text)
print('Done.')
