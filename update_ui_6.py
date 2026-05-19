"""
Fix:
1. Progress bar - fake animated increment 30%->90% while server computes
2. Bigger axis X/Y title fonts in all charts
3. Remove all emojis from mini-conclusions and recommendations
4. Bigger/richer Final Verdict section
"""
import re

# ─── FIX build_static.py (server run function) ───────────────────
build_path = 'webapp/build_static.py'
with open(build_path, 'r', encoding='utf-8') as f:
    btext = f.read()

new_run = '''// === MAIN RUN ===
async function runSimulation(){
  const btn=document.getElementById('btn-run');
  const pw=document.getElementById('progress-wrap');
  const pb=document.getElementById('progress-bar');
  const pl=document.getElementById('progress-label');
  btn.disabled=true;btn.textContent='СИМУЛЯЦИЯ...';pw.classList.add('visible');
  const p=getP();

  // Animated progress helper
  let _pct = 0;
  let _interval = null;
  function setProgress(pct, label) {
    _pct = pct;
    pb.style.width = pct + '%';
    pb.textContent = pct + '%';
    pl.textContent = label;
  }
  function animateTo(target, label, stepMs) {
    return new Promise(resolve => {
      _interval && clearInterval(_interval);
      _interval = setInterval(() => {
        if (_pct < target) {
          _pct = Math.min(_pct + 1, target);
          pb.style.width = _pct + '%';
          pb.textContent = _pct + '%';
          pl.textContent = label + ' ' + _pct + '%';
        } else {
          clearInterval(_interval);
          resolve();
        }
      }, stepMs);
    });
  }

  try{
    setProgress(0, 'Инициализация...');
    await animateTo(15, 'Подключение к API...', 30);

    const body={...p,iters:+p.iters,vel:+p.vel,dur:+p.dur,team:+p.team,spd:+p.spd,wip:+p.wip};

    // Start slow animation 15->88% while server computes
    const fakeAnim = animateTo(88, 'Монте-Карло на сервере...', 80);

    const res=await fetch('/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    if(!res.ok){
      clearInterval(_interval);
      let msg=res.statusText;
      try{const j=await res.json();msg=typeof j.detail==='string'?j.detail:(Array.isArray(j.detail)?j.detail.map(x=>x.msg||x).join('; '):JSON.stringify(j));}catch(_){}
      throw new Error(msg);
    }
    const data=await res.json();
    clearInterval(_interval);

    await animateTo(95, 'Построение графиков...', 20);
    applyPythonExport(data);
    simulationHasRun = true;
    const badge=document.getElementById('badge-mc');
    if(badge&&data.params) badge.textContent='Монте-Карло N='+Number(data.params.iters).toLocaleString();
    await animateTo(100, 'Готово!', 15);
    pl.textContent = 'Симуляция завершена успешно.';
  }catch(e){
    clearInterval(_interval);
    pl.textContent='Ошибка: '+e.message;
    alert('Ошибка: '+e.message);
  }
  btn.disabled=false;btn.textContent='ЗАПУСТИТЬ СНОВА';pw.classList.remove('visible');
}'''

# Replace the new_run string inside build_static.py
old_block_start = '    new_run = """// === MAIN RUN ==='
old_block_end = '  btn.disabled=false;btn.textContent=\'▶ ЗАПУСТИТЬ СНОВА\';pw.classList.remove(\'visible\');\n}"""'

start_idx = btext.find(old_block_start)
end_idx = btext.find(old_block_end) + len(old_block_end)
if start_idx == -1 or end_idx == -1:
    print("WARNING: could not find new_run block in build_static.py")
else:
    btext = btext[:start_idx] + '    new_run = """' + new_run + '"""' + btext[end_idx:]

with open(build_path, 'w', encoding='utf-8') as f:
    f.write(btext)
print("build_static.py updated")

