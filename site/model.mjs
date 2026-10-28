// Pure selection and graph functions: shared by the UI and offline tests.
export const kinds = ['paper', 'system', 'tool', 'benchmark'];
export const categoryThemes = ['ambiguity', 'answerability', 'interaction', 'context', 'verification'];
export function normalizeState(input, data) {
  const workIDs = new Set(data.works.map(w => w.id));
  const resolve = id => workIDs.has(id) ? id : (data.records.find(r => r.id === id)?.work_id || '');
  const requested=Array.isArray(input.theme)?input.theme:[input.theme];
  const theme=[...new Set(requested.filter(id=>data.themes.some(t=>t.id===id)))];
  return {q: String(input.q || '').slice(0, 240), kind: kinds.includes(input.kind) ? input.kind : '',
    year: data.records.some(r => String(r.year) === input.year) ? input.year : '',
    category: categoryThemes.includes(input.category) ? input.category : '',
    code: input.code === true || input.code === '1',
    labels: input.labels === false || input.labels === '0' || input.labels === 'focus' ? 'focus' :
      input.labels === true || input.labels === '1' || input.labels === 'all' ? 'all' : 'auto',
    view: input.view === 'cards' ? 'cards' : 'table',
    theme, match: input.match==='all'?'all':'any',
    selected: resolve(input.selected || ''), focus: resolve(input.focus || ''),
    sort: ['oldest', 'name'].includes(input.sort) ? input.sort : 'newest'};
}
export function fromURL(search, data) {
  const params=new URLSearchParams(search);
  return normalizeState({...Object.fromEntries(params),theme:params.getAll('theme')}, data);
}
export function toURL(state) {
  const p = new URLSearchParams();
  for (const key of ['q','kind','year','category','focus','selected']) if (state[key]) p.set(key,state[key]);
  if (state.code) p.set('code','1');
  if (state.labels === 'focus') p.set('labels','0');
  if (state.labels === 'all') p.set('labels','1');
  if (state.view === 'cards') p.set('view','cards');
  for(const id of state.theme)p.append('theme',id);
  if(state.match==='all')p.set('match','all');
  if (state.sort !== 'newest') p.set('sort',state.sort);
  return p.toString();
}
export function selectWorks(data, state, {ignoreTheme = false} = {}) {
  const records = new Map(data.records.map(r => [r.id, r]));
  let works = data.works.filter(w => {
    // A single record must satisfy the resource/year/code filters together.
    const members = w.entry_ids.map(id => records.get(id));
    const eligible = members.filter(r => (!state.kind || r.kind === state.kind) &&
      (!state.year || String(r.year) === state.year) && (!state.code || r.code_links.length));
    if (!eligible.length || (state.category && !w.categories.includes(state.category))) return false;
    const text = members.map(r => [r.name,r.id,r.summary,...r.tags].join(' ')).join(' ').toLowerCase();
    if (!state.q.toLowerCase().trim().split(/\s+/).every(term => text.includes(term))) return false;
    return ignoreTheme || !state.theme.length || (state.match==='all' ? state.theme.every(t=>w.themes.includes(t)) : state.theme.some(t=>w.themes.includes(t)));
  });
  if (state.focus) {
    const focus = data.works.find(w => w.id === state.focus);
    works = works.filter(w => w.id === state.focus || (focus && w.themes.some(t => focus.themes.includes(t))));
  }
  if (state.sort === 'name') return [...works].sort((a,b) => a.name.localeCompare(b.name));
  // Build order is already newest first with year-only dates last within year.
  return state.sort === 'oldest' ? [...works.filter(w=>w.year)].reverse().concat(works.filter(w=>!w.year)) : works;
}
export function themeCounts(data, works) {
  const counts = new Map();
  for (const w of works) for (const t of new Set(w.themes)) counts.set(t,(counts.get(t)||0)+1);
  return data.themes.map(t => ({...t,count:counts.get(t.id)||0})).filter(t => t.count)
    .sort((a,b) => b.count-a.count || a.label.localeCompare(b.label));
}
export function graphElements(data, works, state) {
  const nodes = works.map((w,i) => ({data:{id:'w:'+w.id,work:w.id,name:w.name,
    label:w.name.split(':')[0].length<=32 ? w.name.split(':')[0] : w.name.slice(0,29)+'…',kind:w.kind,type:'work',count:1},
    position:{x:300+250*Math.cos(i*2.39996),y:250+200*Math.sin(i*2.39996)}}));
  const edges = [];
  {
    const counts = themeCounts(data,works);
    const themes = state.theme.length ? counts.filter(t=>state.theme.includes(t.id)) : counts.slice(0,15);
    for (const [i,t] of themes.entries()) {
      nodes.push({data:{id:'t:'+t.id,theme:t.id,name:t.label,label:t.label,count:t.count,type:'theme'},
        position:{x:300+90*Math.cos(i*2.39996),y:250+90*Math.sin(i*2.39996)}});
      for (const w of works) if (w.themes.includes(t.id)) edges.push({data:{id:'t:'+t.id+':'+w.id,source:'t:'+t.id,target:'w:'+w.id,type:'theme',label:'Shared catalog theme'}});
    }
  }
  return {nodes,edges};
}
export function exportRecords(data, works) {
  const ids = new Set(works.flatMap(w=>w.entry_ids));
  return {scope:'Catalog source observations, not execution results.',checked:data.checked,
    work_count:works.length,entries:data.records.filter(r=>ids.has(r.id))};
}

// Presentation changes never remove works or alter their catalog relationships.
export function graphPresentation(model, labels='auto') {
  const works=model.nodes.filter(n=>n.data.type==='work').length;
  const themes=model.nodes.filter(n=>n.data.type==='theme').length;
  return {works, themes, showNames:labels==='all'||(labels==='auto'&&works<=12),
    quietEdges:works>12&&themes>1};
}

// Topic hubs surround a stable, topic-ordered ring of works. Geometry is navigation only.
export function ringLayout(model, width, height, narrow=width<600) {
  const cx=width/2, cy=height/2;
  const hubs=model.nodes.filter(n=>n.data.type==='theme');
  const rank=new Map(hubs.map((n,i)=>[n.data.id,i]));
  const membership=new Map();
  for(const e of model.edges){const r=rank.get(e.data.source);if(r!==undefined)membership.set(e.data.target,Math.min(membership.get(e.data.target)??Infinity,r));}
  const works=model.nodes.filter(n=>n.data.type==='work').sort((a,b)=>(membership.get(a.data.id)??Infinity)-(membership.get(b.data.id)??Infinity)||a.data.name.localeCompare(b.data.name));
  const positions=new Map();
  hubs.forEach((n,i)=>{const a=-Math.PI/2+i*2*Math.PI/hubs.length;positions.set(n.data.id,{x:cx+Math.sin(a)*width*(narrow?205/720:380/1100),y:cy+Math.cos(a)*height*(narrow?365/980:235/720)});});
  works.forEach((n,i)=>{const a=-Math.PI/2+(i+.5)*2*Math.PI/works.length,stagger=works.length>45?(i%2?20:-20):0;
    positions.set(n.data.id,{x:cx+Math.sin(a)*(width*(narrow?130/720:245/1100)+stagger),y:cy+Math.cos(a)*(height*(narrow?245/980:155/720)+stagger)});});
  return model.nodes.map(n=>({...n,position:positions.get(n.data.id)}));
}
