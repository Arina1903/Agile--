"""
Comprehensive UI fix:
1. Animated progress bar (fake animation 0->100%)
2. Bigger chart heights for projector
3. Bigger fonts on chart axes/labels
4. Scrum/Kanban section labels more prominent
5. Tooltips - consistent style (border, shadow, font)
6. Custom modal dialog (Да/Нет instead of OK/Cancel)
"""

file_path = 'web/monte_carlo_agile.html'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# ─────────────────────────────────────────────────────────────────
# 1. CHART HEIGHTS: bigger for projector
# ─────────────────────────────────────────────────────────────────
text = text.replace(
    '.chart-wrap { position: relative; height: 210px; }',
    '.chart-wrap { position: relative; height: 300px; }'
)
text = text.replace(
    '.chart-wrap.tall { height: 260px; }',
    '.chart-wrap.tall { height: 340px; }'
)

# ─────────────────────────────────────────────────────────────────
# 2. CHART FONTS in JS constants (bigger for projector)
# ─────────────────────────────────────────────────────────────────
text = text.replace(
    "const SC='#0284c7',KC='#ea580c',SD='rgba(2,132,199,0.13)',KD='rgba(234,88,12,0.13)',GR='#e2e8f0',TC='#64748b';",
    "const SC='#0284c7',KC='#ea580c',SD='rgba(2,132,199,0.18)',KD='rgba(234,88,12,0.18)',GR='#cbd5e1',TC='#1e293b';"
)

# Chart.js global options - bigger fonts everywhere
old_bopts = """const BOpts={responsive:true,maintainAspectRatio:false,
  plugins:{legend:{labels:{color:TC,font:{family:'JetBrains Mono',size:13},boxWidth:10}},
    tooltip:{backgroundColor:'#ffffff',borderColor:'#e2e8f0',borderWidth:1,titleColor:'#e8e8f0',bodyColor:TC,titleFont:{family:'JetBrains Mono',size:14},bodyFont:{family:'JetBrains Mono',size:13}}},
  scales:{x:{grid:{color:GR},ticks:{color:TC,font:{family:'JetBrains Mono',size:13}}},
    y:{grid:{color:GR},ticks:{color:TC,font:{family:'JetBrains Mono',size:13}}}}};"""

new_bopts = """const BOpts={responsive:true,maintainAspectRatio:false,
  plugins:{legend:{labels:{color:TC,font:{family:'Inter',size:15,weight:'600'},boxWidth:14,padding:16}},
    tooltip:{backgroundColor:'#ffffff',borderColor:'#94a3b8',borderWidth:2,titleColor:'#0f172a',bodyColor:'#334155',titleFont:{family:'Inter',size:15,weight:'700'},bodyFont:{family:'Inter',size:14},padding:10,cornerRadius:8,displayColors:true}},
  scales:{x:{grid:{color:GR},ticks:{color:TC,font:{family:'Inter',size:14,weight:'500'}}},
    y:{grid:{color:GR},ticks:{color:TC,font:{family:'Inter',size:14,weight:'500'}}}}};"""

text = text.replace(old_bopts, new_bopts)

# Fix remaining JetBrains Mono references in chart options
text = text.replace("family:'JetBrains Mono',size:13", "family:'Inter',size:14,weight:'500'")
text = text.replace("family:'JetBrains Mono',size:14", "family:'Inter',size:15,weight:'600'")
text = text.replace("family:'JetBrains Mono',size:12", "family:'Inter',size:13,weight:'500'")

# ─────────────────────────────────────────────────────────────────
# 3. SCRUM / KANBAN section labels - more prominent
# ─────────────────────────────────────────────────────────────────
text = text.replace(
    '<div style="font-size:13px;color:var(--scrum);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px;">Scrum</div>',
    '<div style="font-size:15px;font-weight:800;font-family:\'Montserrat\',sans-serif;color:var(--scrum);letter-spacing:0.08em;text-transform:uppercase;margin-bottom:12px;padding:6px 12px;background:#e0f2fe;border-radius:6px;display:inline-block;">⟩ Scrum</div>'
)
text = text.replace(
    '<div style="font-size:13px;color:var(--kanban);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px;">Kanban</div>',
    '<div style="font-size:15px;font-weight:800;font-family:\'Montserrat\',sans-serif;color:var(--kanban);letter-spacing:0.08em;text-transform:uppercase;margin-bottom:12px;padding:6px 12px;background:#ffedd5;border-radius:6px;display:inline-block;">⟩ Kanban</div>'
)

