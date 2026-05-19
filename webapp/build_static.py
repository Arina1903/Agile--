"""Собирает webapp/static/index.html из web/monte_carlo_agile.html (один раз или после правок шаблона)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "web" / "monte_carlo_agile.html"
DST_DIR = ROOT / "webapp" / "static"
DST = DST_DIR / "index.html"


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Нет файла: {SRC}")
    DST_DIR.mkdir(parents=True, exist_ok=True)
    text = SRC.read_text(encoding="utf-8")

    text = text.replace(
        "<span class=\"badge badge-mc\">Монте-Карло N=10 000</span>",
        '<span class="badge badge-mc" id="badge-mc">Монте-Карло N=10 000</span>',
    )
    text = text.replace(
        "при разработке веб-приложений. Параметры калиброваны",
        "при разработке веб-приложений. <strong>Симуляция на сервере</strong> (Python / NumPy). Параметры калиброваны",
    )

    old_sim = """// === SIMULATION ===
let SR=null;
function getP(){
  return{
    dur:+document.getElementById('sl-duration').value,
    team:+document.getElementById('sl-team').value,
    sig:+document.getElementById('sl-uncertainty').value/100,
    spd:+document.getElementById('sl-sprint').value,
    vel:+document.getElementById('sl-velocity').value,
    ovh:+document.getElementById('sl-overhead').value/100,
    wip:+document.getElementById('sl-wip').value,
    cyc:+document.getElementById('sl-cycle').value/10,
    flow:+document.getElementById('sl-flow').value/10,
    iters:+document.getElementById('sel-iters').value
  };
}

function simScrum(p){
  const R={tp:[],ct:[],lt:[],cr:[],td:[],def:[]};
  for(let i=0;i<p.iters;i++){
    let totT=0,totC=0,totCR=0;
    for(let s=0;s<p.dur;s++){
      const vel=clamp(randLN(Math.log(p.vel),p.sig),p.vel*0.3,p.vel*2.2);
      const ovh=clamp(p.ovh*(1+0.3*randn()),0,1);
      const tasks=Math.max(1,Math.round(vel/5*(1-ovh)));
      const planned=Math.round(p.vel/5*(1+0.1*randn()));
      totCR+=Math.min(tasks,planned)/Math.max(1,planned);
      for(let t=0;t<tasks;t++) totC+=clamp(randLN(Math.log(p.spd*0.35),p.sig*0.8),0.5,p.spd);
      totT+=tasks;
    }
    const ac=totC/Math.max(1,totT);
    R.tp.push(totT/p.dur);
    R.ct.push(ac);
    R.lt.push(ac+p.spd*(0.5+0.3*Math.abs(randn())));
    R.cr.push(totCR/p.dur);
    R.td.push(p.dur*p.spd*(1+p.sig*0.3*Math.abs(randn())));
    R.def.push(clamp(0.08+p.sig*0.2+0.02*randn(),0.02,0.35));
  }
  return R;
}

function simKanban(p){
  const R={tp:[],ct:[],lt:[],wc:[],td:[],def:[]};
  for(let i=0;i<p.iters;i++){
    let totT=0,totC=0,totWV=0;
    for(let s=0;s<p.dur;s++){
      const arr=randPoisson(p.flow*p.spd);
      const inSys=clamp(arr,0,p.wip*3);
      const wv=Math.max(0,inSys-p.wip)/Math.max(1,inSys);
      totWV+=wv;
      const eWip=Math.min(inSys,p.wip+Math.abs(randn()));
      const tasks=Math.round(eWip*2);
      for(let t=0;t<tasks;t++) totC+=clamp(randLN(Math.log(Math.max(0.5,p.cyc)),p.sig*0.9),0.3,15);
      totT+=tasks;
    }
    const ac=totC/Math.max(1,totT);
    R.tp.push(totT/p.dur);
    R.ct.push(ac);
    R.lt.push(ac*(1.4+0.3*Math.abs(randn())));
    R.wc.push(1-totWV/p.dur);
    R.td.push(p.dur*p.spd*(1+p.sig*0.2*Math.abs(randn())));
    R.def.push(clamp(0.06+p.sig*0.15+0.02*randn(),0.01,0.30));
  }
  return R;
}

// === CHARTS ==="""

    new_sim = """// === SIMULATION (параметры → API /api/simulate) ===
function getP(){
  return{
    dur:+document.getElementById('sl-duration').value,
    team:+document.getElementById('sl-team').value,
    sig:+document.getElementById('sl-uncertainty').value/100,
    spd:+document.getElementById('sl-sprint').value,
    vel:+document.getElementById('sl-velocity').value,
    ovh:+document.getElementById('sl-overhead').value/100,
    wip:+document.getElementById('sl-wip').value,
    cyc:+document.getElementById('sl-cycle').value/10,
    flow:+document.getElementById('sl-flow').value/10,
    iters:+document.getElementById('sel-iters').value
  };
}

// === CHARTS ==="""

    if old_sim not in text:
        raise SystemExit("Шаблон web/monte_carlo_agile.html изменён: блок SIMULATION не найден.")
    text = text.replace(old_sim, new_sim)

    new_run = """// === MAIN RUN ===
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
}"""

    import re
    match = re.search(r'// === MAIN RUN ===.*?btn\.disabled=false;btn\.textContent=.*?;pw\.classList\.remove\(\'visible\'\);\n}', text, flags=re.DOTALL)
    if not match:
        raise SystemExit("Шаблон: блок runSimulation не найден.")
    text = text[:match.start()] + new_run + text[match.end():]

    DST.write_text(text, encoding="utf-8")
    print(f"OK: {DST}")


if __name__ == "__main__":
    main()
