import re

file_path = 'web/monte_carlo_agile.html'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. CHANGE FONTS
old_fonts = '<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">'
new_fonts = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700;800&display=swap" rel="stylesheet">'
text = text.replace(old_fonts, new_fonts)

text = text.replace("'JetBrains Mono', monospace", "'Inter', sans-serif")
text = text.replace("'Syne', sans-serif", "'Montserrat', sans-serif")

# 2. PROGRESS BAR PERCENTAGES
# runSimulation text replacements
text = text.replace("pb.style.width='10%';pl.textContent='Подключение к API...';", "pb.style.width='10%';pl.textContent='10% — Подключение к API...';")
text = text.replace("pb.style.width='30%';pl.textContent='Счёт Монте-Карло на сервере...';", "pb.style.width='30%';pl.textContent='30% — Счёт Монте-Карло на сервере...';")
text = text.replace("pb.style.width='95%';pl.textContent='Построение графиков...';", "pb.style.width='95%';pl.textContent='95% — Построение графиков...';")
text = text.replace("pb.style.width='100%';pl.textContent='Готово!';", "pb.style.width='100%';pl.textContent='100% — Готово!';")

# 3. TAB RESTRICTION
# We need to add "let simulationHasRun = false;" at the top of the JS section.
js_start = "// === UTILS ==="
text = text.replace(js_start, "let simulationHasRun = false;\n// === UTILS ===")

# In runSimulation, set simulationHasRun = true;
text = text.replace("applyPythonExport(data);", "applyPythonExport(data);\n    simulationHasRun = true;")

# Update switchTab function
old_switch_tab = '''function switchTab(n){
  const ns=['simulation','results','distributions','table','recs','history'];
  document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('active',ns[i]===n));
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('tab-'+n).classList.add('active');
}'''

new_switch_tab = '''function switchTab(n){
  if (n !== 'simulation' && !simulationHasRun) {
    alert('Пожалуйста, сначала запустите симуляцию (нажмите кнопку "ЗАПУСТИТЬ СИМУЛЯЦИЮ"), чтобы увидеть результаты.');
    return;
  }
  const ns=['simulation','results','distributions','table','recs','history'];
  document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('active',ns[i]===n));
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('tab-'+n).classList.add('active');
}'''

text = text.replace(old_switch_tab, new_switch_tab)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESS")