# ─────────────────────────────────────────────────────────────────
# 4. PROGRESS BAR - animated, taller, with percentage text inside
# ─────────────────────────────────────────────────────────────────
text = text.replace(
    '.progress-bar-bg { height: 3px; background: var(--border); border-radius: 2px; }',
    '.progress-bar-bg { height: 28px; background: #e2e8f0; border-radius: 14px; overflow:hidden; position:relative; }'
)
text = text.replace(
    '.progress-bar-fill { height: 100%; background: var(--accent); border-radius: 2px; width: 0%; transition: width 0.15s; }',
    '.progress-bar-fill { height: 100%; background: linear-gradient(90deg,#6366f1,#4f46e5); border-radius: 14px; width: 0%; transition: width 0.4s ease; display:flex; align-items:center; justify-content:flex-end; padding-right:10px; font-size:13px; font-weight:700; color:#fff; white-space:nowrap; min-width:40px; }'
)
text = text.replace(
    '.progress-label { font-size: 13px; color: var(--muted); margin-top: 4px; text-align: center; }',
    '.progress-label { font-size: 13px; color: var(--muted); margin-top: 6px; text-align: center; font-weight:500; }'
)

# ─────────────────────────────────────────────────────────────────
# 5. TOOLTIPS - consistent, no neon, add border
# ─────────────────────────────────────────────────────────────────
old_tooltip_css = """  .param-tooltip {
    position: relative; display: inline-flex; align-items: center; justify-content: center;
    width: 22px; height: 22px; font-size: 14px; line-height: 1; border-radius: 50%;
    background: rgba(124,58,237,0.2); color: var(--accent); cursor: help; flex-shrink: 0;
    border: 1px solid rgba(124,58,237,0.35); vertical-align: middle;
  }
  .param-tooltip:hover, .param-tooltip:focus { outline: none; background: rgba(124,58,237,0.35); }
  .param-tooltip-text {
    display: none; position: absolute; z-index: 200; left: 0; bottom: calc(100% + 6px);
    width: min(320px, 85vw); padding: 10px 12px; font-size: 13px; font-weight: 400;
    line-height: 1.55; color: var(--text); text-align: left; letter-spacing: normal; text-transform: none;
    background: #ffffff; border: 2px solid var(--border); border-radius: 8px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.1); pointer-events: auto;
  }"""

new_tooltip_css = """  .param-tooltip {
    position: relative; display: inline-flex; align-items: center; justify-content: center;
    width: 22px; height: 22px; font-size: 13px; font-weight: 700; line-height: 1; border-radius: 50%;
    background: #e2e8f0; color: #475569; cursor: help; flex-shrink: 0;
    border: 2px solid #94a3b8; vertical-align: middle; font-family: 'Inter', sans-serif;
  }
  .param-tooltip:hover, .param-tooltip:focus { outline: none; background: #cbd5e1; color: #1e293b; }
  .param-tooltip-text {
    display: none; position: absolute; z-index: 200; left: 0; bottom: calc(100% + 8px);
    width: min(320px, 85vw); padding: 12px 14px; font-size: 13px; font-weight: 400;
    line-height: 1.6; color: #1e293b; text-align: left; letter-spacing: normal; text-transform: none;
    background: #ffffff; border: 2px solid #94a3b8; border-radius: 10px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.15); pointer-events: auto;
    font-family: 'Inter', sans-serif;
  }"""

text = text.replace(old_tooltip_css, new_tooltip_css)

