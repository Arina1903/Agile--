import re

# 1. Update badges in HTML
html_path = 'web/monte_carlo_agile.html'
with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    '.badge-scrum { background: var(--scrum-dim); color: var(--scrum); border: 1px solid rgba(0,212,255,0.25); }',
    '.badge-scrum { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }'
)
text = text.replace(
    '.badge-kanban { background: var(--kanban-dim); color: var(--kanban); border: 1px solid rgba(255,107,53,0.25); }',
    '.badge-kanban { background: #ffedd5; color: #c2410c; border: 1px solid #fed7aa; }'
)
text = text.replace(
    '.badge-mc { background: rgba(124,58,237,0.15); color: #a78bfa; border: 1px solid rgba(124,58,237,0.3); }',
    '.badge-mc { background: #e0e7ff; color: #4338ca; border: 1px solid #c7d2fe; }'
)
text = text.replace(
    '.badge-mc { background: rgba(124,58,237,0.15); color: #a78bfa; border: 1px solid rgba(124,58,237,0.3); }',
    '.badge-mc { background: #e0e7ff; color: #4338ca; border: 1px solid #c7d2fe; }'
)
# Just in case it was partially replaced:
text = re.sub(r'\.badge-scrum \{.*?\}', '.badge-scrum { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }', text)
text = re.sub(r'\.badge-kanban \{.*?\}', '.badge-kanban { background: #ffedd5; color: #c2410c; border: 1px solid #fed7aa; }', text)
text = re.sub(r'\.badge-mc \{.*?\}', '.badge-mc { background: #e0e7ff; color: #4338ca; border: 1px solid #c7d2fe; }', text)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(text)


# 2. Update build_static.py
build_path = 'webapp/build_static.py'
with open(build_path, 'r', encoding='utf-8') as f:
    btext = f.read()

# Replace new_run with the fixed version
new_run_fixed = """// === MAIN RUN ===
async function runSimulation(){
  const btn=document.getElementById('btn-run');
  const pw=document.getElementById('progress-wrap');
  const pb=document.getElementById('progress-bar');
  const pl=document.getElementById('progress-label');
  btn.disabled=true;btn.textContent='⏳ СИМУЛЯЦИЯ...';pw.classList.add('visible');
  const p=getP();
  pb.style.width='10%';pl.textContent='10% — Подключение к API...';
  try{
    const body={...p,iters:+p.iters,vel:+p.vel,dur:+p.dur,team:+p.team,spd:+p.spd,wip:+p.wip};
    pb.style.width='30%';pl.textContent='30% — Счёт Монте-Карло на сервере...';
    const res=await fetch('/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    if(!res.ok){
      let msg=res.statusText;
      try{const j=await res.json();msg=typeof j.detail==='string'?j.detail:(Array.isArray(j.detail)?j.detail.map(x=>x.msg||x).join('; '):JSON.stringify(j));}catch(_){}
      throw new Error(msg);
    }
    const data=await res.json();
    pb.style.width='95%';pl.textContent='95% — Построение графиков...';
    applyPythonExport(data);
    simulationHasRun = true;
    const badge=document.getElementById('badge-mc');
    if(badge&&data.params) badge.textContent='Монте-Карло N='+Number(data.params.iters).toLocaleString();
    pb.style.width='100%';pl.textContent='100% — Готово!';
  }catch(e){
    pl.textContent='Ошибка: '+e.message;
    alert('Ошибка: '+e.message);
  }
  btn.disabled=false;btn.textContent='▶ ЗАПУСТИТЬ СНОВА';pw.classList.remove('visible');
}"""

btext = re.sub(r'new_run = """// === MAIN RUN ===.*?\}"""', f'new_run = """{new_run_fixed}"""', btext, flags=re.DOTALL)

with open(build_path, 'w', encoding='utf-8') as f:
    f.write(btext)

print("SUCCESS")
