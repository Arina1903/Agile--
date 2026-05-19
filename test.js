
let simulationHasRun = false;
// === UTILS ===
function randn(){let u=0,v=0;while(!u)u=Math.random();while(!v)v=Math.random();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}
function randLN(mu,s){return Math.exp(mu+s*randn());}
function randPoisson(lam){const L=Math.exp(-lam);let k=0,p=1;do{k++;p*=Math.random();}while(p>L);return k-1;}
function clamp(v,lo,hi){return Math.max(lo,Math.min(hi,v));}
function mean(a){return a.reduce((s,v)=>s+v,0)/a.length;}
function std(a){const m=mean(a);return Math.sqrt(a.reduce((s,v)=>s+(v-m)**2,0)/a.length);}
function pct(a,p){const s=[...a].sort((x,y)=>x-y);return s[Math.floor(p/100*(s.length-1))];}
function cohensD(a,b){const ma=mean(a),mb=mean(b),sa=std(a),sb=std(b),sp=Math.sqrt((sa**2+sb**2)/2);return Math.abs(ma-mb)/(sp||1);}
function pValue(a,b){const ma=mean(a),mb=mean(b),sa=std(a),sb=std(b),n=Math.min(a.length,b.length),se=Math.sqrt(sa**2/n+sb**2/n),t=Math.abs(ma-mb)/(se||1);if(t>3.5)return'< 0.001';if(t>2.5)return'< 0.01';if(t>1.96)return'< 0.05';return'≥ 0.05';}

const KPI_HELP={
  throughput:'Среднее число завершённых задач на одну итерацию проекта по всем прогонам Монте-Карло (сумма задач за проект / число итераций, затем усреднение по прогонам). Справа: относительная разница средних Kanban и Scrum в процентах от среднего Scrum: (μ<sub>K</sub>−μ<sub>S</sub>)/μ<sub>S</sub>×100%.',
  cycletime:'Среднее цикловое время задачи в днях по выборке прогонов. В модели — показатель «сколько в среднем занимает прохождение работы по задаче». Для сравнения лучше меньшее значение; процент справа считается так же относительно Scrum.',
  leadtime:'Средний Lead Time в днях — упрощённое время от постановки в работу до готовности в симуляции. Сравнение и Δ% — как для циклового времени (лучше — меньше).',
  predict:'Показатель «стабильности» пропускной способности: 1 / (коэффициент вариации + 0.01), где CoV = std(tp) / mean(tp) по прогонам. Чем выше число, тем меньше относительный разброс throughput между прогонами. Справа — относительное отличие средних Kanban и Scrum.'
};

// === SIMULATION (параметры → API /api/simulate) ===
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

// === CHARTS ===
const CH={};
const SC='#0284c7',KC='#ea580c',SD='rgba(2,132,199,0.18)',KD='rgba(234,88,12,0.18)',GR='#cbd5e1',TC='#1e293b';
const BOpts={responsive:true,maintainAspectRatio:false,
  plugins:{legend:{labels:{color:TC,font:{family:'Inter',size:16,weight:'700'},boxWidth:16,padding:18}},
    tooltip:{backgroundColor:'#ffffff',borderColor:'#94a3b8',borderWidth:2,titleColor:'#0f172a',bodyColor:'#334155',titleFont:{family:'Inter',size:15,weight:'700'},bodyFont:{family:'Inter',size:14},padding:10,cornerRadius:8,displayColors:true}},
  scales:{x:{grid:{color:GR},ticks:{color:TC,font:{family:'Inter',size:15,weight:'600'}}},
    y:{grid:{color:GR},ticks:{color:TC,font:{family:'Inter',size:15,weight:'600'}}}}};

function dc(id){if(CH[id]){CH[id].destroy();delete CH[id];}}