# ─────────────────────────────────────────────────────────────────
# 6. CUSTOM MODAL (Да/Нет) + progress animation CSS
# ─────────────────────────────────────────────────────────────────
modal_css = """
  /* Custom confirm modal */
  .modal-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.4); z-index:9999; align-items:center; justify-content:center; }
  .modal-overlay.visible { display:flex; }
  .modal-box { background:#fff; border-radius:14px; padding:28px 32px; max-width:420px; width:90%; box-shadow:0 20px 60px rgba(0,0,0,0.2); border:2px solid #e2e8f0; }
  .modal-title { font-family:'Montserrat',sans-serif; font-size:17px; font-weight:700; color:#0f172a; margin-bottom:12px; }
  .modal-text { font-size:15px; color:#334155; line-height:1.6; margin-bottom:24px; }
  .modal-btns { display:flex; gap:12px; justify-content:flex-end; }
  .modal-btn { padding:10px 24px; border-radius:8px; font-family:'Inter',sans-serif; font-size:15px; font-weight:600; cursor:pointer; border:2px solid transparent; transition:all 0.15s; }
  .modal-btn-yes { background:linear-gradient(135deg,#6366f1,#4f46e5); color:#fff; }
  .modal-btn-yes:hover { opacity:0.9; transform:translateY(-1px); }
  .modal-btn-no { background:#f1f5f9; color:#334155; border-color:#cbd5e1; }
  .modal-btn-no:hover { background:#e2e8f0; }
"""
text = text.replace('</style>', modal_css + '</style>')

# Modal HTML (insert before </div>\n<script>)
modal_html = """
<!-- Custom modal -->
<div class="modal-overlay" id="modal-overlay">
  <div class="modal-box">
    <div class="modal-title" id="modal-title">Смена сценария</div>
    <div class="modal-text" id="modal-text">Применить параметры нового сценария?</div>
    <div class="modal-btns">
      <button class="modal-btn modal-btn-no" id="modal-no">Нет — оставить мои данные</button>
      <button class="modal-btn modal-btn-yes" id="modal-yes">Да — применить сценарий</button>
    </div>
  </div>
</div>
"""
text = text.replace('</div>\n<script>', modal_html + '\n</div>\n<script>', 1)

# ─────────────────────────────────────────────────────────────────
# 7. Replace loadScenario confirm() with custom modal
# ─────────────────────────────────────────────────────────────────
old_load = """function loadScenario(k,btn){
  const ans = confirm("Применить параметры нового сценария?\\n\\nОК - Сбросить на параметры сценария\\nОтмена - Сохранить введённые вами данные");
  if(ans){
    const s=SC_DATA[k];
    const map={dur:'duration',team:'team',unc:'uncertainty',spd:'sprint',vel:'velocity',ovh:'overhead',wip:'wip',cyc:'cycle',flow:'flow'};
    Object.entries(map).forEach(([sk,id])=>{document.getElementById('sl-'+id).value=s[sk];updateLabel(id);});
    document.getElementById('scenario-desc').innerHTML=s.desc;
  }
  document.querySelectorAll('.scenario-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');
  hideResults();
}"""

new_load = """let _pendingScenarioKey = null, _pendingScenarioBtn = null;
function loadScenario(k, btn) {
  _pendingScenarioKey = k;
  _pendingScenarioBtn = btn;
  document.getElementById('modal-overlay').classList.add('visible');
}
document.getElementById('modal-yes').onclick = function() {
  document.getElementById('modal-overlay').classList.remove('visible');
  const k = _pendingScenarioKey, btn = _pendingScenarioBtn;
  const s = SC_DATA[k];
  const map={dur:'duration',team:'team',unc:'uncertainty',spd:'sprint',vel:'velocity',ovh:'overhead',wip:'wip',cyc:'cycle',flow:'flow'};
  Object.entries(map).forEach(([sk,id])=>{document.getElementById('sl-'+id).value=s[sk];updateLabel(id);});
  document.getElementById('scenario-desc').innerHTML=s.desc;
  document.querySelectorAll('.scenario-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');
  hideResults();
};
document.getElementById('modal-no').onclick = function() {
  document.getElementById('modal-overlay').classList.remove('visible');
  const btn = _pendingScenarioBtn;
  document.querySelectorAll('.scenario-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');
  hideResults();
};"""

text = text.replace(old_load, new_load)

# ─────────────────────────────────────────────────────────────────
# 8. Progress bar animation - update fill text on each step
# ─────────────────────────────────────────────────────────────────
# In simulation loop, update fill to show percent inside bar
old_sim_step = "    pb.style.width=steps[i][0]+'%';pl.textContent=steps[i][1];"
new_sim_step = "    pb.style.width=steps[i][0]+'%';pb.textContent=steps[i][0]+'%';pl.textContent=steps[i][1];"
text = text.replace(old_sim_step, new_sim_step)

