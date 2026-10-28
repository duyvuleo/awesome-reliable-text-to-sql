import {fromURL,toURL,normalizeState,selectWorks,themeCounts,graphElements,exportRecords,categoryThemes,ringLayout} from './model.mjs?v=topic-rings-1';
const $ = id => document.getElementById(id);
const repo = 'https://github.com/duyvuleo/awesome-reliable-text-to-sql';
const names = {paper:'Paper',system:'System',tool:'Tool',benchmark:'Benchmark'};

let data,state,cy,visible=[];
const records = new Map(), works = new Map(), themes = new Map();
function el(tag,text,cls) {const n=document.createElement(tag); if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function link(text,url,cls) {const n=el('a',text,cls);try {const u=new URL(url);if(u.protocol!=='https:')return el('span',text);n.href=u.href;}catch{return el('span',text);}n.target='_blank';n.rel='noopener noreferrer';return n;}
function button(text,fn,cls){const n=el('button',text,cls);n.type='button';n.addEventListener('click',fn);return n;}
function pretty(value){return value.replaceAll('_',' ').replaceAll('-',' ');}
function syncControls(){for(const k of ['kind','year','category','match','sort'])$(k).value=state[k];$('search').value=state.q;$('code').checked=state.code;$('show-labels').checked=state.labels;}
function setState(patch,{graph=true}={}){state=normalizeState({...state,...patch},data);render({graph});}
function chooseTheme(id){setState({theme:state.theme.includes(id)?state.theme.filter(t=>t!==id):[...state.theme,id],focus:'',selected:''});}
function chooseWork(id){setState({selected:id},{graph:false});if(window.innerWidth<781||$('inspector').getBoundingClientRect().bottom<0||$('inspector').getBoundingClientRect().top>window.innerHeight)$('inspector').scrollIntoView({behavior:'auto',block:'start'});}
function updateURL(){const query=toURL(state);history.replaceState(null,'',location.pathname+(query?'?'+query:''));}
function render({graph=true}={}){
  const focusedTheme=document.activeElement?.dataset.theme;
  visible=selectWorks(data,state);
  if(state.selected&&!visible.some(w=>w.id===state.selected))state.selected='';
  syncControls();updateURL();
  const recordCount=visible.reduce((n,w)=>n+w.entry_ids.length,0);
  $('match-count').textContent=`${visible.length} of ${data.works.length} works · ${recordCount} catalog records`;
  $('active-filters').replaceChildren();
  for(const id of state.theme)$('active-filters').append(button(`${themes.get(id).label} ×`,()=>chooseTheme(id)));
  $('clear-themes').hidden=!state.theme.length;
  if(state.focus)$('active-filters').append(button('Neighborhood ×',()=>setState({focus:''})));
  renderCloud();renderRows();
  const layoutChanged=renderDetails();
  if(graph||layoutChanged)renderGraph();else highlightGraph();
  $('export').disabled=!visible.length;
  if(focusedTheme)document.querySelector('#cloud button[data-theme="'+CSS.escape(focusedTheme)+'"]')?.focus({preventScroll:true});
}
function themeButton(t,size){const b=button(t.label,()=>chooseTheme(t.id));b.dataset.theme=t.id;b.setAttribute('aria-label',`${t.label}: ${t.count} ${t.count===1?'work':'works'}`);b.setAttribute('aria-pressed',String(state.theme.includes(t.id)));b.style.fontSize=size+'px';b.style.setProperty('--word-size',size+'px');b.append(el('sup',t.count));return b;}
function renderCloud(){
  const base=selectWorks(data,state,{ignoreTheme:true});
  const counts=themeCounts(data,base);
  let top=counts.slice(0,window.innerWidth<781?16:26);
  for(const id of state.theme)if(!counts.some(t=>t.id===id))counts.push({...themes.get(id),count:0});
  for(const id of state.theme)if(!top.some(t=>t.id===id))top.push(counts.find(t=>t.id===id));
  // Deterministic alternating order keeps the cloud balanced without rotation.
  top=top.filter((_,i)=>i%2===0).concat(top.filter((_,i)=>i%2===1).reverse());
  $('cloud').replaceChildren();
  const max=Math.max(1,...counts.map(t=>t.count));
  for(const t of top)$('cloud').append(themeButton(t,14+22*Math.sqrt(t.count/max)));
  if(!top.length)$('cloud').append(el('p','No themes match the current filters.','empty'));
  $('topic-counts').replaceChildren();
  for(const t of counts){const b=button('',()=>chooseTheme(t.id));b.append(el('span',t.label),el('strong',t.count));b.setAttribute('aria-pressed',String(state.theme.includes(t.id)));$('topic-counts').append(b);}
}
function renderRows(){
  const fragment=document.createDocumentFragment();
  for(const w of visible){const tr=el('tr');if(w.id===state.selected)tr.className='is-selected';
    const date=el('td',w.date),name=el('td'),summary=el('td'),action=el('td');
    name.append(button(w.name,()=>chooseWork(w.id),'work-name'));
    const chips=el('div',undefined,'chips');for(const kind of w.kinds)chips.append(el('span',names[kind],'chip'));chips.append(el('span',records.get(w.id).evidence,'chip'));if(records.get(w.id).original.scope)chips.append(el('span',records.get(w.id).original.scope,'chip'));name.append(chips);
    summary.append(el('div',w.summary,'summary-clamp'));const b=button('Inspect ↗',()=>chooseWork(w.id),'inspect');b.setAttribute('aria-label','Inspect '+w.name);action.append(b);tr.append(date,name,summary,action);fragment.append(tr);
  }
  $('rows').replaceChildren(fragment);$('empty').hidden=!!visible.length;
}
function appendSources(parent,urls){const ul=el('ul');urls.forEach((u,i)=>{const li=el('li');li.append(link(`Source ${i+1} · ${new URL(u).hostname}`,u));ul.append(li);});parent.append(ul);}
function renderDetails(){
  const panel=$('detail'),inspector=$('inspector'),w=works.get(state.selected);
  const layoutChanged=inspector.hidden===!!w;
  inspector.hidden=!w;
  inspector.parentElement.classList.toggle('has-selection',!!w);
  panel.replaceChildren();
  if(!w)return layoutChanged;
  const top=el('div',undefined,'detail-top');top.append(el('p','SELECTED WORK','eyebrow'),button('×',()=>setState({selected:''},{graph:false})));top.lastChild.setAttribute('aria-label','Close work details');panel.append(top,el('h2',w.name));
  const chips=el('div',undefined,'chips');w.kinds.forEach(k=>chips.append(el('span',names[k],'chip')));chips.append(el('span',w.date,'chip'));panel.append(chips,el('p',w.summary,'detail-summary'));
  const actions=el('div',undefined,'detail-actions');actions.append(link('Primary source ↗',records.get(w.id).url,'primary'),button(state.focus===w.id?'Show all works':'Focus neighborhood',()=>setState({focus:state.focus===w.id?'':w.id,theme:[]})));panel.append(actions);
  panel.append(el('h3','Research themes'));const tagWrap=el('div',undefined,'detail-tags');for(const t of w.themes)tagWrap.append(button(themes.get(t)?.label||pretty(t),()=>chooseTheme(t)));panel.append(tagWrap,el('h3',`${w.entry_ids.length} catalog record${w.entry_ids.length===1?'':'s'}`));
  for(const id of w.entry_ids){const r=records.get(id),detail=el('details',undefined,'record');detail.append(el('summary',`${names[r.kind]} · ${pretty(r.evidence)}`));if(id===w.id)detail.open=true;
    if(id!==w.id)detail.append(el('p',r.summary));if(r.status)detail.append(el('p',r.status)); if(r.original.license_note)detail.append(el('p','License: '+r.original.license_note)); if(r.original.protocol)detail.append(el('p',r.original.protocol));
    const links=el('div',undefined,'detail-actions');links.append(link('Catalog entry ↗',r.catalog_url));for(const u of r.code_links)links.append(link('Code / artifact ↗',u));detail.append(links);
    detail.append(el('p',`${r.date_label}: ${r.date}${r.date.length===4?' (year only)':''}${r.added_on ? ` · Added: ${r.added_on}` : ''} · Source checked: ${r.checked}`,'source-meta'));appendSources(detail,r.sources);panel.append(detail);
  }
  for(const c of data.comparisons.filter(c=>w.entry_ids.includes(c.resource_id))){
    const detail=el('details',undefined,'record');detail.append(el('summary','Benchmark coverage · '+c.label));
    for(const key of ['ambiguity','unanswerability','clarification','interaction']){const cell=c[key];detail.append(el('h3',pretty(key)),el('p',`${pretty(cell.status||cell.mode)} · ${cell.detail}`));}
    for(const key of ['domain','evaluation','data_access'])detail.append(el('h3',pretty(key)),el('p',key==='data_access'?pretty(c[key]):c[key]));
    detail.append(el('p','Comparison checked: '+c.checked_on));
    for(const e of c.evidence){detail.append(el('p',e.locator));appendSources(detail,[e.url]);}
    panel.append(detail);
  }
  const associated=data.relations.filter(e=>e.source===w.id||e.target===w.id);
  if(associated.length){panel.append(el('h3','Curated catalog relationships'));for(const edge of associated){const other=works.get(edge.source===w.id?edge.target:edge.source);panel.append(button(other.name,()=>setState({focus:'',q:'',theme:[],kind:'',year:'',category:'',code:false,selected:other.id}),'quiet'));}panel.append(el('p','These links follow the catalog’s explicit paper–resource metadata. They do not assert citation, derivation, or empirical support.'));}
  return layoutChanged;
}
function renderGraph(){
  const model=graphElements(data,visible,state);
  $('graph-empty').hidden=visible.length>0;$('graph-tooltip').hidden=true;
  $('graph-note').textContent='Outer hubs are themes; inner nodes are works. Lines show catalog topic membership, not citations. Hover to trace connections or select a node to explore.';
  if(!window.cytoscape){$('graph-note').textContent='Graph renderer unavailable. All results and evidence remain accessible in the table.';return;}
  if(cy)cy.destroy();
  const width=$('graph').clientWidth, height=$('graph').clientHeight;
  const workNodes=model.nodes.filter(n=>n.data.type==='work');
  const themeNodes=model.nodes.filter(n=>n.data.type==='theme');
  model.nodes=ringLayout(model,width,height);
  $('graph-count').textContent=`${workNodes.length} works · ${themeNodes.length} displayed themes · ${model.edges.length} membership links`;
  for(const n of model.nodes)if(n.data.type==='theme'){
    n.data.displayLabel=n.data.name+'\n'+n.data.count;
    const dx=n.position.x-width/2;
    n.data.align=Math.abs(dx)<width*.1?'center':dx<0?'left':'right';
    n.data.offset=Math.abs(dx)<width*.1?0:dx<0?-12:12;
  }
  const css=getComputedStyle(document.documentElement);const color=name=>css.getPropertyValue(name).trim();
  cy=window.cytoscape({container:$('graph'),elements:[...model.nodes,...model.edges],minZoom:.15,maxZoom:4,
    style:[{selector:'node',style:{'font-family':'system-ui','font-size':10,'color':color('--ink'),'text-wrap':'wrap','text-max-width':110,'text-valign':'bottom','text-margin-y':5,'overlay-opacity':0}},
      {selector:'node[type="work"]',style:{'width':visible.length>40?10:15,'height':visible.length>40?10:15,'label':'data(label)','text-opacity':state.labels?1:0,'font-size':10,'text-background-color':color('--surface'),'text-background-opacity':.85,'text-background-padding':2,'background-color':color('--graph-paper'),'border-width':1.5,'border-color':color('--surface')}},
      ...['system','tool','benchmark'].map(k=>({selector:`node[kind="${k}"]`,style:{'background-color':color('--'+k)}})),
      {selector:'node[type="theme"]',style:{'shape':'ellipse','width':node=>20+Math.sqrt(node.data('count'))*2,'height':node=>20+Math.sqrt(node.data('count'))*2,'label':'data(displayLabel)','font-size':12,'font-weight':600,'text-valign':'center','text-halign':'data(align)','text-margin-x':'data(offset)','text-margin-y':node=>node.data('align')==='center'?-30:0,'background-color':color('--accent'),'color':color('--ink'),'text-background-color':color('--surface'),'text-background-opacity':.9,'text-background-padding':3,'border-width':2,'border-color':color('--surface')}},
      {selector:'edge',style:{'width':1,'line-color':color('--edge'),'curve-style':'straight','opacity':.18}},
      {selector:'node[kind="system"]',style:{'shape':'rectangle'}},
      {selector:'.faded',style:{'opacity':.12}},
      {selector:'.chosen',style:{'border-width':4,'border-color':color('--accent'),'font-weight':700}},
      {selector:'.connected',style:{'opacity':1,'line-color':color('--accent'),'width':1.8}}],
    layout:{name:'preset',fit:true,padding:55}});
  cy.on('tap','node',event=>{const n=event.target;if(n.data('type')==='theme')chooseTheme(n.data('theme'));else chooseWork(n.data('work'));});
  cy.on('mouseover','node',event=>{highlightGraph(event.target.id());renderGraphPreview(event.target.data());});
  cy.on('mouseout','node',()=>{highlightGraph();renderGraphPreview();});
  cy.on('tap','edge',event=>{$('graph-tooltip').textContent=event.target.data('label');$('graph-tooltip').hidden=false;});
  renderGraphPreview();highlightGraph();
}
function renderGraphPreview(item){
  const panel=$('graph-preview');panel.replaceChildren();
  if(!item){panel.append(el('strong','Explore a connection'),el('p','Hover a theme or work to trace its links. Select a work to open its full source and benchmark details.'));return;}
  panel.append(el('strong',item.name));
  panel.append(el('p',item.type==='theme'?`${item.count} matching works carry this theme. Select it to toggle the theme filter.`:works.get(item.work).summary));
}
function highlightGraph(hoverId){
  if(!cy)return;cy.elements().removeClass('faded chosen connected');
  const id=hoverId||(state.selected?'w:'+state.selected:'');if(!id)return;
  const node=cy.getElementById(id);if(!node.length)return;
  cy.elements().addClass('faded');node.closedNeighborhood().removeClass('faded');node.addClass('chosen');node.connectedEdges().addClass('connected');
}

async function init(){
  try{
    const response=await fetch('./data.json');if(!response.ok)throw new Error('Catalog could not be loaded.');data=await response.json();
    if(data.schema_version!==1)throw new Error('Unsupported catalog format.');
    data.records.forEach(r=>records.set(r.id,r));data.works.forEach(w=>works.set(w.id,w));data.themes.forEach(t=>themes.set(t.id,t));
    state=fromURL(location.search,data);
    $('collection-stats').replaceChildren();for(const [count,label] of [[data.works.length,'grouped works'],[data.records.length,'catalog records'],[data.themes.length,'research themes'],[data.comparisons.length,'benchmark comparisons']]){const d=el('div');d.append(el('strong',count),el('span',label));$('collection-stats').append(d);}
    const years=[...new Set(data.records.map(r=>r.year).filter(Boolean))].sort((a,b)=>b-a);for(const y of years){const o=el('option',y);o.value=y;$('year').append(o);}
    for(const id of categoryThemes){const o=el('option',data.categories[id]);o.value=id;$('category').append(o);}
    let timer;$('search').addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>setState({q:$('search').value,focus:''}),150);});
    for(const key of ['kind','year','category','match','sort'])$(key).addEventListener('change',()=>setState({[key]:$(key).value}));
    $('clear-themes').addEventListener('click',()=>setState({theme:[],focus:''}));
    $('code').addEventListener('change',()=>setState({code:$('code').checked}));
    $('reset').addEventListener('click',()=>{clearTimeout(timer);state=normalizeState({},data);render();});
    $('show-labels').addEventListener('change',()=>{state=normalizeState({...state,labels:$('show-labels').checked},data);updateURL();cy?.nodes('[type="work"]').style('text-opacity',state.labels?1:0);});
    $('zoom-in').addEventListener('click',()=>cy?.zoom({level:Math.min(4,cy.zoom()*1.3),renderedPosition:{x:cy.width()/2,y:cy.height()/2}}));
    $('zoom-out').addEventListener('click',()=>cy?.zoom({level:Math.max(.15,cy.zoom()/1.3),renderedPosition:{x:cy.width()/2,y:cy.height()/2}}));
    $('fit').addEventListener('click',()=>cy?.fit(undefined,35));
    $('export').addEventListener('click',()=>{const payload=exportRecords(data,visible);const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json'}));const a=el('a');a.href=url;a.download='reliable-text-to-sql-selection.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
    let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{renderCloud();renderGraph();},150);});
    window.addEventListener('popstate',()=>{state=fromURL(location.search,data);render();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&state.selected)setState({selected:''},{graph:false});});
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>renderGraph());
    $('source-date').textContent='Latest source check: '+data.checked;
    render();
  }catch(error){$('error').hidden=false;$('error').replaceChildren(el('strong','The explorer could not load. '),el('span',error.message+' '),link('Read the catalogs instead.',repo));$('match-count').textContent='Catalog unavailable';}
}
init();
