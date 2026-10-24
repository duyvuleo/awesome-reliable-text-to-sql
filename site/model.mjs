// Pure selection and graph functions: shared by the UI and offline tests.
export const kinds = ['paper', 'system', 'tool', 'benchmark'];
export const categoryThemes = ['ambiguity', 'answerability', 'interaction', 'context', 'verification'];
export function normalizeState(input, data) {
  const workIDs = new Set(data.works.map(w => w.id));
  const resolve = id => workIDs.has(id) ? id : (data.records.find(r => r.id === id)?.work_id || '');
  return {q: String(input.q || '').slice(0, 240), kind: kinds.includes(input.kind) ? input.kind : '',
    year: data.records.some(r => String(r.year) === input.year) ? input.year : '',
    category: categoryThemes.includes(input.category) ? input.category : '',
    code: input.code === true || input.code === '1',
    theme: data.themes.some(t => t.id === input.theme) ? input.theme : '',
    mode: input.mode === 'catalog' ? 'catalog' : 'themes',
    selected: resolve(input.selected || ''), focus: resolve(input.focus || ''),
    sort: ['oldest', 'name'].includes(input.sort) ? input.sort : 'newest'};
}
export function fromURL(search, data) {
  return normalizeState(Object.fromEntries(new URLSearchParams(search)), data);
}
export function toURL(state) {
  const p = new URLSearchParams();
  for (const key of ['q','kind','year','category','theme','focus','selected']) if (state[key]) p.set(key,state[key]);
  if (state.code) p.set('code','1');
  if (state.mode === 'catalog') p.set('mode','catalog');
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
    return ignoreTheme || !state.theme || w.themes.includes(state.theme);
  });
  if (state.focus) {
    const focus = data.works.find(w => w.id === state.focus);
    const direct = new Set(data.relations.flatMap(e => e.source === state.focus ? [e.target] : e.target === state.focus ? [e.source] : []));
    works = works.filter(w => w.id === state.focus || direct.has(w.id) ||
      (state.mode === 'themes' && focus && w.themes.some(t => focus.themes.includes(t))));
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
  const visible = new Set(works.map(w => w.id));
  const nodes = works.map((w,i) => ({data:{id:'w:'+w.id,work:w.id,name:w.name,
    label:w.name.split(':')[0].length<=32 ? w.name.split(':')[0] : w.name.slice(0,29)+'…',kind:w.kind,type:'work',count:1},
    position:{x:300+250*Math.cos(i*2.39996),y:250+200*Math.sin(i*2.39996)}}));
  const edges = data.relations.filter(e => visible.has(e.source) && visible.has(e.target))
    .map((e,i) => ({data:{id:'c:'+i,source:'w:'+e.source,target:'w:'+e.target,type:'catalog',label:'Curated catalog link'}}));
  if (state.mode === 'themes') {
    const counts = themeCounts(data,works);
    const themes = state.theme ? counts.filter(t=>t.id===state.theme) : counts.slice(0,10);
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