# ─── FIX monte_carlo_agile.html ──────────────────────────────────
html_path = 'web/monte_carlo_agile.html'
with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Bigger axis title fonts in Chart.js options (barChart, distChart, crChart)
# Replace all axis title font sizes in chart functions
text = re.sub(
    r"title:\{display:true,text:yLabel,color:TC,font:\{family:'Inter',size:\d+,weight:'500'\}\}",
    "title:{display:true,text:yLabel,color:TC,font:{family:'Inter',size:16,weight:'700'}}",
    text
)
text = re.sub(
    r"title:\{display:true,text:xlabel,color:TC,font:\{family:'Inter',size:\d+,weight:'500'\}\}",
    "title:{display:true,text:xlabel,color:TC,font:{family:'Inter',size:16,weight:'700'}}",
    text
)
text = re.sub(
    r"title:\{display:true,text:'Частота \(%\)',color:TC,font:\{family:'Inter',size:\d+,weight:'500'\}\}",
    "title:{display:true,text:'Частота (%)',color:TC,font:{family:'Inter',size:16,weight:'700'}}",
    text
)
text = re.sub(
    r"title:\{display:true,text:'%',color:TC,font:\{family:'Inter',size:\d+,weight:'500'\}\}",
    "title:{display:true,text:'%',color:TC,font:{family:'Inter',size:16,weight:'700'}}",
    text
)
# Bigger tick fonts
text = text.replace(
    "ticks:{color:TC,font:{family:'Inter',size:14,weight:'500'}}",
    "ticks:{color:TC,font:{family:'Inter',size:15,weight:'600'}}"
)
# Bigger legend labels
text = text.replace(
    "font:{family:'Inter',size:15,weight:'600'},boxWidth:14,padding:16",
    "font:{family:'Inter',size:16,weight:'700'},boxWidth:16,padding:18"
)
# Radar point labels bigger
text = text.replace(
    "pointLabels:{color:TC,font:{family:'Inter',size:14,weight:'500'}}",
    "pointLabels:{color:TC,font:{family:'Inter',size:15,weight:'700'}}"
)
# Radar ticks bigger
text = text.replace(
    "ticks:{color:TC,backdropColor:'transparent',font:{family:'Inter',size:13,weight:'500'}}",
    "ticks:{color:TC,backdropColor:'transparent',font:{family:'Inter',size:14,weight:'600'}}"
)

# 2. Remove all emojis from mini-conclusions
emoji_map = [
    ('📊 ', ''), ('⏱ ', ''), ('🔁 ', ''), ('🏁 ', ''),
    ('📉 ', ''), ('📈 ', ''), ('📐 ', ''), ('✅ ', ''), ('🎯 ', ''),
]
for em, rep in emoji_map:
    text = text.replace(em, rep)

# 3. Remove emojis from recommendations section
text = text.replace('📊', '').replace('⏱', '').replace('🔁', '')
text = text.replace('🏁', '').replace('📉', '').replace('📈', '')
text = text.replace('📐', '').replace('✅', '').replace('🎯', '')

# 4. Bigger / richer Final Verdict section
old_verdict_div = '<div id="verdict-text" style="font-size:12px;line-height:1.9;color:var(--text);"></div>'
new_verdict_div = '<div id="verdict-text" style="font-size:16px;line-height:2.0;color:var(--text);font-family:\'Inter\',sans-serif;"></div>'
text = text.replace(old_verdict_div, new_verdict_div)

# Make final-verdict card more visually prominent
old_verdict_card = '<div class="card" id="final-verdict" style="margin-bottom:18px;">'
new_verdict_card = '<div class="card" id="final-verdict" style="margin-bottom:24px;border:3px solid var(--accent);background:#f8f8ff;">'
text = text.replace(old_verdict_card, new_verdict_card)

# Make verdict card-title bigger
old_verdict_title = '<div class="card-title">Итоговый вердикт симуляции</div>'
new_verdict_title = '<div class="card-title" style="font-size:18px;color:var(--accent);margin-bottom:18px;">Итоговый вердикт симуляции</div>'
text = text.replace(old_verdict_title, new_verdict_title)

# 5. Richer renderRecs verdict text
old_verdict_html = """document.getElementById('verdict-text').innerHTML=`По результатам <strong>${p.iters.toLocaleString()}</strong> итераций Монте-Карло:<br><br><strong style="color:${wc};font-size:15px;">→ Рекомендуется: ${win}</strong><br><br>Scrum: cycle time = <strong style="color:var(--scrum)">${mean(s.ct).toFixed(2)} дн.</strong>, throughput = <strong style="color:var(--scrum)">${mean(s.tp).toFixed(1)} зад/ит.</strong>, предсказуемость = <strong style="color:var(--scrum)">${sp.toFixed(2)}</strong><br>Kanban: cycle time = <strong style="color:var(--kanban)">${mean(k.ct).toFixed(2)} дн.</strong>, throughput = <strong style="color:var(--kanban)">${mean(k.tp).toFixed(1)} зад/ит.</strong>, предсказуемость = <strong style="color:var(--kanban)">${kp.toFixed(2)}</strong><br><br><span style="color:var(--muted);font-size:13px;">σ=${p.sig.toFixed(2)} | Команда: ${p.team} чел. | Спринт: ${p.spd} дн. | WIP: ${p.wip} | Поток: ${p.flow.toFixed(1)} зад/день</span>`;"""