function barChart(id,sD,kD,yLabel){
  dc(id);
  const labs=['P10','P25','Медиана','Среднее','P75','P90'];
  const sv=[pct(sD,10),pct(sD,25),pct(sD,50),mean(sD),pct(sD,75),pct(sD,90)];
  const kv=[pct(kD,10),pct(kD,25),pct(kD,50),mean(kD),pct(kD,75),pct(kD,90)];
  CH[id]=new Chart(document.getElementById(id).getContext('2d'),{type:'bar',
    data:{labels:labs,datasets:[{label:'Scrum',data:sv,backgroundColor:SD,borderColor:SC,borderWidth:1.5,borderRadius:4},{label:'Kanban',data:kv,backgroundColor:KD,borderColor:KC,borderWidth:1.5,borderRadius:4}]},
    options:{...BOpts,scales:{...BOpts.scales,y:{...BOpts.scales.y,title:{display:true,text:yLabel,color:TC,font:{family:'Inter',size:16,weight:'700'}}}}}});
}

function radarChart(s,k){
  dc('chart-radar');
  function norm(v,lo,hi){return clamp((v-lo)/(hi-lo||1),0,1);}
  const sm=mean(s.tp),km=mean(k.tp),sct=mean(s.ct),kct=mean(k.ct),slt=mean(s.lt),klt=mean(k.lt),sdf=mean(s.def),kdf=mean(k.def),scr=mean(s.cr),kwc=mean(k.wc),sp=1/(std(s.tp)/sm+0.01),kp=1/(std(k.tp)/km+0.01);
  const mx={tp:Math.max(sm,km)*1.2,ct:Math.max(sct,kct)*1.2,lt:Math.max(slt,klt)*1.2,p:Math.max(sp,kp)*1.2};
  const sv=[norm(sm,0,mx.tp),1-norm(sct,0,mx.ct),1-norm(slt,0,mx.lt),1-norm(sdf,0,0.35),norm(scr,0,1),norm(sp,0,mx.p)].map(v=>(v*10).toFixed(2));
  const kv=[norm(km,0,mx.tp),1-norm(kct,0,mx.ct),1-norm(klt,0,mx.lt),1-norm(kdf,0,0.35),norm(kwc,0,1),norm(kp,0,mx.p)].map(v=>(v*10).toFixed(2));
  CH['chart-radar']=new Chart(document.getElementById('chart-radar').getContext('2d'),{type:'radar',
    data:{labels:['Пропускная\nспособность','Цикловое\nвремя ↓','Lead Time ↓','Качество ↓','Завершение\nспринта/WIP','Предсказуе\nмость'],
      datasets:[{label:'Scrum',data:sv,backgroundColor:'rgba(0,212,255,0.1)',borderColor:SC,borderWidth:2,pointBackgroundColor:SC},{label:'Kanban',data:kv,backgroundColor:'rgba(255,107,53,0.1)',borderColor:KC,borderWidth:2,pointBackgroundColor:KC}]},
    options:{responsive:true,maintainAspectRatio:false,scales:{r:{grid:{color:GR},ticks:{color:TC,backdropColor:'transparent',font:{family:'Inter',size:14,weight:'600'}},pointLabels:{color:TC,font:{family:'Inter',size:15,weight:'700'}}}},plugins:{...BOpts.plugins}}});
}

function distChart(id,sD,kD,bins,xlabel){
  dc(id);
  const all=[...sD,...kD],mn=pct(all,2),mx=pct(all,98),step=(mx-mn)/bins;
  const labs=Array.from({length:bins},(_,i)=>(mn+i*step).toFixed(1));
  function bld(d){const c=new Array(bins).fill(0);d.forEach(v=>{const b=clamp(Math.floor((v-mn)/step),0,bins-1);c[b]++;});return c.map(x=>x/d.length*100);}
  CH[id]=new Chart(document.getElementById(id).getContext('2d'),{type:'line',
    data:{labels:labs,datasets:[{label:'Scrum',data:bld(sD),backgroundColor:SD,borderColor:SC,borderWidth:1.5,fill:true,tension:0.4,pointRadius:0},{label:'Kanban',data:bld(kD),backgroundColor:KD,borderColor:KC,borderWidth:1.5,fill:true,tension:0.4,pointRadius:0}]},
    options:{...BOpts,scales:{x:{...BOpts.scales.x,title:{display:true,text:xlabel,color:TC,font:{family:'Inter',size:16,weight:'700'}}},y:{...BOpts.scales.y,title:{display:true,text:'Частота (%)',color:TC,font:{family:'Inter',size:16,weight:'700'}}}}}});
}

