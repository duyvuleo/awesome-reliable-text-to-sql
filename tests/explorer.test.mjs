import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {normalizeState,fromURL,toURL,selectWorks,themeCounts,graphElements,exportRecords} from '../site/model.mjs';
const data=JSON.parse(readFileSync(new URL('../site/data.json',import.meta.url),'utf8'));
const blank=()=>normalizeState({},data);
test('default selection preserves all works',()=>assert.equal(selectWorks(data,blank()).length,data.works.length));
test('filters combine and topic counts deduplicate grouped records',()=>{
 const s=normalizeState({kind:'system',theme:'clarification'},data);
 const works=selectWorks(data,s);assert.ok(works.length);
 assert.ok(works.every(w=>w.kinds.includes('system')&&w.themes.includes('clarification')));
 const c=themeCounts(data,works).find(t=>t.id==='clarification');assert.equal(c.count,works.length);
});
test('year and type must match the same member record',()=>{
 const fake={works:[{id:'w',entry_ids:['p','s'],themes:[]}],records:[{id:'p',kind:'paper',year:2024,name:'p',summary:'x',tags:[],code_links:[]},{id:'s',kind:'system',year:2025,name:'s',summary:'x',tags:[],code_links:[]}],relations:[]};
 assert.equal(selectWorks(fake,{...blank(),year:'2024',kind:'system'}).length,0);
});
test('empty search produces empty results and graph without dangling edges',()=>{
 const s={...blank(),q:'zzzz-no-such-resource'};const works=selectWorks(data,s);assert.equal(works.length,0);
 assert.deepEqual(graphElements(data,works,s),{nodes:[],edges:[]});
});
test('graph contains only theme edges with valid endpoints',()=>{
 const s=blank();const g=graphElements(data,selectWorks(data,s),s);const ids=new Set(g.nodes.map(n=>n.data.id));
 assert.ok(g.edges.length);assert.ok(g.edges.every(e=>e.data.type==='theme'&&ids.has(e.data.source)&&ids.has(e.data.target)));
});
test('shared URLs round-trip filters and resolve member record IDs',()=>{
 const s=normalizeState({q:'ambiguity & evidence',kind:'system',year:'2026',code:true,theme:'ambiguity',selected:'clarity-pipeline',mode:'catalog'},data);
 assert.equal(s.selected,'clarity');assert.deepEqual(fromURL('?'+toURL(s),data),s);
 assert.deepEqual(fromURL('?theme=unknown&selected=missing&sort=bad',data).theme,[]);
});
test('selection export retains every member and all sources without mutation',()=>{
 const before=JSON.stringify(data);const works=data.works.filter(w=>w.id==='clarity');const out=exportRecords(data,works);
 assert.equal(out.work_count,1);assert.equal(out.entries.length,3);
 assert.ok(out.entries.every(e=>e.sources.length&&e.catalog_url.startsWith('https://github.com/')));
 assert.equal(JSON.stringify(data),before);
});
test('focus includes only the work and shared-theme neighbors',()=>{
 const s={...blank(),focus:'rts'};const works=selectWorks(data,s);const focus=data.works.find(w=>w.id==='rts');
 assert.ok(works.every(w=>w.id===s.focus||w.themes.some(t=>focus.themes.includes(t))));
});
test('selecting a theme gives one labeled hub for the matching works',()=>{
 const s=normalizeState({theme:'verification'},data);const works=selectWorks(data,s);const g=graphElements(data,works,s);
 assert.equal(g.nodes.filter(n=>n.data.type==='theme').length,1);
 assert.equal(g.edges.filter(e=>e.data.type==='theme').length,works.length);
});
test('undated resources remain last when sorting oldest first',()=>{
 const result=selectWorks(data,{...blank(),sort:'oldest'});
 const firstUndated=result.findIndex(w=>!w.year);
 assert.ok(firstUndated>0);assert.ok(result.slice(firstUndated).every(w=>!w.year));
});
test('research area and code filters preserve genuine matching members',()=>{
 const result=selectWorks(data,normalizeState({category:'verification',kind:'tool',code:true},data));
 assert.ok(result.length);assert.ok(result.every(w=>w.categories.includes('verification')));
 const records=new Map(data.records.map(r=>[r.id,r]));
 assert.ok(result.every(w=>w.entry_ids.some(id=>records.get(id).kind==='tool'&&records.get(id).code_links.length)));
});

test('multiple themes implement union and intersection',()=>{
 const theme=['ambiguity','unanswerability'];
 for(const match of ['any','all']){
  const s=normalizeState({theme,match},data);const found=selectWorks(data,s);
  const expected=data.works.filter(w=>match==='all'?theme.every(t=>w.themes.includes(t)):theme.some(t=>w.themes.includes(t)));
  assert.deepEqual(found.map(w=>w.id),expected.map(w=>w.id));assert.ok(found.length);
  const hubs=graphElements(data,found,s).nodes.filter(n=>n.data.type==='theme').map(n=>n.data.theme);
  assert.deepEqual(new Set(hubs),new Set(theme));
 }
});
test('repeated theme URLs deduplicate, reject unknowns, retain match and discard legacy mode',()=>{
 const s=fromURL('?theme=ambiguity&theme=unanswerability&theme=ambiguity&theme=unknown&match=all&mode=catalog',data);
 assert.deepEqual(s.theme,['ambiguity','unanswerability']);assert.equal(s.match,'all');
 assert.deepEqual(fromURL('?'+toURL(s),data),s);assert.ok(!toURL(s).includes('mode='));
 assert.deepEqual(fromURL('?theme=ambiguity',data).theme,['ambiguity']);
});
test('ignoring themes keeps cloud counts available across multi-selection',()=>{
 const s=normalizeState({theme:['ambiguity','unanswerability'],match:'all',year:'2026'},data);
 assert.deepEqual(selectWorks(data,s,{ignoreTheme:true}),selectWorks(data,{...s,theme:[]}));
});

test('labels default on and off preference survives URL and filter changes',()=>{
 assert.equal(blank().labels,true);
 assert.equal(fromURL('?labels=unexpected',data).labels,true);
 const off=normalizeState({labels:false,theme:['ambiguity','verification']},data);
 assert.equal(fromURL('?'+toURL(off),data).labels,false);
 assert.equal(normalizeState({...off,kind:'paper'},data).labels,false);
 assert.deepEqual(selectWorks(data,off),selectWorks(data,{...off,labels:true}));
 assert.ok(!toURL(blank()).includes('labels='));
});