new_verdict_html = """const d_ct_pct = ((mean(k.ct)-mean(s.ct))/mean(s.ct)*100).toFixed(1);
  const d_tp_pct = ((mean(k.tp)-mean(s.tp))/mean(s.tp)*100).toFixed(1);
  document.getElementById('verdict-text').innerHTML=`
<div style="font-size:22px;font-weight:800;font-family:'Montserrat',sans-serif;color:${wc};margin-bottom:14px;padding:12px 18px;background:${win==='Scrum'?'#e0f2fe':win==='Kanban'?'#ffedd5':'#f1f5f9'};border-radius:8px;">
  Рекомендуемая методология: ${win}
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:18px;">
  <div style="background:#f0f9ff;border:2px solid #bae6fd;border-radius:8px;padding:14px;">
    <div style="font-size:14px;font-weight:700;color:var(--scrum);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">Scrum</div>
    <div style="font-size:16px;margin-bottom:6px;">Cycle Time: <strong style="color:var(--scrum)">${mean(s.ct).toFixed(2)} дн.</strong></div>
    <div style="font-size:16px;margin-bottom:6px;">Throughput: <strong style="color:var(--scrum)">${mean(s.tp).toFixed(1)} зад/ит.</strong></div>
    <div style="font-size:16px;margin-bottom:6px;">Lead Time: <strong style="color:var(--scrum)">${mean(s.lt).toFixed(2)} дн.</strong></div>
    <div style="font-size:16px;">Предсказуемость: <strong style="color:var(--scrum)">${sp.toFixed(2)}</strong></div>
  </div>
  <div style="background:#fff7ed;border:2px solid #fed7aa;border-radius:8px;padding:14px;">
    <div style="font-size:14px;font-weight:700;color:var(--kanban);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">Kanban</div>
    <div style="font-size:16px;margin-bottom:6px;">Cycle Time: <strong style="color:var(--kanban)">${mean(k.ct).toFixed(2)} дн.</strong></div>
    <div style="font-size:16px;margin-bottom:6px;">Throughput: <strong style="color:var(--kanban)">${mean(k.tp).toFixed(1)} зад/ит.</strong></div>
    <div style="font-size:16px;margin-bottom:6px;">Lead Time: <strong style="color:var(--kanban)">${mean(k.lt).toFixed(2)} дн.</strong></div>
    <div style="font-size:16px;">Предсказуемость: <strong style="color:var(--kanban)">${kp.toFixed(2)}</strong></div>
  </div>
</div>
<div style="font-size:15px;line-height:1.8;color:#334155;background:#f8fafc;border-radius:8px;padding:14px;border:1px solid #e2e8f0;">
  <strong>Итог по метрикам:</strong> Цикловое время у Kanban ${d_ct_pct > 0 ? 'выше' : 'ниже'} на ${Math.abs(d_ct_pct)}%, пропускная способность ${d_tp_pct > 0 ? 'выше' : 'ниже'} на ${Math.abs(d_tp_pct)}% относительно Scrum.<br>
  Голосование по метрикам: Scrum побеждает по <strong>${sw}</strong> из 3, Kanban — по <strong>${kw}</strong> из 3.<br>
  <span style="color:var(--muted);">Параметры: σ=${p.sig.toFixed(2)} | Команда ${p.team} чел. | Спринт ${p.spd} дн. | WIP ${p.wip} | Поток ${p.flow.toFixed(1)} зад/день | N=${p.iters.toLocaleString()} итераций</span>
</div>`;"""

text = text.replace(old_verdict_html, new_verdict_html)