function ciChart(sD,kD){
  dc('chart-ci-cycle');
  const labs=['P5','P25','Медиана','P75','P95'];
  const sv=[pct(sD,5),pct(sD,25),pct(sD,50),pct(sD,75),pct(sD,95)];
  const kv=[pct(kD,5),pct(kD,25),pct(kD,50),pct(kD,75),pct(kD,95)];
  CH['chart-ci-cycle']=new Chart(document.getElementById('chart-ci-cycle').getContext('2d'),{type:'line',
    data:{labels:labs,datasets:[{label:'Scrum',data:sv,borderColor:SC,backgroundColor:SD,fill:true,tension:0.3,borderWidth:2,pointRadius:4,pointBackgroundColor:SC},{label:'Kanban',data:kv,borderColor:KC,backgroundColor:KD,fill:true,tension:0.3,borderWidth:2,pointRadius:4,pointBackgroundColor:KC}]},
    options:{...BOpts}});
}

function crChart(sCR,kWC){
  dc('chart-completion-rate');
  const sm=mean(sCR),ss=std(sCR),km=mean(kWC),ks=std(kWC);
  const fmt=v=>clamp(v*100,0,100).toFixed(1);
  CH['chart-completion-rate']=new Chart(document.getElementById('chart-completion-rate').getContext('2d'),{type:'bar',
    data:{labels:['Среднее','−1σ','+1σ','P10','P90'],
      datasets:[{label:'Scrum: %завершения',data:[sm,sm-ss,sm+ss,pct(sCR,10),pct(sCR,90)].map(fmt),backgroundColor:SD,borderColor:SC,borderWidth:1.5,borderRadius:4},{label:'Kanban: WIP-соблюд.',data:[km,km-ks,km+ks,pct(kWC,10),pct(kWC,90)].map(fmt),backgroundColor:KD,borderColor:KC,borderWidth:1.5,borderRadius:4}]},
    options:{...BOpts,scales:{...BOpts.scales,y:{...BOpts.scales.y,max:110,title:{display:true,text:'%',color:TC,font:{family:'Inter',size:16,weight:'700'}}}}}});
}

function metricsTable(s,k){
  const rows=[
    {n:'Цикловое время (дни)',sD:s.ct,kD:k.ct,lb:true},
    {n:'Lead Time (дни)',sD:s.lt,kD:k.lt,lb:true},
    {n:'Пропускная способность (задач/ит.)',sD:s.tp,kD:k.tp,lb:false},
    {n:'Время завершения проекта (дни)',sD:s.td,kD:k.td,lb:true},
    {n:'Уровень дефектов',sD:s.def,kD:k.def,lb:true},
    {n:'Завершение спринта / WIP-соблюд.',sD:s.cr,kD:k.wc,lb:false},
  ];
  const fmt=(v,n)=>n.includes('дефект')||n.includes('Завершение')?(v*100).toFixed(1)+'%':v.toFixed(2);
  document.getElementById('metrics-tbody').innerHTML=rows.map(r=>{
    const sm=mean(r.sD),km=mean(r.kD),ss=std(r.sD),ks=std(r.kD);
    const diff=((km-sm)/sm*100).toFixed(1);
    const kw=r.lb?km<sm:km>sm;const tie=Math.abs(diff)<2;
    return`<tr><td>${r.n}</td><td class="val-scrum">${fmt(sm,r.n)}</td><td style="color:var(--muted)">${fmt(ss,r.n)}</td><td style="color:var(--muted)">${fmt(pct(r.sD,10),r.n)}–${fmt(pct(r.sD,90),r.n)}</td><td class="val-kanban">${fmt(km,r.n)}</td><td style="color:var(--muted)">${fmt(ks,r.n)}</td><td style="color:var(--muted)">${fmt(pct(r.kD,10),r.n)}–${fmt(pct(r.kD,90),r.n)}</td><td style="color:${tie?'var(--muted)':kw?'var(--success)':'#f87171'}">${diff>0?'+':''}${diff}%</td><td><span class="winner ${tie?'tie':kw?'kanban':'scrum'}">${tie?'≈':kw?'Kanban':'Scrum'}</span></td></tr>`;
  }).join('');
}