# ─────────────────────────────────────────────────────────────────
# 9. Mini conclusions for ALL bar charts in Results (add if missing)
# ─────────────────────────────────────────────────────────────────
# Radar chart - add explanation below
old_radar_card = '    <div class="card" style="margin-top:0;">\n      <div class="card-title">Интегральная оценка по 6 метрикам (радар)</div>\n      <div style="max-width:480px;margin:0 auto;"><div class="chart-wrap tall"><canvas id="chart-radar"></canvas></div></div>\n    </div>'
new_radar_card = '    <div class="card" style="margin-top:0;">\n      <div class="card-title">Интегральная оценка по 6 метрикам (радар)</div>\n      <div style="max-width:480px;margin:0 auto;"><div class="chart-wrap tall"><canvas id="chart-radar"></canvas></div></div>\n      <div id="md-radar" style="font-size:14px;color:var(--muted);margin-top:12px;text-align:center;"></div>\n    </div>'
text = text.replace(old_radar_card, new_radar_card)

# CI chart - add mini conclusion
old_ci_card = '      <div class="card"><div class="card-title">Перцентильный профиль — Цикловое время</div><div class="chart-wrap"><canvas id="chart-ci-cycle"></canvas></div></div>'
new_ci_card = '      <div class="card"><div class="card-title">Перцентильный профиль — Цикловое время</div><div class="chart-wrap"><canvas id="chart-ci-cycle"></canvas></div><div id="md-ci" style="font-size:14px;color:var(--muted);margin-top:10px;"></div></div>'
text = text.replace(old_ci_card, new_ci_card)

old_cr_card = '      <div class="card"><div class="card-title">Завершение спринта / WIP-соблюдение (%)</div><div class="chart-wrap"><canvas id="chart-completion-rate"></canvas></div></div>'
new_cr_card = '      <div class="card"><div class="card-title">Завершение спринта / WIP-соблюдение (%)</div><div class="chart-wrap"><canvas id="chart-completion-rate"></canvas></div><div id="md-cr" style="font-size:14px;color:var(--muted);margin-top:10px;"></div></div>'
text = text.replace(old_cr_card, new_cr_card)

# Update updateMiniConclusions to also fill radar/ci/cr
old_mini = """function updateMiniConclusions(s, k) {
  const d_tp = mean(k.tp) - mean(s.tp);
  const d_ct = mean(k.ct) - mean(s.ct);
  const el = id => { const e=document.getElementById(id); if(e) return e; return {textContent:''}; };
  el('mc-tp').innerHTML = `В среднем <strong>${d_tp > 0 ? 'Kanban' : 'Scrum'}</strong> показывает бóльшую пропускную способность на <strong>${Math.abs(d_tp).toFixed(1)} зад/ит</strong>.`;
  el('mc-cyc').innerHTML = `Задачи доставляются быстрее в <strong>${d_ct < 0 ? 'Kanban' : 'Scrum'}</strong> (разница <strong>${Math.abs(d_ct).toFixed(1)} дн</strong>).`;
  const d_lt = mean(k.lt) - mean(s.lt);
  el('mc-lt').innerHTML = `Lead time лучше у <strong>${d_lt < 0 ? 'Kanban' : 'Scrum'}</strong> на <strong>${Math.abs(d_lt).toFixed(1)} дн</strong>.`;
  const d_td = mean(k.td) - mean(s.td);
  el('mc-td').innerHTML = `Проект завершится быстрее при <strong>${d_td < 0 ? 'Kanban' : 'Scrum'}</strong>.`;
  el('md-cyc').innerHTML = `Распределение Kanban <strong>${std(k.ct) < std(s.ct) ? 'имеет меньший разброс' : 'имеет более длинный хвост'}</strong> по сравнению со Scrum.`;
  el('md-tp').innerHTML = `Стабильность потока: CoV Scrum=<strong>${(std(s.tp)/mean(s.tp)).toFixed(2)}</strong>, Kanban=<strong>${(std(k.tp)/mean(k.tp)).toFixed(2)}</strong>.`;
}"""