# 6. In the BROWSER-side runSimulation (for fallback / in HTML source)
# Fix progress bar animation there too (same pattern)
old_sim_steps = """  const steps=[[10,'Инициализация параметров...'],[30,`Симуляция Scrum (${p.iters.toLocaleString()} ит.)...`],[60,`Симуляция Kanban (${p.iters.toLocaleString()} ит.)...`],[80,'Вычисление статистик...'],[95,'Построение графиков...'],[100,'Готово!']];
  let scrum,kanban;
  for(let i=0;i<steps.length;i++){
    pb.style.width=steps[i][0]+'%';pb.textContent=steps[i][0]+'%';pl.textContent=steps[i][1];
    await new Promise(r=>setTimeout(r,150));
    if(i===1) scrum=simScrum(p);
    if(i===2) kanban=simKanban(p);"""

new_sim_steps = """  let scrum,kanban;
  // Animated progress for browser-side simulation
  async function animPct(from, to, label, ms) {
    for(let v=from;v<=to;v++){
      pb.style.width=v+'%';pb.textContent=v+'%';pl.textContent=label+' '+v+'%';
      await new Promise(r=>setTimeout(r,ms));
    }
  }
  await animPct(0,10,'Инициализация...',20);
  scrum=simScrum(p);
  await animPct(11,50,'Симуляция Scrum...',8);
  kanban=simKanban(p);
  await animPct(51,80,'Симуляция Kanban...',8);
  await animPct(81,94,'Вычисление статистик...',15);
  {const i=4;"""

old_render_block = """    if(i===4){
      renderKPIs(scrum,kanban);
      ['results','dist','table'].forEach(x=>{document.getElementById(x+'-placeholder').style.display='none';document.getElementById(x+'-content').style.display='block';});
      document.getElementById('recs-placeholder').style.display='none';document.getElementById('recs-content').style.display='block';
      barChart('chart-throughput',scrum.tp,kanban.tp,'Задач/итерацию');
      barChart('chart-cycle',scrum.ct,kanban.ct,'Дней');
      barChart('chart-lead',scrum.lt,kanban.lt,'Дней');
      barChart('chart-completion',scrum.td,kanban.td,'Дней');
      radarChart(scrum,kanban);
      distChart('chart-dist-cycle',scrum.ct,kanban.ct,30,'Цикловое время (дни)');
      distChart('chart-dist-tp',scrum.tp,kanban.tp,30,'Пропускная способность (зад/ит.)');
      ciChart(scrum.ct,kanban.ct);
      crChart(scrum.cr,kanban.wc);
      metricsTable(scrum,kanban);
      sigTable(scrum,kanban);
      renderRecs(scrum,kanban,p);
      updateMiniConclusions(scrum, kanban);
      saveHistory(p, scrum, kanban);
    }
  }
  btn.disabled=false;btn.textContent='▶ ЗАПУСТИТЬ СНОВА';pw.classList.remove('visible');"""

new_render_block = """      renderKPIs(scrum,kanban);
      ['results','dist','table'].forEach(x=>{document.getElementById(x+'-placeholder').style.display='none';document.getElementById(x+'-content').style.display='block';});
      document.getElementById('recs-placeholder').style.display='none';document.getElementById('recs-content').style.display='block';
      barChart('chart-throughput',scrum.tp,kanban.tp,'Задач/итерацию');
      barChart('chart-cycle',scrum.ct,kanban.ct,'Дней');
      barChart('chart-lead',scrum.lt,kanban.lt,'Дней');
      barChart('chart-completion',scrum.td,kanban.td,'Дней');
      radarChart(scrum,kanban);
      distChart('chart-dist-cycle',scrum.ct,kanban.ct,30,'Цикловое время (дни)');
      distChart('chart-dist-tp',scrum.tp,kanban.tp,30,'Пропускная способность (зад/ит.)');
      ciChart(scrum.ct,kanban.ct);
      crChart(scrum.cr,kanban.wc);
      metricsTable(scrum,kanban);
      sigTable(scrum,kanban);
      renderRecs(scrum,kanban,p);
      updateMiniConclusions(scrum, kanban);
      saveHistory(p, scrum, kanban);
      simulationHasRun=true;
  }
  await animPct(95,100,'Готово!',20);
  pl.textContent='Симуляция завершена успешно.';
  btn.disabled=false;btn.textContent='ЗАПУСТИТЬ СНОВА';pw.classList.remove('visible');"""

if old_sim_steps in text:
    text = text.replace(old_sim_steps, new_sim_steps)
    text = text.replace(old_render_block, new_render_block)
    print("Browser simulation steps updated")
else:
    print("WARNING: browser sim steps not found exactly")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("monte_carlo_agile.html updated")