function sigTable(s,k){
  const rows=[{n:'Цикловое время',a:s.ct,b:k.ct},{n:'Lead Time',a:s.lt,b:k.lt},{n:'Пропускная способность',a:s.tp,b:k.tp},{n:'Дефекты',a:s.def,b:k.def}];
  document.getElementById('sig-tbody').innerHTML=rows.map(r=>{
    const pv=pValue(r.a,r.b),d=cohensD(r.a,r.b).toFixed(3),sig=pv==='≥ 0.05'?'❌ Не значимо':'✓ Значимо';
    const ef=parseFloat(d)<0.2?'Малый':parseFloat(d)<0.5?'Средний':parseFloat(d)<0.8?'Большой':'Очень большой';
    return`<tr><td>${r.n}</td><td style="color:${pv==='≥ 0.05'?'var(--muted)':'var(--success)'}">${pv}</td><td style="color:${pv==='≥ 0.05'?'var(--muted)':'var(--success)'}">${sig}</td><td>${d} (${ef})</td><td style="color:var(--muted);font-size:13px">${pv!=='≥ 0.05'?'Значимо при α=0.05':'Нет оснований отвергнуть H₀'}</td></tr>`;
  }).join('');
}

function renderRecs(s,k,p){
  const sp=1/(std(s.tp)/mean(s.tp)+0.01),kp=1/(std(k.tp)/mean(k.tp)+0.01);
  document.getElementById('scrum-dyn-title').textContent=p.sig>0.4?'При текущей неопределённости Scrum под давлением':'Scrum оптимален при текущих параметрах';
  document.getElementById('scrum-dyn-text').textContent=p.sig>0.4?`Коэффициент σ=${p.sig.toFixed(2)} выше порога 0.35. Рассмотрите Scrumban или сокращение спринта до ${Math.max(7,p.spd-7)} дней.`:`При σ=${p.sig.toFixed(2)} Scrum предсказуем. Cycle time = ${mean(s.ct).toFixed(1)} дн. Текущий спринт ${p.spd} дней оптимален.`;
  document.getElementById('kanban-dyn-title').textContent=p.flow>3?'Kanban оптимален при текущем потоке':'Kanban менее эффективен при низком потоке';
  document.getElementById('kanban-dyn-text').textContent=p.flow>3?`Поток ${p.flow.toFixed(1)} зад/день хорошо подходит для Kanban. Рекомендуемый WIP = ${Math.round(p.team*0.75)}.`:`При потоке ${p.flow.toFixed(1)} зад/день Kanban не реализует преимущества. Throughput = ${mean(k.tp).toFixed(1)} зад/ит.`;
  document.getElementById('wip-rec-text').textContent=`Оптимальный WIP для команды ${p.team} чел. = ${Math.round(p.team*0.75)}–${p.team} задач/этап (закон Литтла). Текущий WIP=${p.wip}. ${p.wip>p.team?'Рекомендуется снизить WIP.':'Текущий WIP в норме.'}`;
  const sw=[mean(s.ct)<mean(k.ct),sp>kp,mean(s.tp)>mean(k.tp)].filter(Boolean).length;
  const kw=[mean(k.ct)<mean(s.ct),kp>sp,mean(k.tp)>mean(s.tp)].filter(Boolean).length;
  const win=sw>kw?'Scrum':kw>sw?'Kanban':'Равнозначны';
  const wc=win==='Scrum'?'var(--scrum)':win==='Kanban'?'var(--kanban)':'var(--muted)';
  const d_ct_pct = ((mean(k.ct)-mean(s.ct))/mean(s.ct)*100).toFixed(1);
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
</div>`;
}

function renderKPIs(s,k){
  document.getElementById('kpi-placeholder').style.display='none';
  document.getElementById('kpi-grid').style.display='block';
  const sTP=mean(s.tp),kTP=mean(k.tp),sCT=mean(s.ct),kCT=mean(k.ct),sLT=mean(s.lt),kLT=mean(k.lt),sP=1/(std(s.tp)/sTP+0.01),kP=1/(std(k.tp)/kTP+0.01);
  function kpi(key,lbl,sv,kv,unit,lb){
    const d=((kv-sv)/sv*100).toFixed(1);const kw=lb?kv<sv:kv>sv;const tie=Math.abs(d)<2;const cls=tie?'neutral':kw?'better':'worse';
    const hint=KPI_HELP[key]||'';
    return`<div class="kpi-head"><span class="kpi-label">${lbl}</span><button type="button" class="kpi-more">Пояснение ▼</button></div><div class="kpi-values"><div><div class="kpi-val scrum">${sv.toFixed(1)}<span style="font-size:14px;color:var(--muted)">${unit}</span></div><div class="kpi-sub">Scrum</div></div><div><div class="kpi-val kanban">${kv.toFixed(1)}<span style="font-size:14px;color:var(--muted)">${unit}</span></div><div class="kpi-sub">Kanban</div></div><div class="kpi-diff ${cls}">${kw?'▼':'▲'} ${Math.abs(d)}%</div></div><div class="kpi-detail" hidden>${hint}</div>`;
  }
  document.getElementById('kpi-throughput').innerHTML=kpi('throughput','Пропускная способность',sTP,kTP,' зад/ит',false);
  document.getElementById('kpi-cycletime').innerHTML=kpi('cycletime','Цикловое время',sCT,kCT,' д',true);
  document.getElementById('kpi-leadtime').innerHTML=kpi('leadtime','Lead Time',sLT,kLT,' д',true);
  document.getElementById('kpi-predict').innerHTML=kpi('predict','Предсказуемость (1/CoV)',sP,kP,'',false);
}

// === MAIN RUN ===
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
}

// === TABS ===
function switchTab(n){
  if (n !== 'simulation' && !simulationHasRun) {
    alert('Пожалуйста, сначала запустите симуляцию (нажмите кнопку "ЗАПУСТИТЬ СИМУЛЯЦИЮ"), чтобы увидеть результаты.');
    return;
  }
  const ns=['simulation','results','distributions','table','recs','history'];
  document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('active',ns[i]===n));
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('tab-'+n).classList.add('active');
}

// === SLIDERS ===
const LM={duration:v=>v,team:v=>v,uncertainty:v=>(v/100).toFixed(2),sprint:v=>v,velocity:v=>v,overhead:v=>v,wip:v=>v,cycle:v=>(v/10).toFixed(1),flow:v=>(v/10).toFixed(1)};
function updateLabel(k){const v=document.getElementById('sl-'+k).value;document.getElementById('lbl-'+k).textContent=LM[k](v);}


const runHistory = [];
function saveHistory(p, s, k) {
  runHistory.push({
    time: new Date().toLocaleTimeString(),
    p: {...p},
    s: s,
    k: k,
    s_ct: mean(s.ct),
    k_ct: mean(k.ct),
    win: mean(s.ct) < mean(k.ct) ? 'Scrum' : 'Kanban'
  });
  const t = document.getElementById('history-tbody');
  if(t) t.innerHTML = runHistory.map((h,i) => `<tr style="cursor:pointer; transition: background 0.2s;" onmouseover="this.style.background='#e2e8f0'" onmouseout="this.style.background='transparent'" onclick="restoreHistory(${i})" title="Нажмите, чтобы загрузить этот прогон"><td>#${i+1} (${h.time})</td><td>σ=${h.p.sig.toFixed(2)}, team=${h.p.team}, wip=${h.p.wip}</td><td><strong>${h.s_ct.toFixed(1)} дн.</strong></td><td><strong>${h.k_ct.toFixed(1)} дн.</strong></td><td style="color:${h.win==='Scrum'?'var(--scrum)':'var(--kanban)'}; font-weight: bold;">${h.win}</td></tr>`).reverse().join('');
}