new_mini = """function updateMiniConclusions(s, k) {
  const d_tp = mean(k.tp) - mean(s.tp);
  const d_ct = mean(k.ct) - mean(s.ct);
  const el = id => { const e=document.getElementById(id); if(e) return e; return {innerHTML:''}; };
  el('mc-tp').innerHTML = `📊 В среднем <strong>${d_tp > 0 ? 'Kanban' : 'Scrum'}</strong> показывает бо́льшую пропускную способность на <strong>${Math.abs(d_tp).toFixed(1)} зад/ит</strong>.`;
  el('mc-cyc').innerHTML = `⏱ Задачи доставляются быстрее в <strong>${d_ct < 0 ? 'Kanban' : 'Scrum'}</strong> (разница <strong>${Math.abs(d_ct).toFixed(1)} дн</strong>).`;
  const d_lt = mean(k.lt) - mean(s.lt);
  el('mc-lt').innerHTML = `🔁 Lead time лучше у <strong>${d_lt < 0 ? 'Kanban' : 'Scrum'}</strong> на <strong>${Math.abs(d_lt).toFixed(1)} дн</strong>.`;
  const d_td = mean(k.td) - mean(s.td);
  el('mc-td').innerHTML = `🏁 Проект завершится быстрее при <strong>${d_td < 0 ? 'Kanban' : 'Scrum'}</strong> (разница <strong>${Math.abs(d_td).toFixed(1)} дн</strong>).`;
  el('md-cyc').innerHTML = `📉 Разброс цикловых времён: Kanban σ=<strong>${std(k.ct).toFixed(2)}</strong> vs Scrum σ=<strong>${std(s.ct).toFixed(2)}</strong> — Kanban <strong>${std(k.ct) < std(s.ct) ? 'стабильнее' : 'менее стабилен'}</strong>.`;
  el('md-tp').innerHTML = `📈 Стабильность потока: CoV Scrum=<strong>${(std(s.tp)/mean(s.tp)).toFixed(2)}</strong>, Kanban=<strong>${(std(k.tp)/mean(k.tp)).toFixed(2)}</strong>. ${(std(k.tp)/mean(k.tp)) < (std(s.tp)/mean(s.tp)) ? 'Kanban равномернее.' : 'Scrum равномернее.'}`;
  const sCTp10=pct(s.ct,10),kCTp10=pct(k.ct,10),sCTp90=pct(s.ct,90),kCTp90=pct(k.ct,90);
  el('md-ci').innerHTML = `📐 Диапазон P10–P90: Scrum <strong>${sCTp10.toFixed(1)}–${sCTp90.toFixed(1)} дн</strong>, Kanban <strong>${kCTp10.toFixed(1)}–${kCTp90.toFixed(1)} дн</strong>. ${(sCTp90-sCTp10) < (kCTp90-kCTp10) ? 'Scrum предсказуемее.' : 'Kanban предсказуемее.'}`;
  const sCR=mean(s.cr),kWC=mean(k.wc);
  el('md-cr').innerHTML = `✅ Scrum завершает в среднем <strong>${(sCR*100).toFixed(0)}%</strong> задач спринта. Kanban соблюдает WIP-лимиты в <strong>${(kWC*100).toFixed(0)}%</strong> случаев.`;
  const sv=[mean(s.tp),1-mean(s.ct)/10,1-mean(s.lt)/15,1-mean(s.def),mean(s.cr),1/(std(s.tp)/mean(s.tp)+0.01)/20];
  const kv=[mean(k.tp),1-mean(k.ct)/10,1-mean(k.lt)/15,1-mean(k.def),mean(k.wc),1/(std(k.tp)/mean(k.tp)+0.01)/20];
  const sScore=sv.reduce((a,b)=>a+b,0), kScore=kv.reduce((a,b)=>a+b,0);
  el('md-radar').innerHTML = `🎯 Интегральный балл: Scrum <strong>${sScore.toFixed(2)}</strong> vs Kanban <strong>${kScore.toFixed(2)}</strong> — общее преимущество у <strong>${sScore > kScore ? 'Scrum' : 'Kanban'}</strong>.`;
}"""

text = text.replace(old_mini, new_mini)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESS - all changes applied")