function restoreHistory(idx) {
  const h = runHistory[idx];
  const p = h.p;
  // Restore sliders
  document.getElementById('sl-duration').value = p.dur;
  document.getElementById('sl-team').value = p.team;
  document.getElementById('sl-uncertainty').value = p.sig * 100;
  document.getElementById('sl-sprint').value = p.spd;
  document.getElementById('sl-velocity').value = p.vel;
  document.getElementById('sl-overhead').value = p.ovh * 100;
  document.getElementById('sl-wip').value = p.wip;
  document.getElementById('sl-cycle').value = p.cyc * 10;
  document.getElementById('sl-flow').value = p.flow * 10;
  document.getElementById('sel-iters').value = p.iters;
  ['duration','team','uncertainty','sprint','velocity','overhead','wip','cycle','flow'].forEach(updateLabel);
  
  // Render views
  renderKPIs(h.s, h.k);
  ['results','dist','table'].forEach(x=>{document.getElementById(x+'-placeholder').style.display='none';document.getElementById(x+'-content').style.display='block';});
  document.getElementById('recs-placeholder').style.display='none';document.getElementById('recs-content').style.display='block';
  barChart('chart-throughput',h.s.tp,h.k.tp,'Задач/итерацию');
  barChart('chart-cycle',h.s.ct,h.k.ct,'Дней');
  barChart('chart-lead',h.s.lt,h.k.lt,'Дней');
  barChart('chart-completion',h.s.td,h.k.td,'Дней');
  radarChart(h.s,h.k);
  distChart('chart-dist-cycle',h.s.ct,h.k.ct,30,'Цикловое время (дни)');
  distChart('chart-dist-tp',h.s.tp,h.k.tp,30,'Пропускная способность (зад/ит.)');
  ciChart(h.s.ct,h.k.ct);
  crChart(h.s.cr,h.k.wc);
  metricsTable(h.s,h.k);
  sigTable(h.s,h.k);
  renderRecs(h.s,h.k,p);
  updateMiniConclusions(h.s, h.k);
  
  // Switch back to results
  switchTab('results');
  window.scrollTo({top: 0, behavior: 'smooth'});
}

function updateMiniConclusions(s, k) {
  const d_tp = mean(k.tp) - mean(s.tp);
  const d_ct = mean(k.ct) - mean(s.ct);
  const el = id => { const e=document.getElementById(id); if(e) return e; return {innerHTML:''}; };
  el('mc-tp').innerHTML = `В среднем <strong>${d_tp > 0 ? 'Kanban' : 'Scrum'}</strong> показывает бо́льшую пропускную способность на <strong>${Math.abs(d_tp).toFixed(1)} зад/ит</strong>.`;
  el('mc-cyc').innerHTML = `Задачи доставляются быстрее в <strong>${d_ct < 0 ? 'Kanban' : 'Scrum'}</strong> (разница <strong>${Math.abs(d_ct).toFixed(1)} дн</strong>).`;
  const d_lt = mean(k.lt) - mean(s.lt);
  el('mc-lt').innerHTML = `Lead time лучше у <strong>${d_lt < 0 ? 'Kanban' : 'Scrum'}</strong> на <strong>${Math.abs(d_lt).toFixed(1)} дн</strong>.`;
  const d_td = mean(k.td) - mean(s.td);
  el('mc-td').innerHTML = `Проект завершится быстрее при <strong>${d_td < 0 ? 'Kanban' : 'Scrum'}</strong> (разница <strong>${Math.abs(d_td).toFixed(1)} дн</strong>).`;
  el('md-cyc').innerHTML = `Разброс цикловых времён: Kanban σ=<strong>${std(k.ct).toFixed(2)}</strong> vs Scrum σ=<strong>${std(s.ct).toFixed(2)}</strong> — Kanban <strong>${std(k.ct) < std(s.ct) ? 'стабильнее' : 'менее стабилен'}</strong>.`;
  el('md-tp').innerHTML = `Стабильность потока: CoV Scrum=<strong>${(std(s.tp)/mean(s.tp)).toFixed(2)}</strong>, Kanban=<strong>${(std(k.tp)/mean(k.tp)).toFixed(2)}</strong>. ${(std(k.tp)/mean(k.tp)) < (std(s.tp)/mean(s.tp)) ? 'Kanban равномернее.' : 'Scrum равномернее.'}`;
  const sCTp10=pct(s.ct,10),kCTp10=pct(k.ct,10),sCTp90=pct(s.ct,90),kCTp90=pct(k.ct,90);
  el('md-ci').innerHTML = `Диапазон P10–P90: Scrum <strong>${sCTp10.toFixed(1)}–${sCTp90.toFixed(1)} дн</strong>, Kanban <strong>${kCTp10.toFixed(1)}–${kCTp90.toFixed(1)} дн</strong>. ${(sCTp90-sCTp10) < (kCTp90-kCTp10) ? 'Scrum предсказуемее.' : 'Kanban предсказуемее.'}`;
  const sCR=mean(s.cr),kWC=mean(k.wc);
  el('md-cr').innerHTML = `Scrum завершает в среднем <strong>${(sCR*100).toFixed(0)}%</strong> задач спринта. Kanban соблюдает WIP-лимиты в <strong>${(kWC*100).toFixed(0)}%</strong> случаев.`;
  const sv=[mean(s.tp),1-mean(s.ct)/10,1-mean(s.lt)/15,1-mean(s.def),mean(s.cr),1/(std(s.tp)/mean(s.tp)+0.01)/20];
  const kv=[mean(k.tp),1-mean(k.ct)/10,1-mean(k.lt)/15,1-mean(k.def),mean(k.wc),1/(std(k.tp)/mean(k.tp)+0.01)/20];
  const sScore=sv.reduce((a,b)=>a+b,0), kScore=kv.reduce((a,b)=>a+b,0);
  el('md-radar').innerHTML = `Интегральный балл: Scrum <strong>${sScore.toFixed(2)}</strong> vs Kanban <strong>${kScore.toFixed(2)}</strong> — общее преимущество у <strong>${sScore > kScore ? 'Scrum' : 'Kanban'}</strong>.`;
}

function hideResults() {
  ['results','dist','table'].forEach(x=>{document.getElementById(x+'-placeholder').style.display='flex';document.getElementById(x+'-content').style.display='none';});
  document.getElementById('recs-placeholder').style.display='flex';document.getElementById('recs-content').style.display='none';
  document.getElementById('kpi-placeholder').style.display='flex';
  document.getElementById('kpi-grid').style.display='none';
}

// === SCENARIOS ===
const SC_DATA={
  web:{dur:12,team:6,unc:30,spd:14,vel:42,ovh:15,wip:4,cyc:35,flow:22,desc:'<strong>Веб-приложение:</strong> Команда 5–7 чел., спринты 2 нед., умеренная неопределённость. Apache JIRA (WICKET, SOLR, TAPESTRY).'},
  startup:{dur:8,team:4,unc:55,spd:7,vel:28,ovh:10,wip:3,cyc:25,flow:30,desc:'<strong>Стартап MVP:</strong> Высокая неопределённость σ=0.55, частые смены приоритетов, маленькая команда. GitHub Issues стартап-проектов.'},
  enterprise:{dur:20,team:10,unc:20,spd:14,vel:65,ovh:22,wip:6,cyc:45,flow:18,desc:'<strong>Энтерпрайз:</strong> Крупный проект, большая команда, жёсткие процессы, overhead 22%. Apache JIRA корпоративных проектов.'},
  maintenance:{dur:24,team:3,unc:40,spd:14,vel:20,ovh:8,wip:2,cyc:15,flow:45,desc:'<strong>Поддержка/обслуживание:</strong> Непрерывный поток багфиксов и hotfix. Поток 4.5 зад/день. Идеальный сценарий для Kanban.'}
};
let _pendingScenarioKey = null, _pendingScenarioBtn = null;
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
};

['duration','team','uncertainty','sprint','velocity','overhead','wip','cycle','flow'].forEach(updateLabel);

function applyPythonExport(py){
  const p=py.params;
  const scrum=py.scrum;
  const kanban=py.kanban;
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

(function(){
  const grid=document.getElementById('kpi-grid');
  if(!grid)return;
  grid.addEventListener('click',function(e){
    const btn=e.target.closest('.kpi-more');
    if(!btn)return;
    e.preventDefault();
    const card=btn.closest('.kpi-card');
    const det=card.querySelector('.kpi-detail');
    if(!det)return;
    const show=det.hasAttribute('hidden');
    if(show){det.removeAttribute('hidden');btn.textContent='Свернуть ▲';}
    else{det.setAttribute('hidden','');btn.textContent='Пояснение ▼';}
  });
})();
